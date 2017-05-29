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

#include <modules/graph2d/processors/plotter.h>

#include <inviwo/core/common/inviwo.h>

#include <inviwo/core/util/indexmapper.h>
#include <inviwo/core/datastructures/image/image.h>
#include <inviwo/core/datastructures/image/layer.h>
#include <inviwo/core/datastructures/image/layerramprecision.h>

#include <modules/python3/pythonscript.h>
#include <modules/python3/pythoninterface/pyvalueparser.h>
#include <modules/python3/defaultinterface/utilities.h>

#include <modules/graph2d/util/stringcomparenatural.h>

namespace inviwo {

// The Class Identifier has to be globally unique. Use a reverse DNS naming scheme
const ProcessorInfo Plotter::processorInfo_{
        "org.inviwo.Plotter",       // Class identifier
        "Plotter",                  // Display name
        "Graphing",                 // Category
        CodeState::Stable,          // Code state
        Tags::None,                 // Tags
    };

const ProcessorInfo Plotter::getProcessorInfo() const {
    return processorInfo_;
}

Plotter::Plotter()
    : Processor()
    , functionFlatMultiInport_("functionFlatMultiInport")
    , markXFlatMultiInport_("markXFlatMultiInport")
    , markYFlatMultiInport_("markYFlatMultiInport")
    , sortOnNameProperty_("sortOnName", "Sort on name", true)
    , legendShowProperty_("legendShowProperty", "Show legend", true)
    , legendSymbolsProperty_("legendSymbolsProperty", "Use symbols in legend", false)
    , markShiftToZeroXProperty_("markShiftToZeroXProperty", "Shift x mark to zero")
    , markShiftToZeroYProperty_("markShiftToZeroYProperty", "Shift y mark to zero")
    , axisLimitAutoAdjustXProperty_(
            "axisLimitAutoAdjustXProperty",
            "Auto adjust x axis limit",
            true
        )
    , axisLimitXProperty_("axisLimitXProperty", "X axis limit")
    , axisLimitAutoAdjustYProperty_(
            "axisLimitAutoAdjustYProperty",
            "Auto adjust y axis limit",
            true
        )
    , axisLimitYProperty_("axisLimitYProperty", "Y axis limit")
    , imageOutport_("imageOutport", DataVec4UInt8::get())
{
    addPort(functionFlatMultiInport_);
    addPort(markXFlatMultiInport_);
    addPort(markYFlatMultiInport_);

    addProperty(sortOnNameProperty_);
    addProperty(legendShowProperty_);
    addProperty(legendSymbolsProperty_);
    addProperty(markShiftToZeroXProperty_);
    addProperty(markShiftToZeroYProperty_);
    addProperty(axisLimitAutoAdjustXProperty_);
    addProperty(axisLimitXProperty_);
    addProperty(axisLimitAutoAdjustYProperty_);
    addProperty(axisLimitYProperty_);

    addPort(imageOutport_);

    markXFlatMultiInport_.setOptional(true);
    markYFlatMultiInport_.setOptional(true);

    const auto& onMarkXFlatMultiInportChange = [this]() {
            std::vector<OptionPropertyStringOption> markShiftToZeroXPropertyOptionVector;
            markShiftToZeroXPropertyOptionVector.emplace_back("<none>", "<None>", "<none");
            for (const auto& markXSharedPtr : markXFlatMultiInport_.getVectorData()) {
                const auto& variableName = markXSharedPtr->variableInfo.variableName;
                markShiftToZeroXPropertyOptionVector.emplace_back(
                        variableName,
                        variableName,
                        variableName
                    );
            }
            markShiftToZeroXProperty_.replaceOptions(markShiftToZeroXPropertyOptionVector);

        };
    onMarkXFlatMultiInportChange();
    markXFlatMultiInport_.onChange(onMarkXFlatMultiInportChange);

    const auto& onMarkYFlatMultiInportChange = [this]() {
            std::vector<OptionPropertyStringOption> markShiftToZeroYPropertyOptionVector;
            markShiftToZeroYPropertyOptionVector.emplace_back("<none>", "<None>", "<none");
            for (const auto& markYSharedPtr : markYFlatMultiInport_.getVectorData()) {
                const auto& variableName = markYSharedPtr->variableInfo.variableName;
                markShiftToZeroYPropertyOptionVector.emplace_back(
                        variableName,
                        variableName,
                        variableName
                    );
            }
            markShiftToZeroYProperty_.replaceOptions(markShiftToZeroYPropertyOptionVector);

        };
    onMarkYFlatMultiInportChange();
    markYFlatMultiInport_.onChange(onMarkYFlatMultiInportChange);

    const auto& onaxisLimitAutoAdjustXPropertyChange = [this]() {
            const auto& visible = !axisLimitAutoAdjustXProperty_.get();
            axisLimitXProperty_.setVisible(visible);
        };
    onaxisLimitAutoAdjustXPropertyChange();
    axisLimitAutoAdjustXProperty_.onChange(onaxisLimitAutoAdjustXPropertyChange);

    const auto& onaxisLimitAutoAdjustYPropertyChange = [this]() {
            const auto& visible = !axisLimitAutoAdjustYProperty_.get();
            axisLimitYProperty_.setVisible(visible);
        };
    onaxisLimitAutoAdjustYPropertyChange();
    axisLimitAutoAdjustYProperty_.onChange(onaxisLimitAutoAdjustYPropertyChange);

    const auto& onLegendShowPropertyChange = [this]() {
            const auto& visible = legendShowProperty_.get();
            legendSymbolsProperty_.setVisible(visible);
        };
    onLegendShowPropertyChange();
    legendShowProperty_.onChange(onLegendShowPropertyChange);

}

void Plotter::process() {

    auto functionSharedPtrVector = functionFlatMultiInport_.getVectorData();
    auto markXSharedPtrVector = markXFlatMultiInport_.getVectorData();
    auto markYSharedPtrVector = markYFlatMultiInport_.getVectorData();

    if (sortOnNameProperty_.get()) {
        std::sort(
                functionSharedPtrVector.begin(),
                functionSharedPtrVector.end(),
                [](const auto& lhs, const auto& rhs){
                        return StringCompareNatural(
                                lhs->yAxis.variableInfo.variableName,
                                rhs->yAxis.variableInfo.variableName
                            );
                    }
            );
        }

    const auto& setPyValue = [](
            const auto& pyDict, const auto& name, const auto& value
        ) {
            const auto& valuePyObject = PyValueParser::toPyObject(value);
            PyDict_SetItemString(pyDict, name, valuePyObject);
            Py_DecRef(valuePyObject);
        };

    const auto& setPyList = [](
            const auto& pyDict, const auto& name, const auto& value
        ){
            auto valuePyList = utilpy::makePyList(value);
            PyDict_SetItemString(pyDict, name, valuePyList);
            Py_DecRef(valuePyList);
        };

    const auto& createVariableInfoPyDict = [&setPyValue](const auto& variableInfo) {
            const auto& variableInfoPyDict = PyDict_New();
            setPyValue(variableInfoPyDict, "variable_name", variableInfo.variableName);
            setPyValue(variableInfoPyDict, "variable_symbol", variableInfo.variableSymbol);
            setPyValue(variableInfoPyDict, "quantity_name", variableInfo.quantityName);
            setPyValue(variableInfoPyDict, "quantity_symbol", variableInfo.quantitySymbol);
            setPyValue(variableInfoPyDict, "unit", variableInfo.unit);
            return variableInfoPyDict;
        };

    const auto& createPointPyDict = [&setPyValue, &createVariableInfoPyDict](
            const auto& point
        ) {
            const auto& pointPyDict = PyDict_New();
            const auto& variableInfoPyDict = createVariableInfoPyDict(point.variableInfo);
            PyDict_SetItemString(pointPyDict, "variable_info", variableInfoPyDict);
            Py_DecRef(variableInfoPyDict);
            setPyValue(pointPyDict, "value", point.value);
            return pointPyDict;
        };

    const auto& createMarkPyDictPyList = [&createPointPyDict](
            const auto& markAxisSharedPtrVector
        ) {
            const auto& markPyDictPyList = PyList_New(0);
            for (const auto& markAxisSharedPtr : markAxisSharedPtrVector) {
                const auto& markPyDict = createPointPyDict(*markAxisSharedPtr);
                PyList_Append(markPyDictPyList, markPyDict);
                Py_DecRef(markPyDict);
            }
            return markPyDictPyList;
        };

    const auto& createAxisPyDict = [&setPyList, &createVariableInfoPyDict](const auto& axis) {
            const auto& axisPyDict = PyDict_New();
            const auto& variableInfoPyDict = createVariableInfoPyDict(axis.variableInfo);
            PyDict_SetItemString(axisPyDict, "variable_info", variableInfoPyDict);
            Py_DecRef(variableInfoPyDict);
            setPyList(axisPyDict, "value_list", axis.valueVector);
            return axisPyDict;
        };

    const auto& createFunctionPyDict = [&createAxisPyDict](const auto& function) {
            const auto& functionPyDict = PyDict_New();
            const auto& xAxisPyDict = createAxisPyDict(function.xAxis);
            const auto& yAxisPyDict = createAxisPyDict(function.yAxis);
            PyDict_SetItemString(functionPyDict, "x_axis", xAxisPyDict);
            PyDict_SetItemString(functionPyDict, "y_axis", yAxisPyDict);
            Py_DecRef(xAxisPyDict);
            Py_DecRef(yAxisPyDict);
            return functionPyDict;
        };

    const auto& markPyDictPyListPyDict = PyDict_New();
    const auto& markXAxisPyDictPyList = createMarkPyDictPyList(markXSharedPtrVector);
    const auto& markYAxisPyDictPyList = createMarkPyDictPyList(markYSharedPtrVector);
    PyDict_SetItemString(markPyDictPyListPyDict, "x_axis", markXAxisPyDictPyList);
    PyDict_SetItemString(markPyDictPyListPyDict, "y_axis", markYAxisPyDictPyList);
    Py_DecRef(markXAxisPyDictPyList);
    Py_DecRef(markYAxisPyDictPyList);

    const auto& functionListPyList = PyList_New(0);
    for (const auto& functionSharedPtr : functionSharedPtrVector) {
        const auto& functionPyDict = createFunctionPyDict(*functionSharedPtr);
        PyList_Append(functionListPyList, functionPyDict);
        Py_DecRef(functionPyDict);
    }

    const auto& legendShow = legendShowProperty_.get();
    const auto& legendShowPyObject = PyValueParser::toPyObject(legendShow);

    const auto& legendSymbols = legendSymbolsProperty_.get();
    const auto& legendSymbolsPyObject = PyValueParser::toPyObject(legendSymbols);

    const auto& markShiftToZeroPyDict = PyDict_New();
    if (markShiftToZeroXProperty_.getSelectedIdentifier() == "<none>") {
        PyDict_SetItemString(markShiftToZeroPyDict, "x_axis", Py_None);
    } else {
        const auto& index = markShiftToZeroXProperty_.getSelectedIndex() - 1;
        const auto& markPyDict = createPointPyDict(*markXFlatMultiInport_.getVectorData()[index]);
        PyDict_SetItemString(markShiftToZeroPyDict, "x_axis", markPyDict);
        Py_DecRef(markPyDict);
    }
    if (markShiftToZeroYProperty_.getSelectedIdentifier() == "<none>") {
        PyDict_SetItemString(markShiftToZeroPyDict, "y_axis", Py_None);
    } else {
        const auto& index = markShiftToZeroYProperty_.getSelectedIndex() - 1;
        const auto& markPyDict = createPointPyDict(*markYFlatMultiInport_.getVectorData()[index]);
        PyDict_SetItemString(markShiftToZeroPyDict, "y_axis", markPyDict);
        Py_DecRef(markPyDict);
    }

    const auto& axisLimitPyDict = PyDict_New();
    if (axisLimitAutoAdjustXProperty_.get()) {
        PyDict_SetItemString(axisLimitPyDict, "x_axis", Py_None);
    } else {
        const auto& axisLimitX = axisLimitXProperty_.get();
        const auto& axisLimitXPythonList = utilpy::makePyList<float>({
                axisLimitX[0],
                axisLimitX[1],
            });
        PyDict_SetItemString(axisLimitPyDict, "x_axis", axisLimitXPythonList);
        Py_DecRef(axisLimitXPythonList);
    }
    if (axisLimitAutoAdjustYProperty_.get()) {
        PyDict_SetItemString(axisLimitPyDict, "y_axis", Py_None);
    } else {
        const auto& axisLimitY = axisLimitYProperty_.get();
        const auto& axisLimitYPythonList = utilpy::makePyList<float>({
                axisLimitY[0],
                axisLimitY[1]
            });
        PyDict_SetItemString(axisLimitPyDict, "y_axis", axisLimitYPythonList);
        Py_DecRef(axisLimitYPythonList);
    }

    const auto& imageSize = imageOutport_.getDimensions();
    const auto& imageSizePyObject = PyValueParser::toPyObject(imageSize);

    PythonScript::VariableMap variableMap {
            { "function_list", functionListPyList },
            { "mark_list_dict", markPyDictPyListPyDict },
            { "legend_show", legendShowPyObject },
            { "legend_symbols", legendSymbolsPyObject },
            { "mark_shift_to_zero", markShiftToZeroPyDict },
            { "axis_limit", axisLimitPyDict },
            { "image_size", imageSizePyObject },
        };

    // escape() { sed '/^\/\//! { s/\\/\\\\/g ; s/"/\\"/g ; s/^\(.*\)$/"\1\\n"/ }' ; }
    // unescape() { sed 's/^ *// ; /^\/\//! { s/^ *"\(.*\)\\n"$/\1/ ; s/\\"/"/g } ; s/\\\\/\\/g' ; }
    PythonScript s;
    s.setSource(
            "import io\n"
            "import matplotlib\n"
            //"matplotlib.use("Qt5Agg")\n"
            "matplotlib.use(\"Agg\")\n"
            "matplotlib.rcParams.update({\n"
            "    'figure.autolayout' : True,\n"
            "    'legend.fontsize' : \"small\",\n"
            "    'legend.fontsize' : \"small\",\n"
            "})\n"
            "import matplotlib.pyplot as plt\n"
            //"plt.ion()\n"
            "\n"
            "def join_iterator_unique(join_str, iterator):\n"
            "    seen = set()\n"
            "    unique = list()\n"
            "    for item in iterator:\n"
            "        if item in seen:\n"
            "            continue\n"
            "        unique.append(item)\n"
            "        seen.add(item)\n"
            "    return join_str.join(unique)\n"
            "\n"
            "def join_iterator_if(join_str, iterator):\n"
            "    return join_str.join(filter(None, iterator))\n"
            "\n"
            "def format_value_if(format_str, value):\n"
            "    return format_str.format(value) if value else \"\"\n"
            "\n"
            "fig, ax = plt.subplots()\n"
            "\n"
            "line_func = {\n"
            "    \"x_axis\" : ax.axvline,\n"
            "    \"y_axis\" : ax.axhline,\n"
            "}\n"
            "for axis in [\"x_axis\", \"y_axis\"]:\n"
            "    for mark in mark_list_dict[axis]:\n"
            "        label = mark[\"variable_info\"][\n"
            "            \"variable_symbol\" if legend_symbols else \"variable_name\"\n"
            "        ]\n"
            "        line_func[axis](\n"
            "            mark[\"value\"] - (\n"
            "                mark_shift_to_zero[axis][\"value\"]\n"
            "                    if mark_shift_to_zero[axis]\n"
            "                    else 0\n"
            "            ),\n"
            "            linestyle='dashed',\n"
            "            label=label\n"
            "        )\n"
            "\n"
            "for function in function_list:\n"
            "    label = function[\"y_axis\"][\"variable_info\"][\n"
            "        \"variable_symbol\" if legend_symbols else \"variable_name\"\n"
            "    ]\n"
            "    ax.plot(\n"
            "        *[\n"
            "            [\n"
            "                value - (\n"
            "                    mark_shift_to_zero[axis][\"value\"]\n"
            "                        if mark_shift_to_zero[axis]\n"
            "                        else 0\n"
            "                )\n"
            "                for value in function[axis][\"value_list\"]\n"
            "            ]\n"
            "            for axis in [\"x_axis\", \"y_axis\"]\n"
            "        ],\n"
            "        label=label\n"
            "    )\n"
            "\n"
            "set_label_func = {\n"
            "    \"x_axis\" : ax.set_xlabel,\n"
            "    \"y_axis\" : ax.set_ylabel,\n"
            "}\n"
            "if function_list:\n"
            "    for axis in [\"x_axis\", \"y_axis\"]:\n"
            "        set_label_func[axis](join_iterator_unique(\"\\n\", [\n"
            "            join_iterator_if(\" \", [\n"
            "                join_iterator_if(\", \", [\n"
            "                    function[axis][\"variable_info\"][\"quantity_name\"],\n"
            "                    join_iterator_if(\"-\", [\n"
            "                        function[axis][\"variable_info\"][\"quantity_symbol\"],\n"
            "                        mark_shift_to_zero[axis][\"variable_info\"][\n"
            "                            \"variable_symbol\"]\n"
            "                            if mark_shift_to_zero[axis]\n"
            "                            else \"\"\n"
            "                    ])\n"
            "                ]),\n"
            "                format_value_if(\n"
            "                    \"[{}]\",\n"
            "                    function[axis][\"variable_info\"][\"unit\"]\n"
            "                ),\n"
            "            ])\n"
            "            for function in function_list\n"
            "        ]))\n"
            "\n"
            "if legend_show and (function_list or mark_list):\n"
            "    ax.legend()\n"
            "\n"
            "set_lim_func = {\n"
            "    \"x_axis\" : ax.set_xlim,\n"
            "    \"y_axis\" : ax.set_ylim,\n"
            "}\n"
            "get_lim_func = {\n"
            "    \"x_axis\" : ax.get_xlim,\n"
            "    \"y_axis\" : ax.get_ylim,\n"
            "}\n"
            "for axis in [\"x_axis\", \"y_axis\"]:\n"
            "    if axis_limit[axis]:\n"
            "        set_lim_func[axis](*axis_limit[axis])\n"
            "    axis_limit[axis] = get_lim_func[axis]()\n"
            "\n"
            "graph_bytes_io = io.BytesIO()\n"
            "fig.set_size_inches(*[dim / fig.dpi for dim in image_size])\n"
            "fig.savefig(graph_bytes_io, format='rgba', dpi=fig.dpi)\n"
            "graph_bytes = graph_bytes_io.getvalue()\n"
            "\n"
            "plt.close(fig)\n"
        );

    const auto& imageData = new glm::u8vec4[imageSize.x * imageSize.y];
    const auto& callback = [this, imageData, imageSize](PyObject* variablesDict) {

            char* buffer = PyBytes_AsString(PyDict_GetItemString(variablesDict, "graph_bytes"));
            util::IndexMapper2D index(imageSize);
            for (size_t x = 0; x < imageSize.x; ++x) {
                for (size_t y = 0; y < imageSize.y; ++y) {
                    const auto& base = index(x, (imageSize.y - 1) - y) * sizeof(glm::u8vec4);
                    imageData[index(x, y)] = {
                            buffer[base + 0],
                            buffer[base + 1],
                            buffer[base + 2],
                            buffer[base + 3],
                        };
                }
            }

            const auto& axisLimitPyDict = PyDict_GetItemString(variablesDict, "axis_limit");
            if (axisLimitAutoAdjustXProperty_.get()) {
                const auto& axisLimitXPyTuple = PyDict_GetItemString(axisLimitPyDict, "x_axis");
                const auto& axisLimitX = glm::vec2 {
                        PyFloat_AsDouble(PyTuple_GetItem(axisLimitXPyTuple, 0)),
                        PyFloat_AsDouble(PyTuple_GetItem(axisLimitXPyTuple, 1)),
                    };
                axisLimitXProperty_.set(axisLimitX);
                const auto& widthHalfX = std::abs(axisLimitX[1] - axisLimitX[0]) / 4;
                axisLimitXProperty_.setRangeMin(axisLimitX[0] - widthHalfX);
                axisLimitXProperty_.setRangeMax(axisLimitX[1] + widthHalfX);
            }
            if (axisLimitAutoAdjustYProperty_.get()) {
                const auto& axisLimitYPyTuple = PyDict_GetItemString(axisLimitPyDict, "y_axis");
                const auto& axisLimitY = glm::vec2 {
                        PyFloat_AsDouble(PyTuple_GetItem(axisLimitYPyTuple, 0)),
                        PyFloat_AsDouble(PyTuple_GetItem(axisLimitYPyTuple, 1)),
                    };
                axisLimitYProperty_.set(axisLimitY);
                const auto& widthHalfY = std::abs(axisLimitY[1] - axisLimitY[0]) / 4;
                axisLimitYProperty_.setRangeMin(axisLimitY[0] - widthHalfY);
                axisLimitYProperty_.setRangeMax(axisLimitY[1] + widthHalfY);
            }
        };
    s.run(variableMap, callback);

    for (const auto& variable : variableMap)
        Py_DecRef(variable.second);

    imageOutport_.setData(
            std::make_shared<Image>(
            std::make_shared<Layer>(
            std::make_shared<LayerRAMPrecision<glm::u8vec4>>(
                    imageData,
                    imageSize
                )
        )));
}

} // namespace

