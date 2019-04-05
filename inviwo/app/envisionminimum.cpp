/*********************************************************************************
 *
 * Inviwo - Interactive Visualization Workshop
 *
 * Copyright (c) 2014-2019 Inviwo Foundation, Abdullatif Ismail
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

#include <inviwo/qt/editor/inviwomainwindow.h>
#include <inviwo/qt/applicationbase/inviwoapplicationqt.h>
#include <inviwo/core/common/defaulttohighperformancegpu.h>
#include <inviwo/core/util/commandlineparser.h>
#include <inviwo/core/util/filesystem.h>
#include <inviwo/core/util/logcentral.h>
#include <inviwo/core/util/logerrorcounter.h>
#include <inviwo/core/util/raiiutils.h>
#include <inviwo/core/network/processornetwork.h>
#include <inviwo/core/util/ostreamjoiner.h>
#include <inviwo/core/util/filelogger.h>
#include <modules/python3/python3modulesharedlibrary.h>
#include <modules/python3/python3module.h>
#include <modules/python3/pythoninterpreter.h>
#include <inviwo/core/moduleregistration.h>

#include <sstream>
#include <algorithm>

#include <warn/push>
#include <warn/ignore/all>
#include <QFile>
#include <QMessageBox>
#include <warn/pop>

using namespace inviwo;

int main(int argc, char** argv) {
    inviwo::LogCentral logger;
    inviwo::LogCentral::init(&logger);
    auto logCounter = std::make_shared<inviwo::LogErrorCounter>();
    logger.registerLogger(logCounter);

    inviwo::InviwoApplicationQt envisionApp(argc, argv, "ENVISIoN");
    envisionApp.setWindowIcon(QIcon(":/inviwo/liu-black.png"));
    envisionApp.setAttribute(Qt::AA_NativeWindows);
    QFile styleSheetFile(":/stylesheets/inviwo.qss");
    styleSheetFile.open(QFile::ReadOnly);
    QString styleSheet = QString::fromUtf8(styleSheetFile.readAll());
    envisionApp.setStyleSheet(styleSheet);
    styleSheetFile.close();

    auto& clp = envisionApp.getCommandLineParser();

    envisionApp.registerModules(inviwo::getModuleList());
    envisionApp.processEvents();

    // Do this after registerModules if some arguments were added
    clp.parse(inviwo::CommandLineParser::Mode::Normal);
    envisionApp.processEvents();

    envisionApp.setProgressCallback(std::function<void(std::string)>{});

    envisionApp.processEvents();
    clp.processCallbacks();  // run any command line callbacks from modules.
    envisionApp.processEvents();

    auto pyInter{envisionApp.getModuleByType<Python3Module>()->getPythonInterpreter()};
    pyInter->runString("import ENVISIoNimport");

    return 0;
    try {
        return envisionApp.exec();
    } catch (const std::exception &e) {
        std::cout << e.what() << std::endl;
    }
}