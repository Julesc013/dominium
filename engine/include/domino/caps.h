/*
FILE: include/domino/caps.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / caps
RESPONSIBILITY: Defines the public contract for `caps` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_CAPS_H_INCLUDED
#define DOMINO_CAPS_H_INCLUDED
/*
 * Capability registry + deterministic backend selection (C89/C++98 visible).
 *
 * This module centralizes backend registration and selection for runtime
 * subsystems (platform/system, graphics, etc.). Selection is deterministic:
 * registration order is not trusted.
 */

#include "domino/abi.h"
#include "domino/core/types.h"
#include "domino/determinism.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ABI / sizing */
#define DOM_CAPS_ABI_VERSION 1u

/* Limits (fixed-size, no allocations) */
#define DOM_CAPS_MAX_BACKENDS        128u
#define DOM_CAPS_MAX_SELECTION       32u
#define DOM_CAPS_AUDIT_LOG_MAX_BYTES 4096u

/* dom_subsystem_id: Public type used by `caps`. */
typedef u32 dom_subsystem_id;

/* Built-in subsystem IDs (stable numeric identifiers). */
#define DOM_SUBSYS_DSYS ((dom_subsystem_id)0x44535953u) /* 'DSYS' */
#define DOM_SUBSYS_DGFX ((dom_subsystem_id)0x44474658u) /* 'DGFX' */
#define DOM_SUBSYS_DUI  ((dom_subsystem_id)0x44554920u) /* 'DUI ' */

/* dom_caps_perf_class: Public type used by `caps`. */
typedef enum dom_caps_perf_class_e {
    DOM_CAPS_PERF_BASELINE = 0,
    DOM_CAPS_PERF_COMPAT   = 1,
    DOM_CAPS_PERF_PERF     = 2
} dom_caps_perf_class;

/* Subsystem flags (declared per backend; must match within a subsystem). */
#define DOM_CAPS_SUBSYS_LOCKSTEP_RELEVANT (1u << 0u)

/* Backend flags */
#define DOM_CAPS_BACKEND_PRESENTATION_ONLY (1u << 0u)

/* dom_hw_caps: Public type used by `caps`. */
typedef struct dom_hw_caps_s {
    DOM_ABI_HEADER;
    u32 os_flags;
    u32 cpu_flags;
    u32 gpu_flags;
} dom_hw_caps;

/* Host capability flags (bitset values for (os_flags|cpu_flags|gpu_flags)). */

/* OS flags (bits 0..7). */
#define DOM_HW_OS_WIN32  (1u << 0u)
#define DOM_HW_OS_UNIX   (1u << 1u)
#define DOM_HW_OS_APPLE  (1u << 2u)

/* CPU flags (bits 8..15). */
#define DOM_HW_CPU_X86_16 (1u << 8u)
#define DOM_HW_CPU_X86_32 (1u << 9u)
#define DOM_HW_CPU_X86_64 (1u << 10u)
#define DOM_HW_CPU_ARM_32 (1u << 11u)
#define DOM_HW_CPU_ARM_64 (1u << 12u)

/* Basic host probe (no allocations, no syscalls required). */
dom_abi_result dom_hw_caps_probe_host(dom_hw_caps* io_hw_caps);

/* io_hw_caps: Public type used by `caps`. */
typedef dom_abi_result (*dom_caps_probe_fn)(dom_hw_caps* io_hw_caps);

/*
 * Generic API pointer provider for a subsystem/backend.
 *
 * Returns a pointer to a versioned ABI struct/vtable whose first fields match
 * DOM_ABI_HEADER. The pointer must remain valid for the process lifetime.
 *
 * The registry treats this pointer as opaque; the caller interprets it based
 * on the subsystem_id.
 */
typedef const void* (*dom_caps_get_api_fn)(u32 requested_abi);

/* dom_backend_desc: Public type used by `caps`. */
typedef struct dom_backend_desc_s {
    DOM_ABI_HEADER;

    dom_subsystem_id subsystem_id;
    const char*      subsystem_name; /* optional; used for diagnostics only */

    const char* backend_name;  /* stable ASCII id (recommend lowercase) */
    u32         backend_priority;

    u32 required_hw_flags; /* bitset compared against (os|cpu|gpu) flags */
    u32 subsystem_flags;   /* DOM_CAPS_SUBSYS_* */
    u32 backend_flags;     /* DOM_CAPS_BACKEND_* */

    dom_det_grade       determinism;
    dom_caps_perf_class perf_class;

    dom_caps_get_api_fn get_api; /* optional */
    dom_caps_probe_fn   probe;   /* optional */
} dom_backend_desc;

/* dom_caps_result: Public type used by `caps`. */
typedef enum dom_caps_result_e {
    DOM_CAPS_OK = 0,

    DOM_CAPS_ERR = -1,
    DOM_CAPS_ERR_NULL = -2,
    DOM_CAPS_ERR_BAD_DESC = -3,
    DOM_CAPS_ERR_TOO_MANY = -4,
    DOM_CAPS_ERR_DUPLICATE = -5,
    DOM_CAPS_ERR_FINALIZED = -6,
    DOM_CAPS_ERR_NOT_FINALIZED = -7,
    DOM_CAPS_ERR_NO_ELIGIBLE = -8
} dom_caps_result;

/* dom_sel_fail_reason: Public type used by `caps`. */
typedef enum dom_sel_fail_reason_e {
    DOM_SEL_FAIL_NONE = 0,
    DOM_SEL_FAIL_REGISTRY_NOT_FINALIZED = 1,
    DOM_SEL_FAIL_NO_ELIGIBLE_BACKEND = 2,
    DOM_SEL_FAIL_LOCKSTEP_REQUIRES_D0 = 3,
    DOM_SEL_FAIL_OVERRIDE_NOT_FOUND = 4
} dom_sel_fail_reason;

/* dom_selection_entry: Public type used by `caps`. */
typedef struct dom_selection_entry_s {
    dom_subsystem_id subsystem_id;
    const char*      subsystem_name; /* may be NULL */
    const char*      backend_name;
    dom_det_grade    determinism;
    dom_caps_perf_class perf_class;
    u32 backend_priority;

    u32 chosen_by_override;
} dom_selection_entry;

/* dom_selection: Public type used by `caps`. */
typedef struct dom_selection_s {
    DOM_ABI_HEADER;

    dom_caps_result result;
    dom_sel_fail_reason fail_reason;
    dom_subsystem_id fail_subsystem_id;

    u32 entry_count;
    dom_selection_entry entries[DOM_CAPS_MAX_SELECTION];
} dom_selection;

/* Profile is defined by the product layer; caps treats it as opaque. */
struct dom_profile;

/* Registry lifecycle */
dom_caps_result dom_caps_register_backend(const dom_backend_desc* desc);
/* Purpose: Register builtin backends.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_caps_result dom_caps_register_builtin_backends(void);
/* Purpose: Finalize registry.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_caps_result dom_caps_finalize_registry(void);

/* Inspection */
u32 dom_caps_backend_count(void);
/* Purpose: Get caps backend.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_caps_result dom_caps_backend_get(u32 index, dom_backend_desc* out_desc);

/* Selection */
dom_caps_result dom_caps_select(const struct dom_profile* profile,
                                const dom_hw_caps* hw,
                                dom_selection* out);

/* Audit log generation */
dom_caps_result dom_caps_get_audit_log(const dom_selection* sel,
                                       char* buf,
                                       u32* io_len);

/* Purpose: Write capabilities export to a DTLV file.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dom_caps_result dom_caps_write_capabilities_tlv(const dom_selection* sel,
                                                const char* path);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CAPS_H_INCLUDED */
