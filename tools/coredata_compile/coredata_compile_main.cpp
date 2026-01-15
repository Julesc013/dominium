/*
FILE: source/dominium/tools/coredata_compile/coredata_compile_main.cpp
MODULE: Dominium
PURPOSE: Coredata compiler CLI entry point.
*/
#include <cstdio>
#include <cstring>
#include <string>
#include <cerrno>
#include <cstdlib>

#if defined(_WIN32)
#include <direct.h>
#else
#include <sys/stat.h>
#endif

#include "coredata_emit_tlv.h"
#include "coredata_manifest.h"
#include "coredata_validate.h"
#include "dom_paths.h"

namespace {

static void usage() {
    std::printf("Usage: coredata_compile [--input-root=<path>] [--output-pack-id=<id>]\n");
    std::printf("                        [--output-version=<ver>] [--output-root=<path>]\n");
    std::printf("                        [--emit-manifest=1|0] [--strict=1]\n");
}

static bool parse_u32(const std::string &s, u32 &out) {
    char *end = 0;
    unsigned long v = std::strtoul(s.c_str(), &end, 10);
    if (!end || end[0] != '\0') {
        return false;
    }
    out = (u32)v;
    return true;
}

static bool parse_version_num(const std::string &s, u32 &out, std::string &err) {
    size_t i = 0u;
    u32 parts[3] = {0u, 0u, 0u};
    int part_index = 0;
    std::string cur;
    if (s.empty()) {
        err = "empty_version";
        return false;
    }
    for (i = 0u; i < s.size(); ++i) {
        char c = s[i];
        if (c == '.') {
            if (part_index >= 2 || cur.empty()) {
                err = "invalid_version";
                return false;
            }
            if (!parse_u32(cur, parts[part_index])) {
                err = "invalid_version";
                return false;
            }
            cur.clear();
            ++part_index;
        } else if (c >= '0' && c <= '9') {
            cur.push_back(c);
        } else {
            err = "invalid_version";
            return false;
        }
    }
    if (!cur.empty()) {
        if (!parse_u32(cur, parts[part_index])) {
            err = "invalid_version";
            return false;
        }
    } else if (part_index > 0) {
        err = "invalid_version";
        return false;
    }

    if (part_index == 0 && s.find('.') == std::string::npos) {
        out = parts[0];
        return true;
    }

    if (parts[0] > 9999u || parts[1] > 99u || parts[2] > 99u) {
        err = "version_out_of_range";
        return false;
    }
    out = (parts[0] * 10000u) + (parts[1] * 100u) + parts[2];
    return true;
}

static std::string format_version_dir(u32 version_num) {
    char buf[16];
    std::sprintf(buf, "%08u", version_num);
    return std::string(buf);
}

static bool write_file(const std::string &path,
                       const std::vector<unsigned char> &bytes,
                       std::string &err) {
    std::FILE *f = std::fopen(path.c_str(), "wb");
    if (!f) {
        err = "open_failed";
        return false;
    }
    if (!bytes.empty()) {
        size_t wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
        if (wrote != bytes.size()) {
            std::fclose(f);
            err = "write_failed";
            return false;
        }
    }
    std::fclose(f);
    return true;
}

static int is_sep(char c) { return c == '/' || c == '\\'; }

static bool make_dir(const std::string &path) {
    if (path.empty()) {
        return false;
    }
#if defined(_WIN32)
    if (_mkdir(path.c_str()) == 0) {
        return true;
    }
#else
    if (mkdir(path.c_str(), 0755) == 0) {
        return true;
    }
#endif
    if (errno == EEXIST) {
        return true;
    }
    return false;
}

static bool ensure_dir_recursive(const std::string &path) {
    size_t i = 0u;
    std::string cur;
    if (path.empty()) {
        return false;
    }
    if (path.size() >= 2u && path[1] == ':') {
        cur = path.substr(0u, 2u);
        i = 2u;
        if (i < path.size() && is_sep(path[i])) {
            cur.push_back(path[i]);
            ++i;
        }
    }
    for (; i < path.size(); ++i) {
        char c = path[i];
        if (is_sep(c)) {
            if (!cur.empty() && !make_dir(cur)) {
                return false;
            }
        }
        cur.push_back(c);
    }
    if (!cur.empty() && !make_dir(cur)) {
        return false;
    }
    return true;
}

} // namespace

