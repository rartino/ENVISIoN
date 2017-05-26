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

#include <modules/graph2d/processors/functionoperationnary.h>

#include <inviwo/core/common/inviwo.h>

namespace inviwo {

const ProcessorInfo FunctionOperationNary::processorInfo_ {
        "org.inviwo.FunctionOperationNary", // Class identifier.
        "Function Operation Nary",          // Display name.
        "Graphing",                         // Category.
        CodeState::Stable,                  // Code state.
        Tags::None,                         // Tags.
    };

const ProcessorInfo FunctionOperationNary::getProcessorInfo() const {
    return processorInfo_;
}

FunctionOperationNary::FunctionOperationNary()
    : Processor()
    , operationVector_ {
            {
                    "add",
                    "Add",
                    "Added",
                    "+",
                    [](float partial, float value) { return partial + value; },
                },
            {
                    "multiply",
                    "Multiply",
                    "Multiplied",
                    "\\cdot ",
                    [](float partial, float value) { return partial * value; },
                },
        }
    , functionFlatMultiInport_("functionFlatMultiInport")
    , operationProperty_("operationProperty", "Operation")
    , undefinedFallbackProperty_("undefinedFallbackProperty", "Undefined fallback")
    , sampleFilterEnableProperty_("sampleFilterEnableProperty", "Enable sample filter", true)
    , sampleFilterEpsilonProperty_("sampleFilterEpsilonProperty", "Sample filter epsilon", 0.0f)
    , functionVectorOutport_("functionVectorOutport")
{

    addPort(functionFlatMultiInport_);

    addProperty(operationProperty_);
    addProperty(undefinedFallbackProperty_);
    addProperty(sampleFilterEnableProperty_);
    addProperty(sampleFilterEpsilonProperty_);

    addPort(functionVectorOutport_);

    std::vector<OptionPropertyStringOption> operationPropertyOptionVector;
    for (const auto& operation : operationVector_) {
        operationPropertyOptionVector.emplace_back(
                operation.identifier,
                operation.displayName,
                operation.identifier
            );
    }
    operationProperty_.replaceOptions(operationPropertyOptionVector);

    undefinedFallbackProperty_.replaceOptions({
            { "zero", "Zero", "zero" },
            { "extend", "Extend", "extend" },
        });

    const auto& onSampleFilterEnablePropertyChange = [this]() {
            sampleFilterEpsilonProperty_.setVisible(sampleFilterEnableProperty_.get());
        };
    onSampleFilterEnablePropertyChange();
    sampleFilterEnableProperty_.onChange(onSampleFilterEnablePropertyChange);
}

void FunctionOperationNary::process() {

    const auto& functionVectorSharedPtr = std::make_shared<std::vector<Function>>();
    functionVectorOutport_.setData(functionVectorSharedPtr);

    const auto& functionSharedPtrVector = functionFlatMultiInport_.getVectorData();

    const auto& operation = *std::find_if(
            operationVector_.begin(),
            operationVector_.end(),
            [this](const Operation& operation) {
                    return operation.identifier == operationProperty_.getSelectedIdentifier();
                }
        );

    std::vector<Function> resultFunctionVector;

    if (!functionSharedPtrVector.empty()) {

        // Define x axis.
        Function::Axis xAxis;

        // Set x axis properties.
        // TODO: We just assume all the properties are the same for all the inputs.
        const auto& functionXAxis = functionSharedPtrVector.front()->xAxis;
        xAxis.variableName = functionXAxis.variableName;
        xAxis.variableSymbol = functionXAxis.variableSymbol;
        xAxis.quantityName = functionXAxis.quantityName;
        xAxis.quantitySymbol = functionXAxis.quantitySymbol;
        xAxis.unit = functionXAxis.unit;

        // Gather x axis data.
        std::vector<float> xAxisData;
        xAxisData.reserve(std::accumulate(
                functionSharedPtrVector.begin(),
                functionSharedPtrVector.end(),
                0,
                [](const auto& size, const auto& functionSharedPtr) {
                        return size + functionSharedPtr->xAxis.data.size();
                    }
            ));
        for (const auto& functionSharedPtr : functionSharedPtrVector) {
            std::copy(
                    functionSharedPtr->xAxis.data.begin(),
                    functionSharedPtr->xAxis.data.end(),
                    std::back_inserter(xAxisData)
                );
        }
        std::sort(xAxisData.begin(), xAxisData.end());

        // Filter x axis data.
        if (!sampleFilterEnableProperty_.get()) {
            xAxis.data.swap(xAxisData);
        } else {
            const auto& sampleFilterEpsilon = sampleFilterEpsilonProperty_.get();
            auto lastValue = -std::numeric_limits<float>::infinity();
            std::copy_if(
                    xAxisData.begin(),
                    xAxisData.end(),
                    std::back_inserter(xAxis.data),
                    [&sampleFilterEpsilon, &lastValue](const auto& value) {
                            if (value <= lastValue + sampleFilterEpsilon)
                                return false;
                            lastValue = value;
                            return true;
                        }
                );
        }

        // Define y axis.
        Function::Axis yAxis;

        // Define help functions.
        const auto& tokenize = [](const auto& string) {
                std::vector<std::string> result;

                std::string::size_type indexStart = 0;
                std::string::size_type size = string.size();

                while(indexStart < size)
                {
                    auto index = string.find_first_of(" -({[<", indexStart);
                    if (index == indexStart) {
                        if (string.find_first_of("({[<", indexStart) == indexStart)
                            index = string.find_first_of(")}]>", indexStart) + 1;
                        else
                            index = string.find_first_not_of(" -", indexStart);
                    }
                    const auto& token = string.substr(indexStart, index - indexStart);
                    result.emplace_back(token);
                    indexStart = index;
                }

                return result;
            };

        // Set y axis variable name.
        std::vector<std::vector<std::string>> variableNameTokenVectorVector;
        std::transform(
                functionSharedPtrVector.begin(),
                functionSharedPtrVector.end(),
                std::back_inserter(variableNameTokenVectorVector),
                [&tokenize](const auto& functionSharedPtr) {
                        return tokenize(functionSharedPtr->yAxis.variableName);
                    }
            );
        std::vector<std::string> resultVariableNameTokenVector;
        const auto& referenceVariableNameTokenVector = variableNameTokenVectorVector.front();
        std::copy_if(
                referenceVariableNameTokenVector.begin(),
                referenceVariableNameTokenVector.end(),
                std::back_inserter(resultVariableNameTokenVector),
                [&variableNameTokenVectorVector, indexBase = size_t(0)](
                        const auto& referenceVariableWord
                    ) mutable {
                        const auto& index = indexBase++;
                        return std::all_of(
                                variableNameTokenVectorVector.begin(),
                                variableNameTokenVectorVector.end(),
                                [&referenceVariableWord, &index](const auto& variableWordVector) {
                                        return
                                            index < variableWordVector.size()
                                            && variableWordVector[index] == referenceVariableWord;
                                    }
                            );
                    }
            );
        if (std::all_of(
                resultVariableNameTokenVector.begin(),
                resultVariableNameTokenVector.end(),
                [](const auto& resultVariableNameToken) {
                        return !resultVariableNameToken.empty();
                    }
            )
        ) {
            std::string last;
            for (const auto& token : resultVariableNameTokenVector) {
                if (!((last == "" || last == "-" || last == " ") && (token == "-" || token == " ")))
                    yAxis.variableName += token;
                last = token;
            }
            if (!yAxis.variableName.empty())
                yAxis.variableName += " ";
            yAxis.variableName += operation.resultName;
        }

        // Set y axis variable symbol.
        std::vector<std::string> variableSymbolVector;
        std::transform(
                functionSharedPtrVector.begin(),
                functionSharedPtrVector.end(),
                std::back_inserter(variableSymbolVector),
                [](const auto& functionSharedPtr) {
                        return functionSharedPtr->yAxis.variableSymbol;
                    }
            );
        if (std::all_of(
                variableSymbolVector.begin(),
                variableSymbolVector.end(),
                [](const auto& variableSymbol) {
                        return !variableSymbol.empty();
                    }
            )
        ) {
            for (const auto& variableSymbol : variableSymbolVector) {
                if (!yAxis.variableSymbol.empty())
                    yAxis.variableSymbol += " " + operation.resultSymbol + " ";
                yAxis.variableSymbol += variableSymbol;
            }
        }

        // Set other y axis properties.
        // TODO: We just assume all the properties are the same for all the inputs.
        if (operation.identifier == "add") {
            const auto& functionYAxis = functionSharedPtrVector.front()->yAxis;
            yAxis.quantityName = functionYAxis.quantityName;
            yAxis.quantitySymbol = functionYAxis.quantitySymbol;
            yAxis.unit = functionYAxis.unit;
        }

        // Define help functions.
        const auto& undefinedFallback = undefinedFallbackProperty_.getSelectedIdentifier();
        const auto& evaluate = [&undefinedFallback](const Function& function, const float& xValue) {
                const auto& xData = function.xAxis.data;
                const auto& yData = function.yAxis.data;
                const auto& lower_iter = std::lower_bound(xData.begin(), xData.end(), xValue);
                const auto& upper_iter = std::upper_bound(xData.begin(), xData.end(), xValue);
                if (lower_iter == xData.end()) {
                    if (undefinedFallback == "zero") return 0.0f;
                    else if (undefinedFallback == "extend") return yData.front();
                }
                if (upper_iter == xData.end()) {
                    if (undefinedFallback == "zero") return 0.0f;
                    else if (undefinedFallback == "extend") return yData.back();
                }
                const auto& lower_index = std::distance(xData.begin(), lower_iter);
                const auto& upper_index = std::distance(xData.begin(), upper_iter);
                return yData[lower_index]
                    + (yData[upper_index] - yData[lower_index])
                        * (xValue - xData[lower_index]) / (xData[upper_index] - xData[lower_index]);
            };

        // Calculate y axis data.
        yAxis.data.reserve(xAxis.data.size());
        std::generate_n(
                std::back_inserter(yAxis.data),
                xAxis.data.size(),
                [
                        &operation,
                        &evaluate,
                        &functionSharedPtrVector,
                        xDataIter = xAxis.data.begin()
                    ]() mutable {
                        const auto& xValue = *xDataIter++;
                        return std::accumulate(
                                std::next(functionSharedPtrVector.begin()),
                                functionSharedPtrVector.end(),
                                evaluate(**functionSharedPtrVector.begin(), xValue),
                                [&operation, &evaluate, &xValue](
                                        const auto& yValuePartial,
                                        const auto& functionSharedPtr
                                    ) {
                                        return operation.reducePartial(
                                                yValuePartial,
                                                evaluate(*functionSharedPtr, xValue)
                                            );
                                    }
                            );
                    }
            );

        functionVectorSharedPtr->emplace_back(Function {
                std::move(xAxis),
                std::move(yAxis)
            });
    }
}

} // namespace

