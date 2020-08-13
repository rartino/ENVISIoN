#include <modules/graph2d/graph2dmodule.h>
#include <modules/graph2d/processors/hdf5todataframe.h>

namespace inviwo {

graph2dModule::graph2dModule(InviwoApplication* app) : InviwoModule(app, "graph2d") {

    // Processors.
    registerProcessor<HDF5ToDataframe>();

    // Ports.
}

} // namespace
