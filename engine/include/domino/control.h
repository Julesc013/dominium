/*
FILE: include/domino/control.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / control
RESPONSIBILITY: Control capability registry + gating hooks (mechanism only).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: product-layer headers; policy logic; secrets.
DETERMINISM: Control hooks must not mutate authoritative state.
REFERENCES: `docs/arch/CONTROL_LAYERS.md`, `docs/arch/NON_INTERFERENCE.md`.
*/
#ifndef DOMINO_CONTROL_H_INCLUDED
#define DOMINO_CONTROL_H_INCLUDED

#include "domino/core/types.h"
#include "domino/registry.h"

#ifdef __cplusplus
extern "C" {
#endif

#ifndef DOM_CONTROL_HOOKS
#define DOM_CONTROL_HOOKS 1
#endif

typedef enum dom_control_result {
    DOM_CONTROL_OK = 0,
    DOM_CONTROL_ERR_NULL = -1,
    DOM_CONTROL_ERR_DISABLED = -2,
    DOM_CONTROL_ERR_INVALID = -3,
    DOM_CONTROL_ERR_NOT_FOUND = -4,
    DOM_CONTROL_ERR_OOM = -5
} dom_control_result;

typedef struct dom_control_caps {
    dom_registry registry;
    u8* enabled;
    u32 enabled_count;
} dom_control_caps;

dom_control_result dom_control_caps_init(dom_control_caps* caps,
                                         const char* registry_path);
void dom_control_caps_free(dom_control_caps* caps);

dom_control_result dom_control_caps_enable_id(dom_control_caps* caps, u32 id);
dom_control_result dom_control_caps_enable_key(dom_control_caps* caps,
                                               const char* key);
dom_control_result dom_control_caps_disable_id(dom_control_caps* caps, u32 id);

int dom_control_caps_is_enabled(const dom_control_caps* caps, u32 id);
u32 dom_control_caps_count(const dom_control_caps* caps);
u32 dom_control_caps_enabled_count(const dom_control_caps* caps);
const dom_registry* dom_control_caps_registry(const dom_control_caps* caps);

dom_control_result dom_control_caps_require(const dom_control_caps* caps,
                                            u32 id,
                                            const char* context);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CONTROL_H_INCLUDED */
