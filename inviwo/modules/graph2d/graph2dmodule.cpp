/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2017 Inviwo Foundation
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *********************************************************************************/

#include <modules/graph2d/graph2dmodule.h>

#include <modules/graph2d/datastructures/function.h>
#include <modules/graph2d/processors/hdf5pathselectionint.h>
#include <modules/graph2d/processors/hdf5pathselectionintvector.h>
#include <modules/graph2d/processors/hdf5pathselectionallchildren.h>
#include <modules/graph2d/processors/hdf5tofunction.h>
#include <modules/graph2d/processors/functionoperation.h>
#include <modules/graph2d/processors/plotter.h>

namespace inviwo {

graph2dModule::graph2dModule(InviwoApplication* app) : InviwoModule(app, "graph2d") {   

    // Processors.
    registerProcessor<HDF5PathSelectionInt>();
    registerProcessor<HDF5PathSelectionIntVector>();
    registerProcessor<HDF5PathSelectionAllChildren>();
    registerProcessor<HDF5ToFunction>();
    registerProcessor<FunctionOperation>();
    registerProcessor<Plotter>();
    
    // Ports.
    registerPort<DataOutport<Function>>("FunctionOutport");
    registerPort<DataInport<Function>>("FunctionInport");
}

} // namespace
