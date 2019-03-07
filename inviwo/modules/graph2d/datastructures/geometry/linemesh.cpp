/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2017-2019 Inviwo Foundation, Abdullatif Ismail
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

#include "linemesh.h"

namespace inviwo {

    std::shared_ptr<BasicMesh> lineMesh(const vec3 &start, const vec3 &stop, const vec3 &normal,
                                         const vec4 &color /*= vec4(1.0f, 0.0f, 0.0f, 1.0f)*/,
                                         const float &width /*= 1.0f*/,
                                         const ivec2 &inres /*= ivec2(1)*/) {
        auto mesh = std::make_shared<BasicMesh>();
        mesh->setModelMatrix(mat4(1.f));
        auto inds = mesh->addIndexBuffer(DrawType::Triangles, ConnectivityType::None);

        vec3 direction = stop - start;
        vec3 up = glm::cross(glm::normalize(direction), normal);

        vec3 startCornerPoint = start - 0.5f * width * up;
        ivec2 res = inres + ivec2(1);

        for (int j = 0; j < res.y; j++) {
            for (int i = 0; i < res.x; i++) {
                mesh->addVertex(startCornerPoint +
                                static_cast<float>(i) / static_cast<float>(inres.x) * direction +
                                static_cast<float>(j) / static_cast<float>(inres.y) * width * up,
                                normal, vec3(static_cast<float>(i) / static_cast<float>(inres.x),
                                             static_cast<float>(j) / static_cast<float>(inres.y), 0.0f),
                                color);

                if (i != inres.x && j != inres.y) {
                    inds->add(i + res.x * j);
                    inds->add(i + 1 + res.x * j);
                    inds->add(i + res.x * (j + 1));
                    inds->add(i + 1 + res.x * j);
                    inds->add(i + 1 + res.x * (j + 1));
                    inds->add(i + res.x * (j + 1));
                }
            }
        }
        return mesh;
    }

} // namespace inviwo