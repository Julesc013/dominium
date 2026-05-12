/*
FILE: source/tests/coredata_compile_determinism_test.cpp
MODULE: Dominium Tests
PURPOSE: Ensure coredata compiler emits byte-identical packs/manifests.
*/
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#include "coredata_emit_tlv.h"
#include "coredata_load.h"
#include "coredata_manifest.h"
#include "coredata_validate.h"

#ifndef COREDATA_FIXTURE_ROOT
#define COREDATA_FIXTURE_ROOT "tests/fixtures/coredata_min"
#endif

static int load_and_emit(const std::string &root,
                         dom::tools::CoredataPack &out_pack,
                         dom::tools::CoredataManifest &out_manifest) {
    dom::tools::CoredataData data;
    std::vector<dom::tools::CoredataError> errors;
    dom::tools::CoredataEmitOptions opts;

    if (!dom::tools::coredata_load_all(root, data, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 0;
    }
    if (!dom::tools::coredata_validate(data, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 0;
    }

    opts.pack_id = "base_cosmo";
    opts.pack_version_str = "0.1.0";
    opts.pack_version_num = 100u;
    opts.pack_schema_version = 1u;

    if (!dom::tools::coredata_emit_pack(data, opts, out_pack, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 0;
    }
    if (!dom::tools::coredata_emit_manifest(out_pack, out_manifest, errors)) {
        dom::tools::coredata_errors_print(errors);
        return 0;
    }
    return 1;
}

int main() {
    const std::string root = COREDATA_FIXTURE_ROOT;
    dom::tools::CoredataPack pack1;
    dom::tools::CoredataPack pack2;
    dom::tools::CoredataManifest man1;
    dom::tools::CoredataManifest man2;

    if (!load_and_emit(root, pack1, man1)) {
        std::fprintf(stderr, "coredata_emit failed (first)\n");
        return 1;
    }
    if (!load_and_emit(root, pack2, man2)) {
        std::fprintf(stderr, "coredata_emit failed (second)\n");
        return 1;
    }

    if (pack1.pack_bytes.size() != pack2.pack_bytes.size()) {
        std::fprintf(stderr, "pack size mismatch\n");
        return 1;
    }
    if (!pack1.pack_bytes.empty() &&
        std::memcmp(&pack1.pack_bytes[0], &pack2.pack_bytes[0], pack1.pack_bytes.size()) != 0) {
        std::fprintf(stderr, "pack bytes mismatch\n");
        return 1;
    }

    if (man1.bytes.size() != man2.bytes.size()) {
        std::fprintf(stderr, "manifest size mismatch\n");
        return 1;
    }
    if (!man1.bytes.empty() &&
        std::memcmp(&man1.bytes[0], &man2.bytes[0], man1.bytes.size()) != 0) {
        std::fprintf(stderr, "manifest bytes mismatch\n");
        return 1;
    }

    return 0;
}
