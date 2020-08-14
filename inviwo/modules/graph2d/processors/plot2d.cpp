#include <modules/graph2d/processors/plot2d.h>

#include <modules/plotting/utils/axisutils.h>
#include <modules/opengl/texture/textureutils.h>
#include <inviwo/core/util/raiiutils.h>
#include <inviwo/core/algorithm/boundingbox.h>

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
    , outport_("outport")
    , xAxis_("xAxis", "X Axis")
    , yAxis_("yAxis", "Y Axis")
    , camera_("camera", "Camera")
    , trackball_(&camera_)
	, axisRenderers_({ {xAxis_, yAxis_} })
	, xAxisSelection_("xAxisSelection", "X Axis")
	, yAxisSelection_("yAxisSelection", "Y Axis")
    {

    imageInport_.setOptional(true);
    addPort(inport_);
    addPort(imageInport_);
    addPort(outport_);

	
	addProperties(xAxisSelection_, yAxisSelection_);

	xAxis_.setCaption("x");
	yAxis_.setCaption("y");
	addProperties(xAxis_, yAxis_);

	addProperty(camera_);
	addProperty(trackball_);
	camera_.setCollapsed(true);
	trackball_.setCollapsed(true);


	inport_.onChange([this] { reloadDatasets(); });
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
}

void Plot2dProcessor::process() {
	if (imageInport_.isReady()) {
		utilgl::activateTargetAndCopySource(outport_, imageInport_, ImageType::ColorDepth);
	}
	else {
		utilgl::activateAndClearTarget(outport_, ImageType::ColorDepth);
	}

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

	//// Find extreme values
	//vec
	//for (size_t i = 0; i < xCol.size(); ++i) {

	//}
	//for ()

	//xCol->getSize()


}















} // namespace