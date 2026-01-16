/*
FILE: source/domino/ui_ir/ui_validate.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir validate
RESPONSIBILITY: Validate UI IR documents against backend/tier capabilities.
*/
#include "ui_validate.h"

#include <algorithm>

typedef struct domui_validation_issue {
    int severity; /* 0 = error, 1 = warning */
    domui_widget_id widget_id;
    domui_string feature_key;
    domui_string message;
} domui_validation_issue;

struct domui_issue_less {
    bool operator()(const domui_validation_issue& a, const domui_validation_issue& b) const
    {
        if (a.severity != b.severity) {
            return a.severity < b.severity;
        }
        if (a.widget_id != b.widget_id) {
            return a.widget_id < b.widget_id;
        }
        {
            int cmp = domui_string_compare(a.feature_key, b.feature_key);
            if (cmp != 0) {
                return cmp < 0;
            }
        }
        return domui_string_compare(a.message, b.message) < 0;
    }
};

static bool domui_string_list_has(const domui_string_list& list, const domui_string& key)
{
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (domui_string_equal(list[i], key)) {
            return true;
        }
    }
    return false;
}

static void domui_add_unique(domui_string_list& list, const domui_string& key)
{
    if (!domui_string_list_has(list, key)) {
        list.push_back(key);
    }
}

static const char* domui_widget_type_name(domui_widget_type t)
{
    switch (t) {
    case DOMUI_WIDGET_CONTAINER: return "CONTAINER";
    case DOMUI_WIDGET_STATIC_TEXT: return "STATIC_TEXT";
    case DOMUI_WIDGET_BUTTON: return "BUTTON";
    case DOMUI_WIDGET_EDIT: return "EDIT";
    case DOMUI_WIDGET_LISTBOX: return "LISTBOX";
    case DOMUI_WIDGET_COMBOBOX: return "COMBOBOX";
    case DOMUI_WIDGET_CHECKBOX: return "CHECKBOX";
    case DOMUI_WIDGET_RADIO: return "RADIO";
    case DOMUI_WIDGET_TAB: return "TAB";
    case DOMUI_WIDGET_TREEVIEW: return "TREEVIEW";
    case DOMUI_WIDGET_LISTVIEW: return "LISTVIEW";
    case DOMUI_WIDGET_PROGRESS: return "PROGRESS";
    case DOMUI_WIDGET_SLIDER: return "SLIDER";
    case DOMUI_WIDGET_GROUPBOX: return "GROUPBOX";
    case DOMUI_WIDGET_IMAGE: return "IMAGE";
    case DOMUI_WIDGET_SPLITTER: return "SPLITTER";
    case DOMUI_WIDGET_SCROLLPANEL: return "SCROLLPANEL";
    case DOMUI_WIDGET_TABS: return "TABS";
    case DOMUI_WIDGET_TAB_PAGE: return "TAB_PAGE";
    default:
        break;
    }
    return "UNKNOWN";
}

static void domui_widget_feature_key(domui_widget_type t, domui_string& out_key)
{
    const char* suffix = "unknown";
    switch (t) {
    case DOMUI_WIDGET_CONTAINER: suffix = "container"; break;
    case DOMUI_WIDGET_STATIC_TEXT: suffix = "static_text"; break;
    case DOMUI_WIDGET_BUTTON: suffix = "button"; break;
    case DOMUI_WIDGET_EDIT: suffix = "edit"; break;
    case DOMUI_WIDGET_LISTBOX: suffix = "listbox"; break;
    case DOMUI_WIDGET_COMBOBOX: suffix = "combobox"; break;
    case DOMUI_WIDGET_CHECKBOX: suffix = "checkbox"; break;
    case DOMUI_WIDGET_RADIO: suffix = "radio"; break;
    case DOMUI_WIDGET_TAB: suffix = "tab"; break;
    case DOMUI_WIDGET_TREEVIEW: suffix = "treeview"; break;
    case DOMUI_WIDGET_LISTVIEW: suffix = "listview"; break;
    case DOMUI_WIDGET_PROGRESS: suffix = "progress"; break;
    case DOMUI_WIDGET_SLIDER: suffix = "slider"; break;
    case DOMUI_WIDGET_GROUPBOX: suffix = "groupbox"; break;
    case DOMUI_WIDGET_IMAGE: suffix = "image"; break;
    case DOMUI_WIDGET_SPLITTER: suffix = "splitter"; break;
    case DOMUI_WIDGET_SCROLLPANEL: suffix = "scrollpanel"; break;
    case DOMUI_WIDGET_TABS: suffix = "tabs"; break;
    case DOMUI_WIDGET_TAB_PAGE: suffix = "tab_page"; break;
    default:
        break;
    }
    {
        std::string key = "widget.";
        key += suffix;
        out_key.set(key.c_str());
    }
}

