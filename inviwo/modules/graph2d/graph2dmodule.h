#ifndef IVW_GRAPH2DMODULE_H
#define IVW_GRAPH2DMODULE_H

#include <modules/graph2d/graph2dmoduledefine.h>

#include <inviwo/core/common/inviwomodule.h>

namespace inviwo {

class IVW_MODULE_GRAPH2D_API graph2dModule : public InviwoModule {
public:
    graph2dModule(InviwoApplication* app);
    virtual ~graph2dModule() = default;
};

} // namespace

#endif // IVW_GRAPH2DMODULE_H
