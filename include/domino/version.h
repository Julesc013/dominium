/*
FILE: include/domino/version.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / version
RESPONSIBILITY: Defines the public contract for `version` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_VERSION_H
#define DOMINO_VERSION_H

#define DOMINO_VERSION_MAJOR 0
#define DOMINO_VERSION_MINOR 1
#define DOMINO_VERSION_PATCH 0

#define DOMINO_VERSION_STRING "0.1.0"

#ifdef __cplusplus
extern "C" {
#endif

/* domino_semver: Public type used by `version`. */
typedef struct domino_semver {
    int major;
    int minor;
    int patch;
} domino_semver;

/* domino_semver_range: Public type used by `version`. */
typedef struct domino_semver_range {
    domino_semver min_version;
    domino_semver max_version;
    int has_min;
    int has_max;
} domino_semver_range;

/* Purpose: Parse domino semver.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_semver_parse(const char* str, domino_semver* out);
/* Purpose: Compare domino semver.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_semver_compare(const domino_semver* a, const domino_semver* b);
/* Purpose: Range domino semver in.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_semver_in_range(const domino_semver* v,
                           const domino_semver_range* range);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_VERSION_H */
