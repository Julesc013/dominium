/*
FILE: source/dominium/common/core_job.c
MODULE: Dominium
PURPOSE: Resumable job helpers + deterministic TLV encoding.
*/
#include "dominium/core_job.h"

#include <string.h>

/*------------------------------------------------------------
 * TLV tags.
 *------------------------------------------------------------*/
enum {
    CORE_JOB_TLV_TAG_DEF = 1u,
    CORE_JOB_TLV_TAG_DEF_SCHEMA = 2u,
    CORE_JOB_TLV_TAG_DEF_JOB_TYPE = 3u,
    CORE_JOB_TLV_TAG_DEF_STEP_COUNT = 4u,
    CORE_JOB_TLV_TAG_DEF_STEP = 5u,

    CORE_JOB_TLV_TAG_STATE = 10u,
    CORE_JOB_TLV_TAG_STATE_SCHEMA = 11u,
    CORE_JOB_TLV_TAG_STATE_JOB_ID = 12u,
    CORE_JOB_TLV_TAG_STATE_JOB_TYPE = 13u,
    CORE_JOB_TLV_TAG_STATE_CURRENT_STEP = 14u,
    CORE_JOB_TLV_TAG_STATE_COMPLETED = 15u,
    CORE_JOB_TLV_TAG_STATE_OUTCOME = 16u,
    CORE_JOB_TLV_TAG_STATE_RETRY = 17u,
    CORE_JOB_TLV_TAG_STATE_RETRY_ENTRY = 18u,
    CORE_JOB_TLV_TAG_STATE_LAST_ERROR = 19u
};

enum {
    CORE_JOB_TLV_TAG_STEP_ID = 1u,
    CORE_JOB_TLV_TAG_STEP_FLAGS = 2u,
    CORE_JOB_TLV_TAG_STEP_DEP_COUNT = 3u,
    CORE_JOB_TLV_TAG_STEP_DEP = 4u
};

enum {
    CORE_JOB_TLV_TAG_RETRY_INDEX = 1u,
    CORE_JOB_TLV_TAG_RETRY_COUNT = 2u
};

enum {
    CORE_JOB_TLV_TAG_ERR_DOMAIN = 1u,
    CORE_JOB_TLV_TAG_ERR_CODE = 2u,
    CORE_JOB_TLV_TAG_ERR_FLAGS = 3u,
    CORE_JOB_TLV_TAG_ERR_MSG_ID = 4u,
    CORE_JOB_TLV_TAG_ERR_DETAIL_COUNT = 5u,
    CORE_JOB_TLV_TAG_ERR_DETAIL = 6u
};

enum {
    CORE_JOB_TLV_TAG_ERR_DETAIL_KEY = 1u,
    CORE_JOB_TLV_TAG_ERR_DETAIL_TYPE = 2u,
    CORE_JOB_TLV_TAG_ERR_DETAIL_U32 = 3u,
    CORE_JOB_TLV_TAG_ERR_DETAIL_U64 = 4u
};

/*------------------------------------------------------------
 * Helpers.
 *------------------------------------------------------------*/
static void core_job_write_u32_le(unsigned char out[4], u32 v) {
    out[0] = (unsigned char)(v & 0xFFu);
    out[1] = (unsigned char)((v >> 8u) & 0xFFu);
    out[2] = (unsigned char)((v >> 16u) & 0xFFu);
    out[3] = (unsigned char)((v >> 24u) & 0xFFu);
}

static void core_job_write_u64_le(unsigned char out[8], u64 v) {
    core_job_write_u32_le(out, (u32)(v & 0xFFFFFFFFull));
    core_job_write_u32_le(out + 4, (u32)((v >> 32u) & 0xFFFFFFFFull));
}

static u32 core_job_read_u32_le(const unsigned char* p) {
    return (u32)p[0] | ((u32)p[1] << 8u) | ((u32)p[2] << 16u) | ((u32)p[3] << 24u);
}

static u64 core_job_read_u64_le(const unsigned char* p) {
    u64 lo = (u64)core_job_read_u32_le(p);
    u64 hi = (u64)core_job_read_u32_le(p + 4);
    return lo | (hi << 32u);
}

static dom_abi_result core_job_sink_write(const core_job_write_sink* sink,
                                          const void* data,
                                          u32 len) {
    if (!sink || !sink->write) {
        return (dom_abi_result)-1;
    }
    return sink->write(sink->user, data, len);
}

