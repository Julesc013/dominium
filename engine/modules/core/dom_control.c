/*
FILE: source/domino/core/dom_control.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/control
RESPONSIBILITY: Control capability registry + gating hooks (mechanism only).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, C89 headers.
FORBIDDEN DEPENDENCIES: product-layer headers; policy logic; secrets.
DETERMINISM: Logs only; must not mutate authoritative state.
REFERENCES: `docs/architecture/CONTROL_LAYERS.md`, `docs/architecture/NON_INTERFERENCE.md`.
*/
#include "domino/control.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if DOM_CONTROL_HOOKS

static void dom_control_log_decision(const char* action,
                                     const char* key,
                                     u32 id,
                                     const char* context)
{
    if (!action) {
        action = "unknown";
    }
    fprintf(stderr, "control_%s id=%u key=%s",
            action,
            (unsigned int)id,
            key ? key : "(null)");
    if (context && *context) {
        fprintf(stderr, " context=%s", context);
    }
    fprintf(stderr, "\n");
}

dom_control_result dom_control_caps_init(dom_control_caps* caps,
                                         const char* registry_path)
{
    dom_registry_result reg_res;
    u8* enabled;
    u32 size;

    if (!caps || !registry_path) {
        return DOM_CONTROL_ERR_NULL;
    }

    memset(caps, 0, sizeof(*caps));
    reg_res = dom_registry_load_file(registry_path, &caps->registry);
    if (reg_res != DOM_REGISTRY_OK) {
        memset(caps, 0, sizeof(*caps));
        return DOM_CONTROL_ERR_INVALID;
    }

    size = caps->registry.count + 1u;
    enabled = (u8*)calloc(size, sizeof(u8));
    if (!enabled) {
        dom_registry_free(&caps->registry);
        memset(caps, 0, sizeof(*caps));
        return DOM_CONTROL_ERR_OOM;
    }
    caps->enabled = enabled;
    caps->enabled_count = 0u;
    return DOM_CONTROL_OK;
}

void dom_control_caps_free(dom_control_caps* caps)
{
    if (!caps) {
        return;
    }
    if (caps->enabled) {
        free(caps->enabled);
        caps->enabled = (u8*)0;
    }
    dom_registry_free(&caps->registry);
    caps->enabled_count = 0u;
}

dom_control_result dom_control_caps_enable_id(dom_control_caps* caps, u32 id)
{
    if (!caps || !caps->enabled) {
        return DOM_CONTROL_ERR_NULL;
    }
    if (id == 0u || id > caps->registry.count) {
        return DOM_CONTROL_ERR_INVALID;
    }
    if (!caps->enabled[id]) {
        caps->enabled[id] = 1u;
        caps->enabled_count += 1u;
    }
    return DOM_CONTROL_OK;
}

dom_control_result dom_control_caps_enable_key(dom_control_caps* caps,
                                               const char* key)
{
    u32 id;
    if (!caps || !key) {
        return DOM_CONTROL_ERR_NULL;
    }
    id = dom_registry_id_from_key(&caps->registry, key);
    if (id == 0u) {
        return DOM_CONTROL_ERR_NOT_FOUND;
    }
    return dom_control_caps_enable_id(caps, id);
}

dom_control_result dom_control_caps_disable_id(dom_control_caps* caps, u32 id)
{
    if (!caps || !caps->enabled) {
        return DOM_CONTROL_ERR_NULL;
    }
    if (id == 0u || id > caps->registry.count) {
        return DOM_CONTROL_ERR_INVALID;
    }
    if (caps->enabled[id]) {
        caps->enabled[id] = 0u;
        if (caps->enabled_count > 0u) {
            caps->enabled_count -= 1u;
        }
    }
    return DOM_CONTROL_OK;
}

int dom_control_caps_is_enabled(const dom_control_caps* caps, u32 id)
{
    if (!caps || !caps->enabled) {
        return 0;
    }
    if (id == 0u || id > caps->registry.count) {
        return 0;
    }
    return caps->enabled[id] ? 1 : 0;
}

u32 dom_control_caps_count(const dom_control_caps* caps)
{
    if (!caps) {
        return 0u;
    }
    return caps->registry.count;
}

u32 dom_control_caps_enabled_count(const dom_control_caps* caps)
{
    if (!caps) {
        return 0u;
    }
    return caps->enabled_count;
}

const dom_registry* dom_control_caps_registry(const dom_control_caps* caps)
{
    return caps ? &caps->registry : (const dom_registry*)0;
}

dom_control_result dom_control_caps_require(const dom_control_caps* caps,
                                            u32 id,
                                            const char* context)
{
    const char* key;
    if (!caps || !caps->enabled) {
        return DOM_CONTROL_ERR_NULL;
    }
    if (id == 0u || id > caps->registry.count) {
        dom_control_log_decision("refuse_invalid", "(invalid)", id, context);
        return DOM_CONTROL_ERR_INVALID;
    }
    key = dom_registry_key_from_id(&caps->registry, id);
    if (!dom_control_caps_is_enabled(caps, id)) {
        dom_control_log_decision("refuse", key, id, context);
        return DOM_CONTROL_ERR_DISABLED;
    }
    dom_control_log_decision("allow", key, id, context);
    return DOM_CONTROL_OK;
}

#else

dom_control_result dom_control_caps_init(dom_control_caps* caps,
                                         const char* registry_path)
{
    (void)caps;
    (void)registry_path;
    return DOM_CONTROL_ERR_DISABLED;
}

void dom_control_caps_free(dom_control_caps* caps)
{
    (void)caps;
}

dom_control_result dom_control_caps_enable_id(dom_control_caps* caps, u32 id)
{
    (void)caps;
    (void)id;
    return DOM_CONTROL_ERR_DISABLED;
}

dom_control_result dom_control_caps_enable_key(dom_control_caps* caps,
                                               const char* key)
{
    (void)caps;
    (void)key;
    return DOM_CONTROL_ERR_DISABLED;
}

dom_control_result dom_control_caps_disable_id(dom_control_caps* caps, u32 id)
{
    (void)caps;
    (void)id;
    return DOM_CONTROL_ERR_DISABLED;
}

int dom_control_caps_is_enabled(const dom_control_caps* caps, u32 id)
{
    (void)caps;
    (void)id;
    return 0;
}

u32 dom_control_caps_count(const dom_control_caps* caps)
{
    (void)caps;
    return 0u;
}

u32 dom_control_caps_enabled_count(const dom_control_caps* caps)
{
    (void)caps;
    return 0u;
}

const dom_registry* dom_control_caps_registry(const dom_control_caps* caps)
{
    (void)caps;
    return (const dom_registry*)0;
}

dom_control_result dom_control_caps_require(const dom_control_caps* caps,
                                            u32 id,
                                            const char* context)
{
    (void)caps;
    (void)id;
    (void)context;
    return DOM_CONTROL_ERR_DISABLED;
}

#endif
