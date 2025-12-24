/*
FILE: tools/setup/ui/user/ui_setup_ui_actions_user.h
MODULE: Repository
LAYER / SUBSYSTEM: tools/setup/ui
RESPONSIBILITY: Declares user-owned UI action stubs for the setup tool; does NOT define generated IDs or dispatch tables.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; caller controls threading for UI dispatch.
ERROR MODEL: N/A (void handlers; error reporting is external to these stubs).
DETERMINISM: N/A (tooling/UI layer).
VERSIONING / ABI / DATA FORMAT NOTES: Signatures are generated from UI action schemas; keep in sync with generated tables.
EXTENSION POINTS: Implement handler bodies in the user source file; regenerate stubs via the UI tool pipeline.
*/
/* User action stubs. */
#ifndef UI_SETUP_UI_ACTIONS_USER_H_INCLUDED
#define UI_SETUP_UI_ACTIONS_USER_H_INCLUDED

#include "dui/domui_event.h"

#ifdef __cplusplus
extern "C" {
#endif

// BEGIN AUTO-GENERATED ACTION STUBS
void ui_setup_ui_act_SETUP_BROWSE_PATH(void* user_ctx, const domui_event* e);
void ui_setup_ui_act_SETUP_NAV_BACK(void* user_ctx, const domui_event* e);
void ui_setup_ui_act_SETUP_NAV_CANCEL(void* user_ctx, const domui_event* e);
void ui_setup_ui_act_SETUP_NAV_FINISH(void* user_ctx, const domui_event* e);
void ui_setup_ui_act_SETUP_NAV_INSTALL(void* user_ctx, const domui_event* e);
void ui_setup_ui_act_SETUP_NAV_NEXT(void* user_ctx, const domui_event* e);
void ui_setup_ui_act_SETUP_OPTIONS_CHANGED(void* user_ctx, const domui_event* e);
// END AUTO-GENERATED ACTION STUBS

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* UI_SETUP_UI_ACTIONS_USER_H_INCLUDED */
