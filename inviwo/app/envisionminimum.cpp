/************************************************************************
 *   This file was created 2019 by Abdullatif Ismail
 *
 *   To the extent possible under law, the person who associated CC0
 *   with the alterations to this file has waived all copyright and
 *   related or neighboring rights to the alterations made to this file.
 *
 *   You should have received a copy of the CC0 legalcode along with
 *   this work.  If not, see
 *   <http://creativecommons.org/publicdomain/zero/1.0/>.
 ************************************************************************/

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
    envisionApp.setWindowIcon(QIcon(":/inviwo/inviwo_dark.ico"));
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
}
