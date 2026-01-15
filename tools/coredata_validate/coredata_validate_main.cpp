/*
FILE: source/dominium/tools/coredata_validate/coredata_validate_main.cpp
MODULE: Dominium
PURPOSE: Coredata validator CLI entry point.
*/
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

#include "coredata_validate_checks.h"
#include "coredata_validate_load.h"
#include "coredata_validate_report.h"
#include "coredata_compile/coredata_validate.h"

namespace {

static void usage() {
    std::printf("Usage: coredata_validate --input-root=<path> | --pack=<path>\n");
    std::printf("                        [--format=text|json|tlv] [--strict=1]\n");
}

static std::string dir_name(const std::string &path) {
    size_t pos = path.find_last_of("/\\");
    if (pos == std::string::npos) {
        return std::string(".");
    }
    return path.substr(0u, pos);
}

static bool file_exists(const std::string &path) {
    std::ifstream f(path.c_str(), std::ios::in | std::ios::binary);
    return f.good();
}

} // namespace

int main(int argc, char **argv) {
    std::string input_root;
    std::string pack_path;
    std::string format = "text";
    bool strict = true;
    int i;

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i] ? argv[i] : "";
        if (std::strncmp(arg, "--input-root=", 13) == 0) {
            input_root = std::string(arg + 13);
        } else if (std::strncmp(arg, "--pack=", 7) == 0) {
            pack_path = std::string(arg + 7);
        } else if (std::strncmp(arg, "--format=", 9) == 0) {
            format = std::string(arg + 9);
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

    if ((!input_root.empty() && !pack_path.empty()) ||
        (input_root.empty() && pack_path.empty())) {
        std::fprintf(stderr, "Must supply exactly one of --input-root or --pack.\n");
        usage();
        return 2;
    }

    if (format != "text" && format != "json" && format != "tlv") {
        std::fprintf(stderr, "Unknown format: %s\n", format.c_str());
        usage();
        return 2;
    }

    if (!strict) {
        std::fprintf(stderr, "warning: strict=0 is not supported; enforcing strict\n");
        strict = true;
    }

    dom::tools::CoredataValidationReport report;
    if (!input_root.empty()) {
        dom::tools::coredata_report_init(report, "authoring", input_root);
        dom::tools::CoredataData data;
        std::vector<dom::tools::CoredataError> errors;

        if (!dom::tools::coredata_validate_load_authoring(input_root, data, errors)) {
            dom::tools::coredata_validate_report_errors(errors, report);
        } else {
            dom::tools::coredata_validate_report_errors(errors, report);
            errors.clear();
            if (!dom::tools::coredata_validate(data, errors)) {
                dom::tools::coredata_validate_report_errors(errors, report);
            } else {
                dom::tools::coredata_validate_authoring_policy(data, report);
            }
        }
    } else {
        dom::tools::coredata_report_init(report, "pack", pack_path);
        dom::tools::CoredataPackView pack;
        std::vector<dom::tools::CoredataError> errors;

        if (!dom::tools::coredata_validate_load_pack(pack_path, pack, errors)) {
            dom::tools::coredata_validate_report_errors(errors, report);
        } else {
            dom::tools::CoredataManifestView manifest;
            dom::tools::CoredataManifestView *manifest_ptr = 0;
            const std::string manifest_path = dir_name(pack_path) + "/pack_manifest.tlv";
            if (file_exists(manifest_path)) {
                if (!dom::tools::coredata_validate_load_manifest(manifest_path, manifest, errors)) {
                    dom::tools::coredata_validate_report_errors(errors, report);
                } else {
                    manifest_ptr = &manifest;
                }
            }
            dom::tools::coredata_validate_pack_checks(pack, manifest_ptr, report);
        }
    }

    dom::tools::coredata_report_sort(report);

    if (format == "json") {
        std::string out = dom::tools::coredata_report_json(report);
        std::printf("%s", out.c_str());
    } else if (format == "tlv") {
        std::vector<unsigned char> bytes = dom::tools::coredata_report_tlv(report);
        if (!bytes.empty()) {
            std::fwrite(&bytes[0], 1u, bytes.size(), stdout);
        }
    } else {
        std::string out = dom::tools::coredata_report_text(report);
        std::printf("%s", out.c_str());
    }

    if (dom::tools::coredata_report_has_io_error(report)) {
        return 3;
    }
    return dom::tools::coredata_report_exit_code(report);
}
