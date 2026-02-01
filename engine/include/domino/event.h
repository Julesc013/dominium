/*
FILE: include/domino/event.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / event
RESPONSIBILITY: Defines the public contract for `event` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_EVENT_H_INCLUDED
#define DOMINO_EVENT_H_INCLUDED

#include "domino/baseline.h"
#include "domino/core.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_event_kind: Public type used by `event`. */
typedef enum {
    DOM_EVT_NONE = 0,
    DOM_EVT_PKG_INSTALLED,
    DOM_EVT_PKG_UNINSTALLED,
    DOM_EVT_INST_CREATED,
    DOM_EVT_INST_UPDATED,
    DOM_EVT_INST_DELETED,
    DOM_EVT_SIM_TICKED
} dom_event_kind;

/* u: Public type used by `event`. */
typedef struct {
    uint32_t       struct_size;
    uint32_t       struct_version;
    dom_event_kind kind;
    union {
        dom_package_id  pkg_id;
        dom_instance_id inst_id;
    } u;
} dom_event;

/* user: Public type used by `event`. */
typedef void (*dom_event_handler)(dom_core* core, const dom_event* ev, void* user);

/* Purpose: Subscribe event.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dom_event_subscribe(dom_core* core, dom_event_kind kind, dom_event_handler fn, void* user);
/* Purpose: Unsubscribe event.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dom_event_unsubscribe(dom_core* core, dom_event_kind kind, dom_event_handler fn, void* user);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_EVENT_H_INCLUDED */
