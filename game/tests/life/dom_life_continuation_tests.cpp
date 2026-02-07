/*
LIFE continuation tests (LIFE1).
*/
#include "dominium/life/ability_packages.h"
#include "dominium/life/continuation_policy.h"
#include "dominium/life/controller_binding.h"
#include "dominium/life/life_events_stub.h"

#include <stdio.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int build_registry(life_ability_registry* reg,
                          life_ability_package* storage,
                          u32 capacity)
{
    life_ability_registry_init(reg, storage, capacity);
    return life_ability_register_presets(reg);
}

static int test_ability_inheritance(void)
{
    life_ability_registry reg;
    life_ability_package storage[8];
    life_ability_package resolved;

    EXPECT(build_registry(&reg, storage, 8u) == 0, "register presets failed");
    EXPECT(life_ability_registry_resolve(&reg, LIFE_ABILITY_SOFTCORE_ID, &resolved) == 0,
           "resolve softcore failed");
    EXPECT((resolved.allowed_policy_mask & LIFE_POLICY_MASK(LIFE_POLICY_S1)) != 0u,
           "softcore should include S1");
    EXPECT((resolved.allowed_policy_mask & LIFE_POLICY_MASK(LIFE_POLICY_S2)) != 0u,
           "softcore should include S2");
    EXPECT(resolved.transfer_allowed == LIFE_BOOL_TRUE, "softcore transfer should be allowed");
    EXPECT(resolved.death_end_control == LIFE_BOOL_TRUE, "softcore death_end_control inherited");
    return 0;
}

static int test_s1_selection_determinism(void)
{
    life_ability_registry reg;
    life_ability_package storage[8];
    life_ability_package ability;
    life_candidate candidates_a[3];
    life_candidate candidates_b[3];
    life_authority_record auth_records[3];
    life_authority_set auth_set;
    u64 known_ids[3];
    life_epistemic_set epistemic;
    life_continuation_context ctx;
    life_continuation_decision dec_a;
    life_continuation_decision dec_b;

    EXPECT(build_registry(&reg, storage, 8u) == 0, "register presets failed");
    EXPECT(life_ability_registry_resolve(&reg, LIFE_ABILITY_HARDCORE_ID, &ability) == 0,
           "resolve hardcore failed");

    candidates_a[0].person_id = 42u;
    candidates_a[0].reason = LIFE_CANDIDATE_ORG_MEMBER;
    candidates_a[1].person_id = 7u;
    candidates_a[1].reason = LIFE_CANDIDATE_SPOUSE;
    candidates_a[2].person_id = 9u;
    candidates_a[2].reason = LIFE_CANDIDATE_ADULT_CHILD;

    candidates_b[0] = candidates_a[2];
    candidates_b[1] = candidates_a[0];
    candidates_b[2] = candidates_a[1];

    auth_records[0].controller_id = 1u;
    auth_records[0].target_person_id = 42u;
    auth_records[0].source = LIFE_AUTH_ORG;
    auth_records[1].controller_id = 1u;
    auth_records[1].target_person_id = 7u;
    auth_records[1].source = LIFE_AUTH_CONTRACT;
    auth_records[2].controller_id = 1u;
    auth_records[2].target_person_id = 9u;
    auth_records[2].source = LIFE_AUTH_PERSONAL;

    auth_set.records = auth_records;
    auth_set.count = 3u;

    known_ids[0] = 42u;
    known_ids[1] = 7u;
    known_ids[2] = 9u;
    epistemic.known_person_ids = known_ids;
    epistemic.count = 3u;

    ctx.controller_id = 1u;
    ctx.policy_type = LIFE_POLICY_S1;
    ctx.ability = &ability;
    ctx.candidates = candidates_a;
    ctx.candidate_count = 3u;
    ctx.epistemic = &epistemic;
    ctx.authority = &auth_set;
    ctx.allow_blind_delegation = 0u;
    ctx.prereqs.has_facility = 0u;
    ctx.prereqs.has_resources = 0u;
    ctx.prereqs.has_recording = 0u;
    ctx.prereqs.has_drone = 0u;

    EXPECT(life_continuation_decide(&ctx, &dec_a) == 0, "S1 decide A failed");
    EXPECT(dec_a.action == LIFE_CONT_ACTION_TRANSFER, "S1 A should transfer");

    ctx.candidates = candidates_b;
    EXPECT(life_continuation_decide(&ctx, &dec_b) == 0, "S1 decide B failed");
    EXPECT(dec_b.action == LIFE_CONT_ACTION_TRANSFER, "S1 B should transfer");
    EXPECT(dec_a.target_person_id == dec_b.target_person_id, "S1 determinism mismatch");
    EXPECT(dec_a.target_person_id == 7u, "S1 expected spouse selection");
    return 0;
}

