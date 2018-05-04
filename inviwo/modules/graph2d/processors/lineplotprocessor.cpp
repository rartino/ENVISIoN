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

#include "lineplotprocessor.h"

#include <inviwo/core/datastructures/buffer/bufferramprecision.h>
#include <modules/animation/datastructures/interpolation.h>
#include <modules/opengl/texture/textureutils.cpp>

namespace glm {

using vec2 = tvec2<float, precision::packed_highp>;

bool operator>(const vec2& lhs, const vec2& rhs) {
    return (lhs[0] > rhs[0]) && (lhs[1] > rhs[1]);
}

bool operator<(const vec2& lhs, const vec2& rhs) {
    return (lhs[0] < rhs[0]) && (lhs[1] < rhs[1]);
}

}

namespace inviwo {

using plot::DataFrame;
using plot::Column;

// The Class Identifier has to be globally unique. Use a reverse DNS naming scheme
const ProcessorInfo lineplotprocessor::processorInfo_{
    "org.inviwo.lineplotprocessor",      // Class identifier
    "lineplotprocessor",                // Display name
    "Undefined",              // Category
    CodeState::Experimental,  // Code state
    Tags::None,               // Tags
};
const ProcessorInfo lineplotprocessor::getProcessorInfo() const {
    return processorInfo_;
}

lineplotprocessor::lineplotprocessor()
    : Processor()
    , dataFrameInport_("dataFrameInport")
    , meshOutport_("outport")
    , colour_("colour", "Colour", vec4(1, 0, 0, 1), vec4(0), vec4(1), vec4(0.1f),
            InvalidationLevel::InvalidOutput, PropertySemantics::Color)
    , x_range_("x_range", "X Range")
    , y_range_("y_range", "Y Range")
    , scale_("scale", "Scale")
    , axis_colour_("axis_colour", "Axis Colour", vec4(0, 0, 1, 1), vec4(0),
                   vec4(1), vec4(0.1f), InvalidationLevel::InvalidOutput,
                   PropertySemantics::Color)
    , axis_width_("axis_width", "Axis Width")
    , grid_colour_("grid_colour", "Grid Colour", vec4(0.5, 0.5, 0.5, 1), vec4(0),
                   vec4(1), vec4(0.1f), InvalidationLevel::InvalidOutput,
                   PropertySemantics::Color)
    , grid_width_("grid_width", "Grid Width")
    , font_("font", "Font Setting")
    , text_colour_("text_colour", "Text Colour", vec4(0, 0, 1, 1), vec4(0),
                   vec4(1), vec4(0.1f), InvalidationLevel::InvalidOutput,
                   PropertySemantics::Color)
    , label_number_("label_number", "Number of Labels")
    , labels_("labels", "Lable Outport") {

    addPort(dataFrameInport_);
    addPort(meshOutport_);
    addPort(labels_);
    addProperty(colour_);
    addProperty(x_range_);
    addProperty(y_range_);
    addProperty(scale_);
    addProperty(axis_colour_);
    addProperty(axis_width_);
    addProperty(grid_colour_);
    addProperty(grid_width_);
    addProperty(font_);
    addProperty(text_colour_);
    addProperty(label_number_);

    scale_.setMaxValue(1);
    scale_.setMinValue(0.01);
    scale_.setIncrement(0.01);
    scale_.set(0.8);

    axis_width_.setMaxValue(0.01);
    axis_width_.setMinValue(0.0001);
    axis_width_.setIncrement(0.0001);
    axis_width_.set(0.002);

    grid_width_.setMaxValue(0.01);
    grid_width_.setMinValue(0.0001);
    grid_width_.setIncrement(0.0001);
    grid_width_.set(0.001);

    font_.fontFace_.setSelectedIdentifier("arial");
    font_.fontFace_.setCurrentStateAsDefault();
    font_.fontSize_.setSelectedIndex(5);
    font_.fontSize_.setCurrentStateAsDefault();
    font_.anchorPos_ = vec2(-1, -0.97);

    label_number_.setMaxValue(1000);
    label_number_.setMinValue(0);
    label_number_.setIncrement(1);
    label_number_.set(5);
}

void lineplotprocessor::process() {
    std::shared_ptr<BasicMesh> mesh = std::make_shared<BasicMesh>();
    IndexBufferRAM* indices = mesh->addIndexBuffer(DrawType::Lines, ConnectivityType::None);

    std::shared_ptr<const DataFrame> inputFrame = dataFrameInport_.getData();

    // We want at least two columns. One named X and one named Y.
    if (inputFrame->getNumberOfColumns() >= 2) {
        std::shared_ptr<const Column> x = nullptr;
        std::shared_ptr<const Column> y = nullptr;

        // Find the columns named X and Y.
        for (size_t i = 0; i < inputFrame->getNumberOfColumns(); i++) {
            if (inputFrame->getHeader(i) == "X") {
                x = inputFrame->getColumn(i);
            } else if (inputFrame->getHeader(i) == "Y") {
                y = inputFrame->getColumn(i);
            }
        }

        if (!x) {
            LogError("Could not find any column named X in the DataFrame!");
            return;
        }

        if (!y) {
            LogError("Could not find any column named Y in the DataFrame!");
            return;
        }

        size_t y_size = y->getSize();
        size_t x_size = x->getSize();

        if (y_size != x_size) {
            LogError("The X and Y columns need to contain the same number"
                     " of values!");
        }

        if (y_size == 0 || x_size == 0) {
            return;
        }

        // Find the maximum and minimum values, respectively, and
        // normalise the data ranges to [0, 1].
        double x_min = x->getAsDouble(0);
        double y_min = y->getAsDouble(0);
        double x_max = x->getAsDouble(0);
        double y_max = y->getAsDouble(0);

        // x_size = y_size at this point, only need to check one.
        if (x_size > 1) {
            for (size_t i = 1; i < x_size; i++) {
                double x_val = x->getAsDouble(i);
                double y_val = y->getAsDouble(i);

                x_min = x_val < x_min ? x_val : x_min;
                y_min = y_val < y_min ? y_val : y_min;

                x_max = x_val > x_max ? x_val : x_max;
                y_max = y_val > y_max ? y_val : y_max;
            }
        }

	// Set default values if data changes.
	if (dataFrameInport_.isChanged()) {
	  x_range_.set(vec2(x_max, x_min));
	  y_range_.set(vec2(y_max, y_min));
	}


        // If all values in one dimension have the same value we let
        // them normalise to one by setting the min values to zero.
        if (y_max == y_min) {
            y_min = 0;
        }

        if (x_max == x_min) {
            x_min = 0;
        }

        // Set the increment to 1/100 of the total interval length.
        float x_increment = std::abs(x_max - x_min) / 100.f;
        x_range_.setMaxValue(vec2(x_max, x_max));
        x_range_.setMinValue(vec2(x_min, x_min));
        x_range_.setIncrement(vec2(x_increment, x_increment));

        float y_increment = std::abs(x_max - x_min) / 100.f;
        y_range_.setMaxValue(vec2(y_max, y_max));
        y_range_.setMinValue(vec2(y_min, y_min));
        y_range_.setIncrement(vec2(y_increment, y_increment));

        // Check if the set value falls outside of the allowed range
        // and reset it if that is the case. Also set it if min and
        // max are equal.
        if (x_range_.get() > x_range_.getMaxValue() ||
            x_range_.get() < x_range_.getMinValue() ||
            x_range_.get()[0] == x_range_.get()[1]) {
            x_range_.set(vec2(x_max, x_min));
        } else {
            // Otherwise we assign the set values as min/max.
            x_max = x_range_.get()[0];
            x_min = x_range_.get()[1];
        }

        if (y_range_.get() > y_range_.getMaxValue() ||
            y_range_.get() < y_range_.getMinValue() ||
            y_range_.get()[0] == y_range_.get()[1]) {
            y_range_.set(vec2(y_max, y_min));
        } else {
            y_max = y_range_.get()[0];
            y_min = y_range_.get()[1];
        }

        if (x_max < x_min) {
            LogError("The maximum X value range can't be less"
                     " than the minimum X value range!");
            return;
        }

        if (y_max < y_min) {
            LogError("The maximum Y value range can't be less"
                     " than the minimum Y value range!");
            return;
        }
	
        // Draw background grid.
        drawAxes(mesh, x_min, x_max, y_min, y_max);

        if (font_.fontFace_.isModified()) {
            textRenderer_.setFont(font_.fontFace_.get());
        }

        utilgl::activateAndClearTarget(labels_, ImageType::ColorDepth);
        drawScale(x_min, x_max, y_min, y_max);
        utilgl::deactivateCurrentTarget();

        // Each line segment should start on the current point and end
        // at the next point. Subtract one from the end criteria,
        // since the last point is included when the segment is drawn
        // from the next-to-last point.
        for (size_t i = 0; i < x_size - 1; i++) {
            // Get coordinates, normalise them to [0, 1], scale them
            // and center them.
            float s = scale_.get();
            double x_start = s * normalise(x->getAsDouble(i), x_min, x_max)
                             + (1 - s) / 2;
            double y_start = s * normalise(y->getAsDouble(i), y_min, y_max)
                             + (1 - s) / 2;
            double x_end = s * normalise(x->getAsDouble(i + 1), x_min, x_max)
                           + (1 - s) / 2;
            double y_end = s * normalise(y->getAsDouble(i + 1), y_min, y_max)
                           + (1 - s) / 2;

            vec3 start_point = vec3(x_start, y_start, 0);
            indices->add(mesh->addVertex(start_point, start_point,
                         start_point, colour_));

            vec3 end_point = vec3(x_end, y_end, 0);
            indices->add(mesh->addVertex(end_point, end_point,
                         end_point, colour_));
        }
    } else {
        LogInfo("This processor needs two columns to exist in the DataFrame."
                " One named X and one named Y.")
        return;
    }

    meshOutport_.setData(mesh);
}

void lineplotprocessor::drawAxes(std::shared_ptr<BasicMesh>& mesh,
                                 double x_min, double x_max,
                                 double y_min, double y_max) {
    // Draw the X axis.
    float s = scale_.get();
    vec3 x_start_point = vec3(s * normalise(x_range_.getMinValue()[0],
                                            x_min, x_max) + (1 - s) / 2,
                              s * normalise(0, y_min, y_max) + (1 - s) / 2,
                              0);
    vec3 x_end_point = vec3(s * normalise(x_range_.getMaxValue()[0],
                                          x_min, x_max) + (1 - s) / 2,
                            s * normalise(0, y_min, y_max) + (1 - s) / 2,
                            0);
    mesh->append(BasicMesh::line(x_start_point, x_end_point, vec3(0, 0, 1),
                                 axis_colour_.get(), axis_width_.get(),
                                 ivec2(2, 2)).get());

    // Draw the Y axis.
    vec3 y_start_point = vec3(s * normalise(0, x_min, x_max) + (1 - s) / 2,
                              s * normalise(y_range_.getMinValue()[0],
                                            y_min, y_max) + (1 - s) / 2,
                              0);
    vec3 y_end_point = vec3(s * normalise(0, x_min, x_max) + (1 - s) / 2,
                            s * normalise(y_range_.getMaxValue()[0],
                                          y_min, y_max) + (1 - s) / 2,
                            0);
    mesh->append(BasicMesh::line(y_start_point, y_end_point, vec3(0, 0, 1),
                                 axis_colour_.get(), axis_width_.get(),
                                 ivec2(2, 2)).get());

    // Draw grid.
    double x_step_size = std::abs(x_max - x_min) / label_number_.get();
    for (double x = x_min + x_step_size; x <= x_max; x += x_step_size) {
        vec3 y_start_point = vec3(s * normalise(x, x_min, x_max) + (1 - s) / 2,
                                  s * normalise(y_range_.getMinValue()[0],
                                                y_min, y_max) + (1 - s) / 2,
                                  0);
        vec3 y_end_point = vec3(s * normalise(x, x_min, x_max) + (1 - s) / 2,
                                s * normalise(y_range_.getMaxValue()[0],
                                              y_min, y_max) + (1 - s) / 2,
                                0);
        mesh->append(BasicMesh::line(y_start_point, y_end_point, vec3(0, 0, 1),
                                     grid_colour_.get(), grid_width_.get(),
                                     ivec2(2, 2)).get());
    }

    double y_step_size = std::abs(y_max - y_min) / label_number_.get();
    for (double y = y_min + y_step_size; y <= y_max; y += y_step_size) {
        float s = scale_.get();
        vec3 x_start_point = vec3(s * normalise(x_range_.getMinValue()[0],
                                                x_min, x_max) + (1 - s) / 2,
                                  s * normalise(y, y_min, y_max) + (1 - s) / 2,
                                  0);
        vec3 x_end_point = vec3(s * normalise(x_range_.getMaxValue()[0],
                                              x_min, x_max) + (1 - s) / 2,
                                s * normalise(y, y_min, y_max) + (1 - s) / 2,
                                0);
        mesh->append(BasicMesh::line(x_start_point, x_end_point, vec3(0, 0, 1),
                                     grid_colour_.get(), grid_width_.get(),
                                     ivec2(2, 2)).get());
    }

    // Draw an arrow on the Y axis.
    mesh->append(BasicMesh::line(y_end_point, y_end_point + vec3(0.005, -0.01, 0), vec3(0, 0, 1),
                                 axis_colour_.get(), axis_width_.get(),
                                 ivec2(2, 2)).get());
    mesh->append(BasicMesh::line(y_end_point, y_end_point + vec3(-0.005, -0.01, 0), vec3(0, 0, 1),
                                 axis_colour_.get(), axis_width_.get(),
                                 ivec2(2, 2)).get());

    // Draw an arrow on the X axis.
    mesh->append(BasicMesh::line(x_end_point, x_end_point + vec3(-0.01, 0.005, 0), vec3(0, 0, 1),
                                 axis_colour_.get(), axis_width_.get(),
                                 ivec2(2, 2)).get());
    mesh->append(BasicMesh::line(x_end_point, x_end_point + vec3(-0.01, -0.005, 0), vec3(0, 0, 1),
                                 axis_colour_.get(), axis_width_.get(),
                                 ivec2(2, 2)).get());
}

void lineplotprocessor::drawScale(double x_min, double x_max,
                                  double y_min, double y_max) {
    // Iterate over the length of the X axis and add the number scale.
    double x_step_size = std::abs(x_max - x_min) / label_number_.get();
    for (double x = x_min + x_step_size; x <= x_max; x += x_step_size) {
        float s = scale_.get();
        vec2 x_axis = vec2(s * normalise(x, x_min, x_max) + (1 - s) / 2,
                           s * normalise(0, y_min, y_max) + (1 - s) / 2);

        vec2 image_dims = labels_.getDimensions();
        vec2 image_coords = vec2(image_dims[0] * x_axis[0], image_dims[1] * x_axis[1]);

        vec2 shift = image_dims * (font_.anchorPos_.get() + vec2(1.0f, 1.0f));
        image_coords -= shift;

        drawText(std::to_string(x), image_coords);
    }

    double y_step_size = std::abs(y_max - y_min) / label_number_.get();
    for (double y = y_min + y_step_size; y <= y_max; y += y_step_size) {
        std::string label = std::to_string(y);
        float s = scale_.get();
        vec2 y_axis = vec2(s * normalise(0, x_min, x_max) + (1 - s) / 2,
                           s * normalise(y, y_min, y_max) + (1 - s) / 2);

        vec2 image_dims = labels_.getDimensions();
        vec2 image_coords = vec2(image_dims[0] * y_axis[0], image_dims[1] * y_axis[1]);

        vec2 shift = 0.5f * image_dims * (font_.anchorPos_.get() + vec2(1.0f, 1.0f));
        image_coords -= shift;

        drawText(label, image_coords, true);
    }

}

void lineplotprocessor::drawText(const std::string& text, vec2 position, bool anchor_right) {
    std::shared_ptr<Texture2D> texture(nullptr);
    texture  = util::createTextTexture(textRenderer_,
                                       text,
                                       font_.fontSize_.getSelectedValue(),
                                       text_colour_.get(),
                                       texture);

    // If anchor_right is set, the text will be moved its own length
    // to the left, plus 10 %.
    if (anchor_right) {
        vec2 offset = vec2(texture->getDimensions()[0], 0);
        position -= offset + 0.1f * offset;
    }

    textureRenderer_.render(texture, position, labels_.getDimensions());
}

double lineplotprocessor::normalise(double value, double min, double max) const {
    return (value - min) / (max - min);
}

} // namespace

