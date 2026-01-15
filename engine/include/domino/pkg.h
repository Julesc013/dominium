/*
FILE: include/domino/pkg.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / pkg
RESPONSIBILITY: Defines the public contract for `pkg` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_PKG_H_INCLUDED
#define DOMINO_PKG_H_INCLUDED

#include <stddef.h>
#include "domino/baseline.h"
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dom_core_t;
/* dom_core: Public type used by `pkg`. */
typedef struct dom_core_t dom_core;

/* dom_package_id: Public type used by `pkg`. */
typedef uint32_t dom_package_id;

/* dom_package_kind: Public type used by `pkg`. */
typedef enum dom_package_kind {
    DOM_PKG_KIND_UNKNOWN = 0,
    DOM_PKG_KIND_MOD,
    DOM_PKG_KIND_CONTENT,
    DOM_PKG_KIND_PRODUCT,
    DOM_PKG_KIND_TOOL,
    DOM_PKG_KIND_PACK
} dom_package_kind;

#define DOM_MAX_PACKAGE_DEPS 8

/* dom_package_info: Public type used by `pkg`. */
typedef struct dom_package_info {
    uint32_t         struct_size;
    uint32_t         struct_version;
    dom_package_id   id;
    dom_package_kind kind;
    char             name[64];
    char             version[32];
    char             author[64];
    char             install_path[260];
    char             manifest_path[260];
    char             content_root[260];
    uint32_t         dep_count;
    dom_package_id   deps[DOM_MAX_PACKAGE_DEPS];
    char             game_version_min[32];
    char             game_version_max[32];
} dom_package_info;

/* Purpose: List pkg.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
uint32_t dom_pkg_list(dom_core* core, dom_package_info* out, uint32_t max_out);
/* Purpose: Get pkg.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool     dom_pkg_get(dom_core* core, dom_package_id id, dom_package_info* out);
/* Purpose: Install pkg.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool     dom_pkg_install(dom_core* core, const char* source_path, dom_package_id* out_id);
/* Purpose: Uninstall pkg.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool     dom_pkg_uninstall(dom_core* core, dom_package_id id);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_PKG_H_INCLUDED */
