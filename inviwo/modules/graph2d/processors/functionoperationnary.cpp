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
/*
 *   Alterations to this file by Viktor Bernholtz
 *
 *   To the extent possible under law, the person who associated CC0
 *   with the alterations to this file has waived all copyright and
 *   related or neighboring rights to the alterations made to this file.
 *
 *   You should have received a copy of the CC0 legalcode along with
 *   this work.  If not, see
 *   <http://creativecommons.org/publicdomain/zero/1.0/>.
 */

#include <modules/graph2d/processors/functionoperationnary.h>

#include <inviwo/core/common/inviwo.h>

#include <modules/graph2d/util/stringcomparenatural.h>

using inviwo::plot::TemplateColumn;

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
    , dataframeOutport_("dataframeOutport")
{

    addPort(functionFlatMultiInport_);

    addProperty(operationProperty_);
    addProperty(undefinedFallbackProperty_);
    addProperty(sampleFilterEnableProperty_);
    addProperty(sampleFilterEpsilonProperty_);

    addPort(dataframeOutport_);

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

    const auto& functionSharedPtrVector = functionFlatMultiInport_.getVectorData();

    const auto& operation = *std::find_if(
            operationVector_.begin(),
            operationVector_.end(),
            [this](const Operation& operation) {
                    return operation.identifier == operationProperty_.getSelectedIdentifier();
                }
        );


    if (!functionSharedPtrVector.empty()) {

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

        // Filter x axis data.
        if (!sampleFilterEnableProperty_.get()) {
            xAxis.valueVector.swap(xAxisData);
        } else {
            const auto& sampleFilterEpsilon = sampleFilterEpsilonProperty_.get();
            auto lastValue = -std::numeric_limits<float>::infinity();
            std::copy_if(
                    xAxisData.begin(),
                    xAxisData.end(),
                    std::back_inserter(xAxis.valueVector),
                    [&sampleFilterEpsilon, &lastValue](const auto& value) {
                            if (value <= lastValue + sampleFilterEpsilon)
                                return false;
                            lastValue = value;
                            return true;
                        }
                );
        }

        // Define y axis.
        Axis yAxis;

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
                        return tokenize(functionSharedPtr->yAxis.variableInfo.variableName);
                    }
            );
        std::vector<std::string> resultVariableNameTokenVector;
        const auto& referenceVariableNameTokenVector = variableNameTokenVectorVector.front();
        std::copy_if(
                referenceVariableNameTokenVector.begin(),
                referenceVariableNameTokenVector.end(),
                std::back_inserter(resultVariableNameTokenVector),
                [&variableNameTokenVectorVector, indexBase = size_t(0)](
                        const auto& referenceVariableNameToken
                    ) mutable {
                        const auto& index = indexBase++;
                        return std::all_of(
                                variableNameTokenVectorVector.begin(),
                                variableNameTokenVectorVector.end(),
                                [&referenceVariableNameToken, &index](
                                        const auto& variableNameTokenVector
                                    ) {
                                        return
                                            index < variableNameTokenVector.size()
                                            && variableNameTokenVector[index] ==
                                                referenceVariableNameToken;
                                    }
                            );
                    }
            );
        std::string last;
        for (const auto& token : resultVariableNameTokenVector) {
            if (!((last == "" || last == "-" || last == " ") && (token == "-" || token == " ")))
                yAxis.variableInfo.variableName += token;
            last = token;
        }
        if (!yAxis.variableInfo.variableName.empty())
            yAxis.variableInfo.variableName += " ";
        yAxis.variableInfo.variableName += operation.resultName;

        // Set y axis variable symbol.
        std::vector<std::string> variableSymbolVector;
        std::transform(
                functionSharedPtrVector.begin(),
                functionSharedPtrVector.end(),
                std::back_inserter(variableSymbolVector),
                [](const auto& functionSharedPtr) {
                        return functionSharedPtr->yAxis.variableInfo.variableSymbol;
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
                if (!yAxis.variableInfo.variableSymbol.empty())
                    yAxis.variableInfo.variableSymbol += " " + operation.resultSymbol + " ";
                yAxis.variableInfo.variableSymbol += variableSymbol;
            }
        }

        // Set other y axis properties.
        if (operation.identifier == "add") {
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
        } else {
            LogProcessorInfo(
                    std::string()
                    + "Dropped variable info for"
                    + " "
                    + yAxis.variableInfo.variableName
                );
        }

        // Define help functions.
        const auto& undefinedFallback = undefinedFallbackProperty_.getSelectedIdentifier();
        const auto& evaluate = [&undefinedFallback](const Function& function, const float& xValue) {
                const auto& xData = function.xAxis.valueVector;
                const auto& yData = function.yAxis.valueVector;
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
        yAxis.valueVector.reserve(xAxis.valueVector.size());
        std::generate_n(
                std::back_inserter(yAxis.valueVector),
                xAxis.valueVector.size(),
                [
                        &operation,
                        &evaluate,
                        &functionSharedPtrVector,
                        xDataIter = xAxis.valueVector.begin()
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

        std::shared_ptr<DataFrame> frame = std::make_shared<DataFrame>(0);
        std::shared_ptr<TemplateColumn<float> > x = frame->addColumn<float>("X", 0);
        for (float value : xAxis.valueVector) {
            x->add(value);
        }

        std::shared_ptr<TemplateColumn<float> > y = frame->addColumn<float>("Y", 0);
        for (float value : yAxis.valueVector) {
            y->add(value);
        }


        dataframeOutport_.setData(frame);
    }
}

} // namespace