static int test_no_eligible_refusal(void)
{
    life_ability_registry reg;
    life_ability_package storage[8];
    life_ability_package ability;
    life_continuation_context ctx;
    life_continuation_decision decision;

    EXPECT(build_registry(&reg, storage, 8u) == 0, "register presets failed");
    EXPECT(life_ability_registry_resolve(&reg, LIFE_ABILITY_HARDCORE_ID, &ability) == 0,
           "resolve hardcore failed");

    ctx.controller_id = 1u;
    ctx.policy_type = LIFE_POLICY_S1;
    ctx.ability = &ability;
    ctx.candidates = NULL;
    ctx.candidate_count = 0u;
    ctx.epistemic = NULL;
    ctx.authority = NULL;
    ctx.allow_blind_delegation = 0u;
    ctx.prereqs.has_facility = 0u;
    ctx.prereqs.has_resources = 0u;
    ctx.prereqs.has_recording = 0u;
    ctx.prereqs.has_drone = 0u;

    EXPECT(life_continuation_decide(&ctx, &decision) == 0, "S1 no-eligible decide failed");
    EXPECT(decision.refusal == LIFE_REFUSAL_NO_ELIGIBLE_PERSON, "expected no eligible refusal");
    EXPECT(decision.action == LIFE_CONT_ACTION_SPECTATOR, "hardcore should fall back to spectator");
    return 0;
}

static int test_softcore_prereq_refusal(void)
{
    life_ability_registry reg;
    life_ability_package storage[8];
    life_ability_package ability;
    life_continuation_context ctx;
    life_continuation_decision decision;

    EXPECT(build_registry(&reg, storage, 8u) == 0, "register presets failed");
    EXPECT(life_ability_registry_resolve(&reg, LIFE_ABILITY_SOFTCORE_ID, &ability) == 0,
           "resolve softcore failed");

    ctx.controller_id = 1u;
    ctx.policy_type = LIFE_POLICY_S2;
    ctx.ability = &ability;
    ctx.candidates = NULL;
    ctx.candidate_count = 0u;
    ctx.epistemic = NULL;
    ctx.authority = NULL;
    ctx.allow_blind_delegation = 0u;
    ctx.prereqs.has_facility = 0u;
    ctx.prereqs.has_resources = 0u;
    ctx.prereqs.has_recording = 0u;
    ctx.prereqs.has_drone = 0u;

    EXPECT(life_continuation_decide(&ctx, &decision) == 0, "S2 prereq decide failed");
    EXPECT(decision.refusal == LIFE_REFUSAL_PREREQ_MISSING_FACILITY,
           "S2 missing facility refusal expected");

    ctx.policy_type = LIFE_POLICY_S3;
    EXPECT(life_continuation_decide(&ctx, &decision) == 0, "S3 prereq decide failed");
    EXPECT(decision.refusal == LIFE_REFUSAL_PREREQ_MISSING_FACILITY,
           "S3 missing drone refusal expected");

    ctx.policy_type = LIFE_POLICY_S4;
    EXPECT(life_continuation_decide(&ctx, &decision) == 0, "S4 prereq decide failed");
    EXPECT(decision.refusal == LIFE_REFUSAL_PREREQ_MISSING_RECORDING,
           "S4 missing recording refusal expected");
    return 0;
}

static int test_lockstep_parity(void)
{
    life_controller_binding storage_a[4];
    life_controller_binding storage_b[4];
    life_controller_binding_set bindings_a;
    life_controller_binding_set bindings_b;
    life_cmd_continuation_select cmd;
    life_refusal_code refusal_a = LIFE_REFUSAL_NONE;
    life_refusal_code refusal_b = LIFE_REFUSAL_NONE;
    u64 person_a = 0u;
    u64 person_b = 0u;

    life_controller_bindings_init(&bindings_a, storage_a, 4u);
    life_controller_bindings_init(&bindings_b, storage_b, 4u);

    cmd.controller_id = 3u;
    cmd.policy_id = LIFE_POLICY_S1;
    cmd.target_person_id = 77u;
    cmd.action = LIFE_CONT_ACTION_TRANSFER;

    EXPECT(life_cmd_continuation_apply_ex(&bindings_a, &cmd, &refusal_a) != 0,
           "apply A should refuse");
    EXPECT(life_cmd_continuation_apply_ex(&bindings_b, &cmd, &refusal_b) != 0,
           "apply B should refuse");
    EXPECT(refusal_a == LIFE_REFUSAL_NOT_IMPLEMENTED, "apply A refusal mismatch");
    EXPECT(refusal_b == LIFE_REFUSAL_NOT_IMPLEMENTED, "apply B refusal mismatch");

    EXPECT(life_controller_bindings_get(&bindings_a, 3u, &person_a) == 0,
           "binding A should remain unset");
    EXPECT(life_controller_bindings_get(&bindings_b, 3u, &person_b) == 0,
           "binding B should remain unset");
    return 0;
}

