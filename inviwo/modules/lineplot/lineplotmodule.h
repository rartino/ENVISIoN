#ifndef IVW_LINEPLOTMODULE_H
#define IVW_LINEPLOTMODULE_H

#include <modules/lineplot/lineplotmoduledefine.h>

#include <inviwo/core/common/inviwomodule.h>

namespace inviwo {

class IVW_MODULE_LINEPLOT_API lineplotModule : public InviwoModule {
public:
    lineplotModule(InviwoApplication* app);
    virtual ~lineplotModule() = default;
};

} // namespace

#endif // IVW_LINEPLOTMODULE_H
