/*
FILE: source/dominium/tools/modcheck/dom_modcheck.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/modcheck/dom_modcheck
RESPONSIBILITY: Implements `dom_modcheck`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_modcheck.h"

#include <cstdio>
#include <vector>
#include <cstring>

extern "C" {
#include "domino/sys.h"
#include "domino/core/types.h"
#include "content/d_content.h"
#include "content/d_content_schema.h"
#include "core/d_tlv_schema.h"
}

namespace dom {
namespace {

static bool read_file(const std::string &path, std::vector<unsigned char> &out) {
    void *fh;
    long size;
    size_t read_len;

    fh = dsys_file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }

    if (dsys_file_seek(fh, 0L, SEEK_END) != 0) {
        dsys_file_close(fh);
        return false;
    }
    size = dsys_file_tell(fh);
    if (size <= 0L) {
        dsys_file_close(fh);
        return false;
    }
    if (dsys_file_seek(fh, 0L, SEEK_SET) != 0) {
        dsys_file_close(fh);
        return false;
    }

    out.resize(static_cast<size_t>(size));
    read_len = dsys_file_read(fh, &out[0], static_cast<size_t>(size));
    dsys_file_close(fh);
    if (read_len != static_cast<size_t>(size)) {
        out.clear();
        return false;
    }
    return true;
}

} // namespace

bool modcheck_run(const std::string &path) {
    std::vector<unsigned char> data;
    d_tlv_blob blob;
    int vrc;

    if (!read_file(path, data)) {
        std::printf("modcheck: failed to read '%s'\n", path.c_str());
        return false;
    }

    blob.ptr = data.empty() ? (unsigned char *)0 : &data[0];
    blob.len = (u32)data.size();

    d_content_register_schemas();
    vrc = d_tlv_schema_validate(D_TLV_SCHEMA_MOD_V1, 1u, &blob, (d_tlv_blob *)0);
    if (vrc != 0) {
        std::printf("modcheck: schema validation failed (%d)\n", vrc);
        return false;
    }

    if (blob.len < 8u) {
        std::printf("modcheck: TLV manifest too small.\n");
        return false;
    }

    std::printf("modcheck: '%s' passed TLV schema validation.\n", path.c_str());
    std::printf("modcheck: dependency/reference checks TODO.\n");
    return true;
}

} // namespace dom
