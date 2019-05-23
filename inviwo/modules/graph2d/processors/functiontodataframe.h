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

#ifndef IVW_FUNCTIONTODATAFRAME_H
#define IVW_FUNCTIONTODATAFRAME_H

#include <modules/graph2d/graph2dmoduledefine.h>
#include <inviwo/core/common/inviwo.h>
#include <inviwo/core/ports/datainport.h>
#include <inviwo/core/processors/processor.h>
#include <modules/plotting/datastructures/dataframe.h>
#include <modules/graph2d/datastructures/graph2ddata.h>

using inviwo::plot::DataFrame;
using inviwo::plot::DataFrameOutport;

namespace inviwo {

/** \docpage{org.inviwo.FunctionToDataFrame, Function To Data Frame}
 * ![](org.inviwo.FunctionToDataFrame.png?classIdentifier=org.inviwo.FunctionToDataFrame)
 * Explanation of how to use the processor.
 *
 * ### Inports
 *   * __functionFlatMultiImport__
 *   Made to take data from 'HDF5 To Function' processor.
 *   Able to handle multiple vectors of data.
 *
 * ### Outports
 *   * __dataFrame__
 *   Made to give data to 'Line Plot' processor.
 *
 * ### Properties
 *   This processor doesn't have any properties.
 */


/**
 * \class FunctionToDataFrame
 * Converts function data to data frame of columns.
 */
class IVW_MODULE_GRAPH2D_API FunctionToDataFrame : public Processor {

public:
    FunctionToDataFrame();
    virtual ~FunctionToDataFrame() = default;
    virtual void process() override;
    virtual const ProcessorInfo getProcessorInfo() const override;
    static const ProcessorInfo processorInfo_;
private:
    DataInport<Function, 0, true> functionFlatMultiInport_;
    DataFrameOutport dataframeOutport_;
};

} // namespace

#endif // IVW_FUNCTIONTODATAFRAME_H
