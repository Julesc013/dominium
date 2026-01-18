/*
CIV3 knowledge and technology tests.
*/
#include "dominium/rules/knowledge/diffusion_model.h"
#include "dominium/rules/knowledge/institution_knowledge_binding.h"
#include "dominium/rules/knowledge/knowledge_item.h"
#include "dominium/rules/knowledge/research_process.h"
#include "dominium/rules/knowledge/secrecy_controls.h"
#include "dominium/rules/technology/tech_activation.h"
#include "dominium/rules/technology/tech_prerequisites.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct completion_log {
    u64 ids[8];
    u32 count;
} completion_log;

static int log_completion(void* user, const research_process* process)
{
    completion_log* log = (completion_log*)user;
    if (!log || !process) {
        return -1;
    }
    if (log->count < 8u) {
        log->ids[log->count++] = process->process_id;
    }
    return 0;
}

static int run_research_order_case(int reverse, completion_log* out_log)
{
    knowledge_item knowledge_storage[4];
    knowledge_registry knowledge;
    research_process proc_storage[4];
    research_process_registry reg;
    knowledge_institution inst_storage[2];
    knowledge_institution_registry inst_reg;
    dom_time_event events[16];
    dg_due_entry entries[4];
    research_due_user users[4];
    research_scheduler sched;
    research_completion_hook hook;
    research_process* p1;
    research_process* p2;

    knowledge_registry_init(&knowledge, knowledge_storage, 4u);
    EXPECT(knowledge_register(&knowledge, 11u, KNOW_TYPE_THEORY, 0u) == 0, "knowledge 11");
    EXPECT(knowledge_register(&knowledge, 12u, KNOW_TYPE_THEORY, 0u) == 0, "knowledge 12");

    knowledge_institution_registry_init(&inst_reg, inst_storage, 2u);
    EXPECT(knowledge_institution_register(&inst_reg, 100u, KNOW_INST_LAB, 4u, 0u) == 0, "inst reg");

    research_process_registry_init(&reg, proc_storage, 4u);
    EXPECT(research_process_register(&reg, 1u, 100u, 5u, 10u) == 0, "proc 1");
    EXPECT(research_process_add_output(&reg, 1u, 11u) == 0, "proc 1 output");
    EXPECT(research_process_register(&reg, 2u, 100u, 5u, 10u) == 0, "proc 2");
    EXPECT(research_process_add_output(&reg, 2u, 12u) == 0, "proc 2 output");

    EXPECT(research_scheduler_init(&sched, events, 16u, entries, users, 4u, 0u,
                                   &reg, &knowledge, &inst_reg) == 0, "sched init");
    hook.on_complete = log_completion;
    hook.user = out_log;
    research_scheduler_set_completion_hook(&sched, &hook);

    p1 = research_process_find(&reg, 1u);
    p2 = research_process_find(&reg, 2u);
    EXPECT(p1 && p2, "proc find");
    if (reverse) {
        EXPECT(research_scheduler_register(&sched, p2) == 0, "register p2");
        EXPECT(research_scheduler_register(&sched, p1) == 0, "register p1");
    } else {
        EXPECT(research_scheduler_register(&sched, p1) == 0, "register p1");
        EXPECT(research_scheduler_register(&sched, p2) == 0, "register p2");
    }

    EXPECT(research_scheduler_advance(&sched, 10u, 0) == 0, "advance");
    return 0;
}

static int test_research_completion_determinism(void)
{
    completion_log log_a;
    completion_log log_b;
    memset(&log_a, 0, sizeof(log_a));
    memset(&log_b, 0, sizeof(log_b));

    EXPECT(run_research_order_case(0, &log_a) == 0, "run order a");
    EXPECT(run_research_order_case(1, &log_b) == 0, "run order b");

    EXPECT(log_a.count == 2u, "log a count");
    EXPECT(log_b.count == 2u, "log b count");
    EXPECT(log_a.ids[0] == log_b.ids[0], "order mismatch 0");
    EXPECT(log_a.ids[1] == log_b.ids[1], "order mismatch 1");
    EXPECT(log_a.ids[0] == 1u && log_a.ids[1] == 2u, "unexpected completion order");
    return 0;
}

