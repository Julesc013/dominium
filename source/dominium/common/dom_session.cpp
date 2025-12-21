/*
FILE: source/dominium/common/dom_session.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / common/dom_session
RESPONSIBILITY: Implements `dom_session`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_session.h"

#include <cstring>
#include <map>

extern "C" {
#include "res/d_res.h"
#include "env/d_env.h"
#include "build/d_build.h"
#include "trans/d_trans.h"
#include "struct/d_struct.h"
#include "vehicle/d_vehicle.h"
#include "job/d_job.h"
#include "ai/d_agent.h"
#include "core/d_org.h"
#include "econ/d_econ_metrics.h"
#include "policy/d_policy.h"
#include "research/d_research_state.h"
}

namespace dom {

namespace {

static int str_ieq(const std::string &a, const char *b) {
    size_t i;
    if (!b) {
        return 0;
    }
    if (a.size() != std::strlen(b)) {
        return 0;
    }
    for (i = 0u; i < a.size(); ++i) {
        char ca = a[i];
        char cb = b[i];
        if (ca >= 'A' && ca <= 'Z') ca = static_cast<char>(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = static_cast<char>(cb - 'A' + 'a');
        if (ca != cb) {
            return 0;
        }
    }
    return 1;
}

static dgfx_backend_t choose_gfx_backend(const SessionConfig &cfg) {
    if (cfg.headless || cfg.tui) {
        return DGFX_BACKEND_NULL;
    }
    if (str_ieq(cfg.gfx_backend, "dx11")) return DGFX_BACKEND_DX11;
    if (str_ieq(cfg.gfx_backend, "dx9"))  return DGFX_BACKEND_DX9;
    if (str_ieq(cfg.gfx_backend, "gl2"))  return DGFX_BACKEND_GL2;
    if (str_ieq(cfg.gfx_backend, "gl1"))  return DGFX_BACKEND_GL1;
    if (str_ieq(cfg.gfx_backend, "vk1"))  return DGFX_BACKEND_VK1;
    if (str_ieq(cfg.gfx_backend, "metal")) return DGFX_BACKEND_METAL;
    if (str_ieq(cfg.gfx_backend, "quartz")) return DGFX_BACKEND_QUARTZ;
    if (str_ieq(cfg.gfx_backend, "gdi")) return DGFX_BACKEND_GDI;
    if (str_ieq(cfg.gfx_backend, "null")) return DGFX_BACKEND_NULL;
    return DGFX_BACKEND_SOFT;
}

struct IdAllocator {
    std::map<std::string, unsigned> *map;
    unsigned *next;

    unsigned get(const std::string &key) {
        std::map<std::string, unsigned>::iterator it = map->find(key);
        if (it != map->end()) {
            return it->second;
        }
        unsigned id = *next;
        *next += 1u;
        (*map)[key] = id;
        return id;
    }
};

static bool run_validators(d_world *w) {
    if (!w) {
        return false;
    }
    if (d_org_validate(w) != 0) return false;
    if (d_research_validate(w) != 0) return false;
    if (d_policy_validate(w) != 0) return false;
    if (d_econ_validate(w) != 0) return false;
    if (d_res_validate(w) != 0) return false;
    if (d_env_validate(w) != 0) return false;
    if (d_build_validate_world(w) != 0) return false;
    if (d_trans_validate(w) != 0) return false;
    if (d_struct_validate(w) != 0) return false;
    if (d_vehicle_validate(w) != 0) return false;
    if (d_job_validate(w) != 0) return false;
    if (d_agent_validate(w) != 0) return false;
    return true;
}

} // namespace

DomSession::DomSession()
    : m_world(0),
      m_engine_initialized(false),
      m_initialized(false) {
    std::memset(&m_sim, 0, sizeof(m_sim));
    std::memset(&m_replay, 0, sizeof(m_replay));
}

DomSession::~DomSession() {
    shutdown();
}

bool DomSession::init(const Paths &paths,
                      const InstanceInfo &inst,
                      const SessionConfig &cfg) {
    if (m_initialized) {
        shutdown();
    }

    m_paths = paths;
    m_inst = inst;

    if (!init_engine(cfg)) {
        shutdown();
        return false;
    }

    if (!m_packset.load_for_instance(m_paths, m_inst)) {
        shutdown();
        return false;
    }

    if (!load_content(m_packset)) {
        shutdown();
        return false;
    }

    if (d_content_validate_all() != 0) {
        shutdown();
        return false;
    }

    if (!create_world(m_inst)) {
        shutdown();
        return false;
    }

    if (!run_validators(m_world)) {
        shutdown();
        return false;
    }

    if (d_sim_init(&m_sim, m_world, d_q16_16_from_int(1)) != 0) {
        shutdown();
        return false;
    }

    /* Replay starts disabled. */
    std::memset(&m_replay, 0, sizeof(m_replay));
    m_replay.mode = DREPLAY_MODE_OFF;

    m_initialized = true;
    return true;
}

