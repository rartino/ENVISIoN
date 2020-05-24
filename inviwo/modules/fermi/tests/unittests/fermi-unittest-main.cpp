#ifdef _MSC_VER
#pragma comment(linker, "/SUBSYSTEM:CONSOLE")
#endif

#include <inviwo/core/common/inviwo.h>
#include <inviwo/core/common/inviwoapplication.h>
#include <inviwo/core/util/logcentral.h>
#include <inviwo/core/util/consolelogger.h>
#include <inviwo/core/common/coremodulesharedlibrary.h>
#include <modules/python3/python3modulesharedlibrary.h>
#include <modules/fermi/fermimodulesharedlibrary.h>

#include <inviwo/testutil/configurablegtesteventlistener.h>

#include <warn/push>
#include <warn/ignore/all>
#include <gtest/gtest.h>
#include <warn/pop>

using namespace inviwo;

int main(int argc, char** argv) {

    LogCentral::init();
    auto logger = std::make_shared<ConsoleLogger>();
    LogCentral::getPtr()->setVerbosity(LogVerbosity::Error);
    LogCentral::getPtr()->registerLogger(logger);
    InviwoApplication app(argc, argv, "Inviwo-Unittests-Fermi");

    {
        std::vector<std::unique_ptr<InviwoModuleFactoryObject>> modules;
        modules.emplace_back(createInviwoCore());
        modules.emplace_back(createPython3Module());
        modules.emplace_back(createFermiModule());
        app.registerModules(std::move(modules));
    }

    app.processFront();

    int ret = -1;
    {
#ifdef IVW_ENABLE_MSVC_MEM_LEAK_TEST
        VLDDisable();
        ::testing::InitGoogleTest(&argc, argv);
        VLDEnable();
#else
        ::testing::InitGoogleTest(&argc, argv);
#endif
        ConfigurableGTestEventListener::setup();
        ret = RUN_ALL_TESTS();
    }
    return ret;
}
