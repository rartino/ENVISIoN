/************************************************************************
 *   This file was created 2019 by Abdullatif Ismail
 *
 *   To the extent possible under law, the person who associated CC0
 *   with the alterations to this file has waived all copyright and
 *   related or neighboring rights to the alterations made to this file.
 *
 *   You should have received a copy of the CC0 legalcode along with
 *   this work.  If not, see
 *   <http://creativecommons.org/publicdomain/zero/1.0/>.
 ************************************************************************/

#include <modules/graph2d/processors/dataframecollector.h>
#include <inviwo/core/common/inviwo.h>

using inviwo::TemplateColumn;

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
