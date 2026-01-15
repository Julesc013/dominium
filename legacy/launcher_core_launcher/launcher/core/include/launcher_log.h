/*
FILE: source/dominium/launcher/core/include/launcher_log.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / log
RESPONSIBILITY: Provides a small helper to emit structured log events via services.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_LOG_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_LOG_H

#ifdef __cplusplus
extern "C" {
#endif

#include "launcher_core_api.h"

const launcher_log_api_v1* launcher_services_get_log_api(const launcher_services_api_v1* services);
int launcher_services_emit_event(const launcher_services_api_v1* services,
                                 const core_log_scope* scope,
                                 const core_log_event* ev);
void launcher_log_add_err_fields(core_log_event* ev, const err_t* err);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_LOG_H */
