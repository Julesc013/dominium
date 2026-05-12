/*
FILE: source/dominium/common/core_solver.c
MODULE: Dominium
PURPOSE: Implements deterministic constraint solver with explainable output + TLV encoding.
*/
#include "dominium/core_solver.h"

#include <string.h>
#include <ctype.h>

enum {
    CORE_SOLVER_TLV_VERSION = 1u
};

enum {
    CORE_SOLVER_TLV_TAG_SCHEMA_VERSION = 1u,
    CORE_SOLVER_TLV_TAG_SELECTED = 2u,
    CORE_SOLVER_TLV_TAG_REJECTED = 3u
};

enum {
    CORE_SOLVER_SEL_TAG_CATEGORY_ID = 1u,
    CORE_SOLVER_SEL_TAG_COMPONENT_ID = 2u,
    CORE_SOLVER_SEL_TAG_REASON = 3u,
    CORE_SOLVER_SEL_TAG_SCORE = 4u,
    CORE_SOLVER_SEL_TAG_PRIORITY = 5u,
    CORE_SOLVER_SEL_TAG_PREFERS_SAT = 6u
};

enum {
    CORE_SOLVER_REJ_TAG_CATEGORY_ID = 1u,
    CORE_SOLVER_REJ_TAG_COMPONENT_ID = 2u,
    CORE_SOLVER_REJ_TAG_REASON = 3u,
    CORE_SOLVER_REJ_TAG_CONSTRAINT = 4u,
    CORE_SOLVER_REJ_TAG_ACTUAL = 5u,
    CORE_SOLVER_REJ_TAG_CONFLICT_ID = 6u
};

enum {
    CORE_SOLVER_CONSTRAINT_TAG_KEY_ID = 1u,
    CORE_SOLVER_CONSTRAINT_TAG_OP = 2u,
    CORE_SOLVER_CONSTRAINT_TAG_TYPE = 3u,
    CORE_SOLVER_CONSTRAINT_TAG_WEIGHT = 4u,
    CORE_SOLVER_CONSTRAINT_TAG_VALUE_U32 = 5u,
    CORE_SOLVER_CONSTRAINT_TAG_VALUE_I32 = 6u,
    CORE_SOLVER_CONSTRAINT_TAG_VALUE_U64 = 7u,
    CORE_SOLVER_CONSTRAINT_TAG_VALUE_I64 = 8u,
    CORE_SOLVER_CONSTRAINT_TAG_RANGE_MIN = 9u,
    CORE_SOLVER_CONSTRAINT_TAG_RANGE_MAX = 10u
};

enum {
    CORE_SOLVER_ACTUAL_TAG_TYPE = 1u,
    CORE_SOLVER_ACTUAL_TAG_VALUE_U32 = 2u,
    CORE_SOLVER_ACTUAL_TAG_VALUE_I32 = 3u,
    CORE_SOLVER_ACTUAL_TAG_VALUE_U64 = 4u,
    CORE_SOLVER_ACTUAL_TAG_VALUE_I64 = 5u,
    CORE_SOLVER_ACTUAL_TAG_RANGE_MIN = 6u,
    CORE_SOLVER_ACTUAL_TAG_RANGE_MAX = 7u
};

static void solver_write_u32_le(unsigned char out[4], u32 v) {
    out[0] = (unsigned char)(v & 0xFFu);
    out[1] = (unsigned char)((v >> 8u) & 0xFFu);
    out[2] = (unsigned char)((v >> 16u) & 0xFFu);
    out[3] = (unsigned char)((v >> 24u) & 0xFFu);
}

static void solver_write_u64_le(unsigned char out[8], u64 v) {
    out[0] = (unsigned char)(v & 0xFFu);
    out[1] = (unsigned char)((v >> 8u) & 0xFFu);
    out[2] = (unsigned char)((v >> 16u) & 0xFFu);
    out[3] = (unsigned char)((v >> 24u) & 0xFFu);
    out[4] = (unsigned char)((v >> 32u) & 0xFFu);
    out[5] = (unsigned char)((v >> 40u) & 0xFFu);
    out[6] = (unsigned char)((v >> 48u) & 0xFFu);
    out[7] = (unsigned char)((v >> 56u) & 0xFFu);
}

static int solver_read_u32_le(const unsigned char* data, u32 len, u32* out_v) {
    if (!data || len != 4u || !out_v) {
        return 0;
    }
    *out_v = (u32)data[0] |
             ((u32)data[1] << 8u) |
             ((u32)data[2] << 16u) |
             ((u32)data[3] << 24u);
    return 1;
}

static int solver_read_i32_le(const unsigned char* data, u32 len, i32* out_v) {
    u32 v;
    if (!solver_read_u32_le(data, len, &v) || !out_v) {
        return 0;
    }
    *out_v = (i32)v;
    return 1;
}

static int solver_read_u64_le(const unsigned char* data, u32 len, u64* out_v) {
    if (!data || len != 8u || !out_v) {
        return 0;
    }
    *out_v = (u64)data[0] |
             ((u64)data[1] << 8u) |
             ((u64)data[2] << 16u) |
             ((u64)data[3] << 24u) |
             ((u64)data[4] << 32u) |
             ((u64)data[5] << 40u) |
             ((u64)data[6] << 48u) |
             ((u64)data[7] << 56u);
    return 1;
}

static int solver_read_i64_le(const unsigned char* data, u32 len, i64* out_v) {
    u64 v;
    if (!solver_read_u64_le(data, len, &v) || !out_v) {
        return 0;
    }
    *out_v = (i64)v;
    return 1;
}

static int solver_ascii_tolower(int c) {
    if (c >= 'A' && c <= 'Z') {
        return c - 'A' + 'a';
    }
    return c;
}

