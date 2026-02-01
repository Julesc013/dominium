/*
FILE: include/dominium/repo.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / repo
RESPONSIBILITY: Defines the public contract for `repo` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/dominium/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_REPO_H
#define DOMINIUM_REPO_H

#include "domino/compat.h"
#include <stddef.h>

/* DmnRepoItem: Public type used by `repo`. */
typedef struct DmnRepoItem_ {
    char id[64];
    char version[32];
    char source[32];
    char path[260];
} DmnRepoItem;

/* DmnRepoItemList: Public type used by `repo`. */
typedef struct DmnRepoItemList_ {
    DmnRepoItem* items;
    size_t       count;
} DmnRepoItemList;

/* Purpose: Find product build.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dmn_repo_find_product_build(const char* product,
                                const char* version,
                                const char* core_version,
                                DomOSFamily osfam,
                                DomArch arch,
                                char* out_path,
                                size_t out_path_cap);

/* Purpose: List mods.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dmn_repo_list_mods(DmnRepoItemList* out);
/* Purpose: Resolve mod.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dmn_repo_resolve_mod(const char* id, const char* version, char* out_path, size_t out_path_cap);

/* Purpose: List packs.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dmn_repo_list_packs(DmnRepoItemList* out);
/* Purpose: Resolve pack.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dmn_repo_resolve_pack(const char* id, const char* version, char* out_path, size_t out_path_cap);

/* Purpose: Free item list.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void dmn_repo_free_item_list(DmnRepoItemList* list);

#endif /* DOMINIUM_REPO_H */
