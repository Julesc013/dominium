/*
FILE: source/domino/core/mod_loader.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/mod_loader
RESPONSIBILITY: Implements `mod_loader`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/mod.h"
#include "core_internal.h"

bool dom_mod_load_all(dom_core* core, dom_instance_id inst)
{
    (void)core;
    (void)inst;
    return true;
}

void dom_mod_unload_all(dom_core* core, dom_instance_id inst)
{
    (void)core;
    (void)inst;
}

uint32_t dom_launcher_ext_count(dom_core* core)
{
    if (!core) return 0u;
    return core->launcher_ext_count;
}

const dom_launcher_ext_v1* dom_launcher_ext_get(dom_core* core, uint32_t index)
{
    if (!core || index >= core->launcher_ext_count) {
        return NULL;
    }
    return &core->launcher_exts[index];
}

bool dom_launcher_ext_register(dom_core* core, const dom_launcher_ext_v1* ext)
{
    dom_launcher_ext_v1* dst;
    if (!core || !ext) {
        return false;
    }
    if (ext->struct_size < sizeof(dom_launcher_ext_v1) ||
        ext->struct_version == 0u) {
        return false;
    }
    if (core->launcher_ext_count >= DOM_MAX_LAUNCHER_EXT) {
        return false;
    }
    dst = &core->launcher_exts[core->launcher_ext_count];
    *dst = *ext;
    core->launcher_ext_count += 1u;
    return true;
}
