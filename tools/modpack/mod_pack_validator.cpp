/*
FILE: tools/modpack/mod_pack_validator.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / modpack
RESPONSIBILITY: Deterministic mod pack and graph validator.
ALLOWED DEPENDENCIES: engine/game public headers and C++98 standard headers.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; privileged OS APIs.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic parsing and ordering.
*/
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "dominium/mods/mod_loader.h"
#include "dominium/mods/mod_hash.h"
#include "validation/validator_common.h"

using dom::validation::read_file_text;

struct PackEntry {
    std::string path;
    long size;
    u64 hash;
};

static void usage() {
    std::printf("Usage: mod_pack_validator [--pack <pack_path> --root <mod_root>] "
                "[--manifest-list <path>] [--schema id:ver] [--epoch id:val] "
                "[--cap id] [--render-feature id] [--perf-budget n] "
                "[--safe-mode none|non-sim|base] [--print-graph]\n");
}

static void normalize_slashes(std::string& path) {
    size_t i;
    for (i = 0u; i < path.size(); ++i) {
        if (path[i] == '\\') {
            path[i] = '/';
        }
    }
}

static void hash_to_hex(u64 value, char* out_hex, size_t cap) {
    static const char* digits = "0123456789abcdef";
    int i;
    if (!out_hex || cap < 17u) {
        return;
    }
    for (i = 0; i < 16; ++i) {
        int shift = (15 - i) * 4;
        out_hex[i] = digits[(value >> shift) & 0x0f];
    }
    out_hex[16] = '\0';
}

static u64 hash_file_bytes(const std::string& path) {
    unsigned char buf[4096];
    u64 hash = mod_hash_fnv1a64_init();
    FILE* f = std::fopen(path.c_str(), "rb");
    if (!f) {
        return 0u;
    }
    while (!std::feof(f)) {
        size_t n = std::fread(buf, 1u, sizeof(buf), f);
        if (n == 0u) {
            break;
        }
        hash = mod_hash_fnv1a64_update(hash, buf, (u32)n);
    }
    std::fclose(f);
    return hash;
}

static u64 hash_payload(const std::vector<PackEntry>& entries, const std::string& root) {
    u64 hash = mod_hash_fnv1a64_init();
    unsigned char buf[4096];
    size_t i;
    for (i = 0u; i < entries.size(); ++i) {
        std::string full = root;
        if (!full.empty() && full[full.size() - 1u] != '/' && full[full.size() - 1u] != '\\') {
            full += "/";
        }
        full += entries[i].path;
        normalize_slashes(full);
        FILE* f = std::fopen(full.c_str(), "rb");
        if (!f) {
            return 0u;
        }
        hash = mod_hash_fnv1a64_update_str(hash, entries[i].path.c_str());
        {
            char sep = '\n';
            hash = mod_hash_fnv1a64_update(hash, &sep, 1u);
        }
        while (!std::feof(f)) {
            size_t n = std::fread(buf, 1u, sizeof(buf), f);
            if (n == 0u) {
                break;
            }
            hash = mod_hash_fnv1a64_update(hash, buf, (u32)n);
        }
        std::fclose(f);
    }
    return hash;
}

