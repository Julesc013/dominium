#include <string.h>

#include "policy/d_policy.h"

#include "core/d_subsystem.h"
#include "core/d_tlv_kv.h"
#include "content/d_content_extra.h"
#include "research/d_research_state.h"

static int g_policy_initialized = 0;
static int g_policy_registered = 0;

int d_policy_system_init(void) {
    g_policy_initialized = 1;
    return 0;
}

void d_policy_system_shutdown(void) {
    g_policy_initialized = 0;
}

static int dpolicy_scope_matches(const d_proto_policy_rule *p, const d_policy_context *ctx) {
    u32 off = 0u;
    u32 tag;
    d_tlv_blob payload;
    int rc;

    int have_subject_kind = 0;
    u32 required_subject_kind = 0u;

    int have_subject_ids = 0;
    int subject_id_ok = 0;

    int have_org_ids = 0;
    int org_id_ok = 0;

    u32 tags_all = 0u;
    u32 tags_any = 0u;

    if (!p || !ctx) {
        return 0;
    }
    if (!p->scope.ptr || p->scope.len == 0u) {
        return 0;
    }

    while ((rc = d_tlv_kv_next(&p->scope, &off, &tag, &payload)) == 0) {
        if (tag == D_TLV_POLICY_SCOPE_SUBJECT_KIND) {
            u32 tmp = 0u;
            if (d_tlv_kv_read_u32(&payload, &tmp) == 0) {
                have_subject_kind = 1;
                required_subject_kind = tmp;
            }
        } else if (tag == D_TLV_POLICY_SCOPE_SUBJECT_ID) {
            u32 tmp = 0u;
            have_subject_ids = 1;
            if (d_tlv_kv_read_u32(&payload, &tmp) == 0) {
                if (tmp == ctx->subject_id) {
                    subject_id_ok = 1;
                }
            }
        } else if (tag == D_TLV_POLICY_SCOPE_SUBJECT_TAGS_ALL) {
            u32 tmp = 0u;
            if (d_tlv_kv_read_u32(&payload, &tmp) == 0) {
                tags_all |= tmp;
            }
        } else if (tag == D_TLV_POLICY_SCOPE_SUBJECT_TAGS_ANY) {
            u32 tmp = 0u;
            if (d_tlv_kv_read_u32(&payload, &tmp) == 0) {
                tags_any |= tmp;
            }
        } else if (tag == D_TLV_POLICY_SCOPE_ORG_ID) {
            u32 tmp = 0u;
            have_org_ids = 1;
            if (d_tlv_kv_read_u32(&payload, &tmp) == 0) {
                if ((d_org_id)tmp == ctx->org_id) {
                    org_id_ok = 1;
                }
            }
        }
    }

    if (have_subject_kind && required_subject_kind != ctx->subject_kind) {
        return 0;
    }
    if (have_subject_ids && !subject_id_ok) {
        return 0;
    }
    if (have_org_ids && !org_id_ok) {
        return 0;
    }
    if (tags_all != 0u && (ctx->subject_tags & tags_all) != tags_all) {
        return 0;
    }
    if (tags_any != 0u && (ctx->subject_tags & tags_any) == 0u) {
        return 0;
    }

    return 1;
}

static int dpolicy_conditions_met(const d_proto_policy_rule *p, const d_policy_context *ctx) {
    u32 off = 0u;
    u32 tag;
    d_tlv_blob payload;
    int rc;

    if (!p || !ctx) {
        return 0;
    }
    if (!p->conditions.ptr || p->conditions.len == 0u) {
        return 1;
    }

    while ((rc = d_tlv_kv_next(&p->conditions, &off, &tag, &payload)) == 0) {
        if (tag == D_TLV_POLICY_COND_RESEARCH_COMPLETED) {
            u32 rid = 0u;
            if (d_tlv_kv_read_u32(&payload, &rid) == 0) {
                if (!d_research_is_completed(ctx->org_id, (d_research_id)rid)) {
                    return 0;
                }
            }
        } else if (tag == D_TLV_POLICY_COND_RESEARCH_NOT_COMPLETED) {
            u32 rid = 0u;
            if (d_tlv_kv_read_u32(&payload, &rid) == 0) {
                if (d_research_is_completed(ctx->org_id, (d_research_id)rid)) {
                    return 0;
                }
            }
        }
    }

    return 1;
}

