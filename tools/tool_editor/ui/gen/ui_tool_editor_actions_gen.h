/* Auto-generated; do not edit. */
#ifndef UI_TOOL_EDITOR_ACTIONS_GEN_H_INCLUDED
#define UI_TOOL_EDITOR_ACTIONS_GEN_H_INCLUDED

#include "dui/domui_event.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct domui_action_entry {
    domui_action_id action_id;
    domui_action_fn fn;
    const char* key;
} domui_action_entry;

#define DOMUI_ACT_TOOL_EDITOR_ADD_WIDGET 1u
#define DOMUI_ACT_TOOL_EDITOR_DELETE_WIDGET 2u
#define DOMUI_ACT_TOOL_EDITOR_HIERARCHY_SELECT 3u
#define DOMUI_ACT_TOOL_EDITOR_NEW 4u
#define DOMUI_ACT_TOOL_EDITOR_OPEN 5u
#define DOMUI_ACT_TOOL_EDITOR_PROP_H 6u
#define DOMUI_ACT_TOOL_EDITOR_PROP_NAME 7u
#define DOMUI_ACT_TOOL_EDITOR_PROP_W 8u
#define DOMUI_ACT_TOOL_EDITOR_PROP_X 9u
#define DOMUI_ACT_TOOL_EDITOR_PROP_Y 10u
#define DOMUI_ACT_TOOL_EDITOR_SAVE 11u
#define DOMUI_ACT_TOOL_EDITOR_SAVE_AS 12u
#define DOMUI_ACT_TOOL_EDITOR_TAB_CHANGE 13u
#define DOMUI_ACT_TOOL_EDITOR_VALIDATE 14u

const domui_action_entry* ui_tool_editor_get_action_table(domui_u32* out_count);
domui_action_id ui_tool_editor_action_id_from_key(const char* key, domui_u32 len);
void ui_tool_editor_dispatch(void* user_ctx, const domui_event* e);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* UI_TOOL_EDITOR_ACTIONS_GEN_H_INCLUDED */
