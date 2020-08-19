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
	, camera2d_{ InviwoApplication::getPtr()->getCameraFactory()->create("OrthographicCamera") }
    , trackball_(&camera_)
	, axisRenderers_({ {xAxis_, yAxis_} })
	, xAxisSelection_("xAxisSelection", "X Axis")
	, yAxisSelection_("yAxisSelection", "Y Axis")
	, toggle3d_("toggle3d", "Render in 3D space")
	, lineMesh_( std::make_shared<BasicMesh>() )
	, meshDrawer_( std::unique_ptr<MeshDrawer>() )
	, shader_("meshrendering.vert", "meshrendering.frag", false)
	, lightingProperty_("lighting", "Lighting", &camera_)
    {

	shader_.onReload([this]() { invalidate(InvalidationLevel::InvalidResources); });
	

	MeshDrawerFactory* factory = InviwoApplication::getPtr()->getMeshDrawerFactory();
	meshDrawer_ = std::move(factory->create(lineMesh_.get()));

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
	toggle3d_.onChange([this] {
		position_.setVisible(toggle3d_.get());
		size_.setVisible(toggle3d_.get());
		camera_.setVisible(toggle3d_.get());
		trackball_.setVisible(toggle3d_.get());
		updateDimensions();
	});
	size_.onChange([this] { updateDimensions(); });
	position_.onChange([this] { updateDimensions(); });

	inport_.onChange([this] { 
		reloadDatasets();
		updatePlotData(); });
	xAxisSelection_.onChange([this] { updatePlotData(); });
	yAxisSelection_.onChange([this] { updatePlotData(); });
	
	// Initialize axis default values.
	for (auto axis : { &xAxis_, &yAxis_ }) {
		axis->captionSettings_.offset_.set(0.7f);
		axis->captionSettings_.position_.set(0.5f);
		axis->labelSettings_.offset_.set(0.7f);

		axis->majorTicks_.tickLength_.set(0.3f);
		axis->majorTicks_.tickWidth_.set(1.5f);
		axis->majorTicks_.style_.set(plot::TickStyle::Outside);
		axis->majorTicks_.setCurrentStateAsDefault();

		axis->minorTicks_.tickLength_.set(0.15f);
		axis->minorTicks_.tickWidth_.set(1.3f);
		axis->minorTicks_.style_.set(plot::TickStyle::Outside);
		axis->minorTicks_.setCurrentStateAsDefault();
	}
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
	const size2_t dims = outport_.getDimensions();
	if (!toggle3d_.get() && oldDims_ != dims) updateDimensions();
	
	// Save a pointer to the camera that will be used
	Camera* activeCamera;
	if (toggle3d_.get())
		activeCamera = &camera_.get();
	else
		activeCamera = camera2d_.get();


	auto dot = [](const vec3& v1, const vec3& v2) { return v1.x*v2.x + v1.y*v2.y + v1.z*v2.z;  };
	auto cross = [](const vec3& v1, const vec3& v2) { return vec3(
		v1.y * v2.z - v1.z * v2.y,
		v1.z * v2.x - v1.x * v2.z,
		v1.x * v2.y - v1.y * v2.x); };
	auto length = [](const vec3& v) { return std::sqrt(v.x*v.x + v.y*v.y + v.z*v.z); };
	auto normalize = [length](const vec3& v) { return v / length(v); };

	vec3 xDir(1, 0, 0);
	vec3 yDir(0, 1, 0);

	if (toggle3d_.get()) {
		// Direct the graph to face the camera.
		auto from = camera_.getLookFrom();
		auto to = camera_.getLookTo();
		auto up = camera_.getLookUp();
		//glm::dot(from, to);

		auto normal = from - to;
		normal = normalize(normal);
		xDir = vec3(normal[1], -normal[0], 0);
		auto a = normal * xDir;
		yDir = cross(normal, xDir);

		xDir = normalize(xDir);
		yDir = normalize(yDir);

		xDir = xDir * dot(xDir, up) + yDir * dot(yDir, up);
		xDir = normalize(xDir);

		yDir = cross(normal, xDir);
		yDir = -normalize(yDir);
		

		std::swap(yDir, xDir);

		LogInfo("Camera: \n"
			<< from[0] << ", " << from[1] << ", " << from[2] << "\n"
			<< to[0] << ", " << to[1] << ", " << to[2] << "\n"
			<< up[0] << ", " << up[1] << ", " << up[2] << "\n"
		);
		//camera_.setLookFrom(vec3(0, 0, from[2]));
		//camera_.setLookUp(vec3(0, 1, 0));
		/*lineMesh_->setBasis(Matrix<3U, float>(
			graphDims_[0], 0, 0, 
			0, graphDims_[1], 0, 
			0, 0, 1));*/
		/*lineMesh_->setBasis(Matrix<3U, float>(
			graphDims_[0]*xDir.x, yDir.x, 0,
			xDir.y, graphDims_[1]*yDir.y, 0,
			xDir.z, yDir.z, 1));*/
		/*lineMesh_->setBasis(Matrix<3U, float>(
			graphDims_[0] * xDir.x, xDir.y, xDir.z,
			yDir.x, graphDims_[1] * yDir.y, yDir.z,
			0, 0, 1));*/

		lineMesh_->setBasis(Matrix<3U, float>(
			graphDims_[0] * xDir.x, graphDims_[0] * xDir.y, graphDims_[0] * xDir.z,
			graphDims_[1] * yDir.x, graphDims_[1] * yDir.y, graphDims_[1] * yDir.z,
			0, 0, 1));

		//lineMesh_->setOffset(origin_);

		LogInfo("Normal: \n"
			<< length(normal) << ", " << length(xDir) << ", " << length(yDir) << "\n"
			<< dot(normal, xDir) << ", " << dot(normal, yDir) << ", " << dot(xDir, yDir) << "\n"
			<< normal[0] << ", " << normal[1] << ", " << normal[2] << "\n"
		);
		//camera_.setLookFrom(vec3(from[0], 0, 0));
	}

	// Render x and y axis

	axisRenderers_[0].render(activeCamera, dims, origin_, origin_ + xDir * graphDims_[0], yDir);
	axisRenderers_[1].render(activeCamera, dims, origin_, origin_ + yDir * graphDims_[1], xDir);

	//axisRenderers_[0].render(activeCamera, dims, origin_, origin_ + xDir*graphDims_[0], vec3(0.0f, 1.0f, 0.0f));
	//axisRenderers_[1].render(activeCamera, dims, origin_, origin_ + yDir*graphDims_[1], vec3(1.0f, 0.0f, 0.0f));
	
	// Render lines.
	shader_.activate();
	utilgl::setUniforms(shader_, lightingProperty_);
	utilgl::setShaderUniforms(shader_, *activeCamera, "camera");
	utilgl::setShaderUniforms(shader_, *meshDrawer_->getMesh(), "geometry");
	meshDrawer_->draw();
	shader_.deactivate();

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



void Plot2dProcessor::updatePlotData() {
	// Clear index buffers
	//lineMesh_->clearRepresentations();
	/*while (lineMesh_->getIndexBuffers().size() != 0){
		lineMesh_->getIndexBuffers()[0].second->clearRepresentations();
		lineMesh_->removeIndexBuffer(0);
	}*/

	// Reset line mesh
	lineMesh_ = std::make_shared<BasicMesh>(); 
	meshDrawer_ = std::move(InviwoApplication::getPtr()->getMeshDrawerFactory()->create(lineMesh_.get()));


	if (!inport_.hasData()) return;

	const std::shared_ptr<const DataFrame> dataframe = inport_.getData();
	const std::shared_ptr<const Column> xCol = dataframe->getColumn(xAxisSelection_.getSelectedIndex());
	const std::shared_ptr<const Column> yCol = dataframe->getColumn(yAxisSelection_.getSelectedIndex());

	if (xCol->getSize() < 2 || yCol->getSize() < 2 || yCol->getSize() != xCol->getSize()) return;
	
	// Find extreme values for x and y axis
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

	const float offsetX = -xrange[0];
	const float offsetY = -yrange[0];
	const float scaleX = 1.0f / (xrange[1] - xrange[0]);
	const float scaleY = 1.0f / (yrange[1] - yrange[0]);

	std::shared_ptr<IndexBufferRAM> indices = lineMesh_->addIndexBuffer(DrawType::Lines, ConnectivityType::Strip);

	vec4 color(1, 0, 0, 1);
	//// Add point from dataframe to line mesh
	for (size_t i = 0; i < xCol->getSize(); i+=1) {
		const vec3 p1((xCol->getAsDouble(i) + offsetX)*scaleX, (yCol->getAsDouble(i) + offsetY)*scaleY, 0);
		//const vec3 p2((xCol->getAsDouble(i+1) + offsetX)*scaleX, (yCol->getAsDouble(i+1) + offsetY)*scaleY, 0);
		
		indices->add(lineMesh_->addVertex(p1, p1, p1, color));
	}
	

	// Update the dimensions of the mesh.
	updateDimensions();


}














} // namespace