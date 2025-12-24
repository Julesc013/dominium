/* Auto-generated; do not edit. */
#ifndef UI_SETUP_UI_ACTIONS_GEN_H_INCLUDED
#define UI_SETUP_UI_ACTIONS_GEN_H_INCLUDED

#include "dui/domui_event.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct domui_action_entry {
    domui_action_id action_id;
    domui_action_fn fn;
    const char* key;
} domui_action_entry;

#define DOMUI_ACT_SETUP_BROWSE_PATH 1u
#define DOMUI_ACT_SETUP_NAV_BACK 2u
#define DOMUI_ACT_SETUP_NAV_CANCEL 3u
#define DOMUI_ACT_SETUP_NAV_FINISH 4u
#define DOMUI_ACT_SETUP_NAV_INSTALL 5u
#define DOMUI_ACT_SETUP_NAV_NEXT 6u
#define DOMUI_ACT_SETUP_OPTIONS_CHANGED 7u

const domui_action_entry* ui_setup_ui_get_action_table(domui_u32* out_count);
domui_action_id ui_setup_ui_action_id_from_key(const char* key, domui_u32 len);
void ui_setup_ui_dispatch(void* user_ctx, const domui_event* e);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* UI_SETUP_UI_ACTIONS_GEN_H_INCLUDED */
