/*
FILE: tools/risk/risk_cli.cpp
MODULE: Dominium
PURPOSE: Risk fixture CLI for deterministic risk, liability, and insurance checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/risk_fields.h"

#define RISK_FIXTURE_HEADER "DOMINIUM_RISK_FIXTURE_V1"

#define RISK_VALIDATE_HEADER "DOMINIUM_RISK_VALIDATE_V1"
#define RISK_INSPECT_HEADER "DOMINIUM_RISK_INSPECT_V1"
#define RISK_RESOLVE_HEADER "DOMINIUM_RISK_RESOLVE_V1"
#define RISK_COLLAPSE_HEADER "DOMINIUM_RISK_COLLAPSE_V1"

#define RISK_PROVIDER_CHAIN "types->fields->exposures->profiles->liability->insurance"

#define RISK_LINE_MAX 512u

typedef struct risk_fixture {
    char fixture_id[96];
    dom_risk_surface_desc risk_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char type_names[DOM_RISK_MAX_TYPES][64];
    char field_names[DOM_RISK_MAX_FIELDS][64];
    char exposure_names[DOM_RISK_MAX_EXPOSURES][64];
    char profile_names[DOM_RISK_MAX_PROFILES][64];
    char event_names[DOM_RISK_MAX_EVENTS][64];
    char attribution_names[DOM_RISK_MAX_ATTRIBUTIONS][64];
    char policy_names[DOM_RISK_MAX_POLICIES][64];
    char claim_names[DOM_RISK_MAX_CLAIMS][64];
    char region_names[DOM_RISK_MAX_REGIONS][64];
    u32 region_ids[DOM_RISK_MAX_REGIONS];
    u32 region_count;
} risk_fixture;

static u64 risk_hash_u64(u64 h, u64 v)
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

static u64 risk_hash_u32(u64 h, u32 v)
{
    return risk_hash_u64(h, (u64)v);
}

static u64 risk_hash_q16(u64 h, q16_16 v)
{
    return risk_hash_u64(h, (u64)(u32)v);
}

static u64 risk_hash_q48(u64 h, q48_16 v)
{
    return risk_hash_u64(h, (u64)v);
}

static char* risk_trim(char* text)
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

static int risk_parse_u32(const char* text, u32* out_value)
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

static int risk_parse_u64(const char* text, u64* out_value)
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

static int risk_parse_q16(const char* text, q16_16* out_value)
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

static int risk_parse_q48(const char* text, q48_16* out_value)
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
    *out_value = d_q48_16_from_double(value);
    return 1;
}

static int risk_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[RISK_LINE_MAX];
    char* first;
    char* second;
    char* third;
    if (!text || !a || !b || !c) {
        return 0;
    }
    strncpy(buffer, text, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';
    first = buffer;
    second = strchr(first, ',');
    if (!second) {
        return 0;
    }
    *second++ = '\0';
    third = strchr(second, ',');
    if (!third) {
        return 0;
    }
    *third++ = '\0';
    if (!risk_parse_q16(risk_trim(first), a)) return 0;
    if (!risk_parse_q16(risk_trim(second), b)) return 0;
    if (!risk_parse_q16(risk_trim(third), c)) return 0;
    return 1;
}

static int risk_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!risk_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static int risk_parse_indexed_key(const char* key,
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

static u32 risk_class_from_text(const char* text)
{
    if (!text) {
        return DOM_RISK_CLASS_UNSET;
    }
    if (strcmp(text, "fire") == 0) return DOM_RISK_CLASS_FIRE;
    if (strcmp(text, "flood") == 0) return DOM_RISK_CLASS_FLOOD;
    if (strcmp(text, "toxic") == 0) return DOM_RISK_CLASS_TOXIC;
    if (strcmp(text, "thermal") == 0) return DOM_RISK_CLASS_THERMAL;
    if (strcmp(text, "financial") == 0) return DOM_RISK_CLASS_FINANCIAL;
    if (strcmp(text, "info") == 0) return DOM_RISK_CLASS_INFO;
    return DOM_RISK_CLASS_UNSET;
}

static void risk_fixture_init(risk_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_risk_surface_desc_init(&fixture->risk_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "risk.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void risk_fixture_register_region(risk_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_RISK_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int risk_fixture_apply_type(risk_fixture* fixture,
                                   u32 index,
                                   const char* suffix,
                                   const char* value)
{
    dom_risk_type_desc* type;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_RISK_MAX_TYPES) {
        return 0;
    }
    if (fixture->risk_desc.type_count <= index) {
        fixture->risk_desc.type_count = index + 1u;
    }
    type = &fixture->risk_desc.types[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->type_names[index], value, sizeof(fixture->type_names[index]) - 1);
        fixture->type_names[index][sizeof(fixture->type_names[index]) - 1] = '\0';
        type->type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "class") == 0) {
        type->risk_class = risk_class_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "default_exposure") == 0) {
        return risk_parse_q16(value, &type->default_exposure_rate);
    }
    if (strcmp(suffix, "default_impact_mean") == 0) {
        return risk_parse_q48(value, &type->default_impact_mean);
    }
    if (strcmp(suffix, "default_impact_spread") == 0) {
        return risk_parse_q16(value, &type->default_impact_spread);
    }
    if (strcmp(suffix, "default_uncertainty") == 0) {
        return risk_parse_q16(value, &type->default_uncertainty);
    }
    return 0;
}

static int risk_fixture_apply_field(risk_fixture* fixture,
                                    u32 index,
                                    const char* suffix,
                                    const char* value)
{
    dom_risk_field_desc* field;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_RISK_MAX_FIELDS) {
        return 0;
    }
    if (fixture->risk_desc.field_count <= index) {
        fixture->risk_desc.field_count = index + 1u;
    }
    field = &fixture->risk_desc.fields[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->field_names[index], value, sizeof(fixture->field_names[index]) - 1);
        fixture->field_names[index][sizeof(fixture->field_names[index]) - 1] = '\0';
        field->risk_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        field->risk_type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "exposure_rate") == 0) {
        return risk_parse_q16(value, &field->exposure_rate);
    }
    if (strcmp(suffix, "impact_mean") == 0) {
        return risk_parse_q48(value, &field->impact_mean);
    }
    if (strcmp(suffix, "impact_spread") == 0) {
        return risk_parse_q16(value, &field->impact_spread);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return risk_parse_q16(value, &field->uncertainty);
    }
    if (strcmp(suffix, "hazard_ref") == 0) {
        field->hazard_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        field->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        field->region_id = region_id;
        risk_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "radius") == 0) {
        return risk_parse_q16(value, &field->radius);
    }
    if (strcmp(suffix, "pos") == 0) {
        return risk_parse_point(value, &field->center);
    }
    return 0;
}

static int risk_fixture_apply_exposure(risk_fixture* fixture,
                                       u32 index,
                                       const char* suffix,
                                       const char* value)
{
    dom_risk_exposure_desc* exposure;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_RISK_MAX_EXPOSURES) {
        return 0;
    }
    if (fixture->risk_desc.exposure_count <= index) {
        fixture->risk_desc.exposure_count = index + 1u;
    }
    exposure = &fixture->risk_desc.exposures[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->exposure_names[index], value, sizeof(fixture->exposure_names[index]) - 1);
        fixture->exposure_names[index][sizeof(fixture->exposure_names[index]) - 1] = '\0';
        exposure->exposure_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        exposure->risk_type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "exposure_rate") == 0) {
        return risk_parse_q16(value, &exposure->exposure_rate);
    }
    if (strcmp(suffix, "limit") == 0) {
        return risk_parse_q48(value, &exposure->exposure_limit);
    }
    if (strcmp(suffix, "accumulated") == 0) {
        return risk_parse_q48(value, &exposure->exposure_accumulated);
    }
    if (strcmp(suffix, "sensitivity") == 0) {
        return risk_parse_q16(value, &exposure->sensitivity);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return risk_parse_q16(value, &exposure->uncertainty);
    }
    if (strcmp(suffix, "subject") == 0) {
        exposure->subject_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        exposure->region_id = region_id;
        risk_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "pos") == 0) {
        return risk_parse_point(value, &exposure->location);
    }
    if (strcmp(suffix, "provenance") == 0) {
        exposure->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    return 0;
}

static int risk_fixture_apply_profile(risk_fixture* fixture,
                                      u32 index,
                                      const char* suffix,
                                      const char* value)
{
    dom_risk_profile_desc* profile;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_RISK_MAX_PROFILES) {
        return 0;
    }
    if (fixture->risk_desc.profile_count <= index) {
        fixture->risk_desc.profile_count = index + 1u;
    }
    profile = &fixture->risk_desc.profiles[index];
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
        risk_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "exposure_total") == 0) {
        return risk_parse_q48(value, &profile->exposure_total);
    }
    if (strcmp(suffix, "impact_mean") == 0) {
        return risk_parse_q48(value, &profile->impact_mean);
    }
    if (strcmp(suffix, "impact_spread") == 0) {
        return risk_parse_q16(value, &profile->impact_spread);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return risk_parse_q16(value, &profile->uncertainty);
    }
    return 0;
}

static int risk_fixture_apply_event(risk_fixture* fixture,
                                    u32 index,
                                    const char* suffix,
                                    const char* value)
{
    dom_liability_event_desc* event;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_RISK_MAX_EVENTS) {
        return 0;
    }
    if (fixture->risk_desc.event_count <= index) {
        fixture->risk_desc.event_count = index + 1u;
    }
    event = &fixture->risk_desc.events[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->event_names[index], value, sizeof(fixture->event_names[index]) - 1);
        fixture->event_names[index][sizeof(fixture->event_names[index]) - 1] = '\0';
        event->event_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        event->risk_type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "hazard_ref") == 0) {
        event->hazard_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "exposure_ref") == 0) {
        event->exposure_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "loss") == 0) {
        return risk_parse_q48(value, &event->loss_amount);
    }
    if (strcmp(suffix, "tick") == 0) {
        return risk_parse_u64(value, &event->event_tick);
    }
    if (strcmp(suffix, "subject") == 0) {
        event->subject_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        event->region_id = region_id;
        risk_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        event->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    return 0;
}

static int risk_fixture_apply_attribution(risk_fixture* fixture,
                                          u32 index,
                                          const char* suffix,
                                          const char* value)
{
    dom_liability_attribution_desc* attrib;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_RISK_MAX_ATTRIBUTIONS) {
        return 0;
    }
    if (fixture->risk_desc.attribution_count <= index) {
        fixture->risk_desc.attribution_count = index + 1u;
    }
    attrib = &fixture->risk_desc.attributions[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->attribution_names[index], value,
                sizeof(fixture->attribution_names[index]) - 1);
        fixture->attribution_names[index][sizeof(fixture->attribution_names[index]) - 1] = '\0';
        attrib->attribution_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "event") == 0) {
        attrib->event_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "responsible") == 0) {
        attrib->responsible_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "role") == 0) {
        attrib->role_tag = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "compliance") == 0) {
        attrib->compliance_tag = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "negligence") == 0) {
        return risk_parse_q16(value, &attrib->negligence_score);
    }
    if (strcmp(suffix, "share") == 0) {
        return risk_parse_q16(value, &attrib->share_ratio);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return risk_parse_q16(value, &attrib->uncertainty);
    }
    if (strcmp(suffix, "provenance") == 0) {
        attrib->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    return 0;
}

static int risk_fixture_apply_policy(risk_fixture* fixture,
                                     u32 index,
                                     const char* suffix,
                                     const char* value)
{
    dom_insurance_policy_desc* policy;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_RISK_MAX_POLICIES) {
        return 0;
    }
    if (fixture->risk_desc.policy_count <= index) {
        fixture->risk_desc.policy_count = index + 1u;
    }
    policy = &fixture->risk_desc.policies[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->policy_names[index], value, sizeof(fixture->policy_names[index]) - 1);
        fixture->policy_names[index][sizeof(fixture->policy_names[index]) - 1] = '\0';
        policy->policy_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "holder") == 0) {
        policy->holder_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        policy->risk_type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "coverage") == 0) {
        return risk_parse_q16(value, &policy->coverage_ratio);
    }
    if (strcmp(suffix, "premium") == 0) {
        return risk_parse_q48(value, &policy->premium);
    }
    if (strcmp(suffix, "limit") == 0) {
        return risk_parse_q48(value, &policy->payout_limit);
    }
    if (strcmp(suffix, "deductible") == 0) {
        return risk_parse_q48(value, &policy->deductible);
    }
    if (strcmp(suffix, "audit_tag") == 0) {
        policy->audit_tag = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "audit_score") == 0) {
        return risk_parse_q16(value, &policy->audit_score);
    }
    if (strcmp(suffix, "start_tick") == 0) {
        return risk_parse_u64(value, &policy->start_tick);
    }
    if (strcmp(suffix, "end_tick") == 0) {
        return risk_parse_u64(value, &policy->end_tick);
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        policy->region_id = region_id;
        risk_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int risk_fixture_apply_claim(risk_fixture* fixture,
                                    u32 index,
                                    const char* suffix,
                                    const char* value)
{
    dom_insurance_claim_desc* claim;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_RISK_MAX_CLAIMS) {
        return 0;
    }
    if (fixture->risk_desc.claim_count <= index) {
        fixture->risk_desc.claim_count = index + 1u;
    }
    claim = &fixture->risk_desc.claims[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->claim_names[index], value, sizeof(fixture->claim_names[index]) - 1);
        fixture->claim_names[index][sizeof(fixture->claim_names[index]) - 1] = '\0';
        claim->claim_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "policy") == 0) {
        claim->policy_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "event") == 0) {
        claim->event_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "amount") == 0) {
        return risk_parse_q48(value, &claim->claim_amount);
    }
    if (strcmp(suffix, "approved") == 0) {
        return risk_parse_q48(value, &claim->approved_amount);
    }
    if (strcmp(suffix, "status") == 0) {
        claim->status_tag = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "filed") == 0) {
        return risk_parse_u64(value, &claim->filed_tick);
    }
    if (strcmp(suffix, "resolved") == 0) {
        return risk_parse_u64(value, &claim->resolved_tick);
    }
    if (strcmp(suffix, "audit_ref") == 0) {
        claim->audit_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    return 0;
}

static int risk_fixture_apply(risk_fixture* fixture, const char* key, const char* value)
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
        return risk_parse_u64(value, &fixture->risk_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return risk_parse_u64(value, &fixture->risk_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return risk_parse_q16(value, &fixture->risk_desc.meters_per_unit);
    }
    if (strcmp(key, "type_count") == 0) {
        return risk_parse_u32(value, &fixture->risk_desc.type_count);
    }
    if (strcmp(key, "field_count") == 0) {
        return risk_parse_u32(value, &fixture->risk_desc.field_count);
    }
    if (strcmp(key, "exposure_count") == 0) {
        return risk_parse_u32(value, &fixture->risk_desc.exposure_count);
    }
    if (strcmp(key, "profile_count") == 0) {
        return risk_parse_u32(value, &fixture->risk_desc.profile_count);
    }
    if (strcmp(key, "event_count") == 0) {
        return risk_parse_u32(value, &fixture->risk_desc.event_count);
    }
    if (strcmp(key, "attribution_count") == 0) {
        return risk_parse_u32(value, &fixture->risk_desc.attribution_count);
    }
    if (strcmp(key, "policy_count") == 0) {
        return risk_parse_u32(value, &fixture->risk_desc.policy_count);
    }
    if (strcmp(key, "claim_count") == 0) {
        return risk_parse_u32(value, &fixture->risk_desc.claim_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return risk_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return risk_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return risk_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return risk_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (risk_parse_indexed_key(key, "type_", &index, &suffix)) {
        return risk_fixture_apply_type(fixture, index, suffix, value);
    }
    if (risk_parse_indexed_key(key, "field_", &index, &suffix)) {
        return risk_fixture_apply_field(fixture, index, suffix, value);
    }
    if (risk_parse_indexed_key(key, "exposure_", &index, &suffix)) {
        return risk_fixture_apply_exposure(fixture, index, suffix, value);
    }
    if (risk_parse_indexed_key(key, "profile_", &index, &suffix)) {
        return risk_fixture_apply_profile(fixture, index, suffix, value);
    }
    if (risk_parse_indexed_key(key, "event_", &index, &suffix)) {
        return risk_fixture_apply_event(fixture, index, suffix, value);
    }
    if (risk_parse_indexed_key(key, "attribution_", &index, &suffix)) {
        return risk_fixture_apply_attribution(fixture, index, suffix, value);
    }
    if (risk_parse_indexed_key(key, "policy_", &index, &suffix)) {
        return risk_fixture_apply_policy(fixture, index, suffix, value);
    }
    if (risk_parse_indexed_key(key, "claim_", &index, &suffix)) {
        return risk_fixture_apply_claim(fixture, index, suffix, value);
    }
    return 0;
}

static int risk_fixture_load(const char* path, risk_fixture* out_fixture)
{
    FILE* file;
    char line[RISK_LINE_MAX];
    int header_ok = 0;
    risk_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    risk_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = risk_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, RISK_FIXTURE_HEADER) != 0) {
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
        risk_fixture_apply(&fixture, risk_trim(text), risk_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* risk_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 risk_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = risk_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && risk_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 risk_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = risk_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && risk_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 risk_find_region_id(const risk_fixture* fixture, const char* name)
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

static const char* risk_lookup_type_name(const risk_fixture* fixture, u32 type_id)
{
    if (!fixture || type_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->risk_desc.type_count; ++i) {
        if (fixture->risk_desc.types[i].type_id == type_id) {
            return fixture->type_names[i];
        }
    }
    return "";
}

static const char* risk_lookup_field_name(const risk_fixture* fixture, u32 field_id)
{
    if (!fixture || field_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->risk_desc.field_count; ++i) {
        if (fixture->risk_desc.fields[i].risk_id == field_id) {
            return fixture->field_names[i];
        }
    }
    return "";
}

static const char* risk_lookup_exposure_name(const risk_fixture* fixture, u32 exposure_id)
{
    if (!fixture || exposure_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->risk_desc.exposure_count; ++i) {
        if (fixture->risk_desc.exposures[i].exposure_id == exposure_id) {
            return fixture->exposure_names[i];
        }
    }
    return "";
}

static const char* risk_lookup_profile_name(const risk_fixture* fixture, u32 profile_id)
{
    if (!fixture || profile_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->risk_desc.profile_count; ++i) {
        if (fixture->risk_desc.profiles[i].profile_id == profile_id) {
            return fixture->profile_names[i];
        }
    }
    return "";
}

static const char* risk_lookup_event_name(const risk_fixture* fixture, u32 event_id)
{
    if (!fixture || event_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->risk_desc.event_count; ++i) {
        if (fixture->risk_desc.events[i].event_id == event_id) {
            return fixture->event_names[i];
        }
    }
    return "";
}

static const char* risk_lookup_policy_name(const risk_fixture* fixture, u32 policy_id)
{
    if (!fixture || policy_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->risk_desc.policy_count; ++i) {
        if (fixture->risk_desc.policies[i].policy_id == policy_id) {
            return fixture->policy_names[i];
        }
    }
    return "";
}

static const char* risk_lookup_claim_name(const risk_fixture* fixture, u32 claim_id)
{
    if (!fixture || claim_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->risk_desc.claim_count; ++i) {
        if (fixture->risk_desc.claims[i].claim_id == claim_id) {
            return fixture->claim_names[i];
        }
    }
    return "";
}

static const char* risk_lookup_attribution_name(const risk_fixture* fixture, u32 attribution_id)
{
    if (!fixture || attribution_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->risk_desc.attribution_count; ++i) {
        if (fixture->risk_desc.attributions[i].attribution_id == attribution_id) {
            return fixture->attribution_names[i];
        }
    }
    return "";
}

static int risk_type_exists(const risk_fixture* fixture, u32 type_id)
{
    if (!fixture || type_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->risk_desc.type_count; ++i) {
        if (fixture->risk_desc.types[i].type_id == type_id) {
            return 1;
        }
    }
    return 0;
}

static int risk_ratio_valid(q16_16 value)
{
    return !(value < 0 || value > DOM_RISK_RATIO_ONE_Q16);
}

static int risk_validate_fixture(const risk_fixture* fixture)
{
    if (!fixture) {
        return 0;
    }
    if (fixture->risk_desc.type_count > DOM_RISK_MAX_TYPES) {
        return 0;
    }
    if (fixture->risk_desc.field_count > DOM_RISK_MAX_FIELDS) {
        return 0;
    }
    if (fixture->risk_desc.exposure_count > DOM_RISK_MAX_EXPOSURES) {
        return 0;
    }
    if (fixture->risk_desc.profile_count > DOM_RISK_MAX_PROFILES) {
        return 0;
    }
    if (fixture->risk_desc.event_count > DOM_RISK_MAX_EVENTS) {
        return 0;
    }
    if (fixture->risk_desc.attribution_count > DOM_RISK_MAX_ATTRIBUTIONS) {
        return 0;
    }
    if (fixture->risk_desc.policy_count > DOM_RISK_MAX_POLICIES) {
        return 0;
    }
    if (fixture->risk_desc.claim_count > DOM_RISK_MAX_CLAIMS) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->risk_desc.type_count; ++i) {
        const dom_risk_type_desc* type = &fixture->risk_desc.types[i];
        if (type->type_id == 0u) {
            return 0;
        }
        if (!risk_ratio_valid(type->default_exposure_rate)) {
            return 0;
        }
        if (!risk_ratio_valid(type->default_impact_spread)) {
            return 0;
        }
        if (!risk_ratio_valid(type->default_uncertainty)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->risk_desc.field_count; ++i) {
        const dom_risk_field_desc* field = &fixture->risk_desc.fields[i];
        if (field->risk_id == 0u) {
            return 0;
        }
        if (field->risk_type_id == 0u || !risk_type_exists(fixture, field->risk_type_id)) {
            return 0;
        }
        if (!risk_ratio_valid(field->exposure_rate)) {
            return 0;
        }
        if (!risk_ratio_valid(field->impact_spread)) {
            return 0;
        }
        if (!risk_ratio_valid(field->uncertainty)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->risk_desc.exposure_count; ++i) {
        const dom_risk_exposure_desc* exposure = &fixture->risk_desc.exposures[i];
        if (exposure->exposure_id == 0u) {
            return 0;
        }
        if (exposure->risk_type_id != 0u &&
            !risk_type_exists(fixture, exposure->risk_type_id)) {
            return 0;
        }
        if (!risk_ratio_valid(exposure->exposure_rate)) {
            return 0;
        }
        if (!risk_ratio_valid(exposure->sensitivity)) {
            return 0;
        }
        if (!risk_ratio_valid(exposure->uncertainty)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->risk_desc.profile_count; ++i) {
        const dom_risk_profile_desc* profile = &fixture->risk_desc.profiles[i];
        if (profile->profile_id == 0u) {
            return 0;
        }
        if (!risk_ratio_valid(profile->impact_spread)) {
            return 0;
        }
        if (!risk_ratio_valid(profile->uncertainty)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->risk_desc.policy_count; ++i) {
        const dom_insurance_policy_desc* policy = &fixture->risk_desc.policies[i];
        if (policy->policy_id == 0u) {
            return 0;
        }
        if (!risk_ratio_valid(policy->coverage_ratio)) {
            return 0;
        }
        if (!risk_ratio_valid(policy->audit_score)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->risk_desc.claim_count; ++i) {
        const dom_insurance_claim_desc* claim = &fixture->risk_desc.claims[i];
        if (claim->claim_id == 0u) {
            return 0;
        }
        if (claim->policy_id == 0u || claim->event_id == 0u) {
            return 0;
        }
    }
    return 1;
}

static int risk_run_validate(const risk_fixture* fixture)
{
    int ok = risk_validate_fixture(fixture);
    printf("%s\n", RISK_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("type_count=%u\n", (unsigned int)fixture->risk_desc.type_count);
    printf("field_count=%u\n", (unsigned int)fixture->risk_desc.field_count);
    printf("exposure_count=%u\n", (unsigned int)fixture->risk_desc.exposure_count);
    printf("profile_count=%u\n", (unsigned int)fixture->risk_desc.profile_count);
    printf("event_count=%u\n", (unsigned int)fixture->risk_desc.event_count);
    printf("policy_count=%u\n", (unsigned int)fixture->risk_desc.policy_count);
    printf("claim_count=%u\n", (unsigned int)fixture->risk_desc.claim_count);
    printf("ok=%u\n", (unsigned int)(ok ? 1u : 0u));
    return ok ? 0 : 1;
}

static int risk_run_inspect_type(const risk_fixture* fixture,
                                 const char* type_name,
                                 u32 budget_max)
{
    dom_risk_domain domain;
    dom_domain_budget budget;
    dom_risk_type_sample sample;
    u32 type_id;
    if (!type_name) {
        return 1;
    }
    type_id = d_rng_hash_str32(type_name);
    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_risk_type_query(&domain, type_id, &budget, &sample);

    printf("%s\n", RISK_INSPECT_HEADER);
    printf("entity=type\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("type_id=%u\n", (unsigned int)sample.type_id);
    printf("type_id_str=%s\n", risk_lookup_type_name(fixture, sample.type_id));
    printf("risk_class=%u\n", (unsigned int)sample.risk_class);
    printf("default_exposure_rate_q16=%d\n", (int)sample.default_exposure_rate);
    printf("default_impact_mean_q48=%lld\n", (long long)sample.default_impact_mean);
    printf("default_impact_spread_q16=%d\n", (int)sample.default_impact_spread);
    printf("default_uncertainty_q16=%d\n", (int)sample.default_uncertainty);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_risk_domain_free(&domain);
    return 0;
}

static int risk_run_inspect_field(const risk_fixture* fixture,
                                  const char* field_name,
                                  u32 budget_max)
{
    dom_risk_domain domain;
    dom_domain_budget budget;
    dom_risk_field_sample sample;
    u32 field_id;
    if (!field_name) {
        return 1;
    }
    field_id = d_rng_hash_str32(field_name);
    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_risk_field_query(&domain, field_id, &budget, &sample);

    printf("%s\n", RISK_INSPECT_HEADER);
    printf("entity=field\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("risk_id=%u\n", (unsigned int)sample.risk_id);
    printf("risk_id_str=%s\n", risk_lookup_field_name(fixture, sample.risk_id));
    printf("risk_type_id=%u\n", (unsigned int)sample.risk_type_id);
    printf("risk_type_id_str=%s\n", risk_lookup_type_name(fixture, sample.risk_type_id));
    printf("exposure_rate_q16=%d\n", (int)sample.exposure_rate);
    printf("impact_mean_q48=%lld\n", (long long)sample.impact_mean);
    printf("impact_spread_q16=%d\n", (int)sample.impact_spread);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
    printf("hazard_ref_id=%u\n", (unsigned int)sample.hazard_ref_id);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("radius_q16=%d\n", (int)sample.radius);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_risk_domain_free(&domain);
    return 0;
}

static int risk_run_inspect_exposure(const risk_fixture* fixture,
                                     const char* exposure_name,
                                     u32 budget_max)
{
    dom_risk_domain domain;
    dom_domain_budget budget;
    dom_risk_exposure_sample sample;
    u32 exposure_id;
    if (!exposure_name) {
        return 1;
    }
    exposure_id = d_rng_hash_str32(exposure_name);
    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_risk_exposure_query(&domain, exposure_id, &budget, &sample);

    printf("%s\n", RISK_INSPECT_HEADER);
    printf("entity=exposure\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("exposure_id=%u\n", (unsigned int)sample.exposure_id);
    printf("exposure_id_str=%s\n", risk_lookup_exposure_name(fixture, sample.exposure_id));
    printf("risk_type_id=%u\n", (unsigned int)sample.risk_type_id);
    printf("risk_type_id_str=%s\n", risk_lookup_type_name(fixture, sample.risk_type_id));
    printf("exposure_rate_q16=%d\n", (int)sample.exposure_rate);
    printf("exposure_limit_q48=%lld\n", (long long)sample.exposure_limit);
    printf("exposure_accumulated_q48=%lld\n", (long long)sample.exposure_accumulated);
    printf("sensitivity_q16=%d\n", (int)sample.sensitivity);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
    printf("subject_ref_id=%u\n", (unsigned int)sample.subject_ref_id);
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

    dom_risk_domain_free(&domain);
    return 0;
}

static int risk_run_inspect_profile(const risk_fixture* fixture,
                                    const char* profile_name,
                                    u32 budget_max)
{
    dom_risk_domain domain;
    dom_domain_budget budget;
    dom_risk_profile_sample sample;
    u32 profile_id;
    if (!profile_name) {
        return 1;
    }
    profile_id = d_rng_hash_str32(profile_name);
    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_risk_profile_query(&domain, profile_id, &budget, &sample);

    printf("%s\n", RISK_INSPECT_HEADER);
    printf("entity=profile\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("profile_id=%u\n", (unsigned int)sample.profile_id);
    printf("profile_id_str=%s\n", risk_lookup_profile_name(fixture, sample.profile_id));
    printf("subject_ref_id=%u\n", (unsigned int)sample.subject_ref_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("exposure_total_q48=%lld\n", (long long)sample.exposure_total);
    printf("impact_mean_q48=%lld\n", (long long)sample.impact_mean);
    printf("impact_spread_q16=%d\n", (int)sample.impact_spread);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_risk_domain_free(&domain);
    return 0;
}

static int risk_run_inspect_event(const risk_fixture* fixture,
                                  const char* event_name,
                                  u32 budget_max)
{
    dom_risk_domain domain;
    dom_domain_budget budget;
    dom_liability_event_sample sample;
    u32 event_id;
    if (!event_name) {
        return 1;
    }
    event_id = d_rng_hash_str32(event_name);
    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_liability_event_query(&domain, event_id, &budget, &sample);

    printf("%s\n", RISK_INSPECT_HEADER);
    printf("entity=event\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("event_id=%u\n", (unsigned int)sample.event_id);
    printf("event_id_str=%s\n", risk_lookup_event_name(fixture, sample.event_id));
    printf("risk_type_id=%u\n", (unsigned int)sample.risk_type_id);
    printf("risk_type_id_str=%s\n", risk_lookup_type_name(fixture, sample.risk_type_id));
    printf("hazard_ref_id=%u\n", (unsigned int)sample.hazard_ref_id);
    printf("exposure_ref_id=%u\n", (unsigned int)sample.exposure_ref_id);
    printf("loss_amount_q48=%lld\n", (long long)sample.loss_amount);
    printf("event_tick=%llu\n", (unsigned long long)sample.event_tick);
    printf("subject_ref_id=%u\n", (unsigned int)sample.subject_ref_id);
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

    dom_risk_domain_free(&domain);
    return 0;
}

static int risk_run_inspect_attribution(const risk_fixture* fixture,
                                        const char* attribution_name,
                                        u32 budget_max)
{
    dom_risk_domain domain;
    dom_domain_budget budget;
    dom_liability_attribution_sample sample;
    u32 attribution_id;
    if (!attribution_name) {
        return 1;
    }
    attribution_id = d_rng_hash_str32(attribution_name);
    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_liability_attribution_query(&domain, attribution_id, &budget, &sample);

    printf("%s\n", RISK_INSPECT_HEADER);
    printf("entity=attribution\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("attribution_id=%u\n", (unsigned int)sample.attribution_id);
    printf("attribution_id_str=%s\n", risk_lookup_attribution_name(fixture, sample.attribution_id));
    printf("event_id=%u\n", (unsigned int)sample.event_id);
    printf("responsible_ref_id=%u\n", (unsigned int)sample.responsible_ref_id);
    printf("role_tag=%u\n", (unsigned int)sample.role_tag);
    printf("compliance_tag=%u\n", (unsigned int)sample.compliance_tag);
    printf("negligence_score_q16=%d\n", (int)sample.negligence_score);
    printf("share_ratio_q16=%d\n", (int)sample.share_ratio);
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

    dom_risk_domain_free(&domain);
    return 0;
}

static int risk_run_inspect_policy(const risk_fixture* fixture,
                                   const char* policy_name,
                                   u32 budget_max)
{
    dom_risk_domain domain;
    dom_domain_budget budget;
    dom_insurance_policy_sample sample;
    u32 policy_id;
    if (!policy_name) {
        return 1;
    }
    policy_id = d_rng_hash_str32(policy_name);
    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_insurance_policy_query(&domain, policy_id, &budget, &sample);

    printf("%s\n", RISK_INSPECT_HEADER);
    printf("entity=policy\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("policy_id=%u\n", (unsigned int)sample.policy_id);
    printf("policy_id_str=%s\n", risk_lookup_policy_name(fixture, sample.policy_id));
    printf("holder_ref_id=%u\n", (unsigned int)sample.holder_ref_id);
    printf("risk_type_id=%u\n", (unsigned int)sample.risk_type_id);
    printf("risk_type_id_str=%s\n", risk_lookup_type_name(fixture, sample.risk_type_id));
    printf("coverage_ratio_q16=%d\n", (int)sample.coverage_ratio);
    printf("premium_q48=%lld\n", (long long)sample.premium);
    printf("payout_limit_q48=%lld\n", (long long)sample.payout_limit);
    printf("deductible_q48=%lld\n", (long long)sample.deductible);
    printf("audit_tag=%u\n", (unsigned int)sample.audit_tag);
    printf("audit_score_q16=%d\n", (int)sample.audit_score);
    printf("start_tick=%llu\n", (unsigned long long)sample.start_tick);
    printf("end_tick=%llu\n", (unsigned long long)sample.end_tick);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_risk_domain_free(&domain);
    return 0;
}

static int risk_run_inspect_claim(const risk_fixture* fixture,
                                  const char* claim_name,
                                  u32 budget_max)
{
    dom_risk_domain domain;
    dom_domain_budget budget;
    dom_insurance_claim_sample sample;
    u32 claim_id;
    if (!claim_name) {
        return 1;
    }
    claim_id = d_rng_hash_str32(claim_name);
    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_insurance_claim_query(&domain, claim_id, &budget, &sample);

    printf("%s\n", RISK_INSPECT_HEADER);
    printf("entity=claim\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("claim_id=%u\n", (unsigned int)sample.claim_id);
    printf("claim_id_str=%s\n", risk_lookup_claim_name(fixture, sample.claim_id));
    printf("policy_id=%u\n", (unsigned int)sample.policy_id);
    printf("policy_id_str=%s\n", risk_lookup_policy_name(fixture, sample.policy_id));
    printf("event_id=%u\n", (unsigned int)sample.event_id);
    printf("event_id_str=%s\n", risk_lookup_event_name(fixture, sample.event_id));
    printf("claim_amount_q48=%lld\n", (long long)sample.claim_amount);
    printf("approved_amount_q48=%lld\n", (long long)sample.approved_amount);
    printf("status_tag=%u\n", (unsigned int)sample.status_tag);
    printf("filed_tick=%llu\n", (unsigned long long)sample.filed_tick);
    printf("resolved_tick=%llu\n", (unsigned long long)sample.resolved_tick);
    printf("audit_ref_id=%u\n", (unsigned int)sample.audit_ref_id);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_risk_domain_free(&domain);
    return 0;
}

static int risk_run_inspect_region(const risk_fixture* fixture,
                                   const char* region_name,
                                   u32 budget_max)
{
    dom_risk_domain domain;
    dom_domain_budget budget;
    dom_risk_region_sample sample;
    u32 region_id = risk_find_region_id(fixture, region_name);

    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_risk_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", RISK_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("field_count=%u\n", (unsigned int)sample.field_count);
    printf("exposure_count=%u\n", (unsigned int)sample.exposure_count);
    printf("profile_count=%u\n", (unsigned int)sample.profile_count);
    printf("exposure_total_q48=%lld\n", (long long)sample.exposure_total);
    printf("impact_mean_total_q48=%lld\n", (long long)sample.impact_mean_total);
    printf("impact_spread_avg_q16=%d\n", (int)sample.impact_spread_avg);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_risk_domain_free(&domain);
    return 0;
}

static int risk_run_resolve(const risk_fixture* fixture,
                            const char* region_name,
                            u64 tick,
                            u64 tick_delta,
                            u32 budget_max,
                            u32 inactive_count)
{
    dom_risk_domain domain;
    dom_risk_domain* inactive = 0;
    dom_domain_budget budget;
    dom_risk_resolve_result result;
    u32 region_id = risk_find_region_id(fixture, region_name);
    u64 hash = 14695981039346656037ULL;

    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_risk_domain*)malloc(sizeof(dom_risk_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                risk_fixture temp = *fixture;
                temp.risk_desc.domain_id = fixture->risk_desc.domain_id + (u64)(i + 1u);
                dom_risk_domain_init(&inactive[i], &temp.risk_desc);
                dom_risk_domain_set_state(&inactive[i],
                                          DOM_DOMAIN_EXISTENCE_DECLARED,
                                          DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_risk_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.exposure_count; ++i) {
        hash = risk_hash_u32(hash, domain.exposures[i].exposure_id);
        hash = risk_hash_q48(hash, domain.exposures[i].exposure_accumulated);
    }
    for (u32 i = 0u; i < domain.profile_count; ++i) {
        hash = risk_hash_u32(hash, domain.profiles[i].profile_id);
        hash = risk_hash_q48(hash, domain.profiles[i].impact_mean);
    }
    for (u32 i = 0u; i < domain.claim_count; ++i) {
        hash = risk_hash_u32(hash, domain.claims[i].claim_id);
        hash = risk_hash_q48(hash, domain.claims[i].approved_amount);
        hash = risk_hash_u32(hash, domain.claims[i].flags);
    }

    printf("%s\n", RISK_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("field_count=%u\n", (unsigned int)result.field_count);
    printf("exposure_count=%u\n", (unsigned int)result.exposure_count);
    printf("exposure_over_limit_count=%u\n", (unsigned int)result.exposure_over_limit_count);
    printf("profile_count=%u\n", (unsigned int)result.profile_count);
    printf("claim_count=%u\n", (unsigned int)result.claim_count);
    printf("claim_approved_count=%u\n", (unsigned int)result.claim_approved_count);
    printf("claim_denied_count=%u\n", (unsigned int)result.claim_denied_count);
    printf("exposure_total_q48=%lld\n", (long long)result.exposure_total);
    printf("impact_mean_total_q48=%lld\n", (long long)result.impact_mean_total);
    printf("claim_paid_total_q48=%lld\n", (long long)result.claim_paid_total);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_risk_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_risk_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int risk_run_collapse(const risk_fixture* fixture, const char* region_name)
{
    dom_risk_domain domain;
    u32 region_id = risk_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_risk_domain_init(&domain, &fixture->risk_desc);
    if (fixture->policy_set) {
        dom_risk_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_risk_domain_capsule_count(&domain);
    (void)dom_risk_domain_collapse_region(&domain, region_id);
    count_after = dom_risk_domain_capsule_count(&domain);

    printf("%s\n", RISK_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", RISK_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_risk_domain_free(&domain);
    return 0;
}

static void risk_usage(void)
{
    printf("dom_tool_risk commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --type <id> [--budget N]\n");
    printf("  inspect --fixture <path> --field <id> [--budget N]\n");
    printf("  inspect --fixture <path> --exposure <id> [--budget N]\n");
    printf("  inspect --fixture <path> --profile <id> [--budget N]\n");
    printf("  inspect --fixture <path> --event <id> [--budget N]\n");
    printf("  inspect --fixture <path> --attribution <id> [--budget N]\n");
    printf("  inspect --fixture <path> --policy <id> [--budget N]\n");
    printf("  inspect --fixture <path> --claim <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        risk_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = risk_find_arg(argc, argv, "--fixture");
        risk_fixture fixture;
        if (!fixture_path || !risk_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "risk: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return risk_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* type_name = risk_find_arg(argc, argv, "--type");
            const char* field_name = risk_find_arg(argc, argv, "--field");
            const char* exposure_name = risk_find_arg(argc, argv, "--exposure");
            const char* profile_name = risk_find_arg(argc, argv, "--profile");
            const char* event_name = risk_find_arg(argc, argv, "--event");
            const char* attribution_name = risk_find_arg(argc, argv, "--attribution");
            const char* policy_name = risk_find_arg(argc, argv, "--policy");
            const char* claim_name = risk_find_arg(argc, argv, "--claim");
            const char* region_name = risk_find_arg(argc, argv, "--region");
            u32 budget_max = risk_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (type_name) {
                return risk_run_inspect_type(&fixture, type_name, budget_max);
            }
            if (field_name) {
                return risk_run_inspect_field(&fixture, field_name, budget_max);
            }
            if (exposure_name) {
                return risk_run_inspect_exposure(&fixture, exposure_name, budget_max);
            }
            if (profile_name) {
                return risk_run_inspect_profile(&fixture, profile_name, budget_max);
            }
            if (event_name) {
                return risk_run_inspect_event(&fixture, event_name, budget_max);
            }
            if (attribution_name) {
                return risk_run_inspect_attribution(&fixture, attribution_name, budget_max);
            }
            if (policy_name) {
                return risk_run_inspect_policy(&fixture, policy_name, budget_max);
            }
            if (claim_name) {
                return risk_run_inspect_claim(&fixture, claim_name, budget_max);
            }
            if (region_name) {
                return risk_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr, "risk: inspect requires --type, --field, --exposure, --profile, --event, --attribution, --policy, --claim, or --region\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = risk_find_arg(argc, argv, "--region");
            u64 tick = risk_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = risk_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = risk_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = risk_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!region_name) {
                fprintf(stderr, "risk: resolve requires --region\n");
                return 2;
            }
            return risk_run_resolve(&fixture, region_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = risk_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "risk: collapse requires --region\n");
                return 2;
            }
            return risk_run_collapse(&fixture, region_name);
        }
    }

    risk_usage();
    return 2;
}
