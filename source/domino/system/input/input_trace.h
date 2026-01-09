/*
FILE: source/domino/system/input/input_trace.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/input/input_trace
RESPONSIBILITY: Deterministic input trace normalization and hashing for backend conformance tests.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Normalization and hashing must be stable across platforms.
VERSIONING / ABI / DATA FORMAT NOTES: Internal header, not part of public ABI.
*/
#ifndef D_SYS_INPUT_TRACE_H
#define D_SYS_INPUT_TRACE_H

#include "domino/core/types.h"
#include "system/d_system_input.h"

#ifdef __cplusplus
extern "C" {
#endif

#define D_SYS_INPUT_TRACE_MAX_EVENTS 256u

typedef struct d_sys_input_trace {
    d_sys_event events[D_SYS_INPUT_TRACE_MAX_EVENTS];
    u32 count;
} d_sys_input_trace;

void d_sys_input_trace_clear(d_sys_input_trace* trace);
int  d_sys_input_trace_record(d_sys_input_trace* trace,
                              const d_sys_event* events,
                              u32 count);
int  d_sys_input_trace_play(const d_sys_input_trace* trace,
                            const char* backend_name,
                            d_sys_event* out_events,
                            u32 max_events,
                            u32* out_count);
u64  d_sys_input_trace_hash(const d_sys_event* events, u32 count);
void d_sys_input_trace_normalize(d_sys_event* events, u32 count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_SYS_INPUT_TRACE_H */