static int solver_stricmp(const char* a, const char* b) {
    if (!a && !b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    while (*a && *b) {
        int ca = solver_ascii_tolower((unsigned char)*a);
        int cb = solver_ascii_tolower((unsigned char)*b);
        if (ca != cb) return (ca < cb) ? -1 : 1;
        ++a;
        ++b;
    }
    if (*a == *b) return 0;
    return (*a < *b) ? -1 : 1;
}

static void solver_copy_id(char* dst, const char* src) {
    size_t n = 0u;
    if (!dst) return;
    if (!src) {
        dst[0] = '\0';
        return;
    }
    while (src[n] && n + 1u < CORE_SOLVER_MAX_ID) {
        dst[n] = src[n];
        ++n;
    }
    dst[n] = '\0';
}

static const core_cap_entry* solver_find_entry(const core_cap_entry* entries, u32 count, u32 key_id) {
    u32 i;
    if (!entries) return (const core_cap_entry*)0;
    for (i = 0u; i < count; ++i) {
        if (entries[i].key_id == key_id) {
            return &entries[i];
        }
    }
    return (const core_cap_entry*)0;
}

static const core_cap_entry* solver_lookup_cap(const core_solver_desc* desc,
                                               const core_solver_component_desc* comp,
                                               u32 key_id) {
    const core_cap_entry* e;
    if (comp) {
        e = solver_find_entry(comp->provides, comp->provides_count, key_id);
        if (e) return e;
    }
    if (desc && desc->host_caps) {
        return solver_find_entry(desc->host_caps->entries, desc->host_caps->count, key_id);
    }
    return (const core_cap_entry*)0;
}

static int solver_value_cmp(u8 type, const core_cap_value* a, const core_cap_value* b) {
    if (!a || !b) {
        return 0;
    }
    switch (type) {
    case CORE_CAP_BOOL:
    case CORE_CAP_U32:
    case CORE_CAP_ENUM_ID:
    case CORE_CAP_STRING_ID:
        if (a->u32_value < b->u32_value) return -1;
        if (a->u32_value > b->u32_value) return 1;
        return 0;
    case CORE_CAP_I32:
        if (a->i32_value < b->i32_value) return -1;
        if (a->i32_value > b->i32_value) return 1;
        return 0;
    case CORE_CAP_U64:
        if (a->u64_value < b->u64_value) return -1;
        if (a->u64_value > b->u64_value) return 1;
        return 0;
    case CORE_CAP_I64:
        if (a->i64_value < b->i64_value) return -1;
        if (a->i64_value > b->i64_value) return 1;
        return 0;
    case CORE_CAP_RANGE_U32:
        if (a->range_u32.min_value < b->range_u32.min_value) return -1;
        if (a->range_u32.min_value > b->range_u32.min_value) return 1;
        if (a->range_u32.max_value < b->range_u32.max_value) return -1;
        if (a->range_u32.max_value > b->range_u32.max_value) return 1;
        return 0;
    default:
        break;
    }
    return 0;
}

static int solver_eval_constraint(const core_solver_constraint* c,
                                  const core_cap_entry* actual,
                                  u32* out_actual_present,
                                  u8* out_actual_type,
                                  core_cap_value* out_actual_value) {
    if (!c) return 0;
    if (out_actual_present) *out_actual_present = 0u;
    if (out_actual_type) *out_actual_type = 0u;
    if (out_actual_value) memset(out_actual_value, 0, sizeof(*out_actual_value));

    if (!actual) {
        return 0;
    }

    if (out_actual_present) *out_actual_present = 1u;
    if (out_actual_type) *out_actual_type = actual->type;
    if (out_actual_value) *out_actual_value = actual->v;

    switch (c->op) {
    case CORE_SOLVER_OP_EQ:
        if (actual->type != c->type) return 0;
        return solver_value_cmp(c->type, &actual->v, &c->value) == 0;
    case CORE_SOLVER_OP_NE:
        if (actual->type != c->type) return 0;
        return solver_value_cmp(c->type, &actual->v, &c->value) != 0;
    case CORE_SOLVER_OP_GE:
        if (actual->type != c->type) return 0;
        return solver_value_cmp(c->type, &actual->v, &c->value) >= 0;
    case CORE_SOLVER_OP_LE:
        if (actual->type != c->type) return 0;
        return solver_value_cmp(c->type, &actual->v, &c->value) <= 0;
    case CORE_SOLVER_OP_IN_RANGE:
        if (c->type != CORE_CAP_RANGE_U32) {
            return 0;
        }
        if (actual->type != CORE_CAP_U32 &&
            actual->type != CORE_CAP_ENUM_ID &&
            actual->type != CORE_CAP_BOOL) {
            return 0;
        }
        return (actual->v.u32_value >= c->value.range_u32.min_value &&
                actual->v.u32_value <= c->value.range_u32.max_value);
    default:
        break;
    }
    return 0;
}

static int solver_constraint_fails(const core_solver_desc* desc,
                                   const core_solver_component_desc* comp,
                                   const core_solver_constraint* c,
                                   u32* out_actual_present,
                                   u8* out_actual_type,
                                   core_cap_value* out_actual_value) {
    const core_cap_entry* actual;
    actual = solver_lookup_cap(desc, comp, c->key_id);
    if (!solver_eval_constraint(c, actual, out_actual_present, out_actual_type, out_actual_value)) {
        return 1;
    }
    return 0;
}

static int solver_forbid_hits(const core_solver_desc* desc,
                              const core_solver_component_desc* comp,
                              const core_solver_constraint* c,
                              u32* out_actual_present,
                              u8* out_actual_type,
                              core_cap_value* out_actual_value) {
    const core_cap_entry* actual;
    actual = solver_lookup_cap(desc, comp, c->key_id);
    if (solver_eval_constraint(c, actual, out_actual_present, out_actual_type, out_actual_value)) {
        return 1;
    }
    return 0;
}

static u32 solver_prefers_score(const core_solver_desc* desc,
                                const core_solver_component_desc* comp,
                                u32* out_satisfied) {
    u32 i;
    u32 score = 0u;
    u32 sat = 0u;
    if (!comp || !comp->prefers || comp->prefers_count == 0u) {
        if (out_satisfied) *out_satisfied = 0u;
        return 0u;
    }
    for (i = 0u; i < comp->prefers_count; ++i) {
        const core_solver_constraint* c = &comp->prefers[i];
        if (!c) continue;
        if (!solver_constraint_fails(desc, comp, c, (u32*)0, (u8*)0, (core_cap_value*)0)) {
            u32 w = c->weight ? c->weight : 1u;
            score += w;
            sat += 1u;
        }
    }
    if (out_satisfied) *out_satisfied = sat;
    return score;
}

static const core_solver_override* solver_find_override(const core_solver_desc* desc, u32 category_id) {
    u32 i;
    if (!desc || !desc->overrides) {
        return (const core_solver_override*)0;
    }
    for (i = 0u; i < desc->override_count; ++i) {
        if (desc->overrides[i].category_id == category_id) {
            return &desc->overrides[i];
        }
    }
    return (const core_solver_override*)0;
}

void core_solver_result_clear(core_solver_result* out_result) {
    if (!out_result) {
        return;
    }
    memset(out_result, 0, sizeof(*out_result));
    out_result->ok = 0u;
    out_result->fail_reason = CORE_SOLVER_FAIL_NONE;
    out_result->fail_category = 0u;
}

dom_abi_result core_solver_select(const core_solver_desc* desc, core_solver_result* out_result) {
    u32 cat_idx[CORE_SOLVER_MAX_CATEGORIES];
    u32 cat_count;
    u32 i;
    if (!desc || !out_result || !desc->categories || !desc->components) {
        return (dom_abi_result)-1;
    }
    core_solver_result_clear(out_result);

    cat_count = (desc->category_count > CORE_SOLVER_MAX_CATEGORIES) ? CORE_SOLVER_MAX_CATEGORIES : desc->category_count;
    for (i = 0u; i < cat_count; ++i) {
        cat_idx[i] = i;
    }
    for (i = 1u; i < cat_count; ++i) {
        u32 key = cat_idx[i];
        u32 j = i;
        while (j > 0u) {
            const core_solver_category_desc* a = &desc->categories[cat_idx[j - 1u]];
            const core_solver_category_desc* b = &desc->categories[key];
            if (a->category_id <= b->category_id) {
                break;
            }
            cat_idx[j] = cat_idx[j - 1u];
            --j;
        }
        cat_idx[j] = key;
    }

    for (i = 0u; i < cat_count; ++i) {
        const core_solver_category_desc* cat = &desc->categories[cat_idx[i]];
        u32 cand_idx[CORE_SOLVER_MAX_COMPONENTS];
        u32 cand_count = 0u;
        u32 j;
        const core_solver_override* ov = solver_find_override(desc, cat->category_id);
        const core_solver_component_desc* selected = (const core_solver_component_desc*)0;
        u32 best_score = 0u;
        u32 best_pref = 0u;
        u32 best_priority = 0u;
        u32 chosen_by_override = 0u;

        for (j = 0u; j < desc->component_count && cand_count < CORE_SOLVER_MAX_COMPONENTS; ++j) {
            if (desc->components[j].category_id == cat->category_id) {
                cand_idx[cand_count++] = j;
            }
        }

        for (j = 1u; j < cand_count; ++j) {
            u32 key = cand_idx[j];
            u32 k = j;
            while (k > 0u) {
                const core_solver_component_desc* a = &desc->components[cand_idx[k - 1u]];
                const core_solver_component_desc* b = &desc->components[key];
                if (solver_stricmp(a->component_id, b->component_id) <= 0) {
                    break;
                }
                cand_idx[k] = cand_idx[k - 1u];
                --k;
            }
            cand_idx[k] = key;
        }

        if (cand_count == 0u) {
            if (cat->required) {
                out_result->ok = 0u;
                out_result->fail_reason = CORE_SOLVER_FAIL_NO_ELIGIBLE;
                out_result->fail_category = cat->category_id;
                return (dom_abi_result)-1;
            }
            continue;
        }

        for (j = 0u; j < cand_count; ++j) {
            const core_solver_component_desc* comp = &desc->components[cand_idx[j]];
            u32 actual_present = 0u;
            u8 actual_type = 0u;
            core_cap_value actual_value;
            int rejected = 0;

            if (ov && ov->component_id && ov->component_id[0]) {
                if (solver_stricmp(comp->component_id, ov->component_id) != 0) {
                    if (out_result->rejected_count < CORE_SOLVER_MAX_REJECTIONS) {
                        core_solver_reject* r = &out_result->rejected[out_result->rejected_count++];
                        memset(r, 0, sizeof(*r));
                        r->category_id = cat->category_id;
                        solver_copy_id(r->component_id, comp->component_id);
                        r->reason = CORE_SOLVER_REJECT_OVERRIDE_MISMATCH;
                    }
                    continue;
                }
            }

            if (desc->profile_requires && desc->profile_requires_count > 0u) {
                u32 k;
                for (k = 0u; k < desc->profile_requires_count; ++k) {
                    const core_solver_constraint* c = &desc->profile_requires[k];
                    if (solver_constraint_fails(desc, comp, c, &actual_present, &actual_type, &actual_value)) {
                        rejected = 1;
                        if (out_result->rejected_count < CORE_SOLVER_MAX_REJECTIONS) {
                            core_solver_reject* r = &out_result->rejected[out_result->rejected_count++];
                            memset(r, 0, sizeof(*r));
                            r->category_id = cat->category_id;
                            solver_copy_id(r->component_id, comp->component_id);
                            r->reason = CORE_SOLVER_REJECT_CONSTRAINT;
                            r->constraint = *c;
                            r->actual_present = actual_present;
                            r->actual_type = actual_type;
                            r->actual_value = actual_value;
                        }
                        break;
                    }
                }
            }

            if (!rejected && desc->profile_forbids && desc->profile_forbids_count > 0u) {
                u32 k;
                for (k = 0u; k < desc->profile_forbids_count; ++k) {
                    const core_solver_constraint* c = &desc->profile_forbids[k];
                    if (solver_forbid_hits(desc, comp, c, &actual_present, &actual_type, &actual_value)) {
                        rejected = 1;
                        if (out_result->rejected_count < CORE_SOLVER_MAX_REJECTIONS) {
                            core_solver_reject* r = &out_result->rejected[out_result->rejected_count++];
                            memset(r, 0, sizeof(*r));
                            r->category_id = cat->category_id;
                            solver_copy_id(r->component_id, comp->component_id);
                            r->reason = CORE_SOLVER_REJECT_CONSTRAINT;
                            r->constraint = *c;
                            r->actual_present = actual_present;
                            r->actual_type = actual_type;
                            r->actual_value = actual_value;
                        }
                        break;
                    }
                }
            }

            if (!rejected && comp->requires && comp->requires_count > 0u) {
                u32 k;
                for (k = 0u; k < comp->requires_count; ++k) {
                    const core_solver_constraint* c = &comp->requires[k];
                    if (solver_constraint_fails(desc, comp, c, &actual_present, &actual_type, &actual_value)) {
                        rejected = 1;
                        if (out_result->rejected_count < CORE_SOLVER_MAX_REJECTIONS) {
                            core_solver_reject* r = &out_result->rejected[out_result->rejected_count++];
                            memset(r, 0, sizeof(*r));
                            r->category_id = cat->category_id;
                            solver_copy_id(r->component_id, comp->component_id);
                            r->reason = CORE_SOLVER_REJECT_CONSTRAINT;
                            r->constraint = *c;
                            r->actual_present = actual_present;
                            r->actual_type = actual_type;
                            r->actual_value = actual_value;
                        }
                        break;
                    }
                }
            }

            if (!rejected && comp->forbids && comp->forbids_count > 0u) {
                u32 k;
                for (k = 0u; k < comp->forbids_count; ++k) {
                    const core_solver_constraint* c = &comp->forbids[k];
                    if (solver_forbid_hits(desc, comp, c, &actual_present, &actual_type, &actual_value)) {
                        rejected = 1;
                        if (out_result->rejected_count < CORE_SOLVER_MAX_REJECTIONS) {
                            core_solver_reject* r = &out_result->rejected[out_result->rejected_count++];
                            memset(r, 0, sizeof(*r));
                            r->category_id = cat->category_id;
                            solver_copy_id(r->component_id, comp->component_id);
                            r->reason = CORE_SOLVER_REJECT_CONSTRAINT;
                            r->constraint = *c;
                            r->actual_present = actual_present;
                            r->actual_type = actual_type;
                            r->actual_value = actual_value;
                        }
                        break;
                    }
                }
            }

            if (!rejected && comp->conflicts && comp->conflicts_count > 0u) {
                u32 k;
                u32 s;
                for (k = 0u; k < comp->conflicts_count; ++k) {
                    const char* conflict_id = comp->conflicts[k];
                    for (s = 0u; s < out_result->selected_count; ++s) {
                        if (solver_stricmp(conflict_id, out_result->selected[s].component_id) == 0) {
                            rejected = 1;
                            if (out_result->rejected_count < CORE_SOLVER_MAX_REJECTIONS) {
                                core_solver_reject* r = &out_result->rejected[out_result->rejected_count++];
                                memset(r, 0, sizeof(*r));
                                r->category_id = cat->category_id;
                                solver_copy_id(r->component_id, comp->component_id);
                                r->reason = CORE_SOLVER_REJECT_CONFLICT;
                                solver_copy_id(r->conflict_component_id, conflict_id);
                            }
                            break;
                        }
                    }
                    if (rejected) break;
                }
            }

            if (rejected) {
                if (ov && ov->component_id && solver_stricmp(comp->component_id, ov->component_id) == 0) {
                    out_result->ok = 0u;
                    out_result->fail_reason = CORE_SOLVER_FAIL_OVERRIDE_INELIGIBLE;
                    out_result->fail_category = cat->category_id;
                    return (dom_abi_result)-1;
                }
                continue;
            }

            {
                u32 pref_sat = 0u;
                u32 base = desc->score_fn ? desc->score_fn(comp, desc->score_user) : 0u;
                u32 pref_score = solver_prefers_score(desc, comp, &pref_sat);
                u32 score = base + pref_score;
                if (!selected ||
                    score > best_score ||
                    (score == best_score && comp->priority > best_priority) ||
                    (score == best_score && comp->priority == best_priority &&
                     solver_stricmp(comp->component_id, selected->component_id) < 0)) {
                    selected = comp;
                    best_score = score;
                    best_priority = comp->priority;
                    best_pref = pref_sat;
                    chosen_by_override = (ov && ov->component_id && solver_stricmp(comp->component_id, ov->component_id) == 0) ? 1u : 0u;
                }
            }

            if (ov && ov->component_id && solver_stricmp(comp->component_id, ov->component_id) == 0) {
                break;
            }
        }

        if (!selected) {
            if (cat->required) {
                out_result->ok = 0u;
                out_result->fail_reason = ov ? CORE_SOLVER_FAIL_OVERRIDE_NOT_FOUND : CORE_SOLVER_FAIL_NO_ELIGIBLE;
                out_result->fail_category = cat->category_id;
                return (dom_abi_result)-1;
            }
            continue;
        }

        if (out_result->selected_count < CORE_SOLVER_MAX_SELECTION) {
            core_solver_selected* s = &out_result->selected[out_result->selected_count++];
            memset(s, 0, sizeof(*s));
            s->category_id = cat->category_id;
            solver_copy_id(s->component_id, selected->component_id);
            s->reason = chosen_by_override ? CORE_SOLVER_SELECT_OVERRIDE : CORE_SOLVER_SELECT_SCORE;
            s->score = best_score;
            s->priority = best_priority;
            s->prefers_satisfied = best_pref;
        }
    }

    out_result->ok = 1u;
    out_result->fail_reason = CORE_SOLVER_FAIL_NONE;
    out_result->fail_category = 0u;
    return 0;
}

const char* core_solver_category_token(u32 category_id) {
    switch (category_id) {
    case CORE_SOLVER_CAT_PLATFORM: return "platform";
    case CORE_SOLVER_CAT_UI: return "ui";
    case CORE_SOLVER_CAT_RENDERER: return "renderer";
    case CORE_SOLVER_CAT_PROVIDER_NET: return "provider_net";
    case CORE_SOLVER_CAT_PROVIDER_TRUST: return "provider_trust";
    case CORE_SOLVER_CAT_PROVIDER_KEYCHAIN: return "provider_keychain";
    case CORE_SOLVER_CAT_PROVIDER_CONTENT: return "provider_content";
    case CORE_SOLVER_CAT_PROVIDER_OS_INTEGRATION: return "provider_os_integration";
    default: break;
    }
    return "unknown";
}

const char* core_solver_op_token(u32 op) {
    switch (op) {
    case CORE_SOLVER_OP_EQ: return "==";
    case CORE_SOLVER_OP_NE: return "!=";
    case CORE_SOLVER_OP_GE: return ">=";
    case CORE_SOLVER_OP_LE: return "<=";
    case CORE_SOLVER_OP_IN_RANGE: return "in_range";
    default: break;
    }
    return "?";
}

const char* core_solver_fail_reason_token(u32 reason) {
    switch (reason) {
    case CORE_SOLVER_FAIL_NONE: return "none";
    case CORE_SOLVER_FAIL_OVERRIDE_NOT_FOUND: return "override_not_found";
    case CORE_SOLVER_FAIL_OVERRIDE_INELIGIBLE: return "override_ineligible";
    case CORE_SOLVER_FAIL_NO_ELIGIBLE: return "no_eligible";
    default: break;
    }
    return "unknown";
}

const char* core_solver_reject_reason_token(u32 reason) {
    switch (reason) {
    case CORE_SOLVER_REJECT_CONSTRAINT: return "constraint";
    case CORE_SOLVER_REJECT_CONFLICT: return "conflict";
    case CORE_SOLVER_REJECT_OVERRIDE_MISMATCH: return "override_mismatch";
    default: break;
    }
    return "unknown";
}

const char* core_solver_select_reason_token(u32 reason) {
    switch (reason) {
    case CORE_SOLVER_SELECT_SCORE: return "score";
    case CORE_SOLVER_SELECT_OVERRIDE: return "override";
    default: break;
    }
    return "unknown";
}

static dom_abi_result solver_sink_write(const core_solver_write_sink* sink,
                                        const unsigned char* data,
                                        u32 len) {
    if (!sink || !sink->write) {
        return (dom_abi_result)-1;
    }
    return sink->write(sink->user, data, len);
}

static dom_abi_result solver_write_record(const core_solver_write_sink* sink,
                                          u32 tag,
                                          const unsigned char* payload,
                                          u32 len) {
    unsigned char hdr[8];
    solver_write_u32_le(hdr, tag);
    solver_write_u32_le(hdr + 4, len);
    if (solver_sink_write(sink, hdr, 8u) != 0) return (dom_abi_result)-1;
    if (len > 0u && payload) {
        if (solver_sink_write(sink, payload, len) != 0) return (dom_abi_result)-1;
    }
    return 0;
}

static u32 solver_constraint_value_size(const core_solver_constraint* c) {
    if (!c) return 0u;
    switch (c->type) {
    case CORE_CAP_BOOL:
    case CORE_CAP_U32:
    case CORE_CAP_ENUM_ID:
    case CORE_CAP_STRING_ID:
    case CORE_CAP_I32:
        return 8u + 4u;
    case CORE_CAP_U64:
    case CORE_CAP_I64:
        return 8u + 8u;
    case CORE_CAP_RANGE_U32:
        return (8u + 4u) + (8u + 4u);
    default:
        break;
    }
    return 0u;
}

static u32 solver_constraint_payload_size(const core_solver_constraint* c) {
    u32 size = 0u;
    size += 8u + 4u; /* key */
    size += 8u + 4u; /* op */
    size += 8u + 4u; /* type */
    size += 8u + 4u; /* weight */
    size += solver_constraint_value_size(c);
    return size;
}

static u32 solver_actual_payload_size(u8 type) {
    u32 size = 0u;
    size += 8u + 4u; /* type */
    switch (type) {
    case CORE_CAP_BOOL:
    case CORE_CAP_U32:
    case CORE_CAP_ENUM_ID:
    case CORE_CAP_STRING_ID:
    case CORE_CAP_I32:
        size += 8u + 4u;
        break;
    case CORE_CAP_U64:
    case CORE_CAP_I64:
        size += 8u + 8u;
        break;
    case CORE_CAP_RANGE_U32:
        size += (8u + 4u) + (8u + 4u);
        break;
    default:
        break;
    }
    return size;
}

u32 core_solver_explain_encoded_size(const core_solver_result* result) {
    u32 size = 0u;
    u32 i;
    if (!result) return 0u;
    size += 8u + 4u;
    for (i = 0u; i < result->selected_count; ++i) {
        const core_solver_selected* s = &result->selected[i];
        u32 payload = 0u;
        payload += 8u + 4u;
        payload += 8u + (u32)strlen(s->component_id);
        payload += 8u + 4u;
        payload += 8u + 4u;
        payload += 8u + 4u;
        payload += 8u + 4u;
        size += 8u + payload;
    }
    for (i = 0u; i < result->rejected_count; ++i) {
        const core_solver_reject* r = &result->rejected[i];
        u32 payload = 0u;
        payload += 8u + 4u;
        payload += 8u + (u32)strlen(r->component_id);
        payload += 8u + 4u;
        if (r->constraint.key_id != 0u) {
            payload += 8u + solver_constraint_payload_size(&r->constraint);
        }
        if (r->actual_present) {
            payload += 8u + solver_actual_payload_size(r->actual_type);
        }
        if (r->conflict_component_id[0]) {
            payload += 8u + (u32)strlen(r->conflict_component_id);
        }
        size += 8u + payload;
    }
    return size;
}

static dom_abi_result solver_write_constraint(const core_solver_write_sink* sink,
                                              const core_solver_constraint* c) {
    unsigned char buf[96];
    u32 off = 0u;
    unsigned char tmp[8];
    if (!sink || !c) return (dom_abi_result)-1;

    solver_write_u32_le(tmp, CORE_SOLVER_CONSTRAINT_TAG_KEY_ID);
    memcpy(buf + off, tmp, 4u); off += 4u;
    solver_write_u32_le(tmp, 4u);
    memcpy(buf + off, tmp, 4u); off += 4u;
    solver_write_u32_le(tmp, c->key_id);
    memcpy(buf + off, tmp, 4u); off += 4u;

    solver_write_u32_le(tmp, CORE_SOLVER_CONSTRAINT_TAG_OP);
    memcpy(buf + off, tmp, 4u); off += 4u;
    solver_write_u32_le(tmp, 4u);
    memcpy(buf + off, tmp, 4u); off += 4u;
    solver_write_u32_le(tmp, (u32)c->op);
    memcpy(buf + off, tmp, 4u); off += 4u;

    solver_write_u32_le(tmp, CORE_SOLVER_CONSTRAINT_TAG_TYPE);
    memcpy(buf + off, tmp, 4u); off += 4u;
    solver_write_u32_le(tmp, 4u);
    memcpy(buf + off, tmp, 4u); off += 4u;
    solver_write_u32_le(tmp, (u32)c->type);
    memcpy(buf + off, tmp, 4u); off += 4u;

    solver_write_u32_le(tmp, CORE_SOLVER_CONSTRAINT_TAG_WEIGHT);
    memcpy(buf + off, tmp, 4u); off += 4u;
    solver_write_u32_le(tmp, 4u);
    memcpy(buf + off, tmp, 4u); off += 4u;
    solver_write_u32_le(tmp, c->weight);
    memcpy(buf + off, tmp, 4u); off += 4u;

    switch (c->type) {
    case CORE_CAP_BOOL:
    case CORE_CAP_U32:
    case CORE_CAP_ENUM_ID:
    case CORE_CAP_STRING_ID:
        solver_write_u32_le(tmp, CORE_SOLVER_CONSTRAINT_TAG_VALUE_U32);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, c->value.u32_value);
        memcpy(buf + off, tmp, 4u); off += 4u;
        break;
    case CORE_CAP_I32:
        solver_write_u32_le(tmp, CORE_SOLVER_CONSTRAINT_TAG_VALUE_I32);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, (u32)c->value.i32_value);
        memcpy(buf + off, tmp, 4u); off += 4u;
        break;
    case CORE_CAP_U64:
        solver_write_u32_le(tmp, CORE_SOLVER_CONSTRAINT_TAG_VALUE_U64);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 8u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u64_le(tmp, c->value.u64_value);
        memcpy(buf + off, tmp, 8u); off += 8u;
        break;
    case CORE_CAP_I64:
        solver_write_u32_le(tmp, CORE_SOLVER_CONSTRAINT_TAG_VALUE_I64);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 8u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u64_le(tmp, (u64)c->value.i64_value);
        memcpy(buf + off, tmp, 8u); off += 8u;
        break;
    case CORE_CAP_RANGE_U32:
        solver_write_u32_le(tmp, CORE_SOLVER_CONSTRAINT_TAG_RANGE_MIN);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, c->value.range_u32.min_value);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, CORE_SOLVER_CONSTRAINT_TAG_RANGE_MAX);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, c->value.range_u32.max_value);
        memcpy(buf + off, tmp, 4u); off += 4u;
        break;
    default:
        break;
    }

    return solver_write_record(sink, CORE_SOLVER_REJ_TAG_CONSTRAINT, buf, off);
}

