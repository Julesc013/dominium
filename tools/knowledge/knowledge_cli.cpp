/*
FILE: tools/knowledge/knowledge_cli.cpp
MODULE: Dominium
PURPOSE: Knowledge fixture CLI for deterministic learning/skill checks.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#include "domino/core/fixed.h"
#include "domino/core/rng_model.h"
#include "domino/world/knowledge_fields.h"

#define KNOWLEDGE_FIXTURE_HEADER "DOMINIUM_KNOWLEDGE_FIXTURE_V1"

#define KNOWLEDGE_VALIDATE_HEADER "DOMINIUM_KNOWLEDGE_VALIDATE_V1"
#define KNOWLEDGE_INSPECT_HEADER "DOMINIUM_KNOWLEDGE_INSPECT_V1"
#define KNOWLEDGE_RESOLVE_HEADER "DOMINIUM_KNOWLEDGE_RESOLVE_V1"
#define KNOWLEDGE_COLLAPSE_HEADER "DOMINIUM_KNOWLEDGE_COLLAPSE_V1"

#define KNOWLEDGE_PROVIDER_CHAIN "artifacts->skills->programs->events"

#define KNOWLEDGE_LINE_MAX 512u

typedef struct knowledge_fixture {
    char fixture_id[96];
    dom_knowledge_surface_desc knowledge_desc;
    dom_domain_policy policy;
    u32 policy_set;
    char artifact_names[DOM_KNOWLEDGE_MAX_ARTIFACTS][64];
    char skill_names[DOM_KNOWLEDGE_MAX_SKILLS][64];
    char program_names[DOM_KNOWLEDGE_MAX_PROGRAMS][64];
    char event_names[DOM_KNOWLEDGE_MAX_EVENTS][64];
    char region_names[DOM_KNOWLEDGE_MAX_REGIONS][64];
    u32 region_ids[DOM_KNOWLEDGE_MAX_REGIONS];
    u32 region_count;
} knowledge_fixture;

static u64 knowledge_hash_u64(u64 h, u64 v)
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

static u64 knowledge_hash_u32(u64 h, u32 v)
{
    return knowledge_hash_u64(h, (u64)v);
}

static u64 knowledge_hash_q16(u64 h, q16_16 v)
{
    return knowledge_hash_u64(h, (u64)(u32)v);
}

static u64 knowledge_hash_q48(u64 h, q48_16 v)
{
    return knowledge_hash_u64(h, (u64)v);
}

static char* knowledge_trim(char* text)
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

static int knowledge_parse_u32(const char* text, u32* out_value)
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

static int knowledge_parse_u64(const char* text, u64* out_value)
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

static int knowledge_parse_q16(const char* text, q16_16* out_value)
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

static int knowledge_parse_q48(const char* text, q48_16* out_value)
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

static int knowledge_parse_indexed_key(const char* key,
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

static u32 knowledge_process_from_text(const char* text)
{
    if (!text) {
        return DOM_KNOWLEDGE_PROCESS_UNSET;
    }
    if (strcmp(text, "practice") == 0) return DOM_KNOWLEDGE_PROCESS_PRACTICE;
    if (strcmp(text, "study") == 0) return DOM_KNOWLEDGE_PROCESS_STUDY;
    if (strcmp(text, "train") == 0) return DOM_KNOWLEDGE_PROCESS_TRAIN;
    if (strcmp(text, "certify") == 0) return DOM_KNOWLEDGE_PROCESS_CERTIFY;
    return DOM_KNOWLEDGE_PROCESS_UNSET;
}

static void knowledge_fixture_init(knowledge_fixture* fixture)
{
    if (!fixture) {
        return;
    }
    memset(fixture, 0, sizeof(*fixture));
    dom_knowledge_surface_desc_init(&fixture->knowledge_desc);
    dom_domain_policy_init(&fixture->policy);
    fixture->policy_set = 0u;
    fixture->region_count = 0u;
    strncpy(fixture->fixture_id, "knowledge.fixture.unknown", sizeof(fixture->fixture_id) - 1);
    fixture->fixture_id[sizeof(fixture->fixture_id) - 1] = '\0';
}

static void knowledge_fixture_register_region(knowledge_fixture* fixture, const char* name, u32 id)
{
    if (!fixture || !name || !*name || id == 0u) {
        return;
    }
    for (u32 i = 0u; i < fixture->region_count; ++i) {
        if (fixture->region_ids[i] == id) {
            return;
        }
    }
    if (fixture->region_count >= DOM_KNOWLEDGE_MAX_REGIONS) {
        return;
    }
    fixture->region_ids[fixture->region_count] = id;
    strncpy(fixture->region_names[fixture->region_count], name,
            sizeof(fixture->region_names[fixture->region_count]) - 1);
    fixture->region_names[fixture->region_count][sizeof(fixture->region_names[fixture->region_count]) - 1] = '\0';
    fixture->region_count += 1u;
}

static int knowledge_fixture_apply_artifact(knowledge_fixture* fixture,
                                            u32 index,
                                            const char* suffix,
                                            const char* value)
{
    dom_knowledge_artifact_desc* artifact;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_KNOWLEDGE_MAX_ARTIFACTS) {
        return 0;
    }
    if (fixture->knowledge_desc.artifact_count <= index) {
        fixture->knowledge_desc.artifact_count = index + 1u;
    }
    artifact = &fixture->knowledge_desc.artifacts[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->artifact_names[index], value, sizeof(fixture->artifact_names[index]) - 1);
        fixture->artifact_names[index][sizeof(fixture->artifact_names[index]) - 1] = '\0';
        artifact->artifact_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "domain") == 0) {
        artifact->subject_domain_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "claims") == 0) {
        return knowledge_parse_u32(value, &artifact->claim_count);
    }
    if (strcmp(suffix, "evidence") == 0) {
        return knowledge_parse_u32(value, &artifact->evidence_count);
    }
    if (strcmp(suffix, "confidence") == 0) {
        return knowledge_parse_q16(value, &artifact->confidence);
    }
    if (strcmp(suffix, "uncertainty") == 0) {
        return knowledge_parse_q16(value, &artifact->uncertainty);
    }
    if (strcmp(suffix, "decay") == 0) {
        return knowledge_parse_q16(value, &artifact->decay_rate);
    }
    if (strcmp(suffix, "provenance") == 0) {
        artifact->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        artifact->region_id = region_id;
        knowledge_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int knowledge_fixture_apply_skill(knowledge_fixture* fixture,
                                         u32 index,
                                         const char* suffix,
                                         const char* value)
{
    dom_skill_profile_desc* profile;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_KNOWLEDGE_MAX_SKILLS) {
        return 0;
    }
    if (fixture->knowledge_desc.skill_count <= index) {
        fixture->knowledge_desc.skill_count = index + 1u;
    }
    profile = &fixture->knowledge_desc.skills[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->skill_names[index], value, sizeof(fixture->skill_names[index]) - 1);
        fixture->skill_names[index][sizeof(fixture->skill_names[index]) - 1] = '\0';
        profile->profile_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "subject") == 0) {
        profile->subject_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "domain") == 0) {
        profile->skill_domain_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "variance") == 0) {
        return knowledge_parse_q16(value, &profile->variance_reduction);
    }
    if (strcmp(suffix, "bias") == 0) {
        return knowledge_parse_q16(value, &profile->failure_bias_reduction);
    }
    if (strcmp(suffix, "decay") == 0) {
        return knowledge_parse_q16(value, &profile->decay_rate);
    }
    if (strcmp(suffix, "process_count") == 0) {
        return knowledge_parse_u32(value, &profile->process_ref_count);
    }
    if (strncmp(suffix, "process_", 8) == 0) {
        u32 proc_index = 0u;
        if (knowledge_parse_u32(suffix + 8, &proc_index) && proc_index < DOM_KNOWLEDGE_MAX_PROCESS_REFS) {
            profile->process_refs[proc_index] = d_rng_hash_str32(value);
            if (profile->process_ref_count <= proc_index) {
                profile->process_ref_count = proc_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "provenance") == 0) {
        profile->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        profile->region_id = region_id;
        knowledge_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int knowledge_fixture_apply_program(knowledge_fixture* fixture,
                                           u32 index,
                                           const char* suffix,
                                           const char* value)
{
    dom_education_program_desc* program;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_KNOWLEDGE_MAX_PROGRAMS) {
        return 0;
    }
    if (fixture->knowledge_desc.program_count <= index) {
        fixture->knowledge_desc.program_count = index + 1u;
    }
    program = &fixture->knowledge_desc.programs[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->program_names[index], value, sizeof(fixture->program_names[index]) - 1);
        fixture->program_names[index][sizeof(fixture->program_names[index]) - 1] = '\0';
        program->program_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "curriculum") == 0) {
        program->curriculum_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "duration") == 0) {
        return knowledge_parse_u64(value, &program->duration_ticks);
    }
    if (strcmp(suffix, "energy") == 0) {
        return knowledge_parse_q48(value, &program->energy_cost);
    }
    if (strcmp(suffix, "resource") == 0) {
        return knowledge_parse_q48(value, &program->resource_cost);
    }
    if (strcmp(suffix, "instructor_count") == 0) {
        return knowledge_parse_u32(value, &program->instructor_count);
    }
    if (strncmp(suffix, "instructor_", 11) == 0) {
        u32 inst_index = 0u;
        if (knowledge_parse_u32(suffix + 11, &inst_index) &&
            inst_index < DOM_KNOWLEDGE_MAX_INSTRUCTOR_REFS) {
            program->instructor_refs[inst_index] = d_rng_hash_str32(value);
            if (program->instructor_count <= inst_index) {
                program->instructor_count = inst_index + 1u;
            }
            return 1;
        }
    }
    if (strcmp(suffix, "output_skill") == 0) {
        program->output_skill_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "accreditation") == 0) {
        program->accreditation_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        program->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        program->region_id = region_id;
        knowledge_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    return 0;
}

static int knowledge_fixture_apply_event(knowledge_fixture* fixture,
                                         u32 index,
                                         const char* suffix,
                                         const char* value)
{
    dom_knowledge_event_desc* event;
    if (!fixture || !suffix || !value) {
        return 0;
    }
    if (index >= DOM_KNOWLEDGE_MAX_EVENTS) {
        return 0;
    }
    if (fixture->knowledge_desc.event_count <= index) {
        fixture->knowledge_desc.event_count = index + 1u;
    }
    event = &fixture->knowledge_desc.events[index];
    if (strcmp(suffix, "id") == 0) {
        strncpy(fixture->event_names[index], value, sizeof(fixture->event_names[index]) - 1);
        fixture->event_names[index][sizeof(fixture->event_names[index]) - 1] = '\0';
        event->event_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "process") == 0) {
        event->process_type = knowledge_process_from_text(value);
        return 1;
    }
    if (strcmp(suffix, "subject") == 0) {
        event->subject_ref_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "artifact") == 0) {
        event->artifact_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "skill") == 0) {
        event->skill_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "program") == 0) {
        event->program_id = d_rng_hash_str32(value);
        return 1;
    }
    if (strcmp(suffix, "delta_confidence") == 0) {
        return knowledge_parse_q16(value, &event->delta_confidence);
    }
    if (strcmp(suffix, "delta_uncertainty") == 0) {
        return knowledge_parse_q16(value, &event->delta_uncertainty);
    }
    if (strcmp(suffix, "delta_variance") == 0) {
        return knowledge_parse_q16(value, &event->delta_variance);
    }
    if (strcmp(suffix, "delta_bias") == 0) {
        return knowledge_parse_q16(value, &event->delta_failure_bias);
    }
    if (strcmp(suffix, "tick") == 0) {
        return knowledge_parse_u64(value, &event->event_tick);
    }
    if (strcmp(suffix, "region") == 0) {
        u32 region_id = d_rng_hash_str32(value);
        event->region_id = region_id;
        knowledge_fixture_register_region(fixture, value, region_id);
        return 1;
    }
    if (strcmp(suffix, "provenance") == 0) {
        event->provenance_id = d_rng_hash_str32(value);
        return 1;
    }
    return 0;
}

static int knowledge_fixture_apply(knowledge_fixture* fixture, const char* key, const char* value)
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
        return knowledge_parse_u64(value, &fixture->knowledge_desc.world_seed);
    }
    if (strcmp(key, "domain_id") == 0) {
        return knowledge_parse_u64(value, &fixture->knowledge_desc.domain_id);
    }
    if (strcmp(key, "meters_per_unit") == 0) {
        return knowledge_parse_q16(value, &fixture->knowledge_desc.meters_per_unit);
    }
    if (strcmp(key, "artifact_count") == 0) {
        return knowledge_parse_u32(value, &fixture->knowledge_desc.artifact_count);
    }
    if (strcmp(key, "skill_count") == 0) {
        return knowledge_parse_u32(value, &fixture->knowledge_desc.skill_count);
    }
    if (strcmp(key, "program_count") == 0) {
        return knowledge_parse_u32(value, &fixture->knowledge_desc.program_count);
    }
    if (strcmp(key, "event_count") == 0) {
        return knowledge_parse_u32(value, &fixture->knowledge_desc.event_count);
    }
    if (strcmp(key, "cost_full") == 0) {
        fixture->policy_set = 1u;
        return knowledge_parse_u32(value, &fixture->policy.cost_full);
    }
    if (strcmp(key, "cost_medium") == 0) {
        fixture->policy_set = 1u;
        return knowledge_parse_u32(value, &fixture->policy.cost_medium);
    }
    if (strcmp(key, "cost_coarse") == 0) {
        fixture->policy_set = 1u;
        return knowledge_parse_u32(value, &fixture->policy.cost_coarse);
    }
    if (strcmp(key, "cost_analytic") == 0) {
        fixture->policy_set = 1u;
        return knowledge_parse_u32(value, &fixture->policy.cost_analytic);
    }

    if (knowledge_parse_indexed_key(key, "artifact_", &index, &suffix)) {
        return knowledge_fixture_apply_artifact(fixture, index, suffix, value);
    }
    if (knowledge_parse_indexed_key(key, "skill_", &index, &suffix)) {
        return knowledge_fixture_apply_skill(fixture, index, suffix, value);
    }
    if (knowledge_parse_indexed_key(key, "program_", &index, &suffix)) {
        return knowledge_fixture_apply_program(fixture, index, suffix, value);
    }
    if (knowledge_parse_indexed_key(key, "event_", &index, &suffix)) {
        return knowledge_fixture_apply_event(fixture, index, suffix, value);
    }
    return 0;
}

static int knowledge_fixture_load(const char* path, knowledge_fixture* out_fixture)
{
    FILE* file;
    char line[KNOWLEDGE_LINE_MAX];
    int header_ok = 0;
    knowledge_fixture fixture;
    if (!path || !out_fixture) {
        return 0;
    }
    file = fopen(path, "r");
    if (!file) {
        return 0;
    }
    knowledge_fixture_init(&fixture);
    while (fgets(line, sizeof(line), file)) {
        char* text = knowledge_trim(line);
        char* eq;
        if (!text || !*text) {
            continue;
        }
        if (text[0] == '#') {
            continue;
        }
        if (!header_ok) {
            if (strcmp(text, KNOWLEDGE_FIXTURE_HEADER) != 0) {
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
        knowledge_fixture_apply(&fixture, knowledge_trim(text), knowledge_trim(eq));
    }
    fclose(file);
    if (!header_ok) {
        return 0;
    }
    *out_fixture = fixture;
    return 1;
}

static const char* knowledge_find_arg(int argc, char** argv, const char* key)
{
    for (int i = 0; i < argc; ++i) {
        if (strcmp(argv[i], key) == 0 && i + 1 < argc) {
            return argv[i + 1];
        }
    }
    return 0;
}

static u32 knowledge_find_arg_u32(int argc, char** argv, const char* key, u32 fallback)
{
    const char* value = knowledge_find_arg(argc, argv, key);
    u32 parsed = fallback;
    if (value && knowledge_parse_u32(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u64 knowledge_find_arg_u64(int argc, char** argv, const char* key, u64 fallback)
{
    const char* value = knowledge_find_arg(argc, argv, key);
    u64 parsed = fallback;
    if (value && knowledge_parse_u64(value, &parsed)) {
        return parsed;
    }
    return fallback;
}

static u32 knowledge_find_region_id(const knowledge_fixture* fixture, const char* name)
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

static const char* knowledge_lookup_artifact_name(const knowledge_fixture* fixture, u32 artifact_id)
{
    if (!fixture || artifact_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->knowledge_desc.artifact_count; ++i) {
        if (fixture->knowledge_desc.artifacts[i].artifact_id == artifact_id) {
            return fixture->artifact_names[i];
        }
    }
    return "";
}

static const char* knowledge_lookup_skill_name(const knowledge_fixture* fixture, u32 skill_id)
{
    if (!fixture || skill_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->knowledge_desc.skill_count; ++i) {
        if (fixture->knowledge_desc.skills[i].profile_id == skill_id) {
            return fixture->skill_names[i];
        }
    }
    return "";
}

static const char* knowledge_lookup_program_name(const knowledge_fixture* fixture, u32 program_id)
{
    if (!fixture || program_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->knowledge_desc.program_count; ++i) {
        if (fixture->knowledge_desc.programs[i].program_id == program_id) {
            return fixture->program_names[i];
        }
    }
    return "";
}

static const char* knowledge_lookup_event_name(const knowledge_fixture* fixture, u32 event_id)
{
    if (!fixture || event_id == 0u) {
        return "";
    }
    for (u32 i = 0u; i < fixture->knowledge_desc.event_count; ++i) {
        if (fixture->knowledge_desc.events[i].event_id == event_id) {
            return fixture->event_names[i];
        }
    }
    return "";
}

static int knowledge_run_validate(const knowledge_fixture* fixture)
{
    int ok = 1;
    if (!fixture) {
        return 1;
    }
    printf("%s\n", KNOWLEDGE_VALIDATE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", KNOWLEDGE_PROVIDER_CHAIN);
    printf("artifact_count=%u\n", (unsigned int)fixture->knowledge_desc.artifact_count);
    printf("skill_count=%u\n", (unsigned int)fixture->knowledge_desc.skill_count);
    printf("program_count=%u\n", (unsigned int)fixture->knowledge_desc.program_count);
    printf("event_count=%u\n", (unsigned int)fixture->knowledge_desc.event_count);
    printf("ok=%u\n", (unsigned int)(ok ? 1u : 0u));
    return ok ? 0 : 1;
}

static int knowledge_run_inspect_artifact(const knowledge_fixture* fixture,
                                          const char* artifact_name,
                                          u32 budget_max)
{
    dom_knowledge_domain domain;
    dom_domain_budget budget;
    dom_knowledge_artifact_sample sample;
    u32 artifact_id;
    if (!artifact_name) {
        return 1;
    }
    artifact_id = d_rng_hash_str32(artifact_name);
    dom_knowledge_domain_init(&domain, &fixture->knowledge_desc);
    if (fixture->policy_set) {
        dom_knowledge_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_knowledge_artifact_query(&domain, artifact_id, &budget, &sample);

    printf("%s\n", KNOWLEDGE_INSPECT_HEADER);
    printf("entity=artifact\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", KNOWLEDGE_PROVIDER_CHAIN);
    printf("artifact_id=%u\n", (unsigned int)sample.artifact_id);
    printf("artifact_id_str=%s\n", knowledge_lookup_artifact_name(fixture, sample.artifact_id));
    printf("subject_domain_id=%u\n", (unsigned int)sample.subject_domain_id);
    printf("claim_count=%u\n", (unsigned int)sample.claim_count);
    printf("evidence_count=%u\n", (unsigned int)sample.evidence_count);
    printf("confidence_q16=%d\n", (int)sample.confidence);
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

    dom_knowledge_domain_free(&domain);
    return 0;
}

static int knowledge_run_inspect_skill(const knowledge_fixture* fixture,
                                       const char* skill_name,
                                       u32 budget_max)
{
    dom_knowledge_domain domain;
    dom_domain_budget budget;
    dom_skill_profile_sample sample;
    u32 skill_id;
    if (!skill_name) {
        return 1;
    }
    skill_id = d_rng_hash_str32(skill_name);
    dom_knowledge_domain_init(&domain, &fixture->knowledge_desc);
    if (fixture->policy_set) {
        dom_knowledge_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_skill_profile_query(&domain, skill_id, &budget, &sample);

    printf("%s\n", KNOWLEDGE_INSPECT_HEADER);
    printf("entity=skill\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", KNOWLEDGE_PROVIDER_CHAIN);
    printf("profile_id=%u\n", (unsigned int)sample.profile_id);
    printf("profile_id_str=%s\n", knowledge_lookup_skill_name(fixture, sample.profile_id));
    printf("subject_ref_id=%u\n", (unsigned int)sample.subject_ref_id);
    printf("skill_domain_id=%u\n", (unsigned int)sample.skill_domain_id);
    printf("variance_reduction_q16=%d\n", (int)sample.variance_reduction);
    printf("failure_bias_reduction_q16=%d\n", (int)sample.failure_bias_reduction);
    printf("decay_rate_q16=%d\n", (int)sample.decay_rate);
    printf("process_ref_count=%u\n", (unsigned int)sample.process_ref_count);
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

    dom_knowledge_domain_free(&domain);
    return 0;
}

static int knowledge_run_inspect_program(const knowledge_fixture* fixture,
                                         const char* program_name,
                                         u32 budget_max)
{
    dom_knowledge_domain domain;
    dom_domain_budget budget;
    dom_education_program_sample sample;
    u32 program_id;
    if (!program_name) {
        return 1;
    }
    program_id = d_rng_hash_str32(program_name);
    dom_knowledge_domain_init(&domain, &fixture->knowledge_desc);
    if (fixture->policy_set) {
        dom_knowledge_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_education_program_query(&domain, program_id, &budget, &sample);

    printf("%s\n", KNOWLEDGE_INSPECT_HEADER);
    printf("entity=program\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", KNOWLEDGE_PROVIDER_CHAIN);
    printf("program_id=%u\n", (unsigned int)sample.program_id);
    printf("program_id_str=%s\n", knowledge_lookup_program_name(fixture, sample.program_id));
    printf("curriculum_id=%u\n", (unsigned int)sample.curriculum_id);
    printf("duration_ticks=%llu\n", (unsigned long long)sample.duration_ticks);
    printf("energy_cost_q48=%lld\n", (long long)sample.energy_cost);
    printf("resource_cost_q48=%lld\n", (long long)sample.resource_cost);
    printf("instructor_count=%u\n", (unsigned int)sample.instructor_count);
    printf("output_skill_id=%u\n", (unsigned int)sample.output_skill_id);
    printf("accreditation_id=%u\n", (unsigned int)sample.accreditation_id);
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

    dom_knowledge_domain_free(&domain);
    return 0;
}

static int knowledge_run_inspect_event(const knowledge_fixture* fixture,
                                       const char* event_name,
                                       u32 budget_max)
{
    dom_knowledge_domain domain;
    dom_domain_budget budget;
    dom_knowledge_event_sample sample;
    u32 event_id;
    if (!event_name) {
        return 1;
    }
    event_id = d_rng_hash_str32(event_name);
    dom_knowledge_domain_init(&domain, &fixture->knowledge_desc);
    if (fixture->policy_set) {
        dom_knowledge_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_knowledge_event_query(&domain, event_id, &budget, &sample);

    printf("%s\n", KNOWLEDGE_INSPECT_HEADER);
    printf("entity=event\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", KNOWLEDGE_PROVIDER_CHAIN);
    printf("event_id=%u\n", (unsigned int)sample.event_id);
    printf("event_id_str=%s\n", knowledge_lookup_event_name(fixture, sample.event_id));
    printf("process_type=%u\n", (unsigned int)sample.process_type);
    printf("subject_ref_id=%u\n", (unsigned int)sample.subject_ref_id);
    printf("artifact_id=%u\n", (unsigned int)sample.artifact_id);
    printf("skill_id=%u\n", (unsigned int)sample.skill_id);
    printf("program_id=%u\n", (unsigned int)sample.program_id);
    printf("delta_confidence_q16=%d\n", (int)sample.delta_confidence);
    printf("delta_uncertainty_q16=%d\n", (int)sample.delta_uncertainty);
    printf("delta_variance_q16=%d\n", (int)sample.delta_variance);
    printf("delta_bias_q16=%d\n", (int)sample.delta_failure_bias);
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

    dom_knowledge_domain_free(&domain);
    return 0;
}

static int knowledge_run_inspect_region(const knowledge_fixture* fixture,
                                        const char* region_name,
                                        u32 budget_max)
{
    dom_knowledge_domain domain;
    dom_domain_budget budget;
    dom_knowledge_region_sample sample;
    u32 region_id = knowledge_find_region_id(fixture, region_name);

    dom_knowledge_domain_init(&domain, &fixture->knowledge_desc);
    if (fixture->policy_set) {
        dom_knowledge_domain_set_policy(&domain, &fixture->policy);
    }
    dom_domain_budget_init(&budget, budget_max);
    (void)dom_knowledge_region_query(&domain, region_id, &budget, &sample);

    printf("%s\n", KNOWLEDGE_INSPECT_HEADER);
    printf("entity=region\n");
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", KNOWLEDGE_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)sample.region_id);
    printf("artifact_count=%u\n", (unsigned int)sample.artifact_count);
    printf("skill_count=%u\n", (unsigned int)sample.skill_count);
    printf("program_count=%u\n", (unsigned int)sample.program_count);
    printf("event_count=%u\n", (unsigned int)sample.event_count);
    printf("confidence_avg_q16=%d\n", (int)sample.confidence_avg);
    printf("uncertainty_avg_q16=%d\n", (int)sample.uncertainty_avg);
    printf("variance_reduction_avg_q16=%d\n", (int)sample.variance_reduction_avg);
    printf("failure_bias_reduction_avg_q16=%d\n", (int)sample.failure_bias_reduction_avg);
    printf("flags=%u\n", (unsigned int)sample.flags);
    printf("meta.status=%u\n", (unsigned int)sample.meta.status);
    printf("meta.resolution=%u\n", (unsigned int)sample.meta.resolution);
    printf("meta.confidence=%u\n", (unsigned int)sample.meta.confidence);
    printf("meta.refusal_reason=%u\n", (unsigned int)sample.meta.refusal_reason);
    printf("meta.cost_units=%u\n", (unsigned int)sample.meta.cost_units);
    printf("budget.used=%u\n", (unsigned int)sample.meta.budget_used);
    printf("budget.max=%u\n", (unsigned int)sample.meta.budget_max);

    dom_knowledge_domain_free(&domain);
    return 0;
}

static int knowledge_run_resolve(const knowledge_fixture* fixture,
                                 const char* region_name,
                                 u64 tick,
                                 u64 tick_delta,
                                 u32 budget_max,
                                 u32 inactive_count)
{
    dom_knowledge_domain domain;
    dom_knowledge_domain* inactive = 0;
    dom_domain_budget budget;
    dom_knowledge_resolve_result result;
    u32 region_id = knowledge_find_region_id(fixture, region_name);
    u64 hash = 14695981039346656037ULL;

    dom_knowledge_domain_init(&domain, &fixture->knowledge_desc);
    if (fixture->policy_set) {
        dom_knowledge_domain_set_policy(&domain, &fixture->policy);
    }

    if (inactive_count > 0u) {
        inactive = (dom_knowledge_domain*)malloc(sizeof(dom_knowledge_domain) * inactive_count);
        if (inactive) {
            for (u32 i = 0u; i < inactive_count; ++i) {
                knowledge_fixture temp = *fixture;
                temp.knowledge_desc.domain_id = fixture->knowledge_desc.domain_id + (u64)(i + 1u);
                dom_knowledge_domain_init(&inactive[i], &temp.knowledge_desc);
                dom_knowledge_domain_set_state(&inactive[i],
                                               DOM_DOMAIN_EXISTENCE_DECLARED,
                                               DOM_DOMAIN_ARCHIVAL_LIVE);
            }
        }
    }

    dom_domain_budget_init(&budget, budget_max);
    (void)dom_knowledge_resolve(&domain, region_id, tick, tick_delta, &budget, &result);

    for (u32 i = 0u; i < domain.artifact_count; ++i) {
        hash = knowledge_hash_u32(hash, domain.artifacts[i].artifact_id);
        hash = knowledge_hash_q16(hash, domain.artifacts[i].confidence);
        hash = knowledge_hash_q16(hash, domain.artifacts[i].uncertainty);
    }
    for (u32 i = 0u; i < domain.skill_count; ++i) {
        hash = knowledge_hash_u32(hash, domain.skills[i].profile_id);
        hash = knowledge_hash_q16(hash, domain.skills[i].variance_reduction);
        hash = knowledge_hash_q16(hash, domain.skills[i].failure_bias_reduction);
    }
    for (u32 i = 0u; i < domain.program_count; ++i) {
        hash = knowledge_hash_u32(hash, domain.programs[i].program_id);
        hash = knowledge_hash_u32(hash, domain.programs[i].output_skill_id);
        hash = knowledge_hash_q48(hash, domain.programs[i].energy_cost);
    }
    for (u32 i = 0u; i < domain.event_count; ++i) {
        hash = knowledge_hash_u32(hash, domain.events[i].event_id);
        hash = knowledge_hash_u32(hash, domain.events[i].flags);
    }

    printf("%s\n", KNOWLEDGE_RESOLVE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", KNOWLEDGE_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("artifact_count=%u\n", (unsigned int)result.artifact_count);
    printf("skill_count=%u\n", (unsigned int)result.skill_count);
    printf("program_count=%u\n", (unsigned int)result.program_count);
    printf("event_count=%u\n", (unsigned int)result.event_count);
    printf("event_applied_count=%u\n", (unsigned int)result.event_applied_count);
    printf("confidence_avg_q16=%d\n", (int)result.confidence_avg);
    printf("uncertainty_avg_q16=%d\n", (int)result.uncertainty_avg);
    printf("variance_reduction_avg_q16=%d\n", (int)result.variance_reduction_avg);
    printf("failure_bias_reduction_avg_q16=%d\n", (int)result.failure_bias_reduction_avg);
    printf("flags=%u\n", (unsigned int)result.flags);
    printf("ok=%u\n", (unsigned int)result.ok);
    printf("refusal_reason=%u\n", (unsigned int)result.refusal_reason);
    printf("budget.used=%u\n", (unsigned int)budget.used_units);
    printf("budget.max=%u\n", (unsigned int)budget.max_units);
    printf("resolve_hash=%llu\n", (unsigned long long)hash);

    dom_knowledge_domain_free(&domain);
    if (inactive) {
        for (u32 i = 0u; i < inactive_count; ++i) {
            dom_knowledge_domain_free(&inactive[i]);
        }
        free(inactive);
    }
    return 0;
}

static int knowledge_run_collapse(const knowledge_fixture* fixture, const char* region_name)
{
    dom_knowledge_domain domain;
    u32 region_id = knowledge_find_region_id(fixture, region_name);
    u32 count_before;
    u32 count_after;

    dom_knowledge_domain_init(&domain, &fixture->knowledge_desc);
    if (fixture->policy_set) {
        dom_knowledge_domain_set_policy(&domain, &fixture->policy);
    }
    count_before = dom_knowledge_domain_capsule_count(&domain);
    (void)dom_knowledge_domain_collapse_region(&domain, region_id);
    count_after = dom_knowledge_domain_capsule_count(&domain);

    printf("%s\n", KNOWLEDGE_COLLAPSE_HEADER);
    printf("fixture_id=%s\n", fixture->fixture_id);
    printf("provider_chain=%s\n", KNOWLEDGE_PROVIDER_CHAIN);
    printf("region_id=%u\n", (unsigned int)region_id);
    printf("capsule_count_before=%u\n", (unsigned int)count_before);
    printf("capsule_count_after=%u\n", (unsigned int)count_after);

    dom_knowledge_domain_free(&domain);
    return 0;
}

static void knowledge_usage(void)
{
    printf("dom_tool_knowledge commands:\n");
    printf("  validate --fixture <path>\n");
    printf("  inspect --fixture <path> --artifact <id> [--budget N]\n");
    printf("  inspect --fixture <path> --skill <id> [--budget N]\n");
    printf("  inspect --fixture <path> --program <id> [--budget N]\n");
    printf("  inspect --fixture <path> --event <id> [--budget N]\n");
    printf("  inspect --fixture <path> --region <id> [--budget N]\n");
    printf("  resolve --fixture <path> --region <id> [--tick N] [--delta N] [--budget N] [--inactive N]\n");
    printf("  collapse --fixture <path> --region <id>\n");
}

int main(int argc, char** argv)
{
    const char* cmd;
    if (argc < 2) {
        knowledge_usage();
        return 2;
    }
    cmd = argv[1];
    if (strcmp(cmd, "validate") == 0 ||
        strcmp(cmd, "inspect") == 0 ||
        strcmp(cmd, "resolve") == 0 ||
        strcmp(cmd, "collapse") == 0) {
        const char* fixture_path = knowledge_find_arg(argc, argv, "--fixture");
        knowledge_fixture fixture;
        if (!fixture_path || !knowledge_fixture_load(fixture_path, &fixture)) {
            fprintf(stderr, "knowledge: missing or invalid --fixture\n");
            return 2;
        }

        if (strcmp(cmd, "validate") == 0) {
            return knowledge_run_validate(&fixture);
        }
        if (strcmp(cmd, "inspect") == 0) {
            const char* artifact_name = knowledge_find_arg(argc, argv, "--artifact");
            const char* skill_name = knowledge_find_arg(argc, argv, "--skill");
            const char* program_name = knowledge_find_arg(argc, argv, "--program");
            const char* event_name = knowledge_find_arg(argc, argv, "--event");
            const char* region_name = knowledge_find_arg(argc, argv, "--region");
            u32 budget_max = knowledge_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_full);
            if (artifact_name) {
                return knowledge_run_inspect_artifact(&fixture, artifact_name, budget_max);
            }
            if (skill_name) {
                return knowledge_run_inspect_skill(&fixture, skill_name, budget_max);
            }
            if (program_name) {
                return knowledge_run_inspect_program(&fixture, program_name, budget_max);
            }
            if (event_name) {
                return knowledge_run_inspect_event(&fixture, event_name, budget_max);
            }
            if (region_name) {
                return knowledge_run_inspect_region(&fixture, region_name, budget_max);
            }
            fprintf(stderr, "knowledge: inspect requires --artifact, --skill, --program, --event, or --region\n");
            return 2;
        }
        if (strcmp(cmd, "resolve") == 0) {
            const char* region_name = knowledge_find_arg(argc, argv, "--region");
            u64 tick = knowledge_find_arg_u64(argc, argv, "--tick", 0u);
            u64 delta = knowledge_find_arg_u64(argc, argv, "--delta", 1u);
            u32 budget_max = knowledge_find_arg_u32(argc, argv, "--budget", fixture.policy.cost_medium);
            u32 inactive = knowledge_find_arg_u32(argc, argv, "--inactive", 0u);
            if (!region_name) {
                fprintf(stderr, "knowledge: resolve requires --region\n");
                return 2;
            }
            return knowledge_run_resolve(&fixture, region_name, tick, delta, budget_max, inactive);
        }
        if (strcmp(cmd, "collapse") == 0) {
            const char* region_name = knowledge_find_arg(argc, argv, "--region");
            if (!region_name) {
                fprintf(stderr, "knowledge: collapse requires --region\n");
                return 2;
            }
            return knowledge_run_collapse(&fixture, region_name);
        }
    }

    knowledge_usage();
    return 2;
}
