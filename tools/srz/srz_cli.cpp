/*
FILE: tools/srz/srz_cli.cpp
MODULE: Dominium
PURPOSE: SRZ fixture CLI for deterministic verification checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/srz_fields.h"

#define SRZ_FIXTURE_HEADER "DOMINIUM_SRZ_FIXTURE_V1"

#define SRZ_VALIDATE_HEADER "DOMINIUM_SRZ_VALIDATE_V1"
#define SRZ_INSPECT_HEADER "DOMINIUM_SRZ_INSPECT_V1"
#define SRZ_RESOLVE_HEADER "DOMINIUM_SRZ_RESOLVE_V1"
#define SRZ_COLLAPSE_HEADER "DOMINIUM_SRZ_COLLAPSE_V1"

#define SRZ_PROVIDER_CHAIN "zones->assignments->policies->logs->hashchain->deltas"

#define SRZ_LINE_MAX 512u

typedef struct srz_fixture {
    char fixture_id[96];
    dom_srz_surface_desc srz_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char zone_names[DOM_SRZ_MAX_ZONES][64];
    char assignment_names[DOM_SRZ_MAX_ASSIGNMENTS][64];
    char policy_names[DOM_SRZ_MAX_POLICIES][64];
    char log_names[DOM_SRZ_MAX_LOGS][64];
    char chain_names[DOM_SRZ_MAX_LOGS][64];
    char delta_names[DOM_SRZ_MAX_DELTAS][64];
    char region_names[DOM_SRZ_MAX_REGIONS][64];
    u32 region_ids[DOM_SRZ_MAX_REGIONS];
    u32 region_count;
} srz_fixture;

static u64 srz_hash_u64(u64 h, u64 v)
{
    unsigned char bytes[8];
    bytes[0] = (unsigned char)((v >> 56) & 0xFFu);
    bytes[1] = (unsigned char)((v >> 48) & 0xFFu);
    bytes[2] = (unsigned char)((v >> 40) & 0xFFu);
    bytes[3] = (unsigned char)((v >> 32) & 0xFFu);
    bytes[4] = (unsigned char)((v >> 24) & 0xFFu);
    bytes[5] = (unsigned char)((v >> 16) & 0xFFu);
    bytes[6] = (unsigned char)((v >> 8) & 0xFFu);
    bytes[7] = (unsigned char)(v & 0xFFu);
    for (u32 i = 0u; i < 8u; ++i) {
        h ^= (u64)bytes[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 srz_hash_u32(u64 h, u32 v)
{
    return srz_hash_u64(h, (u64)v);
}

static u64 srz_hash_q16(u64 h, q16_16 v)
{
    return srz_hash_u64(h, (u64)(u32)v);
}

static char* srz_trim(char* text)
{
    char* end;
    while (text && *text && isspace((unsigned char)*text)) {
        ++text;
    }
    if (!text || !*text) {
        return text;
    }
    end = text + strlen(text);
    while (end > text && isspace((unsigned char)end[-1])) {
        --end;
    }
    *end = '\0';
    return text;
}

static int srz_parse_u32(const char* text, u32* out_value)
{
    char* end = 0;
    unsigned long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoul(text, &end, 0);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (u32)value;
    return 1;
}

static int srz_parse_u64(const char* text, u64* out_value)
{
    const char* ptr;
    u64 value = 0;
    int base = 10;
    if (!text || !out_value) {
        return 0;
    }
    ptr = text;
    if (ptr[0] == '0' && (ptr[1] == 'x' || ptr[1] == 'X')) {
        base = 16;
        ptr += 2;
    }
    if (!*ptr) {
        return 0;
    }
    for (; *ptr; ++ptr) {
        int digit = -1;
        char ch = *ptr;
        if (base == 10) {
            if (ch < '0' || ch > '9') {
                return 0;
            }
            digit = ch - '0';
        } else {
            if (ch >= '0' && ch <= '9') {
                digit = ch - '0';
            } else if (ch >= 'a' && ch <= 'f') {
                digit = ch - 'a' + 10;
            } else if (ch >= 'A' && ch <= 'F') {
                digit = ch - 'A' + 10;
            } else {
                return 0;
            }
        }
        if (value > (0xFFFFFFFFFFFFFFFFULL - (u64)digit) / (u64)base) {
            return 0;
        }
        value = value * (u64)base + (u64)digit;
    }
    *out_value = value;
    return 1;
}

static int srz_parse_q16(const char* text, q16_16* out_value)
{
    char* end = 0;
    double value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtod(text, &end);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = d_q16_16_from_double(value);
    return 1;
}

static int srz_parse_indexed_key(const char* key,
                                 const char* prefix,
                                 u32* out_index,
                                 const char** out_suffix)
{
    size_t len;
    char* end = 0;
    unsigned long idx;
    if (!key || !prefix || !out_index || !out_suffix) {
        return 0;
    }
    len = strlen(prefix);
    if (strncmp(key, prefix, len) != 0) {
        return 0;
    }
    idx = strtoul(key + len, &end, 10);
    if (!end || end == key + len || *end != '_') {
        return 0;
    }
    *out_index = (u32)idx;
    *out_suffix = end + 1;
    return 1;
}

static int srz_parse_sub_indexed_key(const char* key,
                                     const char* prefix,
                                     u32* out_index,
                                     const char** out_suffix)
{
    size_t len;
    char* end = 0;
    unsigned long idx;
    if (!key || !prefix || !out_index || !out_suffix) {
        return 0;
    }
    len = strlen(prefix);
    if (strncmp(key, prefix, len) != 0) {
        return 0;
    }
    idx = strtoul(key + len, &end, 10);
    if (!end || end == key + len || *end != '_') {
        return 0;
    }
    *out_index = (u32)idx;
    *out_suffix = end + 1;
    return 1;
}

static u32 srz_mode_from_text(const char* text)
{
    if (!text) {
        return DOM_SRZ_MODE_UNSET;
    }
    if (strcmp(text, "server") == 0) return DOM_SRZ_MODE_SERVER;
    if (strcmp(text, "delegated") == 0) return DOM_SRZ_MODE_DELEGATED;
    if (strcmp(text, "dormant") == 0) return DOM_SRZ_MODE_DORMANT;
    return DOM_SRZ_MODE_UNSET;
}

static u32 srz_policy_from_text(const char* text)
{
    if (!text) {
        return DOM_SRZ_VERIFY_UNSET;
    }
    if (strcmp(text, "strict") == 0) return DOM_SRZ_VERIFY_STRICT;
    if (strcmp(text, "spot") == 0) return DOM_SRZ_VERIFY_SPOT;
    if (strcmp(text, "invariant") == 0) return DOM_SRZ_VERIFY_INVARIANT_ONLY;
    return DOM_SRZ_VERIFY_UNSET;
}

static u32 srz_metric_from_text(const char* text)
{
    if (!text) {
        return DOM_SRZ_METRIC_UNSET;
    }
    if (strcmp(text, "fail_rate") == 0) return DOM_SRZ_METRIC_FAIL_RATE;
    return DOM_SRZ_METRIC_UNSET;
}

static void srz_fixture_init(srz_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_srz_surface_desc_init(&fixture->srz_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "srz.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void srz_fixture_register_region(srz_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_SRZ_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int srz_fixture_apply_zone(srz_fixture* fixture,
                                  u32 index,
                                  const char* suffix,
                                  const char* value)
{
    dom_srz_zone_desc* zone;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_SRZ_MAX_ZONES) {
        return 0;
    }
    if (fixture->srz_desc.zone_count <= index) {
        fixture->srz_desc.zone_count = index + 1u;
    }
    zone = &fixture->srz_desc.zones[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->zone_names[index], value, sizeof(fixture->zone_names[index]) - 1);
        fixture->zone_names[index][sizeof(fixture->zone_names[index]) - 1] = '\0';
        zone->srz_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "mode") == 0) {
        zone->mode = srz_mode_from_text(value);
        return zone->mode != DOM_SRZ_MODE_UNSET;
    }
    if (strcmp(suffix, "verification") == 0) {
        zone->verification_policy = srz_policy_from_text(value);
        return zone->verification_policy != DOM_SRZ_VERIFY_UNSET;
    }
    if (strcmp(suffix, "policy") == 0) {
        zone->policy_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "domain_count") == 0) {
        return srz_parse_u32(value, &zone->domain_count);
    }
    if (strncmp(suffix, "domain_", 7) == 0) {
        u32 domain_index = 0u;
        const char* domain_suffix = 0;
        if (srz_parse_sub_indexed_key(suffix, "domain_", &domain_index, &domain_suffix)) {
            if (domain_suffix[0] == '\0') {
                if (domain_index < DOM_SRZ_MAX_DOMAIN_REFS) {
                    zone->domain_ids[domain_index] = d_rng_hash_str32(value);
                    return 1;
                }
            }
        }
    }
    if (strcmp(suffix, "escalate_count") == 0) {
        return srz_parse_u32(value, &zone->escalation_count);
    }
    if (strncmp(suffix, "escalate_", 9) == 0) {
        u32 tindex = 0u;
        const char* tfield = 0;
        if (srz_parse_sub_indexed_key(suffix, "escalate_", &tindex, &tfield)) {
            if (tindex >= DOM_SRZ_MAX_THRESHOLDS) {
                return 0;
            }
            if (strcmp(tfield, "metric") == 0) {
                zone->escalation[tindex].metric_id = srz_metric_from_text(value);
                return zone->escalation[tindex].metric_id != DOM_SRZ_METRIC_UNSET;
            }
            if (strcmp(tfield, "value") == 0) {
                return srz_parse_q16(value, &zone->escalation[tindex].value);
            }
        }
    }
    if (strcmp(suffix, "deescalate_count") == 0) {
        return srz_parse_u32(value, &zone->deescalation_count);
    }
    if (strncmp(suffix, "deescalate_", 11) == 0) {
        u32 tindex = 0u;
        const char* tfield = 0;
        if (srz_parse_sub_indexed_key(suffix, "deescalate_", &tindex, &tfield)) {
            if (tindex >= DOM_SRZ_MAX_THRESHOLDS) {
                return 0;
            }
            if (strcmp(tfield, "metric") == 0) {
                zone->deescalation[tindex].metric_id = srz_metric_from_text(value);
                return zone->deescalation[tindex].metric_id != DOM_SRZ_METRIC_UNSET;
            }
            if (strcmp(tfield, "value") == 0) {
                return srz_parse_q16(value, &zone->deescalation[tindex].value);
            }
        }
    }
    if (strcmp(suffix, "epistemic") == 0) {
        zone->epistemic_scope_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        zone->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        zone->region_id = region_id;
        srz_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int srz_fixture_apply_assignment(srz_fixture* fixture,
                                        u32 index,
                                        const char* suffix,
                                        const char* value)
{
    dom_srz_assignment_desc* assignment;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_SRZ_MAX_ASSIGNMENTS) {
        return 0;
    }
    if (fixture->srz_desc.assignment_count <= index) {
        fixture->srz_desc.assignment_count = index + 1u;
    }
    assignment = &fixture->srz_desc.assignments[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->assignment_names[index], value, sizeof(fixture->assignment_names[index]) - 1);
        fixture->assignment_names[index][sizeof(fixture->assignment_names[index]) - 1] = '\0';
        assignment->assignment_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "srz") == 0) {
        assignment->srz_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "executor") == 0) {
        assignment->executor_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "token") == 0) {
        assignment->authority_token_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "capability") == 0) {
        assignment->capability_baseline_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "start") == 0) {
        return srz_parse_u64(value, &assignment->start_tick);
    }
    if (strcmp(suffix, "expiry") == 0) {
        return srz_parse_u64(value, &assignment->expiry_tick);
    }
    if (strcmp(suffix, "provenance") == 0) {
        assignment->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        assignment->region_id = region_id;
        srz_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int srz_fixture_apply_policy(srz_fixture* fixture,
                                    u32 index,
                                    const char* suffix,
                                    const char* value)
{
    dom_srz_policy_desc* policy;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_SRZ_MAX_POLICIES) {
        return 0;
    }
    if (fixture->srz_desc.policy_count <= index) {
        fixture->srz_desc.policy_count = index + 1u;
    }
    policy = &fixture->srz_desc.policies[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->policy_names[index], value, sizeof(fixture->policy_names[index]) - 1);
        fixture->policy_names[index][sizeof(fixture->policy_names[index]) - 1] = '\0';
        policy->policy_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "verification") == 0) {
        policy->verification_policy = srz_policy_from_text(value);
        return policy->verification_policy != DOM_SRZ_VERIFY_UNSET;
    }
    if (strcmp(suffix, "spot_rate") == 0) {
        return srz_parse_q16(value, &policy->spot_check_rate);
    }
    if (strcmp(suffix, "strict_interval") == 0) {
        return srz_parse_u64(value, &policy->strict_replay_interval);
    }
    if (strcmp(suffix, "max_segment") == 0) {
        return srz_parse_u64(value, &policy->max_segment_ticks);
    }
    if (strcmp(suffix, "provenance") == 0) {
        policy->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        policy->region_id = region_id;
        srz_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int srz_fixture_apply_log(srz_fixture* fixture,
                                 u32 index,
                                 const char* suffix,
                                 const char* value)
{
    dom_srz_log_desc* log;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_SRZ_MAX_LOGS) {
        return 0;
    }
    if (fixture->srz_desc.log_count <= index) {
        fixture->srz_desc.log_count = index + 1u;
    }
    log = &fixture->srz_desc.logs[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->log_names[index], value, sizeof(fixture->log_names[index]) - 1);
        fixture->log_names[index][sizeof(fixture->log_names[index]) - 1] = '\0';
        log->log_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "srz") == 0) {
        log->srz_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "assignment") == 0) {
        log->assignment_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "policy") == 0) {
        log->policy_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "chain") == 0) {
        strncpy(fixture->chain_names[index], value, sizeof(fixture->chain_names[index]) - 1);
        fixture->chain_names[index][sizeof(fixture->chain_names[index]) - 1] = '\0';
        log->chain_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "delta") == 0) {
        log->delta_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "start") == 0) {
        return srz_parse_u64(value, &log->start_tick);
    }
    if (strcmp(suffix, "end") == 0) {
        return srz_parse_u64(value, &log->end_tick);
    }
    if (strcmp(suffix, "process_count") == 0) {
        return srz_parse_u32(value, &log->process_count);
    }
    if (strcmp(suffix, "rng_count") == 0) {
        return srz_parse_u32(value, &log->rng_stream_count);
    }
    if (strcmp(suffix, "epistemic") == 0) {
        log->epistemic_scope_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        log->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        log->region_id = region_id;
        srz_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int srz_fixture_apply_hash(srz_fixture* fixture,
                                  u32 index,
                                  const char* suffix,
                                  const char* value)
{
    dom_srz_hash_link_desc* link;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_SRZ_MAX_HASH_LINKS) {
        return 0;
    }
    if (fixture->srz_desc.hash_link_count <= index) {
        fixture->srz_desc.hash_link_count = index + 1u;
    }
    link = &fixture->srz_desc.hash_links[index];
    if (strcmp(suffix, "id") == 0) {
        link->link_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "chain") == 0) {
        link->chain_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "index") == 0) {
        return srz_parse_u32(value, &link->segment_index);
    }
    if (strcmp(suffix, "prev") == 0) {
        return srz_parse_u64(value, &link->prev_hash);
    }
    if (strcmp(suffix, "hash") == 0) {
        return srz_parse_u64(value, &link->hash);
    }
    if (strcmp(suffix, "start") == 0) {
        return srz_parse_u64(value, &link->start_tick);
    }
    if (strcmp(suffix, "end") == 0) {
        return srz_parse_u64(value, &link->end_tick);
    }
    if (strcmp(suffix, "process_count") == 0) {
        return srz_parse_u32(value, &link->process_count);
    }
    if (strcmp(suffix, "rng_count") == 0) {
        return srz_parse_u32(value, &link->rng_stream_count);
    }
    if (strcmp(suffix, "provenance") == 0) {
        link->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        link->region_id = region_id;
        srz_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int srz_fixture_apply_delta(srz_fixture* fixture,
                                   u32 index,
                                   const char* suffix,
                                   const char* value)
{
    dom_srz_state_delta_desc* delta;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_SRZ_MAX_DELTAS) {
        return 0;
    }
    if (fixture->srz_desc.delta_count <= index) {
        fixture->srz_desc.delta_count = index + 1u;
    }
    delta = &fixture->srz_desc.deltas[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->delta_names[index], value, sizeof(fixture->delta_names[index]) - 1);
        fixture->delta_names[index][sizeof(fixture->delta_names[index]) - 1] = '\0';
        delta->delta_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "srz") == 0) {
        delta->srz_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "log") == 0) {
        delta->log_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "process_count") == 0) {
        return srz_parse_u32(value, &delta->process_count);
    }
    if (strcmp(suffix, "rng_count") == 0) {
        return srz_parse_u32(value, &delta->rng_stream_count);
    }
    if (strcmp(suffix, "invariants_ok") == 0) {
        u32 flag = 0u;
        if (!srz_parse_u32(value, &flag)) {
            return 0;
        }
        if (flag) {
            delta->flags |= DOM_SRZ_DELTA_INVARIANTS_OK;
        } else {
            delta->flags |= DOM_SRZ_DELTA_INVARIANTS_FAIL;
        }
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        delta->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        delta->region_id = region_id;
        srz_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int srz_fixture_apply(srz_fixture* fixture, const char* key, const char* value)
{
    u32 index = 0u;
    const char* suffix = 0;
    if (!fixture || !key || !value) {
        return 0;
    }
    if (strcmp(key, "fixture_id") == 0) {
        strncpy(fixture->fixture_id, value, sizeof(fixture->fixture_id) - 1);
        fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
        return 1;
    }
    if (strcmp(key, "world_seed") == 0) {
        return srz_parse_u64(value, &fixture->srz_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return srz_parse_u64(value, &fixture->srz_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return srz_parse_q16(value, &fixture->srz_desc.meters_per_unit);
    }
    if (strcmp(key, "zone_count") == 0) {
        return srz_parse_u32(value, &fixture->srz_desc.zone_count);
    }
    if (strcmp(key, "assignment_count") == 0) {
        return srz_parse_u32(value, &fixture->srz_desc.assignment_count);
    }
    if (strcmp(key, "policy_count") == 0) {
        return srz_parse_u32(value, &fixture->srz_desc.policy_count);
    }
    if (strcmp(key, "log_count") == 0) {
        return srz_parse_u32(value, &fixture->srz_desc.log_count);
    }
    if (strcmp(key, "hash_link_count") == 0) {
        return srz_parse_u32(value, &fixture->srz_desc.hash_link_count);
    }
    if (strcmp(key, "delta_count") == 0) {
        return srz_parse_u32(value, &fixture->srz_desc.delta_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return srz_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return srz_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return srz_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return srz_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (srz_parse_indexed_key(key, "zone_", &index, &suffix)) {
        return srz_fixture_apply_zone(fixture, index, suffix, value);
    }
    if (srz_parse_indexed_key(key, "assignment_", &index, &suffix)) {
        return srz_fixture_apply_assignment(fixture, index, suffix, value);
    }
    if (srz_parse_indexed_key(key, "policy_", &index, &suffix)) {
        return srz_fixture_apply_policy(fixture, index, suffix, value);
    }
    if (srz_parse_indexed_key(key, "log_", &index, &suffix)) {
        return srz_fixture_apply_log(fixture, index, suffix, value);
    }
    if (srz_parse_indexed_key(key, "hash_", &index, &suffix)) {
        return srz_fixture_apply_hash(fixture, index, suffix, value);
    }
    if (srz_parse_indexed_key(key, "delta_", &index, &suffix)) {
        return srz_fixture_apply_delta(fixture, index, suffix, value);
    }
    return 0;
}

static int srz_fixture_load(const char* path, srz_fixture* out_fixture)
{
    FILE* file;
    char line[SRZ_LINE_MAX];
    int header_ok = 0;
    srz_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    srz_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = srz_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, SRZ_FIXTURE_HEADER) != 0) {
                fclose(file);
                return 0;
            }
            header_ok = 1;
            continue;
        }
        eq = strchr(text, '=');
        if (!eq) {
            continue;
        }
        *eq++ = '\0';
        srz_fixture_apply(&fixture, srz_trim(text), srz_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* srz_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 srz_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = srz_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && srz_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 srz_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = srz_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && srz_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 srz_find_region_id(const srz_fixture* fixture, const char* name)
{
    if (!name || !*name) {
        return 0u;
    }
    if (!fixture) {
        return d_rng_hash_str32(name);
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (strcmp(fixture->region_names[i], name) == 0) {
            return fixture->region_ids[i];
        }
    }
    return d_rng_hash_str32(name);
}

static const char* srz_lookup_zone_name(const srz_fixture* fixture, u32 srz_id)
{
    if (!fixture || srz_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->srz_desc.zone_count; ++i) {
        if (fixture->srz_desc.zones[i].srz_id == srz_id) {
            return fixture->zone_names[i];
        }
    }
    return "";
}

static const char* srz_lookup_assignment_name(const srz_fixture* fixture, u32 assignment_id)
{
    if (!fixture || assignment_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->srz_desc.assignment_count; ++i) {
        if (fixture->srz_desc.assignments[i].assignment_id == assignment_id) {
            return fixture->assignment_names[i];
        }
    }
    return "";
}

static const char* srz_lookup_policy_name(const srz_fixture* fixture, u32 policy_id)
{
    if (!fixture || policy_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->srz_desc.policy_count; ++i) {
        if (fixture->srz_desc.policies[i].policy_id == policy_id) {
            return fixture->policy_names[i];
        }
    }
    return "";
}

static const char* srz_lookup_log_name(const srz_fixture* fixture, u32 log_id)
{
    if (!fixture || log_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->srz_desc.log_count; ++i) {
        if (fixture->srz_desc.logs[i].log_id == log_id) {
            return fixture->log_names[i];
        }
    }
    return "";
}

static int srz_zone_exists(const srz_fixture* fixture, u32 srz_id)
{
    if (!fixture || srz_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->srz_desc.zone_count; ++i) {
        if (fixture->srz_desc.zones[i].srz_id == srz_id) {
            return 1;
        }
    }
    return 0;
}

static int srz_log_exists(const srz_fixture* fixture, u32 log_id)
{
    if (!fixture || log_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->srz_desc.log_count; ++i) {
        if (fixture->srz_desc.logs[i].log_id == log_id) {
            return 1;
        }
    }
    return 0;
}

static int srz_chain_exists(const srz_fixture* fixture, u32 chain_id)
{
    if (!fixture || chain_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->srz_desc.log_count; ++i) {
        if (fixture->srz_desc.logs[i].chain_id == chain_id) {
            return 1;
        }
    }
    return 0;
}

static int srz_ratio_valid(q16_16 value)
{
    return !(value < 0 || value > DOM_SRZ_RATIO_ONE_Q16);
}

static int srz_validate_fixture(const srz_fixture* fixture)
{
    if (!fixture) {
        return 0;
    }
    if (fixture->srz_desc.zone_count > DOM_SRZ_MAX_ZONES) {
        return 0;
    }
    if (fixture->srz_desc.assignment_count > DOM_SRZ_MAX_ASSIGNMENTS) {
        return 0;
    }
    if (fixture->srz_desc.policy_count > DOM_SRZ_MAX_POLICIES) {
        return 0;
    }
    if (fixture->srz_desc.log_count > DOM_SRZ_MAX_LOGS) {
        return 0;
    }
    if (fixture->srz_desc.hash_link_count > DOM_SRZ_MAX_HASH_LINKS) {
        return 0;
    }
    if (fixture->srz_desc.delta_count > DOM_SRZ_MAX_DELTAS) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->srz_desc.zone_count; ++i) {
        const dom_srz_zone_desc* zone = &fixture->srz_desc.zones[i];
        if (zone->srz_id == 0u) {
            return 0;
        }
        if (zone->mode == DOM_SRZ_MODE_UNSET) {
            return 0;
        }
        if (zone->verification_policy == DOM_SRZ_VERIFY_UNSET) {
            return 0;
        }
        if (zone->domain_count > DOM_SRZ_MAX_DOMAIN_REFS) {
            return 0;
        }
        for (u32 t = 0u; t < zone->escalation_count; ++t) {
            if (zone->escalation[t].metric_id == DOM_SRZ_METRIC_UNSET) {
                return 0;
            }
            if (!srz_ratio_valid(zone->escalation[t].value)) {
                return 0;
            }
        }
        for (u32 t = 0u; t < zone->deescalation_count; ++t) {
            if (zone->deescalation[t].metric_id == DOM_SRZ_METRIC_UNSET) {
                return 0;
            }
            if (!srz_ratio_valid(zone->deescalation[t].value)) {
                return 0;
            }
        }
    }
    for (u32 i = 0u; i < fixture->srz_desc.assignment_count; ++i) {
        const dom_srz_assignment_desc* assignment = &fixture->srz_desc.assignments[i];
        if (assignment->assignment_id == 0u) {
            return 0;
        }
        if (!srz_zone_exists(fixture, assignment->srz_id)) {
            return 0;
        }
        if (assignment->expiry_tick && assignment->start_tick > assignment->expiry_tick) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->srz_desc.policy_count; ++i) {
        const dom_srz_policy_desc* policy = &fixture->srz_desc.policies[i];
        if (policy->policy_id == 0u) {
            return 0;
        }
        if (policy->verification_policy == DOM_SRZ_VERIFY_UNSET) {
            return 0;
        }
        if (!srz_ratio_valid(policy->spot_check_rate)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->srz_desc.log_count; ++i) {
        const dom_srz_log_desc* log = &fixture->srz_desc.logs[i];
        if (log->log_id == 0u) {
            return 0;
        }
        if (!srz_zone_exists(fixture, log->srz_id)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->srz_desc.hash_link_count; ++i) {
        const dom_srz_hash_link_desc* link = &fixture->srz_desc.hash_links[i];
        if (link->link_id == 0u) {
            return 0;
        }
        if (link->chain_id != 0u && !srz_chain_exists(fixture, link->chain_id)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->srz_desc.delta_count; ++i) {
        const dom_srz_state_delta_desc* delta = &fixture->srz_desc.deltas[i];
        if (delta->delta_id == 0u) {
            return 0;
        }
        if (delta->log_id != 0u && !srz_log_exists(fixture, delta->log_id)) {
            return 0;
        }
    }
    return 1;
}

static int srz_run_validate(const srz_fixture* fixture)
{
    int ok = srz_validate_fixture(fixture);
    printf("%s\n", SRZ_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", SRZ_PROVIDER_CHAIN);
    printf("zone_count=%u\n", (unsigned int)fixture->srz_desc.zone_count);
    printf("assignment_count=%u\n", (unsigned int)fixture->srz_desc.assignment_count);
    printf("policy_count=%u\n", (unsigned int)fixture->srz_desc.policy_count);
    printf("log_count=%u\n", (unsigned int)fixture->srz_desc.log_count);
    printf("hash_link_count=%u\n", (unsigned int)fixture->srz_desc.hash_link_count);
    printf("delta_count=%u\n", (unsigned int)fixture->srz_desc.delta_count);
    printf("ok=%u\n", (unsigned int)(ok ? 1u : 0u));
    return ok ? 0 : 1;
}

static int srz_run_inspect_zone(const srz_fixture* fixture, const char* zone_name, u32 budget_max)
{
    dom_srz_domain domain;
    dom_domain_budget budget;
    dom_srz_zone_sample sample;
    u32 zone_id;
    if (!zone_name) {
        return 1;
    }
    zone_id = d_rng_hash_str32(zone_name);
    dom_srz_domain_init(&domain, &fixture->srz_desc);
    if (fixture->policy_set) {
        dom_srz_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_srz_zone_query(&domain, zone_id, &budget, &sample);

    printf("%s\n", SRZ_INSPECT_HEADER);
    printf("entity=zone\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", SRZ_PROVIDER_CHAIN);
    printf("srz_id=%u\n", (unsigned int)sample.srz_id);
    printf("srz_id_str=%s\n", srz_lookup_zone_name(fixture, sample.srz_id));
    printf("domain_count=%u\n", (unsigned int)sample.domain_count);
    printf("mode=%u\n", (unsigned int)sample.mode);
    printf("verification_policy=%u\n", (unsigned int)sample.verification_policy);
    printf("escalation_count=%u\n", (unsigned int)sample.escalation_count);
    printf("deescalation_count=%u\n", (unsigned int)sample.deescalation_count);
    printf("epistemic_scope_id=%u\n", (unsigned int)sample.epistemic_scope_id);
    printf("policy_id=%u\n", (unsigned int)sample.policy_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_srz_domain_free(&domain);
    return 0;
}

static int srz_run_inspect_assignment(const srz_fixture* fixture, const char* name, u32 budget_max)
{
    dom_srz_domain domain;
    dom_domain_budget budget;
    dom_srz_assignment_sample sample;
    u32 assignment_id;
    if (!name) {
        return 1;
    }
    assignment_id = d_rng_hash_str32(name);
    dom_srz_domain_init(&domain, &fixture->srz_desc);
    if (fixture->policy_set) {
        dom_srz_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_srz_assignment_query(&domain, assignment_id, &budget, &sample);

    printf("%s\n", SRZ_INSPECT_HEADER);
    printf("entity=assignment\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", SRZ_PROVIDER_CHAIN);
    printf("assignment_id=%u\n", (unsigned int)sample.assignment_id);
    printf("assignment_id_str=%s\n", srz_lookup_assignment_name(fixture, sample.assignment_id));
    printf("srz_id=%u\n", (unsigned int)sample.srz_id);
    printf("executor_id=%u\n", (unsigned int)sample.executor_id);
    printf("authority_token_id=%u\n", (unsigned int)sample.authority_token_id);
    printf("capability_baseline_id=%u\n", (unsigned int)sample.capability_baseline_id);
    printf("start_tick=%llu\n", (unsigned long long)sample.start_tick);
    printf("expiry_tick=%llu\n", (unsigned long long)sample.expiry_tick);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_srz_domain_free(&domain);
    return 0;
}

static int srz_run_inspect_policy(const srz_fixture* fixture, const char* name, u32 budget_max)
{
    dom_srz_domain domain;
    dom_domain_budget budget;
    dom_srz_policy_sample sample;
    u32 policy_id;
    if (!name) {
        return 1;
    }
    policy_id = d_rng_hash_str32(name);
    dom_srz_domain_init(&domain, &fixture->srz_desc);
    if (fixture->policy_set) {
        dom_srz_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_srz_policy_query(&domain, policy_id, &budget, &sample);

    printf("%s\n", SRZ_INSPECT_HEADER);
    printf("entity=policy\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", SRZ_PROVIDER_CHAIN);
    printf("policy_id=%u\n", (unsigned int)sample.policy_id);
    printf("policy_id_str=%s\n", srz_lookup_policy_name(fixture, sample.policy_id));
    printf("verification_policy=%u\n", (unsigned int)sample.verification_policy);
    printf("spot_check_rate_q16=%d\n", (int)sample.spot_check_rate);
    printf("strict_replay_interval=%llu\n", (unsigned long long)sample.strict_replay_interval);
    printf("max_segment_ticks=%llu\n", (unsigned long long)sample.max_segment_ticks);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_srz_domain_free(&domain);
    return 0;
}

static int srz_run_inspect_log(const srz_fixture* fixture, const char* name, u32 budget_max)
{
    dom_srz_domain domain;
    dom_domain_budget budget;
    dom_srz_log_sample sample;
    u32 log_id;
    if (!name) {
        return 1;
    }
    log_id = d_rng_hash_str32(name);
    dom_srz_domain_init(&domain, &fixture->srz_desc);
    if (fixture->policy_set) {
        dom_srz_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_srz_log_query(&domain, log_id, &budget, &sample);

    printf("%s\n", SRZ_INSPECT_HEADER);
    printf("entity=log\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", SRZ_PROVIDER_CHAIN);
    printf("log_id=%u\n", (unsigned int)sample.log_id);
    printf("log_id_str=%s\n", srz_lookup_log_name(fixture, sample.log_id));
    printf("srz_id=%u\n", (unsigned int)sample.srz_id);
    printf("assignment_id=%u\n", (unsigned int)sample.assignment_id);
    printf("policy_id=%u\n", (unsigned int)sample.policy_id);
    printf("chain_id=%u\n", (unsigned int)sample.chain_id);
    printf("delta_id=%u\n", (unsigned int)sample.delta_id);
    printf("start_tick=%llu\n", (unsigned long long)sample.start_tick);
    printf("end_tick=%llu\n", (unsigned long long)sample.end_tick);
    printf("process_count=%u\n", (unsigned int)sample.process_count);
    printf("rng_stream_count=%u\n", (unsigned int)sample.rng_stream_count);
    printf("epistemic_scope_id=%u\n", (unsigned int)sample.epistemic_scope_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_srz_domain_free(&domain);
    return 0;
}

static int srz_run_inspect_region(const srz_fixture* fixture, const char* region_name, u32 budget_max)
{
    dom_srz_domain domain;
    dom_domain_budget budget;
    dom_srz_region_sample sample;
    u32 region_id = srz_find_region_id(fixture, region_name);

    dom_srz_domain_init(&domain, &fixture->srz_desc);
    if (fixture->policy_set) {
        dom_srz_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_srz_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", SRZ_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", SRZ_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("zone_count=%u\n", (unsigned int)sample.zone_count);
    printf("assignment_count=%u\n", (unsigned int)sample.assignment_count);
    printf("policy_count=%u\n", (unsigned int)sample.policy_count);
    printf("log_count=%u\n", (unsigned int)sample.log_count);
    printf("hash_link_count=%u\n", (unsigned int)sample.hash_link_count);
    printf("delta_count=%u\n", (unsigned int)sample.delta_count);
    printf("server_mode_count=%u\n", (unsigned int)sample.server_mode_count);
    printf("delegated_mode_count=%u\n", (unsigned int)sample.delegated_mode_count);
    printf("dormant_mode_count=%u\n", (unsigned int)sample.dormant_mode_count);
    printf("verification_ok_count=%u\n", (unsigned int)sample.verification_ok_count);
    printf("verification_fail_count=%u\n", (unsigned int)sample.verification_fail_count);
    printf("failure_rate_q16=%d\n", (int)sample.failure_rate);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_srz_domain_free(&domain);
    return 0;
}

static int srz_run_resolve(const srz_fixture* fixture,
                           const char* region_name,
                           u64 tick,
                           u64 tick_delta,
                           u32 budget_max,
                           u32 inactive_count,
                           u32 simulate_sparse,
                           u32 simulate_dense)
{
    dom_srz_domain domain;
    dom_srz_domain* inactive = 0;
    dom_domain_budget budget;
    dom_srz_resolve_result result;
    u32 region_id = srz_find_region_id(fixture, region_name);
    u64 agg_hash = 0u;

    dom_srz_domain_init(&domain, &fixture->srz_desc);
    if (fixture->policy_set) {
        dom_srz_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_srz_domain*)malloc(sizeof(dom_srz_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                srz_fixture temp = *fixture;
                temp.srz_desc.domain_id = fixture->srz_desc.domain_id + (u64)(i + 1u);
                dom_srz_domain_init(&inactive[i], &temp.srz_desc);
                dom_srz_domain_set_state(&inactive[i],
                                         DOM_DOMAIN_EXISTENCE_DECLARED,
                                         DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_srz_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.zone_count; ++i) {
        u64 h = 14695981039346656037ULL;
        h = srz_hash_u32(h, domain.zones[i].srz_id);
        h = srz_hash_u32(h, domain.zones[i].mode);
        h = srz_hash_u32(h, domain.zones[i].verification_policy);
        h = srz_hash_u32(h, domain.zones[i].epistemic_scope_id);
        agg_hash += h;
    }
    for (u32 i = 0u; i < domain.log_count; ++i) {
        u64 h = 14695981039346656037ULL;
        h = srz_hash_u32(h, domain.logs[i].log_id);
        h = srz_hash_u32(h, domain.logs[i].chain_id);
        h = srz_hash_u32(h, domain.logs[i].process_count);
        h = srz_hash_u32(h, domain.logs[i].rng_stream_count);
        h = srz_hash_u32(h, domain.logs[i].flags);
        agg_hash += h;
    }
    for (u32 i = 0u; i < domain.hash_link_count; ++i) {
        u64 h = 14695981039346656037ULL;
        h = srz_hash_u32(h, domain.hash_links[i].link_id);
        h = srz_hash_u64(h, domain.hash_links[i].hash);
        h = srz_hash_u64(h, domain.hash_links[i].prev_hash);
        agg_hash += h;
    }
    for (u32 i = 0u; i < domain.delta_count; ++i) {
        u64 h = 14695981039346656037ULL;
        h = srz_hash_u32(h, domain.deltas[i].delta_id);
        h = srz_hash_u32(h, domain.deltas[i].process_count);
        h = srz_hash_u32(h, domain.deltas[i].rng_stream_count);
        agg_hash += h;
    }

    printf("%s\n", SRZ_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", SRZ_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("zone_count=%u\n", (unsigned int)result.zone_count);
    printf("assignment_count=%u\n", (unsigned int)result.assignment_count);
    printf("policy_count=%u\n", (unsigned int)result.policy_count);
    printf("log_count=%u\n", (unsigned int)result.log_count);
    printf("hash_link_count=%u\n", (unsigned int)result.hash_link_count);
    printf("delta_count=%u\n", (unsigned int)result.delta_count);
    printf("server_mode_count=%u\n", (unsigned int)result.server_mode_count);
    printf("delegated_mode_count=%u\n", (unsigned int)result.delegated_mode_count);
    printf("dormant_mode_count=%u\n", (unsigned int)result.dormant_mode_count);
    printf("verification_ok_count=%u\n", (unsigned int)result.verification_ok_count);
    printf("verification_fail_count=%u\n", (unsigned int)result.verification_fail_count);
    printf("failure_rate_q16=%d\n", (int)result.failure_rate);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)agg_hash);
    printf("sim_sparse=%u\n", (unsigned int)simulate_sparse);
    printf("sim_dense=%u\n", (unsigned int)simulate_dense);

    dom_srz_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_srz_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int srz_run_collapse(const srz_fixture* fixture, const char* region_name)
{
    dom_srz_domain domain;
    u32 region_id = srz_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_srz_domain_init(&domain, &fixture->srz_desc);
    if (fixture->policy_set) {
        dom_srz_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_srz_domain_capsule_count(&domain);
    (void)dom_srz_domain_collapse_region(&domain, region_id);
    count_after = dom_srz_domain_capsule_count(&domain);

    printf("%s\n", SRZ_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", SRZ_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_srz_domain_free(&domain);
    return 0;
}

static void srz_usage(void)
{
    printf("dom_tool_srz commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --zone <id> [--budget N]\n");
    printf("  inspect --fixture <path> --assignment <id> [--budget N]\n");
    printf("  inspect --fixture <path> --policy <id> [--budget N]\n");
    printf("  inspect --fixture <path> --log <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  resolve --fixture <path> --region <id> [--simulate_sparse N] [--simulate_dense N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        srz_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = srz_find_arg(argc, argv, "--fixture");
        srz_fixture fixture;
        if (!fixture_path || !srz_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "srz: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return srz_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* zone_name = srz_find_arg(argc, argv, "--zone");
            const char* assignment_name = srz_find_arg(argc, argv, "--assignment");
            const char* policy_name = srz_find_arg(argc, argv, "--policy");
            const char* log_name = srz_find_arg(argc, argv, "--log");
            const char* region_name = srz_find_arg(argc, argv, "--region");
            u32 budget_max = srz_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (zone_name) {
                return srz_run_inspect_zone(&fixture, zone_name, budget_max);
            }
            if (assignment_name) {
                return srz_run_inspect_assignment(&fixture, assignment_name, budget_max);
            }
            if (policy_name) {
                return srz_run_inspect_policy(&fixture, policy_name, budget_max);
            }
            if (log_name) {
                return srz_run_inspect_log(&fixture, log_name, budget_max);
            }
            if (region_name) {
                return srz_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr, "srz: inspect requires --zone, --assignment, --policy, --log, or --region\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = srz_find_arg(argc, argv, "--region");
            u64 tick = srz_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = srz_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = srz_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            u32 inactive = srz_find_arg_u32(argc, argv, "--inactive", 0u);
            u32 simulate_sparse = srz_find_arg_u32(argc, argv, "--simulate_sparse", 0u);
            u32 simulate_dense = srz_find_arg_u32(argc, argv, "--simulate_dense", 0u);
            if (!region_name) {
                fprintf(stderr, "srz: resolve requires --region\n");
                return 2;
            }
            return srz_run_resolve(&fixture, region_name, tick, delta, budget_max,
                                   inactive, simulate_sparse, simulate_dense);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = srz_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "srz: collapse requires --region\n");
                return 2;
            }
            return srz_run_collapse(&fixture, region_name);
        }
    }

    srz_usage();
    return 2;
}
