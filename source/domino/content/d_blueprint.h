/*
FILE: source/domino/content/d_blueprint.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / content/d_blueprint
RESPONSIBILITY: Implements `d_blueprint`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Generic blueprint definitions (data-only, C89). */
#ifndef D_BLUEPRINT_H
#define D_BLUEPRINT_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_blueprint_id;
typedef u16 d_blueprint_kind_id;

typedef struct d_blueprint {
    d_blueprint_id     id;
    d_blueprint_kind_id kind_id;
    u16                version;
    d_tlv_blob         payload;   /* kind-specific TLV payload */
} d_blueprint;

/* Kind vtable */
typedef struct dblueprint_kind_vtable {
    d_blueprint_kind_id kind_id;
    const char         *name;  /* "building", "vehicle", "weapon", "subassembly", "spline_profile", "machine_config" */

    /* Validate blueprint payload; return 0 on success. */
    int (*validate)(const d_tlv_blob *payload);

    /*
     * Compile blueprint payload into one or more engine protos.
     * Typically this populates d_proto_building, d_proto_vehicle, etc. via d_content's registries.
     * Return 0 on success.
     */
    int (*compile)(const d_tlv_blob *payload);
} dblueprint_kind_vtable;

/* Built-in blueprint kinds */
enum {
    BLUEPRINT_KIND_BUILDING       = 1,
    BLUEPRINT_KIND_VEHICLE        = 2,
    BLUEPRINT_KIND_WEAPON         = 3,
    BLUEPRINT_KIND_SUBASSEMBLY    = 4,
    BLUEPRINT_KIND_SPLINE_PROFILE = 5,
    BLUEPRINT_KIND_MACHINE_CONFIG = 6
};

/* Register a blueprint kind; returns 0 on success. */
int d_blueprint_register_kind(const dblueprint_kind_vtable *vt);

/* Lookup a kind by id; returns NULL if not found. */
const dblueprint_kind_vtable *d_blueprint_get_kind(d_blueprint_kind_id kind_id);

/* Register built-in kinds (idempotent). */
void d_blueprint_register_builtin_kinds(void);

#ifdef __cplusplus
}
#endif

#endif /* D_BLUEPRINT_H */
