/*
FILE: source/dominium/game/runtime/dom_econ_access_control.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/econ_access_control
RESPONSIBILITY: Deterministic access control for economic data visibility.
*/
#include "runtime/dom_econ_access_control.h"

#include <vector>

namespace {

struct AccessEntry {
    u64 actor_id;
    u64 account_id;
    u32 flags;
};

static int find_index(const std::vector<AccessEntry> &list, u64 actor_id, u64 account_id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].actor_id == actor_id && list[i].account_id == account_id) {
            return (int)i;
        }
    }
    return -1;
}

static bool entry_less(const AccessEntry &a, const AccessEntry &b) {
    if (a.actor_id != b.actor_id) {
        return a.actor_id < b.actor_id;
    }
    return a.account_id < b.account_id;
}

static void insert_sorted(std::vector<AccessEntry> &list, const AccessEntry &entry) {
    size_t i = 0u;
    while (i < list.size() && entry_less(list[i], entry)) {
        ++i;
    }
    while (i < list.size() && !entry_less(entry, list[i])) {
        ++i;
    }
    list.insert(list.begin() + (std::vector<AccessEntry>::difference_type)i, entry);
}

} // namespace

struct dom_econ_access_control {
    std::vector<AccessEntry> grants;
};

dom_econ_access_control *dom_econ_access_control_create(void) {
    return new dom_econ_access_control();
}

void dom_econ_access_control_destroy(dom_econ_access_control *ctrl) {
    if (!ctrl) {
        return;
    }
    delete ctrl;
}

int dom_econ_access_grant(dom_econ_access_control *ctrl,
                          const dom_econ_access_grant_desc *desc) {
    AccessEntry entry;
    int idx;
    if (!ctrl || !desc) {
        return DOM_ECON_ACCESS_INVALID_ARGUMENT;
    }
    entry.actor_id = desc->actor_id;
    entry.account_id = desc->account_id;
    entry.flags = desc->flags;
    idx = find_index(ctrl->grants, entry.actor_id, entry.account_id);
    if (idx >= 0) {
        ctrl->grants[(size_t)idx].flags = entry.flags;
        return DOM_ECON_ACCESS_OK;
    }
    insert_sorted(ctrl->grants, entry);
    return DOM_ECON_ACCESS_OK;
}

int dom_econ_access_revoke(dom_econ_access_control *ctrl,
                           u64 actor_id,
                           u64 account_id) {
    int idx;
    if (!ctrl) {
        return DOM_ECON_ACCESS_INVALID_ARGUMENT;
    }
    idx = find_index(ctrl->grants, actor_id, account_id);
    if (idx < 0) {
        return DOM_ECON_ACCESS_OK;
    }
    ctrl->grants.erase(ctrl->grants.begin() + (std::vector<AccessEntry>::difference_type)idx);
    return DOM_ECON_ACCESS_OK;
}

u32 dom_econ_access_check(const dom_econ_access_control *ctrl,
                          u64 actor_id,
                          u64 account_id) {
    int idx;
    if (!ctrl) {
        return 0u;
    }
    idx = find_index(ctrl->grants, actor_id, account_id);
    if (idx < 0) {
        return 0u;
    }
    return ctrl->grants[(size_t)idx].flags;
}

int dom_econ_access_iterate(const dom_econ_access_control *ctrl,
                            dom_econ_access_iter_fn fn,
                            void *user) {
    size_t i;
    if (!ctrl || !fn) {
        return DOM_ECON_ACCESS_INVALID_ARGUMENT;
    }
    for (i = 0u; i < ctrl->grants.size(); ++i) {
        const AccessEntry &entry = ctrl->grants[i];
        dom_econ_access_grant_info info;
        info.actor_id = entry.actor_id;
        info.account_id = entry.account_id;
        info.flags = entry.flags;
        fn(&info, user);
    }
    return DOM_ECON_ACCESS_OK;
}

u32 dom_econ_access_count(const dom_econ_access_control *ctrl) {
    if (!ctrl) {
        return 0u;
    }
    return (u32)ctrl->grants.size();
}