static int test_research_batch_equivalence(void)
{
    knowledge_item knowledge_step_storage[2];
    knowledge_item knowledge_batch_storage[2];
    knowledge_registry knowledge_step;
    knowledge_registry knowledge_batch;
    research_process proc_step_storage[2];
    research_process proc_batch_storage[2];
    research_process_registry reg_step;
    research_process_registry reg_batch;
    knowledge_institution inst_storage[1];
    knowledge_institution_registry inst_reg;
    dom_time_event events_step[8];
    dom_time_event events_batch[8];
    dg_due_entry entries_step[2];
    dg_due_entry entries_batch[2];
    research_due_user users_step[2];
    research_due_user users_batch[2];
    research_scheduler sched_step;
    research_scheduler sched_batch;
    research_process* proc_step;
    research_process* proc_batch;

    knowledge_registry_init(&knowledge_step, knowledge_step_storage, 2u);
    knowledge_registry_init(&knowledge_batch, knowledge_batch_storage, 2u);
    EXPECT(knowledge_register(&knowledge_step, 21u, KNOW_TYPE_METHOD, 0u) == 0, "knowledge 21");
    EXPECT(knowledge_register(&knowledge_batch, 21u, KNOW_TYPE_METHOD, 0u) == 0, "knowledge 21");

    knowledge_institution_registry_init(&inst_reg, inst_storage, 1u);
    EXPECT(knowledge_institution_register(&inst_reg, 200u, KNOW_INST_LAB, 2u, 0u) == 0, "inst reg");

    research_process_registry_init(&reg_step, proc_step_storage, 2u);
    research_process_registry_init(&reg_batch, proc_batch_storage, 2u);
    EXPECT(research_process_register(&reg_step, 3u, 200u, 2u, 6u) == 0, "proc 3 step");
    EXPECT(research_process_add_output(&reg_step, 3u, 21u) == 0, "proc 3 step output");
    EXPECT(research_process_register(&reg_batch, 3u, 200u, 2u, 6u) == 0, "proc 3 batch");
    EXPECT(research_process_add_output(&reg_batch, 3u, 21u) == 0, "proc 3 batch output");
    proc_step = research_process_find(&reg_step, 3u);
    proc_batch = research_process_find(&reg_batch, 3u);
    EXPECT(proc_step != 0 && proc_batch != 0, "proc find");

    EXPECT(research_scheduler_init(&sched_step, events_step, 8u, entries_step, users_step, 2u, 0u,
                                   &reg_step, &knowledge_step, &inst_reg) == 0, "step init");
    EXPECT(research_scheduler_init(&sched_batch, events_batch, 8u, entries_batch, users_batch, 2u, 0u,
                                   &reg_batch, &knowledge_batch, &inst_reg) == 0, "batch init");
    EXPECT(research_scheduler_register(&sched_step, proc_step) == 0, "step register");
    EXPECT(research_scheduler_register(&sched_batch, proc_batch) == 0, "batch register");

    EXPECT(research_scheduler_advance(&sched_step, 2u, 0) == 0, "step advance 2");
    EXPECT(research_scheduler_advance(&sched_step, 6u, 0) == 0, "step advance 6");
    EXPECT(research_scheduler_advance(&sched_batch, 6u, 0) == 0, "batch advance 6");
    EXPECT(proc_step->status == RESEARCH_COMPLETED, "proc completed step");
    EXPECT(proc_batch->status == RESEARCH_COMPLETED, "proc completed batch");
    EXPECT(knowledge_find(&knowledge_step, 21u)->completeness == KNOWLEDGE_COMPLETENESS_MAX,
           "knowledge complete step");
    EXPECT(knowledge_find(&knowledge_batch, 21u)->completeness == KNOWLEDGE_COMPLETENESS_MAX,
           "knowledge complete batch");
    return 0;
}

static int test_diffusion_delay_and_secrecy(void)
{
    knowledge_diffusion_event event_storage[2];
    knowledge_diffusion_registry reg;
    knowledge_institution inst_storage[2];
    knowledge_institution_registry inst_reg;
    knowledge_secrecy_policy secrecy_storage[2];
    knowledge_secrecy_registry secrecy_reg;
    dom_time_event events[8];
    dg_due_entry entries[2];
    knowledge_diffusion_due_user users[2];
    knowledge_diffusion_scheduler sched;
    knowledge_diffusion_event* ev;

    knowledge_institution_registry_init(&inst_reg, inst_storage, 2u);
    EXPECT(knowledge_institution_register(&inst_reg, 300u, KNOW_INST_ARCHIVE, 4u, 0u) == 0,
           "inst reg");
    knowledge_secrecy_registry_init(&secrecy_reg, secrecy_storage, 2u);
    EXPECT(knowledge_secrecy_register(&secrecy_reg, 7u, 0u, 0u) == 0, "secrecy reg");

    knowledge_diffusion_registry_init(&reg, event_storage, 2u);
    EXPECT(knowledge_diffusion_register(&reg, 1u, 99u, 10u, 300u, 0u, 1u, 7u,
                                        100u, 0u, 0u) == 0, "diff reg");
    EXPECT(knowledge_diffusion_register(&reg, 2u, 88u, 10u, 300u, 0u, 1u, 7u,
                                        100u, 0u, 7u) == 0, "diff reg 2");

    EXPECT(knowledge_diffusion_scheduler_init(&sched, events, 8u, entries, users, 2u, 0u,
                                              &reg, &inst_reg, &secrecy_reg) == 0,
           "diff sched init");

    ev = knowledge_diffusion_find(&reg, 1u);
    EXPECT(ev != 0, "find event 1");
    EXPECT(knowledge_diffusion_scheduler_register(&sched, ev) == 0, "register ev1");
    ev = knowledge_diffusion_find(&reg, 2u);
    EXPECT(ev != 0, "find event 2");
    EXPECT(knowledge_diffusion_scheduler_register(&sched, ev) == 0, "register ev2");

    EXPECT(knowledge_diffusion_scheduler_advance(&sched, 6u) == 0, "advance 6");
    EXPECT(knowledge_institution_knows(&inst_reg, 300u, 99u) == 0, "premature delivery");
    EXPECT(knowledge_diffusion_scheduler_advance(&sched, 7u) == 0, "advance 7");
    EXPECT(knowledge_institution_knows(&inst_reg, 300u, 99u) == 1, "delivery missing");
    EXPECT(knowledge_institution_knows(&inst_reg, 300u, 88u) == 0, "secrecy leak");
    return 0;
}

