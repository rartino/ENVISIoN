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

#ifndef IVW_FERMIVOLUMECREATOR_H
#define IVW_FERMIVOLUMECREATOR_H

#include <modules/fermi/fermimoduledefine.h>

#include <inviwo/core/common/inviwo.h>
#include <inviwo/core/datastructures/volume/volume.h>
#include <inviwo/core/ports/imageport.h>
#include <inviwo/core/ports/volumeport.h>
#include <inviwo/core/processors/processor.h>
#include <inviwo/core/properties/ordinalproperty.h>
#include <modules/hdf5/ports/hdf5port.h>

namespace inviwo {

struct KPoint {
    vec3 coordinates;
    std::vector<float> energies;

    float operator[](size_t idx) const {
        return coordinates[idx];
    }
};

/** \docpage{org.inviwo.fermivolumecreator, fermivolumecreator}
 * ![](org.inviwo.fermivolumecreator.png?classIdentifier=org.inviwo.fermivolumecreator)
 * Explanation of how to use the processor.
 *
 * ### Inports
 *   * __inport__ takes a HDF5 source with fermi data created by the
 *   ENVISIoN fermi surface parser.
 *
 * ### Outports
 *   * __outport__ outputs an Inviwo volume containing points in the
 *   reciprocal space.
 *
 * ### Properties
 *   * __energy_selector__ chooses which energy band should be mapped
 *   to the output volume from the parsed fermi data.
 *   * __interpolation__ decides how many times the volume should be
 *   expanded and interpolated, ex. a 20x20x20 volume with interpolation
 *   set to 4 would result in a 80x80x80 volume.
 *   * __iso_value__ is set by the processor to the fermi energy as
 *   recorded in the VASP data. This to allow for easy surface
 *   extraction via linked properties.
 */


/**
 * \class fermivolumecreator
 * \brief Processor creating volumes from fermi data.
 * This processor takes data from the ENVISIoN fermi parser and
 * converts it to an Inviwo volume. This way, other processors for
 * visualisation can be applied to the data.
 */
class IVW_MODULE_FERMI_API fermivolumecreator : public Processor {
public:
    fermivolumecreator();
    virtual ~fermivolumecreator() = default;

    virtual void process() override;

    virtual const ProcessorInfo getProcessorInfo() const override;
    static const ProcessorInfo processorInfo_;

    IntSizeTProperty energy_selector_;
    IntSizeTProperty interpolation_;
    FloatProperty iso_value_;

private:
    vec3 readVec3(const H5::Group& group, const std::string& path) const;
    float readFermiEnergy(const H5::Group& group, const std::string& path) const;
    std::vector<float> readKPointEnergy(const H5::Group& group, const std::string& path) const;

    void getMaxCoordinates(const std::vector<KPoint> &points,
                           double &maxX, double &maxY, double &maxZ) const;
    void getMinCoordinates(const std::vector<KPoint> &points,
                           double &minX, double &minY, double &minZ) const;

    size_t volume_size_;

    hdf5::Inport inport_;
    VolumeOutport outport_;
};

} // namespace

#endif // IVW_FERMIVOLUMECREATOR_H

