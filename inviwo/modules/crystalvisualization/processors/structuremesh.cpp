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

#include <modules/crystalvisualization/processors/structuremesh.h>
#include <inviwo/core/datastructures/geometry/basicmesh.h>

namespace inviwo {

// The Class Identifier has to be globally unique. Use a reverse DNS naming scheme
const ProcessorInfo StructureMesh::processorInfo_{
    "org.inviwo.StructureMesh",      // Class identifier
    "Structure Mesh",                // Display name
    "Crystal",              // Category
    CodeState::Experimental,  // Code state
    Tags::None,               // Tags
};
const ProcessorInfo StructureMesh::getProcessorInfo() const {
    return processorInfo_;
}

StructureMesh::StructureMesh()
    : Processor()
    , structure_("coordinates")
    , mesh_("mesh")

{
    addPort(structure_);
    addPort(mesh_);
    
    structure_.onChange([&](){
        const auto data = structure_.getVectorData();
        for(int i = colors_.size(); i < data.size(); ++i) {
            colors_.push_back(std::make_unique<FloatVec4Property>("color" + toString(i), "Color " + toString(i),
                                                vec4(1.0f, 1.0f, 1.0f, 1.0f), vec4(0.0f), vec4(1.0f), vec4(0.01f),
                                                InvalidationLevel::InvalidOutput, PropertySemantics::Color));
            addProperty(colors_.back().get(), false);

            radii_.push_back(std::make_unique<FloatProperty>("radius"+ toString(i), "Atom Radius"+ toString(i), 1.0f));
            addProperty(radii_.back().get(), false);
        }          

    });

}
    
void StructureMesh::process() {
    auto mesh = std::make_shared<BasicMesh>();
    mesh_.setData(mesh);
    size_t ind = 0;
    for (const auto &strucs : structure_) {
        for (long long j = 0; j < static_cast<long long>(strucs->size()); ++j) {
            auto center = strucs->at(j);
            BasicMesh::sphere(center, radii_[ind]->get(), colors_[ind]->get(), mesh);
        }
        ++ind;
    }
}

} // namespace

