#include "dom_game_app.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "dom_game_states.h"
#include "dom_game_ui.h"
#include "dom_game_save.h"
#include "dominium/version.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/gfx.h"
#include "domino/sys.h"
}

namespace dom {

namespace {

static const unsigned DEFAULT_TICK_RATE = 60u;

static unsigned make_version_u32(unsigned major, unsigned minor, unsigned patch) {
    return major * 10000u + minor * 100u + patch;
}

static unsigned suite_version_u32() {
    return make_version_u32(DOMINIUM_VERSION_MAJOR,
                            DOMINIUM_VERSION_MINOR,
                            DOMINIUM_VERSION_PATCH);
}

static void apply_default_instance_values(InstanceInfo &inst) {
    inst.world_seed = 12345u;
    inst.world_size_m = 2048u;
    inst.vertical_min_m = -256;
    inst.vertical_max_m = 512;
    inst.suite_version = suite_version_u32();
    inst.core_version = suite_version_u32();
    inst.last_product = "game";
    inst.last_product_version = DOMINIUM_GAME_VERSION;
}

} // namespace

DomGameApp::DomGameApp()
    : m_mode(GAME_MODE_GUI),
      m_server_mode(SERVER_OFF),
      m_demo_mode(false),
      m_compat_read_only(false),
      m_compat_limited(false),
      m_tick_rate_hz(DEFAULT_TICK_RATE),
      m_main_view_id(0),
      m_state_id(GAME_STATE_BOOT),
      m_state(0),
      m_running(false) {
    std::memset(&m_ui_ctx, 0, sizeof(m_ui_ctx));
}

DomGameApp::~DomGameApp() {
    shutdown();
}

bool DomGameApp::init_from_cli(const GameConfig &cfg) {
    shutdown();

    m_mode = cfg.mode;
    m_server_mode = cfg.server_mode;
    m_demo_mode = cfg.demo_mode;
    m_tick_rate_hz = cfg.tick_rate_hz ? cfg.tick_rate_hz : DEFAULT_TICK_RATE;
    m_compat_read_only = false;
    m_compat_limited = false;

    if (!init_paths(cfg)) {
        std::printf("DomGameApp: failed to resolve paths\n");
        return false;
    }
    if (!load_instance(cfg)) {
        std::printf("DomGameApp: failed to load instance '%s'\n",
                    m_instance.id.c_str());
        return false;
    }
    if (!evaluate_compatibility(cfg)) {
        std::printf("DomGameApp: compatibility check failed\n");
        return false;
    }
    if (!init_session(cfg)) {
        std::printf("DomGameApp: session init failed\n");
        return false;
    }
    if (!init_views_and_ui(cfg)) {
        std::printf("DomGameApp: view/UI init failed\n");
        return false;
    }

    m_state_id = GAME_STATE_BOOT;
    m_state = create_state(m_state_id);
    if (!m_state) {
        return false;
    }
    m_state->on_enter(*this);

    m_running = true;
    return true;
}

void DomGameApp::run() {
    if (!m_running) {
        return;
    }
    main_loop();
}

void DomGameApp::shutdown() {
    if (m_state) {
        m_state->on_exit(*this);
        destroy_state(m_state);
        m_state = 0;
    }

    if (m_main_view_id != 0u) {
        d_view_destroy(m_main_view_id);
        m_main_view_id = 0u;
    }

    dui_shutdown_context(&m_ui_ctx);
    m_session.shutdown();

    m_running = false;
}

void DomGameApp::request_state_change(GameStateId next) {
    change_state(next);
}

void DomGameApp::request_exit() {
    m_running = false;
}

bool DomGameApp::init_paths(const GameConfig &cfg) {
    std::string home = cfg.dominium_home;
    const char *env_home;

    if (home.empty()) {
        env_home = std::getenv("DOMINIUM_HOME");
        if (env_home && env_home[0] != '\0') {
            home = env_home;
        }
    }
    if (home.empty()) {
        home = ".";
    }
    return resolve_paths(m_paths, home);
}

bool DomGameApp::load_instance(const GameConfig &cfg) {
    m_instance.id = cfg.instance_id.empty() ? "default" : cfg.instance_id;

    if (!m_instance.load(m_paths)) {
        apply_default_instance_values(m_instance);
        if (!m_instance.save(m_paths)) {
            std::printf("DomGameApp: created default instance '%s' (unsaved)\n",
                        m_instance.id.c_str());
        }
    }
    return true;
}

bool DomGameApp::evaluate_compatibility(const GameConfig &cfg) {
    ProductInfo prod;
    CompatResult res;

    prod.product = "game";
    prod.role_detail = (cfg.server_mode == SERVER_DEDICATED) ? "server" : "client";
    prod.product_version = suite_version_u32();
    prod.core_version = suite_version_u32();
    prod.suite_version = suite_version_u32();

    res = evaluate_compat(prod, m_instance);
    if (res == COMPAT_INCOMPATIBLE) {
        return false;
    }
    m_compat_read_only = (res == COMPAT_READONLY);
    m_compat_limited = (res == COMPAT_LIMITED);
    return true;
}

bool DomGameApp::init_session(const GameConfig &cfg) {
    SessionConfig scfg;
    scfg.platform_backend = cfg.platform_backend;
    scfg.gfx_backend = cfg.gfx_backend;
    scfg.audio_backend = std::string();
    scfg.headless = (cfg.mode == GAME_MODE_HEADLESS);
    scfg.tui = (cfg.mode == GAME_MODE_TUI);
    return m_session.init(m_paths, m_instance, scfg);
}

bool DomGameApp::init_views_and_ui(const GameConfig &cfg) {
    d_view_desc desc;
    (void)cfg;

    std::memset(&desc, 0, sizeof(desc));
    desc.id = 1u;
    desc.camera.pos_x = d_q16_16_from_int(0);
    desc.camera.pos_y = d_q16_16_from_int(0);
    desc.camera.pos_z = d_q16_16_from_int(5);
    desc.camera.dir_x = d_q16_16_from_int(0);
    desc.camera.dir_y = d_q16_16_from_int(0);
    desc.camera.dir_z = d_q16_16_from_int(-1);
    desc.camera.up_x = d_q16_16_from_int(0);
    desc.camera.up_y = d_q16_16_from_int(1);
    desc.camera.up_z = d_q16_16_from_int(0);
    desc.camera.fov = d_q16_16_from_int(60);
    desc.vp_x = d_q16_16_from_int(0);
    desc.vp_y = d_q16_16_from_int(0);
    desc.vp_w = d_q16_16_from_int(1024);
    desc.vp_h = d_q16_16_from_int(768);

    m_main_view_id = d_view_create(&desc);
    if (m_main_view_id == 0u) {
        return false;
    }

    dui_shutdown_context(&m_ui_ctx);
    dui_init_context(&m_ui_ctx);

    dom_game_ui_build_root(m_ui_ctx, m_mode);
    return true;
}

void DomGameApp::main_loop() {
    const unsigned sleep_ms = (m_tick_rate_hz > 0u) ? (1000u / m_tick_rate_hz) : 0u;

    while (m_running) {
        tick_fixed();
        if (!m_running) {
            break;
        }
        if (m_mode != GAME_MODE_HEADLESS) {
            render_frame();
        }
        if (sleep_ms > 0u) {
            dsys_sleep_ms(sleep_ms);
        }
    }
}

void DomGameApp::tick_fixed() {
    /* TODO: integrate real input, net, and replay layers here. */
    if (m_state) {
        m_state->tick(*this);
    }

    if (m_session.is_initialized()) {
        d_sim_step(m_session.sim(), 1u);
    }
}

void DomGameApp::render_frame() {
    d_view_desc *view = d_view_get(m_main_view_id);
    dgfx_cmd_buffer *cmd_buffer;
    d_view_frame frame;
    dui_rect root_rect;

    if (!view) {
        return;
    }

    cmd_buffer = dgfx_get_frame_cmd_buffer();
    if (!cmd_buffer) {
        return;
    }

    frame.view = view;
    frame.cmd_buffer = cmd_buffer;

    dgfx_begin_frame();

    root_rect.x = 0;
    root_rect.y = 0;
    root_rect.w = view->vp_w ? view->vp_w : d_q16_16_from_int(1024);
    root_rect.h = view->vp_h ? view->vp_h : d_q16_16_from_int(768);

    d_view_render(m_session.world(), view, &frame);
    dui_layout(&m_ui_ctx, &root_rect);
    dui_render(&m_ui_ctx, &frame);

    dgfx_execute(frame.cmd_buffer);
    dgfx_end_frame();
}

void DomGameApp::change_state(GameStateId next) {
    if (m_state_id == next && m_state) {
        return;
    }

    if (m_state) {
        m_state->on_exit(*this);
        destroy_state(m_state);
        m_state = 0;
    }

    m_state_id = next;
    m_state = create_state(next);
    if (m_state) {
        m_state->on_enter(*this);
    }
}

} // namespace dom
