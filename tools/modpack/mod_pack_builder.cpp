/*
FILE: tools/modpack/mod_pack_builder.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / modpack
RESPONSIBILITY: Deterministic mod pack builder (manifest + payload hash).
ALLOWED DEPENDENCIES: engine/game public headers and C++98 standard headers.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; privileged OS APIs.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic file ordering and hashing.
*/
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "dominium/mods/mod_manifest.h"
#include "dominium/mods/mod_hash.h"
#include "validation/validator_common.h"

using dom::validation::list_files_recursive;
using dom::validation::read_file_text;

static void usage() {
    std::printf("Usage: mod_pack_builder --root <mod_root> --manifest <manifest_path> --out <pack_path>\n");
}

static void normalize_slashes(std::string& path) {
    size_t i;
    for (i = 0u; i < path.size(); ++i) {
        if (path[i] == '\\') {
            path[i] = '/';
        }
    }
}

static std::string make_relative(const std::string& root, const std::string& full) {
    std::string rel = full;
    if (full.size() >= root.size() && full.compare(0u, root.size(), root) == 0) {
        rel = full.substr(root.size());
        if (!rel.empty() && (rel[0] == '\\' || rel[0] == '/')) {
            rel.erase(0u, 1u);
        }
    }
    normalize_slashes(rel);
    return rel;
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

static u64 hash_payload(const std::vector<std::string>& files,
                        const std::vector<std::string>& rel_paths) {
    u64 hash = mod_hash_fnv1a64_init();
    unsigned char buf[4096];
    size_t i;
    for (i = 0u; i < files.size(); ++i) {
        const std::string& rel = rel_paths[i];
        FILE* f = std::fopen(files[i].c_str(), "rb");
        if (!f) {
            return 0u;
        }
        hash = mod_hash_fnv1a64_update_str(hash, rel.c_str());
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

int main(int argc, char** argv) {
    std::string root;
    std::string normalized_root;
    std::string normalized_out;
    std::string manifest_path;
    std::string out_path;
    std::vector<std::string> files;
    std::vector<std::string> rel_paths;
    std::vector<std::string> skip_dirs;
    mod_manifest manifest;
    mod_manifest_error err;
    std::string manifest_text;
    FILE* out = 0;
    u64 payload_hash = 0u;
    char payload_hex[17];
    size_t i;

    for (i = 1u; i < (size_t)argc; ++i) {
        const char* arg = argv[i];
        if (std::strcmp(arg, "--root") == 0 && i + 1u < (size_t)argc) {
            root = argv[++i];
        } else if (std::strcmp(arg, "--manifest") == 0 && i + 1u < (size_t)argc) {
            manifest_path = argv[++i];
        } else if (std::strcmp(arg, "--out") == 0 && i + 1u < (size_t)argc) {
            out_path = argv[++i];
        } else if (std::strcmp(arg, "--help") == 0) {
            usage();
            return 0;
        } else {
            usage();
            return 1;
        }
    }
    if (root.empty() || manifest_path.empty() || out_path.empty()) {
        usage();
        return 1;
    }
    normalized_root = root;
    normalize_slashes(normalized_root);
    normalized_out = out_path;
    normalize_slashes(normalized_out);

    if (!read_file_text(manifest_path, manifest_text)) {
        std::fprintf(stderr, "Failed to read manifest: %s\n", manifest_path.c_str());
        return 1;
    }
    if (mod_manifest_parse_text(manifest_text.c_str(), &manifest, &err) != 0) {
        std::fprintf(stderr, "Manifest parse error (line %u): %s\n", err.line, err.message);
        return 1;
    }

    skip_dirs.push_back(".git");
    skip_dirs.push_back("build");
    skip_dirs.push_back("dist");
    skip_dirs.push_back("out");
    skip_dirs.push_back(".vs");
    skip_dirs.push_back(".vscode");
    skip_dirs.push_back("cache");
    skip_dirs.push_back("temp");
    list_files_recursive(root, std::vector<std::string>(), skip_dirs, files);
    if (files.empty()) {
        std::fprintf(stderr, "No files found under root: %s\n", root.c_str());
        return 1;
    }

    for (i = 0u; i < files.size(); ++i) {
        normalize_slashes(files[i]);
    }
    std::sort(files.begin(), files.end());
    rel_paths.reserve(files.size());
    for (i = 0u; i < files.size(); ++i) {
        std::string rel = make_relative(normalized_root, files[i]);
        if (rel == make_relative(normalized_root, normalized_out)) {
            continue;
        }
        if (rel == "mod.pack" || rel == "mod_pack.txt") {
            continue;
        }
        rel_paths.push_back(rel);
    }
    if (rel_paths.size() != files.size()) {
        std::vector<std::string> filtered_files;
        filtered_files.reserve(rel_paths.size());
        for (i = 0u; i < rel_paths.size(); ++i) {
            std::string full = normalized_root;
            if (!full.empty() && full[full.size() - 1u] != '\\' && full[full.size() - 1u] != '/') {
                full += "/";
            }
            full += rel_paths[i];
            normalize_slashes(full);
            filtered_files.push_back(full);
        }
        files.swap(filtered_files);
    }

    payload_hash = hash_payload(files, rel_paths);
    hash_to_hex(payload_hash, payload_hex, sizeof(payload_hex));
    if (manifest.payload_hash_str[0] != '\0' && manifest.payload_hash_value != payload_hash) {
        std::fprintf(stderr, "Manifest payload_hash mismatch (manifest %s, computed fnv1a64:%s)\n",
                     manifest.payload_hash_str, payload_hex);
        return 1;
    }

    out = std::fopen(out_path.c_str(), "wb");
    if (!out) {
        std::fprintf(stderr, "Failed to write pack: %s\n", out_path.c_str());
        return 1;
    }
    std::fprintf(out, "pack_version=1\n");
    std::fprintf(out, "mod_id=%s\n", manifest.mod_id);
    std::fprintf(out, "mod_version=%u.%u.%u\n",
                 (unsigned)manifest.mod_version.major,
                 (unsigned)manifest.mod_version.minor,
                 (unsigned)manifest.mod_version.patch);
    std::fprintf(out, "payload_hash=fnv1a64:%s\n", payload_hex);
    std::fprintf(out, "file_count=%u\n", (unsigned)files.size());
    for (i = 0u; i < files.size(); ++i) {
        u64 file_hash = hash_file_bytes(files[i]);
        char file_hex[17];
        long size = 0;
        FILE* f = std::fopen(files[i].c_str(), "rb");
        if (f) {
            std::fseek(f, 0, SEEK_END);
            size = std::ftell(f);
            std::fclose(f);
        }
        hash_to_hex(file_hash, file_hex, sizeof(file_hex));
        std::fprintf(out, "file=%s|%ld|fnv1a64:%s\n",
                     rel_paths[i].c_str(), size, file_hex);
    }
    std::fclose(out);
    std::printf("Pack written: %s\n", out_path.c_str());
    return 0;
}
