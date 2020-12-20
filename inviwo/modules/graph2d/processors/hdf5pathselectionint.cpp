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

#include <modules/graph2d/processors/hdf5pathselectionint.h>

#include <inviwo/core/common/inviwo.h>

namespace inviwo {

const ProcessorInfo HDF5PathSelectionInt::processorInfo_ {
        "org.inviwo.HDF5PathSelectionInt",  // Class identifier.
        "HDF5 Path Selection Int",          // Display name.
        "Data Input",                       // Category.
        CodeState::Stable,                  // Code state.
        Tags::None,                         // Tags.
    };

const ProcessorInfo HDF5PathSelectionInt::getProcessorInfo() const {
    return processorInfo_;
}

HDF5PathSelectionInt::HDF5PathSelectionInt()
    : Processor()
    , hdf5HandleInport_("hdf5HandleInport")
    , intProperty_("intProperty", "Int")
    , zeroPadWidthProperty_("zeroPadWidthProperty_", "Zero pad width")
    , hdf5HandleVectorOutport_("hdf5HandleVectorOutport")
{
    addPort(hdf5HandleInport_);

    addProperty(intProperty_);
    addProperty(zeroPadWidthProperty_);

    addPort(hdf5HandleVectorOutport_);
}

void HDF5PathSelectionInt::process() {

    const auto& hdf5HandleVectorSharedPtr = std::make_shared<std::vector<hdf5::Handle>>();
    hdf5HandleVectorOutport_.setData(hdf5HandleVectorSharedPtr);

    const auto& hdf5HandleSharedPtr = hdf5HandleInport_.getData();

    std::ostringstream ostringstream;
    const auto& zeroPadWidth = zeroPadWidthProperty_.get();
    if (zeroPadWidth != 0)
        ostringstream << std::setfill('0') << std::setw(zeroPadWidth);
    ostringstream << intProperty_.get();
    const auto& hdf5Path = ostringstream.str();

    // WORKAROUND: `getHandleForPath` should really return a value not a pointer...
    auto hdf5PathHandle = hdf5HandleSharedPtr->getHandleForPath(hdf5Path);
    hdf5HandleVectorSharedPtr->emplace_back(std::move(*hdf5PathHandle));
    delete hdf5PathHandle;
}

} // namespace

