#include "domino/compat.h"

static int dom_version_in_range(const DomVersionedCapability *cap, uint32_t value)
{
    if (!cap) return 0;
    /* Treat zeroed capabilities as unspecified/compatible. */
    if (cap->min_compat == 0 && cap->max_compat == 0) return 1;
    if (value == 0) return 1;
    if (cap->min_compat != 0 && value < cap->min_compat) return 0;
    if (cap->max_compat != 0 && value > cap->max_compat) return 0;
    return 1;
}

static int dom_version_overlap(const DomVersionedCapability *a, const DomVersionedCapability *b)
{
    if (!a || !b) return 0;
    if (!dom_version_in_range(a, b->current)) return 0;
    if (!dom_version_in_range(b, a->current)) return 0;
    return 1;
}

static const DomVersionedCapability *dom_select_format_cap(const DomCompatProfile *p, int kind)
{
    if (!p) return 0;
    switch (kind) {
    case 0: return &p->save_format;
    case 1: return &p->pack_format;
    case 2: return &p->replay_format;
    default: return 0;
    }
}

int dom_compat_check_core(const DomCompatProfile *a, const DomCompatProfile *b)
{
    if (!a || !b) return 0;
    return dom_version_overlap(&a->core, &b->core);
}

int dom_compat_check_format(const DomCompatProfile *a, const DomCompatProfile *b, int kind)
{
    const DomVersionedCapability *ca;
    const DomVersionedCapability *cb;
    if (!a || !b) return 0;
    ca = dom_select_format_cap(a, kind);
    cb = dom_select_format_cap(b, kind);
    if (!ca || !cb) return 0;
    return dom_version_overlap(ca, cb);
}

int dom_compat_check_net(const DomCompatProfile *a, const DomCompatProfile *b)
{
    if (!a || !b) return 0;
    return dom_version_overlap(&a->net_proto, &b->net_proto);
}

DomCompatDecision dom_decide_compat(const DomCompatProfile *a, const DomCompatProfile *b)
{
    int core_ok;
    int save_ok;
    int pack_ok;
    int replay_ok;
    int net_ok;

    if (!a || !b) return DOM_COMPAT_INCOMPATIBLE;

    core_ok = dom_compat_check_core(a, b);
    save_ok = dom_compat_check_format(a, b, 0);
    pack_ok = dom_compat_check_format(a, b, 1);
    replay_ok = dom_compat_check_format(a, b, 2);
    net_ok = dom_compat_check_net(a, b);

    if (!core_ok) return DOM_COMPAT_INCOMPATIBLE;
    if (!save_ok || !pack_ok || !replay_ok) return DOM_COMPAT_OK_READONLY;
    if (!net_ok) return DOM_COMPAT_OK_LIMITED;
    return DOM_COMPAT_OK_FULL;
}