static dom_abi_result solver_write_actual(const core_solver_write_sink* sink,
                                          u8 type,
                                          const core_cap_value* v) {
    unsigned char buf[64];
    u32 off = 0u;
    unsigned char tmp[8];
    if (!sink || !v) return (dom_abi_result)-1;

    solver_write_u32_le(tmp, CORE_SOLVER_ACTUAL_TAG_TYPE);
    memcpy(buf + off, tmp, 4u); off += 4u;
    solver_write_u32_le(tmp, 4u);
    memcpy(buf + off, tmp, 4u); off += 4u;
    solver_write_u32_le(tmp, (u32)type);
    memcpy(buf + off, tmp, 4u); off += 4u;

    switch (type) {
    case CORE_CAP_BOOL:
    case CORE_CAP_U32:
    case CORE_CAP_ENUM_ID:
    case CORE_CAP_STRING_ID:
        solver_write_u32_le(tmp, CORE_SOLVER_ACTUAL_TAG_VALUE_U32);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, v->u32_value);
        memcpy(buf + off, tmp, 4u); off += 4u;
        break;
    case CORE_CAP_I32:
        solver_write_u32_le(tmp, CORE_SOLVER_ACTUAL_TAG_VALUE_I32);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, (u32)v->i32_value);
        memcpy(buf + off, tmp, 4u); off += 4u;
        break;
    case CORE_CAP_U64:
        solver_write_u32_le(tmp, CORE_SOLVER_ACTUAL_TAG_VALUE_U64);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 8u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u64_le(tmp, v->u64_value);
        memcpy(buf + off, tmp, 8u); off += 8u;
        break;
    case CORE_CAP_I64:
        solver_write_u32_le(tmp, CORE_SOLVER_ACTUAL_TAG_VALUE_I64);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 8u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u64_le(tmp, (u64)v->i64_value);
        memcpy(buf + off, tmp, 8u); off += 8u;
        break;
    case CORE_CAP_RANGE_U32:
        solver_write_u32_le(tmp, CORE_SOLVER_ACTUAL_TAG_RANGE_MIN);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, v->range_u32.min_value);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, CORE_SOLVER_ACTUAL_TAG_RANGE_MAX);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, 4u);
        memcpy(buf + off, tmp, 4u); off += 4u;
        solver_write_u32_le(tmp, v->range_u32.max_value);
        memcpy(buf + off, tmp, 4u); off += 4u;
        break;
    default:
        break;
    }

    return solver_write_record(sink, CORE_SOLVER_REJ_TAG_ACTUAL, buf, off);
}