static int parse_pack(const std::string& pack_path,
                      std::string& mod_id,
                      mod_semver& mod_version,
                      u64& payload_hash,
                      std::vector<PackEntry>& entries) {
    std::string text;
    size_t pos = 0u;
    u32 line_no = 1u;
    d_bool has_id = D_FALSE;
    d_bool has_version = D_FALSE;
    d_bool has_payload = D_FALSE;
    if (!read_file_text(pack_path, text)) {
        std::fprintf(stderr, "Failed to read pack: %s\n", pack_path.c_str());
        return 1;
    }
    while (pos < text.size()) {
        size_t end = text.find('\n', pos);
        if (end == std::string::npos) {
            end = text.size();
        }
        std::string line = text.substr(pos, end - pos);
        pos = (end == text.size()) ? end : end + 1u;
        if (!line.empty() && (line[line.size() - 1u] == '\r')) {
            line.erase(line.size() - 1u);
        }
        if (line.empty() || line[0] == '#' || line[0] == ';') {
            line_no++;
            continue;
        }
        size_t eq = line.find('=');
        if (eq == std::string::npos) {
            std::fprintf(stderr, "Pack parse error line %u\n", line_no);
            return 1;
        }
        std::string key = line.substr(0, eq);
        std::string value = line.substr(eq + 1u);
        if (key == "mod_id") {
            mod_id = value;
            has_id = D_TRUE;
        } else if (key == "mod_version") {
            if (mod_semver_parse(value.c_str(), &mod_version) != 0) {
                std::fprintf(stderr, "Bad mod_version line %u\n", line_no);
                return 1;
            }
            has_version = D_TRUE;
        } else if (key == "payload_hash") {
            if (mod_parse_hash64(value.c_str(), &payload_hash) != 0) {
                std::fprintf(stderr, "Bad payload_hash line %u\n", line_no);
                return 1;
            }
            has_payload = D_TRUE;
        } else if (key == "file") {
            size_t p1 = value.find('|');
            size_t p2 = (p1 == std::string::npos) ? std::string::npos : value.find('|', p1 + 1u);
            if (p1 == std::string::npos || p2 == std::string::npos) {
                std::fprintf(stderr, "Bad file entry line %u\n", line_no);
                return 1;
            }
            PackEntry entry;
            entry.path = value.substr(0, p1);
            entry.size = std::strtol(value.substr(p1 + 1u, p2 - p1 - 1u).c_str(), 0, 10);
            if (mod_parse_hash64(value.substr(p2 + 1u).c_str(), &entry.hash) != 0) {
                std::fprintf(stderr, "Bad file hash line %u\n", line_no);
                return 1;
            }
            entries.push_back(entry);
        }
        line_no++;
    }
    if (!has_id || !has_version || !has_payload) {
        std::fprintf(stderr, "Pack missing required fields\n");
        return 1;
    }
    if (entries.empty()) {
        std::fprintf(stderr, "Pack contains no files\n");
        return 1;
    }
    return 0;
}

static int load_manifest_list(const std::string& list_path,
                              std::vector<std::string>& out_paths) {
    std::string text;
    size_t pos = 0u;
    if (!read_file_text(list_path, text)) {
        std::fprintf(stderr, "Failed to read manifest list: %s\n", list_path.c_str());
        return 1;
    }
    while (pos < text.size()) {
        size_t end = text.find('\n', pos);
        if (end == std::string::npos) {
            end = text.size();
        }
        std::string line = text.substr(pos, end - pos);
        pos = (end == text.size()) ? end : end + 1u;
        if (!line.empty() && (line[line.size() - 1u] == '\r')) {
            line.erase(line.size() - 1u);
        }
        if (line.empty() || line[0] == '#' || line[0] == ';') {
            continue;
        }
        out_paths.push_back(line);
    }
    return 0;
}

static mod_safe_mode_policy parse_safe_mode(const std::string& text) {
    if (text == "non-sim") {
        return MOD_SAFE_MODE_NON_SIM_ONLY;
    }
    if (text == "base") {
        return MOD_SAFE_MODE_BASE_ONLY;
    }
    return MOD_SAFE_MODE_NONE;
}

