#include <modules/graph2d/graph2dmodule.h>
#include <modules/graph2d/processors/hdf5todataframe.h>
#include <modules/graph2d/processors/plot2d.h>

namespace inviwo {

graph2dModule::graph2dModule(InviwoApplication* app) : InviwoModule(app, "graph2d") {

    // Processors.
    registerProcessor<HDF5ToDataframe>();
    registerProcessor<Plot2dProcessor>();

    // Ports.
}

} // namespace