static int test_epistemic_gating(void)
{
    life_ability_registry reg;
    life_ability_package storage[8];
    life_ability_package ability;
    life_candidate candidates[1];
    life_authority_record auth_records[1];
    life_authority_set auth_set;
    u64 known_ids[1];
    life_epistemic_set epistemic;
    life_continuation_context ctx;
    life_continuation_decision decision;

    EXPECT(build_registry(&reg, storage, 8u) == 0, "register presets failed");
    EXPECT(life_ability_registry_resolve(&reg, LIFE_ABILITY_HARDCORE_ID, &ability) == 0,
           "resolve hardcore failed");

    candidates[0].person_id = 12u;
    candidates[0].reason = LIFE_CANDIDATE_DELEGATED;

    auth_records[0].controller_id = 1u;
    auth_records[0].target_person_id = 12u;
    auth_records[0].source = LIFE_AUTH_CONTRACT;
    auth_set.records = auth_records;
    auth_set.count = 1u;

    known_ids[0] = 99u;
    epistemic.known_person_ids = known_ids;
    epistemic.count = 1u;

    ctx.controller_id = 1u;
    ctx.policy_type = LIFE_POLICY_S1;
    ctx.ability = &ability;
    ctx.candidates = candidates;
    ctx.candidate_count = 1u;
    ctx.epistemic = &epistemic;
    ctx.authority = &auth_set;
    ctx.allow_blind_delegation = 0u;
    ctx.prereqs.has_facility = 0u;
    ctx.prereqs.has_resources = 0u;
    ctx.prereqs.has_recording = 0u;
    ctx.prereqs.has_drone = 0u;

    EXPECT(life_continuation_decide(&ctx, &decision) == 0, "epistemic decide failed");
    EXPECT(decision.refusal == LIFE_REFUSAL_EPISTEMIC_INSUFFICIENT_KNOWLEDGE,
           "expected epistemic refusal");
    return 0;
}

static int test_authority_enforcement(void)
{
    life_ability_registry reg;
    life_ability_package storage[8];
    life_ability_package ability;
    life_candidate candidates[1];
    life_authority_record auth_records[1];
    life_authority_set auth_set;
    u64 known_ids[1];
    life_epistemic_set epistemic;
    life_continuation_context ctx;
    life_continuation_decision decision;

    EXPECT(build_registry(&reg, storage, 8u) == 0, "register presets failed");
    EXPECT(life_ability_registry_resolve(&reg, LIFE_ABILITY_HARDCORE_ID, &ability) == 0,
           "resolve hardcore failed");

    candidates[0].person_id = 33u;
    candidates[0].reason = LIFE_CANDIDATE_ORG_MEMBER;

    auth_records[0].controller_id = 1u;
    auth_records[0].target_person_id = 55u;
    auth_records[0].source = LIFE_AUTH_ORG;
    auth_set.records = auth_records;
    auth_set.count = 1u;

    known_ids[0] = 33u;
    epistemic.known_person_ids = known_ids;
    epistemic.count = 1u;

    ctx.controller_id = 1u;
    ctx.policy_type = LIFE_POLICY_S1;
    ctx.ability = &ability;
    ctx.candidates = candidates;
    ctx.candidate_count = 1u;
    ctx.epistemic = &epistemic;
    ctx.authority = &auth_set;
    ctx.allow_blind_delegation = 0u;
    ctx.prereqs.has_facility = 0u;
    ctx.prereqs.has_resources = 0u;
    ctx.prereqs.has_recording = 0u;
    ctx.prereqs.has_drone = 0u;

    EXPECT(life_continuation_decide(&ctx, &decision) == 0, "authority decide failed");
    EXPECT(decision.refusal == LIFE_REFUSAL_INSUFFICIENT_AUTHORITY,
           "expected authority refusal");
    return 0;
}

static int test_no_fabrication(void)
{
    life_ability_registry reg;
    life_ability_package storage[8];
    life_ability_package ability;
    life_continuation_context ctx;
    life_continuation_decision decision;

    EXPECT(build_registry(&reg, storage, 8u) == 0, "register presets failed");
    EXPECT(life_ability_registry_resolve(&reg, LIFE_ABILITY_SOFTCORE_ID, &ability) == 0,
           "resolve softcore failed");

    ctx.controller_id = 1u;
    ctx.policy_type = LIFE_POLICY_S2;
    ctx.ability = &ability;
    ctx.candidates = NULL;
    ctx.candidate_count = 0u;
    ctx.epistemic = NULL;
    ctx.authority = NULL;
    ctx.allow_blind_delegation = 0u;
    ctx.prereqs.has_facility = 1u;
    ctx.prereqs.has_resources = 1u;
    ctx.prereqs.has_recording = 1u;
    ctx.prereqs.has_drone = 1u;

    EXPECT(life_continuation_decide(&ctx, &decision) == 0, "S2 decide failed");
    EXPECT(decision.action == LIFE_CONT_ACTION_PENDING, "expected pending action");
    EXPECT(decision.target_person_id == 0u, "no fabricated target expected");
    return 0;
}

int main(void)
{
    if (test_ability_inheritance() != 0) {
        return 1;
    }
    if (test_s1_selection_determinism() != 0) {
        return 1;
    }
    if (test_no_eligible_refusal() != 0) {
        return 1;
    }
    if (test_softcore_prereq_refusal() != 0) {
        return 1;
    }
    if (test_lockstep_parity() != 0) {
        return 1;
    }
    if (test_epistemic_gating() != 0) {
        return 1;
    }
    if (test_authority_enforcement() != 0) {
        return 1;
    }
    if (test_no_fabrication() != 0) {
        return 1;
    }
    return 0;
}
