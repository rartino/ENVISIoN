#include <modules/graph2d/processors/plot2d.h>

#include <modules/plotting/utils/axisutils.h>
#include <modules/opengl/texture/textureutils.h>
#include <inviwo/core/util/raiiutils.h>
#include <inviwo/core/algorithm/boundingbox.h>
#include <inviwo/core/rendering/meshdrawerfactory.h>


#include <modules/opengl/texture/textureutils.h>
#include <modules/opengl/shader/shaderutils.h>
#include <modules/opengl/openglutils.h>


#include <modules/opengl/openglutils.h>
#include <inviwo/core/datastructures/coordinatetransformer.h>
#include <modules/opengl/texture/textureutils.h>

namespace inviwo {


// The Class Identifier has to be globally unique. Use a reverse DNS naming scheme
const ProcessorInfo Plot2dProcessor::processorInfo_{
    "org.inviwo.Plot2D",    // Class identifier
    "Plot2D",                 // Display name
    "Plotting",               // Category
    CodeState::Stable,        // Code state
    "Plotting",           // Tags
};

const ProcessorInfo Plot2dProcessor::getProcessorInfo() const { return processorInfo_; }

Plot2dProcessor::Plot2dProcessor()
    : Processor()
    , inport_("inport")
    , imageInport_("imageInport")
	, meshOutport_("meshOutport")
    , outport_("outport")
    , xAxis_("xAxis", "X Axis")
    , yAxis_("yAxis", "Y Axis")
	, position_("position", "Position", vec3(0), vec3(-25), vec3(25), vec3(0.01))
	, size_("size", "Size", vec2(3), vec2(0.01), vec2(25), vec2(0.01))
    , camera_("camera", "Camera")
    , trackball_(&camera_)
	, axisRenderers_({ {xAxis_, yAxis_} })
	, xAxisSelection_("xAxisSelection", "X Axis")
	, yAxisSelection_("yAxisSelection", "Y Axis")
	, toggle3d_("toggle3d", "Render in 3D space")
	, camera2d_{ InviwoApplication::getPtr()->getCameraFactory()->create("OrthographicCamera") }
	/*, lines_(DrawType::Lines, ConnectivityType::Strip)
	, lineDrawer_(&lines_)
	, lineShader_("img_color.frag")*/
	, lineMesh_( std::make_shared<BasicMesh>() )
	, meshDrawer_( std::unique_ptr<MeshDrawer>() )
	, shader_("meshrendering.vert", "meshrendering.frag", false)
	, lightingProperty_("lighting", "Lighting", &camera_)
	, shader2d_("mesh2drendering.vert", "mesh2drendering.frag")
    {
	shader_.onReload([this]() { invalidate(InvalidationLevel::InvalidResources); });
	

	indices_ = lineMesh_->addIndexBuffer(DrawType::Lines, ConnectivityType::None);
	vec4 col(1, 0, 0, 1);
	vec3 p1(0, 0, 0);
	vec3 p2(0.5, 0.5, 0);
	vec3 p3(0.1, 0.9, 0);
	vec3 p4(0.6, 0.2, 0);
	indices_->add(lineMesh_->addVertex(p1, p1, p1, col));
	indices_->add(lineMesh_->addVertex(p2, p2, p2, col));
	indices_->add(lineMesh_->addVertex(p2, p2, p2, col));
	indices_->add(lineMesh_->addVertex(p3, p3, p3, col));
	indices_->add(lineMesh_->addVertex(p3, p3, p3, col));
	indices_->add(lineMesh_->addVertex(p4, p4, p4, col));
	indices_->add(lineMesh_->addVertex(p4, p4, p4, col));
	indices_->add(lineMesh_->addVertex(p1, p1, p1, col));
	//LogInfo("INDICES1 : " + std::to_string(lineMesh_->get));

	//lineMesh_->clearRepresentations();
	//indices_->clear();
	indices_->add(lineMesh_->addVertex(p1, p1, p1, col));
	indices_->add(lineMesh_->addVertex(p4, p4, p4, col));

	//LogInfo("INDICES2 : " + std::to_string(lineMesh_->getNumberOfIndicies()));

	MeshDrawerFactory* factory = InviwoApplication::getPtr()->getMeshDrawerFactory();
	meshDrawer_ = std::move(factory->create(lineMesh_.get()));
	//auto renderer = ;

	//indices_->add(lineMesh_->addVertex(vec3(0, 0, 0)));
	/*indices_ = lineMesh_.addIndexBuffer(DrawType::Lines, ConnectivityType::None);
	indices_->add(lineMesh_.addVertex(vec3(10, 10, 0)));
	indices_->add(lineMesh_.addVertex(vec3(10, 10, 0)));
	indices_->add(lineMesh_.addVertex(vec3(5, 3, 0)));
	indices_->add(lineMesh_.addVertex(vec3(5, 3, 0)));
	indices_->add(lineMesh_.addVertex(vec3(8, 1, 0)));
	indices_->add(lineMesh_.addVertex(vec3(8, 1, 0)));
	indices_->add(lineMesh_.addVertex(vec3(0, 0, 0)));*/
	//ConnectivityType::Strip

	// Initialize the 2d camera.
	camera2d_->setLookFrom(vec3(0, 0, 100));
	camera2d_->setLookTo(vec3(0, 0, 0));
	camera2d_->setLookUp(vec3(0, 1, 0));
	camera2d_->setFarPlaneDist(200);
	camera2d_->setNearPlaneDist(1);

	// Setup ports
    imageInport_.setOptional(true);
    addPort(inport_);
    addPort(imageInport_);
    addPort(outport_);
	addPort(meshOutport_);

	// Add properties
	addProperty(toggle3d_);
	addProperty(position_);
	addProperty(size_);
	addProperties(xAxisSelection_, yAxisSelection_);
	addProperties(xAxis_, yAxis_);
	addProperty(camera_);
	addProperty(trackball_);
	addProperty(lightingProperty_);

	// Setup property default values
	xAxis_.setCaption("x");
	yAxis_.setCaption("y");
	yAxis_.orientation_.setSelectedDisplayName("Vertical");
	xAxis_.setCollapsed(true);
	yAxis_.setCollapsed(true);

	toggle3d_.set(false);
	camera_.setVisible(false);
	trackball_.setVisible(false);

	camera_.setVisible(false);
	trackball_.setVisible(false);
	camera_.setCollapsed(true);
	trackball_.setCollapsed(true);

	// Event callbacks
	inport_.onChange([this] { reloadDatasets(); });
	toggle3d_.onChange([this] {
		position_.setVisible(toggle3d_.get());
		size_.setVisible(toggle3d_.get());

		position_.setVisible(true);
		size_.setVisible(true);
		camera_.setVisible(toggle3d_.get());
		trackball_.setVisible(toggle3d_.get());

		updateDimensions();

	});
	size_.onChange([this] { updateDimensions(); });
	position_.onChange([this] { updateDimensions(); });

	xAxisSelection_.onChange([this] { updateAxis(); });
	yAxisSelection_.onChange([this] { updateAxis(); });

	const float majorTick = 0.3f;
	const float minorTick = 0.15f;
	for (auto axis : { &xAxis_, &yAxis_ }) {
		axis->captionSettings_.offset_.set(0.7f);
		axis->captionSettings_.position_.set(0.5f);
		axis->labelSettings_.offset_.set(0.7f);

		axis->majorTicks_.tickLength_.set(majorTick);
		axis->majorTicks_.tickWidth_.set(1.5f);
		axis->majorTicks_.style_.set(plot::TickStyle::Outside);
		axis->majorTicks_.setCurrentStateAsDefault();

		axis->minorTicks_.tickLength_.set(minorTick);
		axis->minorTicks_.tickWidth_.set(1.3f);
		axis->minorTicks_.style_.set(plot::TickStyle::Outside);
		axis->minorTicks_.setCurrentStateAsDefault();
	}
	updateDimensions();
}


void Plot2dProcessor::initializeResources() {
	LogInfo("Initializing resources plot2d");
	utilgl::addShaderDefines(shader_, lightingProperty_);
	shader_.build();
}


void Plot2dProcessor::process() {
	LogInfo("Process start");
	if (imageInport_.isReady()) {
		utilgl::activateTargetAndCopySource(outport_, imageInport_, ImageType::ColorDepth);
	}
	else {
		utilgl::activateAndClearTarget(outport_, ImageType::ColorDepth);
	}

	
	if (!toggle3d_.get() && oldDims_ != outport_.getDimensions()) {
		updateDimensions();
		updateDimensions();

	}
	const size2_t dims = outport_.getDimensions();
	double aspect = (double)dims[0] / (double)dims[1];
	
	Camera* activeCamera;
	
	if (toggle3d_.get())
		activeCamera = &camera_.get();
	else
		activeCamera = camera2d_.get();

	axisRenderers_[0].render(activeCamera, dims, origin_, origin_ + vec3(graphDims_[0], 0, 0), vec3(0.0f, 1.0f, 0.0f));
	axisRenderers_[1].render(activeCamera, dims, origin_, origin_ + vec3(0, graphDims_[1], 0), vec3(1.0f, 0.0f, 0.0f));
	
	// Render lines.
	shader_.activate();
	utilgl::setUniforms(shader_, lightingProperty_);
	utilgl::setShaderUniforms(shader_, *activeCamera, "camera");
	utilgl::setShaderUniforms(shader_, *meshDrawer_->getMesh(), "geometry");
	meshDrawer_->draw();
	shader_.deactivate();

	meshOutport_.setData(lineMesh_);

	utilgl::deactivateCurrentTarget();
}


void Plot2dProcessor::reloadDatasets() {
	if (!inport_.hasData()) {
		xAxisSelection_.clearOptions();
		yAxisSelection_.clearOptions();
		return;
	}
	const std::shared_ptr<const DataFrame> dataframe = inport_.getData();
	// Update column selection properties
	std::vector<OptionPropertyStringOption> options;
	for (const auto& column : *dataframe) {
		options.emplace_back(column->getHeader(), column->getHeader(), column->getHeader());
	}

	xAxisSelection_.replaceOptions(options);
	yAxisSelection_.replaceOptions(options);
	xAxisSelection_.setCurrentStateAsDefault();
	yAxisSelection_.setCurrentStateAsDefault();
}

void Plot2dProcessor::updateAxis() {
	if (!inport_.hasData()) return;
	LogInfo("UPDATING VALUE RANGE");

	const std::shared_ptr<const DataFrame> dataframe = inport_.getData();
	const std::shared_ptr<const Column> xCol = dataframe->getColumn(xAxisSelection_.getSelectedIndex());
	const std::shared_ptr<const Column> yCol = dataframe->getColumn(yAxisSelection_.getSelectedIndex());

	if (xCol->getSize() == 0 || yCol->getSize() == 0) return;

	// Find extreme values
	dvec2 xrange(xCol->getAsDouble(0), xCol->getAsDouble(0));
	dvec2 yrange(yCol->getAsDouble(0), yCol->getAsDouble(0));
	for (size_t i = 1; i < xCol->getSize(); ++i) {
		double v = xCol->getAsDouble(i);
		if (v < xrange[0]) xrange[0] = v;
		if (v > xrange[1]) xrange[1] = v;
	}
	for (size_t i = 1; i < yCol->getSize(); ++i) {
		double v = yCol->getAsDouble(i);
		if (v < yrange[0]) yrange[0] = v;
		if (v > yrange[1]) yrange[1] = v;
	}
	xAxis_.range_.set(xrange);
	yAxis_.range_.set(yrange);
	LogInfo("xrange: " + std::to_string(xrange[0]) + ":" + std::to_string(xrange[1]));
	LogInfo("yrange: " + std::to_string(yrange[0]) + ":" + std::to_string(yrange[1]));


	//xAxis_.set
}

void Plot2dProcessor::updateDimensions() {
	if (toggle3d_.get()) {
		origin_ = position_.get();
		graphDims_ = size_.get();
	}
	else {
		const size2_t dims = outport_.getDimensions();
		const float aspect = (float)dims[0] / (float)dims[1];
		const float scale = (double)dims[0] / 512;
		const float width = 50 * scale;
		const float height = width / aspect;
		const float padding = 50 * width / (double)dims[0];

		oldDims_ = dims;
		origin_ = vec3(-width / 2 + padding, -height / 2 + padding, 0);
		graphDims_ = vec2(width - 2 * padding, height - 2 * padding);
		// Update 2d camera to fit new dimensions.
		static_cast<OrthographicCamera*>(camera2d_.get())->setFrustum({ -width / 2.0f, +width / 2.0f, -width / 2.0f / aspect, +width / 2.0f / aspect });
	}
	// Scale and offset line mesh to align with axises.
	lineMesh_->setBasis(Matrix<3U, float>(graphDims_[0], 0, 0, 0, graphDims_[1], 0, 0, 0, 1));
	lineMesh_->setOffset(origin_);
}

void Plot2dProcessor::rebuildMesh() {
	// Set the line mesh indices to represent the selected dataframe data.
}














} // namespace