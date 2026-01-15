/*
FILE: source/dominium/tools/coredata_compile/coredata_load.cpp
MODULE: Dominium
PURPOSE: Coredata compiler loader (TOML authoring -> in-memory structs).
*/

#include "coredata_load.h"

#include <algorithm>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>

#include "dom_paths.h"

namespace dom {
namespace tools {

CoredataAnchor::CoredataAnchor()
    : id(),
      kind(),
      display_name(),
      system_class(),
      region_type(),
      evidence_grade(),
      mechanics_profile_id(),
      anchor_weight(0u),
      tags(),
      has_present_pos(false) {
    present_pos_q16[0] = 0;
    present_pos_q16[1] = 0;
    present_pos_q16[2] = 0;
}

CoredataProceduralRules::CoredataProceduralRules()
    : present(false),
      systems_per_anchor_min(0u),
      systems_per_anchor_max(0u),
      red_dwarf_ratio_q16(0),
      binary_ratio_q16(0),
      exotic_ratio_q16(0),
      cluster_density(),
      metallicity_bias(),
      hazard_frequency() {
}

CoredataSystemProfile::CoredataSystemProfile()
    : id(),
      navigation_instability_q16(0),
      debris_collision_q16(0),
      radiation_baseline_q16(0),
      warp_cap_q16(0),
      survey_difficulty_q16(0),
      has_supernova_ticks(false),
      supernova_timer_ticks(0ull) {
}

CoredataSiteProfile::CoredataSiteProfile()
    : id(),
      hazard_radiation_q16(0),
      hazard_pressure_q16(0),
      corrosion_rate_q16(0),
      temperature_extreme_q16(0),
      resource_yield(),
      access_constraints() {
}

CoredataAstroBody::CoredataAstroBody()
    : id(),
      has_radius(false),
      radius_m(0ull),
      mu_mantissa(0ull),
      mu_exp10(0),
      has_rotation_rate(false),
      rotation_rate_q16(0),
      atmosphere_profile_id() {
}

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

static void add_error(std::vector<CoredataError> &errors,
                      const std::string &path,
                      int line,
                      const char *code,
                      const std::string &message) {
    CoredataError e;
    e.path = path;
    e.line = line;
    e.code = code ? code : "error";
    e.message = message;
    errors.push_back(e);
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
    out = (u32)v;
    return true;
}

static bool parse_u64(const std::string &s, u64 &out, std::string &err) {
    char *end = 0;
    unsigned long long v;
    if (s.empty()) {
        err = "empty_number";
        return false;
    }
    v = std::strtoull(s.c_str(), &end, 10);
    if (!end || end[0] != '\0') {
        err = "invalid_number";
        return false;
    }
    out = (u64)v;
    return true;
}

struct DecNumber {
    bool negative;
    std::string digits;
    int frac_digits;
    int exp10;
};

static bool parse_decimal(const std::string &s, DecNumber &out, std::string &err) {
    size_t i = 0u;
    bool neg = false;
    bool has_dot = false;
    bool has_digit = false;
    std::string digits;
    int frac_digits = 0;
    int exp10 = 0;
    if (s.empty()) {
        err = "empty_number";
        return false;
    }
    if (s[i] == '+' || s[i] == '-') {
        neg = (s[i] == '-');
        ++i;
    }
    for (; i < s.size(); ++i) {
        char c = s[i];
        if (c >= '0' && c <= '9') {
            digits.push_back(c);
            if (has_dot) {
                ++frac_digits;
            }
            has_digit = true;
        } else if (c == '.' && !has_dot) {
            has_dot = true;
        } else {
            break;
        }
    }
    if (!has_digit) {
        err = "invalid_number";
        return false;
    }
    if (i < s.size()) {
        char c = s[i];
        if (c != 'e' && c != 'E') {
            err = "invalid_number";
            return false;
        }
        ++i;
        if (i >= s.size()) {
            err = "invalid_exponent";
            return false;
        }
        {
            bool exp_neg = false;
            if (s[i] == '+' || s[i] == '-') {
                exp_neg = (s[i] == '-');
                ++i;
            }
            if (i >= s.size()) {
                err = "invalid_exponent";
                return false;
            }
            int exp_val = 0;
            for (; i < s.size(); ++i) {
                char d = s[i];
                if (d < '0' || d > '9') {
                    err = "invalid_exponent";
                    return false;
                }
                exp_val = (exp_val * 10) + (d - '0');
            }
            exp10 = exp_neg ? -exp_val : exp_val;
        }
    }
    out.negative = neg;
    out.digits = digits;
    out.frac_digits = frac_digits;
    out.exp10 = exp10;
    return true;
}

static bool parse_digits_u64(const std::string &digits, u64 &out, std::string &err) {
    u64 v = 0ull;
    size_t i;
    if (digits.empty()) {
        err = "invalid_number";
        return false;
    }
    for (i = 0u; i < digits.size(); ++i) {
        char c = digits[i];
        if (c < '0' || c > '9') {
            err = "invalid_number";
            return false;
        }
        if (v > (0xffffffffffffffffull - 9ull) / 10ull) {
            err = "number_overflow";
            return false;
        }
        v = (v * 10ull) + (u64)(c - '0');
    }
    out = v;
    return true;
}

static bool mul_pow10_u64(u64 &value, int exp, std::string &err) {
    int i;
    if (exp < 0) {
        err = "negative_exponent";
        return false;
    }
    for (i = 0; i < exp; ++i) {
        if (value > 0xffffffffffffffffull / 10ull) {
            err = "number_overflow";
            return false;
        }
        value *= 10ull;
    }
    return true;
}

static bool parse_q16_16(const std::string &s, i32 &out, std::string &err) {
    DecNumber d;
    u64 num = 0ull;
    u64 denom = 1ull;
    u64 scaled = 0ull;
    u64 q = 0ull;
    int exp;
    if (!parse_decimal(trim(s), d, err)) {
        return false;
    }
    if (d.negative) {
        err = "negative_number";
        return false;
    }
    if (!parse_digits_u64(d.digits, num, err)) {
        return false;
    }
    exp = d.exp10 - d.frac_digits;
    if (exp >= 0) {
        if (!mul_pow10_u64(num, exp, err)) {
            return false;
        }
    } else {
        if (!mul_pow10_u64(denom, -exp, err)) {
            return false;
        }
    }
    if (num > (0xffffffffffffffffull / 65536ull)) {
        err = "number_overflow";
        return false;
    }
    scaled = num * 65536ull;
    q = (scaled + (denom / 2ull)) / denom;
    if (q > 0x7fffffffull) {
        err = "number_overflow";
        return false;
    }
    out = (i32)q;
    return true;
}

static bool parse_mantissa_exp10(const std::string &s,
                                 u64 &mantissa,
                                 i32 &exp10,
                                 std::string &err) {
    DecNumber d;
    u64 num = 0ull;
    int exp;
    if (!parse_decimal(trim(s), d, err)) {
        return false;
    }
    if (d.negative) {
        err = "negative_number";
        return false;
    }
    if (!parse_digits_u64(d.digits, num, err)) {
        return false;
    }
    exp = d.exp10 - d.frac_digits;
    while (num != 0ull && (num % 10ull) == 0ull) {
        num /= 10ull;
        exp += 1;
    }
    mantissa = num;
    exp10 = (i32)exp;
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

static bool parse_u32_array(const std::string &s,
                            std::vector<u32> &out,
                            std::string &err) {
    std::string t = trim(s);
    std::string cur;
    size_t i;
    if (t.size() < 2u || t[0] != '[' || t[t.size() - 1u] != ']') {
        err = "invalid_array";
        return false;
    }
    t = trim(t.substr(1u, t.size() - 2u));
    for (i = 0u; i < t.size(); ++i) {
        char c = t[i];
        if (c == ',') {
            std::string item = trim(cur);
            u32 val = 0u;
            if (!item.empty()) {
                if (!parse_u32(item, val, err)) {
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
        u32 val = 0u;
        if (!parse_u32(item, val, err)) {
            return false;
        }
        out.push_back(val);
    }
    return true;
}

static bool parse_inline_table(const std::string &s,
                               std::vector<CoredataResourceModifier> &out,
                               std::string &err) {
    std::string t = trim(s);
    std::string cur;
    size_t i;
    if (t.size() < 2u || t[0] != '{' || t[t.size() - 1u] != '}') {
        err = "invalid_inline_table";
        return false;
    }
    t = trim(t.substr(1u, t.size() - 2u));
    for (i = 0u; i < t.size(); ++i) {
        char c = t[i];
        if (c == ',') {
            std::string item = trim(cur);
            if (!item.empty()) {
                std::string k;
                std::string v;
                i32 q16 = 0;
                if (!parse_key_value(item, k, v)) {
                    err = "invalid_inline_table_entry";
                    return false;
                }
                if (!parse_q16_16(v, q16, err)) {
                    return false;
                }
                CoredataResourceModifier mod;
                mod.resource_id = trim(k);
                mod.modifier_q16 = q16;
                out.push_back(mod);
            }
            cur.clear();
        } else {
            cur.push_back(c);
        }
    }
    if (!cur.empty()) {
        std::string item = trim(cur);
        std::string k;
        std::string v;
        i32 q16 = 0;
        if (!parse_key_value(item, k, v)) {
            err = "invalid_inline_table_entry";
            return false;
        }
        if (!parse_q16_16(v, q16, err)) {
            return false;
        }
        CoredataResourceModifier mod;
        mod.resource_id = trim(k);
        mod.modifier_q16 = q16;
        out.push_back(mod);
    }
    return true;
}

static bool parse_anchor_file(const std::string &path,
                              std::vector<CoredataAnchor> &out,
                              std::vector<CoredataError> &errors) {
    std::vector<std::string> lines;
    std::string err;
    CoredataAnchor current;
    bool in_anchor = false;
    std::vector<std::string> seen;
    int line_no = 0;
    size_t i;
    if (!read_lines(path, lines, err)) {
        add_error(errors, path, 0, "file_error", err);
        return false;
    }
    for (i = 0u; i < lines.size(); ++i) {
        std::string raw = strip_comment(lines[i]);
        std::string line = trim(raw);
        std::string key;
        std::string value;
        ++line_no;
        if (line.empty()) {
            continue;
        }
        if (line == "[[anchor]]") {
            if (in_anchor) {
                out.push_back(current);
                current = CoredataAnchor();
                seen.clear();
            } else {
                in_anchor = true;
            }
            continue;
        }
        if (!in_anchor) {
            add_error(errors, path, line_no, "field_outside_anchor", line);
            continue;
        }
        if (!parse_key_value(line, key, value)) {
            add_error(errors, path, line_no, "invalid_kv", line);
            continue;
        }
        if (std::find(seen.begin(), seen.end(), key) != seen.end()) {
            add_error(errors, path, line_no, "duplicate_key", key);
            continue;
        }
        seen.push_back(key);
        if (key == "id") {
            if (!parse_string(value, current.id, err)) {
                add_error(errors, path, line_no, "invalid_id", err);
            }
        } else if (key == "kind") {
            if (!parse_string(value, current.kind, err)) {
                add_error(errors, path, line_no, "invalid_kind", err);
            }
        } else if (key == "display_name") {
            if (!parse_string(value, current.display_name, err)) {
                add_error(errors, path, line_no, "invalid_display_name", err);
            }
        } else if (key == "system_class") {
            if (!parse_string(value, current.system_class, err)) {
                add_error(errors, path, line_no, "invalid_system_class", err);
            }
        } else if (key == "region_type") {
            if (!parse_string(value, current.region_type, err)) {
                add_error(errors, path, line_no, "invalid_region_type", err);
            }
        } else if (key == "evidence_grade") {
            if (!parse_string(value, current.evidence_grade, err)) {
                add_error(errors, path, line_no, "invalid_evidence_grade", err);
            }
        } else if (key == "mechanics_profile_id") {
            if (!parse_string(value, current.mechanics_profile_id, err)) {
                add_error(errors, path, line_no, "invalid_mechanics_profile_id", err);
            }
        } else if (key == "anchor_weight") {
            if (!parse_u32(value, current.anchor_weight, err)) {
                add_error(errors, path, line_no, "invalid_anchor_weight", err);
            }
        } else if (key == "tags") {
            if (!parse_string_array(value, current.tags, err)) {
                add_error(errors, path, line_no, "invalid_tags", err);
            }
        } else if (key == "presentational_position") {
            std::vector<u32> parts;
            std::vector<std::string> items;
            i32 q16 = 0;
            size_t idx = 0u;
            if (!parse_string_array(value, items, err)) {
                err.clear();
                parts.clear();
                if (!parse_u32_array(value, parts, err) || parts.size() != 3u) {
                    add_error(errors, path, line_no, "invalid_presentational_position", err);
                    continue;
                }
                current.present_pos_q16[0] = (i32)(parts[0] << 16);
                current.present_pos_q16[1] = (i32)(parts[1] << 16);
                current.present_pos_q16[2] = (i32)(parts[2] << 16);
                current.has_present_pos = true;
                continue;
            }
            if (items.size() != 3u) {
                add_error(errors, path, line_no, "invalid_presentational_position", "need 3 values");
                continue;
            }
            for (idx = 0u; idx < 3u; ++idx) {
                if (!parse_q16_16(items[idx], q16, err)) {
                    add_error(errors, path, line_no, "invalid_presentational_position", err);
                    break;
                }
                current.present_pos_q16[idx] = q16;
            }
            current.has_present_pos = true;
        } else {
            add_error(errors, path, line_no, "unknown_field", key);
        }
    }
    if (in_anchor) {
        out.push_back(current);
    }
    return errors.empty();
}

static bool parse_system_profiles(const std::string &path,
                                  std::vector<CoredataSystemProfile> &out,
                                  std::vector<CoredataError> &errors) {
    std::vector<std::string> lines;
    std::string err;
    CoredataSystemProfile current;
    bool in_profile = false;
    std::vector<std::string> seen;
    int line_no = 0;
    size_t i;
    if (!read_lines(path, lines, err)) {
        add_error(errors, path, 0, "file_error", err);
        return false;
    }
    for (i = 0u; i < lines.size(); ++i) {
        std::string raw = strip_comment(lines[i]);
        std::string line = trim(raw);
        std::string key;
        std::string value;
        ++line_no;
        if (line.empty()) {
            continue;
        }
        if (line == "[[profile]]") {
            if (in_profile) {
                out.push_back(current);
                current = CoredataSystemProfile();
                seen.clear();
            } else {
                in_profile = true;
            }
            continue;
        }
        if (!in_profile) {
            add_error(errors, path, line_no, "field_outside_profile", line);
            continue;
        }
        if (!parse_key_value(line, key, value)) {
            add_error(errors, path, line_no, "invalid_kv", line);
            continue;
        }
        if (std::find(seen.begin(), seen.end(), key) != seen.end()) {
            add_error(errors, path, line_no, "duplicate_key", key);
            continue;
        }
        seen.push_back(key);
        if (key == "id") {
            if (!parse_string(value, current.id, err)) {
                add_error(errors, path, line_no, "invalid_id", err);
            }
        } else if (key == "navigation_instability_factor") {
            if (!parse_q16_16(value, current.navigation_instability_q16, err)) {
                add_error(errors, path, line_no, "invalid_navigation_instability", err);
            }
        } else if (key == "debris_collision_modifier") {
            if (!parse_q16_16(value, current.debris_collision_q16, err)) {
                add_error(errors, path, line_no, "invalid_debris_collision", err);
            }
        } else if (key == "radiation_baseline") {
            if (!parse_q16_16(value, current.radiation_baseline_q16, err)) {
                add_error(errors, path, line_no, "invalid_radiation_baseline", err);
            }
        } else if (key == "warp_cap_modifier") {
            if (!parse_q16_16(value, current.warp_cap_q16, err)) {
                add_error(errors, path, line_no, "invalid_warp_cap", err);
            }
        } else if (key == "survey_difficulty") {
            if (!parse_q16_16(value, current.survey_difficulty_q16, err)) {
                add_error(errors, path, line_no, "invalid_survey_difficulty", err);
            }
        } else if (key == "supernova_timer_ticks") {
            if (!parse_u64(value, current.supernova_timer_ticks, err)) {
                add_error(errors, path, line_no, "invalid_supernova_timer", err);
            } else {
                current.has_supernova_ticks = true;
            }
        } else {
            add_error(errors, path, line_no, "unknown_field", key);
        }
    }
    if (in_profile) {
        out.push_back(current);
    }
    return errors.empty();
}

static bool parse_site_profiles(const std::string &path,
                                std::vector<CoredataSiteProfile> &out,
                                std::vector<CoredataError> &errors) {
    std::vector<std::string> lines;
    std::string err;
    CoredataSiteProfile current;
    bool in_profile = false;
    std::vector<std::string> seen;
    int line_no = 0;
    size_t i;
    if (!read_lines(path, lines, err)) {
        add_error(errors, path, 0, "file_error", err);
        return false;
    }
    for (i = 0u; i < lines.size(); ++i) {
        std::string raw = strip_comment(lines[i]);
        std::string line = trim(raw);
        std::string key;
        std::string value;
        ++line_no;
        if (line.empty()) {
            continue;
        }
        if (line == "[[profile]]") {
            if (in_profile) {
                out.push_back(current);
                current = CoredataSiteProfile();
                seen.clear();
            } else {
                in_profile = true;
            }
            continue;
        }
        if (!in_profile) {
            add_error(errors, path, line_no, "field_outside_profile", line);
            continue;
        }
        if (!parse_key_value(line, key, value)) {
            add_error(errors, path, line_no, "invalid_kv", line);
            continue;
        }
        if (std::find(seen.begin(), seen.end(), key) != seen.end()) {
            add_error(errors, path, line_no, "duplicate_key", key);
            continue;
        }
        seen.push_back(key);
        if (key == "id") {
            if (!parse_string(value, current.id, err)) {
                add_error(errors, path, line_no, "invalid_id", err);
            }
        } else if (key == "hazard_radiation") {
            if (!parse_q16_16(value, current.hazard_radiation_q16, err)) {
                add_error(errors, path, line_no, "invalid_hazard_radiation", err);
            }
        } else if (key == "hazard_pressure") {
            if (!parse_q16_16(value, current.hazard_pressure_q16, err)) {
                add_error(errors, path, line_no, "invalid_hazard_pressure", err);
            }
        } else if (key == "corrosion_rate") {
            if (!parse_q16_16(value, current.corrosion_rate_q16, err)) {
                add_error(errors, path, line_no, "invalid_corrosion_rate", err);
            }
        } else if (key == "temperature_extreme") {
            if (!parse_q16_16(value, current.temperature_extreme_q16, err)) {
                add_error(errors, path, line_no, "invalid_temperature_extreme", err);
            }
        } else if (key == "resource_yield_modifiers") {
            if (!parse_inline_table(value, current.resource_yield, err)) {
                add_error(errors, path, line_no, "invalid_resource_yield_modifiers", err);
            }
        } else if (key == "access_constraints") {
            if (!parse_string_array(value, current.access_constraints, err)) {
                add_error(errors, path, line_no, "invalid_access_constraints", err);
            }
        } else {
            add_error(errors, path, line_no, "unknown_field", key);
        }
    }
    if (in_profile) {
        out.push_back(current);
    }
    return errors.empty();
}

static bool parse_procedural_rules(const std::string &path,
                                   CoredataProceduralRules &out,
                                   std::vector<CoredataError> &errors) {
    std::vector<std::string> lines;
    std::string err;
    std::string section;
    int line_no = 0;
    size_t i;
    if (!read_lines(path, lines, err)) {
        add_error(errors, path, 0, "file_error", err);
        return false;
    }
    out.present = true;
    for (i = 0u; i < lines.size(); ++i) {
        std::string raw = strip_comment(lines[i]);
        std::string line = trim(raw);
        std::string key;
        std::string value;
        ++line_no;
        if (line.empty()) {
            continue;
        }
        if (line[0] == '[' && line[line.size() - 1u] == ']') {
            section = trim(line.substr(1u, line.size() - 2u));
            continue;
        }
        if (!parse_key_value(line, key, value)) {
            add_error(errors, path, line_no, "invalid_kv", line);
            continue;
        }
        if (section == "procedural") {
            if (key == "systems_per_anchor_range") {
                std::vector<u32> range;
                if (!parse_u32_array(value, range, err) || range.size() != 2u) {
                    add_error(errors, path, line_no, "invalid_systems_per_anchor_range", err);
                    continue;
                }
                out.systems_per_anchor_min = range[0];
                out.systems_per_anchor_max = range[1];
            } else if (key == "red_dwarf_ratio") {
                if (!parse_q16_16(value, out.red_dwarf_ratio_q16, err)) {
                    add_error(errors, path, line_no, "invalid_red_dwarf_ratio", err);
                }
            } else if (key == "binary_ratio") {
                if (!parse_q16_16(value, out.binary_ratio_q16, err)) {
                    add_error(errors, path, line_no, "invalid_binary_ratio", err);
                }
            } else if (key == "exotic_ratio") {
                if (!parse_q16_16(value, out.exotic_ratio_q16, err)) {
                    add_error(errors, path, line_no, "invalid_exotic_ratio", err);
                }
            } else {
                add_error(errors, path, line_no, "unknown_field", key);
            }
        } else if (section == "procedural.cluster_density_multiplier") {
            CoredataRulesEntry entry;
            entry.region_type = key;
            if (!parse_q16_16(value, entry.value_q16, err)) {
                add_error(errors, path, line_no, "invalid_cluster_density", err);
            } else {
                out.cluster_density.push_back(entry);
            }
        } else if (section == "procedural.metallicity_bias_by_region_type") {
            CoredataRulesEntry entry;
            entry.region_type = key;
            if (!parse_q16_16(value, entry.value_q16, err)) {
                add_error(errors, path, line_no, "invalid_metallicity_bias", err);
            } else {
                out.metallicity_bias.push_back(entry);
            }
        } else if (section == "procedural.hazard_frequency_by_region_type") {
            CoredataRulesEntry entry;
            entry.region_type = key;
            if (!parse_q16_16(value, entry.value_q16, err)) {
                add_error(errors, path, line_no, "invalid_hazard_frequency", err);
            } else {
                out.hazard_frequency.push_back(entry);
            }
        } else {
            add_error(errors, path, line_no, "unknown_section", section);
        }
    }
    return errors.empty();
}

static bool parse_astro_constants(const std::string &path,
                                  std::vector<CoredataAstroBody> &out,
                                  std::vector<CoredataError> &errors) {
    std::vector<std::string> lines;
    std::string err;
    std::string section;
    CoredataAstroBody current;
    bool has_section = false;
    int line_no = 0;
    size_t i;
    if (!read_lines(path, lines, err)) {
        add_error(errors, path, 0, "file_error", err);
        return false;
    }
    for (i = 0u; i < lines.size(); ++i) {
        std::string raw = strip_comment(lines[i]);
        std::string line = trim(raw);
        std::string key;
        std::string value;
        ++line_no;
        if (line.empty()) {
            continue;
        }
        if (line[0] == '[' && line[line.size() - 1u] == ']') {
            if (has_section) {
                out.push_back(current);
                current = CoredataAstroBody();
            }
            section = trim(line.substr(1u, line.size() - 2u));
            current.id = section;
            has_section = true;
            continue;
        }
        if (!has_section) {
            add_error(errors, path, line_no, "field_outside_section", line);
            continue;
        }
        if (!parse_key_value(line, key, value)) {
            add_error(errors, path, line_no, "invalid_kv", line);
            continue;
        }
        if (key == "radius_m") {
            if (!parse_u64(value, current.radius_m, err)) {
                add_error(errors, path, line_no, "invalid_radius_m", err);
            } else {
                current.has_radius = true;
            }
        } else if (key == "mu_m3_s2") {
            if (!parse_mantissa_exp10(value, current.mu_mantissa, current.mu_exp10, err)) {
                add_error(errors, path, line_no, "invalid_mu_m3_s2", err);
            }
        } else if (key == "rotation_rate_rad_s") {
            if (!parse_q16_16(value, current.rotation_rate_q16, err)) {
                add_error(errors, path, line_no, "invalid_rotation_rate", err);
            } else {
                current.has_rotation_rate = true;
            }
        } else if (key == "atmosphere_profile_id") {
            if (!parse_string(value, current.atmosphere_profile_id, err)) {
                add_error(errors, path, line_no, "invalid_atmosphere_profile_id", err);
            }
        } else {
            add_error(errors, path, line_no, "unknown_field", key);
        }
    }
    if (has_section) {
        out.push_back(current);
    }
    return errors.empty();
}

} // namespace

bool coredata_load_all(const std::string &root,
                       CoredataData &out,
                       std::vector<CoredataError> &errors) {
    const std::string cosmo_root = dom::join(root, "cosmo");
    const std::string mechanics_root = dom::join(root, "mechanics");
    const std::string astro_root = dom::join(root, "astro");
    CoredataProceduralRules rules;
    bool ok = true;

    errors.clear();
    out = CoredataData();

    ok &= parse_anchor_file(dom::join(cosmo_root, "milky_way_anchors.toml"),
                            out.anchors, errors);
    ok &= parse_anchor_file(dom::join(cosmo_root, "regions.toml"),
                            out.anchors, errors);

    if (parse_procedural_rules(dom::join(cosmo_root, "procedural_rules.toml"),
                               rules, errors)) {
        out.rules.push_back(rules);
    } else {
        ok = false;
    }

    ok &= parse_system_profiles(dom::join(mechanics_root, "system_profiles.toml"),
                                out.system_profiles, errors);
    ok &= parse_site_profiles(dom::join(mechanics_root, "site_profiles.toml"),
                              out.site_profiles, errors);
    ok &= parse_astro_constants(dom::join(astro_root, "sol_earth_constants.toml"),
                                out.astro_bodies, errors);

    return ok && errors.empty();
}

void coredata_errors_print(const std::vector<CoredataError> &errors) {
    size_t i;
    for (i = 0u; i < errors.size(); ++i) {
        const CoredataError &e = errors[i];
        if (!e.path.empty()) {
            if (e.line > 0) {
                std::fprintf(stderr, "error: %s:%d: %s: %s\n",
                             e.path.c_str(), e.line,
                             e.code.c_str(), e.message.c_str());
            } else {
                std::fprintf(stderr, "error: %s: %s: %s\n",
                             e.path.c_str(), e.code.c_str(), e.message.c_str());
            }
        } else {
            std::fprintf(stderr, "error: %s: %s\n", e.code.c_str(), e.message.c_str());
        }
    }
}

} // namespace tools
} // namespace dom
