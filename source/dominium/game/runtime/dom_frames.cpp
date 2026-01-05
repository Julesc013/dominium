/*
FILE: source/dominium/game/runtime/dom_frames.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/frames
RESPONSIBILITY: Reference frame registry scaffolding (tree + transform stubs).
*/
#include "runtime/dom_frames.h"

#include <vector>

namespace {

struct FrameEntry {
    dom_frame_id id;
    dom_frame_id parent_id;
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
    if (find_frame_index(frames->frames, desc->id) >= 0) {
        return DOM_FRAMES_DUPLICATE_ID;
    }
    entry.id = desc->id;
    entry.parent_id = desc->parent_id;
    frames->frames.push_back(entry);
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
    }
    return DOM_FRAMES_OK;
}

int dom_frames_transform_pos(const dom_frames *frames,
                             dom_frame_id src_frame,
                             dom_frame_id dst_frame,
                             const dom_posseg_q16 *pos,
                             dom_tick /*tick*/,
                             dom_posseg_q16 *out_pos) {
    if (!frames || !pos || !out_pos) {
        return DOM_FRAMES_INVALID_ARGUMENT;
    }
    if (src_frame == dst_frame) {
        *out_pos = *pos;
        return DOM_FRAMES_OK;
    }
    return DOM_FRAMES_NOT_IMPLEMENTED;
}
