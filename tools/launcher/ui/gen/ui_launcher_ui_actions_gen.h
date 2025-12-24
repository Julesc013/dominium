/* Auto-generated; do not edit. */
#ifndef UI_LAUNCHER_UI_ACTIONS_GEN_H_INCLUDED
#define UI_LAUNCHER_UI_ACTIONS_GEN_H_INCLUDED

#include "dui/domui_event.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct domui_action_entry {
    domui_action_id action_id;
    domui_action_fn fn;
    const char* key;
} domui_action_entry;

#define DOMUI_ACT_LAUNCHER_INSTANCES_DELETE_SELECTED 1u
#define DOMUI_ACT_LAUNCHER_INSTANCES_EDIT_SELECTED 2u
#define DOMUI_ACT_LAUNCHER_INSTANCES_PLAY_SELECTED 3u
#define DOMUI_ACT_LAUNCHER_INSTANCES_SELECT 4u
#define DOMUI_ACT_LAUNCHER_NAV_INSTANCES 5u
#define DOMUI_ACT_LAUNCHER_NAV_MODS 6u
#define DOMUI_ACT_LAUNCHER_NAV_PLAY 7u
#define DOMUI_ACT_LAUNCHER_NAV_SETTINGS 8u
#define DOMUI_ACT_LAUNCHER_SETTINGS_APPLY 9u

const domui_action_entry* ui_launcher_ui_get_action_table(domui_u32* out_count);
domui_action_id ui_launcher_ui_action_id_from_key(const char* key, domui_u32 len);
void ui_launcher_ui_dispatch(void* user_ctx, const domui_event* e);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* UI_LAUNCHER_UI_ACTIONS_GEN_H_INCLUDED */