static dom_abi_result core_job_write_tlv_u32(const core_job_write_sink* sink, u32 tag, u32 value) {
    unsigned char hdr[8];
    unsigned char payload[4];
    core_job_write_u32_le(hdr, tag);
    core_job_write_u32_le(hdr + 4, 4u);
    core_job_write_u32_le(payload, value);
    if (core_job_sink_write(sink, hdr, 8u) != 0) return (dom_abi_result)-1;
    if (core_job_sink_write(sink, payload, 4u) != 0) return (dom_abi_result)-1;
    return 0;
}

static dom_abi_result core_job_write_tlv_u64(const core_job_write_sink* sink, u32 tag, u64 value) {
    unsigned char hdr[8];
    unsigned char payload[8];
    core_job_write_u32_le(hdr, tag);
    core_job_write_u32_le(hdr + 4, 8u);
    core_job_write_u64_le(payload, value);
    if (core_job_sink_write(sink, hdr, 8u) != 0) return (dom_abi_result)-1;
    if (core_job_sink_write(sink, payload, 8u) != 0) return (dom_abi_result)-1;
    return 0;
}

static dom_abi_result core_job_write_tlv_bytes(const core_job_write_sink* sink,
                                               u32 tag,
                                               const unsigned char* data,
                                               u32 len) {
    unsigned char hdr[8];
    core_job_write_u32_le(hdr, tag);
    core_job_write_u32_le(hdr + 4, len);
    if (core_job_sink_write(sink, hdr, 8u) != 0) return (dom_abi_result)-1;
    if (len > 0u && data) {
        if (core_job_sink_write(sink, data, len) != 0) return (dom_abi_result)-1;
    }
    return 0;
}

static u32 core_job_step_payload_size(const core_job_step* step) {
    u32 size = 0u;
    u32 i;
    if (!step) {
        return 0u;
    }
    size += 8u + 4u; /* step_id */
    size += 8u + 4u; /* flags */
    size += 8u + 4u; /* depends_on_count */
    for (i = 0u; i < step->depends_on_count && i < CORE_JOB_MAX_DEPS; ++i) {
        size += 8u + 4u; /* depends_on */
    }
    return size;
}

static u32 core_job_def_payload_size(const core_job_def* def) {
    u32 size = 0u;
    u32 i;
    if (!def) {
        return 0u;
    }
    size += 8u + 4u; /* schema_version */
    size += 8u + 4u; /* job_type */
    size += 8u + 4u; /* step_count */
    for (i = 0u; i < def->step_count && i < CORE_JOB_MAX_STEPS; ++i) {
        size += 8u + core_job_step_payload_size(&def->steps[i]);
    }
    return size;
}

static u32 core_job_retry_entry_payload_size(void) {
    u32 size = 0u;
    size += 8u + 4u; /* index */
    size += 8u + 4u; /* count */
    return size;
}

static u32 core_job_err_detail_payload_size(const err_detail* d) {
    u32 size = 0u;
    if (!d) {
        return 0u;
    }
    size += 8u + 4u; /* key */
    size += 8u + 4u; /* type */
    switch (d->type) {
    case ERR_DETAIL_TYPE_U32:
    case ERR_DETAIL_TYPE_MSG_ID:
        size += 8u + 4u;
        break;
    case ERR_DETAIL_TYPE_U64:
    case ERR_DETAIL_TYPE_HASH64:
    case ERR_DETAIL_TYPE_PATH_HASH64:
        size += 8u + 8u;
        break;
    default:
        break;
    }
    return size;
}

static u32 core_job_err_payload_size(const err_t* err) {
    u32 size = 0u;
    u32 i;
    if (!err) {
        return 0u;
    }
    size += 8u + 4u; /* domain */
    size += 8u + 4u; /* code */
    size += 8u + 4u; /* flags */
    size += 8u + 4u; /* msg_id */
    size += 8u + 4u; /* detail_count */
    for (i = 0u; i < err->detail_count && i < (u32)ERR_DETAIL_MAX; ++i) {
        size += 8u + core_job_err_detail_payload_size(&err->details[i]);
    }
    return size;
}

