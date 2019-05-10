/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2019 Abdullatif Ismail
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

#ifndef IVW_DATAFRAMECOLLECTOR_H
#define IVW_DATAFRAMECOLLECTOR_H

#include <modules/graph2d/graph2dmoduledefine.h>
#include <inviwo/core/common/inviwo.h>
#include <inviwo/core/ports/datainport.h>
#include <inviwo/core/processors/processor.h>
#include <modules/plotting/datastructures/dataframe.h>
#include <modules/graph2d/datastructures/graph2ddata.h>

using inviwo::plot::DataFrame;
using inviwo::plot::DataFrameOutport;

namespace inviwo {

/**
 * \class DataFrameCollector
 * Collects data frames into a single data frame.
 */
    class IVW_MODULE_GRAPH2D_API DataFrameCollector : public Processor {

    public:
    DataFrameCollector();
    virtual ~DataFrameCollector() = default;
    virtual void process() override;
    virtual const ProcessorInfo getProcessorInfo() const override;
    static const ProcessorInfo processorInfo_;
    private:
    DataInport<DataFrame, 0> dataframeInport_;
    DataFrameOutport dataframeOutport_;
};

} // namespace

#endif // IVW_DATAFRAMECOLLECTOR_H