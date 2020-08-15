#ifndef IVW_PLOT2DPROCESSOR_H
#define IVW_PLOT2DPROCESSOR_H

#include <modules/graph2d/graph2dmoduledefine.h>
#include <inviwo/core/common/inviwo.h>

#include <inviwo/core/processors/processor.h>
#include <inviwo/core/properties/ordinalproperty.h>
#include <inviwo/core/properties/minmaxproperty.h>
#include <inviwo/core/properties/compositeproperty.h>
#include <inviwo/core/properties/optionproperty.h>
#include <inviwo/core/properties/cameraproperty.h>
#include <inviwo/core/properties/boolproperty.h>

#include <inviwo/core/ports/volumeport.h>
#include <inviwo/core/ports/imageport.h>

#include <inviwo/core/interaction/cameratrackball.h>
#include <inviwo/dataframe/datastructures/dataframe.h>

#include <modules/plotting/properties/axisproperty.h>
#include <modules/plotting/properties/axisstyleproperty.h>

#include <modules/plottinggl/plottingglmoduledefine.h>
#include <modules/plottinggl/utils/axisrenderer.h>

#include <modules/basegl/baseglmoduledefine.h>




namespace inviwo {

class IVW_MODULE_GRAPH2D_API Plot2dProcessor : public Processor {
public:

    Plot2dProcessor();
    virtual ~Plot2dProcessor() = default;
    virtual const ProcessorInfo getProcessorInfo() const override;

    virtual void process() override;

    static const ProcessorInfo processorInfo_;

private:
	DataInport<DataFrame, 1, false> inport_;
	ImageInport imageInport_;
    ImageOutport outport_;

    OptionPropertyString xAxisSelection_;
	OptionPropertyString yAxisSelection_;

    plot::AxisProperty xAxis_;
	plot::AxisProperty yAxis_;

	BoolProperty toggle3d_;
	FloatVec3Property position_;
	FloatVec2Property size_;

    CameraProperty camera_;
	//OrthographicCamera camera2d_;
	std::unique_ptr<Camera> camera2d_;

    CameraTrackball trackball_;

    std::vector<plot::AxisRenderer3D> axisRenderers_;
	MeshDrawerGL lineDrawer_;

	void reloadDatasets();
	void updateAxis();

};

}  // namespace inviwo

#endif  // IVW_VOLUMEAXIS_H
