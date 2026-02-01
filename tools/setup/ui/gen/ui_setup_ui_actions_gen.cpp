/* Auto-generated; do not edit. */
#include "ui_setup_ui_actions_gen.h"
#include "ui_setup_ui_actions_user.h"
#include <cstring>

typedef struct domui_action_key_entry {
    const char* key;
    domui_action_id id;
} domui_action_key_entry;

static const domui_action_entry g_actions[] = {
    { DOMUI_ACT_SETUP_BROWSE_PATH, ui_setup_ui_act_SETUP_BROWSE_PATH, "tools.setup.browse_path" },
    { DOMUI_ACT_SETUP_NAV_BACK, ui_setup_ui_act_SETUP_NAV_BACK, "tools.setup.nav.back" },
    { DOMUI_ACT_SETUP_NAV_CANCEL, ui_setup_ui_act_SETUP_NAV_CANCEL, "tools.setup.nav.cancel" },
    { DOMUI_ACT_SETUP_NAV_FINISH, ui_setup_ui_act_SETUP_NAV_FINISH, "tools.setup.nav.finish" },
    { DOMUI_ACT_SETUP_NAV_INSTALL, ui_setup_ui_act_SETUP_NAV_INSTALL, "tools.setup.nav.install" },
    { DOMUI_ACT_SETUP_NAV_NEXT, ui_setup_ui_act_SETUP_NAV_NEXT, "tools.setup.nav.next" },
    { DOMUI_ACT_SETUP_OPTIONS_CHANGED, ui_setup_ui_act_SETUP_OPTIONS_CHANGED, "tools.setup.options.changed" }
};
static const domui_u32 g_action_count = 7u;

static const domui_action_key_entry g_action_keys[] = {
    { "tools.setup.browse_path", DOMUI_ACT_SETUP_BROWSE_PATH },
    { "tools.setup.nav.back", DOMUI_ACT_SETUP_NAV_BACK },
    { "tools.setup.nav.cancel", DOMUI_ACT_SETUP_NAV_CANCEL },
    { "tools.setup.nav.finish", DOMUI_ACT_SETUP_NAV_FINISH },
    { "tools.setup.nav.install", DOMUI_ACT_SETUP_NAV_INSTALL },
    { "tools.setup.nav.next", DOMUI_ACT_SETUP_NAV_NEXT },
    { "tools.setup.options.changed", DOMUI_ACT_SETUP_OPTIONS_CHANGED }
};
static const domui_u32 g_action_key_count = 7u;

const domui_action_entry* ui_setup_ui_get_action_table(domui_u32* out_count)
{
    if (out_count) {
        *out_count = g_action_count;
    }
    return g_actions;
}

static domui_action_fn ui_setup_ui_action_fn_from_id(domui_action_id id)
{
    size_t lo = 0u;
    size_t hi = (size_t)g_action_count;
    while (lo < hi) {
        size_t mid = (lo + hi) / 2u;
        domui_action_id cur = g_actions[mid].action_id;
        if (cur < id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    if (lo < (size_t)g_action_count && g_actions[lo].action_id == id) {
        return g_actions[lo].fn;
    }
    return (domui_action_fn)0;
}

domui_action_id ui_setup_ui_action_id_from_key(const char* key, domui_u32 len)
{
    size_t lo = 0u;
    size_t hi = (size_t)g_action_key_count;
    if (!key) {
        return 0u;
    }
    while (lo < hi) {
        size_t mid = (lo + hi) / 2u;
        const char* cur = g_action_keys[mid].key;
        size_t cur_len = std::strlen(cur);
        size_t min_len = (len < (domui_u32)cur_len) ? (size_t)len : cur_len;
        int cmp = std::strncmp(key, cur, min_len);
        if (cmp == 0) {
            if (len < (domui_u32)cur_len) {
                cmp = -1;
            } else if (len > (domui_u32)cur_len) {
                cmp = 1;
            }
        }
        if (cmp < 0) {
            hi = mid;
        } else if (cmp > 0) {
            lo = mid + 1u;
        } else {
            return g_action_keys[mid].id;
        }
    }
    return 0u;
}

void ui_setup_ui_dispatch(void* user_ctx, const domui_event* e)
{
    domui_action_fn fn;
    if (!e) {
        return;
    }
    fn = ui_setup_ui_action_fn_from_id(e->action_id);
    if (fn) {
        fn(user_ctx, e);
    }
}
