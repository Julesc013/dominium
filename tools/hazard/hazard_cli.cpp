/*
FILE: tools/hazard/hazard_cli.cpp
MODULE: Dominium
PURPOSE: Hazard fixture CLI for deterministic hazard propagation checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"
#include "domino/world/hazard_fields.h"

#define HAZARD_FIXTURE_HEADER "DOMINIUM_HAZARD_FIXTURE_V1"

#define HAZARD_VALIDATE_HEADER "DOMINIUM_HAZARD_VALIDATE_V1"
#define HAZARD_INSPECT_HEADER "DOMINIUM_HAZARD_INSPECT_V1"
#define HAZARD_RESOLVE_HEADER "DOMINIUM_HAZARD_RESOLVE_V1"
#define HAZARD_COLLAPSE_HEADER "DOMINIUM_HAZARD_COLLAPSE_V1"

#define HAZARD_PROVIDER_CHAIN "types->fields->exposures"

#define HAZARD_LINE_MAX 512u

typedef struct hazard_fixture {
    char fixture_id[96];
    dom_hazard_surface_desc hazard_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char type_names[DOM_HAZARD_MAX_TYPES][64];
    char field_names[DOM_HAZARD_MAX_FIELDS][64];
    char exposure_names[DOM_HAZARD_MAX_EXPOSURES][64];
    char region_names[DOM_HAZARD_MAX_REGIONS][64];
    u32 region_ids[DOM_HAZARD_MAX_REGIONS];
    u32 region_count;
} hazard_fixture;

static u64 hazard_hash_u64(u64 h, u64 v)
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

static u64 hazard_hash_u32(u64 h, u32 v)
{
    return hazard_hash_u64(h, (u64)v);
}

static u64 hazard_hash_q16(u64 h, q16_16 v)
{
    return hazard_hash_u64(h, (u64)(u32)v);
}

static u64 hazard_hash_q48(u64 h, q48_16 v)
{
    return hazard_hash_u64(h, (u64)v);
}

static char* hazard_trim(char* text)
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

static int hazard_parse_u32(const char* text, u32* out_value)
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

static int hazard_parse_u64(const char* text, u64* out_value)
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

static int hazard_parse_q16(const char* text, q16_16* out_value)
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

static int hazard_parse_q48(const char* text, q48_16* out_value)
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

static int hazard_parse_triplet_q16(const char* text, q16_16* a, q16_16* b, q16_16* c)
{
    char buffer[HAZARD_LINE_MAX];
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
    if (!hazard_parse_q16(hazard_trim(first), a)) return 0;
    if (!hazard_parse_q16(hazard_trim(second), b)) return 0;
    if (!hazard_parse_q16(hazard_trim(third), c)) return 0;
    return 1;
}

static int hazard_parse_point(const char* text, dom_domain_point* out_point)
{
    q16_16 x;
    q16_16 y;
    q16_16 z;
    if (!text || !out_point) {
        return 0;
    }
    if (!hazard_parse_triplet_q16(text, &x, &y, &z)) {
        return 0;
    }
    out_point->x = x;
    out_point->y = y;
    out_point->z = z;
    return 1;
}

static int hazard_parse_indexed_key(const char* key,
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

static u32 hazard_class_from_text(const char* text)
{
    if (!text) {
        return DOM_HAZARD_CLASS_UNSET;
    }
    if (strcmp(text, "fire") == 0) return DOM_HAZARD_CLASS_FIRE;
    if (strcmp(text, "toxic") == 0) return DOM_HAZARD_CLASS_TOXIC;
    if (strcmp(text, "radiation") == 0) return DOM_HAZARD_CLASS_RADIATION;
    if (strcmp(text, "pressure") == 0) return DOM_HAZARD_CLASS_PRESSURE;
    if (strcmp(text, "thermal") == 0) return DOM_HAZARD_CLASS_THERMAL;
    if (strcmp(text, "biological") == 0) return DOM_HAZARD_CLASS_BIOLOGICAL;
    if (strcmp(text, "information") == 0) return DOM_HAZARD_CLASS_INFORMATION;
    return DOM_HAZARD_CLASS_UNSET;
}

static void hazard_fixture_init(hazard_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_hazard_surface_desc_init(&fixture->hazard_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "hazard.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void hazard_fixture_register_region(hazard_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_HAZARD_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int hazard_fixture_apply_type(hazard_fixture* fixture,
                                     u32 index,
                                     const char* suffix,
                                     const char* value)
{
    dom_hazard_type_desc* type;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HAZARD_MAX_TYPES) {
        return 0;
    }
    if (fixture->hazard_desc.type_count <= index) {
        fixture->hazard_desc.type_count = index + 1u;
    }
    type = &fixture->hazard_desc.types[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->type_names[index], value, sizeof(fixture->type_names[index]) - 1);
        fixture->type_names[index][sizeof(fixture->type_names[index]) - 1] = '\0';
        type->type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "class") == 0) {
        type->hazard_class = hazard_class_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "default_intensity") == 0) {
        return hazard_parse_q16(value, &type->default_intensity);
    }
    if (strcmp(suffix, "default_exposure") == 0) {
        return hazard_parse_q16(value, &type->default_exposure_rate);
    }
    if (strcmp(suffix, "default_decay") == 0) {
        return hazard_parse_q16(value, &type->default_decay_rate);
    }
    if (strcmp(suffix, "default_uncertainty") == 0) {
        return hazard_parse_q16(value, &type->default_uncertainty);
    }
    return 0;
}

static int hazard_fixture_apply_field(hazard_fixture* fixture,
                                      u32 index,
                                      const char* suffix,
                                      const char* value)
{
    dom_hazard_field_desc* field;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HAZARD_MAX_FIELDS) {
        return 0;
    }
    if (fixture->hazard_desc.field_count <= index) {
        fixture->hazard_desc.field_count = index + 1u;
    }
    field = &fixture->hazard_desc.fields[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->field_names[index], value, sizeof(fixture->field_names[index]) - 1);
        fixture->field_names[index][sizeof(fixture->field_names[index]) - 1] = '\0';
        field->hazard_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        field->hazard_type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "intensity") == 0) {
        return hazard_parse_q16(value, &field->intensity);
    }
    if (strcmp(suffix, "exposure") == 0) {
        return hazard_parse_q16(value, &field->exposure_rate);
    }
    if (strcmp(suffix, "decay") == 0) {
        return hazard_parse_q16(value, &field->decay_rate);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return hazard_parse_q16(value, &field->uncertainty);
    }
    if (strcmp(suffix, "provenance") == 0) {
        field->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        field->region_id = region_id;
        hazard_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "radius") == 0) {
        return hazard_parse_q16(value, &field->radius);
    }
    if (strcmp(suffix, "pos") == 0) {
        return hazard_parse_point(value, &field->center);
    }
    return 0;
}

static int hazard_fixture_apply_exposure(hazard_fixture* fixture,
                                         u32 index,
                                         const char* suffix,
                                         const char* value)
{
    dom_hazard_exposure_desc* exposure;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_HAZARD_MAX_EXPOSURES) {
        return 0;
    }
    if (fixture->hazard_desc.exposure_count <= index) {
        fixture->hazard_desc.exposure_count = index + 1u;
    }
    exposure = &fixture->hazard_desc.exposures[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->exposure_names[index], value, sizeof(fixture->exposure_names[index]) - 1);
        fixture->exposure_names[index][sizeof(fixture->exposure_names[index]) - 1] = '\0';
        exposure->exposure_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "type") == 0) {
        exposure->hazard_type_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "limit") == 0) {
        return hazard_parse_q48(value, &exposure->exposure_limit);
    }
    if (strcmp(suffix, "sensitivity") == 0) {
        return hazard_parse_q16(value, &exposure->sensitivity);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return hazard_parse_q16(value, &exposure->uncertainty);
    }
    if (strcmp(suffix, "provenance") == 0) {
        exposure->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        exposure->region_id = region_id;
        hazard_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "pos") == 0) {
        return hazard_parse_point(value, &exposure->location);
    }
    if (strcmp(suffix, "accumulated") == 0) {
        return hazard_parse_q48(value, &exposure->exposure_accumulated);
    }
    return 0;
}

static int hazard_fixture_apply(hazard_fixture* fixture, const char* key, const char* value)
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
        return hazard_parse_u64(value, &fixture->hazard_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return hazard_parse_u64(value, &fixture->hazard_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return hazard_parse_q16(value, &fixture->hazard_desc.meters_per_unit);
    }
    if (strcmp(key, "type_count") == 0) {
        return hazard_parse_u32(value, &fixture->hazard_desc.type_count);
    }
    if (strcmp(key, "field_count") == 0) {
        return hazard_parse_u32(value, &fixture->hazard_desc.field_count);
    }
    if (strcmp(key, "exposure_count") == 0) {
        return hazard_parse_u32(value, &fixture->hazard_desc.exposure_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return hazard_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return hazard_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return hazard_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return hazard_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (hazard_parse_indexed_key(key, "type_", &index, &suffix)) {
        return hazard_fixture_apply_type(fixture, index, suffix, value);
    }
    if (hazard_parse_indexed_key(key, "field_", &index, &suffix)) {
        return hazard_fixture_apply_field(fixture, index, suffix, value);
    }
    if (hazard_parse_indexed_key(key, "exposure_", &index, &suffix)) {
        return hazard_fixture_apply_exposure(fixture, index, suffix, value);
    }
    return 0;
}

static int hazard_fixture_load(const char* path, hazard_fixture* out_fixture)
{
    FILE* file;
    char line[HAZARD_LINE_MAX];
    int header_ok = 0;
    hazard_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    hazard_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = hazard_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, HAZARD_FIXTURE_HEADER) != 0) {
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
        hazard_fixture_apply(&fixture, hazard_trim(text), hazard_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* hazard_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 hazard_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = hazard_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && hazard_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 hazard_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = hazard_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && hazard_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 hazard_find_region_id(const hazard_fixture* fixture, const char* name)
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

static const char* hazard_lookup_type_name(const hazard_fixture* fixture, u32 type_id)
{
    if (!fixture || type_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->hazard_desc.type_count; ++i) {
        if (fixture->hazard_desc.types[i].type_id == type_id) {
            return fixture->type_names[i];
        }
    }
    return "";
}

static const char* hazard_lookup_field_name(const hazard_fixture* fixture, u32 field_id)
{
    if (!fixture || field_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->hazard_desc.field_count; ++i) {
        if (fixture->hazard_desc.fields[i].hazard_id == field_id) {
            return fixture->field_names[i];
        }
    }
    return "";
}

static const char* hazard_lookup_exposure_name(const hazard_fixture* fixture, u32 exposure_id)
{
    if (!fixture || exposure_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->hazard_desc.exposure_count; ++i) {
        if (fixture->hazard_desc.exposures[i].exposure_id == exposure_id) {
            return fixture->exposure_names[i];
        }
    }
    return "";
}

static int hazard_type_exists(const hazard_fixture* fixture, u32 type_id)
{
    if (!fixture || type_id == 0u) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->hazard_desc.type_count; ++i) {
        if (fixture->hazard_desc.types[i].type_id == type_id) {
            return 1;
        }
    }
    return 0;
}

static int hazard_ratio_valid(q16_16 value)
{
    return !(value < 0 || value > DOM_HAZARD_RATIO_ONE_Q16);
}

static int hazard_validate_fixture(const hazard_fixture* fixture)
{
    if (!fixture) {
        return 0;
    }
    if (fixture->hazard_desc.type_count > DOM_HAZARD_MAX_TYPES) {
        return 0;
    }
    if (fixture->hazard_desc.field_count > DOM_HAZARD_MAX_FIELDS) {
        return 0;
    }
    if (fixture->hazard_desc.exposure_count > DOM_HAZARD_MAX_EXPOSURES) {
        return 0;
    }
    for (u32 i = 0u; i < fixture->hazard_desc.type_count; ++i) {
        const dom_hazard_type_desc* type = &fixture->hazard_desc.types[i];
        if (type->type_id == 0u) {
            return 0;
        }
        if (!hazard_ratio_valid(type->default_intensity)) {
            return 0;
        }
        if (!hazard_ratio_valid(type->default_exposure_rate)) {
            return 0;
        }
        if (!hazard_ratio_valid(type->default_decay_rate)) {
            return 0;
        }
        if (!hazard_ratio_valid(type->default_uncertainty)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->hazard_desc.field_count; ++i) {
        const dom_hazard_field_desc* field = &fixture->hazard_desc.fields[i];
        if (field->hazard_id == 0u) {
            return 0;
        }
        if (field->hazard_type_id == 0u || !hazard_type_exists(fixture, field->hazard_type_id)) {
            return 0;
        }
        if (!hazard_ratio_valid(field->intensity)) {
            return 0;
        }
        if (!hazard_ratio_valid(field->exposure_rate)) {
            return 0;
        }
        if (!hazard_ratio_valid(field->decay_rate)) {
            return 0;
        }
        if (!hazard_ratio_valid(field->uncertainty)) {
            return 0;
        }
    }
    for (u32 i = 0u; i < fixture->hazard_desc.exposure_count; ++i) {
        const dom_hazard_exposure_desc* exposure = &fixture->hazard_desc.exposures[i];
        if (exposure->exposure_id == 0u) {
            return 0;
        }
        if (exposure->hazard_type_id != 0u &&
            !hazard_type_exists(fixture, exposure->hazard_type_id)) {
            return 0;
        }
        if (!hazard_ratio_valid(exposure->sensitivity)) {
            return 0;
        }
        if (!hazard_ratio_valid(exposure->uncertainty)) {
            return 0;
        }
    }
    return 1;
}

static int hazard_run_validate(const hazard_fixture* fixture)
{
    int ok = hazard_validate_fixture(fixture);
    printf("%s\n", HAZARD_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HAZARD_PROVIDER_CHAIN);
    printf("type_count=%u\n", (unsigned int)fixture->hazard_desc.type_count);
    printf("field_count=%u\n", (unsigned int)fixture->hazard_desc.field_count);
    printf("exposure_count=%u\n", (unsigned int)fixture->hazard_desc.exposure_count);
    printf("ok=%u\n", (unsigned int)(ok ? 1u : 0u));
    return ok ? 0 : 1;
}

static int hazard_run_inspect_type(const hazard_fixture* fixture,
                                   const char* type_name,
                                   u32 budget_max)
{
    dom_hazard_domain domain;
    dom_domain_budget budget;
    dom_hazard_type_sample sample;
    u32 type_id;
    if (!type_name) {
        return 1;
    }
    type_id = d_rng_hash_str32(type_name);
    dom_hazard_domain_init(&domain, &fixture->hazard_desc);
    if (fixture->policy_set) {
        dom_hazard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_hazard_type_query(&domain, type_id, &budget, &sample);

    printf("%s\n", HAZARD_INSPECT_HEADER);
    printf("entity=type\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HAZARD_PROVIDER_CHAIN);
    printf("type_id=%u\n", (unsigned int)sample.type_id);
    printf("type_id_str=%s\n", hazard_lookup_type_name(fixture, sample.type_id));
    printf("hazard_class=%u\n", (unsigned int)sample.hazard_class);
    printf("default_intensity_q16=%d\n", (int)sample.default_intensity);
    printf("default_exposure_rate_q16=%d\n", (int)sample.default_exposure_rate);
    printf("default_decay_rate_q16=%d\n", (int)sample.default_decay_rate);
    printf("default_uncertainty_q16=%d\n", (int)sample.default_uncertainty);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_hazard_domain_free(&domain);
    return 0;
}

static int hazard_run_inspect_field(const hazard_fixture* fixture,
                                    const char* field_name,
                                    u32 budget_max)
{
    dom_hazard_domain domain;
    dom_domain_budget budget;
    dom_hazard_field_sample sample;
    u32 field_id;
    if (!field_name) {
        return 1;
    }
    field_id = d_rng_hash_str32(field_name);
    dom_hazard_domain_init(&domain, &fixture->hazard_desc);
    if (fixture->policy_set) {
        dom_hazard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_hazard_field_query(&domain, field_id, &budget, &sample);

    printf("%s\n", HAZARD_INSPECT_HEADER);
    printf("entity=field\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HAZARD_PROVIDER_CHAIN);
    printf("hazard_id=%u\n", (unsigned int)sample.hazard_id);
    printf("hazard_id_str=%s\n", hazard_lookup_field_name(fixture, sample.hazard_id));
    printf("hazard_type_id=%u\n", (unsigned int)sample.hazard_type_id);
    printf("hazard_type_id_str=%s\n", hazard_lookup_type_name(fixture, sample.hazard_type_id));
    printf("intensity_q16=%d\n", (int)sample.intensity);
    printf("exposure_rate_q16=%d\n", (int)sample.exposure_rate);
    printf("decay_rate_q16=%d\n", (int)sample.decay_rate);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
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

    dom_hazard_domain_free(&domain);
    return 0;
}

static int hazard_run_inspect_exposure(const hazard_fixture* fixture,
                                       const char* exposure_name,
                                       u32 budget_max)
{
    dom_hazard_domain domain;
    dom_domain_budget budget;
    dom_hazard_exposure_sample sample;
    u32 exposure_id;
    if (!exposure_name) {
        return 1;
    }
    exposure_id = d_rng_hash_str32(exposure_name);
    dom_hazard_domain_init(&domain, &fixture->hazard_desc);
    if (fixture->policy_set) {
        dom_hazard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_hazard_exposure_query(&domain, exposure_id, &budget, &sample);

    printf("%s\n", HAZARD_INSPECT_HEADER);
    printf("entity=exposure\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HAZARD_PROVIDER_CHAIN);
    printf("exposure_id=%u\n", (unsigned int)sample.exposure_id);
    printf("exposure_id_str=%s\n", hazard_lookup_exposure_name(fixture, sample.exposure_id));
    printf("hazard_type_id=%u\n", (unsigned int)sample.hazard_type_id);
    printf("hazard_type_id_str=%s\n", hazard_lookup_type_name(fixture, sample.hazard_type_id));
    printf("exposure_limit_q48=%lld\n", (long long)sample.exposure_limit);
    printf("sensitivity_q16=%d\n", (int)sample.sensitivity);
    printf("uncertainty_q16=%d\n", (int)sample.uncertainty);
    printf("provenance_id=%u\n", (unsigned int)sample.provenance_id);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("exposure_accumulated_q48=%lld\n", (long long)sample.exposure_accumulated);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_hazard_domain_free(&domain);
    return 0;
}

static int hazard_run_inspect_region(const hazard_fixture* fixture,
                                     const char* region_name,
                                     u32 budget_max)
{
    dom_hazard_domain domain;
    dom_domain_budget budget;
    dom_hazard_region_sample sample;
    u32 region_id = hazard_find_region_id(fixture, region_name);

    dom_hazard_domain_init(&domain, &fixture->hazard_desc);
    if (fixture->policy_set) {
        dom_hazard_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_hazard_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", HAZARD_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HAZARD_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("field_count=%u\n", (unsigned int)sample.field_count);
    printf("exposure_count=%u\n", (unsigned int)sample.exposure_count);
    printf("hazard_energy_total_q48=%lld\n", (long long)sample.hazard_energy_total);
    printf("exposure_total_q48=%lld\n", (long long)sample.exposure_total);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_hazard_domain_free(&domain);
    return 0;
}

static int hazard_run_resolve(const hazard_fixture* fixture,
                              const char* region_name,
                              u64 tick,
                              u64 tick_delta,
                              u32 budget_max,
                              u32 inactive_count)
{
    dom_hazard_domain domain;
    dom_hazard_domain* inactive = 0;
    dom_domain_budget budget;
    dom_hazard_resolve_result result;
    u32 region_id = hazard_find_region_id(fixture, region_name);
    u64 hash = 14695981039346656037ULL;

    dom_hazard_domain_init(&domain, &fixture->hazard_desc);
    if (fixture->policy_set) {
        dom_hazard_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_hazard_domain*)malloc(sizeof(dom_hazard_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                hazard_fixture temp = *fixture;
                temp.hazard_desc.domain_id = fixture->hazard_desc.domain_id + (u64)(i + 1u);
                dom_hazard_domain_init(&inactive[i], &temp.hazard_desc);
                dom_hazard_domain_set_state(&inactive[i],
                                            DOM_DOMAIN_EXISTENCE_DECLARED,
                                            DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_hazard_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.field_count; ++i) {
        hash = hazard_hash_u32(hash, domain.fields[i].hazard_id);
        hash = hazard_hash_q16(hash, domain.fields[i].intensity);
        hash = hazard_hash_q16(hash, domain.fields[i].exposure_rate);
    }
    for (u32 i = 0u; i < domain.exposure_count; ++i) {
        hash = hazard_hash_u32(hash, domain.exposures[i].exposure_id);
        hash = hazard_hash_q48(hash, domain.exposures[i].exposure_accumulated);
    }

    printf("%s\n", HAZARD_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HAZARD_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("field_count=%u\n", (unsigned int)result.field_count);
    printf("exposure_count=%u\n", (unsigned int)result.exposure_count);
    printf("exposure_over_limit_count=%u\n", (unsigned int)result.exposure_over_limit_count);
    printf("hazard_energy_total_q48=%lld\n", (long long)result.hazard_energy_total);
    printf("exposure_total_q48=%lld\n", (long long)result.exposure_total);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_hazard_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_hazard_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int hazard_run_collapse(const hazard_fixture* fixture, const char* region_name)
{
    dom_hazard_domain domain;
    u32 region_id = hazard_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_hazard_domain_init(&domain, &fixture->hazard_desc);
    if (fixture->policy_set) {
        dom_hazard_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_hazard_domain_capsule_count(&domain);
    (void)dom_hazard_domain_collapse_region(&domain, region_id);
    count_after = dom_hazard_domain_capsule_count(&domain);

    printf("%s\n", HAZARD_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", HAZARD_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_hazard_domain_free(&domain);
    return 0;
}

static void hazard_usage(void)
{
    printf("dom_tool_hazard commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --type <id> [--budget N]\n");
    printf("  inspect --fixture <path> --field <id> [--budget N]\n");
    printf("  inspect --fixture <path> --exposure <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        hazard_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = hazard_find_arg(argc, argv, "--fixture");
        hazard_fixture fixture;
        if (!fixture_path || !hazard_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "hazard: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return hazard_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* type_name = hazard_find_arg(argc, argv, "--type");
            const char* field_name = hazard_find_arg(argc, argv, "--field");
            const char* exposure_name = hazard_find_arg(argc, argv, "--exposure");
            const char* region_name = hazard_find_arg(argc, argv, "--region");
            u32 budget_max = hazard_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (type_name) {
                return hazard_run_inspect_type(&fixture, type_name, budget_max);
            }
            if (field_name) {
                return hazard_run_inspect_field(&fixture, field_name, budget_max);
            }
            if (exposure_name) {
                return hazard_run_inspect_exposure(&fixture, exposure_name, budget_max);
            }
            if (region_name) {
                return hazard_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr, "hazard: inspect requires --type, --field, --exposure, or --region\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = hazard_find_arg(argc, argv, "--region");
            u64 tick = hazard_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = hazard_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = hazard_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = hazard_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!region_name) {
                fprintf(stderr, "hazard: resolve requires --region\n");
                return 2;
            }
            return hazard_run_resolve(&fixture, region_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = hazard_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "hazard: collapse requires --region\n");
                return 2;
            }
            return hazard_run_collapse(&fixture, region_name);
        }
    }

    hazard_usage();
    return 2;
}