static u32 core_job_state_payload_size(const core_job_state* st) {
    u32 size = 0u;
    u32 i;
    if (!st) {
        return 0u;
    }
    size += 8u + 4u; /* schema_version */
    size += 8u + 8u; /* job_id */
    size += 8u + 4u; /* job_type */
    size += 8u + 4u; /* current_step */
    size += 8u + 4u; /* completed_steps_bitset */
    size += 8u + 4u; /* outcome */
    for (i = 0u; i < CORE_JOB_MAX_STEPS; ++i) {
        size += 8u + core_job_retry_entry_payload_size();
    }
    size += 8u + core_job_err_payload_size(&st->last_error);
    return size;
}

void core_job_def_clear(core_job_def* def) {
    if (!def) {
        return;
    }
    memset(def, 0, sizeof(*def));
    def->schema_version = (u32)CORE_JOB_DEF_TLV_VERSION;
}

void core_job_state_clear(core_job_state* st) {
    if (!st) {
        return;
    }
    memset(st, 0, sizeof(*st));
    st->last_error = err_ok();
    st->outcome = (u32)CORE_JOB_OUTCOME_NONE;
}

void core_job_state_init(core_job_state* st, u64 job_id, u32 job_type, u32 step_count) {
    u32 i;
    if (!st) {
        return;
    }
    core_job_state_clear(st);
    st->job_id = job_id;
    st->job_type = job_type;
    st->current_step = 0u;
    st->completed_steps_bitset = 0u;
    for (i = 0u; i < CORE_JOB_MAX_STEPS; ++i) {
        st->retry_count[i] = 0u;
    }
    if (step_count == 0u || step_count > CORE_JOB_MAX_STEPS) {
        st->outcome = (u32)CORE_JOB_OUTCOME_NONE;
    }
}

int core_job_def_find_step_index(const core_job_def* def, u32 step_id, u32* out_index) {
    u32 i;
    if (!def || step_id == 0u) {
        return 0;
    }
    for (i = 0u; i < def->step_count && i < CORE_JOB_MAX_STEPS; ++i) {
        if (def->steps[i].step_id == step_id) {
            if (out_index) {
                *out_index = i;
            }
            return 1;
        }
    }
    return 0;
}

int core_job_def_validate(const core_job_def* def) {
    u32 i;
    u32 j;
    u32 resolved_count = 0u;
    u8 resolved[CORE_JOB_MAX_STEPS];

    if (!def) {
        return 0;
    }
    if (def->step_count == 0u || def->step_count > CORE_JOB_MAX_STEPS) {
        return 0;
    }
    for (i = 0u; i < def->step_count; ++i) {
        const core_job_step* step = &def->steps[i];
        if (step->step_id == 0u) {
            return 0;
        }
        if (step->depends_on_count > CORE_JOB_MAX_DEPS) {
            return 0;
        }
        for (j = i + 1u; j < def->step_count; ++j) {
            if (step->step_id == def->steps[j].step_id) {
                return 0;
            }
        }
        for (j = 0u; j < step->depends_on_count; ++j) {
            u32 dep = step->depends_on[j];
            u32 idx = 0u;
            if (dep == 0u || dep == step->step_id) {
                return 0;
            }
            if (!core_job_def_find_step_index(def, dep, &idx)) {
                return 0;
            }
        }
    }

    memset(resolved, 0, sizeof(resolved));
    while (resolved_count < def->step_count) {
        u32 progress = 0u;
        for (i = 0u; i < def->step_count; ++i) {
            const core_job_step* step = &def->steps[i];
            u32 dep_ok = 1u;
            if (resolved[i]) {
                continue;
            }
            for (j = 0u; j < step->depends_on_count; ++j) {
                u32 dep_idx = 0u;
                if (!core_job_def_find_step_index(def, step->depends_on[j], &dep_idx)) {
                    dep_ok = 0u;
                    break;
                }
                if (!resolved[dep_idx]) {
                    dep_ok = 0u;
                    break;
                }
            }
            if (dep_ok) {
                resolved[i] = 1u;
                resolved_count += 1u;
                progress = 1u;
            }
        }
        if (!progress) {
            return 0;
        }
    }
    return 1;
}

int core_job_state_step_complete(const core_job_state* st, u32 step_index) {
    if (!st) {
        return 0;
    }
    if (step_index >= CORE_JOB_MAX_STEPS) {
        return 0;
    }
    return ((st->completed_steps_bitset >> step_index) & 1u) ? 1 : 0;
}

