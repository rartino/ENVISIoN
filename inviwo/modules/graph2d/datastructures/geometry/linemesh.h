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
/*
 * This file only contains one function called linemesh().
 * The function creates a BasicMesh and forms it into a line
 * using the values given as inparm.
 * */

#ifndef IVW_LINEMESH_H
#define IVW_LINEMESH_H

#include <inviwo/core/datastructures/geometry/basicmesh.h>

namespace inviwo {

    std::shared_ptr<BasicMesh> lineMesh(const vec3& start, const vec3& stop, const vec3& normal,
                                        const vec4& color /*= vec4(1.0f, 0.0f, 0.0f, 1.0f)*/,
                                        const float& width /*= 1.0f*/,
                                        const ivec2& inres /*= ivec2(1)*/);
} // namespace
#endif
