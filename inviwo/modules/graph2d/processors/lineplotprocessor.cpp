/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2017-2019 Inviwo Foundation, Andreas Kempe, Abdullatif Ismail
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
  *   Alterations to this file by Abdullatif Ismail
  *
  *   To the extent possible under law, the person who associated CC0
  *   with the alterations to this file has waived all copyright and
  *   related or neighboring rights to the alterations made to this file.
  *
  *   You should have received a copy of the CC0 legalcode along with
  *   this work.  If not, see
  *   <http://creativecommons.org/publicdomain/zero/1.0/>.
  */

#include "lineplotprocessor.h"
#include <inviwo/core/datastructures/buffer/bufferramprecision.h>
#include <inviwo/core/util/interpolation.h>
#include <modules/opengl/texture/textureutils.h>

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
using plot::TemplateColumn;

// The Class Identifier has to be globally unique. Use a reverse DNS naming scheme
const ProcessorInfo LinePlotProcessor::processorInfo_{
    "org.inviwo.LinePlotProcessor",   // Class identifier
    "Line Plot",                      // Display name
    "Plotting",                       // Category
    CodeState::Experimental,          // Code state
    "Plotting",                       // Tags
};
const ProcessorInfo LinePlotProcessor::getProcessorInfo() const {
    return processorInfo_;
}

LinePlotProcessor::LinePlotProcessor()
    : Processor()
    , dataFrameInport_("dataFrameInport")
    , pointInport_("pointInport")
    , meshOutport_("outport")
    , xSelectionProperty_("xSelectionProperty", "Select X data")
    , ySelectionProperty_("ySelectionProperty", "Select Y data")
    , allYSelection_("allYSelection", "Select all Y")
    , colour_("colour", "Colour", vec4(1, 0, 0, 1), vec4(0), vec4(1), vec4(0.1f),
            InvalidationLevel::InvalidOutput, PropertySemantics::Color)
    , x_range_("x_range", "X Range")
    , y_range_("y_range", "Y Range")
    , scale_("scale", "Scale")
    , enable_line_("enable_line", "Enable Line")
    , line_x_coordinate_("line_x_coordinate", "Line X Coordinate")
    , line_colour_("line_colour", "Line Colour", vec4(0.078, 0.553, 1, 1), vec4(0),
                   vec4(1), vec4(0.1f), InvalidationLevel::InvalidOutput,
                   PropertySemantics::Color)
    , show_x_labels_("show_x_labels", "X Labels")
    , show_y_labels_("show_y_labels", "Y Labels")
    , axis_colour_("axis_colour", "Axis Colour", vec4(0, 0, 0, 1), vec4(0),
                   vec4(1), vec4(0.1f), InvalidationLevel::InvalidOutput,
                   PropertySemantics::Color)
    , axis_width_("axis_width", "Axis Width")
    , enable_grid_("enable_grid", "Enable Grid")
    , grid_colour_("grid_colour", "Grid Colour", vec4(0.9, 0.9, 0.9, 1), vec4(0),
                   vec4(1), vec4(0.1f), InvalidationLevel::InvalidOutput,
                   PropertySemantics::Color)
    , grid_width_("grid_width", "Grid Width")
    , font_("font", "Font Setting")
    , text_colour_("text_colour", "Text Colour", vec4(0, 0, 0, 1), vec4(0),
                   vec4(1), vec4(0.1f), InvalidationLevel::InvalidOutput,
                   PropertySemantics::Color)
    , label_number_("label_number", "Number of Labels")
    , labels_("labels", "Lable Outport") {

    addPort(dataFrameInport_);
    addPort(pointInport_);
    addPort(meshOutport_);
    addPort(labels_);

    addProperty(xSelectionProperty_);
    addProperty(ySelectionProperty_);
    addProperty(allYSelection_);
    addProperty(colour_);
    addProperty(x_range_);
    addProperty(y_range_);
    addProperty(scale_);

    addProperty(enable_line_);
    addProperty(line_x_coordinate_);
    addProperty(line_colour_);
    addProperty(show_x_labels_);
    addProperty(show_y_labels_);

    addProperty(axis_colour_);
    addProperty(axis_width_);
    addProperty(enable_grid_);
    addProperty(grid_colour_);
    addProperty(grid_width_);
    addProperty(font_);
    addProperty(text_colour_);
    addProperty(label_number_);

    pointInport_.setOptional(true);
    allYSelection_.set(false);
    scale_.setMaxValue(1);
    scale_.setMinValue(0.01);
    scale_.setIncrement(0.01);
    scale_.set(0.8);

    enable_line_.set(false);
    show_x_labels_.set(true);
    show_y_labels_.set(true);

    axis_width_.setMaxValue(0.01);
    axis_width_.setMinValue(0.0001);
    axis_width_.setIncrement(0.0001);
    axis_width_.set(0.002);

    enable_grid_.set(false);
    grid_width_.setMaxValue(0.01);
    grid_width_.setMinValue(0.0001);
    grid_width_.setIncrement(0.0001);
    grid_width_.set(0.002);

    font_.fontFace_.setSelectedIdentifier("arial");
    font_.fontFace_.setCurrentStateAsDefault();
    font_.fontSize_.set(20);
    font_.fontSize_.setCurrentStateAsDefault();
    font_.anchorPos_ = vec2(-1, -0.97);

    label_number_.setMaxValue(1000);
    label_number_.setMinValue(0);
    label_number_.setIncrement(1);
    label_number_.set(5);
}

