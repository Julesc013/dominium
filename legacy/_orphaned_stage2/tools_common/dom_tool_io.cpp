/*
FILE: source/dominium/tools/common/dom_tool_io.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_io
RESPONSIBILITY: Implements `dom_tool_io`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_tool_io.h"

#include <cstdio>

extern "C" {
#include "domino/sys.h"
}

namespace dom {
namespace tools {

bool read_file(const std::string &path,
               std::vector<unsigned char> &out,
               std::string *err) {
    void *fh;
    long size;
    size_t read_len;

    out.clear();
    if (path.empty()) {
        if (err) *err = "read_file: empty path";
        return false;
    }

    fh = dsys_file_open(path.c_str(), "rb");
    if (!fh) {
        if (err) *err = "read_file: open failed";
        return false;
    }

    if (dsys_file_seek(fh, 0L, SEEK_END) != 0) {
        dsys_file_close(fh);
        if (err) *err = "read_file: seek end failed";
        return false;
    }
    size = dsys_file_tell(fh);
    if (size < 0L) {
        dsys_file_close(fh);
        if (err) *err = "read_file: tell failed";
        return false;
    }
    if (dsys_file_seek(fh, 0L, SEEK_SET) != 0) {
        dsys_file_close(fh);
        if (err) *err = "read_file: seek set failed";
        return false;
    }

    if (size == 0L) {
        dsys_file_close(fh);
        return true;
    }

    out.resize((size_t)size);
    read_len = dsys_file_read(fh, &out[0], (size_t)size);
    dsys_file_close(fh);

    if (read_len != (size_t)size) {
        out.clear();
        if (err) *err = "read_file: short read";
        return false;
    }
    return true;
}

bool write_file(const std::string &path,
                const unsigned char *data,
                size_t len,
                std::string *err) {
    void *fh;
    size_t wrote;

    if (path.empty()) {
        if (err) *err = "write_file: empty path";
        return false;
    }

    fh = dsys_file_open(path.c_str(), "wb");
    if (!fh) {
        if (err) *err = "write_file: open failed";
        return false;
    }
    wrote = dsys_file_write(fh, data, len);
    dsys_file_close(fh);
    if (wrote != len) {
        if (err) *err = "write_file: short write";
        return false;
    }
    return true;
}

bool file_exists(const std::string &path) {
    void *fh;
    if (path.empty()) {
        return false;
    }
    fh = dsys_file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }
    dsys_file_close(fh);
    return true;
}

} // namespace tools
} // namespace dom

