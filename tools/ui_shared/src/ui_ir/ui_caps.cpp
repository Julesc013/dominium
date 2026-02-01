/*
FILE: source/domino/ui_ir/ui_caps.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir caps
RESPONSIBILITY: Backend/tier capability registry and defaults.
*/
#include "ui_caps.h"

static std::vector<domui_backend_caps> g_backend_caps;
static int g_defaults_registered = 0;

static bool domui_list_contains(const domui_string_list& list, const domui_string& key)
{
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (domui_string_equal(list[i], key)) {
            return true;
        }
    }
    return false;
}

static bool domui_list_contains_cstr(const domui_string_list& list, const char* key)
{
    return domui_list_contains(list, domui_string(key ? key : ""));
}

void domui_register_backend_caps(const domui_backend_caps& caps)
{
    size_t i;
    for (i = 0u; i < g_backend_caps.size(); ++i) {
        if (domui_string_equal(g_backend_caps[i].backend_id, caps.backend_id)) {
            g_backend_caps[i] = caps;
            return;
        }
    }
    g_backend_caps.push_back(caps);
}

const domui_backend_caps* domui_get_backend_caps(const domui_backend_id& backend_id)
{
    size_t i;
    for (i = 0u; i < g_backend_caps.size(); ++i) {
        if (domui_string_equal(g_backend_caps[i].backend_id, backend_id)) {
            return &g_backend_caps[i];
        }
    }
    return 0;
}

const domui_backend_caps* domui_get_backend_caps_cstr(const char* backend_id)
{
    return domui_get_backend_caps(domui_backend_id(backend_id ? backend_id : ""));
}

const domui_tier_caps* domui_get_tier_caps(const domui_backend_caps* backend, const domui_tier_id& tier_id)
{
    size_t i;
    if (!backend) {
        return 0;
    }
    for (i = 0u; i < backend->tier_caps.size(); ++i) {
        if (domui_string_equal(backend->tier_caps[i].tier_id, tier_id)) {
            return &backend->tier_caps[i];
        }
    }
    return 0;
}

const domui_tier_caps* domui_find_tier_caps(const domui_tier_id& tier_id, const domui_backend_caps** out_backend)
{
    size_t i;
    if (out_backend) {
        *out_backend = 0;
    }
    for (i = 0u; i < g_backend_caps.size(); ++i) {
        const domui_tier_caps* tier = domui_get_tier_caps(&g_backend_caps[i], tier_id);
        if (tier) {
            if (out_backend) {
                *out_backend = &g_backend_caps[i];
            }
            return tier;
        }
    }
    return 0;
}

int domui_backend_tier_index(const domui_backend_caps* backend, const domui_tier_id& tier_id)
{
    size_t i;
    if (!backend) {
        return -1;
    }
    for (i = 0u; i < backend->tiers.size(); ++i) {
        if (domui_string_equal(backend->tiers[i], tier_id)) {
            return (int)i;
        }
    }
    return -1;
}

const domui_tier_caps* domui_get_highest_tier_caps(const domui_backend_caps* backend)
{
    int i;
    if (!backend) {
        return 0;
    }
    for (i = (int)backend->tiers.size() - 1; i >= 0; --i) {
        const domui_tier_caps* tier = domui_get_tier_caps(backend, backend->tiers[(size_t)i]);
        if (tier) {
            return tier;
        }
    }
    if (!backend->tier_caps.empty()) {
        return &backend->tier_caps[backend->tier_caps.size() - 1u];
    }
    return 0;
}

const domui_widget_cap* domui_find_widget_cap(const domui_tier_caps* tier, domui_widget_type type)
{
    size_t i;
    if (!tier) {
        return 0;
    }
    for (i = 0u; i < tier->widgets.size(); ++i) {
        if (tier->widgets[i].type == type) {
            return &tier->widgets[i];
        }
    }
    return 0;
}

bool domui_tier_supports_widget(const domui_tier_caps* tier, domui_widget_type type)
{
    return domui_find_widget_cap(tier, type) != 0;
}

bool domui_tier_supports_prop(const domui_tier_caps* tier, domui_widget_type type, const domui_string& prop_key)
{
    {
        const std::string& key = prop_key.str();
        const char* prefix = "accessibility.";
        const size_t prefix_len = 14u;
        if (key.size() >= prefix_len && key.compare(0, prefix_len, prefix) == 0) {
            return true;
        }
    }
    const domui_widget_cap* cap = domui_find_widget_cap(tier, type);
    if (!cap) {
        return false;
    }
    if (cap->props.empty()) {
        return false;
    }
    if (domui_list_contains_cstr(cap->props, "*")) {
        return true;
    }
    return domui_list_contains(cap->props, prop_key);
}