dom_abi_result core_solver_explain_write_tlv(const core_solver_result* result, const core_solver_write_sink* sink) {
    unsigned char tmp[8];
    u32 i;
    if (!result || !sink || !sink->write) return (dom_abi_result)-1;

    solver_write_u32_le(tmp, CORE_SOLVER_TLV_VERSION);
    if (solver_write_record(sink, CORE_SOLVER_TLV_TAG_SCHEMA_VERSION, tmp, 4u) != 0) {
        return (dom_abi_result)-1;
    }

    for (i = 0u; i < result->selected_count; ++i) {
        const core_solver_selected* s = &result->selected[i];
        u32 payload = 0u;
        u32 len_id = (u32)strlen(s->component_id);
        payload += 8u + 4u;
        payload += 8u + len_id;
        payload += 8u + 4u;
        payload += 8u + 4u;
        payload += 8u + 4u;
        payload += 8u + 4u;

        solver_write_u32_le(tmp, CORE_SOLVER_TLV_TAG_SELECTED);
        solver_write_u32_le(tmp + 4, payload);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;

        solver_write_u32_le(tmp, CORE_SOLVER_SEL_TAG_CATEGORY_ID);
        solver_write_u32_le(tmp + 4, 4u);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;
        solver_write_u32_le(tmp, s->category_id);
        if (solver_sink_write(sink, tmp, 4u) != 0) return (dom_abi_result)-1;

        solver_write_u32_le(tmp, CORE_SOLVER_SEL_TAG_COMPONENT_ID);
        solver_write_u32_le(tmp + 4, len_id);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;
        if (len_id > 0u && solver_sink_write(sink, (const unsigned char*)s->component_id, len_id) != 0) {
            return (dom_abi_result)-1;
        }

        solver_write_u32_le(tmp, CORE_SOLVER_SEL_TAG_REASON);
        solver_write_u32_le(tmp + 4, 4u);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;
        solver_write_u32_le(tmp, s->reason);
        if (solver_sink_write(sink, tmp, 4u) != 0) return (dom_abi_result)-1;

        solver_write_u32_le(tmp, CORE_SOLVER_SEL_TAG_SCORE);
        solver_write_u32_le(tmp + 4, 4u);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;
        solver_write_u32_le(tmp, s->score);
        if (solver_sink_write(sink, tmp, 4u) != 0) return (dom_abi_result)-1;

        solver_write_u32_le(tmp, CORE_SOLVER_SEL_TAG_PRIORITY);
        solver_write_u32_le(tmp + 4, 4u);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;
        solver_write_u32_le(tmp, s->priority);
        if (solver_sink_write(sink, tmp, 4u) != 0) return (dom_abi_result)-1;

        solver_write_u32_le(tmp, CORE_SOLVER_SEL_TAG_PREFERS_SAT);
        solver_write_u32_le(tmp + 4, 4u);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;
        solver_write_u32_le(tmp, s->prefers_satisfied);
        if (solver_sink_write(sink, tmp, 4u) != 0) return (dom_abi_result)-1;
    }

    for (i = 0u; i < result->rejected_count; ++i) {
        const core_solver_reject* r = &result->rejected[i];
        u32 payload = 0u;
        u32 len_id = (u32)strlen(r->component_id);
        u32 len_conflict = (u32)strlen(r->conflict_component_id);
        payload += 8u + 4u;
        payload += 8u + len_id;
        payload += 8u + 4u;
        if (r->constraint.key_id != 0u) {
            payload += 8u + solver_constraint_payload_size(&r->constraint);
        }
        if (r->actual_present) {
            payload += 8u + solver_actual_payload_size(r->actual_type);
        }
        if (len_conflict > 0u) {
            payload += 8u + len_conflict;
        }

        solver_write_u32_le(tmp, CORE_SOLVER_TLV_TAG_REJECTED);
        solver_write_u32_le(tmp + 4, payload);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;

        solver_write_u32_le(tmp, CORE_SOLVER_REJ_TAG_CATEGORY_ID);
        solver_write_u32_le(tmp + 4, 4u);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;
        solver_write_u32_le(tmp, r->category_id);
        if (solver_sink_write(sink, tmp, 4u) != 0) return (dom_abi_result)-1;

        solver_write_u32_le(tmp, CORE_SOLVER_REJ_TAG_COMPONENT_ID);
        solver_write_u32_le(tmp + 4, len_id);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;
        if (len_id > 0u && solver_sink_write(sink, (const unsigned char*)r->component_id, len_id) != 0) {
            return (dom_abi_result)-1;
        }

        solver_write_u32_le(tmp, CORE_SOLVER_REJ_TAG_REASON);
        solver_write_u32_le(tmp + 4, 4u);
        if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;
        solver_write_u32_le(tmp, r->reason);
        if (solver_sink_write(sink, tmp, 4u) != 0) return (dom_abi_result)-1;

        if (r->constraint.key_id != 0u) {
            if (solver_write_constraint(sink, &r->constraint) != 0) {
                return (dom_abi_result)-1;
            }
        }
        if (r->actual_present) {
            if (solver_write_actual(sink, r->actual_type, &r->actual_value) != 0) {
                return (dom_abi_result)-1;
            }
        }
        if (len_conflict > 0u) {
            solver_write_u32_le(tmp, CORE_SOLVER_REJ_TAG_CONFLICT_ID);
            solver_write_u32_le(tmp + 4, len_conflict);
            if (solver_sink_write(sink, tmp, 8u) != 0) return (dom_abi_result)-1;
            if (solver_sink_write(sink, (const unsigned char*)r->conflict_component_id, len_conflict) != 0) {
                return (dom_abi_result)-1;
            }
        }
    }

    return 0;
}

