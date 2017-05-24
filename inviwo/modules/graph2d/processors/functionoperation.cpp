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

#include <modules/graph2d/processors/functionoperation.h>

#include <inviwo/core/common/inviwo.h>

namespace inviwo {

const ProcessorInfo FunctionOperation::processorInfo_ {
        "org.inviwo.FunctionOperation", // Class identifier.
        "Function Operation",           // Display name.
        "Graphing",                     // Category.
        CodeState::Stable,              // Code state.
        Tags::None,                     // Tags.
    };

const ProcessorInfo FunctionOperation::getProcessorInfo() const {
    return processorInfo_;
}

FunctionOperation::FunctionOperation()
    : Processor()
    , lhsFunctionInport_("lhsFunctionInport")
    , rhsFunctionFlatMultiInport_("rhsFunctionFlatMultiInport")
    , operationProperty_("operationProperty", "Operation")
    , samplingEpsilonProperty_("samplingEpsilonProperty", "Sampling epsilon", 0.0f)
    , nameModificationTypeProperty_("nameModificationTypeProperty", "Name modification type")
    , nameModificationProperty_("nameModificationProperty", "Name modification", "")
    , functionOutport_("functionOutport")
{
    addPort(lhsFunctionInport_);
    addPort(rhsFunctionFlatMultiInport_);

    lhsFunctionInport_.setOptional(true);

    addProperty(operationProperty_);
    addProperty(nameModificationTypeProperty_);
    addProperty(samplingEpsilonProperty_);

    operationProperty_.replaceOptions({
            { "add", "Add", "add" },
            { "subtract", "Subtract", "subtract" },
            { "multiply", "Multiply", "multiply" },
            { "divide", "Divide", "divide" },
        });
    nameModificationTypeProperty_.replaceOptions({
            { "none", "None", "none" },
            { "prepend", "Prepend", "prepend" },
            { "replace", "Replace", "replace" },
        });
    const auto& onNameModificationTypePropertyChange = [this]() {
            const auto& visible = nameModificationTypeProperty_.getSelectedIdentifier() != "none";
            nameModificationProperty_.setVisible(visible);
            std::cout << "nameModificationProperty_.setVisible(visible)" << " " << visible << std::endl;
        };
    onNameModificationTypePropertyChange();
    nameModificationTypeProperty_.onChange(onNameModificationTypePropertyChange);

    addPort(functionOutport_);
}

void FunctionOperation::process() {

    const auto& rhsFunctionSharedPtrVector = rhsFunctionFlatMultiInport_.getVectorData();
    const auto& lhsFunctionSharedPtr = lhsFunctionInport_.getData();
    std::cout << "DEBUG: FunctionOperation: rhsFunctionSharedPtrVector.size()" << rhsFunctionSharedPtrVector.size() << std::endl;

    std::vector<float> xAxisData;
    xAxisData.reserve(
            (lhsFunctionSharedPtr ? lhsFunctionSharedPtr->x.data.size() : 0)
            + std::accumulate(
                    rhsFunctionSharedPtrVector.begin(),
                    rhsFunctionSharedPtrVector.end(),
                    0,
                    [](const auto& size, const auto& functionSharedPtr) {
                            return size + functionSharedPtr->x.data.size();
                        }
                )
        );
    if (lhsFunctionSharedPtr)
        std::copy(
                lhsFunctionSharedPtr->x.data.begin(),
                lhsFunctionSharedPtr->x.data.begin(),
                std::back_inserter(xAxisData)
            );
    for (const auto& rhsFunctionSharedPtr : rhsFunctionSharedPtrVector) {
        std::copy(
                rhsFunctionSharedPtr->x.data.begin(),
                rhsFunctionSharedPtr->x.data.end(),
                std::back_inserter(xAxisData)
            );
    }
    std::sort(xAxisData.begin(), xAxisData.end());
    std::cout << "DEBUG: FunctionOperation: xAxisData.size()" << xAxisData.size() << std::endl;

    Function::Axis xAxis;
    const auto& samplingEpsilon = samplingEpsilonProperty_.get();
    if (samplingEpsilon > 0.0f) {
        auto lastValue = -std::numeric_limits<float>::infinity();
        std::copy_if(
                xAxisData.begin(),
                xAxisData.end(),
                std::back_inserter(xAxis.data),
                [&samplingEpsilon, &lastValue](const auto& value) {
                        if (value <= lastValue + samplingEpsilon)
                            return false;
                        lastValue = value;
                        return true;
                    }
            );
    } else {
        xAxis.data.swap(xAxisData);
    }
    std::cout << "DEBUG: FunctionOperation: xAxis.data.size()" << xAxis.data.size() << std::endl;

    const auto& evaluate = [](const auto& functionSharedPtr, const auto& xValue) {
            const auto& xData = functionSharedPtr->x.data;
            const auto& yData = functionSharedPtr->y.data;
            if (xValue < xData.front() || xData.back() <= xValue)
                return 0.0f; // TODO: undefinedFallbackProperty_.get()
            const auto& index1 = std::distance(
                    xData.begin(),
                    std::lower_bound(
                            xData.begin(),
                            xData.end(),
                            xValue
                        )
                );
            const auto& index2 = index1 + 1;
            return yData[index1]
                + (yData[index2] - yData[index1])
                    * (xValue - xData[index1]) / (xData[index2] - xData[index1]);
        };

    auto operationInfo =
        std::map<std::string, std::tuple<std::function<float(float, float)>, float, std::string>> {
            { "add", std::make_tuple(std::plus<>(), 0.0f, "+") },
            { "subtract", std::make_tuple(std::minus<>(), 0.0f, "-") },
            { "multiply", std::make_tuple(std::multiplies<>(), 1.0f, "*") },
            { "divide", std::make_tuple(std::divides<>(), 1.0f, "/") },
        }[operationProperty_.get()];
    const auto& operation = std::get<0>(operationInfo);
    const auto& operationIdentity = std::get<1>(operationInfo);
    const auto& operationSymbol = std::get<2>(operationInfo);

    Function::Axis yAxis;

    if (nameModificationTypeProperty_.getSelectedIdentifier() == "none") {

        auto begin = rhsFunctionSharedPtrVector.begin();
        auto end = rhsFunctionSharedPtrVector.end();
        for(auto it = begin; it != end; ++it) {
            if (it != begin)
                yAxis.variableName += " " + operationSymbol + " ";
            yAxis.variableName += (*it)->y.variableName;
        }

    } else if(nameModificationTypeProperty_.getSelectedIdentifier() == "prepend") {

        const auto& longestCommonPrefix = [](const auto& stringVector) {
                if(stringVector.size() == 0)
                    return std::string();
                const auto& referenceString = stringVector.front();
                size_t index = 0;
                while(std::all_of(
                        stringVector.begin(),
                        stringVector.end(),
                        [&index, &referenceString](const auto& string) {
                                return string[index] == referenceString[index];
                            }
                    )
                ) {
                    ++index;
                }
                return referenceString.substr(0, index);
            };
        std::vector<std::string> functionYVariableNameVector;
        std::transform(
                rhsFunctionSharedPtrVector.begin(),
                rhsFunctionSharedPtrVector.end(),
                functionYVariableNameVector.begin(),
                [](const auto& rhsFunctionSharedPtr) { return rhsFunctionSharedPtr->y.variableName; }
            );
        yAxis.variableName = nameModificationProperty_.get()
            + longestCommonPrefix(functionYVariableNameVector);

    } else if(nameModificationTypeProperty_.getSelectedIdentifier() == "replace") {

        yAxis.variableName = nameModificationProperty_.get();

    }

    yAxis.data.resize(xAxis.data.size()); // TODO: reserve?
    auto xDataIter = xAxis.data.begin();
    std::generate_n(
            yAxis.data.begin(),
            xAxis.data.size(),
            [&operation, &operationIdentity, &evaluate, &lhsFunctionSharedPtr, &rhsFunctionSharedPtrVector, &xDataIter]() {
                    const auto& xValue = *xDataIter++;
                    return std::accumulate(
                            rhsFunctionSharedPtrVector.begin(),
                            rhsFunctionSharedPtrVector.end(),
                            lhsFunctionSharedPtr
                                ? evaluate(lhsFunctionSharedPtr, xValue)
                                : operationIdentity,
                            [&operation, &evaluate, &xValue](
                                    const auto& yValue,
                                    const auto& rhsFunctionSharedPtr
                                ) {
                                    return operation(
                                            yValue,
                                            evaluate(rhsFunctionSharedPtr, xValue)
                                        );
                                }
                        );
                }
        );
    std::cout << "DEBUG: FunctionOperation: yAxis.data.size()" << yAxis.data.size() << std::endl;

    functionOutport_.setData(std::make_shared<Function>(Function {
            std::move(xAxis),
            std::move(yAxis)
        }));
}

} // namespace

