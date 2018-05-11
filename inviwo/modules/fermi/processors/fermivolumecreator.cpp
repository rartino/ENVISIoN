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

#include <modules/fermi/processors/fermivolumecreator.h>
#include <modules/fermi/datastructures/kdtree.h>

#include <inviwo/core/util/logcentral.h>
#include <inviwo/core/datastructures/volume/volume.h>
#include <modules/hdf5/datastructures/hdf5handle.h>
#include <modules/hdf5/datastructures/hdf5path.h>
#include <modules/hdf5/datastructures/hdf5metadata.h>

namespace inviwo {

static constexpr const char* KPOINT_PATH = "/FermiSurface/KPoints";

// The Class Identifier has to be globally unique. Use a reverse DNS naming scheme
const ProcessorInfo fermivolumecreator::processorInfo_{
    "org.inviwo.fermivolumecreator",      // Class identifier
    "fermivolumecreator",                // Display name
    "Fermi",              // Category
    CodeState::Experimental,  // Code state
    Tags::None,               // Tags
};
const ProcessorInfo fermivolumecreator::getProcessorInfo() const {
    return processorInfo_;
}

fermivolumecreator::fermivolumecreator()
    : Processor()
    , energy_selector_("energySelector", "Energy Selector")
    , iso_value_("isoValue", "ISO Value")
    , volume_size_(2)
    , inport_("inport")
    , outport_("outport") {

    addProperty(energy_selector_);
    addProperty(iso_value_);

    addPort(inport_);
    addPort(outport_);

    energy_selector_.setMinValue(0);
    energy_selector_.setMaxValue(0);
}

void fermivolumecreator::process() {
    std::shared_ptr<const hdf5::Handle> data = inport_.getData();

    const H5::Group& group = data->getGroup().openGroup(KPOINT_PATH);

    std::vector<hdf5::MetaData> metadataList = hdf5::util::getMetaData(group);

    std::vector<hdf5::MetaData> kpoints;
    for (const hdf5::MetaData& metadata : metadataList)
    {
        // Each individual K-Point is represented by its own group.
        if (metadata.type_ == hdf5::MetaData::HDFType::Group &&
            std::string(metadata.path_) != "/")
        {
            kpoints.push_back(metadata);
        }
    }

    float fermiEnergy = readFermiEnergy(data->getGroup().openGroup("/FermiSurface"),
                                        "/FermiSurface/FermiEnergy");
    LogInfo(std::to_string(fermiEnergy));

    vec3 basis[3];
    for (uint8_t i = 0; i < 3; i++) {
        basis[i] = readVec3(data->getGroup().openGroup("/FermiSurface/ReciprocalLatticeVectors"),
                            "/FermiSurface/ReciprocalLatticeVectors/" + std::to_string(i));
    }

    std::vector<KPoint> points;
    for (const hdf5::MetaData& kpoint : kpoints)
    {
        try
        {
            std::string path = std::string(KPOINT_PATH) +
                               std::string(kpoint.path_);

            KPoint point = { readVec3(group, path + "/Coordinates"),
                             readKPointEnergy(group, path + "/Energy") };


            double x_o = point.coordinates.x;
            double y_o = point.coordinates.y;
            double z_o = point.coordinates.z;

            point.coordinates.x = x_o * basis[0][0] +
                                  y_o * basis[0][1] +
                                  z_o * basis[0][2];

            point.coordinates.y = x_o * basis[1][0] +
                                  y_o * basis[1][1] +
                                  z_o * basis[1][2];

            point.coordinates.z = x_o * basis[2][0] +
                                  y_o * basis[2][1] +
                                  z_o * basis[2][2];

            points.push_back(point);
        }
        catch (const std::exception& e)
        {
            LogInfo("Error opening K-Point: " + std::string(e.what()));
        }
    }

    double maxX, maxY, maxZ;
    {
        auto itrX = std::max_element(points.begin(), points.end(), [](KPoint v1, KPoint v2)
        {
            return v1.coordinates.x < v2.coordinates.x;
        });
        maxX = itrX->coordinates.x;

        auto itrY = std::max_element(points.begin(), points.end(), [](KPoint v1, KPoint v2)
        {
            return v1.coordinates.y < v2.coordinates.y;
        });
        maxY = itrY->coordinates.y;

        auto itrZ = std::max_element(points.begin(), points.end(), [](KPoint v1, KPoint v2)
        {
            return v1.coordinates.z < v2.coordinates.z;
        });
        maxZ = itrZ->coordinates.z;
    }

    double minX, minY, minZ;
    {
        auto itrX = std::min_element(points.begin(), points.end(), [](KPoint v1, KPoint v2)
        {
            return v1.coordinates.x < v2.coordinates.x;
        });
        minX = itrX->coordinates.x;

        auto itrY = std::min_element(points.begin(), points.end(), [](KPoint v1, KPoint v2)
        {
            return v1.coordinates.y < v2.coordinates.y;
        });
        minY = itrY->coordinates.y;

        auto itrZ = std::min_element(points.begin(), points.end(), [](KPoint v1, KPoint v2)
        {
            return v1.coordinates.z < v2.coordinates.z;
        });
        minZ = itrZ->coordinates.z;
    }

    volume_size_ = std::floor(std::cbrt(kpoints.size()));

    energy_selector_.setMinValue(0);
    energy_selector_.setMaxValue(points[0].energies.size() - 1);
    size_t energy = energy_selector_.get();

    float energy_max = points[0].energies[energy];
    float energy_min = points[0].energies[energy];
    for (KPoint& point : points) {
        if (point.energies[energy] > energy_max)
            energy_max = point.energies[energy];
        else if (point.energies[energy] < energy_min)
            energy_min = point.energies[energy];
    }

    std::shared_ptr<Volume> volume(nullptr);
    /*
    if (energy_max < fermiEnergy || energy_min > fermiEnergy) {
         volume = std::make_shared<Volume>(size3_t(2, 2, 2),
                                           DataFloat32::get());
         volume->dataMap_.dataRange = dvec2(0, 1);
         volume->dataMap_.valueRange = dvec2(0, 1);
        iso_value_.setMaxValue(1);
        iso_value_.setMinValue(0);
        iso_value_.set(1);
    } else */ {
        volume = std::make_shared<Volume>(size3_t(volume_size_,
                                                  volume_size_,
                                                  volume_size_),
                                          DataFloat32::get());

        volume->dataMap_.dataRange = dvec2(energy_min, energy_max);
        volume->dataMap_.valueRange = dvec2(energy_min, energy_max);

        iso_value_.setMaxValue(energy_max);
        iso_value_.setMinValue(energy_min);
        iso_value_.set(fermiEnergy);

        VolumeRAMPrecision<float> *ram =
            static_cast<VolumeRAMPrecision<float> *>(volume->getEditableRepresentation<VolumeRAM>());

        for (const KPoint& point : points) {
            double x = std::round((point.coordinates.x - minX) / (maxX - minX) * (volume_size_ - 1));
            double y = std::round((point.coordinates.y - minY) / (maxY - minY) * (volume_size_ - 1));
            double z = std::round((point.coordinates.z - minZ) / (maxZ - minZ) * (volume_size_ - 1));


            ram->setFromDouble(size3_t(x, y, z), point.energies[energy]);
        }
    }



    /*
    volume->setBasis(mat3(-0.22f, 0.22f, 0.22f,
                          0.22f, -0.22f, 0.22f,
                          0.22f, 0.22f, -0.22f));
                          */

    outport_.setData(volume);
}

vec3 fermivolumecreator::readVec3(const H5::Group& group, const std::string& path) const {
    H5::DataSet dataSet = group.openDataSet(path);
    H5::DataSpace dataSpace = dataSet.getSpace();

    hsize_t count[] = { 3 };
    hsize_t start[] = { 0 };
    dataSpace.selectHyperslab(H5S_SELECT_SET, count, start);

    hsize_t dim[] = { 3 };
    H5::DataSpace memSpace(1, dim);

    float output[3];
    dataSet.read(output, H5::PredType::NATIVE_FLOAT, memSpace, dataSpace);

    return dvec3(output[0], output[1], output[2]);
}

float fermivolumecreator::readFermiEnergy(const H5::Group& group, const std::string& path) const {
    H5::DataSet dataSet = group.openDataSet(path);
    H5::DataSpace dataSpace = dataSet.getSpace();

    dataSpace.selectAll();

    hsize_t dim[] = { 1 };
    H5::DataSpace memSpace(1, dim);

    float output;
    dataSet.read(&output, H5::PredType::NATIVE_FLOAT, memSpace, dataSpace);

    return output;
}

std::vector<float> fermivolumecreator::readKPointEnergy(const H5::Group& group, const std::string& path) const {
    std::vector<float> energies;

    H5::DataSet dataSet = group.openDataSet(path);
    H5::DataSpace dataSpace = dataSet.getSpace();

    int ndims = dataSpace.getSimpleExtentNdims();

    if (ndims > 1) {
        LogError("The KPoint energies are not a simple list!");
        return std::vector<float>();
    }

    std::shared_ptr<hsize_t> dims(new hsize_t[ndims], std::default_delete<hsize_t[]>());
    dataSpace.getSimpleExtentDims(dims.get());

    hsize_t length = dims.get()[0];

    hsize_t count[] = { length };
    hsize_t start[] = { 0 };
    dataSpace.selectHyperslab(H5S_SELECT_SET, count, start);

    hsize_t dim[] = { length };
    H5::DataSpace memSpace(1, dim);

    energies.resize(length);
    dataSet.read(energies.data(), H5::PredType::NATIVE_FLOAT, memSpace, dataSpace);

    return energies;
}

} // namespace

