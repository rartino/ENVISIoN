/*********************************************************************************
 *
 * Copyright (c) 2017 Robert Cranston
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

#ifndef IVW_PLOTTER_H
#define IVW_PLOTTER_H

#include <modules/graph2d/graph2dmoduledefine.h>

#include <inviwo/core/common/inviwo.h>
#include <inviwo/core/ports/imageport.h>
#include <inviwo/core/processors/processor.h>
#include <inviwo/core/properties/optionproperty.h>
#include <inviwo/core/properties/boolproperty.h>
#include <inviwo/core/properties/minmaxproperty.h>

#include <modules/graph2d/datastructures/graph2ddata.h>

namespace inviwo {

/** \docpage{org.inviwo.Plotter, Plotter}
 * ![](org.inviwo.Plotter.png?classIdentifier=org.inviwo.Plotter)
 * Explanation of how to use the processor.
 *
 * ### Inports
 *   * __<Inport1>__ <description>.
 *
 * ### Outports
 *   * __<Outport1>__ <description>.
 *
 * ### Properties
 *   * __<Prop1>__ <description>.
 *   * __<Prop2>__ <description>
 */


/**
 * \class Plotter
 * \brief VERY_BRIEFLY_DESCRIBE_THE_PROCESSOR
 * DESCRIBE_THE_PROCESSOR_FROM_A_DEVELOPER_PERSPECTIVE
 */
class IVW_MODULE_GRAPH2D_API Plotter : public Processor {

public:

    Plotter();
    virtual ~Plotter() = default;

    virtual void process() override;

    virtual const ProcessorInfo getProcessorInfo() const override;
    static const ProcessorInfo processorInfo_;

private:

    DataInport<Function, 0, true> functionFlatMultiInport_;
    DataInport<Point, 0, true> markXFlatMultiInport_;
    DataInport<Point, 0, true> markYFlatMultiInport_;

    BoolProperty sortOnNameProperty_;
    BoolProperty legendShowProperty_;
    BoolProperty legendSymbolsProperty_;
    OptionPropertyString markShiftToZeroXProperty_;
    OptionPropertyString markShiftToZeroYProperty_;
    BoolProperty axisLimitAutoAdjustXProperty_;
    FloatMinMaxProperty axisLimitXProperty_;
    BoolProperty axisLimitAutoAdjustYProperty_;
    FloatMinMaxProperty axisLimitYProperty_;

    ImageOutport imageOutport_;
};

} // namespace

#endif // IVW_PLOTTER_H

