#ifndef IVW_HDF5TODATAFRAME_H
#define IVW_HDF5TODATAFRAME_H

#include <modules/graph2d/graph2dmoduledefine.h>

#include <inviwo/core/common/inviwo.h>
#include <inviwo/core/processors/processor.h>
#include <inviwo/core/ports/datainport.h>

#include <inviwo/dataframe/datastructures/dataframe.h>

#include <inviwo/core/properties/ordinalproperty.h>
#include <inviwo/core/properties/boolproperty.h>
#include <inviwo/core/properties/optionproperty.h>

#include <modules/hdf5/hdf5moduledefine.h>
#include <modules/hdf5/datastructures/hdf5handle.h>
#include <modules/hdf5/datastructures/hdf5metadata.h>
#include <modules/hdf5/hdf5utils.h>

/**
 *
 * Load one or more value columns into a DataFrame from a HDF5 file handle
 *
 * ### Inports
 *   * __inport__ HDF5 file handle
 *
 * ### Outports
 *   * __outport__ DataFrame
 *
 * ### Properties
 *   * __selectionMode__ ...
 *   * __colSelection1__ ...
 *   * __colSelection2__ ...
 *
 */

namespace inviwo {

class IVW_MODULE_GRAPH2D_API HDF5ToDataframe : public Processor {
public:
    HDF5ToDataframe();
    virtual ~HDF5ToDataframe() = default;

    virtual const ProcessorInfo getProcessorInfo() const override;
    static const ProcessorInfo processorInfo_;

protected:
    virtual void process() override;

private:

    DataInport<hdf5::Handle, 1, false> hdf5HandleInport_;
    DataOutport<DataFrame> dataframeOutport_;

    OptionPropertyString selectionMode_;
    OptionPropertyString colSelection1_;
    OptionPropertyString colSelection2_;

    std::vector<hdf5::MetaData> columnMatches_;

	std::string getDescription(const hdf5::MetaData&);

	// Reload options based on input hdf5
    void reloadHDF5Options();

	// Reload the columns in the output dataframe
	void reloadColumns();

	// Add a column to the dataframe based on hdf5 metadata and handle
	void addColumn(const hdf5::MetaData&, const std::shared_ptr<const hdf5::Handle>);

	size_t col_size_ = 0;
	std::shared_ptr<DataFrame> dataframe_;

};

} // namespace

#endif // IVW_HDF5TOFUNCTION_H

