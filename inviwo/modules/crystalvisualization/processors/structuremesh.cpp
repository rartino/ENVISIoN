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

#include <inviwo/core/interaction/events/pickingevent.h>
#include <inviwo/core/interaction/events/mouseevent.h>
#include <inviwo/core/datastructures/buffer/bufferramprecision.h>
#include <inviwo/core/datastructures/buffer/buffer.h>

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
    , fullMesh_("fullMesh", "Full mesh", false)
    , enablePicking_("enablePicking", "Enable Picking", false)
    , spherePicking_(this, 0, [&](PickingEvent* p) { handlePicking(p); })
    , inds_("inds", "Picked atoms") {
    addPort(structure_);
    addPort(mesh_);
    addProperty(scalingFactor_);
    addProperty(fullMesh_);
    addProperty(enablePicking_);
    addProperty(inds_);

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
		auto center = scalingFactor_.get()*strucs->at(j);
		BasicMesh::sphere(center, radii_[ind]->get(), colors_[ind]->get(), mesh);
	    }
	    ++ind;
	}
    } else {

        const bool changed = std::any_of(radii_.begin(), radii_.end(), 
                                         [](const std::unique_ptr<FloatProperty>& property){
                                            return property->isModified();
                                            }) ||
                              std::any_of(colors_.begin(), colors_.end(), 
                                         [](const std::unique_ptr<FloatVec4Property>& property){
                                            return property->isModified();
                                            }) ||
                              enablePicking_.isModified();

        if (structure_.isChanged() || scalingFactor_.isModified() || changed) {
        
            int numSpheres = 0;
            for (const auto &strucs : structure_)
                numSpheres += strucs->size();

            auto mesh = std::make_shared<Mesh>(DrawType::Points, ConnectivityType::None);

            auto vertexRAM = std::make_shared<BufferRAMPrecision<vec3>>(numSpheres);
            auto colorRAM = std::make_shared<BufferRAMPrecision<vec4>>(numSpheres);
            auto radiiRAM = std::make_shared<BufferRAMPrecision<float>>(numSpheres);

            colorBuffer_ = colorRAM;

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
                for (long long j = 0; j < static_cast<long long>(strucs->size()); ++j) {
                    auto center = strucs->at(j);
                    vertices[sphereInd] = scalingFactor_.get()*center;
                    colors[sphereInd] = colors_[portInd]->get();
                    radii[sphereInd] = radii_[portInd]->get();
                    ++sphereInd;
                }
                ++portInd;
            }
            if (enablePicking_.get()) {
                //Set alpha-layer of picked atoms
                if(!inds_.get().empty()) {
                    for (const auto &ind : inds_.get()) {
                        colors[ind].w = 0.5;
                    }
                }
                auto pickingRAM = std::make_shared<BufferRAMPrecision<uint32_t>>(numSpheres);
                auto& data = pickingRAM->getDataContainer();
                // fill in picking IDs
                std::iota(data.begin(), data.end(), static_cast<uint32_t>(spherePicking_.getPickingId(0)));

                mesh->addBuffer(Mesh::BufferInfo(BufferType::NumberOfBufferTypes, 4),
                                std::make_shared<Buffer<uint32_t>>(pickingRAM));
            }
        }

    }
}


void StructureMesh::handlePicking(PickingEvent* p) {
    if (enablePicking_.get()) { 
        if (p->getState() == PickingState::Updated &&
            p->getEvent()->hash() == MouseEvent::chash()) {
            auto me = p->getEventAs<MouseEvent>();
            if ((me->buttonState() & MouseButton::Left) && me->state() != MouseState::Move) {
                auto& color = colorBuffer_->getDataContainer();
                std::vector<int> temp = inds_.get();
                auto picked = p->getPickedId();

                if( std::none_of(temp.begin(), temp.end(), [&](unsigned int i){return i == picked;}) ) {
                    temp.push_back(picked);
                    color[picked].w = 0.5;
                } else {
                    temp.erase(std::remove(temp.begin(), temp.end(), picked), temp.end());
                    color[picked].w = 1;
                }
                inds_.set(temp);

                colorBuffer_->getOwner()->invalidateAllOther(colorBuffer_.get());
                invalidate(InvalidationLevel::InvalidOutput);
                p->markAsUsed();
            }
        }
    }

}

} // namespace

