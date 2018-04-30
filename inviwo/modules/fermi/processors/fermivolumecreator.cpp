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

#include <inviwo/core/util/logcentral.h>
#include <inviwo/core/datastructures/volume/volume.h>
#include <modules/hdf5/datastructures/hdf5handle.h>
#include <modules/hdf5/datastructures/hdf5path.h>
#include <modules/hdf5/datastructures/hdf5metadata.h>

namespace inviwo {

static constexpr const char* KPOINT_PATH = "/FermiSurface/KPoints";
static constexpr int VOLUME_WIDTH = 100;
static constexpr int VOLUME_HEIGHT = 100;
static constexpr int VOLUME_DEPTH = 100;

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
    , inport_("inport")
    , outport_("outport") {

    addPort(inport_);
    addPort(outport_);
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

    std::vector<KPoint> points;
    for (const hdf5::MetaData& kpoint : kpoints)
    {
        try
        {
            std::string path = std::string(KPOINT_PATH) +
                               std::string(kpoint.path_);

            KPoint point = { readKPointCoordinates(group, path + "/Coordinates"),
                             readKPointEnergy(group, path + "/Energy") };
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

    std::shared_ptr<Volume> volume = std::make_shared<Volume>(size3_t(VOLUME_WIDTH,
                                                                      VOLUME_HEIGHT,
                                                                      VOLUME_DEPTH),
                                                              DataFloat32::get());
    VolumeRAMPrecision<float> *ram =
        static_cast<VolumeRAMPrecision<float> *>(volume->getEditableRepresentation<VolumeRAM>());
    float* values = ram->getDataTyped();

    for (const KPoint& point : points)
    {
        double x = ((point.coordinates.x - minX) / (maxX - minX)) * VOLUME_WIDTH;
        double y = ((point.coordinates.y - minY) / (maxY - minY)) * VOLUME_HEIGHT;
        double z = ((point.coordinates.z - minZ) / (maxZ - minZ)) * VOLUME_DEPTH;

        values[int(x) + int(VOLUME_HEIGHT * (y + VOLUME_DEPTH * z))] = 1;
    }

    volume->dataMap_.dataRange = dvec2(0, 1);
    volume->dataMap_.valueRange = dvec2(0, 1);
    /*
    volume->setBasis(mat3(-0.22f, 0.22f, 0.22f,
                          0.22f, -0.22f, 0.22f,
                          0.22f, 0.22f, -0.22f));
                          */

    outport_.setData(volume);
}

vec3 fermivolumecreator::readKPointCoordinates(const H5::Group& group, const std::string& path) const {
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

