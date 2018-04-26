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

#include "lineplotprocessor.h"

#include <inviwo/core/datastructures/geometry/basicmesh.h>
#include <inviwo/core/datastructures/buffer/bufferramprecision.h>
#include <modules/animation/datastructures/interpolation.h>

namespace inviwo {

using plot::DataFrame;
using plot::Column;

// The Class Identifier has to be globally unique. Use a reverse DNS naming scheme
const ProcessorInfo lineplotprocessor::processorInfo_{
    "org.inviwo.lineplotprocessor",      // Class identifier
    "lineplotprocessor",                // Display name
    "Undefined",              // Category
    CodeState::Experimental,  // Code state
    Tags::None,               // Tags
};
const ProcessorInfo lineplotprocessor::getProcessorInfo() const {
    return processorInfo_;
}

lineplotprocessor::lineplotprocessor()
    : Processor()
    , dataFrameInport_("dataFrameInport")
    , meshOutport_("outport")
    , position_("position", "Position", vec3(0.0f), vec3(-100.0f), vec3(100.0f)) {

    addPort(dataFrameInport_);
    addPort(meshOutport_);
    addProperty(position_);
}

void lineplotprocessor::process() {
    std::shared_ptr<BasicMesh> mesh = std::make_shared<BasicMesh>();
    IndexBufferRAM* indices = mesh->addIndexBuffer(DrawType::Lines, ConnectivityType::None);

    //auto p = Interpolation<vec3, float>::linear(vec3(0, 0, 0), , percent);


    std::shared_ptr<const DataFrame> inputFrame = dataFrameInport_.getData();

    // We want at least two columns. One named X and one named Y.
    if (inputFrame->getNumberOfColumns() >= 2) {
        std::shared_ptr<const Column> x = nullptr;
        std::shared_ptr<const Column> y = nullptr;
        for (size_t i = 0; i < inputFrame->getNumberOfColumns(); i++) {
            if (inputFrame->getHeader(i) == "X") {
                x = inputFrame->getColumn(i);
            } else if (inputFrame->getHeader(i) == "Y") {
                y = inputFrame->getColumn(i);
            }
        }

        if (!x) {
            LogError("Could not find any column named X in the DataFrame!");
            return;
        }

        if (!y) {
            LogError("Could not fin dany column named Y in the DataFrame!");
            return;
        }

        size_t y_size = y->getSize();
        size_t x_size = x->getSize();

        if (y_size != x_size) {
            LogError("The X and Y columns need to contain the same number"
                     " of values!");
        }

        // Each line segment should start on the current point and end
        // at the next point. Subtract one from the end criteria,
        // since the last point is included when the segment is drawn
        // from the next-to-last point.
        for (size_t i = 0; i < x_size - 1; i++) {
            double x_start = x->getAsDouble(i);
            double y_start = y->getAsDouble(i);
            double x_end = x->getAsDouble(i + 1);
            double y_end = y->getAsDouble(i + 1);

            vec3 start_point = vec3(x_start, y_start, 0);
            indices->add(mesh->addVertex(start_point, start_point,
                         start_point, vec4(255, 255, 255, 0)));

            vec3 end_point = vec3(x_end, y_end, 0);
            indices->add(mesh->addVertex(end_point, end_point,
                         end_point, vec4(255, 255, 255, 0)));
        }
    } else {
        LogInfo("This processor needs two columns to exist in the DataFrame."
                " One named X and one named Y.")
        return;
    }

    meshOutport_.setData(mesh);
}

} // namespace