int main(int argc, char** argv) {
    std::string pack_path;
    std::string root_path;
    std::string manifest_list_path;
    std::vector<std::string> schema_args;
    std::vector<std::string> epoch_args;
    std::vector<std::string> caps;
    std::vector<std::string> render_feats;
    std::string safe_mode_text = "none";
    u32 perf_budget = 0u;
    d_bool print_graph = D_FALSE;
    int i;

    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (std::strcmp(arg, "--pack") == 0 && i + 1 < argc) {
            pack_path = argv[++i];
        } else if (std::strcmp(arg, "--root") == 0 && i + 1 < argc) {
            root_path = argv[++i];
        } else if (std::strcmp(arg, "--manifest-list") == 0 && i + 1 < argc) {
            manifest_list_path = argv[++i];
        } else if (std::strcmp(arg, "--schema") == 0 && i + 1 < argc) {
            schema_args.push_back(argv[++i]);
        } else if (std::strcmp(arg, "--epoch") == 0 && i + 1 < argc) {
            epoch_args.push_back(argv[++i]);
        } else if (std::strcmp(arg, "--cap") == 0 && i + 1 < argc) {
            caps.push_back(argv[++i]);
        } else if (std::strcmp(arg, "--render-feature") == 0 && i + 1 < argc) {
            render_feats.push_back(argv[++i]);
        } else if (std::strcmp(arg, "--perf-budget") == 0 && i + 1 < argc) {
            perf_budget = (u32)std::strtoul(argv[++i], 0, 10);
        } else if (std::strcmp(arg, "--safe-mode") == 0 && i + 1 < argc) {
            safe_mode_text = argv[++i];
        } else if (std::strcmp(arg, "--print-graph") == 0) {
            print_graph = D_TRUE;
        } else if (std::strcmp(arg, "--help") == 0) {
            usage();
            return 0;
        } else {
            usage();
            return 1;
        }
    }

    if (!pack_path.empty()) {
        std::string mod_id;
        mod_semver mod_version;
        u64 payload_hash = 0u;
        std::vector<PackEntry> entries;
        if (parse_pack(pack_path, mod_id, mod_version, payload_hash, entries) != 0) {
            return 1;
        }
        std::printf("Pack mod=%s version=%u.%u.%u\n",
                    mod_id.c_str(),
                    (unsigned)mod_version.major,
                    (unsigned)mod_version.minor,
                    (unsigned)mod_version.patch);
        if (!root_path.empty()) {
            u64 computed = hash_payload(entries, root_path);
            char hex[17];
            hash_to_hex(computed, hex, sizeof(hex));
            if (computed != payload_hash) {
                std::fprintf(stderr, "Payload hash mismatch (expected %llx, got %s)\n",
                             (unsigned long long)payload_hash, hex);
                return 1;
            }
            for (i = 0; i < (int)entries.size(); ++i) {
                std::string full = root_path;
                if (!full.empty() && full[full.size() - 1u] != '/' && full[full.size() - 1u] != '\\') {
                    full += "/";
                }
                full += entries[i].path;
                normalize_slashes(full);
                u64 file_hash = hash_file_bytes(full);
                if (file_hash != entries[i].hash) {
                    std::fprintf(stderr, "File hash mismatch: %s\n", entries[i].path.c_str());
                    return 1;
                }
            }
            std::printf("Pack validation OK.\n");
        }
    }

    if (!manifest_list_path.empty()) {
        std::vector<std::string> manifest_paths;
        std::vector<mod_manifest> manifests;
        std::vector<mod_schema_version> schemas;
        std::vector<mod_feature_epoch> epochs;
        std::vector<mod_required_capability> cap_list;
        std::vector<mod_required_feature> render_list;
        mod_loader_input input;
        mod_loader_output output;

        if (load_manifest_list(manifest_list_path, manifest_paths) != 0) {
            return 1;
        }
        manifests.resize(manifest_paths.size());
        for (i = 0; i < (int)manifest_paths.size(); ++i) {
            std::string text;
            mod_manifest_error err;
            if (!read_file_text(manifest_paths[i], text)) {
                std::fprintf(stderr, "Failed to read manifest: %s\n", manifest_paths[i].c_str());
                return 1;
            }
            if (mod_manifest_parse_text(text.c_str(), &manifests[i], &err) != 0) {
                std::fprintf(stderr, "Manifest parse error %s line %u: %s\n",
                             manifest_paths[i].c_str(), err.line, err.message);
                return 1;
            }
        }

        for (i = 0; i < (int)schema_args.size(); ++i) {
            size_t sep = schema_args[i].find(':');
            if (sep == std::string::npos) {
                std::fprintf(stderr, "Bad schema arg: %s\n", schema_args[i].c_str());
                return 1;
            }
            mod_schema_version schema;
            std::string id = schema_args[i].substr(0, sep);
            std::string ver = schema_args[i].substr(sep + 1u);
            std::memset(&schema, 0, sizeof(schema));
            std::strncpy(schema.schema_id, id.c_str(), sizeof(schema.schema_id) - 1u);
            if (mod_semver_parse(ver.c_str(), &schema.version) != 0) {
                std::fprintf(stderr, "Bad schema version: %s\n", ver.c_str());
                return 1;
            }
            schemas.push_back(schema);
        }

        for (i = 0; i < (int)epoch_args.size(); ++i) {
            size_t sep = epoch_args[i].find(':');
            if (sep == std::string::npos) {
                std::fprintf(stderr, "Bad epoch arg: %s\n", epoch_args[i].c_str());
                return 1;
            }
            mod_feature_epoch epoch;
            std::string id = epoch_args[i].substr(0, sep);
            std::string val = epoch_args[i].substr(sep + 1u);
            std::memset(&epoch, 0, sizeof(epoch));
            std::strncpy(epoch.epoch_id, id.c_str(), sizeof(epoch.epoch_id) - 1u);
            epoch.epoch = (u32)std::strtoul(val.c_str(), 0, 10);
            epochs.push_back(epoch);
        }

        for (i = 0; i < (int)caps.size(); ++i) {
            mod_required_capability cap;
            std::memset(&cap, 0, sizeof(cap));
            std::strncpy(cap.capability_id, caps[i].c_str(), sizeof(cap.capability_id) - 1u);
            cap_list.push_back(cap);
        }
        for (i = 0; i < (int)render_feats.size(); ++i) {
            mod_required_feature feat;
            std::memset(&feat, 0, sizeof(feat));
            std::strncpy(feat.feature_id, render_feats[i].c_str(), sizeof(feat.feature_id) - 1u);
            render_list.push_back(feat);
        }

        std::memset(&input, 0, sizeof(input));
        input.mods = manifests.empty() ? 0 : &manifests[0];
        input.mod_count = (u32)manifests.size();
        input.environment.schemas = schemas.empty() ? 0 : &schemas[0];
        input.environment.schema_count = (u32)schemas.size();
        input.environment.epochs = epochs.empty() ? 0 : &epochs[0];
        input.environment.epoch_count = (u32)epochs.size();
        input.environment.capabilities = cap_list.empty() ? 0 : &cap_list[0];
        input.environment.capability_count = (u32)cap_list.size();
        input.environment.render_features = render_list.empty() ? 0 : &render_list[0];
        input.environment.render_feature_count = (u32)render_list.size();
        input.environment.perf_budget_class = perf_budget;
        input.safe_mode = parse_safe_mode(safe_mode_text);

        mod_loader_resolve(&input, &output);
        if (output.status != MOD_LOADER_OK) {
            std::printf("Mod resolution refused: %s\n", mod_loader_status_to_string(output.status));
            if (output.status == MOD_LOADER_GRAPH_REFUSED) {
                std::printf("Graph refusal: %s (%s -> %s)\n",
                            mod_graph_refusal_to_string(output.graph_refusal.code),
                            output.graph_refusal.mod_id,
                            output.graph_refusal.detail_id);
            }
            return 1;
        }
        if (print_graph) {
            std::printf("Resolved order:\n");
            for (i = 0; i < (int)output.graph.mod_count; ++i) {
                const mod_manifest* manifest = &output.graph.mods[output.graph.order[i]];
                std::printf("  %s\n", manifest->mod_id);
            }
        }
        for (i = 0; i < (int)output.report_count; ++i) {
            const mod_manifest* manifest = &output.graph.mods[output.graph.order[i]];
            const mod_compat_report* report = &output.reports[i];
            std::printf("Mod %s: %s", manifest->mod_id,
                        mod_compat_result_to_string(report->result));
            if (report->result == MOD_COMPAT_REFUSE) {
                std::printf(" (%s)", mod_compat_refusal_to_string(report->refusal));
            }
            std::printf("\n");
        }
        std::printf("Graph hash: %llx\n", (unsigned long long)output.graph_hash);
    }

    return 0;
}
