/*
FILE: source/dominium/setup/cli/setup_ui_gui.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/cli/setup_ui_gui
RESPONSIBILITY: Load and run the Setup UI schema via DUI in a headless-capable CLI path.
ALLOWED DEPENDENCIES: `include/domino/**`, `include/dui/**`, and C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: GUI toolkit frameworks, launcher core headers.
THREADING MODEL: Single-threaded event pump.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: UI is presentation-only; state is static in this stub.
VERSIONING / ABI / DATA FORMAT NOTES: DUI schema TLV + domui action dispatch.
*/
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

extern "C" {
#include "domino/caps.h"
#include "domino/system/dsys.h"
#include "dui/dui_api_v1.h"
}

#include "ui_setup_ui_actions_gen.h"

namespace {

static int ascii_tolower(int c) {
    if (c >= 'A' && c <= 'Z') {
        return c - 'A' + 'a';
    }
    return c;
}

static bool str_ieq(const char* a, const char* b) {
    if (!a || !b) {
        return false;
    }
    while (*a && *b) {
        if (ascii_tolower((unsigned char)*a) != ascii_tolower((unsigned char)*b)) {
            return false;
        }
        ++a;
        ++b;
    }
    return *a == '\0' && *b == '\0';
}

static bool is_sep(char c) { return c == '/' || c == '\\'; }

static std::string normalize_seps(const std::string& in) {
    std::string out = in;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        if (out[i] == '\\') out[i] = '/';
    }
    return out;
}

static std::string dirname_of(const std::string& path) {
    size_t i;
    for (i = path.size(); i > 0u; --i) {
        if (is_sep(path[i - 1u])) {
            return path.substr(0u, i - 1u);
        }
    }
    return std::string();
}

static std::string path_join(const std::string& a, const std::string& b) {
    std::string aa = normalize_seps(a);
    std::string bb = normalize_seps(b);
    if (aa.empty()) return bb;
    if (bb.empty()) return aa;
    if (is_sep(aa[aa.size() - 1u])) return aa + bb;
    return aa + "/" + bb;
}

static bool file_exists_stdio(const std::string& path) {
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) return false;
    std::fclose(f);
    return true;
}

static bool read_file_all_bytes(const std::string& path,
                                std::vector<unsigned char>& out_bytes,
                                std::string& out_error) {
    FILE* f;
    long sz;
    size_t got;
    out_bytes.clear();
    out_error.clear();

    f = std::fopen(path.c_str(), "rb");
    if (!f) {
        out_error = "open_failed";
        return false;
    }
    if (std::fseek(f, 0, SEEK_END) != 0) {
        std::fclose(f);
        out_error = "seek_end_failed";
        return false;
    }
    sz = std::ftell(f);
    if (sz < 0) {
        std::fclose(f);
        out_error = "tell_failed";
        return false;
    }
    if (std::fseek(f, 0, SEEK_SET) != 0) {
        std::fclose(f);
        out_error = "seek_set_failed";
        return false;
    }
    out_bytes.resize((size_t)sz);
    got = 0u;
    if (sz > 0) {
        got = std::fread(&out_bytes[0], 1u, (size_t)sz, f);
    }
    std::fclose(f);
    if (got != (size_t)sz) {
        out_bytes.clear();
        out_error = "read_failed";
        return false;
    }
    return true;
}

static void append_u32_le(std::vector<unsigned char>& out, u32 v) {
    out.push_back((unsigned char)((v >> 0u) & 0xffu));
    out.push_back((unsigned char)((v >> 8u) & 0xffu));
    out.push_back((unsigned char)((v >> 16u) & 0xffu));
    out.push_back((unsigned char)((v >> 24u) & 0xffu));
}

static void append_tlv_raw(std::vector<unsigned char>& out, u32 tag, const void* payload, size_t payload_len) {
    append_u32_le(out, tag);
    append_u32_le(out, (u32)payload_len);
    if (payload_len != 0u) {
        const unsigned char* p = (const unsigned char*)payload;
        out.insert(out.end(), p, p + payload_len);
    }
}

