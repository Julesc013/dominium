/*
FILE: source/dominium/setup/dom_setup_ops.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/dom_setup_ops
RESPONSIBILITY: Implements `dom_setup_ops`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_setup_ops.h"

#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/sys.h"
}

namespace dom {
namespace {

static bool copy_file(const std::string &src, const std::string &dst) {
    unsigned char buf[4096];
    void *in_fh;
    void *out_fh;
    size_t rd;

    in_fh = dsys_file_open(src.c_str(), "rb");
    if (!in_fh) {
        return false;
    }
    out_fh = dsys_file_open(dst.c_str(), "wb");
    if (!out_fh) {
        dsys_file_close(in_fh);
        return false;
    }

    while ((rd = dsys_file_read(in_fh, buf, sizeof(buf))) > 0u) {
        size_t wr = dsys_file_write(out_fh, buf, rd);
        if (wr != rd) {
            dsys_file_close(in_fh);
            dsys_file_close(out_fh);
            return false;
        }
    }

    dsys_file_close(in_fh);
    dsys_file_close(out_fh);
    return true;
}

} // namespace

bool setup_install(const Paths &paths, const std::string &source) {
    std::string manifest = join(source, "product.json");
    if (source.empty()) {
        std::printf("setup: install requires a source path.\n");
        return false;
    }
    if (!file_exists(manifest)) {
        std::printf("setup: %s missing product.json (stub install).\n", source.c_str());
    }
    std::printf("setup: installing from %s into %s (stubbed copy).\n",
                source.c_str(), paths.products.c_str());
    /* TODO: parse manifest to determine product/version and copy tree. */
    return true;
}

bool setup_repair(const Paths &paths, const std::string &product) {
    std::printf("setup: repair requested for %s in %s (stub).\n",
                product.c_str(), paths.products.c_str());
    /* TODO: verify binaries/manifests and rewrite missing assets. */
    return true;
}

bool setup_uninstall(const Paths &paths, const std::string &product) {
    std::string target = join(paths.products, product);
    std::printf("setup: uninstall requested for %s (path %s). No files removed in this stub.\n",
                product.c_str(), target.c_str());
    /* TODO: recursive delete when dsys directory removal helpers are available. */
    return true;
}

bool setup_import(const Paths &paths, const std::string &source) {
    std::string pack_tlv = join(source, "pack.tlv");
    std::string mod_tlv = join(source, "mod.tlv");
    if (file_exists(pack_tlv)) {
        std::string dst = join(paths.packs, "imported.tlv");
        (void)copy_file(pack_tlv, dst);
        std::printf("setup: imported pack from %s -> %s\n", pack_tlv.c_str(), dst.c_str());
        return true;
    }
    if (file_exists(mod_tlv)) {
        std::string dst = join(paths.mods, "imported.tlv");
        (void)copy_file(mod_tlv, dst);
        std::printf("setup: imported mod from %s -> %s\n", mod_tlv.c_str(), dst.c_str());
        return true;
    }
    std::printf("setup: import source %s missing pack.tlv/mod.tlv\n", source.c_str());
    return false;
}

bool setup_gc(const Paths &paths) {
    const char *roots[3];
    size_t i;
    roots[0] = paths.products.c_str();
    roots[1] = paths.packs.c_str();
    roots[2] = paths.mods.c_str();
    for (i = 0u; i < 3u; ++i) {
        dsys_dir_iter *it = dsys_dir_open(roots[i]);
        dsys_dir_entry ent;
        if (!it) {
            continue;
        }
        std::printf("setup: GC dry-run for %s\n", roots[i]);
        while (dsys_dir_next(it, &ent)) {
            if (ent.is_dir) {
                std::printf("  candidate remove: %s/%s\n", roots[i], ent.name);
            }
        }
        dsys_dir_close(it);
    }
    return true;
}

bool setup_validate(const Paths &paths, const std::string &target) {
    (void)paths;
    if (target.empty()) {
        std::printf("setup: validate requires a target path.\n");
        return false;
    }
    if (!file_exists(target)) {
        std::printf("setup: %s does not exist.\n", target.c_str());
        return false;
    }
    std::printf("setup: validated %s (format checks deferred).\n", target.c_str());
    /* TODO: feed TLVs through d_content_load_pack/mod in dry-run once available. */
    return true;
}

} // namespace dom