void LinePlotProcessor::process() {
    std::shared_ptr<const Column> x;
    std::shared_ptr<const Column> y;
    std::shared_ptr<const Column> xData;
    std::vector<std::shared_ptr<const Column>> yData;
    std::vector<std::shared_ptr<const Column>> data;
    std::shared_ptr<BasicMesh> mesh = std::make_shared<BasicMesh>();
    IndexBufferRAM *indices = mesh->addIndexBuffer(DrawType::Lines, ConnectivityType::None).get();
    // Get the input data.
    std::shared_ptr<const DataFrame> inputFrame = dataFrameInport_.getData();

    // We want at least two columns.
    if (inputFrame->getNumberOfColumns() >= 3) {
        for (size_t i = 0; i < inputFrame->getNumberOfColumns(); i++) {
            if (inputFrame->getHeader(i) != "index") {
                data.push_back(inputFrame->getColumn(i));
            }
        }
    } else {
        LogInfo("This processor needs two columns to exist in the DataFrame.")
        return;
    }

    // Clear all options before adding new options.
    // This is done to prevent doubling all options every run.
    if (dataFrameInport_.isChanged()) {
        xSelectionProperty_.clearOptions();
        ySelectionProperty_.clearOptions();
        for (size_t i = 0; i < data.size(); i++) {
            xSelectionProperty_.addOption(data.at(i)->getHeader(),
                                          data.at(i)->getHeader(),
                                          data.at(i)->getHeader());
            ySelectionProperty_.addOption(data.at(i)->getHeader(),
                                          data.at(i)->getHeader(),
                                          data.at(i)->getHeader());
        }
    }
    // Declare global size boundries.
    size_t xSize, ySize;
    double xMax, xMin, yMax, yMin;
    double range;
    // If we only want to plot one X against one Y.
    if (!allYSelection_.get()) {
        for (size_t i = 0; i < data.size(); i++) {
            if (xSelectionProperty_.getSelectedIdentifier() == data.at(i)->getHeader()) {
                x = data.at(i);
            }
            if (ySelectionProperty_.getSelectedIdentifier() == data.at(i)->getHeader()) {
                if (pointInport_.isConnected()) {
                    std::shared_ptr<TemplateColumn<float>> yTmp = std::make_shared<TemplateColumn<float>>(data.at(i)->getHeader());
                    for (size_t j = 0; j < data.at(i)->getSize(); j++) {
                        yTmp->add(data.at(i)->getAsDouble(j) - pointInport_.getData()->value);
                    }
                    y = yTmp;
                } else {
                    y = data.at(i);
                }
            }
        }
        // Set local boundries for one vs one plot.
        xSize = x->getSize();
        ySize = y->getSize();
        if (xSize != ySize) {
            LogError("Columns doesn't have same amount of data.");
            return;
        }
        double localXMax = x->getAsDouble(0);
        double localXMin = x->getAsDouble(0);
        double localYMax = y->getAsDouble(0);
        double localYMin = y->getAsDouble(0);
        for (size_t i = 0; i < xSize; i++) {
            if (x->getAsDouble(i) > localXMax) {
                localXMax = x->getAsDouble(i);
            }
            if (x->getAsDouble(i) < localXMin) {
                localXMin = x->getAsDouble(i);
            }
        }
        for (size_t i = 0; i < ySize; i++) {
            if (y->getAsDouble(i) > localYMax) {
                localYMax = y->getAsDouble(i);
            }
            if (y->getAsDouble(i) < localYMin) {
                localYMin = y->getAsDouble(i);
            }
        }
        range = abs(localYMin + localYMax);
        xMax = localXMax;
        xMin = localXMin;
        yMax = localYMax + 0.1 * range;
        yMin = localYMin - 0.1 * range;
    } else {
        // If we want to plot X against all Y.
        for (size_t i = 0; i < data.size(); i++) {
            if (xSelectionProperty_.getSelectedIdentifier() == data.at(i)->getHeader()) {
                xData = data.at(i);
            } else {
                if (pointInport_.isConnected()) {
                    std::shared_ptr<TemplateColumn<float>> yTmp = std::make_shared<TemplateColumn<float>>(data.at(i)->getHeader());
                    for (size_t j = 0; j < data.at(i)->getSize(); j++) {
                        yTmp->add(data.at(i)->getAsDouble(j) - pointInport_.getData()->value);
                    }
                    yData.push_back(yTmp);
                } else {
                    yData.push_back(data.at(i));
                }
            }
        }
        xSize = xData->getSize();
        for(size_t i = 0; i < yData.size(); i++)
            if (yData.at(i)->getSize() != xSize) {
                LogError("All columns needs to be the same size.");
                return;
        }
        for (size_t i = 0; i < xSize; i++) {
            if (xData->getAsDouble(i) > xMax) {
                xMax = xData->getAsDouble(i);
            }
            if (xData->getAsDouble(i) < xMin) {
                xMin = xData->getAsDouble(i);
            }
        }
        for (size_t column = 0; column < yData.size(); column++) {
            for (size_t i = 0; i < yData.at(column)->getSize(); i++) {
                if (yData.at(column)->getAsDouble(i) > yMax) {
                    yMax = yData.at(column)->getAsDouble(i);
                }
                if (yData.at(column)->getAsDouble(i) < yMin) {
                    yMin = yData.at(column)->getAsDouble(i);
                }
            }
        }
        range = abs(yMin + yMax);
        yMin -= 0.1 * range;
        yMax += 0.1 * range;
    }
    if (dataFrameInport_.isChanged() ||
        xSelectionProperty_.isModified() ||
        ySelectionProperty_.isModified() ||
        allYSelection_.isModified()) {
        // Set boundries for viewing range.
        y_range_.setMaxValue(vec2(yMax, yMax));
        y_range_.setMinValue(vec2(yMin, yMin));
        x_range_.setMaxValue(vec2(xMax, xMax));
        x_range_.setMinValue(vec2(xMin, xMin));

        line_x_coordinate_.setMaxValue(xMax);
        line_x_coordinate_.setMinValue(xMin);

        x_range_.set(vec2(xMax, xMin));
        y_range_.set(vec2(yMax, yMin));
    }

    // If all values in one dimension have the same value we let
    // them normalise to a range that is one wide by subtracting
    // one from the minimum value.
    if (yMax == yMin) {
        yMin -= 1;
    }
    if (xMax == xMin) {
        xMin -= 1;
    }

    // Set the increment to 1/100 of the total interval length.
    float xIncrement = std::abs(xMax - xMin) / 100.f;
    float yIncrement = std::abs(yMax - yMin) / 100.f;
    x_range_.setIncrement(vec2(xIncrement, xIncrement));
    y_range_.setIncrement(vec2(yIncrement, yIncrement));

    // Make sure that max an min values aren't the same.
    if (x_range_.get()[0] == x_range_.get()[1]) {
        x_range_.set(vec2(xMax, xMin));
    } else {
        // Otherwise we assign the set values as min/max.
        xMax = x_range_.get()[0];
        xMin = x_range_.get()[1];
    }

    if (y_range_.get()[0] == y_range_.get()[1]) {
        y_range_.set(vec2(yMax, yMin));
    } else {
        yMax = y_range_.get()[0];
        yMin = y_range_.get()[1];
    }

    if (xMax < xMin) {
        LogError("The maximum X value range can't be less"
                 " than the minimum X value range!");
        return;
    }
    if (yMax < yMin) {
        LogError("The maximum Y value range can't be less"
                 " than the minimum Y value range!");
        return;
    }

    // Draw background grid.
    drawAxes(mesh, x_range_.getMinValue()[0], x_range_.getMaxValue()[0],
             y_range_.getMinValue()[0], y_range_.getMaxValue()[0]);

    textRenderer_.setFontSize(font_.fontSize_);
    textRenderer_.setFont(font_.fontFace_);

    utilgl::activateAndClearTarget(labels_, ImageType::ColorDepth);
    drawScale(xMin, xMax, yMin, yMax);
    utilgl::deactivateCurrentTarget();

    // If the static line is enabled, add it.
    if (enable_line_.get() &&
        (line_x_coordinate_.get() <= x_range_.get()[0] &&
         line_x_coordinate_.get() >= x_range_.get()[1])) {
        float s = scale_.get();
        vec3 yStartPoint = vec3(s * normalise(line_x_coordinate_.get(), xMin, xMax) + (1 - s) / 2,
                                s * normalise(y_range_.getMinValue()[0], yMin, yMax) + (1 - s) / 2,
                                0);
        vec3 yEndPoint = vec3(s * normalise(line_x_coordinate_.get(), xMin, xMax) + (1 - s) / 2,
                              s * normalise(y_range_.getMaxValue()[0], yMin, yMax) + (1 - s) / 2,
                              0);
        mesh->append(lineMesh(yStartPoint, yEndPoint, vec3(0, 0, 1),
                              line_colour_.get(), axis_width_.get(),
                              ivec2(2, 2)).get());
    } else if (enable_line_.get()) {
        LogError("Line out of range!");
    }

    // Each line segment should start on the current point and end
    // at the next point. Subtract one from the end criteria,
    // since the last point is included when the segment is drawn
    // from the next-to-last point.
    if (!allYSelection_.get()) {
        for (size_t i = 0; i < xSize - 1; i++) {
            //Make sure the data is within viewing range
            if (x->getAsDouble(i + 1) < x_range_.get()[0] && x->getAsDouble(i) > x_range_.get()[1] &&
                y->getAsDouble(i + 1) < y_range_.get()[0] && y->getAsDouble(i) > y_range_.get()[1]) {
                // Get coordinates, normalise them to [0, 1], scale them
                // and center them.
                float s = scale_.get();
                double xStart = s * normalise(x->getAsDouble(i), xMin, xMax)
                                + (1 - s) / 2;
                double yStart = s * normalise(y->getAsDouble(i), yMin, yMax)
                                + (1 - s) / 2;
                double xEnd = s * normalise(x->getAsDouble(i + 1), xMin, xMax)
                              + (1 - s) / 2;
                double yEnd = s * normalise(y->getAsDouble(i + 1), yMin, yMax)
                              + (1 - s) / 2;

                vec3 startPoint = vec3(xStart, yStart, 0);
                indices->add(mesh->addVertex(startPoint, startPoint,
                                             startPoint, colour_));

                vec3 endPoint = vec3(xEnd, yEnd, 0);
                indices->add(mesh->addVertex(endPoint, endPoint,
                                             endPoint, colour_));
            }
        }
    } else {
        for (size_t column = 0; column < yData.size(); column++) {
            for (size_t i = 0; i < xSize - 1; i++) {
                //Make sure the data is within viewing range
                if (xData->getAsDouble(i + 1) < x_range_.get()[0] && xData->getAsDouble(i) > x_range_.get()[1] &&
                    yData.at(column)->getAsDouble(i + 1) < y_range_.get()[0] && yData.at(column)->getAsDouble(i) > y_range_.get()[1]) {
                    // Get coordinates, normalise them to [0, 1], scale them
                    // and center them.
                    float s = scale_.get();
                    double xStart = s * normalise(xData->getAsDouble(i), xMin, xMax)
                                    + (1 - s) / 2;
                    double yStart = s * normalise(yData.at(column)->getAsDouble(i), yMin, yMax)
                                    + (1 - s) / 2;
                    double xEnd = s * normalise(xData->getAsDouble(i + 1), xMin, xMax)
                                  + (1 - s) / 2;
                    double yEnd = s * normalise(yData.at(column)->getAsDouble(i + 1), yMin, yMax)
                                  + (1 - s) / 2;

                    vec3 startPoint = vec3(xStart, yStart, 0);
                    indices->add(mesh->addVertex(startPoint, startPoint,
                                                 startPoint, colour_));

                    vec3 endPoint = vec3(xEnd, yEnd, 0);
                    indices->add(mesh->addVertex(endPoint, endPoint,
                                                 endPoint, colour_));
                }
            }
        }
    }
    meshOutport_.setData(mesh);
}