static void build_empty_state(std::vector<unsigned char>& out_state) {
    out_state.clear();
    append_tlv_raw(out_state, DUI_TLV_STATE_V1, 0, 0u);
}

static const dui_api_v1* lookup_dui_api_by_backend_name(const char* want_name, std::string& out_err) {
    u32 i;
    u32 count;
    dom_backend_desc desc;

    if (!want_name || !want_name[0]) {
        out_err = "ui backend name is empty";
        return 0;
    }

    count = dom_caps_backend_count();
    for (i = 0u; i < count; ++i) {
        if (dom_caps_backend_get(i, &desc) != DOM_CAPS_OK) {
            continue;
        }
        if (desc.subsystem_id != DOM_SUBSYS_DUI) {
            continue;
        }
        if (!desc.backend_name || !desc.backend_name[0]) {
            continue;
        }
        if (!str_ieq(desc.backend_name, want_name)) {
            continue;
        }
        if (!desc.get_api) {
            out_err = "ui backend missing get_api";
            return 0;
        }
        {
            const dui_api_v1* api = (const dui_api_v1*)desc.get_api(DUI_API_ABI_VERSION);
            if (!api) {
                out_err = std::string("ui get_api returned null for backend '") + want_name + "'";
                return 0;
            }
            if (api->abi_version != DUI_API_ABI_VERSION || api->struct_size != (u32)sizeof(dui_api_v1)) {
                out_err = std::string("ui api abi mismatch for backend '") + want_name + "'";
                return 0;
            }
            if (!api->create_context || !api->destroy_context ||
                !api->create_window || !api->destroy_window ||
                !api->set_schema_tlv || !api->set_state_tlv ||
                !api->pump || !api->poll_event || !api->request_quit || !api->render) {
                out_err = std::string("ui api missing required functions for backend '") + want_name + "'";
                return 0;
            }
            return api;
        }
    }

    out_err = std::string("ui backend not found in registry: '") + want_name + "'";
    return 0;
}

static const dui_api_v1* select_dui_api(std::string& out_backend_name, std::string& out_err) {
    dom_hw_caps hw;
    dom_selection sel;
    dom_caps_result sel_rc;
    u32 i;
    const char* chosen = (const char*)0;

    out_backend_name.clear();
    out_err.clear();

    (void)dom_caps_register_builtin_backends();
    (void)dom_caps_finalize_registry();

    std::memset(&hw, 0, sizeof(hw));
    hw.abi_version = DOM_CAPS_ABI_VERSION;
    hw.struct_size = (u32)sizeof(hw);
    (void)dom_hw_caps_probe_host(&hw);

    std::memset(&sel, 0, sizeof(sel));
    sel.abi_version = DOM_CAPS_ABI_VERSION;
    sel.struct_size = (u32)sizeof(sel);

    sel_rc = dom_caps_select((const dom_profile*)0, &hw, &sel);
    if (sel_rc != DOM_CAPS_OK) {
        out_err = "caps selection failed";
        return (const dui_api_v1*)0;
    }

    for (i = 0u; i < sel.entry_count; ++i) {
        const dom_selection_entry* e = &sel.entries[i];
        if (e->subsystem_id == DOM_SUBSYS_DUI) {
            chosen = e->backend_name;
            break;
        }
    }
    if (!chosen || !chosen[0]) {
        out_err = "caps selection produced empty ui backend";
        return (const dui_api_v1*)0;
    }

    out_backend_name = chosen;
    return lookup_dui_api_by_backend_name(chosen, out_err);
}

