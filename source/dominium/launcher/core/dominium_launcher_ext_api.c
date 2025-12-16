/*
FILE: source/dominium/launcher/core/dominium_launcher_ext_api.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core/dominium_launcher_ext_api
RESPONSIBILITY: Implements `dominium_launcher_ext_api`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/launcher_ext_api.h"
#include "dominium_launcher_core.h"

#include "domino/mod.h"

int launcher_ext_list_instances(struct dominium_launcher_context* ctx,
                                domino_instance_desc* out,
                                unsigned int max_count,
                                unsigned int* out_count)
{
    return dominium_launcher_list_instances(ctx, out, max_count, out_count);
}

int launcher_ext_run_instance(struct dominium_launcher_context* ctx,
                              const char* instance_id)
{
    return dominium_launcher_run_instance(ctx, instance_id);
}

struct launcher_ext_pkg_ctx {
    domino_package_desc* out;
    unsigned int         max;
    unsigned int         count;
};

static int launcher_ext_pkg_visit(const domino_package_desc* desc, void* user)
{
    struct launcher_ext_pkg_ctx* ctx = (struct launcher_ext_pkg_ctx*)user;
    if (!ctx || !desc) return -1;
    if (ctx->count >= ctx->max) return 1;

    /* TODO: filter for launcher-target packages once manifests expose targets */
    ctx->out[ctx->count++] = *desc;
    return 0;
}

int launcher_ext_list_launcher_packages(struct dominium_launcher_context* ctx,
                                        domino_package_desc* out,
                                        unsigned int max_count,
                                        unsigned int* out_count)
{
    struct launcher_ext_pkg_ctx pctx;
    domino_package_registry* reg;

    if (!ctx || !out) return -1;
    pctx.out = out;
    pctx.max = max_count;
    pctx.count = 0;

    reg = (domino_package_registry*)dominium_launcher_get_registry(ctx);
    if (reg) {
        domino_package_registry_visit(reg, launcher_ext_pkg_visit, &pctx);
    }
    if (out_count) {
        *out_count = pctx.count;
    }
    return 0;
}
