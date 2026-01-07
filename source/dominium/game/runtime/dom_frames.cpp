/*
FILE: source/dominium/game/runtime/dom_frames.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/frames
RESPONSIBILITY: Reference frame registry scaffolding (tree + transform stubs).
*/
#include "runtime/dom_frames.h"

#include <stddef.h>
#include <vector>

#include "domino/core/dom_deterministic_math.h"

namespace {

struct FrameEntry {
    dom_frame_id id;
    dom_frame_id parent_id;
    u32 kind;
    u64 body_id;
    dom_posseg_q16 origin_offset;
    u64 rotation_period_ticks;
    u64 rotation_epoch_tick;
    q16_16 rotation_phase_turns;
};

static int find_frame_index(const std::vector<FrameEntry> &frames, dom_frame_id id) {
    size_t i;
    for (i = 0u; i < frames.size(); ++i) {
        if (frames[i].id == id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_sorted_frame(std::vector<FrameEntry> &frames, const FrameEntry &entry) {
    size_t i = 0u;
    while (i < frames.size() && frames[i].id < entry.id) {
        ++i;
    }
    frames.insert(frames.begin() + (std::vector<FrameEntry>::difference_type)i, entry);
}

static dom_posseg_q16 posseg_add(const dom_posseg_q16 &a, const dom_posseg_q16 &b) {
    dom_posseg_q16 out;
    u32 i;
    for (i = 0u; i < 3u; ++i) {
        out.seg[i] = a.seg[i] + b.seg[i];
        out.loc[i] = d_q16_16_add(a.loc[i], b.loc[i]);
    }
    return out;
}

static dom_posseg_q16 posseg_sub(const dom_posseg_q16 &a, const dom_posseg_q16 &b) {
    dom_posseg_q16 out;
    u32 i;
    for (i = 0u; i < 3u; ++i) {
        out.seg[i] = a.seg[i] - b.seg[i];
        out.loc[i] = d_q16_16_sub(a.loc[i], b.loc[i]);
    }
    return out;
}

static q16_16 rotation_angle_turns(const FrameEntry &frame, dom_tick tick) {
    q16_16 angle = 0;
    if (frame.rotation_period_ticks == 0ull) {
        angle = frame.rotation_phase_turns;
    } else {
        u64 base_tick = (tick >= frame.rotation_epoch_tick)
                            ? (tick - frame.rotation_epoch_tick)
                            : 0ull;
        u64 rem = base_tick % frame.rotation_period_ticks;
        u64 angle_q16 = (rem << 16) / frame.rotation_period_ticks;
        angle = (q16_16)angle_q16;
        angle = (q16_16)(angle + frame.rotation_phase_turns);
    }
    return dom_angle_normalize_q16(angle);
}

static void rotate_vec3(const dom_vec3_q16 &in, q16_16 angle, int inverse, dom_vec3_q16 *out) {
    q16_16 cosv = dom_cos_q16(angle);
    q16_16 sinv = dom_sin_q16(angle);
    if (inverse) {
        sinv = (q16_16)(-sinv);
    }
    out->v[0] = d_q16_16_sub(d_q16_16_mul(in.v[0], cosv),
                            d_q16_16_mul(in.v[1], sinv));
    out->v[1] = d_q16_16_add(d_q16_16_mul(in.v[0], sinv),
                            d_q16_16_mul(in.v[1], cosv));
    out->v[2] = in.v[2];
}

static int transform_parent_to_child_pos(const FrameEntry &parent,
                                         const FrameEntry &child,
                                         const dom_posseg_q16 *pos,
                                         dom_tick tick,
                                         dom_posseg_q16 *out_pos) {
    (void)parent;
    if (child.kind == DOM_FRAME_KIND_BODY_CENTERED_INERTIAL &&
        parent.kind == DOM_FRAME_KIND_INERTIAL_BARYCENTRIC) {
        *out_pos = posseg_sub(*pos, child.origin_offset);
        return DOM_FRAMES_OK;
    }
    if (child.kind == DOM_FRAME_KIND_BODY_FIXED &&
        parent.kind == DOM_FRAME_KIND_BODY_CENTERED_INERTIAL &&
        child.body_id == parent.body_id) {
        dom_vec3_q16 v;
        dom_vec3_q16 rotated;
        q16_16 angle = rotation_angle_turns(child, tick);
        v.v[0] = pos->loc[0];
        v.v[1] = pos->loc[1];
        v.v[2] = pos->loc[2];
        rotate_vec3(v, angle, 0, &rotated);
        *out_pos = *pos;
        out_pos->loc[0] = rotated.v[0];
        out_pos->loc[1] = rotated.v[1];
        out_pos->loc[2] = rotated.v[2];
        return DOM_FRAMES_OK;
    }
    return DOM_FRAMES_NOT_IMPLEMENTED;
}

static int transform_child_to_parent_pos(const FrameEntry &child,
                                         const FrameEntry &parent,
                                         const dom_posseg_q16 *pos,
                                         dom_tick tick,
                                         dom_posseg_q16 *out_pos) {
    (void)parent;
    if (child.kind == DOM_FRAME_KIND_BODY_CENTERED_INERTIAL &&
        parent.kind == DOM_FRAME_KIND_INERTIAL_BARYCENTRIC) {
        *out_pos = posseg_add(*pos, child.origin_offset);
        return DOM_FRAMES_OK;
    }
    if (child.kind == DOM_FRAME_KIND_BODY_FIXED &&
        parent.kind == DOM_FRAME_KIND_BODY_CENTERED_INERTIAL &&
        child.body_id == parent.body_id) {
        dom_vec3_q16 v;
        dom_vec3_q16 rotated;
        q16_16 angle = rotation_angle_turns(child, tick);
        v.v[0] = pos->loc[0];
        v.v[1] = pos->loc[1];
        v.v[2] = pos->loc[2];
        rotate_vec3(v, angle, 1, &rotated);
        *out_pos = *pos;
        out_pos->loc[0] = rotated.v[0];
        out_pos->loc[1] = rotated.v[1];
        out_pos->loc[2] = rotated.v[2];
        return DOM_FRAMES_OK;
    }
    return DOM_FRAMES_NOT_IMPLEMENTED;
}

static int transform_parent_to_child_vel(const FrameEntry &parent,
                                         const FrameEntry &child,
                                         const dom_vec3_q16 *vel,
                                         dom_tick tick,
                                         dom_vec3_q16 *out_vel) {
    if (child.kind == DOM_FRAME_KIND_BODY_FIXED &&
        parent.kind == DOM_FRAME_KIND_BODY_CENTERED_INERTIAL &&
        child.body_id == parent.body_id) {
        q16_16 angle = rotation_angle_turns(child, tick);
        rotate_vec3(*vel, angle, 0, out_vel);
        return DOM_FRAMES_OK;
    }
    if (child.kind == DOM_FRAME_KIND_BODY_CENTERED_INERTIAL &&
        parent.kind == DOM_FRAME_KIND_INERTIAL_BARYCENTRIC) {
        *out_vel = *vel;
        return DOM_FRAMES_OK;
    }
    return DOM_FRAMES_NOT_IMPLEMENTED;
}

static int transform_child_to_parent_vel(const FrameEntry &child,
                                         const FrameEntry &parent,
                                         const dom_vec3_q16 *vel,
                                         dom_tick tick,
                                         dom_vec3_q16 *out_vel) {
    if (child.kind == DOM_FRAME_KIND_BODY_FIXED &&
        parent.kind == DOM_FRAME_KIND_BODY_CENTERED_INERTIAL &&
        child.body_id == parent.body_id) {
        q16_16 angle = rotation_angle_turns(child, tick);
        rotate_vec3(*vel, angle, 1, out_vel);
        return DOM_FRAMES_OK;
    }
    if (child.kind == DOM_FRAME_KIND_BODY_CENTERED_INERTIAL &&
        parent.kind == DOM_FRAME_KIND_INERTIAL_BARYCENTRIC) {
        *out_vel = *vel;
        return DOM_FRAMES_OK;
    }
    return DOM_FRAMES_NOT_IMPLEMENTED;
}

} // namespace

struct dom_frames {
    std::vector<FrameEntry> frames;
};

dom_frames *dom_frames_create(void) {
    return new dom_frames();
}

void dom_frames_destroy(dom_frames *frames) {
    if (!frames) {
        return;
    }
    delete frames;
}

int dom_frames_register(dom_frames *frames, const dom_frame_desc *desc) {
    FrameEntry entry;
    if (!frames || !desc) {
        return DOM_FRAMES_INVALID_ARGUMENT;
    }
    if (desc->id == 0u) {
        return DOM_FRAMES_INVALID_ARGUMENT;
    }
    if (desc->kind < DOM_FRAME_KIND_INERTIAL_BARYCENTRIC ||
        desc->kind > DOM_FRAME_KIND_BODY_FIXED) {
        return DOM_FRAMES_INVALID_ARGUMENT;
    }
    if ((desc->kind == DOM_FRAME_KIND_BODY_CENTERED_INERTIAL ||
         desc->kind == DOM_FRAME_KIND_BODY_FIXED) &&
        desc->body_id == 0ull) {
        return DOM_FRAMES_INVALID_ARGUMENT;
    }
    if (find_frame_index(frames->frames, desc->id) >= 0) {
        return DOM_FRAMES_DUPLICATE_ID;
    }
    entry.id = desc->id;
    entry.parent_id = desc->parent_id;
    entry.kind = desc->kind;
    entry.body_id = desc->body_id;
    entry.origin_offset = desc->origin_offset;
    entry.rotation_period_ticks = desc->rotation_period_ticks;
    entry.rotation_epoch_tick = desc->rotation_epoch_tick;
    entry.rotation_phase_turns = desc->rotation_phase_turns;
    insert_sorted_frame(frames->frames, entry);
    return DOM_FRAMES_OK;
}

int dom_frames_validate(const dom_frames *frames) {
    size_t i;
    if (!frames) {
        return DOM_FRAMES_INVALID_ARGUMENT;
    }
    for (i = 0u; i < frames->frames.size(); ++i) {
        const FrameEntry &entry = frames->frames[i];
        dom_frame_id current = entry.id;
        dom_frame_id parent = entry.parent_id;
        std::vector<dom_frame_id> visited;

        visited.push_back(current);

        while (parent != 0u) {
            int parent_index = find_frame_index(frames->frames, parent);
            size_t v;
            if (parent_index < 0) {
                return DOM_FRAMES_INVALID_TREE;
            }
            for (v = 0u; v < visited.size(); ++v) {
                if (visited[v] == parent) {
                    return DOM_FRAMES_INVALID_TREE;
                }
            }
            visited.push_back(parent);
            parent = frames->frames[(size_t)parent_index].parent_id;
        }
        if (entry.kind < DOM_FRAME_KIND_INERTIAL_BARYCENTRIC ||
            entry.kind > DOM_FRAME_KIND_BODY_FIXED) {
            return DOM_FRAMES_INVALID_TREE;
        }
        if ((entry.kind == DOM_FRAME_KIND_BODY_CENTERED_INERTIAL ||
             entry.kind == DOM_FRAME_KIND_BODY_FIXED) &&
            entry.body_id == 0ull) {
            return DOM_FRAMES_INVALID_TREE;
        }
    }
    return DOM_FRAMES_OK;
}

int dom_frames_transform_pos(const dom_frames *frames,
                             dom_frame_id src_frame,
                             dom_frame_id dst_frame,
                             const dom_posseg_q16 *pos,
                             dom_tick tick,
                             dom_posseg_q16 *out_pos) {
    std::vector<int> src_chain;
    std::vector<int> dst_chain;
    int lca_src = -1;
    int lca_dst = -1;
    size_t i;
    int rc;
    dom_posseg_q16 tmp;

    if (!frames || !pos || !out_pos) {
        return DOM_FRAMES_INVALID_ARGUMENT;
    }
    if (src_frame == dst_frame) {
        *out_pos = *pos;
        return DOM_FRAMES_OK;
    }
    {
        dom_frame_id current = src_frame;
        while (current != 0u) {
            int idx = find_frame_index(frames->frames, current);
            if (idx < 0) {
                return DOM_FRAMES_NOT_FOUND;
            }
            src_chain.push_back(idx);
            current = frames->frames[(size_t)idx].parent_id;
            if (src_chain.size() > frames->frames.size()) {
                return DOM_FRAMES_INVALID_TREE;
            }
        }
    }
    {
        dom_frame_id current = dst_frame;
        while (current != 0u) {
            int idx = find_frame_index(frames->frames, current);
            if (idx < 0) {
                return DOM_FRAMES_NOT_FOUND;
            }
            dst_chain.push_back(idx);
            current = frames->frames[(size_t)idx].parent_id;
            if (dst_chain.size() > frames->frames.size()) {
                return DOM_FRAMES_INVALID_TREE;
            }
        }
    }
    for (i = 0u; i < src_chain.size() && lca_src < 0; ++i) {
        size_t j;
        dom_frame_id src_id = frames->frames[(size_t)src_chain[i]].id;
        for (j = 0u; j < dst_chain.size(); ++j) {
            if (src_id == frames->frames[(size_t)dst_chain[j]].id) {
                lca_src = (int)i;
                lca_dst = (int)j;
                break;
            }
        }
    }
    if (lca_src < 0 || lca_dst < 0) {
        return DOM_FRAMES_NOT_FOUND;
    }

    tmp = *pos;
    for (i = 0u; i < (size_t)lca_src; ++i) {
        const FrameEntry &child = frames->frames[(size_t)src_chain[i]];
        const FrameEntry &parent = frames->frames[(size_t)src_chain[i + 1]];
        dom_posseg_q16 next;
        rc = transform_child_to_parent_pos(child, parent, &tmp, tick, &next);
        if (rc != DOM_FRAMES_OK) {
            return rc;
        }
        tmp = next;
    }
    for (i = (size_t)lca_dst; i > 0u; --i) {
        const FrameEntry &parent = frames->frames[(size_t)dst_chain[i]];
        const FrameEntry &child = frames->frames[(size_t)dst_chain[i - 1]];
        dom_posseg_q16 next;
        rc = transform_parent_to_child_pos(parent, child, &tmp, tick, &next);
        if (rc != DOM_FRAMES_OK) {
            return rc;
        }
        tmp = next;
    }
    *out_pos = tmp;
    return DOM_FRAMES_OK;
}

int dom_frames_transform_vel(const dom_frames *frames,
                             dom_frame_id src_frame,
                             dom_frame_id dst_frame,
                             const dom_vec3_q16 *vel,
                             dom_tick tick,
                             dom_vec3_q16 *out_vel) {
    std::vector<int> src_chain;
    std::vector<int> dst_chain;
    int lca_src = -1;
    int lca_dst = -1;
    size_t i;
    int rc;
    dom_vec3_q16 tmp;

    if (!frames || !vel || !out_vel) {
        return DOM_FRAMES_INVALID_ARGUMENT;
    }
    if (src_frame == dst_frame) {
        *out_vel = *vel;
        return DOM_FRAMES_OK;
    }
    {
        dom_frame_id current = src_frame;
        while (current != 0u) {
            int idx = find_frame_index(frames->frames, current);
            if (idx < 0) {
                return DOM_FRAMES_NOT_FOUND;
            }
            src_chain.push_back(idx);
            current = frames->frames[(size_t)idx].parent_id;
            if (src_chain.size() > frames->frames.size()) {
                return DOM_FRAMES_INVALID_TREE;
            }
        }
    }
    {
        dom_frame_id current = dst_frame;
        while (current != 0u) {
            int idx = find_frame_index(frames->frames, current);
            if (idx < 0) {
                return DOM_FRAMES_NOT_FOUND;
            }
            dst_chain.push_back(idx);
            current = frames->frames[(size_t)idx].parent_id;
            if (dst_chain.size() > frames->frames.size()) {
                return DOM_FRAMES_INVALID_TREE;
            }
        }
    }
    for (i = 0u; i < src_chain.size() && lca_src < 0; ++i) {
        size_t j;
        dom_frame_id src_id = frames->frames[(size_t)src_chain[i]].id;
        for (j = 0u; j < dst_chain.size(); ++j) {
            if (src_id == frames->frames[(size_t)dst_chain[j]].id) {
                lca_src = (int)i;
                lca_dst = (int)j;
                break;
            }
        }
    }
    if (lca_src < 0 || lca_dst < 0) {
        return DOM_FRAMES_NOT_FOUND;
    }

    tmp = *vel;
    for (i = 0u; i < (size_t)lca_src; ++i) {
        const FrameEntry &child = frames->frames[(size_t)src_chain[i]];
        const FrameEntry &parent = frames->frames[(size_t)src_chain[i + 1]];
        dom_vec3_q16 next;
        rc = transform_child_to_parent_vel(child, parent, &tmp, tick, &next);
        if (rc != DOM_FRAMES_OK) {
            return rc;
        }
        tmp = next;
    }
    for (i = (size_t)lca_dst; i > 0u; --i) {
        const FrameEntry &parent = frames->frames[(size_t)dst_chain[i]];
        const FrameEntry &child = frames->frames[(size_t)dst_chain[i - 1]];
        dom_vec3_q16 next;
        rc = transform_parent_to_child_vel(parent, child, &tmp, tick, &next);
        if (rc != DOM_FRAMES_OK) {
            return rc;
        }
        tmp = next;
    }
    *out_vel = tmp;
    return DOM_FRAMES_OK;
}
