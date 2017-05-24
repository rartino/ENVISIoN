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
    , sortOnNameProperty_("sortOnName", "Sort on name", true)
    , showLegendProperty_("showLegendProperty", "Show legend", true)
    , imageOutport_("imageOutport", DataVec4UInt8::get())
{
    addPort(functionFlatMultiInport_);
    addProperty(sortOnNameProperty_);
    addProperty(showLegendProperty_);
    addPort(imageOutport_);
}

void Plotter::process() {

    auto functionSharedPtrVector = functionFlatMultiInport_.getVectorData();
    if (sortOnNameProperty_.get())
        std::sort(
                functionSharedPtrVector.begin(),
                functionSharedPtrVector.end(),
                [](const auto& lhs, const auto& rhs) {
                        return lhs->y.variableName < rhs->y.variableName;
                    }
            );

    const auto& functionListPyList = PyList_New(0);
    for (const auto& functionSharedPtr : functionSharedPtrVector) {

        const auto& functionPyDict = PyDict_New();
        const auto& setAxis = [&functionPyDict](const auto& axisName, const auto& axis) {

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
        setAxis("x", functionSharedPtr->x);
        setAxis("y", functionSharedPtr->y);
        PyList_Append(functionListPyList, functionPyDict);
        Py_DecRef(functionPyDict);
    }

    const auto& imageSize = imageOutport_.getDimensions();
    const auto& imageSizePyObject = PyValueParser::toPyObject(imageSize);

    const auto& showLegend = showLegendProperty_.get();
    const auto& showLegendPyObject = PyValueParser::toPyObject(showLegend);

    PythonScript::VariableMap variableMap {
            { "image_size", imageSizePyObject },
            { "function_list", functionListPyList },
            { "show_legend", showLegendPyObject },
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
            //"plt.ion()\n"
            "fig, ax = plt.subplots()\n"
            "for function in function_list:\n"
            "    print(\"DEBUG: Plotter: {} ({}x{})\".format(\n"
            "        function[\"y\"][\"variable_name\"],\n"
            "        len(function[\"y\"][\"data\"]),\n"
            "        len(function[\"y\"][\"data\"]),\n"
            "    ))\n"
            "    label = join_iterator_if(\", \", [\n"
            "        function[\"y\"][attribute]\n"
            "        for attribute in [\"variable_name\", \"variable_symbol\"]\n"
            "    ])\n"
            "    ax.plot(\n"
            "        function[\"x\"][\"data\"],\n"
            "        function[\"y\"][\"data\"],\n"
            "        label=label\n"
            "    )\n"
            "if function_list:\n"
            "    label = {\n"
            "        axis : join_iterator_unique(\"\\n\", [\n"
            "            join_iterator_if(\" \", [\n"
            "                join_iterator_if(\", \", [\n"
            "                    function[axis][\"quantity_name\"],\n"
            "                    function[axis][\"quantity_symbol\"],\n"
            "                ]),\n"
            "                format_value_if(\"[{}]\", function[axis][\"unit\"]),\n"
            "            ])\n"
            "            for function in function_list\n"
            "        ])\n"
            "        for axis in [\"x\", \"y\"]\n"
            "    }\n"
            "    ax.set_xlabel(label[\"x\"])\n"
            "    ax.set_ylabel(label[\"y\"])\n"
            "    if show_legend:\n"
            "        ax.legend()\n"
            "\n"
            "graph_bytes_io = io.BytesIO()\n"
            "fig.set_size_inches(*[dim / fig.dpi for dim in image_size])\n"
            "fig.savefig(graph_bytes_io, format='rgba', dpi=fig.dpi)\n"
            "graph_bytes = graph_bytes_io.getvalue()\n"
            "\n"
            "plt.close(fig)\n"
        );

    const auto& imageData = new glm::u8vec4[imageSize.x * imageSize.y];
    const auto& callback = [imageData, imageSize](PyObject* variablesDict) {
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