void core_job_state_mark_step_complete(core_job_state* st, u32 step_index) {
    if (!st) {
        return;
    }
    if (step_index >= CORE_JOB_MAX_STEPS) {
        return;
    }
    st->completed_steps_bitset |= (1u << step_index);
}

int core_job_state_all_steps_complete(const core_job_def* def, const core_job_state* st) {
    u32 i;
    if (!def || !st) {
        return 0;
    }
    for (i = 0u; i < def->step_count && i < CORE_JOB_MAX_STEPS; ++i) {
        if (!core_job_state_step_complete(st, i)) {
            return 0;
        }
    }
    return 1;
}

int core_job_next_step_index(const core_job_def* def, const core_job_state* st, u32* out_step_index) {
    u32 i;
    if (!def || !st || !out_step_index) {
        return 0;
    }
    for (i = 0u; i < def->step_count && i < CORE_JOB_MAX_STEPS; ++i) {
        const core_job_step* step = &def->steps[i];
        u32 j;
        u32 deps_ok = 1u;
        if (core_job_state_step_complete(st, i)) {
            continue;
        }
        for (j = 0u; j < step->depends_on_count && j < CORE_JOB_MAX_DEPS; ++j) {
            u32 dep_idx = 0u;
            if (!core_job_def_find_step_index(def, step->depends_on[j], &dep_idx)) {
                deps_ok = 0u;
                break;
            }
            if (!core_job_state_step_complete(st, dep_idx)) {
                deps_ok = 0u;
                break;
            }
        }
        if (deps_ok) {
            *out_step_index = i;
            return 1;
        }
    }
    return 0;
}

u32 core_job_def_encoded_size(const core_job_def* def) {
    if (!def) {
        return 0u;
    }
    return 8u + core_job_def_payload_size(def);
}

u32 core_job_state_encoded_size(const core_job_state* st) {
    if (!st) {
        return 0u;
    }
    return 8u + core_job_state_payload_size(st);
}

static dom_abi_result core_job_write_err_tlv(const err_t* err, const core_job_write_sink* sink) {
    u32 payload_len;
    u32 i;
    unsigned char hdr[8];
    if (!err || !sink || !sink->write) {
        return (dom_abi_result)-1;
    }
    payload_len = core_job_err_payload_size(err);
    core_job_write_u32_le(hdr, (u32)CORE_JOB_TLV_TAG_STATE_LAST_ERROR);
    core_job_write_u32_le(hdr + 4, payload_len);
    if (core_job_sink_write(sink, hdr, 8u) != 0) return (dom_abi_result)-1;

    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_ERR_DOMAIN, (u32)err->domain) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_ERR_CODE, (u32)err->code) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_ERR_FLAGS, (u32)err->flags) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_ERR_MSG_ID, (u32)err->msg_id) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_ERR_DETAIL_COUNT, (u32)err->detail_count) != 0) return (dom_abi_result)-1;

    for (i = 0u; i < err->detail_count && i < (u32)ERR_DETAIL_MAX; ++i) {
        const err_detail* d = &err->details[i];
        u32 detail_payload = core_job_err_detail_payload_size(d);
        unsigned char dhdr[8];
        core_job_write_u32_le(dhdr, (u32)CORE_JOB_TLV_TAG_ERR_DETAIL);
        core_job_write_u32_le(dhdr + 4, detail_payload);
        if (core_job_sink_write(sink, dhdr, 8u) != 0) return (dom_abi_result)-1;

        if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_ERR_DETAIL_KEY, d->key_id) != 0) return (dom_abi_result)-1;
        if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_ERR_DETAIL_TYPE, d->type) != 0) return (dom_abi_result)-1;
        switch (d->type) {
        case ERR_DETAIL_TYPE_U32:
        case ERR_DETAIL_TYPE_MSG_ID:
            if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_ERR_DETAIL_U32, d->v.u32_value) != 0) return (dom_abi_result)-1;
            break;
        case ERR_DETAIL_TYPE_U64:
        case ERR_DETAIL_TYPE_HASH64:
        case ERR_DETAIL_TYPE_PATH_HASH64:
            if (core_job_write_tlv_u64(sink, CORE_JOB_TLV_TAG_ERR_DETAIL_U64, d->v.u64_value) != 0) return (dom_abi_result)-1;
            break;
        default:
            break;
        }
    }
    return 0;
}

