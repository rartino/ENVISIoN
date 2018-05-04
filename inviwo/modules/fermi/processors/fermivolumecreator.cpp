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
static constexpr unsigned int VOLUME_WIDTH = 100;
static constexpr unsigned int VOLUME_HEIGHT = 100;
static constexpr unsigned int VOLUME_DEPTH = 100;

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
    , energy_selector_("energy_selector", "Energy Selector")
    , inport_("inport")
    , outport_("outport") {

    addProperty(energy_selector_);

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

    float fermiEnergy = readFermiEnergy(data->getGroup().openGroup("/FermiSurface"), "/FermiSurface/FermiEnergy");
    LogInfo(std::to_string(fermiEnergy));

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

    for (KPoint& point : points) {
        double x = ((point.coordinates.x - minX) / (maxX - minX)) * VOLUME_WIDTH;
        double y = ((point.coordinates.y - minY) / (maxY - minY)) * VOLUME_HEIGHT;
        double z = ((point.coordinates.z - minZ) / (maxZ - minZ)) * VOLUME_DEPTH;

        point.coordinates = vec3(x, y, z);
    }
    float energy_max = points[0].energies[0];
    float energy_min = points[0].energies[0];

    energy_selector_.setMinValue(0);
    energy_selector_.setMaxValue(points[0].energies.size() - 1);


    std::shared_ptr<Volume> volume = std::make_shared<Volume>(size3_t(VOLUME_WIDTH,
                                                                      VOLUME_HEIGHT,
                                                                      VOLUME_DEPTH),
                                                              DataFloat32::get());
    VolumeRAMPrecision<float> *ram =
        static_cast<VolumeRAMPrecision<float> *>(volume->getEditableRepresentation<VolumeRAM>());
    float* values = ram->getDataTyped();

    size_t energy = energy_selector_.get();
    KDTree<std::vector<KPoint>, 3> kdlist(points);

    std::shared_ptr<InterpolationPoint> interpolation_map(new InterpolationPoint[VOLUME_HEIGHT *
                                                                                 VOLUME_WIDTH *
                                                                                 VOLUME_DEPTH],
                                                          std::default_delete<InterpolationPoint[]>());


    for (const KPoint& point : points) {
        KPoint neighbour = kdlist.findNN(point);

        float r = 0;
        for (int i = 0; i < 3; i++) {
            r += std::pow(neighbour[i] - point[i], 2);
        }
        r = std::sqrt(r);

        float x_min = std::max(0.f, point[0] - r);
        float x_max = std::min((float) VOLUME_WIDTH, point[0] + r);
        float y_min = std::max(0.f, point[1] - r);
        float y_max = std::min((float) VOLUME_HEIGHT, point[1] + r);
        float z_min = std::max(0.f, point[2] - r);
        float z_max = std::min((float) VOLUME_DEPTH, point[2] + r);

        r *= r;

        for (unsigned int x = x_min; x < x_max; x++) {
            for (unsigned int y = y_min; y < y_max; y++) {
                for (unsigned int z = z_min; z < z_max; z++) {
                    float d = std::pow(x - point[0], 2) +
                              std::pow(y - point[1], 2) +
                              std::pow(z - point[2], 2);
                    if (d <= r) {
                        InterpolationPoint& p =
                            interpolation_map.get()[x + VOLUME_HEIGHT * ( y + VOLUME_DEPTH * z)];
                        p.value = point.energies[energy];
                        p.count += 1;
                    }
                }
            }
        }

        if (point.energies[energy] > energy_max)
            energy_max = point.energies[energy];
        else if (point.energies[energy] < energy_min)
            energy_min = point.energies[energy];
    }
    volume->dataMap_.dataRange = dvec2(energy_min, energy_max);
    volume->dataMap_.valueRange = dvec2(energy_min, energy_max);

    for (unsigned int x = 0; x < VOLUME_WIDTH; x++) {
        for (unsigned int y = 0; y < VOLUME_HEIGHT; y++) {
            for (unsigned int z = 0; z < VOLUME_DEPTH; z++) {
                const InterpolationPoint& p =
                    interpolation_map.get()[x + VOLUME_HEIGHT * ( y + VOLUME_DEPTH * z)];
                float pointEnergy = 0;
                if (p.count != 0) {
                   pointEnergy = p.value / (float) p.count;
                }

                if (std::abs(fermiEnergy - pointEnergy) < 0.01) {
                    values[x + VOLUME_HEIGHT * ( y + VOLUME_DEPTH * z)] = pointEnergy;
                }
            }
        }
    }

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

