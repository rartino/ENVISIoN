/*********************************************************************************
 *
 * Copyright (c) 2017-2018 Robert Cranston, Viktor Bernholtz
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

#include <modules/graph2d/processors/functionoperationunary.h>

#include <inviwo/core/common/inviwo.h>
#include <modules/plotting/datastructures/column.h>

using inviwo::plot::TemplateColumn;
using inviwo::plot::Column;

namespace inviwo {

const ProcessorInfo FunctionOperationUnary::processorInfo_ {
        "org.inviwo.FunctionOperationUnary",    // Class identifier.
        "Function Operation Unary",             // Display name.
        "Graphing",                             // Category.
        CodeState::Stable,                      // Code state.
        Tags::None,                             // Tags.
    };

const ProcessorInfo FunctionOperationUnary::getProcessorInfo() const {
    return processorInfo_;
}

FunctionOperationUnary::FunctionOperationUnary()
    : Processor()
    , operationVector_ {
            {
                    "negate",
                    "Negate",
                    "Negated",
                    "-",
                    [](float value) { return -value; },
                },
            {
                    "invert",
                    "Invert",
                    "Inverted",
                    "1/",
                    [](float value) { return 1.0f / value; },
                },
        }
    , operationProperty_("operationProperty", "Operation")
    , dataframeOutport_("dataframeOutport")
    , dataframeInport_("dataframeInport")
{

    addPort(dataframeOutport_);

    addPort(dataframeInport_);

    addProperty(operationProperty_);

    std::vector<OptionPropertyStringOption> operationPropertyOptionVector;
    for (const auto& operation : operationVector_) {
        operationPropertyOptionVector.emplace_back(
                operation.identifier,
                operation.displayName,
                operation.identifier
            );
    }
    operationProperty_.replaceOptions(operationPropertyOptionVector);
}

void FunctionOperationUnary::process() {

    std::shared_ptr<const DataFrame> inData = dataframeInport_.getData();

    const auto& operation = *std::find_if(
            operationVector_.begin(),
            operationVector_.end(),
            [this](const Operation& operation) {
                    return operation.identifier == operationProperty_.getSelectedIdentifier();
                }
        );

    std::shared_ptr<DataFrame> dataFrame = std::make_shared<DataFrame>(0);
    for (const std::shared_ptr<const Column>& column : *inData) {
        if (column->getHeader() == "X") {
            std::shared_ptr<TemplateColumn<float> > x = dataFrame->addColumn<float>("X", 0);
            for (size_t i = 0; i < column->getSize(); i++) {
                x->add(column->getAsDouble(i));
            }
        } else if (column->getHeader() == "Y") {
            std::shared_ptr<TemplateColumn<float> > y = dataFrame->addColumn<float>("Y", 0);
            for (size_t i = 0; i < column->getSize(); i++) {
                y->add(operation.apply(column->getAsDouble(i)));
            }
        }
    }

    dataframeOutport_.setData(dataFrame);

    /*
    for (const auto& functionSharedPtr : functionSharedPtrVector) {

        Axis xAxis = functionSharedPtr->xAxis;

        Axis yAxis;

        if (!functionSharedPtr->yAxis.variableInfo.variableName.empty()) {
            yAxis.variableInfo.variableName =
                functionSharedPtr->yAxis.variableInfo.variableName + " " + operation.resultName;
        }
        if (!functionSharedPtr->yAxis.variableInfo.variableSymbol.empty()) {
            yAxis.variableInfo.variableSymbol =
                operation.resultSymbol + functionSharedPtr->yAxis.variableInfo.variableSymbol;
        }
        if (operation.identifier == "negate") {
            yAxis.variableInfo.quantityName =
                functionSharedPtr->yAxis.variableInfo.quantityName;
            yAxis.variableInfo.quantitySymbol =
                functionSharedPtr->yAxis.variableInfo.quantitySymbol;
            yAxis.variableInfo.unit =
                functionSharedPtr->yAxis.variableInfo.unit;
        } else {
            LogProcessorInfo(
                    std::string()
                    + "Dropped variable info for"
                    + " "
                    + yAxis.variableInfo.variableName
                );
        }

        yAxis.valueVector = functionSharedPtr->yAxis.valueVector;
        for (auto&& value : yAxis.valueVector)
            value = operation.apply(value);

        functionVectorSharedPtr->emplace_back(Function {
                std::move(xAxis),
                std::move(yAxis),
            });

    }*/

}

} // namespace

