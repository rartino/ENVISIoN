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

    std::vector<dvec3> points;
    for (const hdf5::MetaData& kpoint : kpoints)
    {
        try
        {
            std::string path = std::string(KPOINT_PATH) +
                               std::string(kpoint.path_) +
                               "/Coordinates";
            H5::DataSet dataSet = group.openDataSet(path);
            H5::DataSpace dataSpace = dataSet.getSpace();

            hsize_t count[] = { 3 };
            hsize_t start[] = { 0 };
            dataSpace.selectHyperslab(H5S_SELECT_SET, count, start);

            hsize_t dim[] = { 3 };
            H5::DataSpace memSpace(1, dim);

            float data_out[3];
            dataSet.read(data_out, H5::PredType::NATIVE_FLOAT, memSpace, dataSpace);

            /*
            double x = -1 * data_out[0] + data_out[1] + data_out[2];
            double y = data_out[0] - data_out[1] + data_out[2];
            double z = data_out[0] + data_out[1] - data_out[2];

            points.push_back(dvec3(x, y, z));
            */
            points.push_back(dvec3(data_out[0], data_out[1], data_out[2]));
        }
        catch (const std::exception& e)
        {
            LogInfo("Error opening K-Point: " + std::string(e.what()));
        }
    }

    double maxX, maxY, maxZ;
    {
        auto itrX = std::max_element(points.begin(), points.end(), [](dvec3 v1, dvec3 v2)
        {
            return v1.x < v2.x;
        });
        maxX = itrX->x;

        auto itrY = std::max_element(points.begin(), points.end(), [](dvec3 v1, dvec3 v2)
        {
            return v1.y < v2.y;
        });
        maxY = itrY->y;

        auto itrZ = std::max_element(points.begin(), points.end(), [](dvec3 v1, dvec3 v2)
        {
            return v1.z < v2.z;
        });
        maxZ = itrZ->z;
    }

    double minX, minY, minZ;
    {
        auto itrX = std::min_element(points.begin(), points.end(), [](dvec3 v1, dvec3 v2)
        {
            return v1.x < v2.x;
        });
        minX = itrX->x;

        auto itrY = std::min_element(points.begin(), points.end(), [](dvec3 v1, dvec3 v2)
        {
            return v1.y < v2.y;
        });
        minY = itrY->y;

        auto itrZ = std::min_element(points.begin(), points.end(), [](dvec3 v1, dvec3 v2)
        {
            return v1.z < v2.z;
        });
        minZ = itrZ->z;
    }

    double lengthX = abs(maxX) + abs(minX);
    double lengthY = abs(maxY) + abs(minY);
    double lengthZ = abs(maxZ) + abs(minZ);

    double longestAxis = std::max(lengthX, std::max(lengthY, lengthZ));

    double scaleX = lengthX / longestAxis;
    double scaleY = lengthY / longestAxis;
    double scaleZ = lengthZ / longestAxis;

    std::shared_ptr<Volume> volume = std::make_shared<Volume>(size3_t(ceil(100 * scaleX),
                                                                      ceil(100 * scaleY),
                                                                      ceil(100 * scaleZ)),
                                                              DataFloat32::get());
    VolumeRAMPrecision<float> *ram =
        static_cast<VolumeRAMPrecision<float> *>(volume->getEditableRepresentation<VolumeRAM>());
    float* values = ram->getDataTyped();

    for (const dvec3& coord : points)
    {
        double x = (coord.x - minX) / (maxX - minX);
        double y = (coord.y - minY) / (maxY - minY);
        double z = (coord.z - minZ) / (maxZ - minZ);

        values[int(x * 100 * scaleX) + int(y * 100 * scaleY) + int(z * 100 * scaleZ)] = 1;
    }

    volume->dataMap_.dataRange = dvec2(0, 1);
    volume->dataMap_.valueRange = dvec2(0, 1);

    outport_.setData(volume);
}

} // namespace

