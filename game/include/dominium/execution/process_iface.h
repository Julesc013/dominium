/*
FILE: include/dominium/execution/process_iface.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / execution
RESPONSIBILITY: Game-side process descriptor provider interface (no gameplay logic).
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
DETERMINISM: Providers MUST return deterministic descriptors and hooks.
*/
#ifndef DOMINIUM_EXECUTION_PROCESS_IFACE_H
#define DOMINIUM_EXECUTION_PROCESS_IFACE_H

#include "domino/process.h"

#ifdef __cplusplus

class IProcessProvider {
public:
    virtual ~IProcessProvider() {}

    /* Stable provider identifier. */
    virtual u64 provider_id() const = 0;

    /* Process descriptor lookup. */
    virtual u32 process_count() const = 0;
    virtual const dom_process_desc* process_desc(u32 index) const = 0;
    virtual const dom_process_hooks* process_hooks(u32 index) const = 0;
};

#endif /* __cplusplus */

#endif /* DOMINIUM_EXECUTION_PROCESS_IFACE_H */
