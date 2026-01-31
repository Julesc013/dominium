/*
FILE: tools/trust/trust_cli.cpp
MODULE: Dominium
PURPOSE: Trust fixture CLI for deterministic trust/reputation/legitimacy checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/trust_fields.h"

#define TRUST_FIXTURE_HEADER "DOMINIUM_TRUST_FIXTURE_V1"

#define TRUST_VALIDATE_HEADER "DOMINIUM_TRUST_VALIDATE_V1"
#define TRUST_INSPECT_HEADER "DOMINIUM_TRUST_INSPECT_V1"
#define TRUST_RESOLVE_HEADER "DOMINIUM_TRUST_RESOLVE_V1"
#define TRUST_COLLAPSE_HEADER "DOMINIUM_TRUST_COLLAPSE_V1"

#define TRUST_PROVIDER_CHAIN "fields->events->profiles->legitimacy"

#define TRUST_LINE_MAX 512u

typedef struct trust_fixture {
    char fixture_id[96];
    dom_trust_surface_desc trust_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char field_names[DOM_TRUST_MAX_FIELDS][64];
    char event_names[DOM_TRUST_MAX_EVENTS][64];
    char profile_names[DOM_TRUST_MAX_PROFILES][64];
    char legitimacy_names[DOM_TRUST_MAX_LEGITIMACY][64];
    char region_names[DOM_TRUST_MAX_REGIONS][64];
    u32 region_ids[DOM_TRUST_MAX_REGIONS];
    u32 region_count;
} trust_fixture;

static u64 trust_hash_u64(u64 h, u64 v)
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

static u64 trust_hash_u32(u64 h, u32 v)
{
    return trust_hash_u64(h, (u64)v);
}

static u64 trust_hash_q16(u64 h, q16_16 v)
{
    return trust_hash_u64(h, (u64)(u32)v);
}

static char* trust_trim(char* text)
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

static int trust_parse_u32(const char* text, u32* out_value)
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

static int trust_parse_u64(const char* text, u64* out_value)
{
    char* end = 0;
    unsigned long long value;
    if (!text || !out_value) {
        return 0;
    }
    value = strtoull(text, &end, 0);
    if (!end || *end != '\0') {
        return 0;
    }
    *out_value = (u64)value;
    return 1;
}

static int trust_parse_q16(const char* text, q16_16* out_value)
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

static int trust_parse_indexed_key(const char* key,
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

static u32 trust_process_from_text(const char* text)
{
    if (!text) {
        return DOM_TRUST_PROCESS_UNSET;
    }
    if (strcmp(text, "increase") == 0) return DOM_TRUST_PROCESS_INCREASE;
    if (strcmp(text, "decrease") == 0) return DOM_TRUST_PROCESS_DECREASE;
    if (strcmp(text, "decay") == 0) return DOM_TRUST_PROCESS_DECAY;
    if (strcmp(text, "transfer") == 0) return DOM_TRUST_PROCESS_TRANSFER;
    return DOM_TRUST_PROCESS_UNSET;
}

static u32 trust_event_flags_from_text(const char* text)
{
    char buffer[TRUST_LINE_MAX];
    char* token;
    u32 flags = 0u;
    if (!text || !*text) {
        return 0u;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    token = strtok(buffer, "|,");
    while (token) {
        char* trimmed = trust_trim(token);
        if (strcmp(trimmed, "incident") == 0) {
            flags |= DOM_TRUST_EVENT_INCIDENT;
        } else if (strcmp(trimmed, "dispute") == 0) {
            flags |= DOM_TRUST_EVENT_DISPUTE;
        }
        token = strtok(0, "|,");
    }
    return flags;
}

static void trust_fixture_init(trust_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_trust_surface_desc_init(&fixture->trust_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "trust.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void trust_fixture_register_region(trust_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_TRUST_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int trust_fixture_apply_field(trust_fixture* fixture,
                                     u32 index,
                                     const char* suffix,
                                     const char* value)
{
    dom_trust_field_desc* field;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_TRUST_MAX_FIELDS) {
        return 0;
    }
    if (fixture->trust_desc.field_count <= index) {
        fixture->trust_desc.field_count = index + 1u;
    }
    field = &fixture->trust_desc.fields[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->field_names[index], value, sizeof(fixture->field_names[index]) - 1);
        fixture->field_names[index][sizeof(fixture->field_names[index]) - 1] = '\0';
        field->trust_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "subject") == 0) {
        field->subject_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "context") == 0) {
        field->context_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "trust") == 0) {
        return trust_parse_q16(value, &field->trust_level);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return trust_parse_q16(value, &field->uncertainty);
    }
    if (strcmp(suffix, "decay") == 0) {
        return trust_parse_q16(value, &field->decay_rate);
    }
    if (strcmp(suffix, "provenance") == 0) {
        field->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        field->region_id = region_id;
        trust_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int trust_fixture_apply_event(trust_fixture* fixture,
                                     u32 index,
                                     const char* suffix,
                                     const char* value)
{
    dom_trust_event_desc* event;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_TRUST_MAX_EVENTS) {
        return 0;
    }
    if (fixture->trust_desc.event_count <= index) {
        fixture->trust_desc.event_count = index + 1u;
    }
    event = &fixture->trust_desc.events[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->event_names[index], value, sizeof(fixture->event_names[index]) - 1);
        fixture->event_names[index][sizeof(fixture->event_names[index]) - 1] = '\0';
        event->event_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "process") == 0) {
        event->process_type = trust_process_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "subject") == 0) {
        event->subject_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "source") == 0) {
        event->source_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "context") == 0) {
        event->context_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "delta") == 0) {
        return trust_parse_q16(value, &event->delta_level);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return trust_parse_q16(value, &event->uncertainty);
    }
    if (strcmp(suffix, "tick") == 0) {
        return trust_parse_u64(value, &event->event_tick);
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        event->region_id = region_id;
        trust_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        event->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        event->flags = trust_event_flags_from_text(value);
        return 1;
    }
    return 0;
}

static int trust_fixture_apply_profile(trust_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_reputation_profile_desc* profile;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_TRUST_MAX_PROFILES) {
        return 0;
    }
    if (fixture->trust_desc.profile_count <= index) {
        fixture->trust_desc.profile_count = index + 1u;
    }
    profile = &fixture->trust_desc.profiles[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->profile_names[index], value, sizeof(fixture->profile_names[index]) - 1);
        fixture->profile_names[index][sizeof(fixture->profile_names[index]) - 1] = '\0';
        profile->profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "subject") == 0) {
        profile->subject_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        profile->region_id = region_id;
        trust_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "performance") == 0) {
        return trust_parse_q16(value, &profile->historical_performance);
    }
    if (strcmp(suffix, "audit") == 0) {
        return trust_parse_q16(value, &profile->audit_results);
    }
    if (strcmp(suffix, "incident") == 0) {
        return trust_parse_q16(value, &profile->incident_history);
    }
    if (strcmp(suffix, "endorse") == 0) {
        return trust_parse_q16(value, &profile->endorsements);
    }
    if (strcmp(suffix, "disputes") == 0) {
        return trust_parse_q16(value, &profile->disputes);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return trust_parse_q16(value, &profile->uncertainty);
    }
    return 0;
}

static int trust_fixture_apply_legitimacy(trust_fixture* fixture,
                                          u32 index,
                                          const char* suffix,
                                          const char* value)
{
    dom_legitimacy_field_desc* field;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_TRUST_MAX_LEGITIMACY) {
        return 0;
    }
    if (fixture->trust_desc.legitimacy_count <= index) {
        fixture->trust_desc.legitimacy_count = index + 1u;
    }
    field = &fixture->trust_desc.legitimacy[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->legitimacy_names[index], value,
                sizeof(fixture->legitimacy_names[index]) - 1);
        fixture->legitimacy_names[index][sizeof(fixture->legitimacy_names[index]) - 1] = '\0';
        field->legitimacy_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "institution") == 0) {
        field->institution_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "scope") == 0) {
        field->authority_scope_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        field->region_id = region_id;
        trust_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "compliance") == 0) {
        return trust_parse_q16(value, &field->compliance_rate);
    }
    if (strcmp(suffix, "challenge") == 0) {
        return trust_parse_q16(value, &field->challenge_rate);
    }
    if (strcmp(suffix, "support") == 0) {
        return trust_parse_q16(value, &field->symbolic_support);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return trust_parse_q16(value, &field->uncertainty);
    }
    if (strcmp(suffix, "provenance") == 0) {
        field->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    return 0;
}

static int trust_fixture_apply(trust_fixture* fixture, const char* key, const char* value)
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
        return trust_parse_u64(value, &fixture->trust_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return trust_parse_u64(value, &fixture->trust_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return trust_parse_q16(value, &fixture->trust_desc.meters_per_unit);
    }
    if (strcmp(key, "field_count") == 0) {
        return trust_parse_u32(value, &fixture->trust_desc.field_count);
    }
    if (strcmp(key, "event_count") == 0) {
        return trust_parse_u32(value, &fixture->trust_desc.event_count);
    }
    if (strcmp(key, "profile_count") == 0) {
        return trust_parse_u32(value, &fixture->trust_desc.profile_count);
    }
    if (strcmp(key, "legitimacy_count") == 0) {
        return trust_parse_u32(value, &fixture->trust_desc.legitimacy_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return trust_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return trust_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return trust_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return trust_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (trust_parse_indexed_key(key, "field_", &index, &suffix)) {
        return trust_fixture_apply_field(fixture, index, suffix, value);
    }
    if (trust_parse_indexed_key(key, "event_", &index, &suffix)) {
        return trust_fixture_apply_event(fixture, index, suffix, value);
    }
    if (trust_parse_indexed_key(key, "profile_", &index, &suffix)) {
        return trust_fixture_apply_profile(fixture, index, suffix, value);
    }
    if (trust_parse_indexed_key(key, "legitimacy_", &index, &suffix)) {
        return trust_fixture_apply_legitimacy(fixture, index, suffix, value);
    }
    return 0;
}

static int trust_fixture_load(const char* path, trust_fixture* out_fixture)
{
    FILE* file;
    char line[TRUST_LINE_MAX];
    int header_ok = 0;
    trust_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    trust_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = trust_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, TRUST_FIXTURE_HEADER) != 0) {
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
        trust_fixture_apply(&fixture, trust_trim(text), trust_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* trust_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 trust_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = trust_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && trust_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 trust_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = trust_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && trust_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 trust_find_region_id(const trust_fixture* fixture, const char* name)
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

static const char* trust_lookup_field_name(const trust_fixture* fixture, u32 field_id)
{
    if (!fixture || field_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->trust_desc.field_count; ++i) {
        if (fixture->trust_desc.fields[i].trust_id == field_id) {
            return fixture->field_names[i];
        }
    }
    return "";
}

static const char* trust_lookup_event_name(const trust_fixture* fixture, u32 event_id)
{
    if (!fixture || event_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->trust_desc.event_count; ++i) {
        if (fixture->trust_desc.events[i].event_id == event_id) {
            return fixture->event_names[i];
        }
    }
    return "";
}

static const char* trust_lookup_profile_name(const trust_fixture* fixture, u32 profile_id)
{
    if (!fixture || profile_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->trust_desc.profile_count; ++i) {
        if (fixture->trust_desc.profiles[i].profile_id == profile_id) {
            return fixture->profile_names[i];
        }
    }
    return "";
}

static const char* trust_lookup_legitimacy_name(const trust_fixture* fixture, u32 legitimacy_id)
{
    if (!fixture || legitimacy_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->trust_desc.legitimacy_count; ++i) {
        if (fixture->trust_desc.legitimacy[i].legitimacy_id == legitimacy_id) {
            return fixture->legitimacy_names[i];
        }
    }
    return "";
}

static int trust_ratio_valid(q16_16 value)
{
    return !(value < 0 || value > DOM_TRUST_RATIO_ONE_Q16);
}

static int trust_validate_fixture(const trust_fixture* fixture)
{
    if (!fixture) {
        return 0;
    }
    if (fixture->trust_desc.field_count > DOM_TRUST_MAX_FIELDS) {
        return 0;
    }
    if (fixture->trust_desc.event_count > DOM_TRUST_MAX_EVENTS) {
        return 0;
    }
    if (fixture->trust_desc.profile_count > DOM_TRUST_MAX_PROFILES) {
        return 0;
    }
    if (fixture->trust_desc.legitimacy_count > DOM_TRUST_MAX_LEGITIMACY) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->trust_desc.field_count; ++i) {
        const dom_trust_field_desc* field = &fixture->trust_desc.fields[i];
        if (field->trust_id == 0u) {
            return 0;
        }
        if (!trust_ratio_valid(field->trust_level)) {
            return 0;
        }
        if (!trust_ratio_valid(field->uncertainty)) {
            return 0;
        }
        if (!trust_ratio_valid(field->decay_rate)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->trust_desc.event_count; ++i) {
        const dom_trust_event_desc* event = &fixture->trust_desc.events[i];
        if (event->event_id == 0u) {
            return 0;
        }
        if (event->process_type == DOM_TRUST_PROCESS_UNSET) {
            return 0;
        }
        if (!trust_ratio_valid(event->delta_level)) {
            return 0;
        }
        if (!trust_ratio_valid(event->uncertainty)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->trust_desc.profile_count; ++i) {
        const dom_reputation_profile_desc* profile = &fixture->trust_desc.profiles[i];
        if (profile->profile_id == 0u) {
            return 0;
        }
        if (!trust_ratio_valid(profile->historical_performance)) {
            return 0;
        }
        if (!trust_ratio_valid(profile->audit_results)) {
            return 0;
        }
        if (!trust_ratio_valid(profile->incident_history)) {
            return 0;
        }
        if (!trust_ratio_valid(profile->endorsements)) {
            return 0;
        }
        if (!trust_ratio_valid(profile->disputes)) {
            return 0;
        }
        if (!trust_ratio_valid(profile->uncertainty)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->trust_desc.legitimacy_count; ++i) {
        const dom_legitimacy_field_desc* field = &fixture->trust_desc.legitimacy[i];
        if (field->legitimacy_id == 0u) {
            return 0;
        }
        if (!trust_ratio_valid(field->compliance_rate)) {
            return 0;
        }
        if (!trust_ratio_valid(field->challenge_rate)) {
            return 0;
        }
        if (!trust_ratio_valid(field->symbolic_support)) {
            return 0;
        }
        if (!trust_ratio_valid(field->uncertainty)) {
            return 0;
        }
    }
    return 1;
}

static int trust_run_validate(const trust_fixture* fixture)
{
    int ok = trust_validate_fixture(fixture);
    printf("%s\n", TRUST_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRUST_PROVIDER_CHAIN);
    printf("field_count=%u\n", (unsigned int)fixture->trust_desc.field_count);
    printf("event_count=%u\n", (unsigned int)fixture->trust_desc.event_count);
    printf("profile_count=%u\n", (unsigned int)fixture->trust_desc.profile_count);
    printf("legitimacy_count=%u\n", (unsigned int)fixture->trust_desc.legitimacy_count);
    printf("ok=%u\n", (unsigned int)(ok ? 1u : 0u));
    return ok ? 0 : 1;
}

static int trust_run_inspect_field(const trust_fixture* fixture,
                                   const char* field_name,
                                   u32 budget_max)
{
    dom_trust_domain domain;
    dom_domain_budget budget;
    dom_trust_field_sample sample;
    u32 field_id;
    if (!field_name) {
        return 1;
    }
    field_id = d_rng_hash_str32(field_name);
    dom_trust_domain_init(&domain, &fixture->trust_desc);
    if (fixture->policy_set) {
        dom_trust_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_trust_field_query(&domain, field_id, &budget, &sample);

    printf("%s\n", TRUST_INSPECT_HEADER);
    printf("entity=field\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRUST_PROVIDER_CHAIN);
    printf("trust_id=%u\n", (unsigned int)sample.trust_id);
    printf("trust_id_str=%s\n", trust_lookup_field_name(fixture, sample.trust_id));
    printf("subject_ref_id=%u\n", (unsigned int)sample.subject_ref_id);
    printf("context_id=%u\n", (unsigned int)sample.context_id);
    printf("trust_level_q16=%d\n", (int)sample.trust_level);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
    printf("decay_rate_q16=%d\n", (int)sample.decay_rate);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_trust_domain_free(&domain);
    return 0;
}

static int trust_run_inspect_event(const trust_fixture* fixture,
                                   const char* event_name,
                                   u32 budget_max)
{
    dom_trust_domain domain;
    dom_domain_budget budget;
    dom_trust_event_sample sample;
    u32 event_id;
    if (!event_name) {
        return 1;
    }
    event_id = d_rng_hash_str32(event_name);
    dom_trust_domain_init(&domain, &fixture->trust_desc);
    if (fixture->policy_set) {
        dom_trust_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_trust_event_query(&domain, event_id, &budget, &sample);

    printf("%s\n", TRUST_INSPECT_HEADER);
    printf("entity=event\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRUST_PROVIDER_CHAIN);
    printf("event_id=%u\n", (unsigned int)sample.event_id);
    printf("event_id_str=%s\n", trust_lookup_event_name(fixture, sample.event_id));
    printf("process_type=%u\n", (unsigned int)sample.process_type);
    printf("subject_ref_id=%u\n", (unsigned int)sample.subject_ref_id);
    printf("source_ref_id=%u\n", (unsigned int)sample.source_ref_id);
    printf("context_id=%u\n", (unsigned int)sample.context_id);
    printf("delta_level_q16=%d\n", (int)sample.delta_level);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
    printf("event_tick=%llu\n", (unsigned long long)sample.event_tick);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_trust_domain_free(&domain);
    return 0;
}

static int trust_run_inspect_profile(const trust_fixture* fixture,
                                     const char* profile_name,
                                     u32 budget_max)
{
    dom_trust_domain domain;
    dom_domain_budget budget;
    dom_reputation_profile_sample sample;
    u32 profile_id;
    if (!profile_name) {
        return 1;
    }
    profile_id = d_rng_hash_str32(profile_name);
    dom_trust_domain_init(&domain, &fixture->trust_desc);
    if (fixture->policy_set) {
        dom_trust_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_reputation_profile_query(&domain, profile_id, &budget, &sample);

    printf("%s\n", TRUST_INSPECT_HEADER);
    printf("entity=profile\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRUST_PROVIDER_CHAIN);
    printf("profile_id=%u\n", (unsigned int)sample.profile_id);
    printf("profile_id_str=%s\n", trust_lookup_profile_name(fixture, sample.profile_id));
    printf("subject_ref_id=%u\n", (unsigned int)sample.subject_ref_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("historical_performance_q16=%d\n", (int)sample.historical_performance);
    printf("audit_results_q16=%d\n", (int)sample.audit_results);
    printf("incident_history_q16=%d\n", (int)sample.incident_history);
    printf("endorsements_q16=%d\n", (int)sample.endorsements);
    printf("disputes_q16=%d\n", (int)sample.disputes);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_trust_domain_free(&domain);
    return 0;
}

static int trust_run_inspect_legitimacy(const trust_fixture* fixture,
                                        const char* legitimacy_name,
                                        u32 budget_max)
{
    dom_trust_domain domain;
    dom_domain_budget budget;
    dom_legitimacy_field_sample sample;
    u32 legitimacy_id;
    if (!legitimacy_name) {
        return 1;
    }
    legitimacy_id = d_rng_hash_str32(legitimacy_name);
    dom_trust_domain_init(&domain, &fixture->trust_desc);
    if (fixture->policy_set) {
        dom_trust_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_legitimacy_field_query(&domain, legitimacy_id, &budget, &sample);

    printf("%s\n", TRUST_INSPECT_HEADER);
    printf("entity=legitimacy\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRUST_PROVIDER_CHAIN);
    printf("legitimacy_id=%u\n", (unsigned int)sample.legitimacy_id);
    printf("legitimacy_id_str=%s\n", trust_lookup_legitimacy_name(fixture, sample.legitimacy_id));
    printf("institution_ref_id=%u\n", (unsigned int)sample.institution_ref_id);
    printf("authority_scope_id=%u\n", (unsigned int)sample.authority_scope_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("compliance_rate_q16=%d\n", (int)sample.compliance_rate);
    printf("challenge_rate_q16=%d\n", (int)sample.challenge_rate);
    printf("symbolic_support_q16=%d\n", (int)sample.symbolic_support);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_trust_domain_free(&domain);
    return 0;
}

static int trust_run_inspect_region(const trust_fixture* fixture,
                                    const char* region_name,
                                    u32 budget_max)
{
    dom_trust_domain domain;
    dom_domain_budget budget;
    dom_trust_region_sample sample;
    u32 region_id = trust_find_region_id(fixture, region_name);

    dom_trust_domain_init(&domain, &fixture->trust_desc);
    if (fixture->policy_set) {
        dom_trust_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_trust_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", TRUST_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRUST_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("field_count=%u\n", (unsigned int)sample.field_count);
    printf("event_count=%u\n", (unsigned int)sample.event_count);
    printf("profile_count=%u\n", (unsigned int)sample.profile_count);
    printf("legitimacy_count=%u\n", (unsigned int)sample.legitimacy_count);
    printf("trust_avg_q16=%d\n", (int)sample.trust_avg);
    printf("dispute_rate_avg_q16=%d\n", (int)sample.dispute_rate_avg);
    printf("compliance_rate_avg_q16=%d\n", (int)sample.compliance_rate_avg);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_trust_domain_free(&domain);
    return 0;
}

static int trust_run_resolve(const trust_fixture* fixture,
                             const char* region_name,
                             u64 tick,
                             u64 tick_delta,
                             u32 budget_max,
                             u32 inactive_count)
{
    dom_trust_domain domain;
    dom_trust_domain* inactive = 0;
    dom_domain_budget budget;
    dom_trust_resolve_result result;
    u32 region_id = trust_find_region_id(fixture, region_name);
    u64 hash = 14695981039346656037ULL;

    dom_trust_domain_init(&domain, &fixture->trust_desc);
    if (fixture->policy_set) {
        dom_trust_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_trust_domain*)malloc(sizeof(dom_trust_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                trust_fixture temp = *fixture;
                temp.trust_desc.domain_id = fixture->trust_desc.domain_id + (u64)(i + 1u);
                dom_trust_domain_init(&inactive[i], &temp.trust_desc);
                dom_trust_domain_set_state(&inactive[i],
                                           DOM_DOMAIN_EXISTENCE_DECLARED,
                                           DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_trust_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.field_count; ++i) {
        hash = trust_hash_u32(hash, domain.fields[i].trust_id);
        hash = trust_hash_q16(hash, domain.fields[i].trust_level);
        hash = trust_hash_q16(hash, domain.fields[i].uncertainty);
    }
    for (u32 i = 0u; i < domain.event_count; ++i) {
        hash = trust_hash_u32(hash, domain.events[i].event_id);
        hash = trust_hash_u32(hash, domain.events[i].flags);
    }
    for (u32 i = 0u; i < domain.profile_count; ++i) {
        hash = trust_hash_u32(hash, domain.profiles[i].profile_id);
        hash = trust_hash_q16(hash, domain.profiles[i].historical_performance);
        hash = trust_hash_q16(hash, domain.profiles[i].disputes);
    }
    for (u32 i = 0u; i < domain.legitimacy_count; ++i) {
        hash = trust_hash_u32(hash, domain.legitimacy[i].legitimacy_id);
        hash = trust_hash_q16(hash, domain.legitimacy[i].compliance_rate);
        hash = trust_hash_q16(hash, domain.legitimacy[i].challenge_rate);
    }

    printf("%s\n", TRUST_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRUST_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("field_count=%u\n", (unsigned int)result.field_count);
    printf("event_count=%u\n", (unsigned int)result.event_count);
    printf("event_applied_count=%u\n", (unsigned int)result.event_applied_count);
    printf("profile_count=%u\n", (unsigned int)result.profile_count);
    printf("legitimacy_count=%u\n", (unsigned int)result.legitimacy_count);
    printf("trust_avg_q16=%d\n", (int)result.trust_avg);
    printf("dispute_rate_avg_q16=%d\n", (int)result.dispute_rate_avg);
    printf("compliance_rate_avg_q16=%d\n", (int)result.compliance_rate_avg);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_trust_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_trust_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int trust_run_collapse(const trust_fixture* fixture, const char* region_name)
{
    dom_trust_domain domain;
    u32 region_id = trust_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_trust_domain_init(&domain, &fixture->trust_desc);
    if (fixture->policy_set) {
        dom_trust_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_trust_domain_capsule_count(&domain);
    (void)dom_trust_domain_collapse_region(&domain, region_id);
    count_after = dom_trust_domain_capsule_count(&domain);

    printf("%s\n", TRUST_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", TRUST_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_trust_domain_free(&domain);
    return 0;
}

static void trust_usage(void)
{
    printf("dom_tool_trust commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --field <id> [--budget N]\n");
    printf("  inspect --fixture <path> --event <id> [--budget N]\n");
    printf("  inspect --fixture <path> --profile <id> [--budget N]\n");
    printf("  inspect --fixture <path> --legitimacy <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        trust_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = trust_find_arg(argc, argv, "--fixture");
        trust_fixture fixture;
        if (!fixture_path || !trust_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "trust: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return trust_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* field_name = trust_find_arg(argc, argv, "--field");
            const char* event_name = trust_find_arg(argc, argv, "--event");
            const char* profile_name = trust_find_arg(argc, argv, "--profile");
            const char* legitimacy_name = trust_find_arg(argc, argv, "--legitimacy");
            const char* region_name = trust_find_arg(argc, argv, "--region");
            u32 budget_max = trust_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (field_name) {
                return trust_run_inspect_field(&fixture, field_name, budget_max);
            }
            if (event_name) {
                return trust_run_inspect_event(&fixture, event_name, budget_max);
            }
            if (profile_name) {
                return trust_run_inspect_profile(&fixture, profile_name, budget_max);
            }
            if (legitimacy_name) {
                return trust_run_inspect_legitimacy(&fixture, legitimacy_name, budget_max);
            }
            if (region_name) {
                return trust_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr, "trust: inspect requires --field, --event, --profile, --legitimacy, or --region\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = trust_find_arg(argc, argv, "--region");
            u64 tick = trust_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = trust_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = trust_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = trust_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!region_name) {
                fprintf(stderr, "trust: resolve requires --region\n");
                return 2;
            }
            return trust_run_resolve(&fixture, region_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = trust_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "trust: collapse requires --region\n");
                return 2;
            }
            return trust_run_collapse(&fixture, region_name);
        }
    }

    trust_usage();
    return 2;
}
