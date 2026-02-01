/*
FILE: include/domino/inst.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / inst
RESPONSIBILITY: Defines the public contract for `inst` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_INST_H_INCLUDED
#define DOMINO_INST_H_INCLUDED

#include <stddef.h>
#include "domino/baseline.h"
#include "domino/sys.h"
#include "domino/pkg.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dom_core_t;
/* dom_core: Public type used by `inst`. */
typedef struct dom_core_t dom_core;

/* dom_instance_id: Public type used by `inst`. */
typedef uint32_t dom_instance_id;

#define DOM_MAX_INSTANCE_PACKAGES 8

/* dom_instance_info: Public type used by `inst`. */
typedef struct dom_instance_info {
    uint32_t        struct_size;
    uint32_t        struct_version;
    dom_instance_id id;
    char            name[64];
    char            path[260];
    char            descriptor_path[260];
    char            saves_path[260];
    char            config_path[260];
    char            logs_path[260];
    uint32_t        flags;
    uint32_t        pkg_count;
    dom_package_id  pkgs[DOM_MAX_INSTANCE_PACKAGES];
} dom_instance_info;

/* Purpose: List inst.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
uint32_t        dom_inst_list(dom_core* core, dom_instance_info* out, uint32_t max_out);
/* Purpose: Get inst.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool            dom_inst_get(dom_core* core, dom_instance_id id, dom_instance_info* out);
/* Purpose: Create inst.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_instance_id dom_inst_create(dom_core* core, const dom_instance_info* desc);
/* Purpose: Update inst.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool            dom_inst_update(dom_core* core, const dom_instance_info* desc);
/* Purpose: Delete inst.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool            dom_inst_delete(dom_core* core, dom_instance_id id);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_INST_H_INCLUDED */
