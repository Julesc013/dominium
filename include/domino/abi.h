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

typedef u32 dom_abi_version;
typedef u32 dom_iid;
typedef int dom_abi_result;

/* Every ABI-visible struct/vtable begins with these fields. */
#define DOM_ABI_HEADER u32 abi_version; u32 struct_size

/* Convenience initializer for the ABI header prefix. */
#define DOM_ABI_HEADER_INIT(version_u32, struct_type) \
    { (u32)(version_u32), (u32)sizeof(struct_type) }

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