void LinePlotProcessor::drawAxes(std::shared_ptr<BasicMesh>& mesh,
                                 double xMin, double xMax,
                                 double yMin, double yMax) {
    // Draw the X axis. It should always be on the bottom of the Y axis.
    float s = scale_.get();
    vec3 xStartPoint = vec3(s * normalise(x_range_.getMinValue()[0], xMin, xMax) + (1 - s) / 2,
                            s * normalise(y_range_.getMinValue()[0], yMin, yMax) + (1 - s) / 2,
                            0);
    vec3 xEndPoint = vec3(s * normalise(x_range_.getMaxValue()[0], xMin, xMax) + (1 - s) / 2,
                          s * normalise(y_range_.getMinValue()[0], yMin, yMax) + (1 - s) / 2,
                          0);
    mesh->append(lineMesh(xStartPoint, xEndPoint, vec3(0, 0, 1),
                          axis_colour_.get(), axis_width_.get() + 0.001,
                          ivec2(2, 2)).get());

    // Draw the Y axis. It should always be on the left of the X axis.
    vec3 yStartPoint = vec3(s * normalise(x_range_.getMinValue()[0], xMin, xMax) + (1 - s) / 2,
                            s * normalise(y_range_.getMinValue()[0], yMin, yMax) + (1 - s) / 2,
                            0);
    vec3 yEndPoint = vec3(s * normalise(x_range_.getMinValue()[0], xMin, xMax) + (1 - s) / 2,
                          s * normalise(y_range_.getMaxValue()[0], yMin, yMax) + (1 - s) / 2,
                          0);
    mesh->append(lineMesh(yStartPoint, yEndPoint, vec3(0, 0, 1),
                          axis_colour_.get(), axis_width_.get(),
                          ivec2(2, 2)).get());

    // Draw background grid.
    double xStepSize = std::abs(xMax - xMin) / label_number_.get();
    for (double x = xMin + xStepSize; x <= xMax; x += xStepSize) {
        vec3 yStartPoint = vec3(s * normalise(x, xMin, xMax) + (1 - s) / 2,
                                s * normalise(y_range_.getMinValue()[0],
                                              yMin, yMax) + (1 - s) / 2,
                                0);
        vec3 yEndPoint = vec3(s * normalise(x, xMin, xMax) + (1 - s) / 2,
                              s * normalise(y_range_.getMaxValue()[0],
                                            yMin, yMax) + (1 - s) / 2,
                              0);
        if (enable_grid_.get()) {
            mesh->append(lineMesh(yStartPoint, yEndPoint, vec3(0, 0, 1),
                                  grid_colour_.get(), grid_width_.get(),
                                  ivec2(2, 2)).get());
        }
        mesh->append(lineMesh(yStartPoint, yStartPoint + vec3(0, -0.01, 0), vec3(0, 0, 1),
                              axis_colour_.get(), axis_width_.get(),
                              ivec2(2, 2)).get());
    }

    double yStepSize = std::abs(yMax - yMin) / label_number_.get();
    for (double y = yMin + yStepSize; y <= yMax; y += yStepSize) {
        float s = scale_.get();
        vec3 xStartPoint = vec3(s * normalise(x_range_.getMinValue()[0],
                                              xMin, xMax) + (1 - s) / 2,
                                s * normalise(y, yMin, yMax) + (1 - s) / 2,
                                0);
        vec3 xEndPoint = vec3(s * normalise(x_range_.getMaxValue()[0],
                                            xMin, xMax) + (1 - s) / 2,
                              s * normalise(y, yMin, yMax) + (1 - s) / 2,
                              0);
        if (enable_grid_.get()) {
            mesh->append(lineMesh(xStartPoint, xEndPoint, vec3(0, 0, 1),
                                  grid_colour_.get(), grid_width_.get() + 0.001,
                                  ivec2(2, 2)).get());
        }
        mesh->append(lineMesh(xStartPoint, xStartPoint + vec3(-0.01, 0, 0), vec3(0, 0, 1),
                              axis_colour_.get(), axis_width_.get() + 0.001,
                              ivec2(2, 2)).get());
    }

    // Draw end of the Y axis.
    mesh->append(lineMesh(yEndPoint + vec3(-0.01, 0, 0), yEndPoint + vec3(0.01, 0, 0), vec3(0, 0, 1),
                          axis_colour_.get(), axis_width_.get() + 0.001,
                          ivec2(2, 2)).get());

    // Draw end of the X axis.
    mesh->append(lineMesh(xEndPoint + vec3(0, -0.01, 0), xEndPoint + vec3(0, 0.01, 0), vec3(0, 0, 1),
                          axis_colour_.get(), axis_width_.get(),
                          ivec2(2, 2)).get());

    // Draw beginning of each axis.
    mesh->append(lineMesh(xStartPoint, xStartPoint + vec3(0, -0.01, 0), vec3(0, 0, 1),
                          axis_colour_.get(), axis_width_.get(),
                          ivec2(2, 2)).get());
    mesh->append(lineMesh(xStartPoint, xStartPoint + vec3(-0.01, 0, 0), vec3(0, 0, 1),
                          axis_colour_.get(), axis_width_.get() + 0.001,
                          ivec2(2, 2)).get());
}

