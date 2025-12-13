#include "dom_game_app.h"

#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "dom_game_states.h"
#include "dom_game_ui.h"
#include "dom_game_ui_debug.h"
#include "dom_game_save.h"
#include "dominium/version.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/gfx.h"
#include "domino/system/d_system.h"
#include "system/d_system_input.h"
#include "struct/d_struct.h"
#include "struct/d_struct_blueprint.h"
#include "res/d_res.h"
#include "content/d_content.h"
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
    inst.packs.clear();
    inst.mods.clear();
    {
        PackRef pref;
        pref.id = "base";
        pref.version = 1u;
        inst.packs.push_back(pref);
    }
    {
        ModRef mref;
        mref.id = "base_demo";
        mref.version = 1u;
        inst.mods.push_back(mref);
    }
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
      m_running(false),
      m_mouse_x(0),
      m_mouse_y(0),
      m_last_struct_id(0),
      m_dev_mode(false),
      m_detmode(0u),
      m_last_hash(0u),
      m_show_debug_panel(false) {
    std::memset(&m_ui_ctx, 0, sizeof(m_ui_ctx));
    std::memset(m_hud_instance_text, 0, sizeof(m_hud_instance_text));
    std::memset(m_hud_remaining_text, 0, sizeof(m_hud_remaining_text));
    std::memset(m_hud_inventory_text, 0, sizeof(m_hud_inventory_text));
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
    m_dev_mode = cfg.dev_mode;
    m_detmode = cfg.deterministic_test ? 3u : 0u;
    m_replay_record_path = cfg.replay_record_path;
    m_replay_play_path = cfg.replay_play_path;
    m_show_debug_panel = m_dev_mode;
    m_last_hash = 0u;
    if (!m_replay_record_path.empty()) {
        m_detmode = 1u;
    }
    if (!m_replay_play_path.empty()) {
        m_detmode = 2u;
    }

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

    {
        const char *sys_backend = cfg.platform_backend.empty() ? "win32" : cfg.platform_backend.c_str();
        std::printf("DomGameApp: initializing system backend '%s'\n", sys_backend);
        if (!d_system_init(sys_backend)) {
            std::printf("DomGameApp: system init failed\n");
            return false;
        }
    }

    if (m_mode != GAME_MODE_HEADLESS) {
        const char *gfx_backend = cfg.gfx_backend.empty() ? "soft" : cfg.gfx_backend.c_str();
        std::printf("DomGameApp: initializing gfx backend '%s'\n", gfx_backend);
        if (!d_gfx_init(gfx_backend)) {
            std::printf("DomGameApp: gfx init failed\n");
            return false;
        }
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
    d_gfx_shutdown();
    d_system_shutdown();

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
    m_instance.id = cfg.instance_id.empty() ? "demo" : cfg.instance_id;

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
    if (res == COMPAT_INCOMPATIBLE || res == COMPAT_MOD_UNSAFE || res == COMPAT_SCHEMA_MISMATCH) {
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
    desc.vp_x = d_q16_16_from_int(0);
    desc.vp_y = d_q16_16_from_int(0);
    desc.vp_w = d_q16_16_from_int(1);
    desc.vp_h = d_q16_16_from_int(1);
    desc.camera.pos_x = d_q16_16_from_int(0);
    desc.camera.pos_y = d_q16_16_from_int(10);
    desc.camera.pos_z = d_q16_16_from_int(0);
    desc.camera.dir_x = 0;
    desc.camera.dir_y = d_q16_16_from_int(-1);
    desc.camera.dir_z = 0;
    desc.camera.up_x = 0;
    desc.camera.up_y = 0;
    desc.camera.up_z = d_q16_16_from_int(1);

    m_main_view_id = d_view_create(&desc);
    if (m_main_view_id == 0u) {
        return false;
    }

    dui_shutdown_context(&m_ui_ctx);
    dui_init_context(&m_ui_ctx);
    dom_game_ui_set_app(this);

    dom_game_ui_build_root(m_ui_ctx, m_mode);
    m_camera.reset();
    return true;
}

void DomGameApp::main_loop() {
    const unsigned sleep_ms = (m_tick_rate_hz > 0u) ? (1000u / m_tick_rate_hz) : 0u;

    while (m_running) {
        if (d_system_pump_events() != 0) {
            m_running = false;
            break;
        }
        tick_fixed();
        if (!m_running) {
            break;
        }
        if (m_mode != GAME_MODE_HEADLESS) {
            render_frame();
        }
        if (sleep_ms > 0u) {
            d_system_sleep_ms(sleep_ms);
        }
    }
}

void DomGameApp::tick_fixed() {
    process_input_events();
    update_camera();

    if (m_state) {
        m_state->tick(*this);
    }

    if (m_session.is_initialized() && m_state_id == GAME_STATE_RUNNING) {
        d_sim_step(m_session.sim(), 1u);
    }
    update_demo_hud();
    update_debug_panel();
}

void DomGameApp::render_frame() {
    d_view_desc *view = d_view_get(m_main_view_id);
    d_gfx_cmd_buffer *cmd_buffer;
    d_view_frame frame;
    dui_rect root_rect;
    i32 width = 800;
    i32 height = 600;

    if (!view) {
        return;
    }

    cmd_buffer = d_gfx_cmd_buffer_begin();
    if (!cmd_buffer) {
        return;
    }

    frame.view = view;
    frame.cmd_buffer = cmd_buffer;

    d_gfx_get_surface_size(&width, &height);

    root_rect.x = 0;
    root_rect.y = 0;
    root_rect.w = d_q16_16_from_int(width);
    root_rect.h = d_q16_16_from_int(height);

    d_view_render(m_session.world(), view, &frame);
    dui_layout(&m_ui_ctx, &root_rect);
    dui_render(&m_ui_ctx, &frame);

    d_gfx_cmd_buffer_end(cmd_buffer);
    d_gfx_submit(cmd_buffer);
    d_gfx_present();
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

void DomGameApp::process_input_events() {
    d_sys_event ev;
    while (d_system_poll_event(&ev) > 0) {
        if (ev.type == D_SYS_EVENT_QUIT) {
            m_running = false;
            break;
        }
        if (ev.type == D_SYS_EVENT_MOUSE_MOVE) {
            m_mouse_x = ev.u.mouse.x;
            m_mouse_y = ev.u.mouse.y;
        }
        if (ev.type == D_SYS_EVENT_MOUSE_BUTTON_DOWN) {
            dom_game_ui_try_click(m_ui_ctx, m_mouse_x, m_mouse_y);
        }
        if (ev.type == D_SYS_EVENT_KEY_DOWN || ev.type == D_SYS_EVENT_KEY_UP) {
            if (ev.u.key.key == D_SYS_KEY_ESCAPE && ev.type == D_SYS_EVENT_KEY_DOWN) {
                m_running = false;
            }
        }
        m_camera.handle_input(ev);
    }
}

void DomGameApp::update_camera() {
    float tick_dt = (m_tick_rate_hz > 0u) ? (1.0f / (float)m_tick_rate_hz) : (1.0f / 60.0f);
    d_view_desc *view = d_view_get(m_main_view_id);
    m_camera.tick(tick_dt);
    if (view) {
        m_camera.apply_to_view(*view);
    }
}

void DomGameApp::spawn_demo_blueprint() {
    d_world *w = m_session.world();
    const d_proto_blueprint *bp;
    q16_16 pos_x;
    q16_16 pos_z;
    if (!w) {
        return;
    }
    bp = d_content_get_blueprint_by_name("Test Extractor Kit");
    if (!bp) {
        return;
    }
    pos_x = d_q16_16_from_double((double)m_camera.cx);
    pos_z = d_q16_16_from_double((double)m_camera.cy);
    {
        int id = d_struct_spawn_blueprint(w, bp, pos_x, d_q16_16_from_int(0), pos_z);
        if (id > 0) {
            m_last_struct_id = (d_struct_instance_id)id;
        }
    }
}

void DomGameApp::update_demo_hud() {
    d_world *w = m_session.world();
    const d_struct_instance *inst = (const d_struct_instance *)0;
    d_struct_instance_id current = m_last_struct_id;
    if (!w || m_state_id != GAME_STATE_RUNNING) {
        return;
    }

    if (current != 0u) {
        inst = d_struct_get(w, current);
    }
    if (!inst) {
        u32 count = d_struct_count(w);
        double best_dist2 = 0.0;
        u32 i;
        for (i = 0u; i < count; ++i) {
            const d_struct_instance *cand = d_struct_get_by_index(w, i);
            if (!cand) {
                continue;
            }
            double dx = d_q16_16_to_double(cand->pos_x) - (double)m_camera.cx;
            double dz = d_q16_16_to_double(cand->pos_z) - (double)m_camera.cy;
            double dist2 = dx * dx + dz * dz;
            if (!inst || dist2 < best_dist2) {
                inst = cand;
                best_dist2 = dist2;
            }
        }
        if (inst) {
            m_last_struct_id = inst->id;
        }
    }

    std::snprintf(m_hud_instance_text, sizeof(m_hud_instance_text),
                  "Instance: %s / Seed: %u",
                  m_instance.id.c_str(),
                  (unsigned)m_instance.world_seed);

    std::snprintf(m_hud_remaining_text, sizeof(m_hud_remaining_text),
                  "Remaining: (n/a)");
    std::snprintf(m_hud_inventory_text, sizeof(m_hud_inventory_text),
                  "Inventory: (empty)");

    if (inst) {
        dres_sample samples[4];
        u16 sample_count = 4u;
        q16_16 best = 0;
        q32_32 sx = ((q32_32)inst->pos_x) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
        q32_32 sy = ((q32_32)inst->pos_y) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);
        q32_32 sz = ((q32_32)inst->pos_z) << (Q32_32_FRAC_BITS - Q16_16_FRAC_BITS);

        if (dres_sample_at(w, sx, sy, sz, 0u, samples, &sample_count) == 0 && sample_count > 0u) {
            u16 i;
            for (i = 0u; i < sample_count; ++i) {
                if (i == 0u || samples[i].value[0] > best) {
                    best = samples[i].value[0];
                }
            }
            std::snprintf(m_hud_remaining_text, sizeof(m_hud_remaining_text),
                          "Remaining v0: %d", d_q16_16_to_int(best));
        }

        {
            d_item_id item_id = 0u;
            u32 item_count = 0u;
            const d_proto_item *item_proto = (const d_proto_item *)0;
            if (d_struct_get_inventory_summary(w, inst->id, &item_id, &item_count) == 0 && item_id != 0u && item_count > 0u) {
                item_proto = d_content_get_item(item_id);
            }
            if (item_proto && item_proto->name) {
                std::snprintf(m_hud_inventory_text, sizeof(m_hud_inventory_text),
                              "Inventory: %s x %u", item_proto->name, (unsigned)item_count);
            } else if (item_id != 0u && item_count > 0u) {
                std::snprintf(m_hud_inventory_text, sizeof(m_hud_inventory_text),
                              "Inventory: #%u x %u", (unsigned)item_id, (unsigned)item_count);
            } else {
                std::snprintf(m_hud_inventory_text, sizeof(m_hud_inventory_text),
                              "Inventory: (empty)");
            }
        }
    }

    {
        dui_widget *inst_label = dom_game_ui_get_instance_label();
        dui_widget *rem_label = dom_game_ui_get_remaining_label();
        dui_widget *inv_label = dom_game_ui_get_inventory_label();
        if (inst_label) inst_label->text = m_hud_instance_text;
        if (rem_label) rem_label->text = m_hud_remaining_text;
        if (inv_label) inv_label->text = m_hud_inventory_text;
    }
}

void DomGameApp::update_debug_panel() {
    d_world *w = m_session.world();
    d_world_hash h = 0u;
    if (!w) {
        return;
    }

    h = d_sim_hash_world(w);

    if (m_detmode == 3u) {
        if (m_last_hash != 0u && h != m_last_hash) {
            std::fprintf(stderr, "DET FAIL: world hash mismatch at tick %u\n", m_session.sim()->tick_index);
            std::abort();
        }
        m_last_hash = h;
    } else if (m_detmode != 0u) {
        m_last_hash = h;
    }

    if (m_show_debug_panel) {
        dom_game_ui_debug_update(m_ui_ctx, *this, h);
    }
}

} // namespace dom
