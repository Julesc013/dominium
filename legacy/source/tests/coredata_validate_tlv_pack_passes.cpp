/*
FILE: source/tests/coredata_validate_tlv_pack_passes.cpp
MODULE: Dominium Tests
PURPOSE: Ensure coredata_validate accepts a valid compiled pack.
*/
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <direct.h>
#else
#include <sys/stat.h>
#endif

#include "coredata_emit_tlv.h"
#include "coredata_manifest.h"
#include "coredata_validate_checks.h"
#include "coredata_validate_load.h"
#include "coredata_validate_report.h"
#include "coredata_compile/coredata_validate.h"

#ifndef COREDATA_FIXTURE_VALID_ROOT
#define COREDATA_FIXTURE_VALID_ROOT "tests/fixtures/coredata_valid"
#endif

static bool make_dir(const std::string &path) {
#if defined(_WIN32)
    if (_mkdir(path.c_str()) == 0) {
        return true;
    }
#else
    if (mkdir(path.c_str(), 0755) == 0) {
        return true;
    }
#endif
    return true;
}

static bool write_file(const std::string &path,
                       const std::vector<unsigned char> &bytes) {
    std::FILE *f = std::fopen(path.c_str(), "wb");
    if (!f) {
        return false;
    }
    if (!bytes.empty()) {
        size_t wrote = std::fwrite(&bytes[0], 1u, bytes.size(), f);
        if (wrote != bytes.size()) {
            std::fclose(f);
            return false;
        }
    }
    std::fclose(f);
    return true;
}

int main() {
    const std::string root = COREDATA_FIXTURE_VALID_ROOT;
    dom::tools::CoredataData data;
    std::vector<dom::tools::CoredataError> errors;
    dom::tools::CoredataEmitOptions opts;
    dom::tools::CoredataPack pack;
    dom::tools::CoredataManifest manifest;

    if (!dom::tools::coredata_load_all(root, data, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 1;
    }
    if (!dom::tools::coredata_validate(data, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 1;
    }

    opts.pack_id = "base_cosmo";
    opts.pack_version_str = "0.1.0";
    opts.pack_version_num = 100u;
    opts.pack_schema_version = 1u;

    if (!dom::tools::coredata_emit_pack(data, opts, pack, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 1;
    }
    if (!dom::tools::coredata_emit_manifest(pack, manifest, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 1;
    }

    {
        const std::string out_dir = "coredata_validate_pack_tmp";
        const std::string pack_path = out_dir + "/pack.tlv";
        const std::string manifest_path = out_dir + "/pack_manifest.tlv";
        dom::tools::CoredataPackView pack_view;
        dom::tools::CoredataManifestView manifest_view;
        dom::tools::CoredataValidationReport report;

        make_dir(out_dir);
        if (!write_file(pack_path, pack.pack_bytes)) {
            std::fprintf(stderr, "failed to write pack\n");
            return 1;
        }
        if (!write_file(manifest_path, manifest.bytes)) {
            std::fprintf(stderr, "failed to write manifest\n");
            return 1;
        }

        errors.clear();
        if (!dom::tools::coredata_validate_load_pack(pack_path, pack_view, errors)) {
            dom::tools::coredata_errors_print(errors);
            return 1;
        }
        errors.clear();
        if (!dom::tools::coredata_validate_load_manifest(manifest_path, manifest_view, errors)) {
            dom::tools::coredata_errors_print(errors);
            return 1;
        }

        dom::tools::coredata_report_init(report, "pack", pack_path);
        dom::tools::coredata_validate_pack_checks(pack_view, &manifest_view, report);
        if (report.error_count != 0u) {
            std::fprintf(stderr, "pack validation failed\n");
            return 1;
        }
    }

    return 0;
}
