/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2017 Inviwo Foundation
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

#include <modules/graph2d/processors/hdf5pathselectionallchildren.h>

#include <inviwo/core/common/inviwo.h>

namespace inviwo {

const ProcessorInfo HDF5PathSelectionAllChildren::processorInfo_ {
        "org.inviwo.HDF5PathSelectionAllChildren",  // Class identifier.
        "HDF5 Path Selection All Children",         // Display name.
        "Data Input",                               // Category.
        CodeState::Stable,                          // Code state.
        Tags::None,                                 // Tags.
    };

const ProcessorInfo HDF5PathSelectionAllChildren::getProcessorInfo() const {
    return processorInfo_;
}

HDF5PathSelectionAllChildren::HDF5PathSelectionAllChildren()
    : Processor()
    , hdf5HandleInport_("hdf5HandleInport")
    , hdf5HandleVectorOutport_("hdf5HandleVectorOutport")
{
    addPort(hdf5HandleInport_);

    addPort(hdf5HandleVectorOutport_);
}

void HDF5PathSelectionAllChildren::process() {

    const auto& hdf5HandleVectorSharedPtr = std::make_shared<std::vector<hdf5::Handle>>();
    hdf5HandleVectorOutport_.setData(hdf5HandleVectorSharedPtr);

    const auto& hdf5HandleSharedPtr = hdf5HandleInport_.getData();

    std::vector<std::string> hdf5PathVector;
    const auto& group = hdf5HandleSharedPtr->getGroup();
    for (hsize_t childIndex = 0; childIndex < group.getNumObjs(); ++childIndex) {
        const auto& childName = group.getObjnameByIdx(childIndex);
        if (group.getObjTypeByIdx(childIndex) == H5G_GROUP)
            hdf5PathVector.push_back(childName);
    }

    std::sort(hdf5PathVector.begin(), hdf5PathVector.end());

    for (const auto& hdf5Path : hdf5PathVector) {
        // WORKAROUND: `getHandleForPath` should really return a value not a pointer...
        auto hdf5PathHandle = hdf5HandleSharedPtr->getHandleForPath(hdf5Path);
        hdf5HandleVectorSharedPtr->emplace_back(std::move(*hdf5PathHandle));
        delete hdf5PathHandle;
    }
}

} // namespace