bool domui_tier_supports_event(const domui_tier_caps* tier, domui_widget_type type, const domui_string& event_name)
{
    const domui_widget_cap* cap = domui_find_widget_cap(tier, type);
    if (!cap) {
        return false;
    }
    if (cap->events.empty()) {
        return false;
    }
    if (domui_list_contains_cstr(cap->events, "*")) {
        return true;
    }
    return domui_list_contains(cap->events, event_name);
}

const domui_feature_entry* domui_tier_find_feature(const domui_tier_caps* tier, const domui_cap_feature& feature_key)
{
    size_t i;
    if (!tier) {
        return 0;
    }
    for (i = 0u; i < tier->features.size(); ++i) {
        if (domui_string_equal(tier->features[i].key, feature_key)) {
            return &tier->features[i];
        }
    }
    return 0;
}

bool domui_tier_has_feature(const domui_tier_caps* tier, const domui_cap_feature& feature_key)
{
    return domui_tier_find_feature(tier, feature_key) != 0;
}

bool domui_tier_limit_value(const domui_tier_caps* tier, const domui_string& limit_key, int* out_value)
{
    size_t i;
    if (out_value) {
        *out_value = 0;
    }
    if (!tier) {
        return false;
    }
    for (i = 0u; i < tier->limits.size(); ++i) {
        if (domui_string_equal(tier->limits[i].key, limit_key)) {
            if (out_value) {
                *out_value = tier->limits[i].value;
            }
            return true;
        }
    }
    return false;
}

static domui_widget_cap domui_make_widget_cap(domui_widget_type type,
                                              const char** props,
                                              size_t prop_count,
                                              const char** events,
                                              size_t event_count)
{
    domui_widget_cap cap;
    size_t i;
    cap.type = type;
    for (i = 0u; i < prop_count; ++i) {
        cap.props.push_back(domui_string(props[i]));
    }
    for (i = 0u; i < event_count; ++i) {
        cap.events.push_back(domui_string(events[i]));
    }
    return cap;
}

static void domui_add_feature(domui_tier_caps& tier, const char* key, int emulated)
{
    domui_feature_entry entry;
    entry.key.set(key);
    entry.emulated = emulated;
    tier.features.push_back(entry);
}

static domui_backend_caps domui_build_win32_caps(void)
{
    domui_backend_caps backend;
    domui_tier_caps t0;
    domui_tier_caps t1;

    static const char* props_text[] = { "text" };
    static const char* props_text_checked[] = { "text", "checked" };
    static const char* props_value[] = { "value" };
    static const char* props_items[] = { "items", "selected_index" };
    static const char* props_tab[] = { "tab.labels", "selected_index" };
    static const char* props_tree[] = { "tree.items", "selected_id" };
    static const char* props_listview_t0[] = { "items", "selected_index" };
    static const char* props_listview_t1[] = { "items", "selected_index", "listview.columns" };
    static const char* props_minmaxvalue[] = { "min", "max", "value" };
    static const char* props_image[] = { "image" };
    static const char* props_splitter[] = { "splitter.orientation", "splitter.pos", "splitter.thickness", "splitter.min_a", "splitter.min_b" };
    static const char* props_tabs[] = { "tabs.selected_index", "tabs.placement" };
    static const char* props_tab_page[] = { "tab.title", "tab.enabled" };
    static const char* props_scrollpanel[] = { "scroll.h_enabled", "scroll.v_enabled", "scroll.x", "scroll.y" };

    static const char* ev_click[] = { "on_click" };
    static const char* ev_change[] = { "on_change" };
    static const char* ev_submit[] = { "on_submit" };
    static const char* ev_change_submit[] = { "on_change", "on_submit" };
    static const char* ev_tab_change[] = { "on_tab_change" };

    backend.backend_id.set("win32");
    backend.tiers.push_back(domui_string("win32_t0"));
    backend.tiers.push_back(domui_string("win32_t1"));

    t0.tier_id.set("win32_t0");
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_CONTAINER, 0, 0u, 0, 0u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_STATIC_TEXT, props_text, 1u, 0, 0u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_BUTTON, props_text, 1u, ev_click, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_EDIT, props_value, 1u, ev_change_submit, 2u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_LISTBOX, props_items, 2u, ev_change, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_COMBOBOX, props_items, 2u, ev_change, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_CHECKBOX, props_text_checked, 2u, ev_change, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_RADIO, props_text_checked, 2u, ev_change, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_TAB, props_tab, 2u, ev_change, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_TREEVIEW, props_tree, 2u, ev_change, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_LISTVIEW, props_listview_t0, 2u, ev_change, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_PROGRESS, props_minmaxvalue, 3u, 0, 0u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_SLIDER, props_minmaxvalue, 3u, ev_change, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_GROUPBOX, props_text, 1u, 0, 0u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_IMAGE, props_image, 1u, 0, 0u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_SPLITTER, props_splitter, 5u, ev_change, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_SCROLLPANEL, props_scrollpanel, 4u, 0, 0u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_TABS, props_tabs, 2u, ev_tab_change, 1u));
    t0.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_TAB_PAGE, props_tab_page, 2u, 0, 0u));

    t1.tier_id.set("win32_t1");
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_CONTAINER, 0, 0u, 0, 0u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_STATIC_TEXT, props_text, 1u, 0, 0u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_BUTTON, props_text, 1u, ev_click, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_EDIT, props_value, 1u, ev_change_submit, 2u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_LISTBOX, props_items, 2u, ev_change, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_COMBOBOX, props_items, 2u, ev_change, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_CHECKBOX, props_text_checked, 2u, ev_change, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_RADIO, props_text_checked, 2u, ev_change, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_TAB, props_tab, 2u, ev_change, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_TREEVIEW, props_tree, 2u, ev_change, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_LISTVIEW, props_listview_t1, 3u, ev_change, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_PROGRESS, props_minmaxvalue, 3u, 0, 0u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_SLIDER, props_minmaxvalue, 3u, ev_change, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_GROUPBOX, props_text, 1u, 0, 0u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_IMAGE, props_image, 1u, 0, 0u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_SPLITTER, props_splitter, 5u, ev_change, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_SCROLLPANEL, props_scrollpanel, 4u, 0, 0u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_TABS, props_tabs, 2u, ev_tab_change, 1u));
    t1.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_TAB_PAGE, props_tab_page, 2u, 0, 0u));

    domui_add_feature(t1, "widget.listview.columns", 0);
    domui_add_feature(t0, "widget.splitter", 1);
    domui_add_feature(t1, "widget.splitter", 1);

    backend.tier_caps.push_back(t0);
    backend.tier_caps.push_back(t1);
    return backend;
}

