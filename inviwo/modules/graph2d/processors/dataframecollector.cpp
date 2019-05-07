/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2019 Abdullatif Ismail
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

#include <modules/graph2d/processors/dataframecollector.h>
#include <inviwo/core/common/inviwo.h>

using inviwo::plot::TemplateColumn;

namespace inviwo {

const ProcessorInfo DataFrameCollector::processorInfo_{
        "org.inviwo.DataFrameCollector",   // Class identifier.
        "Data Frame Collector",           // Display name.
        "Graphing",                         // Category.
        CodeState::Experimental,            // Code state.
        "Function", "Graphing",             // Tags.
};

const ProcessorInfo DataFrameCollector::getProcessorInfo() const {
    return processorInfo_;
}

DataFrameCollector::DataFrameCollector()
        : Processor(), dataframeInport_("dataframeMultiInport"), dataframeOutport_("dataframeOutport") {

    addPort(dataframeInport_);
    addPort(dataframeOutport_);
}

void DataFrameCollector::process() {
    const auto& inputFrameSharedPtrVector = dataframeInport_.getVectorData();
    std::shared_ptr<DataFrame> outportData = std::make_shared<DataFrame>(0);
    bool foundX {false};

    if (!inputFrameSharedPtrVector.size()) {
        LogError("Inport doesn't contain data.");
        return;
    }

    for (const auto& inputFrameSharedPtr : inputFrameSharedPtrVector) {
        for (size_t i = 0; i < inputFrameSharedPtr->getNumberOfColumns(); i++) {
            if (!foundX || inputFrameSharedPtr->getHeader(i) != "X") {
                if (inputFrameSharedPtr->getHeader(i) == "X") {
                    foundX = true;
                }
                std::shared_ptr<TemplateColumn<float>> col = outportData->addColumn<float>(inputFrameSharedPtr->getHeader(i), 0);
                for (size_t j = 0; j < inputFrameSharedPtr->getColumn(i)->getSize(); j++) {
                    col->add(inputFrameSharedPtr->getColumn(i)->getAsDouble(j));
                }
            }
        }

    }
    dataframeOutport_.setData(outportData);
}
}