bool DomSession::init_engine(const SessionConfig &cfg) {
    m_engine_initialized = true;

    d_content_register_schemas();
    d_content_init();

    return true;
}

bool DomSession::load_content(const PackSet &pset) {
    size_t i;
    unsigned expected_packs = pset.base_loaded ? 1u : 0u;
    for (i = 0u; i < m_inst.packs.size(); ++i) {
        if (!str_ieq(m_inst.packs[i].id, "base")) {
            expected_packs += 1u;
        }
    }

    if (pset.pack_blobs.size() != expected_packs) {
        return false;
    }
    if (pset.mod_blobs.size() != m_inst.mods.size()) {
        return false;
    }

    std::map<std::string, unsigned> pack_id_map;
    std::map<std::string, unsigned> mod_id_map;
    unsigned next_pack_id = 1u;
    unsigned next_mod_id = 1u;
    IdAllocator pack_ids;
    IdAllocator mod_ids;
    pack_ids.map = &pack_id_map;
    pack_ids.next = &next_pack_id;
    mod_ids.map = &mod_id_map;
    mod_ids.next = &next_mod_id;

    size_t blob_index = 0u;
    if (pset.base_loaded) {
        d_proto_pack_manifest man;
        std::memset(&man, 0, sizeof(man));
        man.id = pack_ids.get(std::string("base"));
        man.version = pset.base_version;
        man.name = "base";
        man.description = (const char *)0;
        man.content_tlv = pset.pack_blobs[0];

        if (d_content_load_pack(&man) != 0) {
            return false;
        }
        blob_index = 1u;
    }

    for (i = 0u; i < m_inst.packs.size(); ++i) {
        if (str_ieq(m_inst.packs[i].id, "base")) {
            continue;
        }
        if (blob_index >= pset.pack_blobs.size()) {
            return false;
        }
        d_proto_pack_manifest man;
        std::memset(&man, 0, sizeof(man));
        man.id = pack_ids.get(m_inst.packs[i].id);
        man.version = m_inst.packs[i].version;
        man.name = m_inst.packs[i].id.c_str();
        man.description = (const char *)0;
        man.content_tlv = pset.pack_blobs[blob_index];

        if (d_content_load_pack(&man) != 0) {
            return false;
        }
        blob_index += 1u;
    }
    if (blob_index != pset.pack_blobs.size()) {
        return false;
    }

    for (i = 0u; i < pset.mod_blobs.size(); ++i) {
        d_proto_mod_manifest man;
        std::memset(&man, 0, sizeof(man));
        man.id = mod_ids.get(m_inst.mods[i].id);
        man.version = m_inst.mods[i].version;
        man.name = m_inst.mods[i].id.c_str();
        man.description = (const char *)0;
        man.deps_tlv.ptr = (unsigned char *)0;
        man.deps_tlv.len = 0u;
        man.content_tlv = pset.mod_blobs[i];

        if (d_content_load_mod(&man) != 0) {
            return false;
        }
    }

    return true;
}

bool DomSession::create_world(const InstanceInfo &inst) {
    d_world_meta meta;
    std::memset(&meta, 0, sizeof(meta));

    meta.seed = inst.world_seed;
    meta.world_size_m = inst.world_size_m;
    meta.vertical_min = d_q16_16_from_int(inst.vertical_min_m);
    meta.vertical_max = d_q16_16_from_int(inst.vertical_max_m);
    meta.core_version = inst.core_version;
    meta.suite_version = inst.suite_version;
    meta.compat_profile_id = 0u;
    meta.extra.ptr = (unsigned char *)0;
    meta.extra.len = 0u;

    m_world = d_world_create(&meta);
    return m_world != (d_world *)0;
}

void DomSession::shutdown() {
    if (!m_engine_initialized && !m_initialized) {
        return;
    }

    d_sim_shutdown(&m_sim);
    if (m_world) {
        d_trans_shutdown(m_world);
        d_build_shutdown(m_world);
        d_world_destroy(m_world);
        m_world = (d_world *)0;
    }

    d_replay_shutdown(&m_replay);
    d_content_shutdown();

    m_initialized = false;
    m_engine_initialized = false;
}

} // namespace dom