static void dpolicy_apply_effect(const d_proto_policy_rule *p, d_policy_effect_result *out) {
    u32 off = 0u;
    u32 tag;
    d_tlv_blob payload;
    int rc;

    if (!p || !out) {
        return;
    }
    if (!p->effect.ptr || p->effect.len == 0u) {
        return;
    }

    while ((rc = d_tlv_kv_next(&p->effect, &off, &tag, &payload)) == 0) {
        if (tag == D_TLV_POLICY_EFFECT_ALLOWED) {
            u32 tmp = 1u;
            if (d_tlv_kv_read_u32(&payload, &tmp) == 0) {
                if (tmp == 0u) {
                    out->allowed = 0u;
                }
            }
        } else if (tag == D_TLV_POLICY_EFFECT_MULTIPLIER) {
            q16_16 m = 0;
            if (d_tlv_kv_read_q16_16(&payload, &m) == 0) {
                out->multiplier = d_q16_16_mul(out->multiplier, m);
            }
        } else if (tag == D_TLV_POLICY_EFFECT_CAP) {
            q16_16 c = 0;
            if (d_tlv_kv_read_q16_16(&payload, &c) == 0) {
                if (out->cap == 0 || c < out->cap) {
                    out->cap = c;
                }
            }
        }
    }
}

int d_policy_evaluate(
    const d_policy_context    *ctx,
    d_policy_effect_result    *out
) {
    u32 i;
    u32 count;

    if (!ctx || !out) {
        return -1;
    }
    if (!g_policy_initialized) {
        (void)d_policy_system_init();
    }

    out->allowed = 1u;
    out->multiplier = d_q16_16_from_int(1);
    out->cap = 0;

    count = d_content_policy_rule_count();
    for (i = 0u; i < count; ++i) {
        const d_proto_policy_rule *p = d_content_get_policy_rule_by_index(i);
        if (!p) {
            continue;
        }
        if (!dpolicy_scope_matches(p, ctx)) {
            continue;
        }
        if (!dpolicy_conditions_met(p, ctx)) {
            continue;
        }
        dpolicy_apply_effect(p, out);
        if (out->allowed == 0u) {
            break;
        }
    }

    if (out->cap > 0 && out->multiplier > out->cap) {
        out->multiplier = out->cap;
    }
    if (out->multiplier < 0) {
        out->multiplier = 0;
    }
    return 0;
}

static int d_policy_save_chunk(struct d_world *w, struct d_chunk *chunk, struct d_tlv_blob *out) {
    (void)w;
    (void)chunk;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_policy_load_chunk(struct d_world *w, struct d_chunk *chunk, const struct d_tlv_blob *in) {
    (void)w;
    (void)chunk;
    (void)in;
    return 0;
}

static void d_policy_init_instance_subsys(struct d_world *w) {
    (void)w;
    (void)d_policy_system_init();
}

static void d_policy_tick_subsys(struct d_world *w, u32 ticks) {
    (void)w;
    (void)ticks;
}

static int d_policy_save_instance(struct d_world *w, struct d_tlv_blob *out) {
    (void)w;
    if (!out) {
        return -1;
    }
    out->ptr = (unsigned char *)0;
    out->len = 0u;
    return 0;
}

static int d_policy_load_instance(struct d_world *w, const struct d_tlv_blob *in) {
    (void)w;
    (void)in;
    return 0;
}

static void d_policy_register_models(void) {
    /* No standalone models. */
}

static void d_policy_load_protos(const struct d_tlv_blob *blob) {
    (void)blob;
}

static const d_subsystem_desc g_policy_subsystem = {
    D_SUBSYS_POLICY,
    "policy",
    1u,
    d_policy_register_models,
    d_policy_load_protos,
    d_policy_init_instance_subsys,
    d_policy_tick_subsys,
    d_policy_save_chunk,
    d_policy_load_chunk,
    d_policy_save_instance,
    d_policy_load_instance
};

void d_policy_register_subsystem(void) {
    if (g_policy_registered) {
        return;
    }
    if (d_subsystem_register(&g_policy_subsystem) == 0) {
        g_policy_registered = 1;
    }
}

