/*
FILE: tools/institution/institution_cli.cpp
MODULE: Dominium
PURPOSE: Institution fixture CLI for governance and law field checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/rng_model.h"
#include "domino/world/institution_fields.h"

#define INSTITUTION_FIXTURE_HEADER "DOMINIUM_INSTITUTION_FIXTURE_V1"

#define INSTITUTION_VALIDATE_HEADER "DOMINIUM_INSTITUTION_VALIDATE_V1"
#define INSTITUTION_INSPECT_HEADER "DOMINIUM_INSTITUTION_INSPECT_V1"
#define INSTITUTION_RESOLVE_HEADER "DOMINIUM_INSTITUTION_RESOLVE_V1"
#define INSTITUTION_COLLAPSE_HEADER "DOMINIUM_INSTITUTION_COLLAPSE_V1"

#define INSTITUTION_PROVIDER_CHAIN "entities->scopes->capabilities->rules->enforcement"

#define INSTITUTION_LINE_MAX 512u

typedef struct institution_fixture {
    char fixture_id[96];
    dom_institution_surface_desc institution_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char entity_names[DOM_INSTITUTION_MAX_ENTITIES][64];
    char scope_names[DOM_INSTITUTION_MAX_SCOPES][64];
    char capability_names[DOM_INSTITUTION_MAX_CAPABILITIES][64];
    char rule_names[DOM_INSTITUTION_MAX_RULES][64];
    char enforcement_names[DOM_INSTITUTION_MAX_ENFORCEMENTS][64];
    char region_names[DOM_INSTITUTION_MAX_REGIONS][64];
    u32 region_ids[DOM_INSTITUTION_MAX_REGIONS];
    u32 region_count;
} institution_fixture;

static u64 institution_hash_u64(u64 h, u64 v)
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

static u64 institution_hash_u32(u64 h, u32 v)
{
    return institution_hash_u64(h, (u64)v);
}

static u64 institution_hash_q16(u64 h, q16_16 v)
{
    return institution_hash_u64(h, (u64)(u32)v);
}

static u64 institution_hash_q48(u64 h, q48_16 v)
{
    return institution_hash_u64(h, (u64)v);
}

static char* institution_trim(char* text)
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

static int institution_parse_u32(const char* text, u32* out_value)
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

static int institution_parse_u64(const char* text, u64* out_value)
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

static int institution_parse_q16(const char* text, q16_16* out_value)
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

static int institution_parse_q48(const char* text, q48_16* out_value)
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

static int institution_parse_indexed_key(const char* key,
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

static u32 institution_rule_action_from_text(const char* text)
{
    if (!text) {
        return DOM_INSTITUTION_RULE_UNSET;
    }
    if (strcmp(text, "allow") == 0) return DOM_INSTITUTION_RULE_ALLOW;
    if (strcmp(text, "forbid") == 0) return DOM_INSTITUTION_RULE_FORBID;
    if (strcmp(text, "conditional") == 0) return DOM_INSTITUTION_RULE_CONDITIONAL;
    if (strcmp(text, "license") == 0) return DOM_INSTITUTION_RULE_LICENSE;
    return DOM_INSTITUTION_RULE_UNSET;
}

static u32 institution_enforcement_action_from_text(const char* text)
{
    if (!text) {
        return DOM_INSTITUTION_ENFORCE_UNSET;
    }
    if (strcmp(text, "permit") == 0) return DOM_INSTITUTION_ENFORCE_PERMIT;
    if (strcmp(text, "deny") == 0) return DOM_INSTITUTION_ENFORCE_DENY;
    if (strcmp(text, "penalize") == 0) return DOM_INSTITUTION_ENFORCE_PENALIZE;
    if (strcmp(text, "license") == 0) return DOM_INSTITUTION_ENFORCE_LICENSE;
    return DOM_INSTITUTION_ENFORCE_UNSET;
}

static void institution_fixture_init(institution_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_institution_surface_desc_init(&fixture->institution_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "institution.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void institution_fixture_register_region(institution_fixture* fixture,
                                                const char* name,
                                                u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_INSTITUTION_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int institution_fixture_apply_entity(institution_fixture* fixture,
                                            u32 index,
                                            const char* suffix,
                                            const char* value)
{
    dom_institution_entity_desc* entity;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_INSTITUTION_MAX_ENTITIES) {
        return 0;
    }
    if (fixture->institution_desc.entity_count <= index) {
        fixture->institution_desc.entity_count = index + 1u;
    }
    entity = &fixture->institution_desc.entities[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->entity_names[index], value, sizeof(fixture->entity_names[index]) - 1);
        fixture->entity_names[index][sizeof(fixture->entity_names[index]) - 1] = '\0';
        entity->institution_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "scope") == 0) {
        entity->scope_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "authority_count") == 0) {
        return institution_parse_u32(value, &entity->authority_count);
    }
    if (strncmp(suffix, "authority_", 10) == 0) {
        u32 auth_index = 0u;
        if (institution_parse_u32(suffix + 10, &auth_index) &&
            auth_index < DOM_INSTITUTION_MAX_AUTHORITY_TYPES) {
            entity->authority_types[auth_index] = d_rng_hash_str32(value);
            if (entity->authority_count <= auth_index) {
                entity->authority_count = auth_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "enforcement_capacity") == 0) {
        return institution_parse_q48(value, &entity->enforcement_capacity);
    }
    if (strcmp(suffix, "resource_budget") == 0) {
        return institution_parse_q48(value, &entity->resource_budget);
    }
    if (strcmp(suffix, "legitimacy") == 0) {
        return institution_parse_q16(value, &entity->legitimacy_level);
    }
    if (strcmp(suffix, "legitimacy_ref") == 0) {
        entity->legitimacy_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "knowledge_base") == 0 || strcmp(suffix, "knowledge") == 0) {
        entity->knowledge_base_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        entity->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        entity->region_id = region_id;
        institution_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int institution_fixture_apply_scope(institution_fixture* fixture,
                                           u32 index,
                                           const char* suffix,
                                           const char* value)
{
    dom_institution_scope_desc* scope;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_INSTITUTION_MAX_SCOPES) {
        return 0;
    }
    if (fixture->institution_desc.scope_count <= index) {
        fixture->institution_desc.scope_count = index + 1u;
    }
    scope = &fixture->institution_desc.scopes[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->scope_names[index], value, sizeof(fixture->scope_names[index]) - 1);
        fixture->scope_names[index][sizeof(fixture->scope_names[index]) - 1] = '\0';
        scope->scope_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "spatial") == 0) {
        scope->spatial_domain_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "subject_count") == 0) {
        return institution_parse_u32(value, &scope->subject_domain_count);
    }
    if (strncmp(suffix, "subject_", 8) == 0) {
        u32 subject_index = 0u;
        if (institution_parse_u32(suffix + 8, &subject_index) &&
            subject_index < DOM_INSTITUTION_MAX_SUBJECT_DOMAINS) {
            scope->subject_domain_ids[subject_index] = d_rng_hash_str32(value);
            if (scope->subject_domain_count <= subject_index) {
                scope->subject_domain_count = subject_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "overlap") == 0) {
        scope->overlap_policy_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        scope->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        scope->region_id = region_id;
        institution_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int institution_fixture_apply_capability(institution_fixture* fixture,
                                                u32 index,
                                                const char* suffix,
                                                const char* value)
{
    dom_institution_capability_desc* cap;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_INSTITUTION_MAX_CAPABILITIES) {
        return 0;
    }
    if (fixture->institution_desc.capability_count <= index) {
        fixture->institution_desc.capability_count = index + 1u;
    }
    cap = &fixture->institution_desc.capabilities[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->capability_names[index], value,
                sizeof(fixture->capability_names[index]) - 1);
        fixture->capability_names[index][sizeof(fixture->capability_names[index]) - 1] = '\0';
        cap->capability_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "institution") == 0) {
        cap->institution_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "scope") == 0) {
        cap->scope_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "authority") == 0) {
        cap->authority_type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "process") == 0) {
        cap->process_family_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "capacity") == 0) {
        return institution_parse_q48(value, &cap->capacity_limit);
    }
    if (strcmp(suffix, "license") == 0) {
        cap->license_required_id = d_rng_hash_str32(value);
        if (cap->license_required_id != 0u) {
            cap->flags |= DOM_INSTITUTION_CAPABILITY_LICENSE_REQUIRED;
        }
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        cap->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        cap->region_id = region_id;
        institution_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return institution_parse_u32(value, &cap->flags);
    }
    return 0;
}

static int institution_fixture_apply_rule(institution_fixture* fixture,
                                          u32 index,
                                          const char* suffix,
                                          const char* value)
{
    dom_institution_rule_desc* rule;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_INSTITUTION_MAX_RULES) {
        return 0;
    }
    if (fixture->institution_desc.rule_count <= index) {
        fixture->institution_desc.rule_count = index + 1u;
    }
    rule = &fixture->institution_desc.rules[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->rule_names[index], value, sizeof(fixture->rule_names[index]) - 1);
        fixture->rule_names[index][sizeof(fixture->rule_names[index]) - 1] = '\0';
        rule->rule_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "institution") == 0) {
        rule->institution_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "scope") == 0) {
        rule->scope_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "process") == 0) {
        rule->process_family_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "subject") == 0) {
        rule->subject_domain_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "authority") == 0) {
        rule->authority_type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "action") == 0) {
        rule->action = institution_rule_action_from_text(value);
        if (rule->action == DOM_INSTITUTION_RULE_CONDITIONAL) {
            rule->flags |= DOM_INSTITUTION_RULE_FLAG_CONDITIONAL;
        }
        if (rule->action == DOM_INSTITUTION_RULE_LICENSE) {
            rule->flags |= DOM_INSTITUTION_RULE_FLAG_LICENSE_REQUIRED;
        }
        return 1;
    }
    if (strcmp(suffix, "license") == 0) {
        rule->license_required_id = d_rng_hash_str32(value);
        if (rule->license_required_id != 0u) {
            rule->flags |= DOM_INSTITUTION_RULE_FLAG_LICENSE_REQUIRED;
        }
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        rule->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        rule->region_id = region_id;
        institution_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return institution_parse_u32(value, &rule->flags);
    }
    return 0;
}

static int institution_fixture_apply_enforcement(institution_fixture* fixture,
                                                 u32 index,
                                                 const char* suffix,
                                                 const char* value)
{
    dom_institution_enforcement_desc* enforcement;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_INSTITUTION_MAX_ENFORCEMENTS) {
        return 0;
    }
    if (fixture->institution_desc.enforcement_count <= index) {
        fixture->institution_desc.enforcement_count = index + 1u;
    }
    enforcement = &fixture->institution_desc.enforcement[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->enforcement_names[index], value,
                sizeof(fixture->enforcement_names[index]) - 1);
        fixture->enforcement_names[index][sizeof(fixture->enforcement_names[index]) - 1] = '\0';
        enforcement->enforcement_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "institution") == 0) {
        enforcement->institution_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "rule") == 0) {
        enforcement->rule_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "process") == 0) {
        enforcement->process_family_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "agent") == 0) {
        enforcement->agent_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "action") == 0) {
        enforcement->action = institution_enforcement_action_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "tick") == 0) {
        return institution_parse_u64(value, &enforcement->event_tick);
    }
    if (strcmp(suffix, "provenance") == 0) {
        enforcement->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        enforcement->region_id = region_id;
        institution_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "flags") == 0) {
        return institution_parse_u32(value, &enforcement->flags);
    }
    return 0;
}

static int institution_fixture_apply(institution_fixture* fixture,
                                     const char* key,
                                     const char* value)
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
        return institution_parse_u64(value, &fixture->institution_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return institution_parse_u64(value, &fixture->institution_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return institution_parse_q16(value, &fixture->institution_desc.meters_per_unit);
    }
    if (strcmp(key, "entity_count") == 0) {
        return institution_parse_u32(value, &fixture->institution_desc.entity_count);
    }
    if (strcmp(key, "scope_count") == 0) {
        return institution_parse_u32(value, &fixture->institution_desc.scope_count);
    }
    if (strcmp(key, "capability_count") == 0) {
        return institution_parse_u32(value, &fixture->institution_desc.capability_count);
    }
    if (strcmp(key, "rule_count") == 0) {
        return institution_parse_u32(value, &fixture->institution_desc.rule_count);
    }
    if (strcmp(key, "enforcement_count") == 0) {
        return institution_parse_u32(value, &fixture->institution_desc.enforcement_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return institution_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return institution_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return institution_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return institution_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (institution_parse_indexed_key(key, "entity_", &index, &suffix)) {
        return institution_fixture_apply_entity(fixture, index, suffix, value);
    }
    if (institution_parse_indexed_key(key, "scope_", &index, &suffix)) {
        return institution_fixture_apply_scope(fixture, index, suffix, value);
    }
    if (institution_parse_indexed_key(key, "capability_", &index, &suffix)) {
        return institution_fixture_apply_capability(fixture, index, suffix, value);
    }
    if (institution_parse_indexed_key(key, "rule_", &index, &suffix)) {
        return institution_fixture_apply_rule(fixture, index, suffix, value);
    }
    if (institution_parse_indexed_key(key, "enforcement_", &index, &suffix)) {
        return institution_fixture_apply_enforcement(fixture, index, suffix, value);
    }
    return 0;
}

static int institution_fixture_load(const char* path, institution_fixture* out_fixture)
{
    FILE* file;
    char line[INSTITUTION_LINE_MAX];
    int header_ok = 0;
    institution_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    institution_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = institution_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, INSTITUTION_FIXTURE_HEADER) != 0) {
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
        institution_fixture_apply(&fixture, institution_trim(text), institution_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* institution_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 institution_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = institution_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && institution_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 institution_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = institution_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && institution_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 institution_find_region_id(const institution_fixture* fixture, const char* name)
{
    if (!fixture || !name) {
        return 0u;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (strcmp(fixture->region_names[i], name) == 0) {
            return fixture->region_ids[i];
        }
    }
    return d_rng_hash_str32(name);
}

static const char* institution_lookup_entity_name(const institution_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "institution.entity.unknown";
    }
    for (u32 i = 0u; i < DOM_INSTITUTION_MAX_ENTITIES; ++i) {
        if (!fixture->entity_names[i][0]) {
            continue;
        }
        if (d_rng_hash_str32(fixture->entity_names[i]) == id) {
            return fixture->entity_names[i];
        }
    }
    return "institution.entity.unknown";
}

static const char* institution_lookup_scope_name(const institution_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "institution.scope.unknown";
    }
    for (u32 i = 0u; i < DOM_INSTITUTION_MAX_SCOPES; ++i) {
        if (!fixture->scope_names[i][0]) {
            continue;
        }
        if (d_rng_hash_str32(fixture->scope_names[i]) == id) {
            return fixture->scope_names[i];
        }
    }
    return "institution.scope.unknown";
}

static const char* institution_lookup_capability_name(const institution_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "institution.capability.unknown";
    }
    for (u32 i = 0u; i < DOM_INSTITUTION_MAX_CAPABILITIES; ++i) {
        if (!fixture->capability_names[i][0]) {
            continue;
        }
        if (d_rng_hash_str32(fixture->capability_names[i]) == id) {
            return fixture->capability_names[i];
        }
    }
    return "institution.capability.unknown";
}

static const char* institution_lookup_rule_name(const institution_fixture* fixture, u32 id)
{
    if (!fixture || id == 0u) {
        return "institution.rule.unknown";
    }
    for (u32 i = 0u; i < DOM_INSTITUTION_MAX_RULES; ++i) {
        if (!fixture->rule_names[i][0]) {
            continue;
        }
        if (d_rng_hash_str32(fixture->rule_names[i]) == id) {
            return fixture->rule_names[i];
        }
    }
    return "institution.rule.unknown";
}

static const char* institution_lookup_enforcement_name(const institution_fixture* fixture,
                                                       u32 id)
{
    if (!fixture || id == 0u) {
        return "institution.enforcement.unknown";
    }
    for (u32 i = 0u; i < DOM_INSTITUTION_MAX_ENFORCEMENTS; ++i) {
        if (!fixture->enforcement_names[i][0]) {
            continue;
        }
        if (d_rng_hash_str32(fixture->enforcement_names[i]) == id) {
            return fixture->enforcement_names[i];
        }
    }
    return "institution.enforcement.unknown";
}

static int institution_run_validate(const institution_fixture* fixture)
{
    if (!fixture) {
        return 1;
    }
    printf("%s\n", INSTITUTION_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", INSTITUTION_PROVIDER_CHAIN);
    printf("entity_count=%u\n", (unsigned int)fixture->institution_desc.entity_count);
    printf("scope_count=%u\n", (unsigned int)fixture->institution_desc.scope_count);
    printf("capability_count=%u\n", (unsigned int)fixture->institution_desc.capability_count);
    printf("rule_count=%u\n", (unsigned int)fixture->institution_desc.rule_count);
    printf("enforcement_count=%u\n", (unsigned int)fixture->institution_desc.enforcement_count);
    printf("region_count=%u\n", (unsigned int)fixture->region_count);
    return 0;
}

static int institution_run_inspect_entity(const institution_fixture* fixture,
                                          const char* name,
                                          u32 budget_max)
{
    dom_institution_domain domain;
    dom_domain_budget budget;
    dom_institution_entity_sample sample;
    u32 entity_id;
    if (!name) {
        return 1;
    }
    entity_id = d_rng_hash_str32(name);
    dom_institution_domain_init(&domain, &fixture->institution_desc);
    if (fixture->policy_set) {
        dom_institution_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_institution_entity_query(&domain, entity_id, &budget, &sample);

    printf("%s\n", INSTITUTION_INSPECT_HEADER);
    printf("entity=entity\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", INSTITUTION_PROVIDER_CHAIN);
    printf("institution_id=%u\n", (unsigned int)sample.institution_id);
    printf("institution_id_str=%s\n", institution_lookup_entity_name(fixture, sample.institution_id));
    printf("scope_id=%u\n", (unsigned int)sample.scope_id);
    printf("authority_count=%u\n", (unsigned int)sample.authority_count);
    printf("enforcement_capacity_q48=%lld\n", (long long)sample.enforcement_capacity);
    printf("resource_budget_q48=%lld\n", (long long)sample.resource_budget);
    printf("legitimacy_level_q16=%d\n", (int)sample.legitimacy_level);
    printf("legitimacy_ref_id=%u\n", (unsigned int)sample.legitimacy_ref_id);
    printf("knowledge_base_id=%u\n", (unsigned int)sample.knowledge_base_id);
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

    dom_institution_domain_free(&domain);
    return 0;
}

static int institution_run_inspect_scope(const institution_fixture* fixture,
                                         const char* name,
                                         u32 budget_max)
{
    dom_institution_domain domain;
    dom_domain_budget budget;
    dom_institution_scope_sample sample;
    u32 scope_id;
    if (!name) {
        return 1;
    }
    scope_id = d_rng_hash_str32(name);
    dom_institution_domain_init(&domain, &fixture->institution_desc);
    if (fixture->policy_set) {
        dom_institution_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_institution_scope_query(&domain, scope_id, &budget, &sample);

    printf("%s\n", INSTITUTION_INSPECT_HEADER);
    printf("entity=scope\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", INSTITUTION_PROVIDER_CHAIN);
    printf("scope_id=%u\n", (unsigned int)sample.scope_id);
    printf("scope_id_str=%s\n", institution_lookup_scope_name(fixture, sample.scope_id));
    printf("spatial_domain_id=%u\n", (unsigned int)sample.spatial_domain_id);
    printf("subject_domain_count=%u\n", (unsigned int)sample.subject_domain_count);
    printf("overlap_policy_id=%u\n", (unsigned int)sample.overlap_policy_id);
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

    dom_institution_domain_free(&domain);
    return 0;
}

static int institution_run_inspect_capability(const institution_fixture* fixture,
                                              const char* name,
                                              u32 budget_max)
{
    dom_institution_domain domain;
    dom_domain_budget budget;
    dom_institution_capability_sample sample;
    u32 capability_id;
    if (!name) {
        return 1;
    }
    capability_id = d_rng_hash_str32(name);
    dom_institution_domain_init(&domain, &fixture->institution_desc);
    if (fixture->policy_set) {
        dom_institution_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_institution_capability_query(&domain, capability_id, &budget, &sample);

    printf("%s\n", INSTITUTION_INSPECT_HEADER);
    printf("entity=capability\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", INSTITUTION_PROVIDER_CHAIN);
    printf("capability_id=%u\n", (unsigned int)sample.capability_id);
    printf("capability_id_str=%s\n", institution_lookup_capability_name(fixture, sample.capability_id));
    printf("institution_id=%u\n", (unsigned int)sample.institution_id);
    printf("scope_id=%u\n", (unsigned int)sample.scope_id);
    printf("authority_type_id=%u\n", (unsigned int)sample.authority_type_id);
    printf("process_family_id=%u\n", (unsigned int)sample.process_family_id);
    printf("capacity_limit_q48=%lld\n", (long long)sample.capacity_limit);
    printf("license_required_id=%u\n", (unsigned int)sample.license_required_id);
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

    dom_institution_domain_free(&domain);
    return 0;
}

static int institution_run_inspect_rule(const institution_fixture* fixture,
                                        const char* name,
                                        u32 budget_max)
{
    dom_institution_domain domain;
    dom_domain_budget budget;
    dom_institution_rule_sample sample;
    u32 rule_id;
    if (!name) {
        return 1;
    }
    rule_id = d_rng_hash_str32(name);
    dom_institution_domain_init(&domain, &fixture->institution_desc);
    if (fixture->policy_set) {
        dom_institution_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_institution_rule_query(&domain, rule_id, &budget, &sample);

    printf("%s\n", INSTITUTION_INSPECT_HEADER);
    printf("entity=rule\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", INSTITUTION_PROVIDER_CHAIN);
    printf("rule_id=%u\n", (unsigned int)sample.rule_id);
    printf("rule_id_str=%s\n", institution_lookup_rule_name(fixture, sample.rule_id));
    printf("institution_id=%u\n", (unsigned int)sample.institution_id);
    printf("scope_id=%u\n", (unsigned int)sample.scope_id);
    printf("process_family_id=%u\n", (unsigned int)sample.process_family_id);
    printf("subject_domain_id=%u\n", (unsigned int)sample.subject_domain_id);
    printf("authority_type_id=%u\n", (unsigned int)sample.authority_type_id);
    printf("action=%u\n", (unsigned int)sample.action);
    printf("license_required_id=%u\n", (unsigned int)sample.license_required_id);
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

    dom_institution_domain_free(&domain);
    return 0;
}

static int institution_run_inspect_enforcement(const institution_fixture* fixture,
                                               const char* name,
                                               u32 budget_max)
{
    dom_institution_domain domain;
    dom_domain_budget budget;
    dom_institution_enforcement_sample sample;
    u32 enforcement_id;
    if (!name) {
        return 1;
    }
    enforcement_id = d_rng_hash_str32(name);
    dom_institution_domain_init(&domain, &fixture->institution_desc);
    if (fixture->policy_set) {
        dom_institution_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_institution_enforcement_query(&domain, enforcement_id, &budget, &sample);

    printf("%s\n", INSTITUTION_INSPECT_HEADER);
    printf("entity=enforcement\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", INSTITUTION_PROVIDER_CHAIN);
    printf("enforcement_id=%u\n", (unsigned int)sample.enforcement_id);
    printf("enforcement_id_str=%s\n",
           institution_lookup_enforcement_name(fixture, sample.enforcement_id));
    printf("institution_id=%u\n", (unsigned int)sample.institution_id);
    printf("rule_id=%u\n", (unsigned int)sample.rule_id);
    printf("process_family_id=%u\n", (unsigned int)sample.process_family_id);
    printf("agent_id=%u\n", (unsigned int)sample.agent_id);
    printf("action=%u\n", (unsigned int)sample.action);
    printf("event_tick=%llu\n", (unsigned long long)sample.event_tick);
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

    dom_institution_domain_free(&domain);
    return 0;
}

static int institution_run_inspect_region(const institution_fixture* fixture,
                                          const char* region_name,
                                          u32 budget_max)
{
    dom_institution_domain domain;
    dom_domain_budget budget;
    dom_institution_region_sample sample;
    u32 region_id = institution_find_region_id(fixture, region_name);

    dom_institution_domain_init(&domain, &fixture->institution_desc);
    if (fixture->policy_set) {
        dom_institution_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_institution_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", INSTITUTION_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", INSTITUTION_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("entity_count=%u\n", (unsigned int)sample.entity_count);
    printf("scope_count=%u\n", (unsigned int)sample.scope_count);
    printf("capability_count=%u\n", (unsigned int)sample.capability_count);
    printf("rule_count=%u\n", (unsigned int)sample.rule_count);
    printf("enforcement_count=%u\n", (unsigned int)sample.enforcement_count);
    printf("enforcement_capacity_avg_q48=%lld\n", (long long)sample.enforcement_capacity_avg);
    printf("resource_budget_avg_q48=%lld\n", (long long)sample.resource_budget_avg);
    printf("legitimacy_avg_q16=%d\n", (int)sample.legitimacy_avg);
    printf("enforcement_permit_count=%u\n", (unsigned int)sample.enforcement_action_counts[0]);
    printf("enforcement_deny_count=%u\n", (unsigned int)sample.enforcement_action_counts[1]);
    printf("enforcement_penalize_count=%u\n", (unsigned int)sample.enforcement_action_counts[2]);
    printf("enforcement_license_count=%u\n", (unsigned int)sample.enforcement_action_counts[3]);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_institution_domain_free(&domain);
    return 0;
}

static int institution_run_resolve(const institution_fixture* fixture,
                                   const char* region_name,
                                   u64 tick,
                                   u64 tick_delta,
                                   u32 budget_max,
                                   u32 inactive_count)
{
    dom_institution_domain domain;
    dom_institution_domain* inactive = 0;
    dom_domain_budget budget;
    dom_institution_resolve_result result;
    u32 region_id = institution_find_region_id(fixture, region_name);
    u64 hash = 14695981039346656037ULL;

    dom_institution_domain_init(&domain, &fixture->institution_desc);
    if (fixture->policy_set) {
        dom_institution_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_institution_domain*)malloc(sizeof(dom_institution_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                institution_fixture temp = *fixture;
                temp.institution_desc.domain_id = fixture->institution_desc.domain_id + (u64)(i + 1u);
                dom_institution_domain_init(&inactive[i], &temp.institution_desc);
                dom_institution_domain_set_state(&inactive[i],
                                                 DOM_DOMAIN_EXISTENCE_DECLARED,
                                                 DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_institution_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.entity_count; ++i) {
        hash = institution_hash_u32(hash, domain.entities[i].institution_id);
        hash = institution_hash_q48(hash, domain.entities[i].enforcement_capacity);
        hash = institution_hash_q48(hash, domain.entities[i].resource_budget);
        hash = institution_hash_q16(hash, domain.entities[i].legitimacy_level);
    }
    for (u32 i = 0u; i < domain.scope_count; ++i) {
        hash = institution_hash_u32(hash, domain.scopes[i].scope_id);
        hash = institution_hash_u32(hash, domain.scopes[i].spatial_domain_id);
    }
    for (u32 i = 0u; i < domain.capability_count; ++i) {
        hash = institution_hash_u32(hash, domain.capabilities[i].capability_id);
        hash = institution_hash_q48(hash, domain.capabilities[i].capacity_limit);
        hash = institution_hash_u32(hash, domain.capabilities[i].flags);
    }
    for (u32 i = 0u; i < domain.rule_count; ++i) {
        hash = institution_hash_u32(hash, domain.rules[i].rule_id);
        hash = institution_hash_u32(hash, domain.rules[i].action);
        hash = institution_hash_u32(hash, domain.rules[i].flags);
    }
    for (u32 i = 0u; i < domain.enforcement_count; ++i) {
        hash = institution_hash_u32(hash, domain.enforcement[i].enforcement_id);
        hash = institution_hash_u32(hash, domain.enforcement[i].action);
        hash = institution_hash_u32(hash, domain.enforcement[i].flags);
    }

    printf("%s\n", INSTITUTION_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", INSTITUTION_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("entity_count=%u\n", (unsigned int)result.entity_count);
    printf("scope_count=%u\n", (unsigned int)result.scope_count);
    printf("capability_count=%u\n", (unsigned int)result.capability_count);
    printf("rule_count=%u\n", (unsigned int)result.rule_count);
    printf("enforcement_count=%u\n", (unsigned int)result.enforcement_count);
    printf("enforcement_applied_count=%u\n", (unsigned int)result.enforcement_applied_count);
    printf("enforcement_capacity_avg_q48=%lld\n", (long long)result.enforcement_capacity_avg);
    printf("resource_budget_avg_q48=%lld\n", (long long)result.resource_budget_avg);
    printf("legitimacy_avg_q16=%d\n", (int)result.legitimacy_avg);
    printf("enforcement_permit_count=%u\n", (unsigned int)result.enforcement_action_counts[0]);
    printf("enforcement_deny_count=%u\n", (unsigned int)result.enforcement_action_counts[1]);
    printf("enforcement_penalize_count=%u\n", (unsigned int)result.enforcement_action_counts[2]);
    printf("enforcement_license_count=%u\n", (unsigned int)result.enforcement_action_counts[3]);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_institution_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_institution_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int institution_run_collapse(const institution_fixture* fixture, const char* region_name)
{
    dom_institution_domain domain;
    u32 region_id = institution_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_institution_domain_init(&domain, &fixture->institution_desc);
    if (fixture->policy_set) {
        dom_institution_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_institution_domain_capsule_count(&domain);
    (void)dom_institution_domain_collapse_region(&domain, region_id);
    count_after = dom_institution_domain_capsule_count(&domain);

    printf("%s\n", INSTITUTION_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", INSTITUTION_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_institution_domain_free(&domain);
    return 0;
}

static void institution_usage(void)
{
    printf("dom_tool_institution commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --entity <id> [--budget N]\n");
    printf("  inspect --fixture <path> --scope <id> [--budget N]\n");
    printf("  inspect --fixture <path> --capability <id> [--budget N]\n");
    printf("  inspect --fixture <path> --rule <id> [--budget N]\n");
    printf("  inspect --fixture <path> --enforcement <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        institution_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = institution_find_arg(argc, argv, "--fixture");
        institution_fixture fixture;
        if (!fixture_path || !institution_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "institution: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return institution_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* entity_name = institution_find_arg(argc, argv, "--entity");
            const char* scope_name = institution_find_arg(argc, argv, "--scope");
            const char* capability_name = institution_find_arg(argc, argv, "--capability");
            const char* rule_name = institution_find_arg(argc, argv, "--rule");
            const char* enforcement_name = institution_find_arg(argc, argv, "--enforcement");
            const char* region_name = institution_find_arg(argc, argv, "--region");
            u32 budget_max = institution_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (entity_name) {
                return institution_run_inspect_entity(&fixture, entity_name, budget_max);
            }
            if (scope_name) {
                return institution_run_inspect_scope(&fixture, scope_name, budget_max);
            }
            if (capability_name) {
                return institution_run_inspect_capability(&fixture, capability_name, budget_max);
            }
            if (rule_name) {
                return institution_run_inspect_rule(&fixture, rule_name, budget_max);
            }
            if (enforcement_name) {
                return institution_run_inspect_enforcement(&fixture, enforcement_name, budget_max);
            }
            if (region_name) {
                return institution_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr,
                    "institution: inspect requires --entity, --scope, --capability, --rule, --enforcement, or --region\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = institution_find_arg(argc, argv, "--region");
            u64 tick = institution_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = institution_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = institution_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = institution_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!region_name) {
                fprintf(stderr, "institution: resolve requires --region\n");
                return 2;
            }
            return institution_run_resolve(&fixture, region_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = institution_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "institution: collapse requires --region\n");
                return 2;
            }
            return institution_run_collapse(&fixture, region_name);
        }
    }

    institution_usage();
    return 2;
}
