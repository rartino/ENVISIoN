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

#ifndef IVW_STRINGCOMPARENATURAL_H
#define IVW_STRINGCOMPARENATURAL_H

#include <modules/graph2d/util/stringcomparenatural.h>

#include <inviwo/core/common/inviwo.h>

namespace inviwo {

bool StringCompareNatural(const std::string string1, const std::string string2) {
    if (string1.empty() || (std::isdigit(string1[0]) && !std::isdigit(string2[0])))
        return true;
    if (string2.empty() || (!std::isdigit(string1[0]) && std::isdigit(string2[0])))
        return false;

    if (!std::isdigit(string1[0]) && !std::isdigit(string2[0])) {
        int upper1 = std::toupper(string1[0]);
        int upper2 = std::toupper(string2[0]);
        if (upper1 == upper2)
            return StringCompareNatural(string1.substr(1), string2.substr(1));
        return (upper1 < upper2);
    }

    std::istringstream stream1(string1);
    std::istringstream stream2(string2);

    unsigned long long1;
    unsigned long long2;
    stream1 >> long1;
    stream2 >> long2;
    if (long1 != long2)
        return long1 < long2;

    std::string stringResidual1;
    std::string stringResidual2;
    std::getline(stream1, stringResidual1);
    std::getline(stream2, stringResidual2);
    return StringCompareNatural(stringResidual1, stringResidual2);
}

} // namespace

#endif // IVW_STRINGCOMPARENATURAL_H
