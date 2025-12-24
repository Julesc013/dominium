/*
FILE: tools/tool_editor/ui/user/ui_tool_editor_actions_user.h
MODULE: Repository
LAYER / SUBSYSTEM: tools/tool_editor/ui
RESPONSIBILITY: Declares user-owned UI action stubs for the tool editor; does NOT define generated IDs or dispatch tables.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; caller controls threading for UI dispatch.
ERROR MODEL: N/A (void handlers; error reporting is external to these stubs).
DETERMINISM: N/A (tooling/UI layer).
VERSIONING / ABI / DATA FORMAT NOTES: Signatures are generated from UI action schemas; keep in sync with generated tables.
EXTENSION POINTS: Implement handler bodies in the user source file; regenerate stubs via the UI tool pipeline.
*/
/* User action stubs. */
#ifndef UI_TOOL_EDITOR_ACTIONS_USER_H_INCLUDED
#define UI_TOOL_EDITOR_ACTIONS_USER_H_INCLUDED

#include "dui/domui_event.h"

#ifdef __cplusplus
extern "C" {
#endif

// BEGIN AUTO-GENERATED ACTION STUBS
void ui_tool_editor_act_TOOL_EDITOR_QUIT(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_ADD_WIDGET(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_DELETE_WIDGET(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_HIERARCHY_SELECT(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_NEW(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_OPEN(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_PROP_H(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_PROP_NAME(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_PROP_W(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_PROP_X(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_PROP_Y(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_SAVE(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_SAVE_AS(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_TAB_CHANGE(void* user_ctx, const domui_event* e);
void ui_tool_editor_act_TOOL_EDITOR_VALIDATE(void* user_ctx, const domui_event* e);
// END AUTO-GENERATED ACTION STUBS

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* UI_TOOL_EDITOR_ACTIONS_USER_H_INCLUDED */
