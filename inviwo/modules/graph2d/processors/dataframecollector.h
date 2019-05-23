/************************************************************************
 *   This file was created 2019 by Abdullatif Ismail
 *
 *   To the extent possible under law, the person who associated CC0
 *   with the alterations to this file has waived all copyright and
 *   related or neighboring rights to the alterations made to this file.
 *
 *   You should have received a copy of the CC0 legalcode along with
 *   this work.  If not, see
 *   <http://creativecommons.org/publicdomain/zero/1.0/>.
 ************************************************************************/

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
