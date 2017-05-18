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
    , scalingFactor_("scalingFactor", "Scaling factor", 1.f)
    , basis_("basis", "Basis", glm::mat3x3())
    , fullMesh_("fullMesh", "Full mesh", false)
    , animation_("animation", "Animation", false)
    , timestep_("timestep", "Time step", false)


{
    addPort(structure_);
    addPort(mesh_);
    addProperty(scalingFactor_);
    addProperty(basis_);
    addProperty(fullMesh_);
    addProperty(animation_);
    addProperty(timestep_);

    structure_.onChange([&](){
        const auto data = structure_.getVectorData();
        for(int i = colors_.size(); i < data.size(); ++i) {
            colors_.push_back(std::make_unique<FloatVec4Property>("color" + toString(i), "Color " + toString(i),
                                                vec4(1.0f, 1.0f, 1.0f, 1.0f), vec4(0.0f), vec4(1.0f), vec4(0.01f),
                                                InvalidationLevel::InvalidOutput, PropertySemantics::Color));
            addProperty(colors_.back().get(), false);

            radii_.push_back(std::make_unique<FloatProperty>("radius"+ toString(i), "Atom Radius"+ toString(i), 1.0f));
            addProperty(radii_.back().get(), false);
            species_.push_back(std::make_unique<IntProperty>("atoms" + toString(i), "Atoms" + toString(i), 0));
            addProperty(species_.back().get(), false);
        }

    });

}

void StructureMesh::process() {
    if (fullMesh_.get()) {
	auto mesh = std::make_shared<BasicMesh>();
	mesh_.setData(mesh);
	size_t ind = 0;
	for (const auto &strucs : structure_) {
	    for (long long j = 0; j < static_cast<long long>(strucs->size()); ++j) {
		auto center = scalingFactor_.get() * basis_.get() * strucs->at(j) - 0.5f * (basis_.get()[0] + basis_.get()[1] + basis_.get()[2]);
		BasicMesh::sphere(center, radii_[ind]->get(), colors_[ind]->get(), mesh);
	    }
	    ++ind;
	}
    } else {
        int numSpheres = 0;
        for (const auto &strucs : structure_)
            numSpheres += strucs->size();

            auto mesh = std::make_shared<Mesh>(DrawType::Points, ConnectivityType::None);

        auto vertexRAM = std::make_shared<BufferRAMPrecision<vec3>>(numSpheres);
        auto colorRAM = std::make_shared<BufferRAMPrecision<vec4>>(numSpheres);
        auto radiiRAM = std::make_shared<BufferRAMPrecision<float>>(numSpheres);

        mesh->addBuffer(Mesh::BufferInfo(BufferType::PositionAttrib),
                        std::make_shared<Buffer<vec3>>(vertexRAM));
        mesh->addBuffer(Mesh::BufferInfo(BufferType::ColorAttrib),
                        std::make_shared<Buffer<vec4>>(colorRAM));
        mesh->addBuffer(Mesh::BufferInfo(BufferType::NumberOfBufferTypes, 5),
                        std::make_shared<Buffer<float>>(radiiRAM));

        auto& vertices = vertexRAM->getDataContainer();
        auto& colors = colorRAM->getDataContainer();
        auto& radii = radiiRAM->getDataContainer();


        mesh_.setData(mesh);
        size_t portInd = 0;
        size_t sphereInd = 0;
        for (const auto &strucs : structure_) {
            long long j_start, j_stop;
            j_start = 0;
            j_stop = static_cast<long long>(strucs->size());
            if (animation_.get()) {
                j_start = species_[portInd]->get() * timestep_.get();
                j_stop = species_[portInd]->get() * (timestep_.get() + 1);
            }
            for (long long j = j_start; j < j_stop ; ++j) {
                auto center = scalingFactor_.get() * basis_.get() * strucs->at(j) - 0.5f * (basis_.get()[0] + basis_.get()[1] + basis_.get()[2]);
                vertices[sphereInd] = center;
                colors[sphereInd] = colors_[portInd]->get();
                radii[sphereInd] = radii_[portInd]->get();
                ++sphereInd;
            }
            ++portInd;
        }
    }
}

} // namespace

