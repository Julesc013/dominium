#include "dom_session.h"

#include <cstring>

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

    if (!create_world(m_inst)) {
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
    dsys_result sys_rc;
    dgfx_desc gfx_desc;

    m_engine_initialized = false;

    if (!cfg.platform_backend.empty()) {
        (void)dom_sys_select_backend(cfg.platform_backend.c_str());
    }

    sys_rc = dsys_init();
    if (sys_rc != DSYS_OK) {
        return false;
    }
    m_engine_initialized = true;

    d_content_register_schemas();
    d_content_init();

    if (!cfg.headless) {
        std::memset(&gfx_desc, 0, sizeof(gfx_desc));
        gfx_desc.backend = choose_gfx_backend(cfg);
        gfx_desc.native_window = (void *)0;
        gfx_desc.window = (dsys_window *)0;
        gfx_desc.width = 0;
        gfx_desc.height = 0;
        gfx_desc.fullscreen = 0;
        gfx_desc.vsync = 0;

        if (!dgfx_init(&gfx_desc)) {
            return false;
        }
    }

    return true;
}

bool DomSession::load_content(const PackSet &pset) {
    size_t i;

    if (pset.pack_blobs.size() != m_inst.packs.size()) {
        return false;
    }
    if (pset.mod_blobs.size() != m_inst.mods.size()) {
        return false;
    }

    for (i = 0u; i < pset.pack_blobs.size(); ++i) {
        d_proto_pack_manifest man;
        std::memset(&man, 0, sizeof(man));
        man.pack_id = m_inst.packs[i].id.c_str();
        man.pack_version = m_inst.packs[i].version;
        man.content_tlv = pset.pack_blobs[i];
        man.flags = 0u;
        man.dep_count = 0u;

        if (d_content_load_pack(&man) != D_CONTENT_OK) {
            return false;
        }
    }

    for (i = 0u; i < pset.mod_blobs.size(); ++i) {
        d_proto_mod_manifest man;
        std::memset(&man, 0, sizeof(man));
        man.mod_id = m_inst.mods[i].id.c_str();
        man.mod_version = m_inst.mods[i].version;
        man.base_pack_tlv = pset.mod_blobs[i];
        man.extra_tlv.ptr = (unsigned char *)0;
        man.extra_tlv.len = 0u;
        man.flags = 0u;
        man.dep_count = 0u;

        if (d_content_load_mod(&man) != D_CONTENT_OK) {
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
        d_world_destroy(m_world);
        m_world = (d_world *)0;
    }

    d_replay_shutdown(&m_replay);
    d_content_shutdown();
    dgfx_shutdown();
    dsys_shutdown();

    m_initialized = false;
    m_engine_initialized = false;
}

} // namespace dom
