/*
FILE: include/domino/abi.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / abi
RESPONSIBILITY: Defines the public contract for `abi` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_ABI_H
#define DOMINO_ABI_H
/*
 * Domino ABI helpers (C89/C++98 visible).
 *
 * This header defines the minimum conventions for versioned, POD-only ABI
 * structs and vtables used by facades/backends.
 */

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_abi_version: Public type used by `abi`. */
typedef u32 dom_abi_version;
/* dom_iid: Public type used by `abi`. */
typedef u32 dom_iid;
/* dom_abi_result: Public type used by `abi`. */
typedef int dom_abi_result;

/* Every ABI-visible struct/vtable begins with these fields. */
#define DOM_ABI_HEADER u32 abi_version; u32 struct_size

/* DOM_ABI_HEADER_INIT
 * Purpose: Convenience initializer for the ABI header prefix (`abi_version`, `struct_size`).
 * Parameters:
 *   version_u32 (in): ABI version written to `abi_version`.
 *   struct_type (in): Struct type used to compute `struct_size` via `sizeof`.
 * Expands to:
 *   (u32)(version_u32), (u32)sizeof(struct_type)
 */
#define DOM_ABI_HEADER_INIT(version_u32, struct_type) \
    (u32)(version_u32), (u32)sizeof(struct_type)

/* C89/C++98 static assert (no _Static_assert). */
#define DOM_ABI__CONCAT2(a, b) a##b
#define DOM_ABI__CONCAT(a, b) DOM_ABI__CONCAT2(a, b)
#define DOM_ABI_STATIC_ASSERT(cond) \
    typedef char DOM_ABI__CONCAT(dom_abi_static_assert_, __LINE__)[(cond) ? 1 : -1]

/* Size check helper. */
#define DOM_ABI_SIZE_CHECK(struct_type, expected_size) \
    DOM_ABI_STATIC_ASSERT(sizeof(struct_type) == (expected_size))

/* Canonical query_interface signature for ABI facades. */
typedef dom_abi_result (*dom_query_interface_fn)(dom_iid iid, void** out_iface);

#define DOM_IID_INVALID ((dom_iid)0u)

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_ABI_H */
