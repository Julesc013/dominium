/* Auto-generated; do not edit. */
#include "ui_launcher_ui_actions_gen.h"
#include "ui_launcher_ui_actions_user.h"
#include <cstring>

typedef struct domui_action_key_entry {
    const char* key;
    domui_action_id id;
} domui_action_key_entry;

static const domui_action_entry g_actions[] = {
    { DOMUI_ACT_LAUNCHER_INSTANCES_DELETE_SELECTED, ui_launcher_ui_act_LAUNCHER_INSTANCES_DELETE_SELECTED, "tools.launcher.instances.delete_selected" },
    { DOMUI_ACT_LAUNCHER_INSTANCES_EDIT_SELECTED, ui_launcher_ui_act_LAUNCHER_INSTANCES_EDIT_SELECTED, "tools.launcher.instances.edit_selected" },
    { DOMUI_ACT_LAUNCHER_INSTANCES_PLAY_SELECTED, ui_launcher_ui_act_LAUNCHER_INSTANCES_PLAY_SELECTED, "tools.launcher.instances.play_selected" },
    { DOMUI_ACT_LAUNCHER_INSTANCES_SELECT, ui_launcher_ui_act_LAUNCHER_INSTANCES_SELECT, "tools.launcher.instances.select" },
    { DOMUI_ACT_LAUNCHER_NAV_INSTANCES, ui_launcher_ui_act_LAUNCHER_NAV_INSTANCES, "tools.launcher.nav.instances" },
    { DOMUI_ACT_LAUNCHER_NAV_MODS, ui_launcher_ui_act_LAUNCHER_NAV_MODS, "tools.launcher.nav.mods" },
    { DOMUI_ACT_LAUNCHER_NAV_PLAY, ui_launcher_ui_act_LAUNCHER_NAV_PLAY, "tools.launcher.nav.play" },
    { DOMUI_ACT_LAUNCHER_NAV_SETTINGS, ui_launcher_ui_act_LAUNCHER_NAV_SETTINGS, "tools.launcher.nav.settings" },
    { DOMUI_ACT_LAUNCHER_SETTINGS_APPLY, ui_launcher_ui_act_LAUNCHER_SETTINGS_APPLY, "tools.launcher.settings.apply" }
};
static const domui_u32 g_action_count = 9u;

static const domui_action_key_entry g_action_keys[] = {
    { "tools.launcher.instances.delete_selected", DOMUI_ACT_LAUNCHER_INSTANCES_DELETE_SELECTED },
    { "tools.launcher.instances.edit_selected", DOMUI_ACT_LAUNCHER_INSTANCES_EDIT_SELECTED },
    { "tools.launcher.instances.play_selected", DOMUI_ACT_LAUNCHER_INSTANCES_PLAY_SELECTED },
    { "tools.launcher.instances.select", DOMUI_ACT_LAUNCHER_INSTANCES_SELECT },
    { "tools.launcher.nav.instances", DOMUI_ACT_LAUNCHER_NAV_INSTANCES },
    { "tools.launcher.nav.mods", DOMUI_ACT_LAUNCHER_NAV_MODS },
    { "tools.launcher.nav.play", DOMUI_ACT_LAUNCHER_NAV_PLAY },
    { "tools.launcher.nav.settings", DOMUI_ACT_LAUNCHER_NAV_SETTINGS },
    { "tools.launcher.settings.apply", DOMUI_ACT_LAUNCHER_SETTINGS_APPLY }
};
static const domui_u32 g_action_key_count = 9u;

const domui_action_entry* ui_launcher_ui_get_action_table(domui_u32* out_count)
{
    if (out_count) {
        *out_count = g_action_count;
    }
    return g_actions;
}

static domui_action_fn ui_launcher_ui_action_fn_from_id(domui_action_id id)
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

domui_action_id ui_launcher_ui_action_id_from_key(const char* key, domui_u32 len)
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

void ui_launcher_ui_dispatch(void* user_ctx, const domui_event* e)
{
    domui_action_fn fn;
    if (!e) {
        return;
    }
    fn = ui_launcher_ui_action_fn_from_id(e->action_id);
    if (fn) {
        fn(user_ctx, e);
    }
}