dom_abi_result core_job_def_write_tlv(const core_job_def* def, const core_job_write_sink* sink) {
    u32 payload_len;
    u32 i;
    unsigned char hdr[8];
    if (!def || !sink || !sink->write) {
        return (dom_abi_result)-1;
    }
    payload_len = core_job_def_payload_size(def);
    core_job_write_u32_le(hdr, (u32)CORE_JOB_TLV_TAG_DEF);
    core_job_write_u32_le(hdr + 4, payload_len);
    if (core_job_sink_write(sink, hdr, 8u) != 0) return (dom_abi_result)-1;

    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_DEF_SCHEMA, def->schema_version) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_DEF_JOB_TYPE, def->job_type) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_DEF_STEP_COUNT, def->step_count) != 0) return (dom_abi_result)-1;

    for (i = 0u; i < def->step_count && i < CORE_JOB_MAX_STEPS; ++i) {
        const core_job_step* step = &def->steps[i];
        u32 step_payload = core_job_step_payload_size(step);
        unsigned char shdr[8];
        u32 j;
        core_job_write_u32_le(shdr, (u32)CORE_JOB_TLV_TAG_DEF_STEP);
        core_job_write_u32_le(shdr + 4, step_payload);
        if (core_job_sink_write(sink, shdr, 8u) != 0) return (dom_abi_result)-1;

        if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_STEP_ID, step->step_id) != 0) return (dom_abi_result)-1;
        if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_STEP_FLAGS, step->flags) != 0) return (dom_abi_result)-1;
        if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_STEP_DEP_COUNT, step->depends_on_count) != 0) return (dom_abi_result)-1;
        for (j = 0u; j < step->depends_on_count && j < CORE_JOB_MAX_DEPS; ++j) {
            if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_STEP_DEP, step->depends_on[j]) != 0) return (dom_abi_result)-1;
        }
    }
    return 0;
}

dom_abi_result core_job_state_write_tlv(const core_job_state* st, const core_job_write_sink* sink) {
    u32 payload_len;
    u32 i;
    unsigned char hdr[8];
    if (!st || !sink || !sink->write) {
        return (dom_abi_result)-1;
    }
    payload_len = core_job_state_payload_size(st);
    core_job_write_u32_le(hdr, (u32)CORE_JOB_TLV_TAG_STATE);
    core_job_write_u32_le(hdr + 4, payload_len);
    if (core_job_sink_write(sink, hdr, 8u) != 0) return (dom_abi_result)-1;

    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_STATE_SCHEMA, (u32)CORE_JOB_STATE_TLV_VERSION) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u64(sink, CORE_JOB_TLV_TAG_STATE_JOB_ID, st->job_id) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_STATE_JOB_TYPE, st->job_type) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_STATE_CURRENT_STEP, st->current_step) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_STATE_COMPLETED, st->completed_steps_bitset) != 0) return (dom_abi_result)-1;
    if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_STATE_OUTCOME, st->outcome) != 0) return (dom_abi_result)-1;

    for (i = 0u; i < CORE_JOB_MAX_STEPS; ++i) {
        unsigned char rhdr[8];
        core_job_write_u32_le(rhdr, (u32)CORE_JOB_TLV_TAG_STATE_RETRY_ENTRY);
        core_job_write_u32_le(rhdr + 4, core_job_retry_entry_payload_size());
        if (core_job_sink_write(sink, rhdr, 8u) != 0) return (dom_abi_result)-1;
        if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_RETRY_INDEX, i) != 0) return (dom_abi_result)-1;
        if (core_job_write_tlv_u32(sink, CORE_JOB_TLV_TAG_RETRY_COUNT, st->retry_count[i]) != 0) return (dom_abi_result)-1;
    }

    if (core_job_write_err_tlv(&st->last_error, sink) != 0) return (dom_abi_result)-1;
    return 0;
}

