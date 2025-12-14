#include "dom_world_editor_controller.h"

#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/sim/sim.h"
}

namespace dom {
namespace tools {

DomWorldEditorController::DomWorldEditorController()
    : m_world((d_world *)0),
      m_checksum(0u) {}

DomWorldEditorController::~DomWorldEditorController() {
    if (m_world) {
        d_world_destroy(m_world);
        m_world = (d_world *)0;
    }
}

const char *DomWorldEditorController::tool_id() const { return "world_editor"; }
const char *DomWorldEditorController::tool_name() const { return "World Editor"; }
const char *DomWorldEditorController::tool_description() const { return "Edit world metadata/topology (static preview)."; }

bool DomWorldEditorController::supports_demo() const { return true; }

std::string DomWorldEditorController::demo_path(const std::string &home) const {
    if (home.empty()) {
        return "data/tools_demo/world_demo.dwrl";
    }
    return home + "/data/tools_demo/world_demo.dwrl";
}

bool DomWorldEditorController::load(const std::string &path, std::string &status) {
    if (m_world) {
        d_world_destroy(m_world);
        m_world = (d_world *)0;
    }
    m_checksum = 0u;

    m_world = d_world_load_tlv(path.c_str());
    if (!m_world) {
        status = "Failed to load world (expected DWRL TLV).";
        return false;
    }
    m_checksum = d_world_checksum(m_world);
    status = "Loaded.";
    return true;
}

bool DomWorldEditorController::validate(std::string &status) {
    if (!m_world) {
        status = "Nothing loaded.";
        return false;
    }
    m_checksum = d_world_checksum(m_world);
    status = "Validation OK (checksum updated).";
    return true;
}

bool DomWorldEditorController::save(const std::string &path, std::string &status) {
    if (!m_world) {
        status = "Nothing loaded.";
        return false;
    }
    if (!d_world_save_tlv(m_world, path.c_str())) {
        status = "Save failed.";
        return false;
    }
    status = "Saved.";
    return true;
}

void DomWorldEditorController::summary(std::string &out) const {
    char buf[256];
    if (!m_world) {
        out = "(none)";
        return;
    }
    std::sprintf(buf,
                 "seed=%llu size=%u tick=%u checksum=%u",
                 (unsigned long long)m_world->meta.seed,
                 (unsigned)m_world->meta.world_size_m,
                 (unsigned)m_world->tick_count,
                 (unsigned)m_checksum);
    out = buf;
}

} // namespace tools
} // namespace dom

