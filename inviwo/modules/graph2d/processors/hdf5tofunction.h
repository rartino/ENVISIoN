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

#ifndef IVW_HDF5TOFUNCTION_H
#define IVW_HDF5TOFUNCTION_H

#include <modules/graph2d/graph2dmoduledefine.h>

#include <inviwo/core/common/inviwo.h>
#include <inviwo/core/ports/datainport.h>
#include <inviwo/core/processors/processor.h>
#include <inviwo/core/properties/boolproperty.h>
#include <inviwo/core/properties/optionproperty.h>
#include <inviwo/core/properties/ordinalproperty.h>

#include <modules/hdf5/datastructures/hdf5handle.h>

#include <modules/graph2d/datastructures/graph2ddata.h>

namespace inviwo {

/** \docpage{org.inviwo.HDF5ToFunction, HDF5ToFunction}
 * ![](org.inviwo.HDF5ToFunction.png?classIdentifier=org.inviwo.HDF5ToFunction)
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
 * \class HDF5ToFunction
 * \brief VERY_BRIEFLY_DESCRIBE_THE_PROCESSOR
 * DESCRIBE_THE_PROCESSOR_FROM_A_DEVELOPER_PERSPECTIVE
 */
class IVW_MODULE_GRAPH2D_API HDF5ToFunction : public Processor {

public:

    HDF5ToFunction();
    virtual ~HDF5ToFunction() = default;

    virtual void process() override;

    virtual const ProcessorInfo getProcessorInfo() const override;
    static const ProcessorInfo processorInfo_;

private:

    DataInport<hdf5::Handle, 0, true> hdf5HandleFlatMultiInport_;

    BoolProperty implicitXProperty_;
    OptionPropertyString xPathSelectionProperty_;
    OptionPropertyString yPathSelectionProperty_;
    BoolProperty xPathFreezeProperty_;
    BoolProperty yPathFreezeProperty_;
    IntSizeTProperty xNamePrependParentsProperty_;
    IntSizeTProperty yNamePrependParentsProperty_;

    DataOutport<std::vector<Function>> functionVectorOutport_;

    void pathSelectionOptionsReplace(OptionPropertyString& pathSelectionProperty);
};

} // namespace

#endif // IVW_HDF5TOFUNCTION_H

