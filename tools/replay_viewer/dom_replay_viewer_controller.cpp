/*
FILE: source/dominium/tools/replay_viewer/dom_replay_viewer_controller.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/replay_viewer/dom_replay_viewer_controller
RESPONSIBILITY: Implements `dom_replay_viewer_controller`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_replay_viewer_controller.h"

#include <cstdio>
#include <cstring>

#include "dominium/tools/common/dom_tool_io.h"

namespace dom {
namespace tools {
namespace {

static u32 replay_last_tick(const d_replay_context &ctx) {
    u32 i;
    u32 max_tick = 0u;
    for (i = 0u; i < ctx.frame_count; ++i) {
        if (ctx.frames && ctx.frames[i].tick_index > max_tick) {
            max_tick = ctx.frames[i].tick_index;
        }
    }
    return max_tick;
}

} // namespace

DomReplayViewerController::DomReplayViewerController()
    : m_ctx(),
      m_loaded(false),
      m_last_tick(0u) {
    std::memset(&m_ctx, 0, sizeof(m_ctx));
}

DomReplayViewerController::~DomReplayViewerController() {
    if (m_loaded) {
        d_replay_shutdown(&m_ctx);
        m_loaded = false;
    }
}

const char *DomReplayViewerController::tool_id() const { return "replay_viewer"; }
const char *DomReplayViewerController::tool_name() const { return "Replay Viewer"; }
const char *DomReplayViewerController::tool_description() const { return "Inspect replay timelines and analyze desyncs (stub)."; }

bool DomReplayViewerController::supports_demo() const { return false; }
std::string DomReplayViewerController::demo_path(const std::string &home) const { (void)home; return std::string(); }

bool DomReplayViewerController::load(const std::string &path, std::string &status) {
    std::vector<unsigned char> data;
    std::string err;
    d_tlv_blob blob;

    if (m_loaded) {
        d_replay_shutdown(&m_ctx);
        std::memset(&m_ctx, 0, sizeof(m_ctx));
        m_loaded = false;
    }
    m_last_tick = 0u;

    if (!read_file(path, data, &err)) {
        status = err.empty() ? "Failed to read file." : err;
        return false;
    }
    blob.ptr = data.empty() ? (unsigned char *)0 : &data[0];
    blob.len = (u32)data.size();

    if (d_replay_deserialize(&blob, &m_ctx) != 0) {
        status = "Replay deserialize failed.";
        return false;
    }
    m_loaded = true;
    m_last_tick = replay_last_tick(m_ctx);
    status = "Loaded.";
    return true;
}

bool DomReplayViewerController::validate(std::string &status) {
    if (!m_loaded) {
        status = "Nothing loaded.";
        return false;
    }
    m_last_tick = replay_last_tick(m_ctx);
    status = "OK.";
    return true;
}

bool DomReplayViewerController::save(const std::string &path, std::string &status) {
    (void)path;
    status = "Read-only tool (export TODO).";
    return false;
}

void DomReplayViewerController::summary(std::string &out) const {
    char buf[128];
    if (!m_loaded) {
        out = "(none)";
        return;
    }
    std::sprintf(buf, "frames=%u last_tick=%u", (unsigned)m_ctx.frame_count, (unsigned)m_last_tick);
    out = buf;
}

} // namespace tools
} // namespace dom

