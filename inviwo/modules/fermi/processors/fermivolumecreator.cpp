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

#include <einspline/bspline.h>

namespace inviwo {

static constexpr const char* KPOINT_PATH = "/FermiSurface/KPoints";
static constexpr const char* BASIS_PATH = "/FermiSurface/ReciprocalLatticeVectors";

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
    , interpolation_("interpolation", "Interpolation")
    , iso_value_("isoValue", "ISO Value")
    , volume_size_(2)
    , inport_("inport")
    , outport_("outport") {

    addProperty(energy_selector_);
    addProperty(interpolation_);
    addProperty(iso_value_);

    addPort(inport_);
    addPort(outport_);

    energy_selector_.setMinValue(0);
    energy_selector_.setMaxValue(0);

    interpolation_.setMinValue(1);
    interpolation_.setMaxValue(1000);
    interpolation_.set(1);
}

void fermivolumecreator::process() {
    std::shared_ptr<const hdf5::Handle> data = inport_.getData();

    // Open the path to the KPoints in the HDF5 file.
    const H5::Group& group = data->getGroup().openGroup(KPOINT_PATH);

    // Get a list of items in the KPoints group.
    std::vector<hdf5::MetaData> metadataList = hdf5::util::getMetaData(group);

    // Loop through and pick out all the KPoints from the metadata
    // list.
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

    // Read the basis vectors for the reciprocal space.
    vec3 basis[3];
    for (uint8_t i = 0; i < 3; i++) {
        H5::Group base_group = data->getGroup().openGroup(BASIS_PATH);

        basis[i] = readVec3(base_group, std::string(BASIS_PATH) + "/" +
                            std::to_string(i));
    }

    // Read all k-points from the HDF5 file, convert their coordinates
    // to cartesian coordinates and store them in a list of KPoint
    // objects.
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

    // Find the maximum and minimum values for each coordinate axis.
    // This is used to normalise the coordinates to within the memory
    // space representing the volume.
    double maxX, maxY, maxZ;
    getMaxCoordinates(points, maxX, maxY, maxZ);

    double minX, minY, minZ;
    getMinCoordinates(points, minX, minY, minZ);

    volume_size_ = std::floor(std::cbrt(kpoints.size()));

    energy_selector_.setMinValue(0);
    energy_selector_.setMaxValue(points[0].energies.size() - 1);
    size_t energy = energy_selector_.get();

    // Normalise coordinates.
    for (KPoint& point : points) {
        double x = std::round((point.coordinates.x - minX) /
                              (maxX - minX) * (volume_size_ - 1));
        double y = std::round((point.coordinates.y - minY) /
                              (maxY - minY) * (volume_size_ - 1));
        double z = std::round((point.coordinates.z - minZ) /
                              (maxZ - minZ) * (volume_size_ - 1));

        point.coordinates.x = x;
        point.coordinates.y = y;
        point.coordinates.z = z;
    }

    /* Construct settings for the spline interpolation. The first
     * argument is the starting coordinate of the spline in each
     * dimension, the second argument is the ending coordinate for the
     * spline in each dimension and the list argument is the number of
     * data points along each dimension. The last two zeros are used
     * and set internally by the spline library and the values don't
     * matter. They are simply set to make the compiler shut up.
     *
     * The volume space is coded to always be a cube, so we use the
     * same settings from all the axes.
     */
    Ugrid grid = { 0,
                   static_cast<double>(volume_size_ * interpolation_.get() - 1),
                   static_cast<int>(volume_size_), 0, 0 };
    BCtype_s bc = { NATURAL, NATURAL, 0, 0 };

    float *spline_data = new float[volume_size_ * volume_size_ * volume_size_];
    std::fill(spline_data, spline_data + volume_size_ * volume_size_ *
              volume_size_, 0);

    // Assign all KPoint values to the spline data space for
    // interpolation.
    for (const KPoint& point : points) {
        size_t x = point.coordinates.x;
        size_t y = point.coordinates.y;
        size_t z = point.coordinates.z;
        size_t offset = (x * volume_size_ + y) * volume_size_ + z;

        spline_data[offset] = point.energies[energy];
    }

    UBspline_3d_s *spline = create_UBspline_3d_s(grid, grid, grid,
                                                 bc, bc, bc,
                                                 spline_data);


    // Create an Inviwo volume in memory to be filled with values.
    float energy_max = spline_data[0]; 
    float energy_min = spline_data[0];
    std::shared_ptr<Volume> volume =
        std::make_shared<Volume>(size3_t(volume_size_ * interpolation_.get(),
                                         volume_size_ * interpolation_.get(),
                                         volume_size_ * interpolation_.get()),
                                 DataFloat32::get());


    VolumeRAMPrecision<float> *ram =
        static_cast<VolumeRAMPrecision<float> *>(
                volume->getEditableRepresentation<VolumeRAM>());

    // Loop through every point of the volume in memory and query the
    // spline for a value to assign to each point.
    for (size_t x = 0; x < volume_size_ * interpolation_.get(); x++) {
        for (size_t y = 0; y < volume_size_ * interpolation_.get();  y++) {
            for (size_t z = 0; z < volume_size_ * interpolation_.get(); z++) {
                float value;
                eval_UBspline_3d_s(spline, x, y, z, &value); 
                ram->setFromDouble(size3_t(x, y, z), value);

                if (value > energy_max)
                    energy_max = value;
                else if (value < energy_min)
                    energy_min = value;
            }
        }
    }

    volume->dataMap_.dataRange = dvec2(energy_min, energy_max);
    volume->dataMap_.valueRange = dvec2(energy_min, energy_max);

    iso_value_.setMaxValue(energy_max);
    iso_value_.setMinValue(energy_min);
    iso_value_.set(fermiEnergy);

    destroy_Bspline(spline);
    delete[] spline_data;

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

void fermivolumecreator::getMaxCoordinates(const std::vector<KPoint> &points,
                                           double &maxX, double &maxY,
                                           double &maxZ) const {
    auto itrX = std::max_element(points.begin(), points.end(),
    [](KPoint v1, KPoint v2)
    {
        return v1.coordinates.x < v2.coordinates.x;
    });
    maxX = itrX->coordinates.x;

    auto itrY = std::max_element(points.begin(), points.end(),
    [](KPoint v1, KPoint v2)
    {
        return v1.coordinates.y < v2.coordinates.y;
    });
    maxY = itrY->coordinates.y;

    auto itrZ = std::max_element(points.begin(), points.end(),
    [](KPoint v1, KPoint v2)
    {
        return v1.coordinates.z < v2.coordinates.z;
    });
    maxZ = itrZ->coordinates.z;
}

void fermivolumecreator::getMinCoordinates(const std::vector<KPoint> &points,
                                           double &minX, double &minY,
                                           double &minZ) const {
    auto itrX = std::min_element(points.begin(), points.end(),
    [](KPoint v1, KPoint v2)
    {
        return v1.coordinates.x < v2.coordinates.x;
    });
    minX = itrX->coordinates.x;

    auto itrY = std::min_element(points.begin(), points.end(),
    [](KPoint v1, KPoint v2)
    {
        return v1.coordinates.y < v2.coordinates.y;
    });
    minY = itrY->coordinates.y;

    auto itrZ = std::min_element(points.begin(), points.end(),
    [](KPoint v1, KPoint v2)
    {
        return v1.coordinates.z < v2.coordinates.z;
    });
    minZ = itrZ->coordinates.z;
}

} // namespace