static bool domui_feature_for_property(domui_widget_type type, const domui_string& prop_key, domui_string& out_key)
{
    if (type == DOMUI_WIDGET_LISTVIEW && domui_string_equal(prop_key, domui_string("listview.columns"))) {
        out_key.set("widget.listview.columns");
        return true;
    }
    return false;
}

static void domui_add_issue(std::vector<domui_validation_issue>& issues,
                            int severity,
                            domui_widget_id widget_id,
                            const domui_string& feature_key,
                            const domui_string& message)
{
    domui_validation_issue issue;
    issue.severity = severity;
    issue.widget_id = widget_id;
    issue.feature_key = feature_key;
    issue.message = message;
    issues.push_back(issue);
}

static void domui_sort_issues(std::vector<domui_validation_issue>& issues)
{
    std::sort(issues.begin(), issues.end(), domui_issue_less());
}

static void domui_target_set_from_doc(const domui_doc* doc, domui_target_set& out)
{
    out.backends = doc->meta.target_backends;
    out.tiers = doc->meta.target_tiers;
}

static void domui_default_targets(domui_target_set& targets)
{
    if (targets.backends.empty()) {
        targets.backends.push_back(domui_string("win32"));
    }
}

typedef struct domui_backend_target {
    domui_backend_id backend_id;
    domui_string_list tiers;
} domui_backend_target;

static domui_backend_target* domui_find_backend_target(std::vector<domui_backend_target>& list,
                                                       const domui_backend_id& backend_id)
{
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (domui_string_equal(list[i].backend_id, backend_id)) {
            return &list[i];
        }
    }
    return 0;
}

static void domui_add_backend_target(std::vector<domui_backend_target>& list, const domui_backend_id& backend_id)
{
    if (!domui_find_backend_target(list, backend_id)) {
        domui_backend_target entry;
        entry.backend_id = backend_id;
        list.push_back(entry);
    }
}

static void domui_resolve_targets(const domui_target_set& targets,
                                  std::vector<domui_backend_target>& out_targets,
                                  std::vector<domui_validation_issue>& issues)
{
    size_t i;
    out_targets.clear();

    for (i = 0u; i < targets.backends.size(); ++i) {
        domui_add_backend_target(out_targets, targets.backends[i]);
    }

    for (i = 0u; i < targets.tiers.size(); ++i) {
        const domui_backend_caps* backend = 0;
        const domui_tier_caps* tier = domui_find_tier_caps(targets.tiers[i], &backend);
        if (!tier || !backend) {
            std::string msg = "validate: unknown target tier '";
            msg += targets.tiers[i].c_str();
            msg += "'";
            domui_add_issue(issues, 0, 0u, targets.tiers[i], domui_string(msg));
            continue;
        }
        domui_add_backend_target(out_targets, backend->backend_id);
        {
            domui_backend_target* bt = domui_find_backend_target(out_targets, backend->backend_id);
            if (bt) {
                domui_add_unique(bt->tiers, tier->tier_id);
            }
        }
    }
}

static void domui_add_issue_unknown_backend(std::vector<domui_validation_issue>& issues,
                                            const domui_backend_id& backend_id)
{
    std::string msg = "validate: unknown backend '";
    msg += backend_id.c_str();
    msg += "'";
    domui_add_issue(issues, 0, 0u, backend_id, domui_string(msg));
}

static void domui_add_issue_unknown_required_tier(std::vector<domui_validation_issue>& issues,
                                                  const domui_tier_id& tier_id)
{
    std::string msg = "validate: unknown required tier '";
    msg += tier_id.c_str();
    msg += "'";
    domui_add_issue(issues, 0, 0u, tier_id, domui_string(msg));
}

static void domui_add_issue_tier_mismatch(std::vector<domui_validation_issue>& issues,
                                          const domui_backend_id& backend_id,
                                          const domui_tier_id& target_tier,
                                          const domui_tier_id& required_tier)
{
    std::string msg = "validate: target tier '";
    msg += target_tier.c_str();
    msg += "' lower than required '";
    msg += required_tier.c_str();
    msg += "' for backend '";
    msg += backend_id.c_str();
    msg += "'";
    domui_add_issue(issues, 0, 0u, target_tier, domui_string(msg));
}

