/*
FILE: include/domino/ups.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ups
RESPONSIBILITY: Defines Universal Pack System (UPS) manifest loading and capability resolution contracts.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Resolution order and capability indexing MUST be deterministic for the same inputs.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_UPS_H
#define DOMINO_UPS_H

#include "domino/core/types.h"
#include "domino/version.h"
#include "domino/capability.h"
#include "domino/compat_modes.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Limits (fixed-size, no allocations in public contract). */
#define DOM_UPS_MAX_PACKS           128u
#define DOM_UPS_MAX_PACK_ID         128u
#define DOM_UPS_MAX_CAP_ID          64u
#define DOM_UPS_MAX_CAPS_PER_PACK   32u
#define DOM_UPS_MAX_DEPS_PER_PACK   32u
#define DOM_UPS_MAX_PROTOCOLS       16u
#define DOM_UPS_MAX_PROTOCOL_ID     64u
#define DOM_UPS_MAX_FALLBACKS       128u
#define DOM_UPS_MAX_FALLBACK_ID     64u
#define DOM_UPS_MAX_REASON          96u
#define DOM_UPS_MAX_PROVIDERS       (DOM_UPS_MAX_PACKS * DOM_UPS_MAX_CAPS_PER_PACK)
#define DOM_UPS_MAX_CAPABILITIES    DOM_UPS_MAX_PROVIDERS
#define DOM_UPS_MAX_REQUIREMENTS    (DOM_UPS_MAX_PACKS * DOM_UPS_MAX_DEPS_PER_PACK)

/* dom_ups_manifest_error_code: Parser/validation error codes. */
typedef enum dom_ups_manifest_error_code {
    DOM_UPS_MANIFEST_OK = 0,
    DOM_UPS_MANIFEST_ERR_INVALID = 1,
    DOM_UPS_MANIFEST_ERR_MISSING_FIELD = 2,
    DOM_UPS_MANIFEST_ERR_TOO_MANY = 3,
    DOM_UPS_MANIFEST_ERR_BAD_VERSION = 4,
    DOM_UPS_MANIFEST_ERR_BAD_PROTOCOL = 5,
    DOM_UPS_MANIFEST_ERR_BAD_CAPABILITY = 6
} dom_ups_manifest_error_code;

/* dom_ups_manifest_error: Error details for manifest parse/validate. */
typedef struct dom_ups_manifest_error {
    dom_ups_manifest_error_code code;
    u32                         line;
    char                        message[128];
} dom_ups_manifest_error;

/* dom_ups_protocol_requirement: Required protocol version entry. */
typedef struct dom_ups_protocol_requirement {
    char protocol_id[DOM_UPS_MAX_PROTOCOL_ID];
    u32  version;
} dom_ups_protocol_requirement;

/* dom_ups_manifest: Canonical pack manifest fields (UPS). */
typedef struct dom_ups_manifest {
    char          pack_id[DOM_UPS_MAX_PACK_ID];
    domino_semver pack_version;
    d_bool        has_pack_version;
    u32           pack_format_version;
    domino_semver required_engine_version;
    d_bool        has_required_engine_version;
    d_bool        optional;

    u32           provides_count;
    char          provides[DOM_UPS_MAX_CAPS_PER_PACK][DOM_UPS_MAX_CAP_ID];

    u32           dependency_count;
    char          dependencies[DOM_UPS_MAX_DEPS_PER_PACK][DOM_UPS_MAX_CAP_ID];

    u32           required_protocol_count;
    dom_ups_protocol_requirement required_protocols[DOM_UPS_MAX_PROTOCOLS];
} dom_ups_manifest;

/* dom_ups_pack_entry: Read-only pack entry returned by registry inspection. */
typedef struct dom_ups_pack_entry {
    dom_ups_manifest manifest;
    u32              precedence;
    u64              manifest_hash;
} dom_ups_pack_entry;

/* dom_ups_provider_entry: Resolved provider (capability -> pack). */
typedef struct dom_ups_provider_entry {
    char          capability_id[DOM_UPS_MAX_CAP_ID];
    char          pack_id[DOM_UPS_MAX_PACK_ID];
    domino_semver pack_version;
    u32           precedence;
} dom_ups_provider_entry;

/* dom_ups_fallback_event: Recorded fallback activation. */
typedef struct dom_ups_fallback_event {
    char capability_id[DOM_UPS_MAX_CAP_ID];
    char fallback_id[DOM_UPS_MAX_FALLBACK_ID];
    char reason[DOM_UPS_MAX_REASON];
} dom_ups_fallback_event;

/* dom_ups_registry: Opaque registry of loaded pack manifests. */
typedef struct dom_ups_registry dom_ups_registry;

/* Manifest helpers */
void dom_ups_manifest_init(dom_ups_manifest* out_manifest);
int dom_ups_manifest_parse_text(const char* text,
                                dom_ups_manifest* out_manifest,
                                dom_ups_manifest_error* out_error);
int dom_ups_manifest_parse_file(const char* path,
                                dom_ups_manifest* out_manifest,
                                dom_ups_manifest_error* out_error);
int dom_ups_manifest_validate(const dom_ups_manifest* manifest,
                              dom_ups_manifest_error* out_error);

/* Registry lifecycle */
dom_ups_registry* dom_ups_registry_create(void);
void dom_ups_registry_destroy(dom_ups_registry* reg);
void dom_ups_registry_clear(dom_ups_registry* reg);

/* Registry mutation */
int dom_ups_registry_add_pack(dom_ups_registry* reg,
                              const dom_ups_manifest* manifest,
                              u32 precedence,
                              u64 manifest_hash,
                              dom_ups_manifest_error* out_error);

/* Registry inspection */
u32 dom_ups_registry_pack_count(const dom_ups_registry* reg);
int dom_ups_registry_pack_get(const dom_ups_registry* reg,
                              u32 index,
                              dom_ups_pack_entry* out_entry);

/* Capability sets (sorted, unique). */
dom_capability_set_view dom_ups_registry_provided_caps(const dom_ups_registry* reg);
dom_capability_set_view dom_ups_registry_required_caps(const dom_ups_registry* reg);
dom_capability_set_view dom_ups_registry_optional_caps(const dom_ups_registry* reg);

/* Capability resolution (deterministic precedence). */
int dom_ups_registry_resolve_capability(const dom_ups_registry* reg,
                                        const char* capability_id,
                                        dom_ups_provider_entry* out_entry);
u32 dom_ups_registry_list_providers(const dom_ups_registry* reg,
                                    const char* capability_id,
                                    dom_ups_provider_entry* out_entries,
                                    u32 max_out);

/* Fallback reporting (deterministic, code-level). */
int dom_ups_registry_report_fallback(dom_ups_registry* reg,
                                     const char* capability_id,
                                     const char* fallback_id,
                                     const char* reason);
u32 dom_ups_registry_fallback_count(const dom_ups_registry* reg);
int dom_ups_registry_fallback_get(const dom_ups_registry* reg,
                                  u32 index,
                                  dom_ups_fallback_event* out_event);

/* Compatibility decision storage (explicit). */
void dom_ups_registry_set_compat_decision(dom_ups_registry* reg,
                                          dom_compat_decision decision);
dom_compat_decision dom_ups_registry_get_compat_decision(const dom_ups_registry* reg);
d_bool dom_ups_registry_has_compat_decision(const dom_ups_registry* reg);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_UPS_H */
