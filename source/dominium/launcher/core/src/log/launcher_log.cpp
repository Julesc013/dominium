/*
FILE: source/dominium/launcher/core/src/log/launcher_log.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / log
RESPONSIBILITY: Emits structured log events via launcher services facade.
*/
#include "launcher_log.h"

#include <cstring>

extern "C" const launcher_log_api_v1* launcher_services_get_log_api(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_LOG_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_log_api_v1*)iface;
}

extern "C" int launcher_services_emit_event(const launcher_services_api_v1* services,
                                            const core_log_scope* scope,
                                            const core_log_event* ev) {
    const launcher_log_api_v1* log_api = launcher_services_get_log_api(services);
    core_log_scope local_scope;
    if (!log_api || !log_api->emit_event) {
        return 0;
    }
    if (!scope) {
        std::memset(&local_scope, 0, sizeof(local_scope));
        scope = &local_scope;
    }
    return (log_api->emit_event(log_api->user, scope, ev) == 0) ? 0 : -1;
}

extern "C" void launcher_log_add_err_fields(core_log_event* ev, const err_t* err) {
    if (!ev || !err) {
        return;
    }
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_DOMAIN, (u32)err->domain);
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_CODE, (u32)err->code);
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_FLAGS, (u32)err->flags);
    (void)core_log_event_add_u32(ev, CORE_LOG_KEY_ERR_MSG_ID, (u32)err->msg_id);
}
