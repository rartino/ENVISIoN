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

#include <modules/graph2d/processors/functiontodataframe.h>
#include <inviwo/core/common/inviwo.h>

using inviwo::TemplateColumn;

namespace inviwo {

const ProcessorInfo FunctionToDataFrame::processorInfo_ {
        "org.inviwo.FunctionToDataFrame",   // Class identifier.
        "Function To Data Frame",           // Display name.
        "Graphing",                         // Category.
        CodeState::Experimental,            // Code state.
        "Function", "Graphing",             // Tags.
};

const ProcessorInfo FunctionToDataFrame::getProcessorInfo() const {
    return processorInfo_;
}

FunctionToDataFrame::FunctionToDataFrame()
    : Processor()
    , functionFlatMultiInport_("functionFlatMultiInport")
    , dataframeOutport_("dataframeOutport") {

    addPort(functionFlatMultiInport_);
    addPort(dataframeOutport_);
}

void FunctionToDataFrame::process() {
    const auto& functionSharedPtrVector = functionFlatMultiInport_.getVectorData();
    if (functionSharedPtrVector.empty()) {
        LogError("Inport Doesn't contain data.");
        return;
    }

    // Define x axis.
    Axis xAxis;

    // Set x axis variable info.
    xAxis.variableInfo = functionSharedPtrVector.front()->xAxis.variableInfo;
    if (!std::all_of(
            functionSharedPtrVector.begin(),
            functionSharedPtrVector.end(),
            [&xAxis](const auto& functionSharedPtr) {
                return
                        functionSharedPtr->xAxis.variableInfo.variableName ==
                        xAxis.variableInfo.variableName
                        && functionSharedPtr->xAxis.variableInfo.variableSymbol ==
                           xAxis.variableInfo.variableSymbol
                        && functionSharedPtr->xAxis.variableInfo.quantityName ==
                           xAxis.variableInfo.quantityName
                        && functionSharedPtr->xAxis.variableInfo.quantitySymbol ==
                           xAxis.variableInfo.quantitySymbol
                        && functionSharedPtr->xAxis.variableInfo.unit ==
                           xAxis.variableInfo.unit;
            }
    )
            ) {
        LogProcessorWarn("Not all functions have the same x axis variable info");
    }

    // Gather x axis data.
    std::vector<float> xAxisData;
    xAxisData.reserve(std::accumulate(
            functionSharedPtrVector.begin(),
            functionSharedPtrVector.end(),
            0,
            [](const auto& size, const auto& functionSharedPtr) {
                return size + functionSharedPtr->xAxis.valueVector.size();
            }
    ));
    for (const auto& functionSharedPtr : functionSharedPtrVector) {
        std::copy(
                functionSharedPtr->xAxis.valueVector.begin(),
                functionSharedPtr->xAxis.valueVector.end(),
                std::back_inserter(xAxisData)
        );
    }
    std::sort(xAxisData.begin(), xAxisData.end());

    std::shared_ptr<DataFrame> frame = std::make_shared<DataFrame>(0);
    std::shared_ptr<TemplateColumn<float> > x = frame->addColumn<float>("X", 0);
    for (float value : functionSharedPtrVector.at(0)->xAxis.valueVector) {
        x->add(value);
    }

    // Define y axis.
    Axis yAxis;

    // Set y axis variable info.
    yAxis.variableInfo.quantityName =
            functionSharedPtrVector.front()->yAxis.variableInfo.quantityName;
    yAxis.variableInfo.quantitySymbol =
            functionSharedPtrVector.front()->yAxis.variableInfo.quantitySymbol;
    yAxis.variableInfo.unit =
            functionSharedPtrVector.front()->yAxis.variableInfo.unit;
    if (!std::all_of(
            functionSharedPtrVector.begin(),
            functionSharedPtrVector.end(),
            [&yAxis](const auto& functionSharedPtr) {
                return
                        functionSharedPtr->yAxis.variableInfo.quantityName ==
                        yAxis.variableInfo.quantityName
                        && functionSharedPtr->yAxis.variableInfo.quantitySymbol ==
                           yAxis.variableInfo.quantitySymbol
                        && functionSharedPtr->yAxis.variableInfo.unit ==
                           yAxis.variableInfo.unit;
            }
    )
            ) {
        LogProcessorWarn("Not all functions have the same y axis variable info");
    }

    // Add y axis data.
    yAxis.valueVector.reserve(xAxis.valueVector.size());
    for (size_t column = 0; column < functionSharedPtrVector.size(); column++) {
        std::stringstream ss;
        ss << functionSharedPtrVector.at(column)->yAxis.variableInfo.variableName;
        std::shared_ptr<TemplateColumn<float> > y = frame->addColumn<float>(ss.str(), 0);
        for (float value : functionSharedPtrVector.at(column)->yAxis.valueVector) {
            y->add(value);
        }
    }
    dataframeOutport_.setData(frame);
}

}
