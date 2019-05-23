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
