/*********************************************************************************
 *
 * Copyright (c) 2017-2018 Josef Adamsson, Denise Härnström, Anders Rehult,
 *                         Andreas Kempe
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

#include <inviwo/core/interaction/events/pickingevent.h>
#include <inviwo/core/interaction/events/mouseevent.h>
#include <inviwo/core/datastructures/buffer/bufferramprecision.h>
#include <inviwo/core/datastructures/buffer/buffer.h>

namespace inviwo {

// The Class Identifier has to be globally unique. Use a reverse DNS naming scheme
const ProcessorInfo StructureMesh::processorInfo_{
    "envision.StructureMesh",      // Class identifier
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
    , enablePicking_("enablePicking", "Enable Picking", false)
    , spherePicking_(this, 0, [&](PickingEvent* p) { handlePicking(p); })
    , pickedIndex_("pickedIndex", "Picked atom") {
    addPort(structure_);
    addPort(mesh_);
    addProperty(scalingFactor_);
    addProperty(basis_);
    addProperty(fullMesh_);
    addProperty(animation_);
    addProperty(timestep_);
    addProperty(enablePicking_);
    addProperty(pickedIndex_);

    pickedIndex_.setReadOnly(true);

    structure_.onChange([&](){
        const auto data = structure_.getVectorData();
        for(size_t i = colors_.size(); i < data.size(); ++i) {
            colors_.push_back(std::make_unique<FloatVec4Property>("color" + toString(i), "Color " + toString(i),
                                                vec4(1.0f, 1.0f, 1.0f, 1.0f), vec4(0.0f), vec4(1.0f), vec4(0.01f),
                                                InvalidationLevel::InvalidOutput, PropertySemantics::Color));
            addProperty(colors_.back().get(), false);

            radii_.push_back(std::make_unique<FloatProperty>("radius"+ toString(i), "Atom Radius"+ toString(i), 1.0f));
            addProperty(radii_.back().get(), false);
            num_.push_back(std::make_unique<IntProperty>("atoms" + toString(i), "Atoms" + toString(i), 0));
            addProperty(num_.back().get(), false);
        }
        int numSpheres = 0;
        for (const auto &strucs : structure_)
            numSpheres += strucs->size();
        spherePicking_.resize(numSpheres);

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
        if (structure_.isChanged() || animation_.isModified() || std::any_of(num_.begin(), num_.end(),
            [](const std::unique_ptr<IntProperty>& property) {
            return property->isModified();
            }) || enablePicking_.isModified()) {
            int numSpheres = 0;
            size_t pInd = 0;
            for (const auto &strucs : structure_) {
                if (animation_.get()) {
                    numSpheres += num_[pInd]->get();
                    ++pInd;
                }
                else {
                    numSpheres += strucs->size();
                }
            }
            vertexRAM_ = std::make_shared<BufferRAMPrecision<vec3>>(numSpheres);
            colorRAM_ = std::make_shared<BufferRAMPrecision<vec4>>(numSpheres);
            radiiRAM_ = std::make_shared<BufferRAMPrecision<float>>(numSpheres);
            auto mesh = std::make_shared<Mesh>(DrawType::Points, ConnectivityType::None);
            mesh->addBuffer(Mesh::BufferInfo(BufferType::PositionAttrib),
                std::make_shared<Buffer<vec3>>(vertexRAM_));
            mesh->addBuffer(Mesh::BufferInfo(BufferType::ColorAttrib),
                std::make_shared<Buffer<vec4>>(colorRAM_));
            mesh->addBuffer(Mesh::BufferInfo(BufferType::NumberOfBufferTypes, 5),
                std::make_shared<Buffer<float>>(radiiRAM_));

            mesh_.setData(mesh);

            if (enablePicking_.get()) {
                auto pickingRAM = std::make_shared<BufferRAMPrecision<uint32_t>>(numSpheres);
                auto& data = pickingRAM->getDataContainer();
                // fill in picking IDs
                std::iota(data.begin(), data.end(), static_cast<uint32_t>(spherePicking_.getPickingId(0)));

                mesh->addBuffer(Mesh::BufferInfo(BufferType::NumberOfBufferTypes, 4),
                    std::make_shared<Buffer<uint32_t>>(pickingRAM));
            }
        }



        auto& vertices = vertexRAM_->getDataContainer();
        auto& colors = colorRAM_->getDataContainer();
        auto& radii = radiiRAM_->getDataContainer();

        size_t portInd = 0;
        size_t sphereInd = 0;
        for (const auto &strucs : structure_) {
            long long j_start, j_stop;
            j_start = 0;
            j_stop = static_cast<long long>(strucs->size());
            if (animation_.get()) {
                j_start = num_[portInd]->get() * timestep_.get();
                j_stop = num_[portInd]->get() * (timestep_.get() + 1);
            }
            for (long long j = j_start; j < j_stop ; ++j) {
                auto center = scalingFactor_.get() * basis_.get() * strucs->at(j); //- 0.5f * (basis_.get()[0] + basis_.get()[1] + basis_.get()[2]);
                vertices[sphereInd] = center;
                colors[sphereInd] = colors_[portInd]->get();
                radii[sphereInd] = radii_[portInd]->get();
                ++sphereInd;
            }
            ++portInd;
        }
        if (enablePicking_.get()) {
            //Set alpha-layer of any picked atom
            size_t idx = pickedIndex_.get();
            if (idx < sphereInd) {
                colors[idx].w = 0.5;
            }
        }
        colorRAM_->getOwner()->invalidateAllOther(colorRAM_.get());
        vertexRAM_->getOwner()->invalidateAllOther(vertexRAM_.get());
        radiiRAM_->getOwner()->invalidateAllOther(radiiRAM_.get());
        invalidate(InvalidationLevel::InvalidOutput);
    }

    
}


void StructureMesh::handlePicking(PickingEvent* p) {
    if (enablePicking_.get()) { 
        if (p->getState() == PickingState::Updated &&
            p->getEvent()->hash() == MouseEvent::chash()) {
            auto me = p->getEventAs<MouseEvent>();
            if ((me->buttonState() & MouseButton::Left) && me->state() != MouseState::Move) {
                size_t currentlyPicked = pickedIndex_.get();
                size_t picked = p->getPickedId();

                // A different atom has been selected, change the
                // colours to mach the selection.
                if (picked != currentlyPicked) {
                    auto& color = colorRAM_->getDataContainer();

                    color[currentlyPicked].w = 1;
                    color[picked].w = 0.5;
                    pickedIndex_.set(picked);

                    colorRAM_->getOwner()->invalidateAllOther(colorRAM_.get());
                    invalidate(InvalidationLevel::InvalidOutput);
                }

                p->markAsUsed();
            }
        }
    }

}

} // namespace

