/*
FILE: client/presentation/render_prep_system.h
MODULE: Dominium
LAYER / SUBSYSTEM: Client / presentation
RESPONSIBILITY: Render prep Work IR emitter (derived, IR-only).
ALLOWED DEPENDENCIES: engine/include/**, game/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Emission order and degradation are deterministic.
*/
#ifndef DOMINIUM_CLIENT_PRESENTATION_RENDER_PREP_SYSTEM_H
#define DOMINIUM_CLIENT_PRESENTATION_RENDER_PREP_SYSTEM_H

#include "dominium/execution/system_iface.h"
#include "frame_graph_builder.h"

enum dom_render_prep_op {
    DOM_RENDER_PREP_OP_BUILD_VISIBILITY_MASK = 1,
    DOM_RENDER_PREP_OP_BUILD_INSTANCE_LIST = 2,
    DOM_RENDER_PREP_OP_BUILD_DRAW_LIST = 3
};

typedef struct dom_render_prep_buffers {
    u64 visibility_buffer_id;
    u64 instance_buffer_id;
    u64 draw_list_buffer_id;
} dom_render_prep_buffers;

typedef struct dom_render_prep_task_params {
    u32 op;
    u32 fidelity;
    u32 pass_count;
    u32 flags;
    u64 frame_graph_id;
} dom_render_prep_task_params;

typedef enum dom_render_prep_migration_state {
    DOM_RENDER_PREP_STATE_IR_ONLY = 3
} dom_render_prep_migration_state;

class RenderPrepSystem : public ISimSystem {
public:
    RenderPrepSystem();

    int init(const dom_render_prep_inputs* inputs,
             const dom_render_prep_buffers* buffers);

    void set_inputs(const dom_render_prep_inputs* inputs);
    void set_buffers(const dom_render_prep_buffers* buffers);
    void set_presentation_enabled(d_bool enabled);
    void set_next_due_tick(dom_act_time_t tick);

    dom_render_prep_migration_state migration_state() const;
    u32 last_emitted_task_count() const;
    u64 last_frame_id() const;

    virtual u64 system_id() const;
    virtual d_bool is_sim_affecting() const;
    virtual const u32* law_targets(u32* out_count) const;
    virtual dom_act_time_t get_next_due_tick() const;
    virtual int emit_tasks(dom_act_time_t act_now,
                           dom_act_time_t act_target,
                           dom_work_graph_builder* graph_builder,
                           dom_access_set_builder* access_builder);
    virtual void degrade(dom_fidelity_tier tier, u32 reason);

private:
    u64 system_id_;
    u32 law_targets_[2];
    u32 law_target_count_;
    u64 law_scope_ref_;
    dom_fidelity_tier tier_;
    dom_act_time_t next_due_tick_;
    d_bool presentation_enabled_;
    dom_render_prep_migration_state migration_state_;
    dom_frame_graph_builder graph_builder_;
    dom_frame_graph_desc last_graph_;
    dom_render_prep_task_params params_[3];
    u32 last_emitted_task_count_;

    const dom_render_prep_inputs* inputs_;
    const dom_render_prep_buffers* buffers_;
};

#endif /* DOMINIUM_CLIENT_PRESENTATION_RENDER_PREP_SYSTEM_H */
