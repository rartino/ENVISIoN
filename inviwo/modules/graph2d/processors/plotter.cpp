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
    , markXInport_("markXInport")
    , markYInport_("markYInport")
    , sortOnNameProperty_("sortOnName", "Sort on name", true)
    , legendShowProperty_("legendShowProperty", "Show legend", true)
    , legendSymbolsProperty_("legendSymbolsProperty", "Use symbols in legend", false)
    , markShiftToZeroXProperty_("markShiftToZeroXProperty", "Shift x mark to zero", false)
    , markShiftToZeroYProperty_("markShiftToZeroYProperty", "Shift y mark to zero", false)
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
    addPort(markXInport_);
    addPort(markYInport_);

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

    markXInport_.setOptional(true);
    markYInport_.setOptional(true);

    const auto& onMarkXInportChange = [this]() {
            const auto& visible = !markXInport_.getVectorData().empty();
            markShiftToZeroXProperty_.setVisible(visible);
        };
    onMarkXInportChange();
    markXInport_.onChange(onMarkXInportChange);

    const auto& onMarkYInportChange = [this]() {
            const auto& visible = !markYInport_.getVectorData().empty();
            markShiftToZeroYProperty_.setVisible(visible);
        };
    onMarkYInportChange();
    markYInport_.onChange(onMarkYInportChange);

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
    auto markXSharedPtrVector = markXInport_.getVectorData();
    auto markYSharedPtrVector = markYInport_.getVectorData();

    if (sortOnNameProperty_.get()) {
        std::sort(
                functionSharedPtrVector.begin(),
                functionSharedPtrVector.end(),
                [](const auto& lhs, const auto& rhs) {
                        return lhs->yAxis.variableName < rhs->yAxis.variableName;
                    }
            );
        }

    const auto& setAxis = [](const auto& functionPyDict, const auto& axisName, const auto& axis) {

            const auto& axisPyDict = PyDict_New();
            const auto& setList = [&axisPyDict](const char* name, auto value) {
                    auto valuePyList = utilpy::makePyList(value);
                    PyDict_SetItemString(axisPyDict, name, valuePyList);
                    Py_DecRef(valuePyList);
                };
            const auto& setValue = [&axisPyDict](const char* name, auto value) {
                    const auto& valuePyObject = PyValueParser::toPyObject(value);
                    PyDict_SetItemString(axisPyDict, name, valuePyObject);
                    Py_DecRef(valuePyObject);
                };
            setList("data", axis.data);
            setValue("variable_name", axis.variableName);
            setValue("variable_symbol", axis.variableSymbol);
            setValue("quantity_name", axis.quantityName);
            setValue("quantity_symbol", axis.quantitySymbol);
            setValue("unit", axis.unit);
            PyDict_SetItemString(functionPyDict, axisName, axisPyDict);
            Py_DecRef(axisPyDict);

        };

    const auto& functionListPyList = PyList_New(0);
    for (const auto& functionSharedPtr : functionSharedPtrVector) {
        const auto& functionPyDict = PyDict_New();
        setAxis(functionPyDict, "xAxis", functionSharedPtr->xAxis);
        setAxis(functionPyDict, "yAxis", functionSharedPtr->yAxis);
        PyList_Append(functionListPyList, functionPyDict);
        Py_DecRef(functionPyDict);
    }

    const auto& markPyDict = PyDict_New();
    if (markXSharedPtrVector.empty())
        PyDict_SetItemString(markPyDict, "xAxis", Py_None);
    else
        setAxis(markPyDict, "xAxis", markXSharedPtrVector.front()->yAxis);
    if (markYSharedPtrVector.empty())
        PyDict_SetItemString(markPyDict, "yAxis", Py_None);
    else
        setAxis(markPyDict, "yAxis", markYSharedPtrVector.front()->yAxis);

    const auto& legendShow = legendShowProperty_.get();
    const auto& legendShowPyObject = PyValueParser::toPyObject(legendShow);

    const auto& legendSymbols = legendSymbolsProperty_.get();
    const auto& legendSymbolsPyObject = PyValueParser::toPyObject(legendSymbols);

    const auto& markShiftToZeroPyDict = PyDict_New();
    const auto& markShiftToZeroX = markShiftToZeroXProperty_.get();
    const auto& markShiftToZeroXPyObject = PyValueParser::toPyObject(markShiftToZeroX);
    PyDict_SetItemString(markShiftToZeroPyDict, "xAxis", markShiftToZeroXPyObject);
    const auto& markShiftToZeroY = markShiftToZeroYProperty_.get();
    const auto& markShiftToZeroYPyObject = PyValueParser::toPyObject(markShiftToZeroY);
    PyDict_SetItemString(markShiftToZeroPyDict, "yAxis", markShiftToZeroYPyObject);

    const auto& axisLimitPyDict = PyDict_New();
    if (axisLimitAutoAdjustXProperty_.get()) {
        PyDict_SetItemString(axisLimitPyDict, "xAxis", Py_None);
    } else {
        const auto& axisLimitX = axisLimitXProperty_.get();
        const auto& axisLimitXPythonList = utilpy::makePyList<float>({
                axisLimitX[0],
                axisLimitX[1],
            });
        PyDict_SetItemString(axisLimitPyDict, "xAxis", axisLimitXPythonList);
        Py_DecRef(axisLimitXPythonList);
    }
    if (axisLimitAutoAdjustYProperty_.get()) {
        PyDict_SetItemString(axisLimitPyDict, "yAxis", Py_None);
    } else {
        const auto& axisLimitY = axisLimitYProperty_.get();
        const auto& axisLimitYPythonList = utilpy::makePyList<float>({
                axisLimitY[0],
                axisLimitY[1]
            });
        PyDict_SetItemString(axisLimitPyDict, "yAxis", axisLimitYPythonList);
        Py_DecRef(axisLimitYPythonList);
    }

    const auto& imageSize = imageOutport_.getDimensions();
    const auto& imageSizePyObject = PyValueParser::toPyObject(imageSize);

    PythonScript::VariableMap variableMap {
            { "function_list", functionListPyList },
            { "mark", markPyDict },
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
            "    \"xAxis\" : ax.axvline,\n"
            "    \"yAxis\" : ax.axhline,\n"
            "}\n"
            "mark_shift = {\n"
            "    axis : (\n"
            "        mark[axis][\"data\"][0]\n"
            "        if mark_shift_to_zero[axis] and mark[axis]\n"
            "        else 0\n"
            "    )\n"
            "    for axis in [\"xAxis\", \"yAxis\"]\n"
            "}\n"
            "for axis in [\"xAxis\", \"yAxis\"]:\n"
            "    if mark[axis]:\n"
            "        line_func[axis](\n"
            "            mark[axis][\"data\"][0] - mark_shift[axis],\n"
            "            color='red',\n"
            "            linestyle='dashed',\n"
            "            label=mark[axis][\n"
            "                \"variable_symbol\"\n"
            "                    if legend_symbols\n"
            "                    else \"variable_name\"\n"
            "            ]\n"
            "        )\n"
            "\n"
            "for function in function_list:\n"
            "    label = function[\"yAxis\"][\n"
            "        \"variable_symbol\" if legend_symbols else \"variable_name\"\n"
            "    ]\n"
            "    ax.plot(\n"
            "        *[\n"
            "            [value - mark_shift[axis] for value in function[axis][\"data\"]]\n"
            "            for axis in [\"xAxis\", \"yAxis\"]\n"
            "        ],\n"
            "        label=label\n"
            "    )\n"
            "\n"
            "set_label_func = {\n"
            "    \"xAxis\" : ax.set_xlabel,\n"
            "    \"yAxis\" : ax.set_ylabel,\n"
            "}\n"
            "if function_list:\n"
            "    for axis in [\"xAxis\", \"yAxis\"]:\n"
            "        set_label_func[axis](join_iterator_unique(\"\\n\", [\n"
            "            join_iterator_if(\" \", [\n"
            "                join_iterator_if(\", \", [\n"
            "                    function[axis][\"quantity_name\"],\n"
            "                    join_iterator_if(\"-\", [\n"
            "                        function[axis][\"quantity_symbol\"],\n"
            "                        mark[axis][\"variable_symbol\"]\n"
            "                            if mark_shift_to_zero[axis] and mark[axis]\n"
            "                            else \"\"\n"
            "                    ])\n"
            "                ]),\n"
            "                format_value_if(\"[{}]\", function[axis][\"unit\"]),\n"
            "            ])\n"
            "            for function in function_list\n"
            "        ]))\n"
            "\n"
            "if legend_show:\n"
            "    ax.legend()\n"
            "\n"
            "set_lim_func = {\n"
            "    \"xAxis\" : ax.set_xlim,\n"
            "    \"yAxis\" : ax.set_ylim,\n"
            "}\n"
            "get_lim_func = {\n"
            "    \"xAxis\" : ax.get_xlim,\n"
            "    \"yAxis\" : ax.get_ylim,\n"
            "}\n"
            "for axis in [\"xAxis\", \"yAxis\"]:\n"
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
                const auto& axisLimitXPyTuple = PyDict_GetItemString(axisLimitPyDict, "xAxis");
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
                const auto& axisLimitYPyTuple = PyDict_GetItemString(axisLimitPyDict, "yAxis");
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