static bool load_dui_schema(const std::string& argv0,
                            std::vector<unsigned char>& out_schema,
                            std::string& out_loaded_path,
                            std::string& out_error) {
    std::string err;
    std::string canonical_err;
    std::vector<std::string> canonical;
    std::vector<std::string> candidates;
    std::string cur;
    int i;

    out_schema.clear();
    out_loaded_path.clear();
    out_error.clear();

    canonical.push_back("tools/setup/ui/doc/setup_ui_doc.tlv");
    canonical.push_back("tools\\setup\\ui\\doc\\setup_ui_doc.tlv");
    for (i = 0; i < (int)canonical.size(); ++i) {
        if (file_exists_stdio(canonical[(size_t)i])) {
            if (!read_file_all_bytes(canonical[(size_t)i], out_schema, err)) {
                canonical_err = std::string("schema_read_failed;path=") + canonical[(size_t)i] + ";err=" + err;
                break;
            }
            out_loaded_path = canonical[(size_t)i];
            return true;
        }
    }

    candidates.push_back("source/dominium/setup/ui_schema/setup_ui_v1.tlv");
    candidates.push_back("source\\dominium\\setup\\ui_schema\\setup_ui_v1.tlv");
    candidates.push_back("ui_schema/setup_ui_v1.tlv");
    candidates.push_back("ui_schema\\setup_ui_v1.tlv");
    candidates.push_back("setup_ui_v1.tlv");

    for (i = 0; i < (int)candidates.size(); ++i) {
        if (file_exists_stdio(candidates[(size_t)i])) {
            if (!read_file_all_bytes(candidates[(size_t)i], out_schema, err)) {
                out_error = std::string("schema_read_failed;path=") + candidates[(size_t)i] + ";err=" + err;
                return false;
            }
            out_loaded_path = candidates[(size_t)i];
            return true;
        }
    }

    cur = dirname_of(argv0);
    for (i = 0; i < 10; ++i) {
        if (!cur.empty()) {
            const std::string cc0 = path_join(cur, "tools/setup/ui/doc/setup_ui_doc.tlv");
            const std::string c0 = path_join(cur, "source/dominium/setup/ui_schema/setup_ui_v1.tlv");
            const std::string c1 = path_join(cur, "ui_schema/setup_ui_v1.tlv");
            const std::string c2 = path_join(cur, "setup_ui_v1.tlv");
            if (file_exists_stdio(cc0)) {
                if (read_file_all_bytes(cc0, out_schema, err)) {
                    out_loaded_path = cc0;
                    return true;
                }
                canonical_err = std::string("schema_read_failed;path=") + cc0 + ";err=" + err;
            }
            if (file_exists_stdio(c0) && read_file_all_bytes(c0, out_schema, err)) {
                out_loaded_path = c0;
                return true;
            }
            if (file_exists_stdio(c1) && read_file_all_bytes(c1, out_schema, err)) {
                out_loaded_path = c1;
                return true;
            }
            if (file_exists_stdio(c2) && read_file_all_bytes(c2, out_schema, err)) {
                out_loaded_path = c2;
                return true;
            }
        }
        cur = dirname_of(cur);
        if (cur.empty()) {
            break;
        }
    }

    if (!canonical_err.empty()) {
        out_error = canonical_err;
    } else {
        out_error = "schema_not_found";
    }
    return false;
}

struct SetupUiState {
    int running;
};

static void dispatch_action(SetupUiState* st, const dui_event_v1& ev) {
    domui_event de;
    (void)st;
    std::memset(&de, 0, sizeof(de));
    de.action_id = (domui_action_id)ev.u.action.action_id;
    de.widget_id = (domui_widget_id)ev.u.action.widget_id;
    de.type = DOMUI_EVENT_CLICK;
    if (ev.u.action.item_id != 0u) {
        de.a.type = DOMUI_VALUE_U32;
        de.a.u.v_u32 = (domui_u32)ev.u.action.item_id;
    } else {
        de.a.type = DOMUI_VALUE_NONE;
    }
    ui_setup_ui_dispatch(st, &de);
}

} // namespace