static dom_abi_result core_job_read_err_tlv(const unsigned char* data,
                                            u32 size,
                                            err_t* out_err) {
    u32 off = 0u;
    err_t err;
    if (!data || size < 8u || !out_err) {
        return (dom_abi_result)-1;
    }
    err = err_ok();
    while (off + 8u <= size) {
        u32 tag = core_job_read_u32_le(data + off);
        u32 len = core_job_read_u32_le(data + off + 4u);
        const unsigned char* payload = data + off + 8u;
        off += 8u;
        if (off + len > size) {
            return (dom_abi_result)-1;
        }

        switch (tag) {
        case CORE_JOB_TLV_TAG_ERR_DOMAIN:
            if (len == 4u) err.domain = (u16)core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_ERR_CODE:
            if (len == 4u) err.code = (u16)core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_ERR_FLAGS:
            if (len == 4u) err.flags = core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_ERR_MSG_ID:
            if (len == 4u) err.msg_id = core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_ERR_DETAIL:
            if (len > 0u && err.detail_count < (u32)ERR_DETAIL_MAX) {
                err_detail d;
                u32 doff = 0u;
                u32 dend = len;
                memset(&d, 0, sizeof(d));
                while (doff + 8u <= dend) {
                    u32 dtag = core_job_read_u32_le(payload + doff);
                    u32 dlen = core_job_read_u32_le(payload + doff + 4u);
                    const unsigned char* dpl = payload + doff + 8u;
                    doff += 8u;
                    if (doff + dlen > dend) {
                        break;
                    }
                    switch (dtag) {
                    case CORE_JOB_TLV_TAG_ERR_DETAIL_KEY:
                        if (dlen == 4u) d.key_id = core_job_read_u32_le(dpl);
                        break;
                    case CORE_JOB_TLV_TAG_ERR_DETAIL_TYPE:
                        if (dlen == 4u) d.type = core_job_read_u32_le(dpl);
                        break;
                    case CORE_JOB_TLV_TAG_ERR_DETAIL_U32:
                        if (dlen == 4u) d.v.u32_value = core_job_read_u32_le(dpl);
                        break;
                    case CORE_JOB_TLV_TAG_ERR_DETAIL_U64:
                        if (dlen == 8u) d.v.u64_value = core_job_read_u64_le(dpl);
                        break;
                    default:
                        break;
                    }
                    doff += dlen;
                }
                err.details[err.detail_count] = d;
                err.detail_count += 1u;
            }
            break;
        default:
            break;
        }

        off += len;
    }
    *out_err = err;
    return 0;
}

dom_abi_result core_job_def_read_tlv(const unsigned char* data, u32 size, core_job_def* out_def) {
    u32 off = 0u;
    u32 end = 0u;
    u32 schema_version = 0u;
    u32 step_count = 0u;
    core_job_def def;

    if (!data || size < 8u || !out_def) {
        return (dom_abi_result)-1;
    }
    core_job_def_clear(&def);

    if (core_job_read_u32_le(data) != (u32)CORE_JOB_TLV_TAG_DEF) {
        return (dom_abi_result)-1;
    }
    end = 8u + core_job_read_u32_le(data + 4);
    if (end > size) {
        return (dom_abi_result)-1;
    }

    off = 8u;
    while (off + 8u <= end) {
        u32 tag = core_job_read_u32_le(data + off);
        u32 len = core_job_read_u32_le(data + off + 4u);
        const unsigned char* payload = data + off + 8u;
        off += 8u;
        if (off + len > end) {
            return (dom_abi_result)-1;
        }
        switch (tag) {
        case CORE_JOB_TLV_TAG_DEF_SCHEMA:
            if (len == 4u) schema_version = core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_DEF_JOB_TYPE:
            if (len == 4u) def.job_type = core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_DEF_STEP_COUNT:
            if (len == 4u) step_count = core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_DEF_STEP:
            if (len > 0u && def.step_count < CORE_JOB_MAX_STEPS) {
                core_job_step step;
                u32 soff = 0u;
                u32 send = len;
                memset(&step, 0, sizeof(step));
                while (soff + 8u <= send) {
                    u32 stag = core_job_read_u32_le(payload + soff);
                    u32 slen = core_job_read_u32_le(payload + soff + 4u);
                    const unsigned char* spl = payload + soff + 8u;
                    soff += 8u;
                    if (soff + slen > send) {
                        break;
                    }
                    switch (stag) {
                    case CORE_JOB_TLV_TAG_STEP_ID:
                        if (slen == 4u) step.step_id = core_job_read_u32_le(spl);
                        break;
                    case CORE_JOB_TLV_TAG_STEP_FLAGS:
                        if (slen == 4u) step.flags = core_job_read_u32_le(spl);
                        break;
                    case CORE_JOB_TLV_TAG_STEP_DEP_COUNT:
                        if (slen == 4u) step.depends_on_count = core_job_read_u32_le(spl);
                        break;
                    case CORE_JOB_TLV_TAG_STEP_DEP:
                        if (slen == 4u && step.depends_on_count < CORE_JOB_MAX_DEPS) {
                            step.depends_on[step.depends_on_count] = core_job_read_u32_le(spl);
                            step.depends_on_count += 1u;
                        }
                        break;
                    default:
                        break;
                    }
                    soff += slen;
                }
                def.steps[def.step_count] = step;
                def.step_count += 1u;
            }
            break;
        default:
            break;
        }
        off += len;
    }

    def.schema_version = schema_version ? schema_version : (u32)CORE_JOB_DEF_TLV_VERSION;
    if (def.schema_version > (u32)CORE_JOB_DEF_TLV_VERSION || def.schema_version == 0u) {
        return (dom_abi_result)-1;
    }
    if (step_count != 0u && def.step_count != step_count) {
        /* keep parsed steps; caller can validate */
    }
    *out_def = def;
    return 0;
}

