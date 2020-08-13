#include <modules/graph2d/processors/hdf5todataframe.h>
#include <inviwo/core/common/inviwo.h>

namespace inviwo {

const ProcessorInfo HDF5ToDataframe::processorInfo_ {
        "org.inviwo.HDF5ToDataframe",   // Class identifier.
        "HDF5 To Dataframe",            // Display name.
        "Data Input",                   // Category.
        CodeState::Stable,              // Code state.
        Tags::None,                     // Tags.
    };

const ProcessorInfo HDF5ToDataframe ::getProcessorInfo() const {
    return processorInfo_;
}

HDF5ToDataframe::HDF5ToDataframe()
    : Processor()
    , hdf5HandleInport_("inport")
    , dataframeOutport_("outport")
    , selectionMode_("selectionMode", "Column selection mode")
    , colSelection1_("colSelection1", "Column 1")
    , colSelection2_("colSelection2", "Column 2")
	, dataframe_{ std::make_shared<DataFrame>(0) }
{
	hdf5HandleInport_.onChange([this]() { reloadHDF5Options(); });

	selectionMode_.addOption("One column", "One column", "One column");
	selectionMode_.addOption("Two columns", "Two columns", "Two columns");
	selectionMode_.addOption("All columns", "All columns", "All columns");

	addPort(hdf5HandleInport_);
	addPort(dataframeOutport_);

    addProperty(selectionMode_);
    addProperty(colSelection1_);
    addProperty(colSelection2_);
}

void HDF5ToDataframe::reloadHDF5Options() {
	if (!hdf5HandleInport_.hasData()) {
		colSelection1_.clearOptions();
		colSelection2_.clearOptions();
		return;
	}

    const auto data = hdf5HandleInport_.getData();
    std::vector<hdf5::MetaData> metadata = hdf5::util::getMetaData(data->getGroup());
	
	LogInfo("Port changed3");
	
	
	// Update column matches
    columnMatches_.clear();
	std::copy_if(metadata.begin(), metadata.end(), std::back_inserter(columnMatches_), 
	 	[this](const hdf5::MetaData& meta) {
			auto dims = meta.getColumnMajorDimensions();
			if (meta.type_ != hdf5::MetaData::HDFType::DataSet || dims.size() != 1 || dims[0] == 0) return false;
			if (col_size_ == 0) col_size_ = dims[0];
			return col_size_ == dims[0];
	});


	// Update column selection properties
	std::vector<OptionPropertyStringOption> columnOptions;
	for (const auto& meta : columnMatches_) {
		columnOptions.emplace_back(meta.path_, getDescription(meta), meta.path_);
	}

	colSelection1_.replaceOptions(columnOptions);
	colSelection2_.replaceOptions(columnOptions);
	colSelection1_.setCurrentStateAsDefault();
	colSelection2_.setCurrentStateAsDefault();

}

std::string HDF5ToDataframe::getDescription(const hdf5::MetaData& meta) {
	return meta.path_.toString() +
		(meta.format_ ? (" " + std::string(meta.format_->getString())) : "") + " [" +
		joinString(meta.getColumnMajorDimensions(), ", ") + "]";
}

void HDF5ToDataframe::reloadColumns() {
	// Initialize new dataframe
	dataframe_ = std::make_shared<DataFrame>(0);

	// Exit if valid data exists.
	if (columnMatches_.size() == 0 || !hdf5HandleInport_.hasData()) return;

	const auto handle = hdf5HandleInport_.getData();

	// Load columns from hdf5 file
	switch (selectionMode_.getSelectedIndex())
	{
	case 0:
		addColumn(columnMatches_[colSelection1_.getSelectedIndex()], handle);
		break;
	case 1:
		addColumn(columnMatches_[colSelection1_.getSelectedIndex()], handle);
		addColumn(columnMatches_[colSelection2_.getSelectedIndex()], handle);
		break;
	case 2:
		for (size_t i = 0; i < columnMatches_.size(); ++i)
			addColumn(columnMatches_[i], handle);
		break;
	}

}

void HDF5ToDataframe::addColumn(const hdf5::MetaData& meta, const std::shared_ptr<const hdf5::Handle> handle) {
	const std::vector<float> vec = handle->getVectorAtPath<float>(hdf5::Path(handle->getGroup().getObjName()) + meta.path_);
	std::shared_ptr<TemplateColumn<float>> col = dataframe_->addColumn<float>(meta.path_.toString(), col_size_);
	for (size_t i = 0; i < vec.size(); ++i) {
		col->set(i, vec[i]);
	}
}

void HDF5ToDataframe::process() {
	reloadColumns();
	dataframeOutport_.setData(dataframe_);
}

} // namespace