extern "C" int dom_setup_ui_run_gui(const char* argv0) {
    const dui_api_v1* api = 0;
    dui_context* ctx = 0;
    dui_window* win = 0;
    std::string backend;
    std::string err;
    std::string schema_path;
    std::vector<unsigned char> schema;
    std::vector<unsigned char> state;
    SetupUiState st;
    int rc = 1;

    st.running = 0;

    if (dsys_init() != DSYS_OK) {
        std::printf("Setup: dsys_init failed.\n");
        return 1;
    }

    api = select_dui_api(backend, err);
    if (!api) {
        std::printf("Setup: DUI selection failed: %s\n", err.empty() ? "unknown" : err.c_str());
        goto done;
    }

    {
        const char* initial_name;
        const char* candidates[3];
        u32 cand_count = 0u;
        u32 cand_i;

        initial_name = (api->backend_name && api->backend_name()) ? api->backend_name() : backend.c_str();

        candidates[cand_count++] = initial_name;
        if (!str_ieq(initial_name, "null") && !str_ieq(initial_name, "dgfx")) {
            candidates[cand_count++] = "dgfx";
        }
        if (!str_ieq(initial_name, "null")) {
            candidates[cand_count++] = "null";
        }

        for (cand_i = 0u; cand_i < cand_count; ++cand_i) {
            const char* want = candidates[cand_i];
            const dui_api_v1* cand_api = api;
            std::string lookup_err;
            dui_result dres;
            dui_window_desc_v1 wdesc;

            if (cand_i != 0u) {
                cand_api = lookup_dui_api_by_backend_name(want, lookup_err);
                if (!cand_api) {
                    continue;
                }
            }

            if (cand_api->create_context(&ctx) != DUI_OK || !ctx) {
                continue;
            }

            std::memset(&wdesc, 0, sizeof(wdesc));
            wdesc.abi_version = DUI_API_ABI_VERSION;
            wdesc.struct_size = (u32)sizeof(wdesc);
            wdesc.title = "Dominium Setup";
            wdesc.width = 960;
            wdesc.height = 640;
            wdesc.flags = 0u;

            dres = cand_api->create_window(ctx, &wdesc, &win);
            if (dres != DUI_OK || !win) {
                cand_api->destroy_context(ctx);
                ctx = 0;
                win = 0;
                continue;
            }

            api = cand_api;
            backend = (api->backend_name && api->backend_name()) ? api->backend_name() : want;
            break;
        }
    }

    if (!api || !ctx || !win) {
        std::printf("Setup: DUI init failed.\n");
        goto done;
    }

    if (!load_dui_schema(std::string(argv0 ? argv0 : ""), schema, schema_path, err)) {
        std::printf("Setup: failed to load DUI schema: %s\n", err.empty() ? "unknown" : err.c_str());
        goto done;
    }
    std::printf("Setup: loaded UI schema: %s\n", schema_path.c_str());

    if (api->set_schema_tlv(win, schema.empty() ? (const void*)0 : &schema[0], (u32)schema.size()) != DUI_OK) {
        std::printf("Setup: DUI set_schema_tlv failed.\n");
        goto done;
    }

    build_empty_state(state);
    (void)api->set_state_tlv(win, state.empty() ? (const void*)0 : &state[0], (u32)state.size());
    (void)api->render(win);

    st.running = 1;
    while (st.running) {
        dui_event_v1 ev;
        std::memset(&ev, 0, sizeof(ev));
        (void)api->pump(ctx);
        while (api->poll_event(ctx, &ev) > 0) {
            if (ev.type == (u32)DUI_EVENT_QUIT) {
                st.running = 0;
                break;
            }
            if (ev.type == (u32)DUI_EVENT_ACTION) {
                dispatch_action(&st, ev);
            }
        }
        (void)api->render(win);
        dsys_sleep_ms(16);
    }

    rc = 0;

done:
    if (api && win) {
        api->destroy_window(win);
    }
    if (api && ctx) {
        api->destroy_context(ctx);
    }
    dsys_shutdown();
    return rc;
}
