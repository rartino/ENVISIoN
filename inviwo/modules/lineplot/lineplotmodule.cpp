#include <modules/lineplot/lineplotmodule.h>
#include <modules/lineplot/processors/hdf5todataframe.h>
#include <modules/lineplot/processors/lineplotprocessor.h>

namespace inviwo {

lineplotModule::lineplotModule(InviwoApplication* app) : InviwoModule(app, "lineplot") {

    // Processors.
    registerProcessor<HDF5ToDataframe>();
    registerProcessor<LinePlotProcessor>();

    // Ports.
}

} // namespace