void LinePlotProcessor::drawScale(double xMin, double xMax,
                                  double yMin, double yMax) {
    // Iterate over the length of the X axis and add the number scale.
    double xStepSize = std::abs(xMax - xMin) / label_number_.get();
    for (double x = xMin; x <= xMax; x += xStepSize) {
        float s = scale_.get();
        vec2 xAxis = vec2(s * normalise(x, xMin, xMax) + (1 - s) / 2,
                          s * normalise(yMin, yMin, yMax) + (1 - s) / 2);
        vec2 imageDims = labels_.getDimensions();
        vec2 imageCoords = vec2(imageDims[0] * xAxis[0], imageDims[1] * xAxis[1]);

        vec2 shift = imageDims * (font_.anchorPos_.get() + vec2(1.0f, 1.0f));
        imageCoords -= shift;
        std::stringstream ss;
        ss << std::fixed << std::setprecision(2) << x;
        if (show_x_labels_.get()) {
            drawText(ss.str(), imageCoords);
        }
    }
    // Iterate over the length of the Y axis and add the number scale.
    double yStepSize = std::abs(yMax - yMin) / label_number_.get();
    for (double y = yMin; y <= yMax; y += yStepSize) {
        float s = scale_.get();
        vec2 yAxis = vec2(s * normalise(xMin, xMin, xMax) +(1 - s) / 2,
                           s * normalise(y, yMin, yMax) + (1 - s) / 2);

        vec2 imageDims = labels_.getDimensions();
        vec2 imageCoords = vec2(imageDims[0] * yAxis[0], imageDims[1] * yAxis[1]);

        vec2 shift = 0.5f * imageDims * (font_.anchorPos_.get() + vec2(1.0f, 1.0f));
        imageCoords -= shift;
        std::stringstream ss;
        ss << std::fixed << std::setprecision(2) << y;
        if (show_y_labels_.get()) {
            drawText(ss.str(), imageCoords, true);
        }
    }
}

void LinePlotProcessor::drawText(const std::string& text, vec2 position, bool anchor_right) {
    std::shared_ptr<Texture2D> texture(nullptr);
    texture  = util::createTextTexture(textRenderer_,
                                       text,
                                       text_colour_.get(),
                                       texture);

    // If anchor_right is set, the text will be moved its own length
    // to the left, plus 20 %.
    // Else shift the text half of it's length to the right.
    vec2 offset = vec2(texture->getDimensions()[0], 0);
    if (anchor_right) {
        position -= 1.2f * offset;
    } else {
        position -= offset / 2.0f;
    }

    textureRenderer_.render(texture, position, labels_.getDimensions());
}

double LinePlotProcessor::normalise(double value, double min, double max) const {
    return (value - min) / (max - min);
}

} // namespace
