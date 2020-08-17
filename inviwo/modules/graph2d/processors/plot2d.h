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

#include <modules/opengl/shader/shader.h>
#include <modules/opengl/image/imagecompositor.h>
#include <inviwo/core/datastructures/geometry/mesh.h>
#include <modules/opengl/rendering/meshdrawergl.h>
#include <inviwo/core/datastructures/geometry/basicmesh.h>
#include <inviwo/core/ports/meshport.h>
#include <inviwo/core/rendering/meshdrawer.h>
#include <modules/opengl/shader/shader.h>
#include <inviwo/core/properties/simplelightingproperty.h>




namespace inviwo {

class IVW_MODULE_GRAPH2D_API Plot2dProcessor : public Processor {
public:

    Plot2dProcessor();
    virtual ~Plot2dProcessor() = default;
    virtual const ProcessorInfo getProcessorInfo() const override;


	virtual void initializeResources() override;
    virtual void process() override;

    static const ProcessorInfo processorInfo_;

private:
	DataInport<DataFrame, 1, false> inport_;
	ImageInport imageInport_;
    ImageOutport outport_;
	MeshOutport meshOutport_;

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


	//BasicMesh lineMesh_;
	//BasicMesh lineMesh_;
	std::shared_ptr<BasicMesh> lineMesh_;
	std::shared_ptr<IndexBufferRAM> indices_;
	std::unique_ptr<MeshDrawer> meshDrawer_;
	Shader shader_;
	SimpleLightingProperty lightingProperty_;
	Shader shader2d_;
	//Mesh lines_;
	//MeshDrawerGL lineDrawer_;
	//Shader lineShader_;

	vec3 origin_;
	double width_;
	double height_;
	Camera* activeCamera_;



	void reloadDatasets();
	void updateAxis();
	void rebuildMesh();

};

}  // namespace inviwo

#endif  // IVW_VOLUMEAXIS_H
