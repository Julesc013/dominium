/*
FILE: source/dominium/common/dom_profiler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_profiler
RESPONSIBILITY: Lightweight profiling for runtime subsystems (non-authoritative).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, C89/C++98 headers.
FORBIDDEN DEPENDENCIES: OS headers; sim-affecting logic.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; profiling must not affect sim results.
*/
#ifndef DOM_PROFILER_H
#define DOM_PROFILER_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_PROFILER_FRAME_VERSION = 1u
};

typedef enum dom_profiler_zone {
    DOM_PROFILER_ZONE_SIM_TICK = 0,
    DOM_PROFILER_ZONE_LANE_UPDATE = 1,
    DOM_PROFILER_ZONE_ORBIT_UPDATE = 2,
    DOM_PROFILER_ZONE_SURFACE_STREAM = 3,
    DOM_PROFILER_ZONE_DERIVED_PUMP = 4,
    DOM_PROFILER_ZONE_AI = 5,
    DOM_PROFILER_ZONE_NET_PUMP = 6,
    DOM_PROFILER_ZONE_RENDER_SUBMIT = 7,
    DOM_PROFILER_ZONE_INPUT = 8,
    DOM_PROFILER_ZONE_COUNT = 9
} dom_profiler_zone;

typedef struct dom_profiler_zone_stats {
    u64 total_us;
    u64 last_us;
    u32 hits;
} dom_profiler_zone_stats;

typedef struct dom_profiler_frame {
    u32 struct_size;
    u32 struct_version;
    u64 frame_us;
    dom_profiler_zone_stats zones[DOM_PROFILER_ZONE_COUNT];
} dom_profiler_frame;

void dom_profiler_reset(void);
void dom_profiler_begin_frame(void);
void dom_profiler_end_frame(void);

u64 dom_profiler_begin_zone(u32 zone);
void dom_profiler_end_zone(u32 zone, u64 token);

int dom_profiler_get_last_frame(dom_profiler_frame *out_frame);
const char *dom_profiler_zone_name(u32 zone);

int dom_profiler_write_json(const dom_profiler_frame *frame, const char *path);

#ifdef __cplusplus
} /* extern "C" */
#endif

#ifdef __cplusplus
struct dom_profiler_scope {
    u32 zone;
    u64 start;
    explicit dom_profiler_scope(u32 z)
        : zone(z),
          start(dom_profiler_begin_zone(z)) {}
    ~dom_profiler_scope() {
        dom_profiler_end_zone(zone, start);
    }
};

#define DOM_PROFILE_SCOPE(zone_id) \
    dom_profiler_scope dom_profiler_scope_##__LINE__(zone_id)
#else
#define DOM_PROFILE_SCOPE(zone_id) do { (void)(zone_id); } while (0)
#endif

#endif /* DOM_PROFILER_H */
