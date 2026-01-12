/*
FILE: source/dominium/game/ui/dom_ui_widgets.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/ui
RESPONSIBILITY: Data-driven HUD widget definitions, layout profiles, and capability-driven rendering.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS-specific headers; authoritative sim mutation.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Derived-only; deterministic parsing and ordering.
*/
#include "ui/dom_ui_widgets.h"

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>

extern "C" {
#include "domino/core/fixed.h"
}

namespace dom {

namespace {

static std::string trim(const std::string &s) {
    size_t start = 0u;
    size_t end = s.size();
    while (start < end && std::isspace(static_cast<unsigned char>(s[start]))) {
        ++start;
    }
    while (end > start && std::isspace(static_cast<unsigned char>(s[end - 1u]))) {
        --end;
    }
    return s.substr(start, end - start);
}

static std::string strip_comment(const std::string &s) {
    bool in_string = false;
    size_t i;
    for (i = 0u; i < s.size(); ++i) {
        char c = s[i];
        if (c == '"' && (i == 0u || s[i - 1u] != '\\')) {
            in_string = !in_string;
        } else if (c == '#' && !in_string) {
            return s.substr(0u, i);
        }
    }
    return s;
}

static bool read_lines(const std::string &path,
                       std::vector<std::string> &out,
                       std::string &err) {
    std::ifstream in(path.c_str(), std::ios::in);
    std::string line;
    if (!in.is_open()) {
        err = "open_failed";
        return false;
    }
    while (std::getline(in, line)) {
        out.push_back(line);
    }
    return true;
}

static void set_error(std::string &err,
                      const std::string &path,
                      int line,
                      const std::string &msg) {
    if (!err.empty()) {
        return;
    }
    std::ostringstream oss;
    if (!path.empty()) {
        oss << path;
        if (line > 0) {
            oss << ":" << line;
        }
        oss << ": ";
    }
    oss << msg;
    err = oss.str();
}

static bool parse_key_value(const std::string &line,
                            std::string &key,
                            std::string &value) {
    size_t eq = line.find('=');
    if (eq == std::string::npos) {
        return false;
    }
    key = trim(line.substr(0u, eq));
    value = trim(line.substr(eq + 1u));
    return !(key.empty() || value.empty());
}

static bool parse_string(const std::string &s, std::string &out, std::string &err) {
    if (s.size() < 2u || s[0] != '"' || s[s.size() - 1u] != '"') {
        err = "expected_quoted_string";
        return false;
    }
    out = s.substr(1u, s.size() - 2u);
    return true;
}

static bool parse_bool(const std::string &s, int &out, std::string &err) {
    std::string t = trim(s);
    std::string lower;
    lower.reserve(t.size());
    for (size_t i = 0u; i < t.size(); ++i) {
        lower.push_back((char)std::tolower((unsigned char)t[i]));
    }
    if (lower == "true" || lower == "1") {
        out = 1;
        return true;
    }
    if (lower == "false" || lower == "0") {
        out = 0;
        return true;
    }
    err = "invalid_bool";
    return false;
}

static bool parse_i32(const std::string &s, int &out, std::string &err) {
    char *end = 0;
    long v;
    if (s.empty()) {
        err = "empty_number";
        return false;
    }
    v = std::strtol(s.c_str(), &end, 10);
    if (!end || end[0] != '\0') {
        err = "invalid_number";
        return false;
    }
    if (v < -2147483647L - 1L || v > 2147483647L) {
        err = "number_overflow";
        return false;
    }
    out = (int)v;
    return true;
}

static bool parse_u32(const std::string &s, u32 &out, std::string &err) {
    char *end = 0;
    unsigned long v;
    if (s.empty()) {
        err = "empty_number";
        return false;
    }
    v = std::strtoul(s.c_str(), &end, 10);
    if (!end || end[0] != '\0') {
        err = "invalid_number";
        return false;
    }
    if (v > 0xfffffffful) {
        err = "number_overflow";
        return false;
    }
    out = (u32)v;
    return true;
}

static bool parse_q16_16(const std::string &s, i32 &out, std::string &err) {
    std::string t = trim(s);
    size_t i = 0u;
    bool neg = false;
    u64 int_part = 0ull;
    u64 frac_part = 0ull;
    u64 frac_div = 1ull;
    int frac_digits = 0;
    bool have_digit = false;

    if (t.empty()) {
        err = "empty_number";
        return false;
    }
    if (t[i] == '+' || t[i] == '-') {
        neg = (t[i] == '-');
        ++i;
    }
    for (; i < t.size(); ++i) {
        char c = t[i];
        if (c >= '0' && c <= '9') {
            have_digit = true;
            int_part = (int_part * 10ull) + (u64)(c - '0');
        } else {
            break;
        }
    }
    if (i < t.size() && t[i] == '.') {
        ++i;
        for (; i < t.size(); ++i) {
            char c = t[i];
            if (c < '0' || c > '9') {
                err = "invalid_number";
                return false;
            }
            if (frac_digits < 6) {
                frac_part = (frac_part * 10ull) + (u64)(c - '0');
                frac_div *= 10ull;
                frac_digits++;
            }
        }
    }
    if (!have_digit) {
        err = "invalid_number";
        return false;
    }
    if (neg) {
        err = "negative_number";
        return false;
    }
    if (int_part > (0x7fffffffull >> 16)) {
        err = "number_overflow";
        return false;
    }
    {
        u64 scaled = int_part * 65536ull;
        if (frac_digits > 0) {
            u64 frac_scaled = (frac_part * 65536ull + (frac_div / 2ull)) / frac_div;
            scaled += frac_scaled;
        }
        if (scaled > 0x7fffffffull) {
            err = "number_overflow";
            return false;
        }
        out = (i32)scaled;
    }
    return true;
}

static bool parse_string_array(const std::string &s,
                               std::vector<std::string> &out,
                               std::string &err) {
    std::string t = trim(s);
    std::string cur;
    bool in_string = false;
    size_t i;
    if (t.size() < 2u || t[0] != '[' || t[t.size() - 1u] != ']') {
        err = "invalid_array";
        return false;
    }
    t = trim(t.substr(1u, t.size() - 2u));
    for (i = 0u; i < t.size(); ++i) {
        char c = t[i];
        if (c == '"' && (i == 0u || t[i - 1u] != '\\')) {
            in_string = !in_string;
            cur.push_back(c);
        } else if (c == ',' && !in_string) {
            std::string item = trim(cur);
            std::string val;
            if (!item.empty()) {
                if (!parse_string(item, val, err)) {
                    return false;
                }
                out.push_back(val);
            }
            cur.clear();
        } else {
            cur.push_back(c);
        }
    }
    if (!cur.empty()) {
        std::string item = trim(cur);
        std::string val;
        if (!parse_string(item, val, err)) {
            return false;
        }
        out.push_back(val);
    }
    return true;
}

static std::string to_lower(const std::string &s) {
    std::string out;
    out.reserve(s.size());
    for (size_t i = 0u; i < s.size(); ++i) {
        out.push_back((char)std::tolower((unsigned char)s[i]));
    }
    return out;
}

static bool parse_capability_id(const std::string &value,
                                dom_capability_id &out) {
    std::string name;
    std::string err;
    if (!value.empty() && value[0] == '"') {
        if (!parse_string(value, name, err)) {
            return false;
        }
    } else {
        name = trim(value);
    }
    name = to_lower(name);
    for (size_t i = 0u; i < name.size(); ++i) {
        if (name[i] == '-') {
            name[i] = '_';
        }
    }
    if (name == "time_readout" || name == "time") {
        out = DOM_CAP_TIME_READOUT;
        return true;
    }
    if (name == "calendar_view" || name == "calendar") {
        out = DOM_CAP_CALENDAR_VIEW;
        return true;
    }
    if (name == "map_view" || name == "map") {
        out = DOM_CAP_MAP_VIEW;
        return true;
    }
    if (name == "position_estimate" || name == "position") {
        out = DOM_CAP_POSITION_ESTIMATE;
        return true;
    }
    if (name == "health_status" || name == "health") {
        out = DOM_CAP_HEALTH_STATUS;
        return true;
    }
    if (name == "inventory_summary" || name == "inventory") {
        out = DOM_CAP_INVENTORY_SUMMARY;
        return true;
    }
    if (name == "economic_account" || name == "economy") {
        out = DOM_CAP_ECONOMIC_ACCOUNT;
        return true;
    }
    if (name == "market_quotes" || name == "market") {
        out = DOM_CAP_MARKET_QUOTES;
        return true;
    }
    if (name == "communications" || name == "comms") {
        out = DOM_CAP_COMMUNICATIONS;
        return true;
    }
    if (name == "command_status" || name == "commands") {
        out = DOM_CAP_COMMAND_STATUS;
        return true;
    }
    if (name == "environmental_status" || name == "environment") {
        out = DOM_CAP_ENVIRONMENTAL_STATUS;
        return true;
    }
    if (name == "legal_status" || name == "legal") {
        out = DOM_CAP_LEGAL_STATUS;
        return true;
    }
    return false;
}

static bool parse_anchor(const std::string &value, DomUiWidgetAnchor &out) {
    std::string name;
    std::string err;
    if (!value.empty() && value[0] == '"') {
        if (!parse_string(value, name, err)) {
            return false;
        }
    } else {
        name = trim(value);
    }
    name = to_lower(name);
    if (name == "top_left") {
        out = DOM_UI_ANCHOR_TOP_LEFT;
        return true;
    }
    if (name == "top_right") {
        out = DOM_UI_ANCHOR_TOP_RIGHT;
        return true;
    }
    if (name == "bottom_left") {
        out = DOM_UI_ANCHOR_BOTTOM_LEFT;
        return true;
    }
    if (name == "bottom_right") {
        out = DOM_UI_ANCHOR_BOTTOM_RIGHT;
        return true;
    }
    if (name == "center") {
        out = DOM_UI_ANCHOR_CENTER;
        return true;
    }
    return false;
}

static bool parse_projection(const std::string &value, DomUiWidgetProjection &out) {
    std::string name;
    std::string err;
    if (!value.empty() && value[0] == '"') {
        if (!parse_string(value, name, err)) {
            return false;
        }
    } else {
        name = trim(value);
    }
    name = to_lower(name);
    if (name == "diegetic") {
        out = DOM_UI_PROJECTION_DIEGETIC;
        return true;
    }
    if (name == "hud" || name == "hud_overlay") {
        out = DOM_UI_PROJECTION_HUD_OVERLAY;
        return true;
    }
    if (name == "world" || name == "world_surface") {
        out = DOM_UI_PROJECTION_WORLD_SURFACE;
        return true;
    }
    if (name == "debug") {
        out = DOM_UI_PROJECTION_DEBUG;
        return true;
    }
    return false;
}

static bool parse_resolution(const std::string &value, u32 &out, std::string &err) {
    std::string name;
    u32 number = 0u;
    if (!value.empty() && value[0] == '"') {
        if (!parse_string(value, name, err)) {
            return false;
        }
        name = to_lower(name);
        if (name == "unknown") {
            out = DOM_RESOLUTION_UNKNOWN;
            return true;
        }
        if (name == "binary") {
            out = DOM_RESOLUTION_BINARY;
            return true;
        }
        if (name == "coarse") {
            out = DOM_RESOLUTION_COARSE;
            return true;
        }
        if (name == "bounded") {
            out = DOM_RESOLUTION_BOUNDED;
            return true;
        }
        if (name == "exact") {
            out = DOM_RESOLUTION_EXACT;
            return true;
        }
        err = "invalid_resolution";
        return false;
    }
    if (!parse_u32(value, number, err)) {
        return false;
    }
    out = number;
    return true;
}

static void init_widget_default(DomUiWidgetDefinition &def) {
    def.id.clear();
    def.label.clear();
    def.required_caps.clear();
    def.min_resolution = DOM_RESOLUTION_UNKNOWN;
    def.allow_uncertainty = 1;
    def.width_px = 220;
    def.height_px = 40;
    def.draw_panel = 1;
}

static void init_profile_default(DomUiLayoutProfile &profile) {
    profile.id.clear();
    profile.projection = DOM_UI_PROJECTION_HUD_OVERLAY;
    profile.instances.clear();
}

static void init_instance_default(DomUiWidgetInstance &inst,
                                  DomUiWidgetProjection profile_proj) {
    inst.widget_id.clear();
    inst.projection = profile_proj;
    inst.anchor = DOM_UI_ANCHOR_TOP_LEFT;
    inst.x = 0;
    inst.y = 0;
    inst.scale_q16 = (1 << 16);
    inst.opacity_q16 = (1 << 16);
    inst.enabled = 1;
    inst.input_binding.clear();
}

static d_gfx_color make_color(u8 r, u8 g, u8 b, u8 a) {
    d_gfx_color c;
    c.a = a;
    c.r = r;
    c.g = g;
    c.b = b;
    return c;
}

static d_gfx_color apply_alpha(d_gfx_color c, u8 alpha) {
    u32 scaled = (u32)c.a * (u32)alpha;
    c.a = (u8)(scaled / 255u);
    return c;
}

static u8 alpha_from_q16(i32 opacity_q16) {
    i64 v = opacity_q16;
    if (v < 0) v = 0;
    if (v > (1 << 16)) v = (1 << 16);
    return (u8)((v * 255) / (1 << 16));
}

static int scale_i32(int value, i32 scale_q16) {
    i64 s = scale_q16;
    i64 scaled;
    if (s <= 0) {
        s = (1 << 16);
    }
    scaled = ((i64)value * s) >> 16;
    if (scaled < 1) {
        scaled = 1;
    }
    if (scaled > 0x7fffffffLL) {
        scaled = 0x7fffffffLL;
    }
    return (int)scaled;
}

static void emit_rect(d_gfx_cmd_buffer *buf,
                      int x,
                      int y,
                      int w,
                      int h,
                      d_gfx_color color) {
    d_gfx_draw_rect_cmd r;
    if (!buf || w <= 0 || h <= 0) {
        return;
    }
    r.x = x;
    r.y = y;
    r.w = w;
    r.h = h;
    r.color = color;
    d_gfx_cmd_draw_rect(buf, &r);
}

static void emit_text(d_gfx_cmd_buffer *buf,
                      int x,
                      int y,
                      d_gfx_color color,
                      const char *text) {
    d_gfx_draw_text_cmd t;
    if (!buf || !text) {
        return;
    }
    t.x = x;
    t.y = y;
    t.color = color;
    t.text = text;
    d_gfx_cmd_draw_text(buf, &t);
}

static void resolve_anchor(DomUiWidgetAnchor anchor,
                           int base_x,
                           int base_y,
                           int w,
                           int h,
                           int screen_w,
                           int screen_h,
                           int &out_x,
                           int &out_y) {
    int x = base_x;
    int y = base_y;
    switch (anchor) {
    case DOM_UI_ANCHOR_TOP_RIGHT:
        x = screen_w - base_x - w;
        break;
    case DOM_UI_ANCHOR_BOTTOM_LEFT:
        y = screen_h - base_y - h;
        break;
    case DOM_UI_ANCHOR_BOTTOM_RIGHT:
        x = screen_w - base_x - w;
        y = screen_h - base_y - h;
        break;
    case DOM_UI_ANCHOR_CENTER:
        x = (screen_w / 2) + base_x - (w / 2);
        y = (screen_h / 2) + base_y - (h / 2);
        break;
    case DOM_UI_ANCHOR_TOP_LEFT:
    default:
        break;
    }
    out_x = x;
    out_y = y;
}

static const dom_capability *find_capability(const dom_capability_snapshot *snapshot,
                                             dom_capability_id cap_id) {
    if (!snapshot || !snapshot->capabilities) {
        return 0;
    }
    for (u32 i = 0u; i < snapshot->capability_count; ++i) {
        const dom_capability *cap = snapshot->capabilities + i;
        if (cap->capability_id == cap_id) {
            return cap;
        }
    }
    return 0;
}

static std::vector<std::string> g_text_scratch;

static bool def_less(const DomUiWidgetDefinition &a, const DomUiWidgetDefinition &b) {
    return a.id < b.id;
}

static bool profile_less(const DomUiLayoutProfile &a, const DomUiLayoutProfile &b) {
    return a.id < b.id;
}

static bool append_capability(std::vector<dom_capability_id> &caps,
                              dom_capability_id id) {
    if (id == 0u) {
        return false;
    }
    if (std::find(caps.begin(), caps.end(), id) != caps.end()) {
        return true;
    }
    caps.push_back(id);
    return true;
}

} // namespace

bool dom_ui_widgets_load_definitions(const std::string &path,
                                     DomUiWidgetRegistry &out,
                                     std::string &err) {
    std::vector<std::string> lines;
    DomUiWidgetDefinition current;
    std::vector<std::string> seen;
    std::vector<std::string> ids;
    bool in_widget = false;
    int line_no = 0;

    err.clear();
    out.definitions.clear();
    init_widget_default(current);

    if (!read_lines(path, lines, err)) {
        set_error(err, path, 0, err);
        return false;
    }

    for (size_t i = 0u; i < lines.size(); ++i) {
        std::string raw = strip_comment(lines[i]);
        std::string line = trim(raw);
        std::string key;
        std::string value;
        std::string perr;
        ++line_no;
        if (line.empty()) {
            continue;
        }
        if (line == "[[widget]]") {
            if (in_widget) {
                if (current.id.empty()) {
                    set_error(err, path, line_no, "widget_missing_id");
                    return false;
                }
                if (current.required_caps.empty()) {
                    set_error(err, path, line_no, "widget_missing_capability");
                    return false;
                }
                if (std::find(ids.begin(), ids.end(), current.id) != ids.end()) {
                    set_error(err, path, line_no, "duplicate_widget_id");
                    return false;
                }
                ids.push_back(current.id);
                out.definitions.push_back(current);
                init_widget_default(current);
                seen.clear();
            } else {
                in_widget = true;
            }
            continue;
        }
        if (!in_widget) {
            set_error(err, path, line_no, "field_outside_widget");
            return false;
        }
        if (!parse_key_value(line, key, value)) {
            set_error(err, path, line_no, "invalid_kv");
            return false;
        }
        if (std::find(seen.begin(), seen.end(), key) != seen.end()) {
            set_error(err, path, line_no, "duplicate_key");
            return false;
        }
        seen.push_back(key);
        if (key == "id") {
            if (!parse_string(value, current.id, perr)) {
                set_error(err, path, line_no, perr);
                return false;
            }
        } else if (key == "label") {
            if (!parse_string(value, current.label, perr)) {
                set_error(err, path, line_no, perr);
                return false;
            }
        } else if (key == "capability") {
            dom_capability_id cap = 0u;
            if (!parse_capability_id(value, cap)) {
                set_error(err, path, line_no, "invalid_capability");
                return false;
            }
            append_capability(current.required_caps, cap);
        } else if (key == "required_capabilities") {
            std::vector<std::string> items;
            if (!parse_string_array(value, items, perr)) {
                set_error(err, path, line_no, perr);
                return false;
            }
            for (size_t j = 0u; j < items.size(); ++j) {
                dom_capability_id cap = 0u;
                if (!parse_capability_id(items[j], cap)) {
                    set_error(err, path, line_no, "invalid_capability");
                    return false;
                }
                append_capability(current.required_caps, cap);
            }
        } else if (key == "min_resolution") {
            if (!parse_resolution(value, current.min_resolution, perr)) {
                set_error(err, path, line_no, perr);
                return false;
            }
        } else if (key == "allow_uncertainty") {
            if (!parse_bool(value, current.allow_uncertainty, perr)) {
                set_error(err, path, line_no, perr);
                return false;
            }
        } else if (key == "width_px") {
            if (!parse_i32(value, current.width_px, perr)) {
                set_error(err, path, line_no, perr);
                return false;
            }
        } else if (key == "height_px") {
            if (!parse_i32(value, current.height_px, perr)) {
                set_error(err, path, line_no, perr);
                return false;
            }
        } else if (key == "draw_panel") {
            if (!parse_bool(value, current.draw_panel, perr)) {
                set_error(err, path, line_no, perr);
                return false;
            }
        } else {
            set_error(err, path, line_no, "unknown_field");
            return false;
        }
    }
    if (in_widget) {
        if (current.id.empty()) {
            set_error(err, path, line_no, "widget_missing_id");
            return false;
        }
        if (current.required_caps.empty()) {
            set_error(err, path, line_no, "widget_missing_capability");
            return false;
        }
        if (std::find(ids.begin(), ids.end(), current.id) != ids.end()) {
            set_error(err, path, line_no, "duplicate_widget_id");
            return false;
        }
        ids.push_back(current.id);
        out.definitions.push_back(current);
    }
    std::sort(out.definitions.begin(), out.definitions.end(), def_less);
    return true;
}

bool dom_ui_widgets_load_layouts(const std::string &path,
                                 DomUiLayoutSet &out,
                                 std::string &err) {
    std::vector<std::string> lines;
    DomUiLayoutProfile profile;
    DomUiWidgetInstance instance;
    std::vector<std::string> seen;
    std::vector<std::string> profile_ids;
    bool in_profile = false;
    bool in_instance = false;
    int line_no = 0;

    err.clear();
    out.profiles.clear();
    init_profile_default(profile);
    init_instance_default(instance, profile.projection);

    if (!read_lines(path, lines, err)) {
        set_error(err, path, 0, err);
        return false;
    }

    for (size_t i = 0u; i < lines.size(); ++i) {
        std::string raw = strip_comment(lines[i]);
        std::string line = trim(raw);
        std::string key;
        std::string value;
        std::string perr;
        ++line_no;
        if (line.empty()) {
            continue;
        }
        if (line == "[[profile]]") {
            if (in_instance) {
                if (instance.widget_id.empty()) {
                    set_error(err, path, line_no, "instance_missing_widget_id");
                    return false;
                }
                profile.instances.push_back(instance);
                in_instance = false;
            }
            if (in_profile) {
                if (profile.id.empty()) {
                    set_error(err, path, line_no, "profile_missing_id");
                    return false;
                }
                if (std::find(profile_ids.begin(), profile_ids.end(), profile.id) != profile_ids.end()) {
                    set_error(err, path, line_no, "duplicate_profile_id");
                    return false;
                }
                profile_ids.push_back(profile.id);
                out.profiles.push_back(profile);
                init_profile_default(profile);
            } else {
                in_profile = true;
            }
            seen.clear();
            continue;
        }
        if (line == "[[instance]]") {
            if (!in_profile) {
                set_error(err, path, line_no, "instance_outside_profile");
                return false;
            }
            if (in_instance) {
                if (instance.widget_id.empty()) {
                    set_error(err, path, line_no, "instance_missing_widget_id");
                    return false;
                }
                profile.instances.push_back(instance);
            }
            init_instance_default(instance, profile.projection);
            in_instance = true;
            seen.clear();
            continue;
        }
        if (!parse_key_value(line, key, value)) {
            set_error(err, path, line_no, "invalid_kv");
            return false;
        }
        if (std::find(seen.begin(), seen.end(), key) != seen.end()) {
            set_error(err, path, line_no, "duplicate_key");
            return false;
        }
        seen.push_back(key);
        if (in_instance) {
            if (key == "widget_id") {
                if (!parse_string(value, instance.widget_id, perr)) {
                    set_error(err, path, line_no, perr);
                    return false;
                }
            } else if (key == "projection") {
                if (!parse_projection(value, instance.projection)) {
                    set_error(err, path, line_no, "invalid_projection");
                    return false;
                }
            } else if (key == "anchor") {
                if (!parse_anchor(value, instance.anchor)) {
                    set_error(err, path, line_no, "invalid_anchor");
                    return false;
                }
            } else if (key == "x") {
                if (!parse_i32(value, instance.x, perr)) {
                    set_error(err, path, line_no, perr);
                    return false;
                }
            } else if (key == "y") {
                if (!parse_i32(value, instance.y, perr)) {
                    set_error(err, path, line_no, perr);
                    return false;
                }
            } else if (key == "scale") {
                if (!parse_q16_16(value, instance.scale_q16, perr)) {
                    set_error(err, path, line_no, perr);
                    return false;
                }
            } else if (key == "opacity") {
                if (!parse_q16_16(value, instance.opacity_q16, perr)) {
                    set_error(err, path, line_no, perr);
                    return false;
                }
            } else if (key == "enabled") {
                if (!parse_bool(value, instance.enabled, perr)) {
                    set_error(err, path, line_no, perr);
                    return false;
                }
            } else if (key == "input_binding") {
                if (!parse_string(value, instance.input_binding, perr)) {
                    set_error(err, path, line_no, perr);
                    return false;
                }
            } else {
                set_error(err, path, line_no, "unknown_field");
                return false;
            }
        } else if (in_profile) {
            if (key == "id") {
                if (!parse_string(value, profile.id, perr)) {
                    set_error(err, path, line_no, perr);
                    return false;
                }
            } else if (key == "projection") {
                if (!parse_projection(value, profile.projection)) {
                    set_error(err, path, line_no, "invalid_projection");
                    return false;
                }
            } else {
                set_error(err, path, line_no, "unknown_field");
                return false;
            }
        } else {
            set_error(err, path, line_no, "field_outside_profile");
            return false;
        }
    }
    if (in_instance) {
        if (instance.widget_id.empty()) {
            set_error(err, path, line_no, "instance_missing_widget_id");
            return false;
        }
        profile.instances.push_back(instance);
    }
    if (in_profile) {
        if (profile.id.empty()) {
            set_error(err, path, line_no, "profile_missing_id");
            return false;
        }
        if (std::find(profile_ids.begin(), profile_ids.end(), profile.id) != profile_ids.end()) {
            set_error(err, path, line_no, "duplicate_profile_id");
            return false;
        }
        profile_ids.push_back(profile.id);
        out.profiles.push_back(profile);
    }
    std::sort(out.profiles.begin(), out.profiles.end(), profile_less);
    return true;
}

bool dom_ui_widgets_save_layouts(const std::string &path,
                                 const DomUiLayoutSet &layouts,
                                 std::string &err) {
    std::ofstream out(path.c_str(), std::ios::out | std::ios::trunc);
    err.clear();
    if (!out.is_open()) {
        err = "open_failed";
        return false;
    }
    for (size_t i = 0u; i < layouts.profiles.size(); ++i) {
        const DomUiLayoutProfile &profile = layouts.profiles[i];
        out << "[[profile]]\n";
        out << "id = \"" << profile.id << "\"\n";
        switch (profile.projection) {
        case DOM_UI_PROJECTION_DIEGETIC: out << "projection = \"diegetic\"\n"; break;
        case DOM_UI_PROJECTION_WORLD_SURFACE: out << "projection = \"world_surface\"\n"; break;
        case DOM_UI_PROJECTION_DEBUG: out << "projection = \"debug\"\n"; break;
        case DOM_UI_PROJECTION_HUD_OVERLAY:
        default: out << "projection = \"hud\"\n"; break;
        }
        for (size_t j = 0u; j < profile.instances.size(); ++j) {
            const DomUiWidgetInstance &inst = profile.instances[j];
            int scale_int = inst.scale_q16 >> 16;
            int scale_frac = (int)(((u32)(inst.scale_q16 & 0xffff) * 1000u) / 65536u);
            int op_int = inst.opacity_q16 >> 16;
            int op_frac = (int)(((u32)(inst.opacity_q16 & 0xffff) * 1000u) / 65536u);
            out << "\n[[instance]]\n";
            out << "widget_id = \"" << inst.widget_id << "\"\n";
            out << "x = " << inst.x << "\n";
            out << "y = " << inst.y << "\n";
            out << "scale = " << scale_int << "." << (scale_frac < 100 ? "0" : "")
                << (scale_frac < 10 ? "0" : "") << scale_frac << "\n";
            out << "opacity = " << op_int << "." << (op_frac < 100 ? "0" : "")
                << (op_frac < 10 ? "0" : "") << op_frac << "\n";
            out << "enabled = " << (inst.enabled ? "true" : "false") << "\n";
            if (!inst.input_binding.empty()) {
                out << "input_binding = \"" << inst.input_binding << "\"\n";
            }
            switch (inst.anchor) {
            case DOM_UI_ANCHOR_TOP_RIGHT: out << "anchor = \"top_right\"\n"; break;
            case DOM_UI_ANCHOR_BOTTOM_LEFT: out << "anchor = \"bottom_left\"\n"; break;
            case DOM_UI_ANCHOR_BOTTOM_RIGHT: out << "anchor = \"bottom_right\"\n"; break;
            case DOM_UI_ANCHOR_CENTER: out << "anchor = \"center\"\n"; break;
            case DOM_UI_ANCHOR_TOP_LEFT:
            default: out << "anchor = \"top_left\"\n"; break;
            }
            switch (inst.projection) {
            case DOM_UI_PROJECTION_DIEGETIC: out << "projection = \"diegetic\"\n"; break;
            case DOM_UI_PROJECTION_WORLD_SURFACE: out << "projection = \"world_surface\"\n"; break;
            case DOM_UI_PROJECTION_DEBUG: out << "projection = \"debug\"\n"; break;
            case DOM_UI_PROJECTION_HUD_OVERLAY:
            default: out << "projection = \"hud\"\n"; break;
            }
        }
        out << "\n";
    }
    return true;
}

namespace {

static bool cap_is_unknown(const dom_capability *cap,
                           const DomUiWidgetDefinition &def) {
    if (!cap) {
        return true;
    }
    if (cap->flags & DOM_CAPABILITY_FLAG_UNKNOWN) {
        return true;
    }
    if (cap->resolution_tier < def.min_resolution) {
        return true;
    }
    return false;
}

static std::string format_value(const dom_capability *cap,
                                const DomUiWidgetDefinition &def,
                                bool unknown) {
    char buf[64];
    if (unknown || !cap) {
        return "UNKNOWN";
    }
    if (cap->resolution_tier == DOM_RESOLUTION_BINARY) {
        return (cap->value_max > 0) ? "YES" : "NO";
    }
    if (cap->resolution_tier == DOM_RESOLUTION_EXACT || cap->value_min == cap->value_max) {
        std::snprintf(buf, sizeof(buf), "%lld", (long long)cap->value_min);
        return std::string(buf);
    }
    std::snprintf(buf, sizeof(buf), "%lld..%lld",
                  (long long)cap->value_min,
                  (long long)cap->value_max);
    return std::string(buf);
}

static void append_flag(std::string &text, const char *flag) {
    if (!flag || !flag[0]) {
        return;
    }
    text.push_back(' ');
    text.push_back('(');
    text.append(flag);
    text.push_back(')');
}

} // namespace

void dom_ui_widgets_default(DomUiWidgetRegistry &defs, DomUiLayoutSet &layouts) {
    defs.definitions.clear();
    layouts.profiles.clear();

    {
        DomUiWidgetDefinition def;
        init_widget_default(def);
        def.id = "time";
        def.label = "Time";
        def.min_resolution = DOM_RESOLUTION_BINARY;
        def.allow_uncertainty = 1;
        def.required_caps.push_back(DOM_CAP_TIME_READOUT);
        defs.definitions.push_back(def);
    }
    {
        DomUiWidgetDefinition def;
        init_widget_default(def);
        def.id = "health";
        def.label = "Health";
        def.min_resolution = DOM_RESOLUTION_COARSE;
        def.allow_uncertainty = 0;
        def.required_caps.push_back(DOM_CAP_HEALTH_STATUS);
        defs.definitions.push_back(def);
    }
    {
        DomUiWidgetDefinition def;
        init_widget_default(def);
        def.id = "inventory";
        def.label = "Inventory";
        def.min_resolution = DOM_RESOLUTION_COARSE;
        def.required_caps.push_back(DOM_CAP_INVENTORY_SUMMARY);
        defs.definitions.push_back(def);
    }
    {
        DomUiWidgetDefinition def;
        init_widget_default(def);
        def.id = "map";
        def.label = "Map";
        def.min_resolution = DOM_RESOLUTION_BINARY;
        def.required_caps.push_back(DOM_CAP_MAP_VIEW);
        defs.definitions.push_back(def);
    }

    std::sort(defs.definitions.begin(), defs.definitions.end(), def_less);

    {
        DomUiLayoutProfile profile;
        DomUiWidgetInstance inst;
        init_profile_default(profile);
        profile.id = "default";
        profile.projection = DOM_UI_PROJECTION_HUD_OVERLAY;

        init_instance_default(inst, profile.projection);
        inst.widget_id = "time";
        inst.x = 16;
        inst.y = 16;
        inst.anchor = DOM_UI_ANCHOR_TOP_LEFT;
        profile.instances.push_back(inst);

        init_instance_default(inst, profile.projection);
        inst.widget_id = "health";
        inst.x = 16;
        inst.y = 64;
        inst.anchor = DOM_UI_ANCHOR_TOP_LEFT;
        profile.instances.push_back(inst);

        init_instance_default(inst, profile.projection);
        inst.widget_id = "inventory";
        inst.x = 16;
        inst.y = 112;
        inst.anchor = DOM_UI_ANCHOR_TOP_LEFT;
        profile.instances.push_back(inst);

        layouts.profiles.push_back(profile);
    }
}

const DomUiWidgetDefinition *dom_ui_widgets_find_definition(
    const DomUiWidgetRegistry &defs,
    const std::string &id) {
    for (size_t i = 0u; i < defs.definitions.size(); ++i) {
        if (defs.definitions[i].id == id) {
            return &defs.definitions[i];
        }
    }
    return 0;
}

const DomUiLayoutProfile *dom_ui_widgets_find_profile(
    const DomUiLayoutSet &layouts,
    const std::string &id) {
    for (size_t i = 0u; i < layouts.profiles.size(); ++i) {
        if (layouts.profiles[i].id == id) {
            return &layouts.profiles[i];
        }
    }
    return 0;
}

void dom_ui_widgets_render(const DomUiWidgetRegistry &defs,
                           const DomUiLayoutProfile &profile,
                           const dom_capability_snapshot *snapshot,
                           const DomUiWidgetRenderParams &params) {
    if (!params.buf) {
        return;
    }
    g_text_scratch.clear();
    g_text_scratch.reserve(profile.instances.size());

    for (size_t i = 0u; i < profile.instances.size(); ++i) {
        const DomUiWidgetInstance &inst = profile.instances[i];
        const DomUiWidgetDefinition *def = 0;
        const dom_capability *cap = 0;
        bool unknown = false;
        int width;
        int height;
        int x;
        int y;
        u8 alpha;
        d_gfx_color panel;
        d_gfx_color text_col;
        std::string label;
        std::string value;
        std::string text;

        if (!inst.enabled) {
            continue;
        }
        if (inst.projection != params.projection) {
            continue;
        }
        def = dom_ui_widgets_find_definition(defs, inst.widget_id);
        if (!def) {
            continue;
        }
        if (!def->required_caps.empty()) {
            for (size_t j = 0u; j < def->required_caps.size(); ++j) {
                const dom_capability *found = find_capability(snapshot, def->required_caps[j]);
                if (!found) {
                    unknown = true;
                } else if (!cap) {
                    cap = found;
                }
            }
        }
        if (cap_is_unknown(cap, *def)) {
            unknown = true;
        }
        if (unknown && !def->allow_uncertainty) {
            continue;
        }

        label = def->label.empty() ? def->id : def->label;
        value = format_value(cap, *def, unknown);
        text = label + ": " + value;
        if (cap && (cap->flags & DOM_CAPABILITY_FLAG_STALE)) {
            append_flag(text, "stale");
        }
        if (cap && (cap->flags & DOM_CAPABILITY_FLAG_DEGRADED)) {
            append_flag(text, "degraded");
        }
        if (cap && (cap->flags & DOM_CAPABILITY_FLAG_CONFLICT)) {
            append_flag(text, "conflict");
        }

        g_text_scratch.push_back(text);

        width = scale_i32(def->width_px, inst.scale_q16);
        height = scale_i32(def->height_px, inst.scale_q16);
        resolve_anchor(inst.anchor, inst.x, inst.y, width, height,
                       params.width, params.height, x, y);

        alpha = alpha_from_q16(inst.opacity_q16);
        panel = apply_alpha(make_color(0x16u, 0x18u, 0x1eu, 0xffu), alpha);
        text_col = apply_alpha(make_color(0xe0u, 0xe0u, 0xe0u, 0xffu), alpha);

        if (def->draw_panel) {
            emit_rect(params.buf, x, y, width, height, panel);
        }
        emit_text(params.buf, x + 8, y + (height / 2) - 6,
                  text_col, g_text_scratch.back().c_str());
    }
}

} // namespace dom