static void domui_add_issue_tier_unsupported(std::vector<domui_validation_issue>& issues,
                                             const domui_backend_id& backend_id,
                                             const domui_tier_id& tier_id)
{
    std::string msg = "validate: tier '";
    msg += tier_id.c_str();
    msg += "' not supported by backend '";
    msg += backend_id.c_str();
    msg += "'";
    domui_add_issue(issues, 0, 0u, tier_id, domui_string(msg));
}

static void domui_add_issue_missing_tier(std::vector<domui_validation_issue>& issues,
                                         const domui_backend_id& backend_id)
{
    std::string msg = "validate: no target tier for backend '";
    msg += backend_id.c_str();
    msg += "'";
    domui_add_issue(issues, 0, 0u, backend_id, domui_string(msg));
}

bool domui_validate_doc(const domui_doc* doc, const domui_target_set* targets, domui_diag* out_diag)
{
    std::vector<domui_validation_issue> issues;
    std::vector<domui_backend_target> backend_targets;
    domui_target_set effective_targets;
    size_t i;

    if (!doc) {
        return false;
    }
    if (out_diag) {
        out_diag->clear();
    }

    domui_register_default_backend_caps();

    effective_targets.backends.clear();
    effective_targets.tiers.clear();

    if (targets && (!targets->backends.empty() || !targets->tiers.empty())) {
        effective_targets = *targets;
    } else {
        domui_target_set_from_doc(doc, effective_targets);
    }

    if (effective_targets.backends.empty() && !effective_targets.tiers.empty()) {
        for (i = 0u; i < effective_targets.tiers.size(); ++i) {
            const domui_backend_caps* backend = 0;
            if (domui_find_tier_caps(effective_targets.tiers[i], &backend) && backend) {
                domui_add_unique(effective_targets.backends, backend->backend_id);
            }
        }
    }

    domui_default_targets(effective_targets);

    domui_resolve_targets(effective_targets, backend_targets, issues);

    for (i = 0u; i < backend_targets.size(); ++i) {
        const domui_backend_caps* backend = domui_get_backend_caps(backend_targets[i].backend_id);
        size_t t;
        if (!backend) {
            domui_add_issue_unknown_backend(issues, backend_targets[i].backend_id);
            continue;
        }

        if (backend_targets[i].tiers.empty()) {
            if (!effective_targets.tiers.empty()) {
                domui_add_issue_missing_tier(issues, backend->backend_id);
            } else {
                const domui_tier_caps* highest = domui_get_highest_tier_caps(backend);
                if (highest) {
                    backend_targets[i].tiers.push_back(highest->tier_id);
                } else {
                    domui_add_issue_missing_tier(issues, backend->backend_id);
                }
            }
        }

        for (t = 0u; t < backend_targets[i].tiers.size(); ++t) {
            if (domui_backend_tier_index(backend, backend_targets[i].tiers[t]) < 0) {
                domui_add_issue_tier_unsupported(issues, backend->backend_id, backend_targets[i].tiers[t]);
            }
        }
    }

    /* Required tier checks (from doc metadata). */
    if (!doc->meta.target_tiers.empty()) {
        for (i = 0u; i < backend_targets.size(); ++i) {
            const domui_backend_caps* backend = domui_get_backend_caps(backend_targets[i].backend_id);
            int required_index = -1;
            domui_tier_id required_tier;
            size_t r;

            if (!backend) {
                continue;
            }

            for (r = 0u; r < doc->meta.target_tiers.size(); ++r) {
                const domui_backend_caps* req_backend = 0;
                const domui_tier_caps* req_tier = domui_find_tier_caps(doc->meta.target_tiers[r], &req_backend);
                if (!req_tier || !req_backend) {
                    domui_add_issue_unknown_required_tier(issues, doc->meta.target_tiers[r]);
                    continue;
                }
                if (!domui_string_equal(req_backend->backend_id, backend->backend_id)) {
                    continue;
                }
                {
                    int idx = domui_backend_tier_index(backend, req_tier->tier_id);
                    if (idx >= 0 && idx > required_index) {
                        required_index = idx;
                        required_tier = req_tier->tier_id;
                    }
                }
            }

            if (required_index >= 0) {
                size_t t;
                for (t = 0u; t < backend_targets[i].tiers.size(); ++t) {
                    int idx = domui_backend_tier_index(backend, backend_targets[i].tiers[t]);
                    if (idx >= 0 && idx < required_index) {
                        domui_add_issue_tier_mismatch(issues,
                                                      backend->backend_id,
                                                      backend_targets[i].tiers[t],
                                                      required_tier);
                    }
                }
            }
        }
    }

    /* Validate widgets against targets. */
    for (i = 0u; i < backend_targets.size(); ++i) {
        const domui_backend_caps* backend = domui_get_backend_caps(backend_targets[i].backend_id);
        size_t t;
        if (!backend) {
            continue;
        }
        for (t = 0u; t < backend_targets[i].tiers.size(); ++t) {
            const domui_tier_caps* tier = domui_get_tier_caps(backend, backend_targets[i].tiers[t]);
            std::vector<domui_widget_id> widget_order;
            size_t widx;

            if (!tier) {
                continue;
            }

            doc->canonical_widget_order(widget_order);
            for (widx = 0u; widx < widget_order.size(); ++widx) {
                const domui_widget* w = doc->find_by_id(widget_order[widx]);
                domui_string feature_key;
                if (!w) {
                    continue;
                }

                if (!domui_tier_supports_widget(tier, w->type)) {
                    std::string msg = "validate: widget type '";
                    msg += domui_widget_type_name(w->type);
                    msg += "' unsupported for backend '";
                    msg += backend->backend_id.c_str();
                    msg += "/";
                    msg += tier->tier_id.c_str();
                    msg += "'";
                    domui_widget_feature_key(w->type, feature_key);
                    domui_add_issue(issues, 0, w->id, feature_key, domui_string(msg));
                    continue;
                }

                {
                    size_t p;
                    const domui_props::list_type& props = w->props.entries();
                    for (p = 0u; p < props.size(); ++p) {
                        if (!domui_tier_supports_prop(tier, w->type, props[p].key)) {
                            std::string msg = "validate: property '";
                            msg += props[p].key.c_str();
                            msg += "' unsupported for widget '";
                            msg += domui_widget_type_name(w->type);
                            msg += "' on backend '";
                            msg += backend->backend_id.c_str();
                            msg += "/";
                            msg += tier->tier_id.c_str();
                            msg += "'";
                            domui_add_issue(issues, 0, w->id, props[p].key, domui_string(msg));
                        }
                        {
                            domui_string prop_feature;
                            if (domui_feature_for_property(w->type, props[p].key, prop_feature)) {
                                const domui_feature_entry* feat = domui_tier_find_feature(tier, prop_feature);
                                if (feat && feat->emulated) {
                                    std::string msg = "validate: feature '";
                                    msg += prop_feature.c_str();
                                    msg += "' emulated on backend '";
                                    msg += backend->backend_id.c_str();
                                    msg += "/";
                                    msg += tier->tier_id.c_str();
                                    msg += "'";
                                    domui_add_issue(issues, 1, w->id, prop_feature, domui_string(msg));
                                }
                            }
                        }
                    }
                }

                {
                    size_t e;
                    const domui_events::list_type& events = w->events.entries();
                    for (e = 0u; e < events.size(); ++e) {
                        if (!domui_tier_supports_event(tier, w->type, events[e].event_name)) {
                            std::string msg = "validate: event '";
                            msg += events[e].event_name.c_str();
                            msg += "' unsupported for widget '";
                            msg += domui_widget_type_name(w->type);
                            msg += "' on backend '";
                            msg += backend->backend_id.c_str();
                            msg += "/";
                            msg += tier->tier_id.c_str();
                            msg += "'";
                            domui_add_issue(issues, 0, w->id, events[e].event_name, domui_string(msg));
                        }
                    }
                }

                {
                    domui_string widget_feature;
                    domui_widget_feature_key(w->type, widget_feature);
                    {
                        const domui_feature_entry* feat = domui_tier_find_feature(tier, widget_feature);
                        if (feat && feat->emulated) {
                            std::string msg = "validate: feature '";
                            msg += widget_feature.c_str();
                            msg += "' emulated on backend '";
                            msg += backend->backend_id.c_str();
                            msg += "/";
                            msg += tier->tier_id.c_str();
                            msg += "'";
                            domui_add_issue(issues, 1, w->id, widget_feature, domui_string(msg));
                        }
                    }
                }
            }
        }
    }

    domui_sort_issues(issues);

    if (out_diag) {
        size_t j;
        for (j = 0u; j < issues.size(); ++j) {
            if (issues[j].severity == 0) {
                out_diag->add_error(issues[j].message, issues[j].widget_id, issues[j].feature_key);
            } else {
                out_diag->add_warning(issues[j].message, issues[j].widget_id, issues[j].feature_key);
            }
        }
    }

    {
        size_t j;
        for (j = 0u; j < issues.size(); ++j) {
            if (issues[j].severity == 0) {
                return false;
            }
        }
    }
    return true;
}