dom_abi_result core_job_state_read_tlv(const unsigned char* data, u32 size, core_job_state* out_st) {
    u32 off = 0u;
    u32 end = 0u;
    u32 schema_version = 0u;
    core_job_state st;

    if (!data || size < 8u || !out_st) {
        return (dom_abi_result)-1;
    }
    core_job_state_clear(&st);

    if (core_job_read_u32_le(data) != (u32)CORE_JOB_TLV_TAG_STATE) {
        return (dom_abi_result)-1;
    }
    end = 8u + core_job_read_u32_le(data + 4);
    if (end > size) {
        return (dom_abi_result)-1;
    }

    off = 8u;
    while (off + 8u <= end) {
        u32 tag = core_job_read_u32_le(data + off);
        u32 len = core_job_read_u32_le(data + off + 4u);
        const unsigned char* payload = data + off + 8u;
        off += 8u;
        if (off + len > end) {
            return (dom_abi_result)-1;
        }

        switch (tag) {
        case CORE_JOB_TLV_TAG_STATE_SCHEMA:
            if (len == 4u) schema_version = core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_STATE_JOB_ID:
            if (len == 8u) st.job_id = core_job_read_u64_le(payload);
            break;
        case CORE_JOB_TLV_TAG_STATE_JOB_TYPE:
            if (len == 4u) st.job_type = core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_STATE_CURRENT_STEP:
            if (len == 4u) st.current_step = core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_STATE_COMPLETED:
            if (len == 4u) st.completed_steps_bitset = core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_STATE_OUTCOME:
            if (len == 4u) st.outcome = core_job_read_u32_le(payload);
            break;
        case CORE_JOB_TLV_TAG_STATE_RETRY_ENTRY:
            if (len > 0u) {
                u32 roff = 0u;
                u32 rend = len;
                u32 idx = 0u;
                u32 count = 0u;
                while (roff + 8u <= rend) {
                    u32 rtag = core_job_read_u32_le(payload + roff);
                    u32 rlen = core_job_read_u32_le(payload + roff + 4u);
                    const unsigned char* rpl = payload + roff + 8u;
                    roff += 8u;
                    if (roff + rlen > rend) {
                        break;
                    }
                    if (rtag == CORE_JOB_TLV_TAG_RETRY_INDEX && rlen == 4u) {
                        idx = core_job_read_u32_le(rpl);
                    } else if (rtag == CORE_JOB_TLV_TAG_RETRY_COUNT && rlen == 4u) {
                        count = core_job_read_u32_le(rpl);
                    }
                    roff += rlen;
                }
                if (idx < CORE_JOB_MAX_STEPS) {
                    st.retry_count[idx] = count;
                }
            }
            break;
        case CORE_JOB_TLV_TAG_STATE_LAST_ERROR:
            if (len > 0u) {
                (void)core_job_read_err_tlv(payload, len, &st.last_error);
            }
            break;
        default:
            break;
        }

        off += len;
    }

    if (schema_version > (u32)CORE_JOB_STATE_TLV_VERSION || schema_version == 0u) {
        return (dom_abi_result)-1;
    }
    *out_st = st;
    return 0;
}