static domui_backend_caps domui_build_dgfx_caps(void)
{
    domui_backend_caps backend;
    domui_tier_caps tier;

    static const char* props_text[] = { "text" };
    static const char* props_text_checked[] = { "text", "checked" };
    static const char* props_value[] = { "value" };
    static const char* props_items[] = { "items", "selected_index" };
    static const char* props_minmaxvalue[] = { "min", "max", "value" };

    static const char* ev_click[] = { "on_click" };
    static const char* ev_change[] = { "on_change" };
    static const char* ev_change_submit[] = { "on_change", "on_submit" };

    backend.backend_id.set("dgfx");
    backend.tiers.push_back(domui_string("dgfx_basic"));

    tier.tier_id.set("dgfx_basic");
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_CONTAINER, 0, 0u, 0, 0u));
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_STATIC_TEXT, props_text, 1u, 0, 0u));
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_BUTTON, props_text, 1u, ev_click, 1u));
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_EDIT, props_value, 1u, ev_change_submit, 2u));
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_LISTBOX, props_items, 2u, ev_change, 1u));
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_CHECKBOX, props_text_checked, 2u, ev_change, 1u));
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_RADIO, props_text_checked, 2u, ev_change, 1u));
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_PROGRESS, props_minmaxvalue, 3u, 0, 0u));
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_SLIDER, props_minmaxvalue, 3u, ev_change, 1u));

    domui_add_feature(tier, "widget.image", 1);

    backend.tier_caps.push_back(tier);
    return backend;
}

static domui_backend_caps domui_build_null_caps(void)
{
    domui_backend_caps backend;
    domui_tier_caps tier;

    static const char* props_text[] = { "text" };

    backend.backend_id.set("null");
    backend.tiers.push_back(domui_string("null_basic"));

    tier.tier_id.set("null_basic");
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_CONTAINER, 0, 0u, 0, 0u));
    tier.widgets.push_back(domui_make_widget_cap(DOMUI_WIDGET_STATIC_TEXT, props_text, 1u, 0, 0u));

    backend.tier_caps.push_back(tier);
    return backend;
}

void domui_register_default_backend_caps(void)
{
    if (g_defaults_registered) {
        return;
    }
    g_defaults_registered = 1;
    domui_register_backend_caps(domui_build_win32_caps());
    domui_register_backend_caps(domui_build_dgfx_caps());
    domui_register_backend_caps(domui_build_null_caps());
}
