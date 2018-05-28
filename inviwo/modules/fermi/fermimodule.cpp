/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2017-2018 Inviwo Foundation, Andreas Kempe
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
/*
 *   Alterations to this file by Andreas Kempe
 *
 *   To the extent possible under law, the person who associated CC0
 *   with the alterations to this file has waived all copyright and
 *   related or neighboring rights to the alterations made to this file.
 *
 *   You should have received a copy of the CC0 legalcode along with
 *   this work.  If not, see
 *   <http://creativecommons.org/publicdomain/zero/1.0/>.
 */

#include <modules/fermi/fermimodule.h>
#include <modules/fermi/processors/fermivolumecreator.h>

namespace inviwo {

fermiModule::fermiModule(InviwoApplication* app) : InviwoModule(app, "fermi") {
    registerProcessor<fermivolumecreator>();
    // Add a directory to the search path of the Shadermanager
    // ShaderManager::getPtr()->addShaderSearchPath(getPath(ModulePath::GLSL));

    // Register objects that can be shared with the rest of inviwo here:

    // Processors
    // registerProcessor<fermiProcessor>();

    // Properties
    // registerProperty<fermiProperty>();

    // Readers and writes
    // registerDataReader(util::make_unique<fermiReader>());
    // registerDataWriter(util::make_unique<fermiWriter>());

    // Data converters
    // registerRepresentationConverter(util::make_unique<fermiDisk2RAMConverter>());

    // Ports
    // registerPort<fermiOutport>("fermiOutport");
    // registerPort<fermiInport>("fermiInport");

    // PropertyWidgets
    // registerPropertyWidget<fermiPropertyWidget, fermiProperty>("Default");

    // Dialogs
    // registerDialog<fermiDialog>(fermiOutport);

    // Other varius things
    // registerCapabilities(util::make_unique<fermiCapabilities>());
    // registerSettings(util::make_unique<fermiSettings>());
    // registerMetaData(util::make_unique<fermiMetaData>());
    // registerPortInspector("fermiOutport", "path/workspace.inv");
    // registerProcessorWidget(std::string processorClassName, std::unique_ptr<ProcessorWidget> processorWidget);
    // registerDrawer(util::make_unique_ptr<fermiDrawer>());
}

} // namespace
