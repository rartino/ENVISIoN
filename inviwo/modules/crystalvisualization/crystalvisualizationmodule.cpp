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

#include <modules/crystalvisualization/crystalvisualizationmodule.h>
#include <modules/crystalvisualization/processors/structuremesh.h>
#include <modules/crystalvisualization/processors/coordinatereader.h>
#include <modules/crystalvisualization/properties/intvectorproperty.h>

namespace inviwo {

crystalvisualizationModule::crystalvisualizationModule(InviwoApplication* app) : InviwoModule(app, "crystalvisualization") {   
    registerProcessor<StructureMesh>();
    registerProcessor<CoordinateReader>();
    // Add a directory to the search path of the Shadermanager
    // ShaderManager::getPtr()->addShaderSearchPath(getPath(ModulePath::GLSL));

    // Register objects that can be shared with the rest of inviwo here:
    
    // Processors
    // registerProcessor<crystalvisualizationProcessor>();
    
    // Properties
    registerProperty<IntVectorProperty>();
    
    // Readers and writes
    // registerDataReader(util::make_unique<crystalvisualizationReader>());
    // registerDataWriter(util::make_unique<crystalvisualizationWriter>());
    
    // Data converters
    // registerRepresentationConverter(util::make_unique<crystalvisualizationDisk2RAMConverter>());

    // Ports
    // registerPort<crystalvisualizationOutport>("crystalvisualizationOutport");
    // registerPort<crystalvisualizationInport>("crystalvisualizationInport");

    // PropertyWidgets
    // registerPropertyWidget<crystalvisualizationPropertyWidget, crystalvisualizationProperty>("Default");
    
    // Dialogs
    // registerDialog<crystalvisualizationDialog>(crystalvisualizationOutport);
    
    // Other varius things
    // registerCapabilities(util::make_unique<crystalvisualizationCapabilities>());
    // registerSettings(util::make_unique<crystalvisualizationSettings>());
    // registerMetaData(util::make_unique<crystalvisualizationMetaData>());   
    // registerPortInspector("crystalvisualizationOutport", "path/workspace.inv");
    // registerProcessorWidget(std::string processorClassName, std::unique_ptr<ProcessorWidget> processorWidget);
    // registerDrawer(util::make_unique_ptr<crystalvisualizationDrawer>());  
}

} // namespace
