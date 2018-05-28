/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2017-2018 Inviwo Foundation, Andreas Kempe
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
 *   Alterations to this file by Andreas Kempe
 *
 *   To the extent possible under law, the person who associated CC0
 *   with the alterations to this file has waived all copyright and
 *   related or neighboring rights to the alterations made to this file.
 *
 *   You should have received a copy of the CC0 legalcode along with
 *   this work.  If not, see
 *   <http://creativecommons.org/publicdomain/zero/1.0/>.
 */

#ifndef IVW_LINEPLOTPROCESSOR_H
#define IVW_LINEPLOTPROCESSOR_H

#include <inviwo/core/common/inviwo.h>
#include <inviwo/core/datastructures/geometry/basicmesh.h>
#include <inviwo/core/ports/imageport.h>
#include <inviwo/core/ports/meshport.h>
#include <inviwo/core/processors/processor.h>
#include <inviwo/core/properties/ordinalproperty.h>
#include <modules/fontrendering/properties/fontproperty.h>
#include <modules/fontrendering/textrenderer.h>
#include <modules/graph2d/graph2dmoduledefine.h>
#include <modules/opengl/rendering/texturequadrenderer.h>
#include <modules/plotting/datastructures/dataframe.h>

namespace inviwo {

using plot::DataFrameInport;

/** \docpage{org.inviwo.lineplotprocessor, lineplotprocessor}
 * ![](org.inviwo.lineplotprocessor.png?classIdentifier=org.inviwo.lineplotprocessor)
 * This processor draws a diagram from a DataFrame containing two
 * columns, one named "X" and one named "Y". It plots the values of
 * the "X" column on the horizontal axis versus the "Y" values on the
 * vertical axis.
 *
 * ### Inports
 *   * __dataFrameInport__ is an inport that takes a DataFrame
 *   expected to contain two columns. One named "X" and one named "Y",
 *   containing the x values to be plotted against the y values.
 *
 * ### Outports
 *   * __outport__ outport that outputs a mesh representing the
 *   line graph. Should probably be rendered using the 2D Mesh
 *   Renderer GL processor.
 *   * __labels__ outputs an image that provides the number labels for
 *   the axes. Should probably be rendered using the 2D Mesh Renderer
 *   GL processor.
 *
 * ### Properties
 *   * __x_range__ contains the minimum and maximum values for the x
 *   axis.
 *   * __y_range__ contains the minimum and maximum values for the y
 *   axis.
 *   * __scale__ contains a constant by which the graph will be
 *   scaled.
 *   * __enable_line__ enables a vertical line at x =
 *   line_x_coordinate.
 *   * __line_x_coordinate__ x coordinate at which to draw a vertical
 *   * __line_colour__ is the colour of the static vertical line.
 *   line.
 *   * __axis_colour__ contains the colour of the graph axes.
 *   * __axis_width__ sets how wide the graph axes should be.
 *   * __grid_colour__ sets the colour of the coordinate grid in the
 *   graph.
 *   * __grid_width__ sets the line width for the coordinate grid in
 *   the graph.
 *   * __font__ sets the font for all text in the graph.
 *   * __text_colour__ sets the colour of all text in the graph.
 *   * __label_number__ sets the number of labels, i.e. subdivisions,
 *   to make of the coordinate axes.
 */


/**
 * \class lineplotprocessor
 * \brief VERY_BRIEFLY_DESCRIBE_THE_PROCESSOR
 * DESCRIBE_THE_PROCESSOR_FROM_A_DEVELOPER_PERSPECTIVE
 */
class IVW_MODULE_GRAPH2D_API lineplotprocessor : public Processor {
public:
    lineplotprocessor();
    virtual ~lineplotprocessor() = default;

    virtual void process() override;

    virtual const ProcessorInfo getProcessorInfo() const override;
    static const ProcessorInfo processorInfo_;
private:
    void drawAxes(std::shared_ptr<BasicMesh>& mesh, double x_min, double x_max,
                  double y_min, double y_max);
    void drawScale(double x_min, double x_max,
                   double y_min, double y_max);
    void drawText(const std::string& text, vec2 position, bool anchor_right = false);
    double normalise(double value, double min, double max) const;

    DataFrameInport dataFrameInport_;
    MeshOutport meshOutport_;
    FloatVec4Property colour_;
    FloatVec2Property x_range_;
    FloatVec2Property y_range_;
    FloatProperty scale_;

    BoolProperty enable_line_;
    FloatProperty line_x_coordinate_;
    FloatVec4Property line_colour_;

    FloatVec4Property axis_colour_;
    FloatProperty axis_width_;

    FloatVec4Property grid_colour_;
    FloatProperty grid_width_;

    FontProperty font_;
    TextRenderer textRenderer_;
    TextureQuadRenderer textureRenderer_;
    FloatVec4Property text_colour_;
    IntProperty label_number_;

    ImageOutport labels_;
};

} // namespace

#endif // IVW_LINEPLOTPROCESSOR_H

