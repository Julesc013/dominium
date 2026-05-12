/*
FILE: source/dominium/setup/core/dominium_setup_core.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/core/dominium_setup_core
RESPONSIBILITY: Implements `dominium_setup_core`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium_setup_core.h"
#include "domino/sys.h"
#include <string.h>

static void dom_join_path(char* dst, size_t cap,
                          const char* a, const char* b)
{
    size_t i = 0;
    size_t j = 0;
    if (!dst || cap == 0) return;
    if (!a) a = "";
    if (!b) b = "";
    while (a[i] != '\0' && i + 1 < cap) {
        dst[i] = a[i];
        ++i;
    }
    if (i > 0 && i + 1 < cap) {
        char c = dst[i - 1];
        if (c != '/' && c != '\\') {
            dst[i++] = '/';
        }
    }
    while (b[j] != '\0' && i + 1 < cap) {
        dst[i++] = b[j++];
    }
    dst[i] = '\0';
}

static void dom_log_stub(domino_sys_context* sys,
                         const char* msg)
{
    if (sys && msg) {
        domino_sys_log(sys, DOMINO_LOG_INFO, "setup", msg);
    }
}

static int dom_setup_prepare_roots(domino_sys_context* sys,
                                   const char* install_root)
{
    char path[260];
    if (!sys || !install_root) return -1;
    dom_join_path(path, sizeof(path), install_root, "program");
    domino_sys_mkdirs(sys, path);
    dom_join_path(path, sizeof(path), install_root, "data");
    domino_sys_mkdirs(sys, path);
    dom_join_path(path, sizeof(path), install_root, "user");
    domino_sys_mkdirs(sys, path);
    dom_join_path(path, sizeof(path), install_root, "state");
    domino_sys_mkdirs(sys, path);
    return 0;
}

int dominium_setup_execute(const dominium_setup_plan* plan)
{
    domino_sys_context* sys = NULL;
    domino_sys_desc sdesc;
    domino_sys_paths paths;
    char install_root[260];
    char msg[256];

    if (!plan) return -1;

    sdesc.profile_hint = DOMINO_SYS_PROFILE_FULL;
    if (domino_sys_init(&sdesc, &sys) != 0) {
        return -1;
    }

    domino_sys_get_paths(sys, &paths);
    if (plan->install_root[0]) {
        strncpy(install_root, plan->install_root, sizeof(install_root) - 1);
        install_root[sizeof(install_root) - 1] = '\0';
    } else {
        strncpy(install_root, paths.install_root, sizeof(install_root) - 1);
        install_root[sizeof(install_root) - 1] = '\0';
    }

    switch (plan->mode) {
    case DOMINIUM_SETUP_MODE_INSTALL:
        dom_setup_prepare_roots(sys, install_root);
        dom_log_stub(sys, "Install: prepared install roots");
        /* TODO: copy binaries/content into program/<product>/<version> */
        break;
    case DOMINIUM_SETUP_MODE_REPAIR:
        strncpy(msg, "Repair: stub for product ", sizeof(msg) - 1);
        msg[sizeof(msg) - 1] = '\0';
        strncat(msg, plan->product_id, sizeof(msg) - strlen(msg) - 1);
        dom_log_stub(sys, msg);
        break;
    case DOMINIUM_SETUP_MODE_UNINSTALL:
        strncpy(msg, "Uninstall: stub for product ", sizeof(msg) - 1);
        msg[sizeof(msg) - 1] = '\0';
        strncat(msg, plan->product_id, sizeof(msg) - strlen(msg) - 1);
        dom_log_stub(sys, msg);
        break;
    default:
        domino_sys_shutdown(sys);
        return -1;
    }

    domino_sys_shutdown(sys);
    return 0;
}