dom_abi_result core_solver_explain_read_tlv(const unsigned char* data, u32 size, core_solver_result* out_result, u32* out_used) {
    u32 off = 0u;
    u32 schema_version = 0u;
    int saw_version = 0;
    if (!data || !out_result) return (dom_abi_result)-1;

    core_solver_result_clear(out_result);

    while (off + 8u <= size) {
        u32 tag = 0u;
        u32 len = 0u;
        if (!solver_read_u32_le(data + off, 4u, &tag) ||
            !solver_read_u32_le(data + off + 4u, 4u, &len)) {
            return (dom_abi_result)-1;
        }
        off += 8u;
        if (off + len > size) {
            return (dom_abi_result)-1;
        }
        if (tag == CORE_SOLVER_TLV_TAG_SCHEMA_VERSION) {
            if (len == 4u && solver_read_u32_le(data + off, len, &schema_version)) {
                saw_version = 1;
            }
        } else if (tag == CORE_SOLVER_TLV_TAG_SELECTED) {
            u32 entry_off = 0u;
            core_solver_selected s;
            memset(&s, 0, sizeof(s));
            while (entry_off + 8u <= len) {
                u32 etag = 0u;
                u32 elen = 0u;
                if (!solver_read_u32_le(data + off + entry_off, 4u, &etag) ||
                    !solver_read_u32_le(data + off + entry_off + 4u, 4u, &elen)) {
                    return (dom_abi_result)-1;
                }
                entry_off += 8u;
                if (entry_off + elen > len) {
                    return (dom_abi_result)-1;
                }
                switch (etag) {
                case CORE_SOLVER_SEL_TAG_CATEGORY_ID:
                    solver_read_u32_le(data + off + entry_off, elen, &s.category_id);
                    break;
                case CORE_SOLVER_SEL_TAG_COMPONENT_ID: {
                    u32 copy = (elen + 1u < CORE_SOLVER_MAX_ID) ? elen : (CORE_SOLVER_MAX_ID - 1u);
                    memcpy(s.component_id, data + off + entry_off, copy);
                    s.component_id[copy] = '\0';
                    break;
                }
                case CORE_SOLVER_SEL_TAG_REASON:
                    solver_read_u32_le(data + off + entry_off, elen, &s.reason);
                    break;
                case CORE_SOLVER_SEL_TAG_SCORE:
                    solver_read_u32_le(data + off + entry_off, elen, &s.score);
                    break;
                case CORE_SOLVER_SEL_TAG_PRIORITY:
                    solver_read_u32_le(data + off + entry_off, elen, &s.priority);
                    break;
                case CORE_SOLVER_SEL_TAG_PREFERS_SAT:
                    solver_read_u32_le(data + off + entry_off, elen, &s.prefers_satisfied);
                    break;
                default:
                    break;
                }
                entry_off += elen;
            }
            if (out_result->selected_count < CORE_SOLVER_MAX_SELECTION) {
                out_result->selected[out_result->selected_count++] = s;
            }
        } else if (tag == CORE_SOLVER_TLV_TAG_REJECTED) {
            u32 entry_off = 0u;
            core_solver_reject r;
            memset(&r, 0, sizeof(r));
            while (entry_off + 8u <= len) {
                u32 etag = 0u;
                u32 elen = 0u;
                if (!solver_read_u32_le(data + off + entry_off, 4u, &etag) ||
                    !solver_read_u32_le(data + off + entry_off + 4u, 4u, &elen)) {
                    return (dom_abi_result)-1;
                }
                entry_off += 8u;
                if (entry_off + elen > len) {
                    return (dom_abi_result)-1;
                }
                switch (etag) {
                case CORE_SOLVER_REJ_TAG_CATEGORY_ID:
                    solver_read_u32_le(data + off + entry_off, elen, &r.category_id);
                    break;
                case CORE_SOLVER_REJ_TAG_COMPONENT_ID: {
                    u32 copy = (elen + 1u < CORE_SOLVER_MAX_ID) ? elen : (CORE_SOLVER_MAX_ID - 1u);
                    memcpy(r.component_id, data + off + entry_off, copy);
                    r.component_id[copy] = '\0';
                    break;
                }
                case CORE_SOLVER_REJ_TAG_REASON:
                    solver_read_u32_le(data + off + entry_off, elen, &r.reason);
                    break;
                case CORE_SOLVER_REJ_TAG_CONFLICT_ID: {
                    u32 copy = (elen + 1u < CORE_SOLVER_MAX_ID) ? elen : (CORE_SOLVER_MAX_ID - 1u);
                    memcpy(r.conflict_component_id, data + off + entry_off, copy);
                    r.conflict_component_id[copy] = '\0';
                    break;
                }
                case CORE_SOLVER_REJ_TAG_CONSTRAINT: {
                    u32 c_off = 0u;
                    while (c_off + 8u <= elen) {
                        u32 ctag = 0u;
                        u32 clen = 0u;
                        if (!solver_read_u32_le(data + off + entry_off + c_off, 4u, &ctag) ||
                            !solver_read_u32_le(data + off + entry_off + c_off + 4u, 4u, &clen)) {
                            return (dom_abi_result)-1;
                        }
                        c_off += 8u;
                        if (c_off + clen > elen) return (dom_abi_result)-1;
                        switch (ctag) {
                        case CORE_SOLVER_CONSTRAINT_TAG_KEY_ID:
                            solver_read_u32_le(data + off + entry_off + c_off, clen, &r.constraint.key_id);
                            break;
                        case CORE_SOLVER_CONSTRAINT_TAG_OP:
                            solver_read_u32_le(data + off + entry_off + c_off, clen, &r.constraint.op);
                            break;
                        case CORE_SOLVER_CONSTRAINT_TAG_TYPE: {
                            u32 v = 0u;
                            if (solver_read_u32_le(data + off + entry_off + c_off, clen, &v)) {
                                r.constraint.type = (u8)v;
                            }
                            break;
                        }
                        case CORE_SOLVER_CONSTRAINT_TAG_WEIGHT:
                            solver_read_u32_le(data + off + entry_off + c_off, clen, &r.constraint.weight);
                            break;
                        case CORE_SOLVER_CONSTRAINT_TAG_VALUE_U32:
                            solver_read_u32_le(data + off + entry_off + c_off, clen, &r.constraint.value.u32_value);
                            break;
                        case CORE_SOLVER_CONSTRAINT_TAG_VALUE_I32:
                            solver_read_i32_le(data + off + entry_off + c_off, clen, &r.constraint.value.i32_value);
                            break;
                        case CORE_SOLVER_CONSTRAINT_TAG_VALUE_U64:
                            solver_read_u64_le(data + off + entry_off + c_off, clen, &r.constraint.value.u64_value);
                            break;
                        case CORE_SOLVER_CONSTRAINT_TAG_VALUE_I64:
                            solver_read_i64_le(data + off + entry_off + c_off, clen, &r.constraint.value.i64_value);
                            break;
                        case CORE_SOLVER_CONSTRAINT_TAG_RANGE_MIN:
                            solver_read_u32_le(data + off + entry_off + c_off, clen, &r.constraint.value.range_u32.min_value);
                            break;
                        case CORE_SOLVER_CONSTRAINT_TAG_RANGE_MAX:
                            solver_read_u32_le(data + off + entry_off + c_off, clen, &r.constraint.value.range_u32.max_value);
                            break;
                        default:
                            break;
                        }
                        c_off += clen;
                    }
                    break;
                }
                case CORE_SOLVER_REJ_TAG_ACTUAL: {
                    u32 a_off = 0u;
                    r.actual_present = 1u;
                    while (a_off + 8u <= elen) {
                        u32 atag = 0u;
                        u32 alen = 0u;
                        if (!solver_read_u32_le(data + off + entry_off + a_off, 4u, &atag) ||
                            !solver_read_u32_le(data + off + entry_off + a_off + 4u, 4u, &alen)) {
                            return (dom_abi_result)-1;
                        }
                        a_off += 8u;
                        if (a_off + alen > elen) return (dom_abi_result)-1;
                        switch (atag) {
                        case CORE_SOLVER_ACTUAL_TAG_TYPE: {
                            u32 v = 0u;
                            if (solver_read_u32_le(data + off + entry_off + a_off, alen, &v)) {
                                r.actual_type = (u8)v;
                            }
                            break;
                        }
                        case CORE_SOLVER_ACTUAL_TAG_VALUE_U32:
                            solver_read_u32_le(data + off + entry_off + a_off, alen, &r.actual_value.u32_value);
                            break;
                        case CORE_SOLVER_ACTUAL_TAG_VALUE_I32:
                            solver_read_i32_le(data + off + entry_off + a_off, alen, &r.actual_value.i32_value);
                            break;
                        case CORE_SOLVER_ACTUAL_TAG_VALUE_U64:
                            solver_read_u64_le(data + off + entry_off + a_off, alen, &r.actual_value.u64_value);
                            break;
                        case CORE_SOLVER_ACTUAL_TAG_VALUE_I64:
                            solver_read_i64_le(data + off + entry_off + a_off, alen, &r.actual_value.i64_value);
                            break;
                        case CORE_SOLVER_ACTUAL_TAG_RANGE_MIN:
                            solver_read_u32_le(data + off + entry_off + a_off, alen, &r.actual_value.range_u32.min_value);
                            break;
                        case CORE_SOLVER_ACTUAL_TAG_RANGE_MAX:
                            solver_read_u32_le(data + off + entry_off + a_off, alen, &r.actual_value.range_u32.max_value);
                            break;
                        default:
                            break;
                        }
                        a_off += alen;
                    }
                    break;
                }
                default:
                    break;
                }
                entry_off += elen;
            }
            if (out_result->rejected_count < CORE_SOLVER_MAX_REJECTIONS) {
                out_result->rejected[out_result->rejected_count++] = r;
            }
        }
        off += len;
    }
    if (out_used) {
        *out_used = off;
    }
    if (saw_version && schema_version != CORE_SOLVER_TLV_VERSION) {
        return (dom_abi_result)-1;
    }
    return 0;
}
