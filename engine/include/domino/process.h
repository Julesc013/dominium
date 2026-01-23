/*
FILE: include/domino/process.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / process
RESPONSIBILITY: Defines process classes, descriptors, and hook interfaces.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Process scheduling/execution MUST be deterministic given the same inputs.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.
*/
#ifndef DOMINO_PROCESS_H
#define DOMINO_PROCESS_H

#include "domino/dnumeric.h"
#include "domino/capability.h"
#include "domino/authority.h"
#include "domino/domain.h"
#include "domino/provenance.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dom_process_id: Stable identifier for a process definition. */
typedef u64 dom_process_id;

/* dom_process_class: Process classification (mutations are class-aware). */
typedef enum dom_process_class {
    DOM_PROCESS_TRANSFORMATIVE = 0,
    DOM_PROCESS_TRANSACTIONAL = 1,
    DOM_PROCESS_EPISTEMIC = 2
} dom_process_class;

/* dom_process_io_kind: Input/output/waste classification. */
typedef enum dom_process_io_kind {
    DOM_PROCESS_IO_INPUT = 0,
    DOM_PROCESS_IO_OUTPUT = 1,
    DOM_PROCESS_IO_WASTE = 2
} dom_process_io_kind;

/* dom_process_io_desc: Declarative IO slot for a process. */
typedef struct dom_process_io_desc {
    u32               io_id;       /* data-defined slot id */
    u32               unit_id;     /* data-defined unit id */
    u32               quantity_q16; /* fixed-point quantity or cost */
    u32               flags;
    u32               kind;        /* dom_process_io_kind */
} dom_process_io_desc;

/* dom_process_cost: Declarative time/cost for a process. */
typedef struct dom_process_cost {
    SimTick duration_ticks;
    u32     cost_units;
} dom_process_cost;

/* dom_process_desc: Descriptor for a process definition. */
typedef struct dom_process_desc {
    dom_process_id          id;
    dom_process_class       process_class;

    const dom_process_io_desc* inputs;
    u32                        input_count;
    const dom_process_io_desc* outputs;
    u32                        output_count;
    const dom_process_io_desc* waste;
    u32                        waste_count;

    dom_process_cost        cost;
    dom_capability_set_view required_caps;
    dom_authority_scope     required_authority;

    const dom_domain_volume_ref* applicable_domains;
    u32                         domain_count;

    const u32*             failure_mode_ids; /* data-defined */
    u32                    failure_mode_count;
} dom_process_desc;

/* dom_process_schedule_context: Read-only scheduling inputs. */
typedef struct dom_process_schedule_context {
    SimTick            now_tick;
    const dom_authority_token* authority;
    dom_provenance_id provenance_id;
} dom_process_schedule_context;

/* dom_process_exec_context: Read-only execution inputs. */
typedef struct dom_process_exec_context {
    SimTick                 now_tick;
    const dom_authority_token* authority;
    dom_provenance_id       provenance_id;
} dom_process_exec_context;

/* dom_process_exec_result: Execution outcome metadata. */
typedef struct dom_process_exec_result {
    d_bool   ok;
    u32      failure_mode_id; /* 0 when ok */
    u32      cost_units;
} dom_process_exec_result;

/* Scheduling hook signature. */
typedef int (*dom_process_schedule_fn)(const dom_process_desc* desc,
                                       const dom_process_schedule_context* ctx,
                                       void* user);

/* Execution hook signature. */
typedef int (*dom_process_execute_fn)(const dom_process_desc* desc,
                                      const dom_process_exec_context* ctx,
                                      dom_process_exec_result* out_result,
                                      void* user);

/* Audit hook signature. */
typedef void (*dom_process_audit_fn)(const dom_process_desc* desc,
                                     const dom_process_exec_result* result,
                                     void* user);

/* dom_process_hooks: Bundle of scheduling/execution/audit hooks. */
typedef struct dom_process_hooks {
    dom_process_schedule_fn schedule;
    dom_process_execute_fn  execute;
    dom_process_audit_fn    audit;
    void*                   user;
} dom_process_hooks;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_PROCESS_H */