static int test_tech_activation_gate(void)
{
    knowledge_item knowledge_storage[2];
    knowledge_registry knowledge;
    tech_prerequisite prereq_storage[4];
    tech_prereq_registry prereqs;
    tech_activation activation_storage[2];
    tech_activation_registry activations;

    knowledge_registry_init(&knowledge, knowledge_storage, 2u);
    EXPECT(knowledge_register(&knowledge, 55u, KNOW_TYPE_DESIGN, 0u) == 0, "knowledge reg");
    EXPECT(knowledge_set_completeness(&knowledge, 55u, 500u) == 0, "knowledge set");

    tech_prereq_registry_init(&prereqs, prereq_storage, 4u);
    EXPECT(tech_prereq_register(&prereqs, 100u, 55u, 800u) == 0, "prereq reg");

    tech_activation_registry_init(&activations, activation_storage, 2u);
    EXPECT(tech_activation_request(&activations, &prereqs, &knowledge, 100u, 1u, 10u, 1) != 0,
           "activation should fail");
    EXPECT(knowledge_set_completeness(&knowledge, 55u, KNOWLEDGE_COMPLETENESS_MAX) == 0,
           "knowledge max");
    EXPECT(tech_activation_request(&activations, &prereqs, &knowledge, 100u, 1u, 10u, 1) == 0,
           "activation should succeed");
    EXPECT(tech_activation_is_active(&activations, 100u, 1u) == 1, "activation not active");
    return 0;
}

static int test_no_global_iteration(void)
{
    knowledge_item knowledge_storage[2];
    knowledge_registry knowledge;
    research_process proc_storage[2];
    research_process_registry reg;
    knowledge_institution inst_storage[1];
    knowledge_institution_registry inst_reg;
    dom_time_event events[8];
    dg_due_entry entries[2];
    research_due_user users[2];
    research_scheduler sched;
    research_process* p1;
    research_process* p2;

    knowledge_registry_init(&knowledge, knowledge_storage, 2u);
    EXPECT(knowledge_register(&knowledge, 77u, KNOW_TYPE_METHOD, 0u) == 0, "knowledge 77");
    EXPECT(knowledge_register(&knowledge, 78u, KNOW_TYPE_METHOD, 0u) == 0, "knowledge 78");

    knowledge_institution_registry_init(&inst_reg, inst_storage, 1u);
    EXPECT(knowledge_institution_register(&inst_reg, 400u, KNOW_INST_LAB, 2u, 0u) == 0,
           "inst reg");

    research_process_registry_init(&reg, proc_storage, 2u);
    EXPECT(research_process_register(&reg, 10u, 400u, 5u, 50u) == 0, "proc 10");
    EXPECT(research_process_add_output(&reg, 10u, 77u) == 0, "proc 10 output");
    EXPECT(research_process_register(&reg, 11u, 400u, 100u, 150u) == 0, "proc 11");
    EXPECT(research_process_add_output(&reg, 11u, 78u) == 0, "proc 11 output");

    EXPECT(research_scheduler_init(&sched, events, 8u, entries, users, 2u, 0u,
                                   &reg, &knowledge, &inst_reg) == 0, "sched init");
    p1 = research_process_find(&reg, 10u);
    p2 = research_process_find(&reg, 11u);
    EXPECT(research_scheduler_register(&sched, p1) == 0, "register p1");
    EXPECT(research_scheduler_register(&sched, p2) == 0, "register p2");

    EXPECT(research_scheduler_advance(&sched, 5u, 0) == 0, "advance 5");
    EXPECT(sched.processed_last == 1u, "processed unexpected count");
    EXPECT(p2->status == RESEARCH_PENDING, "p2 should be pending");
    return 0;
}

int main(void)
{
    if (test_research_completion_determinism() != 0) return 1;
    if (test_research_batch_equivalence() != 0) return 1;
    if (test_diffusion_delay_and_secrecy() != 0) return 1;
    if (test_tech_activation_gate() != 0) return 1;
    if (test_no_global_iteration() != 0) return 1;
    return 0;
}
