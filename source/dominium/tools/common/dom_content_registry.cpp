#include "dom_content_registry.h"

#include <cstring>

#include "dom_tool_engine.h"

extern "C" {
#include "content/d_content.h"
#include "policy/d_policy.h"
#include "research/d_research_state.h"
#include "job/d_job.h"
#include "struct/d_struct.h"
#include "vehicle/d_vehicle.h"
#include "trans/d_trans.h"
}

namespace dom {
namespace tools {

DomContentRegistry::DomContentRegistry() {}

DomContentRegistry::~DomContentRegistry() {}

void DomContentRegistry::reset() {
    ensure_engine_content_initialized();
    d_content_reset();
}

bool DomContentRegistry::load_as_pack(const d_tlv_blob &content_or_pack_manifest, std::string &err) {
    d_proto_pack_manifest man;
    ensure_engine_content_initialized();
    d_content_reset();
    std::memset(&man, 0, sizeof(man));
    man.id = 1u;
    man.version = 1u;
    man.name = "tool_pack";
    man.description = (const char *)0;
    man.content_tlv = content_or_pack_manifest;
    if (d_content_load_pack(&man) != 0) {
        err = "d_content_load_pack failed";
        return false;
    }
    return true;
}

bool DomContentRegistry::load_as_mod(const d_tlv_blob &content_or_mod_manifest, std::string &err) {
    d_proto_mod_manifest man;
    ensure_engine_content_initialized();
    d_content_reset();
    std::memset(&man, 0, sizeof(man));
    man.id = 1u;
    man.version = 1u;
    man.name = "tool_mod";
    man.description = (const char *)0;
    man.deps_tlv.ptr = (unsigned char *)0;
    man.deps_tlv.len = 0u;
    man.content_tlv = content_or_mod_manifest;
    if (d_content_load_mod(&man) != 0) {
        err = "d_content_load_mod failed";
        return false;
    }
    return true;
}

bool DomContentRegistry::validate_all(std::string &err) {
    ensure_engine_content_initialized();

    if (d_content_validate_all() != 0) { err = "d_content_validate_all failed"; return false; }
    if (d_research_validate((const d_world *)0) != 0) { err = "d_research_validate failed"; return false; }
    if (d_policy_validate((const d_world *)0) != 0) { err = "d_policy_validate failed"; return false; }
    if (d_trans_validate((const d_world *)0) != 0) { err = "d_trans_validate failed"; return false; }
    if (d_struct_validate((const d_world *)0) != 0) { err = "d_struct_validate failed"; return false; }
    if (d_vehicle_validate((const d_world *)0) != 0) { err = "d_vehicle_validate failed"; return false; }
    if (d_job_validate((const d_world *)0) != 0) { err = "d_job_validate failed"; return false; }
    return true;
}

} // namespace tools
} // namespace dom

