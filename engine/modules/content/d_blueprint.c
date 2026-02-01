/*
FILE: source/domino/content/d_blueprint.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / content/d_blueprint
RESPONSIBILITY: Implements `d_blueprint`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "content/d_blueprint.h"

#define D_BLUEPRINT_KIND_MAX 32u

static dblueprint_kind_vtable g_kind_vtables[D_BLUEPRINT_KIND_MAX];
static u32 g_kind_count = 0u;
static d_bool g_builtins_registered = D_FALSE;

static int d_blueprint_validate_stub(const d_tlv_blob *payload)
{
    if (!payload) {
        return -1;
    }
    /* TODO: implement strict validation once blueprint payload schemas exist. */
    return 0;
}

static int d_blueprint_compile_stub(const d_tlv_blob *payload)
{
    (void)payload;
    /* TODO: compile blueprint payload into protos and register via d_content. */
    return 0;
}

int d_blueprint_register_kind(const dblueprint_kind_vtable *vt)
{
    u32 i;
    if (!vt || vt->kind_id == 0u) {
        return -1;
    }
    for (i = 0u; i < g_kind_count; ++i) {
        if (g_kind_vtables[i].kind_id == vt->kind_id) {
            return -2;
        }
    }
    if (g_kind_count >= D_BLUEPRINT_KIND_MAX) {
        return -3;
    }
    g_kind_vtables[g_kind_count] = *vt;
    g_kind_count += 1u;
    return 0;
}

const dblueprint_kind_vtable *d_blueprint_get_kind(d_blueprint_kind_id kind_id)
{
    u32 i;
    for (i = 0u; i < g_kind_count; ++i) {
        if (g_kind_vtables[i].kind_id == kind_id) {
            return &g_kind_vtables[i];
        }
    }
    return (const dblueprint_kind_vtable *)0;
}

void d_blueprint_register_builtin_kinds(void)
{
    if (g_builtins_registered) {
        return;
    }

    {
        dblueprint_kind_vtable vt;
        memset(&vt, 0, sizeof(vt));
        vt.kind_id = BLUEPRINT_KIND_BUILDING;
        vt.name = "building";
        vt.validate = d_blueprint_validate_stub;
        vt.compile = d_blueprint_compile_stub; /* TODO: compile building into d_proto_building. */
        (void)d_blueprint_register_kind(&vt);
    }
    {
        dblueprint_kind_vtable vt;
        memset(&vt, 0, sizeof(vt));
        vt.kind_id = BLUEPRINT_KIND_VEHICLE;
        vt.name = "vehicle";
        vt.validate = d_blueprint_validate_stub;
        vt.compile = d_blueprint_compile_stub; /* TODO: compile vehicle + modules into registries. */
        (void)d_blueprint_register_kind(&vt);
    }
    {
        dblueprint_kind_vtable vt;
        memset(&vt, 0, sizeof(vt));
        vt.kind_id = BLUEPRINT_KIND_WEAPON;
        vt.name = "weapon";
        vt.validate = d_blueprint_validate_stub;
        vt.compile = d_blueprint_compile_stub; /* TODO: compile weapon blueprint. */
        (void)d_blueprint_register_kind(&vt);
    }
    {
        dblueprint_kind_vtable vt;
        memset(&vt, 0, sizeof(vt));
        vt.kind_id = BLUEPRINT_KIND_SUBASSEMBLY;
        vt.name = "subassembly";
        vt.validate = d_blueprint_validate_stub;
        vt.compile = d_blueprint_compile_stub; /* TODO: compile module/subassembly. */
        (void)d_blueprint_register_kind(&vt);
    }
    {
        dblueprint_kind_vtable vt;
        memset(&vt, 0, sizeof(vt));
        vt.kind_id = BLUEPRINT_KIND_SPLINE_PROFILE;
        vt.name = "spline_profile";
        vt.validate = d_blueprint_validate_stub;
        vt.compile = d_blueprint_compile_stub; /* TODO: compile spline profile blueprint. */
        (void)d_blueprint_register_kind(&vt);
    }
    {
        dblueprint_kind_vtable vt;
        memset(&vt, 0, sizeof(vt));
        vt.kind_id = BLUEPRINT_KIND_MACHINE_CONFIG;
        vt.name = "machine_config";
        vt.validate = d_blueprint_validate_stub;
        vt.compile = d_blueprint_compile_stub; /* TODO: compile machine config blueprint. */
        (void)d_blueprint_register_kind(&vt);
    }

    g_builtins_registered = D_TRUE;
}