int main(int argc, char **argv) {
    std::string input_root = "data/core";
    std::string output_root = "repo/packs";
    std::string pack_id = "base_cosmo";
    std::string version_str = "0.1.0";
    u32 version_num = 0u;
    bool emit_manifest = true;
    bool strict = true;
    std::string err;
    int i;

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i] ? argv[i] : "";
        if (std::strncmp(arg, "--input-root=", 13) == 0) {
            input_root = std::string(arg + 13);
        } else if (std::strncmp(arg, "--output-pack-id=", 17) == 0) {
            pack_id = std::string(arg + 17);
        } else if (std::strncmp(arg, "--output-version=", 17) == 0) {
            version_str = std::string(arg + 17);
        } else if (std::strncmp(arg, "--output-root=", 14) == 0) {
            output_root = std::string(arg + 14);
        } else if (std::strncmp(arg, "--emit-manifest=", 16) == 0) {
            std::string v = std::string(arg + 16);
            emit_manifest = (v != "0");
        } else if (std::strncmp(arg, "--strict=", 9) == 0) {
            std::string v = std::string(arg + 9);
            strict = (v != "0");
        } else if (std::strcmp(arg, "--help") == 0 || std::strcmp(arg, "-h") == 0) {
            usage();
            return 0;
        } else {
            std::fprintf(stderr, "Unknown arg: %s\n", arg);
            usage();
            return 2;
        }
    }

    if (!strict) {
        std::fprintf(stderr, "warning: strict=0 is not supported; enforcing strict\n");
        strict = true;
    }

    if (!parse_version_num(version_str, version_num, err)) {
        std::fprintf(stderr, "version error: %s\n", err.c_str());
        return 2;
    }

    dom::tools::CoredataData data;
    std::vector<dom::tools::CoredataError> errors;
    if (!dom::tools::coredata_load_all(input_root, data, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 3;
    }
    if (!dom::tools::coredata_validate(data, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 3;
    }

    dom::tools::CoredataEmitOptions opts;
    opts.pack_id = pack_id;
    opts.pack_version_str = version_str;
    opts.pack_version_num = version_num;
    opts.pack_schema_version = 1u;

    dom::tools::CoredataPack pack;
    if (!dom::tools::coredata_emit_pack(data, opts, pack, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 4;
    }

    dom::tools::CoredataManifest manifest;
    if (emit_manifest) {
        if (!dom::tools::coredata_emit_manifest(pack, manifest, errors)) {
            dom::tools::coredata_errors_print(errors);
            return 4;
        }
    }

    {
        const std::string version_dir = format_version_dir(version_num);
        const std::string pack_root = dom::join(output_root, pack_id);
        const std::string out_dir = dom::join(pack_root, version_dir);
        const std::string pack_path = dom::join(out_dir, "pack.tlv");
        const std::string manifest_path = dom::join(out_dir, "pack_manifest.tlv");

        if (!ensure_dir_recursive(out_dir)) {
            std::fprintf(stderr, "output mkdir failed: %s\n", out_dir.c_str());
            return 5;
        }

        if (!write_file(pack_path, pack.pack_bytes, err)) {
            std::fprintf(stderr, "write pack failed: %s (%s)\n", pack_path.c_str(), err.c_str());
            return 5;
        }

        if (emit_manifest) {
            if (!write_file(manifest_path, manifest.bytes, err)) {
                std::fprintf(stderr, "write manifest failed: %s (%s)\n", manifest_path.c_str(), err.c_str());
                return 5;
            }
        }

        std::printf("coredata_compile: wrote %s\n", pack_path.c_str());
        if (emit_manifest) {
            std::printf("coredata_compile: wrote %s\n", manifest_path.c_str());
        }
    }

    return 0;
}
