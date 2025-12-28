#import <Cocoa/Cocoa.h>

#include "dsu_macos_args.h"
#include "dsu_macos_bridge.h"
#include "dsu_macos_invocation.h"
#include "dsu_macos_log.h"
#include "dsu_macos_ui.h"

#include "dsu/dsu_callbacks.h"
#include "dsu/dsu_config.h"
#include "dsu/dsu_ctx.h"
#include "dsu/dsu_manifest.h"
#include "dsu/dsu_state.h"

#include <dispatch/dispatch.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(__unix__) || defined(__APPLE__)
#include <sys/stat.h>
#include <unistd.h>
#endif

#define DSU_MACOS_GUI_NAME "dominium-setup-gui"
#define DSU_MACOS_GUI_VERSION "0.0.0"

static void dsu__usage(FILE *out) {
    fprintf(out,
            "%s %s\n"
            "\n"
            "Usage:\n"
            "  %s [--manifest <path>] [--non-interactive] [--defaults]\n"
            "     [--op install|upgrade|repair|uninstall]\n"
            "     [--scope portable|user|system]\n"
            "     [--components <csv>] [--exclude <csv>]\n"
            "     [--install-root <path>] [--platform <triple>]\n"
            "     [--export-invocation --out <path>]\n"
            "     [--plan --out <plan>] [--apply] [--dry-run]\n",
            DSU_MACOS_GUI_NAME, DSU_MACOS_GUI_VERSION,
            DSU_MACOS_GUI_NAME);
}

static int dsu__streq_nocase(const char *a, const char *b) {
    unsigned char ca;
    unsigned char cb;
    if (a == b) return 1;
    if (!a || !b) return 0;
    for (;;) {
        ca = (unsigned char)*a++;
        cb = (unsigned char)*b++;
        if (ca >= 'A' && ca <= 'Z') ca = (unsigned char)(ca - 'A' + 'a');
        if (cb >= 'A' && cb <= 'Z') cb = (unsigned char)(cb - 'A' + 'a');
        if (ca != cb) return 0;
        if (ca == 0u) return 1;
    }
}

static int dsu__file_exists(const char *path) {
#if defined(__unix__) || defined(__APPLE__)
    struct stat st;
    if (!path || !path[0]) return 0;
    return stat(path, &st) == 0;
#else
    (void)path;
    return 0;
#endif
}

static int dsu__file_is_exec(const char *path) {
#if defined(__unix__) || defined(__APPLE__)
    return (path && path[0] && access(path, X_OK) == 0);
#else
    (void)path;
    return 0;
#endif
}

static int dsu__find_in_path(const char *name, char *out, size_t cap) {
    const char *path = getenv("PATH");
    const char *p;
    const char *next;
    char buf[512];
    size_t len;

    if (!name || !out || cap == 0u) return 0;
    out[0] = '\0';

    if (dsu__file_is_exec(name)) {
        strncpy(out, name, cap - 1u);
        out[cap - 1u] = '\0';
        return 1;
    }

    if (!path || !path[0]) return 0;
    p = path;
    while (p && *p) {
        next = strchr(p, ':');
        len = next ? (size_t)(next - p) : strlen(p);
        if (len > 0 && len < sizeof(buf)) {
            memcpy(buf, p, len);
            buf[len] = '\0';
            snprintf(out, cap, "%s/%s", buf, name);
            if (dsu__file_is_exec(out)) {
                return 1;
            }
        }
        if (!next) break;
        p = next + 1;
    }
    out[0] = '\0';
    return 0;
}

static const char *dsu__resolve_exe_path(const char *argv0, const char *name, char *out, size_t cap) {
    const char *slash = NULL;
    if (!name) return "";
    if (out && cap) out[0] = '\0';
    if (argv0) {
        const char *s1 = strrchr(argv0, '/');
        const char *s2 = strrchr(argv0, '\\');
        slash = s1;
        if (s2 && (!slash || s2 > slash)) slash = s2;
        if (slash && out && cap) {
            size_t len = (size_t)(slash - argv0);
            char dir[512];
            if (len >= sizeof(dir)) len = sizeof(dir) - 1u;
            memcpy(dir, argv0, len);
            dir[len] = '\0';
            snprintf(out, cap, "%s/%s", dir, name);
            if (dsu__file_is_exec(out)) {
                return out;
            }
        }
    }
    if (out && cap && dsu__find_in_path(name, out, cap)) {
        return out;
    }
    return name;
}

static const char *dsu__resolve_core_path(const char *argv0, char *out, size_t cap) {
    const char *candidate = dsu__resolve_exe_path(argv0, "dominium-setup", out, cap);
    if (candidate && dsu__file_is_exec(candidate)) {
        return candidate;
    }
    candidate = dsu__resolve_exe_path(argv0, "tool_setup", out, cap);
    if (candidate && dsu__file_is_exec(candidate)) {
        return candidate;
    }
    return "dominium-setup";
}

static const char *dsu__resolve_adapter_path(const char *argv0, char *out, size_t cap) {
    const char *candidate = dsu__resolve_exe_path(argv0, "dominium-setup-macos", out, cap);
    if (candidate && dsu__file_is_exec(candidate)) {
        return candidate;
    }
    return "dominium-setup-macos";
}

static const char *dsu__default_platform(void) {
#if defined(__aarch64__) || defined(__arm64__)
    return "macos-arm64";
#elif defined(__x86_64__) || defined(__amd64__)
    return "macos-x64";
#else
    return "macos-x64";
#endif
}

static const char *dsu__default_manifest_path(const char *argv0, char *out_path, size_t cap) {
    const char *fallback = "setup/manifests/product.dsumanifest";
    const char *slash = NULL;
    char dir[512];
    if (!out_path || cap == 0u) return fallback;
    out_path[0] = '\0';

    if (dsu__file_exists(fallback)) {
        strncpy(out_path, fallback, cap - 1u);
        out_path[cap - 1u] = '\0';
        return out_path;
    }

    if (argv0) {
        const char *s1 = strrchr(argv0, '/');
        const char *s2 = strrchr(argv0, '\\');
        slash = s1;
        if (s2 && (!slash || s2 > slash)) slash = s2;
    }
    if (slash) {
        size_t len = (size_t)(slash - argv0);
        if (len >= sizeof(dir)) len = sizeof(dir) - 1u;
        memcpy(dir, argv0, len);
        dir[len] = '\0';
        if (snprintf(out_path, cap, "%s/manifests/product.dsumanifest", dir) > 0 && dsu__file_exists(out_path)) {
            return out_path;
        }
        if (snprintf(out_path, cap, "%s/../setup/manifests/product.dsumanifest", dir) > 0 && dsu__file_exists(out_path)) {
            return out_path;
        }
    }

    strncpy(out_path, fallback, cap - 1u);
    out_path[cap - 1u] = '\0';
    return out_path;
}

static dsu_manifest_install_scope_t dsu__scope_from_str(const char *s, dsu_manifest_install_scope_t fallback) {
    if (!s || !s[0]) return fallback;
    if (dsu__streq_nocase(s, "system")) return DSU_MANIFEST_INSTALL_SCOPE_SYSTEM;
    if (dsu__streq_nocase(s, "portable")) return DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    if (dsu__streq_nocase(s, "user")) return DSU_MANIFEST_INSTALL_SCOPE_USER;
    return fallback;
}

static int dsu__operation_needs_state(const char *op) {
    if (!op || !op[0]) return 0;
    return dsu__streq_nocase(op, "upgrade") ||
           dsu__streq_nocase(op, "repair") ||
           dsu__streq_nocase(op, "uninstall");
}

static const char *dsu__default_temp_path(const char *name, char *out_path, size_t cap) {
    const char *tmp = getenv("TMPDIR");
    if (!tmp || !tmp[0]) tmp = "/tmp";
    if (!out_path || cap == 0u) return name;
    out_path[0] = '\0';
    snprintf(out_path, cap, "%s/%s", tmp, name);
    return out_path;
}

static int dsu__find_manifest_install_root(const dsu_manifest_t *manifest,
                                           dsu_manifest_install_scope_t scope,
                                           const char *platform,
                                           char *out_root,
                                           size_t out_cap) {
    dsu_u32 count;
    dsu_u32 i;
    const char *found = NULL;
    dsu_u32 found_count = 0u;
    if (!manifest || !platform || !out_root || out_cap == 0u) {
        return 0;
    }
    out_root[0] = '\0';
    count = dsu_manifest_install_root_count(manifest);
    for (i = 0u; i < count; ++i) {
        dsu_manifest_install_scope_t s = dsu_manifest_install_root_scope(manifest, i);
        const char *p = dsu_manifest_install_root_platform(manifest, i);
        const char *path = dsu_manifest_install_root_path(manifest, i);
        if ((dsu_u8)s != (dsu_u8)scope) {
            continue;
        }
        if (!p || strcmp(p, platform) != 0) {
            continue;
        }
        found = path;
        ++found_count;
    }
    if (!found || found_count != 1u) {
        return 0;
    }
    strncpy(out_root, found, out_cap - 1u);
    out_root[out_cap - 1u] = '\0';
    return 1;
}

static int dsu__build_state_path(const char *install_root, char *out_state, size_t cap) {
    if (!install_root || !install_root[0] || !out_state || cap == 0u) {
        return 0;
    }
    snprintf(out_state, cap, "%s/.dsu/installed_state.dsustate", install_root);
    return 1;
}

static int dsu__detect_installed_state(const dsu_manifest_t *manifest,
                                       const char *platform,
                                       char *out_state,
                                       size_t out_cap,
                                       dsu_manifest_install_scope_t *out_scope) {
    dsu_manifest_install_scope_t scopes[3];
    size_t i;
    char root[512];
    char state[512];

    scopes[0] = DSU_MANIFEST_INSTALL_SCOPE_SYSTEM;
    scopes[1] = DSU_MANIFEST_INSTALL_SCOPE_USER;
    scopes[2] = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;

    for (i = 0u; i < 3u; ++i) {
        if (!dsu__find_manifest_install_root(manifest, scopes[i], platform, root, sizeof(root))) {
            continue;
        }
        if (!dsu__build_state_path(root, state, sizeof(state))) {
            continue;
        }
        if (dsu__file_exists(state)) {
            if (out_state && out_cap) {
                strncpy(out_state, state, out_cap - 1u);
                out_state[out_cap - 1u] = '\0';
            }
            if (out_scope) {
                *out_scope = scopes[i];
            }
            return 1;
        }
    }
    return 0;
}

static int dsu__run_platform_register(const dsu_macos_bridge_paths_t *paths,
                                      const char *state_path,
                                      int deterministic,
                                      int quiet) {
    char cmd[1024];
    if (!paths || !paths->adapter_exe_path || !state_path) {
        return 0;
    }
    snprintf(cmd,
             sizeof(cmd),
             "\"%s\" platform-register --state \"%s\"%s",
             paths->adapter_exe_path,
             state_path,
             deterministic ? " --deterministic" : "");
    return (dsu_macos_bridge_spawn(cmd, quiet) == 0);
}

static int dsu__run_platform_unregister(const dsu_macos_bridge_paths_t *paths,
                                        const char *state_path,
                                        int deterministic,
                                        int quiet) {
    char cmd[1024];
    if (!paths || !paths->adapter_exe_path || !state_path) {
        return 0;
    }
    snprintf(cmd,
             sizeof(cmd),
             "\"%s\" platform-unregister --state \"%s\"%s",
             paths->adapter_exe_path,
             state_path,
             deterministic ? " --deterministic" : "");
    return (dsu_macos_bridge_spawn(cmd, quiet) == 0);
}

static int dsu__run_non_interactive(const dsu_macos_cli_args_t *args, const char *argv0) {
    dsu_macos_cli_args_t tmp_args;
    dsu_macos_bridge_paths_t paths;
    dsu_ctx_t *ctx = NULL;
    dsu_manifest_t *manifest = NULL;
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_invocation_t inv;
    char manifest_path[512];
    char install_root[512];
    char state_path[512];
    char platform_buf[64];
    char core_path[512];
    char adapter_path[512];
    char inv_path[512];
    char plan_path[512];
    const char *platform;
    const char *out_inv;
    const char *out_plan;
    dsu_u64 digest = 0u;
    int ok;

    if (!args) return 1;

    tmp_args = *args;
    if (!tmp_args.ui_mode) tmp_args.ui_mode = "gui";
    if (!tmp_args.frontend_id) tmp_args.frontend_id = "gui-macos";
    if (!tmp_args.operation) tmp_args.operation = "install";
    if (!tmp_args.scope) tmp_args.scope = "user";

    platform = tmp_args.platform ? tmp_args.platform : dsu__default_platform();
    strncpy(platform_buf, platform, sizeof(platform_buf) - 1u);
    platform_buf[sizeof(platform_buf) - 1u] = '\0';

    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    if (dsu_ctx_create(&cfg, &cbs, NULL, &ctx) != DSU_STATUS_SUCCESS) {
        dsu_macos_log_error("failed to init setup core");
        return 1;
    }

    dsu__default_manifest_path(argv0, manifest_path, sizeof(manifest_path));
    if (tmp_args.manifest_path && tmp_args.manifest_path[0]) {
        strncpy(manifest_path, tmp_args.manifest_path, sizeof(manifest_path) - 1u);
        manifest_path[sizeof(manifest_path) - 1u] = '\0';
    }

    if (dsu_manifest_load_file(ctx, manifest_path, &manifest) != DSU_STATUS_SUCCESS) {
        dsu_macos_log_error("failed to load manifest: %s", manifest_path);
        dsu_ctx_destroy(ctx);
        return 1;
    }

    if ((!tmp_args.install_root || !tmp_args.install_root[0])) {
        dsu_manifest_install_scope_t scope = dsu__scope_from_str(tmp_args.scope, DSU_MANIFEST_INSTALL_SCOPE_USER);
        if (dsu__find_manifest_install_root(manifest, scope, platform_buf, install_root, sizeof(install_root))) {
            tmp_args.install_root = install_root;
        }
    }
    if ((!tmp_args.state_path || !tmp_args.state_path[0]) && dsu__operation_needs_state(tmp_args.operation)) {
        dsu_manifest_install_scope_t detected_scope = 0;
        if (dsu__detect_installed_state(manifest, platform_buf, state_path, sizeof(state_path), &detected_scope)) {
            tmp_args.state_path = state_path;
        }
    }

    memset(&paths, 0, sizeof(paths));
    paths.manifest_path = manifest_path;
    paths.core_exe_path = dsu__resolve_core_path(argv0, core_path, sizeof(core_path));
    paths.adapter_exe_path = dsu__resolve_adapter_path(argv0, adapter_path, sizeof(adapter_path));

    dsu_invocation_init(&inv);
    out_inv = tmp_args.out_path ? tmp_args.out_path : tmp_args.invocation_path;
    if (!out_inv || !out_inv[0]) {
        out_inv = dsu__default_temp_path("dominium-invocation.tlv", inv_path, sizeof(inv_path));
    }

    ok = dsu_macos_build_invocation(&tmp_args, platform_buf, tmp_args.ui_mode, tmp_args.frontend_id, &inv);
    if (!ok) {
        dsu_macos_log_error("failed to build invocation");
        dsu_invocation_destroy(NULL, &inv);
        dsu_manifest_destroy(ctx, manifest);
        dsu_ctx_destroy(ctx);
        return 1;
    }
    if (!dsu_macos_write_invocation(&inv, out_inv, &digest)) {
        dsu_macos_log_error("failed to write invocation: %s", out_inv);
        dsu_invocation_destroy(NULL, &inv);
        dsu_manifest_destroy(ctx, manifest);
        dsu_ctx_destroy(ctx);
        return 1;
    }
    dsu_macos_log_info("invocation written: %s", out_inv);
    dsu_macos_log_info("invocation digest64: 0x%016llx", (unsigned long long)digest);

    if (tmp_args.export_invocation && !tmp_args.run_plan && !tmp_args.run_apply && !tmp_args.apply_invocation) {
        dsu_invocation_destroy(NULL, &inv);
        dsu_manifest_destroy(ctx, manifest);
        dsu_ctx_destroy(ctx);
        return 0;
    }

    out_plan = tmp_args.plan_path;
    if (!out_plan || !out_plan[0]) {
        out_plan = dsu__default_temp_path("dominium-plan.tlv", plan_path, sizeof(plan_path));
    }

    if (tmp_args.run_plan || tmp_args.run_apply || tmp_args.apply_invocation) {
        if (dsu_macos_bridge_plan(&paths,
                                  out_inv,
                                  out_plan,
                                  tmp_args.state_path,
                                  tmp_args.deterministic,
                                  tmp_args.quiet,
                                  tmp_args.want_json) != 0) {
            dsu_macos_log_error("plan failed");
            dsu_invocation_destroy(NULL, &inv);
            dsu_manifest_destroy(ctx, manifest);
            dsu_ctx_destroy(ctx);
            return 1;
        }
    }

    if (tmp_args.run_plan && !tmp_args.run_apply && !tmp_args.apply_invocation) {
        dsu_invocation_destroy(NULL, &inv);
        dsu_manifest_destroy(ctx, manifest);
        dsu_ctx_destroy(ctx);
        return 0;
    }

    if (tmp_args.apply_invocation) {
        if (dsu_macos_bridge_apply_invocation(&paths, out_inv, tmp_args.deterministic, tmp_args.dry_run, tmp_args.quiet, tmp_args.want_json) != 0) {
            dsu_macos_log_error("apply (invocation) failed");
            dsu_invocation_destroy(NULL, &inv);
            dsu_manifest_destroy(ctx, manifest);
            dsu_ctx_destroy(ctx);
            return 1;
        }
    } else if (tmp_args.run_apply || !tmp_args.export_invocation) {
        if (dsu_macos_bridge_apply_plan(&paths, out_plan, tmp_args.deterministic, tmp_args.dry_run, tmp_args.quiet, tmp_args.want_json) != 0) {
            dsu_macos_log_error("apply failed");
            dsu_invocation_destroy(NULL, &inv);
            dsu_manifest_destroy(ctx, manifest);
            dsu_ctx_destroy(ctx);
            return 1;
        }
    }

    if (tmp_args.install_root && tmp_args.install_root[0]) {
        dsu__build_state_path(tmp_args.install_root, state_path, sizeof(state_path));
        if (dsu__streq_nocase(tmp_args.operation, "uninstall")) {
            (void)dsu__run_platform_unregister(&paths, state_path, tmp_args.deterministic, tmp_args.quiet);
        } else {
            (void)dsu__run_platform_register(&paths, state_path, tmp_args.deterministic, tmp_args.quiet);
        }
    }

    dsu_invocation_destroy(NULL, &inv);
    dsu_manifest_destroy(ctx, manifest);
    dsu_ctx_destroy(ctx);
    return 0;
}

typedef NS_ENUM(NSInteger, DomSetupStep) {
    DomSetupStepDetect = 0,
    DomSetupStepOperation,
    DomSetupStepMode,
    DomSetupStepScope,
    DomSetupStepPath,
    DomSetupStepComponents,
    DomSetupStepSummary,
    DomSetupStepExecute,
    DomSetupStepComplete
};

@interface DomSetupComponent : NSObject
@property(nonatomic, copy) NSString *componentId;
@property(nonatomic, assign) BOOL optional;
@property(nonatomic, assign) BOOL defaultSelected;
@property(nonatomic, assign) BOOL selected;
@property(nonatomic, weak) NSButton *checkbox;
@end

@implementation DomSetupComponent
@end

@interface DomSetupController : NSObject <NSApplicationDelegate>
@property(nonatomic, assign) dsu_ctx_t *ctx;
@property(nonatomic, assign) dsu_manifest_t *manifest;
@property(nonatomic, copy) NSString *manifestPath;
@property(nonatomic, copy) NSString *platform;
@property(nonatomic, copy) NSString *argv0;
@property(nonatomic, copy) NSString *installRoot;
@property(nonatomic, copy) NSString *detectedStatePath;
@property(nonatomic, assign) dsu_manifest_install_scope_t scope;
@property(nonatomic, assign) dsu_u8 operation;
@property(nonatomic, assign) dsu_macos_ui_install_mode_t installMode;
@property(nonatomic, assign) BOOL installedDetected;
@property(nonatomic, assign) BOOL enableShortcuts;
@property(nonatomic, assign) BOOL enableFileAssoc;
@property(nonatomic, assign) BOOL enableUrlHandlers;
@property(nonatomic, strong) NSMutableArray<DomSetupComponent *> *components;

@property(nonatomic, strong) NSWindow *window;
@property(nonatomic, strong) NSView *container;
@property(nonatomic, strong) NSArray<NSView *> *steps;
@property(nonatomic, assign) NSInteger stepIndex;

@property(nonatomic, strong) NSTextField *detectLabel;
@property(nonatomic, strong) NSButton *opInstallButton;
@property(nonatomic, strong) NSButton *opUpgradeButton;
@property(nonatomic, strong) NSButton *opRepairButton;
@property(nonatomic, strong) NSButton *opUninstallButton;
@property(nonatomic, strong) NSButton *modeQuickButton;
@property(nonatomic, strong) NSButton *modeCustomButton;
@property(nonatomic, strong) NSPopUpButton *scopePopup;
@property(nonatomic, strong) NSTextField *pathField;
@property(nonatomic, strong) NSButton *browseButton;
@property(nonatomic, strong) NSButton *shortcutsCheck;
@property(nonatomic, strong) NSButton *fileAssocCheck;
@property(nonatomic, strong) NSButton *urlHandlersCheck;
@property(nonatomic, strong) NSTextView *summaryView;
@property(nonatomic, strong) NSProgressIndicator *executeSpinner;
@property(nonatomic, strong) NSTextField *executeStatus;
@property(nonatomic, strong) NSTextField *completeLabel;
@property(nonatomic, strong) NSButton *backButton;
@property(nonatomic, strong) NSButton *nextButton;
@property(nonatomic, strong) NSButton *cancelButton;

@property(nonatomic, assign) BOOL executionDone;
@property(nonatomic, assign) BOOL executionSuccess;
@end

@implementation DomSetupController
- (instancetype)initWithArgs:(const dsu_macos_cli_args_t *)args argv0:(const char *)argv0 {
    self = [super init];
    if (!self) return nil;
    _argv0 = argv0 ? [NSString stringWithUTF8String:argv0] : @"";

    if (args && args->manifest_path && args->manifest_path[0]) {
        _manifestPath = [NSString stringWithUTF8String:args->manifest_path];
    } else {
        char buf[512];
        dsu__default_manifest_path(argv0, buf, sizeof(buf));
        _manifestPath = [NSString stringWithUTF8String:buf];
    }

    if (args && args->platform && args->platform[0]) {
        _platform = [NSString stringWithUTF8String:args->platform];
    } else {
        _platform = [NSString stringWithUTF8String:dsu__default_platform()];
    }

    _components = [[NSMutableArray alloc] init];
    _scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
    _installMode = DSU_MACOS_UI_INSTALL_MODE_QUICK;
    _operation = (dsu_u8)DSU_INVOCATION_OPERATION_INSTALL;
    _enableShortcuts = YES;
    _enableFileAssoc = NO;
    _enableUrlHandlers = NO;
    _executionDone = NO;
    _executionSuccess = NO;

    return self;
}

- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    (void)notification;
    if (![self loadManifest]) {
        [NSApp terminate:nil];
        return;
    }
    [self detectInstalledState];
    [self loadComponents];
    [self updateInstallRootForScope];
    [self buildWindow];
    [self showStep:DomSetupStepDetect];
}

- (void)applicationWillTerminate:(NSNotification *)notification {
    (void)notification;
    if (self.manifest) {
        dsu_manifest_destroy(self.ctx, self.manifest);
        self.manifest = NULL;
    }
    if (self.ctx) {
        dsu_ctx_destroy(self.ctx);
        self.ctx = NULL;
    }
}

- (BOOL)loadManifest {
    dsu_config_t cfg;
    dsu_callbacks_t cbs;
    dsu_status_t st;

    dsu_config_init(&cfg);
    dsu_callbacks_init(&cbs);
    st = dsu_ctx_create(&cfg, &cbs, NULL, &_ctx);
    if (st != DSU_STATUS_SUCCESS || !self.ctx) {
        dsu_macos_log_error("failed to init setup core");
        return NO;
    }
    st = dsu_manifest_load_file(self.ctx, [self.manifestPath UTF8String], &_manifest);
    if (st != DSU_STATUS_SUCCESS || !self.manifest) {
        dsu_macos_log_error("failed to load manifest: %s", [self.manifestPath UTF8String]);
        return NO;
    }
    return YES;
}

- (void)detectInstalledState {
    char state_path[512];
    dsu_manifest_install_scope_t detected = DSU_MANIFEST_INSTALL_SCOPE_USER;
    self.installedDetected = NO;
    self.detectedStatePath = nil;
    if (dsu__detect_installed_state(self.manifest,
                                    [self.platform UTF8String],
                                    state_path,
                                    sizeof(state_path),
                                    &detected)) {
        self.installedDetected = YES;
        self.detectedStatePath = [NSString stringWithUTF8String:state_path];
        self.scope = detected;
        if (self.operation == DSU_INVOCATION_OPERATION_INSTALL) {
            self.operation = (dsu_u8)DSU_INVOCATION_OPERATION_UPGRADE;
        }
    }
}

- (void)loadComponents {
    dsu_u32 count = dsu_manifest_component_count(self.manifest);
    dsu_u32 i;
    [self.components removeAllObjects];
    for (i = 0u; i < count; ++i) {
        const char *cid = dsu_manifest_component_id(self.manifest, i);
        dsu_u32 flags = dsu_manifest_component_flags(self.manifest, i);
        DomSetupComponent *comp = [[DomSetupComponent alloc] init];
        comp.componentId = cid ? [NSString stringWithUTF8String:cid] : @"";
        comp.optional = (flags & DSU_MANIFEST_COMPONENT_FLAG_OPTIONAL) != 0u;
        comp.defaultSelected = (flags & DSU_MANIFEST_COMPONENT_FLAG_DEFAULT_SELECTED) != 0u;
        comp.selected = (!comp.optional) || comp.defaultSelected;
        [self.components addObject:comp];
    }
}

- (void)updateInstallRootForScope {
    char root[512];
    if (dsu__find_manifest_install_root(self.manifest,
                                        self.scope,
                                        [self.platform UTF8String],
                                        root,
                                        sizeof(root))) {
        self.installRoot = [NSString stringWithUTF8String:root];
    }
    if (self.pathField) {
        [self.pathField setStringValue:self.installRoot ? self.installRoot : @""];
    }
}

- (void)buildWindow {
    NSRect frame = NSMakeRect(0, 0, 640, 420);
    self.window = [[NSWindow alloc] initWithContentRect:frame
                                              styleMask:(NSWindowStyleMaskTitled |
                                                         NSWindowStyleMaskClosable |
                                                         NSWindowStyleMaskMiniaturizable)
                                                backing:NSBackingStoreBuffered
                                                  defer:NO];
    [self.window setTitle:@"Dominium Setup"];
    [self.window center];

    NSView *content = [self.window contentView];
    NSRect bounds = [content bounds];
    CGFloat footerHeight = 52.0;
    self.container = [[NSView alloc] initWithFrame:NSMakeRect(0, footerHeight, bounds.size.width, bounds.size.height - footerHeight)];
    [self.container setAutoresizingMask:NSViewWidthSizable | NSViewHeightSizable];
    [content addSubview:self.container];

    self.backButton = [[NSButton alloc] initWithFrame:NSMakeRect(bounds.size.width - 260, 12, 80, 30)];
    [self.backButton setTitle:@"Back"];
    [self.backButton setTarget:self];
    [self.backButton setAction:@selector(backPressed:)];
    [self.backButton setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];
    [content addSubview:self.backButton];

    self.nextButton = [[NSButton alloc] initWithFrame:NSMakeRect(bounds.size.width - 170, 12, 80, 30)];
    [self.nextButton setTitle:@"Next"];
    [self.nextButton setTarget:self];
    [self.nextButton setAction:@selector(nextPressed:)];
    [self.nextButton setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];
    [content addSubview:self.nextButton];

    self.cancelButton = [[NSButton alloc] initWithFrame:NSMakeRect(bounds.size.width - 80, 12, 70, 30)];
    [self.cancelButton setTitle:@"Cancel"];
    [self.cancelButton setTarget:self];
    [self.cancelButton setAction:@selector(cancelPressed:)];
    [self.cancelButton setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];
    [content addSubview:self.cancelButton];

    self.steps = @[
        [self buildDetectView],
        [self buildOperationView],
        [self buildModeView],
        [self buildScopeView],
        [self buildPathView],
        [self buildComponentsView],
        [self buildSummaryView],
        [self buildExecuteView],
        [self buildCompleteView]
    ];
    for (NSView *view in self.steps) {
        [view setFrame:self.container.bounds];
        [view setAutoresizingMask:NSViewWidthSizable | NSViewHeightSizable];
        [view setHidden:YES];
        [self.container addSubview:view];
    }
    [self.window makeKeyAndOrderFront:nil];
}

- (NSView *)buildDetectView {
    NSView *view = [[NSView alloc] initWithFrame:self.container.bounds];
    NSTextField *title = [self labelWithText:@"Detection"
                                       frame:NSMakeRect(20, view.bounds.size.height - 50, 400, 24)
                                        bold:YES];
    [view addSubview:title];

    self.detectLabel = [self labelWithText:@""
                                     frame:NSMakeRect(20, view.bounds.size.height - 90, 560, 22)
                                      bold:NO];
    [view addSubview:self.detectLabel];
    if (self.installedDetected) {
        NSString *msg = [NSString stringWithFormat:@"Existing installation detected (%@).", self.detectedStatePath ?: @""];
        [self.detectLabel setStringValue:msg];
    } else {
        [self.detectLabel setStringValue:@"No existing installation detected."];
    }
    return view;
}

- (NSView *)buildOperationView {
    NSView *view = [[NSView alloc] initWithFrame:self.container.bounds];
    NSTextField *title = [self labelWithText:@"Operation"
                                       frame:NSMakeRect(20, view.bounds.size.height - 50, 400, 24)
                                        bold:YES];
    [view addSubview:title];

    CGFloat y = view.bounds.size.height - 90;
    self.opInstallButton = [self radioButtonWithTitle:@"Install" frame:NSMakeRect(40, y, 200, 22) action:@selector(operationChanged:)];
    self.opUpgradeButton = [self radioButtonWithTitle:@"Upgrade" frame:NSMakeRect(40, y - 30, 200, 22) action:@selector(operationChanged:)];
    self.opRepairButton = [self radioButtonWithTitle:@"Repair" frame:NSMakeRect(40, y - 60, 200, 22) action:@selector(operationChanged:)];
    self.opUninstallButton = [self radioButtonWithTitle:@"Uninstall" frame:NSMakeRect(40, y - 90, 200, 22) action:@selector(operationChanged:)];

    [view addSubview:self.opInstallButton];
    [view addSubview:self.opUpgradeButton];
    [view addSubview:self.opRepairButton];
    [view addSubview:self.opUninstallButton];

    [self updateOperationButtons];
    return view;
}

- (NSView *)buildModeView {
    NSView *view = [[NSView alloc] initWithFrame:self.container.bounds];
    NSTextField *title = [self labelWithText:@"Install Mode"
                                       frame:NSMakeRect(20, view.bounds.size.height - 50, 400, 24)
                                        bold:YES];
    [view addSubview:title];

    CGFloat y = view.bounds.size.height - 90;
    self.modeQuickButton = [self radioButtonWithTitle:@"Quick Install (recommended)"
                                                frame:NSMakeRect(40, y, 280, 22)
                                               action:@selector(modeChanged:)];
    self.modeCustomButton = [self radioButtonWithTitle:@"Custom Install"
                                                 frame:NSMakeRect(40, y - 30, 200, 22)
                                                action:@selector(modeChanged:)];

    [view addSubview:self.modeQuickButton];
    [view addSubview:self.modeCustomButton];
    [self updateModeButtons];
    return view;
}

- (NSView *)buildScopeView {
    NSView *view = [[NSView alloc] initWithFrame:self.container.bounds];
    NSTextField *title = [self labelWithText:@"Scope"
                                       frame:NSMakeRect(20, view.bounds.size.height - 50, 400, 24)
                                        bold:YES];
    [view addSubview:title];

    NSTextField *label = [self labelWithText:@"Install scope:"
                                       frame:NSMakeRect(20, view.bounds.size.height - 90, 120, 22)
                                        bold:NO];
    [view addSubview:label];

    self.scopePopup = [[NSPopUpButton alloc] initWithFrame:NSMakeRect(150, view.bounds.size.height - 94, 260, 26)];
    [self.scopePopup addItemsWithTitles:@[@"User", @"System", @"Portable"]];
    [self.scopePopup setTarget:self];
    [self.scopePopup setAction:@selector(scopeChanged:)];
    [view addSubview:self.scopePopup];

    [self updateScopePopup];
    return view;
}

- (NSView *)buildPathView {
    NSView *view = [[NSView alloc] initWithFrame:self.container.bounds];
    NSTextField *title = [self labelWithText:@"Install Path"
                                       frame:NSMakeRect(20, view.bounds.size.height - 50, 400, 24)
                                        bold:YES];
    [view addSubview:title];

    NSTextField *label = [self labelWithText:@"Install location:"
                                       frame:NSMakeRect(20, view.bounds.size.height - 90, 120, 22)
                                        bold:NO];
    [view addSubview:label];

    self.pathField = [[NSTextField alloc] initWithFrame:NSMakeRect(150, view.bounds.size.height - 94, 360, 24)];
    [self.pathField setStringValue:self.installRoot ? self.installRoot : @""];
    [view addSubview:self.pathField];

    self.browseButton = [[NSButton alloc] initWithFrame:NSMakeRect(520, view.bounds.size.height - 96, 90, 28)];
    [self.browseButton setTitle:@"Browse..."];
    [self.browseButton setTarget:self];
    [self.browseButton setAction:@selector(browsePressed:)];
    [view addSubview:self.browseButton];

    return view;
}

- (NSView *)buildComponentsView {
    NSView *view = [[NSView alloc] initWithFrame:self.container.bounds];
    NSTextField *title = [self labelWithText:@"Components"
                                       frame:NSMakeRect(20, view.bounds.size.height - 50, 400, 24)
                                        bold:YES];
    [view addSubview:title];

    CGFloat listTop = view.bounds.size.height - 90;
    NSScrollView *scroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(20, 120, view.bounds.size.width - 40, listTop - 120)];
    [scroll setHasVerticalScroller:YES];
    NSView *doc = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, scroll.contentView.bounds.size.width, 10)];

    CGFloat y = listTop - 20;
    for (NSUInteger i = 0; i < [self.components count]; ++i) {
        DomSetupComponent *comp = self.components[i];
        NSString *label = comp.componentId.length ? comp.componentId : [NSString stringWithFormat:@"component_%lu", (unsigned long)i];
        NSButton *check = [[NSButton alloc] initWithFrame:NSMakeRect(0, y, scroll.contentView.bounds.size.width - 20, 22)];
        [check setButtonType:NSSwitchButton];
        [check setTitle:label];
        [check setState:comp.selected ? NSControlStateValueOn : NSControlStateValueOff];
        if (!comp.optional) {
            [check setEnabled:NO];
        }
        [check setTarget:self];
        [check setAction:@selector(componentToggled:)];
        [check setTag:(NSInteger)i];
        [doc addSubview:check];
        comp.checkbox = check;
        y -= 26;
    }
    [doc setFrame:NSMakeRect(0, 0, scroll.contentView.bounds.size.width, listTop - y)];
    [scroll setDocumentView:doc];
    [view addSubview:scroll];

    self.shortcutsCheck = [[NSButton alloc] initWithFrame:NSMakeRect(20, 80, 240, 22)];
    [self.shortcutsCheck setButtonType:NSSwitchButton];
    [self.shortcutsCheck setTitle:@"Enable shortcuts"];
    [self.shortcutsCheck setState:self.enableShortcuts ? NSControlStateValueOn : NSControlStateValueOff];
    [self.shortcutsCheck setTarget:self];
    [self.shortcutsCheck setAction:@selector(policyToggled:)];
    [view addSubview:self.shortcutsCheck];

    self.fileAssocCheck = [[NSButton alloc] initWithFrame:NSMakeRect(20, 52, 240, 22)];
    [self.fileAssocCheck setButtonType:NSSwitchButton];
    [self.fileAssocCheck setTitle:@"Enable file associations"];
    [self.fileAssocCheck setState:self.enableFileAssoc ? NSControlStateValueOn : NSControlStateValueOff];
    [self.fileAssocCheck setTarget:self];
    [self.fileAssocCheck setAction:@selector(policyToggled:)];
    [view addSubview:self.fileAssocCheck];

    self.urlHandlersCheck = [[NSButton alloc] initWithFrame:NSMakeRect(20, 24, 240, 22)];
    [self.urlHandlersCheck setButtonType:NSSwitchButton];
    [self.urlHandlersCheck setTitle:@"Enable URL handlers"];
    [self.urlHandlersCheck setState:self.enableUrlHandlers ? NSControlStateValueOn : NSControlStateValueOff];
    [self.urlHandlersCheck setTarget:self];
    [self.urlHandlersCheck setAction:@selector(policyToggled:)];
    [view addSubview:self.urlHandlersCheck];

    return view;
}

- (NSView *)buildSummaryView {
    NSView *view = [[NSView alloc] initWithFrame:self.container.bounds];
    NSTextField *title = [self labelWithText:@"Summary"
                                       frame:NSMakeRect(20, view.bounds.size.height - 50, 400, 24)
                                        bold:YES];
    [view addSubview:title];

    NSScrollView *scroll = [[NSScrollView alloc] initWithFrame:NSMakeRect(20, 20, view.bounds.size.width - 40, view.bounds.size.height - 80)];
    [scroll setHasVerticalScroller:YES];
    self.summaryView = [[NSTextView alloc] initWithFrame:NSMakeRect(0, 0, scroll.contentView.bounds.size.width, scroll.contentView.bounds.size.height)];
    [self.summaryView setEditable:NO];
    [self.summaryView setSelectable:YES];
    [self.summaryView setRichText:NO];
    [scroll setDocumentView:self.summaryView];
    [view addSubview:scroll];
    return view;
}

- (NSView *)buildExecuteView {
    NSView *view = [[NSView alloc] initWithFrame:self.container.bounds];
    NSTextField *title = [self labelWithText:@"Executing"
                                       frame:NSMakeRect(20, view.bounds.size.height - 50, 400, 24)
                                        bold:YES];
    [view addSubview:title];

    self.executeSpinner = [[NSProgressIndicator alloc] initWithFrame:NSMakeRect(20, view.bounds.size.height - 90, 32, 32)];
    [self.executeSpinner setStyle:NSProgressIndicatorSpinningStyle];
    [self.executeSpinner setDisplayedWhenStopped:NO];
    [view addSubview:self.executeSpinner];

    self.executeStatus = [self labelWithText:@"Preparing..."
                                       frame:NSMakeRect(60, view.bounds.size.height - 84, 500, 22)
                                        bold:NO];
    [view addSubview:self.executeStatus];
    return view;
}

- (NSView *)buildCompleteView {
    NSView *view = [[NSView alloc] initWithFrame:self.container.bounds];
    NSTextField *title = [self labelWithText:@"Complete"
                                       frame:NSMakeRect(20, view.bounds.size.height - 50, 400, 24)
                                        bold:YES];
    [view addSubview:title];
    self.completeLabel = [self labelWithText:@""
                                       frame:NSMakeRect(20, view.bounds.size.height - 90, 560, 22)
                                        bold:NO];
    [view addSubview:self.completeLabel];
    return view;
}

- (NSTextField *)labelWithText:(NSString *)text frame:(NSRect)frame bold:(BOOL)bold {
    NSTextField *label = [[NSTextField alloc] initWithFrame:frame];
    [label setStringValue:text ?: @""];
    [label setEditable:NO];
    [label setBezeled:NO];
    [label setDrawsBackground:NO];
    if (bold) {
        [label setFont:[NSFont boldSystemFontOfSize:13.0]];
    }
    return label;
}

- (NSButton *)radioButtonWithTitle:(NSString *)title frame:(NSRect)frame action:(SEL)action {
    NSButton *button = [[NSButton alloc] initWithFrame:frame];
    [button setButtonType:NSRadioButton];
    [button setTitle:title ?: @""];
    [button setTarget:self];
    [button setAction:action];
    return button;
}

- (void)showStep:(NSInteger)index {
    if (index < 0 || index >= (NSInteger)[self.steps count]) {
        return;
    }
    self.stepIndex = index;
    for (NSInteger i = 0; i < (NSInteger)[self.steps count]; ++i) {
        NSView *view = self.steps[i];
        [view setHidden:(i != index)];
    }
    if (index == DomSetupStepSummary) {
        [self updateSummary];
    }
    if (index == DomSetupStepExecute) {
        [self startExecution];
    }
    if (index == DomSetupStepComplete) {
        if (self.executionSuccess) {
            [self.completeLabel setStringValue:@"Completed successfully."];
        } else {
            [self.completeLabel setStringValue:@"Setup failed. See logs for details."];
        }
    }
    [self updateButtons];
}

- (void)updateButtons {
    BOOL onExecute = (self.stepIndex == DomSetupStepExecute);
    BOOL onComplete = (self.stepIndex == DomSetupStepComplete);
    [self.backButton setEnabled:(self.stepIndex > DomSetupStepDetect && !onExecute && !onComplete)];
    if (onComplete) {
        [self.nextButton setTitle:@"Finish"];
        [self.nextButton setEnabled:YES];
    } else if (self.stepIndex == DomSetupStepSummary) {
        const char *label = "Install";
        if (self.operation == DSU_INVOCATION_OPERATION_UNINSTALL) {
            label = "Remove";
        } else if (self.operation == DSU_INVOCATION_OPERATION_REPAIR) {
            label = "Repair";
        } else if (self.operation == DSU_INVOCATION_OPERATION_UPGRADE) {
            label = "Upgrade";
        }
        [self.nextButton setTitle:[NSString stringWithUTF8String:label]];
        [self.nextButton setEnabled:YES];
    } else {
        [self.nextButton setTitle:@"Next"];
        [self.nextButton setEnabled:!onExecute];
    }
}

- (NSInteger)nextStepIndexFrom:(NSInteger)index {
    if (index == DomSetupStepPath && self.installMode == DSU_MACOS_UI_INSTALL_MODE_QUICK) {
        return DomSetupStepSummary;
    }
    return index + 1;
}

- (NSInteger)prevStepIndexFrom:(NSInteger)index {
    if (index == DomSetupStepSummary && self.installMode == DSU_MACOS_UI_INSTALL_MODE_QUICK) {
        return DomSetupStepPath;
    }
    return index - 1;
}

- (void)backPressed:(id)sender {
    (void)sender;
    if (self.stepIndex == DomSetupStepDetect) return;
    if (self.stepIndex == DomSetupStepExecute || self.stepIndex == DomSetupStepComplete) return;
    NSInteger prev = [self prevStepIndexFrom:self.stepIndex];
    if (prev >= 0) {
        [self showStep:prev];
    }
}

- (void)nextPressed:(id)sender {
    (void)sender;
    if (self.stepIndex == DomSetupStepComplete) {
        [NSApp terminate:nil];
        return;
    }
    if (self.stepIndex == DomSetupStepPath) {
        NSString *path = [self.pathField stringValue];
        if (!path || path.length == 0) {
            [self showAlert:@"Install path is required."];
            return;
        }
        self.installRoot = path;
    }
    if (self.stepIndex == DomSetupStepSummary) {
        [self showStep:DomSetupStepExecute];
        return;
    }
    NSInteger next = [self nextStepIndexFrom:self.stepIndex];
    if (next < (NSInteger)[self.steps count]) {
        [self showStep:next];
    }
}

- (void)cancelPressed:(id)sender {
    (void)sender;
    [NSApp terminate:nil];
}

- (void)operationChanged:(id)sender {
    (void)sender;
    if ([self.opInstallButton state] == NSControlStateValueOn) {
        self.operation = (dsu_u8)DSU_INVOCATION_OPERATION_INSTALL;
    } else if ([self.opUpgradeButton state] == NSControlStateValueOn) {
        self.operation = (dsu_u8)DSU_INVOCATION_OPERATION_UPGRADE;
    } else if ([self.opRepairButton state] == NSControlStateValueOn) {
        self.operation = (dsu_u8)DSU_INVOCATION_OPERATION_REPAIR;
    } else if ([self.opUninstallButton state] == NSControlStateValueOn) {
        self.operation = (dsu_u8)DSU_INVOCATION_OPERATION_UNINSTALL;
    }
}

- (void)modeChanged:(id)sender {
    (void)sender;
    if ([self.modeCustomButton state] == NSControlStateValueOn) {
        self.installMode = DSU_MACOS_UI_INSTALL_MODE_CUSTOM;
    } else {
        self.installMode = DSU_MACOS_UI_INSTALL_MODE_QUICK;
    }
    [self updateModeButtons];
}

- (void)scopeChanged:(id)sender {
    (void)sender;
    NSInteger idx = [self.scopePopup indexOfSelectedItem];
    if (idx == 1) {
        self.scope = DSU_MANIFEST_INSTALL_SCOPE_SYSTEM;
    } else if (idx == 2) {
        self.scope = DSU_MANIFEST_INSTALL_SCOPE_PORTABLE;
    } else {
        self.scope = DSU_MANIFEST_INSTALL_SCOPE_USER;
    }
    [self updateInstallRootForScope];
}

- (void)browsePressed:(id)sender {
    (void)sender;
    NSOpenPanel *panel = [NSOpenPanel openPanel];
    [panel setCanChooseDirectories:YES];
    [panel setCanChooseFiles:NO];
    [panel setAllowsMultipleSelection:NO];
    [panel setMessage:@"Select install location"];
    [panel beginSheetModalForWindow:self.window completionHandler:^(NSModalResponse result) {
        if (result == NSModalResponseOK) {
            NSURL *url = [[panel URLs] firstObject];
            if (url) {
                [self.pathField setStringValue:[url path]];
            }
        }
    }];
}

- (void)componentToggled:(id)sender {
    NSButton *button = (NSButton *)sender;
    NSInteger idx = [button tag];
    if (idx < 0 || idx >= (NSInteger)[self.components count]) return;
    DomSetupComponent *comp = self.components[idx];
    comp.selected = ([button state] == NSControlStateValueOn);
}

- (void)policyToggled:(id)sender {
    (void)sender;
    self.enableShortcuts = ([self.shortcutsCheck state] == NSControlStateValueOn);
    self.enableFileAssoc = ([self.fileAssocCheck state] == NSControlStateValueOn);
    self.enableUrlHandlers = ([self.urlHandlersCheck state] == NSControlStateValueOn);
}

- (void)updateOperationButtons {
    [self.opInstallButton setState:(self.operation == DSU_INVOCATION_OPERATION_INSTALL) ? NSControlStateValueOn : NSControlStateValueOff];
    [self.opUpgradeButton setState:(self.operation == DSU_INVOCATION_OPERATION_UPGRADE) ? NSControlStateValueOn : NSControlStateValueOff];
    [self.opRepairButton setState:(self.operation == DSU_INVOCATION_OPERATION_REPAIR) ? NSControlStateValueOn : NSControlStateValueOff];
    [self.opUninstallButton setState:(self.operation == DSU_INVOCATION_OPERATION_UNINSTALL) ? NSControlStateValueOn : NSControlStateValueOff];
}

- (void)updateModeButtons {
    [self.modeQuickButton setState:(self.installMode == DSU_MACOS_UI_INSTALL_MODE_QUICK) ? NSControlStateValueOn : NSControlStateValueOff];
    [self.modeCustomButton setState:(self.installMode == DSU_MACOS_UI_INSTALL_MODE_CUSTOM) ? NSControlStateValueOn : NSControlStateValueOff];
    if (self.pathField) {
        BOOL custom = (self.installMode == DSU_MACOS_UI_INSTALL_MODE_CUSTOM);
        [self.pathField setEnabled:custom];
        if (self.browseButton) {
            [self.browseButton setEnabled:custom];
        }
    }
}

- (void)updateScopePopup {
    NSInteger idx = 0;
    if (self.scope == DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) {
        idx = 1;
    } else if (self.scope == DSU_MANIFEST_INSTALL_SCOPE_PORTABLE) {
        idx = 2;
    }
    [self.scopePopup selectItemAtIndex:idx];
}

- (void)updateSummary {
    NSMutableString *summary = [[NSMutableString alloc] init];
    NSString *op = @"install";
    if (self.operation == DSU_INVOCATION_OPERATION_UPGRADE) op = @"upgrade";
    if (self.operation == DSU_INVOCATION_OPERATION_REPAIR) op = @"repair";
    if (self.operation == DSU_INVOCATION_OPERATION_UNINSTALL) op = @"uninstall";
    NSString *scope = @"user";
    if (self.scope == DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) scope = @"system";
    if (self.scope == DSU_MANIFEST_INSTALL_SCOPE_PORTABLE) scope = @"portable";

    [summary appendFormat:@"Operation: %@\n", op];
    [summary appendFormat:@"Scope: %@\n", scope];
    [summary appendFormat:@"Install root: %@\n", self.installRoot ?: @""];
    [summary appendFormat:@"Platform: %@\n", self.platform ?: @""];
    [summary appendFormat:@"Install mode: %@\n",
        (self.installMode == DSU_MACOS_UI_INSTALL_MODE_CUSTOM) ? @"custom" : @"quick"];

    if (self.installMode == DSU_MACOS_UI_INSTALL_MODE_CUSTOM) {
        NSMutableArray *ids = [[NSMutableArray alloc] init];
        for (DomSetupComponent *comp in self.components) {
            if (comp.selected && comp.componentId.length > 0) {
                [ids addObject:comp.componentId];
            }
        }
        if ([ids count] > 0) {
            [summary appendFormat:@"Components: %@\n", [ids componentsJoinedByString:@","]];
        } else {
            [summary appendString:@"Components: defaults\n"];
        }
        [summary appendFormat:@"Shortcuts: %@\n", self.enableShortcuts ? @"on" : @"off"];
        [summary appendFormat:@"File associations: %@\n", self.enableFileAssoc ? @"on" : @"off"];
        [summary appendFormat:@"URL handlers: %@\n", self.enableUrlHandlers ? @"on" : @"off"];
    } else {
        [summary appendString:@"Components: defaults\n"];
    }

    {
        dsu_macos_cli_args_t call_args;
        dsu_invocation_t inv;
        dsu_u64 digest;
        NSString *componentsCsv = nil;

        memset(&call_args, 0, sizeof(call_args));
        call_args.deterministic = 1;
        call_args.platform = [self.platform UTF8String];
        call_args.ui_mode = "gui";
        call_args.frontend_id = "gui-macos";
        call_args.scope = [scope UTF8String];
        call_args.operation = [op UTF8String];
        call_args.install_root = [self.installRoot UTF8String];
        if (self.installMode == DSU_MACOS_UI_INSTALL_MODE_CUSTOM) {
            NSMutableArray *ids = [[NSMutableArray alloc] init];
            for (DomSetupComponent *comp in self.components) {
                if (comp.selected && comp.componentId.length > 0) {
                    [ids addObject:comp.componentId];
                }
            }
            if ([ids count] > 0) {
                componentsCsv = [ids componentsJoinedByString:@","];
                call_args.components_csv = [componentsCsv UTF8String];
            }
            call_args.policy_shortcuts = self.enableShortcuts ? 1 : 0;
            call_args.policy_file_assoc = self.enableFileAssoc ? 1 : 0;
            call_args.policy_url_handlers = self.enableUrlHandlers ? 1 : 0;
        }

        dsu_invocation_init(&inv);
        if (dsu_macos_build_invocation(&call_args, [self.platform UTF8String], "gui", "gui-macos", &inv)) {
            digest = dsu_invocation_digest(&inv);
            [summary appendFormat:@"Invocation digest64: 0x%016llx\n", (unsigned long long)digest];
        } else {
            [summary appendString:@"Invocation digest64: error\n"];
        }
        dsu_invocation_destroy(NULL, &inv);
    }

    [self.summaryView setString:summary];
}

- (void)startExecution {
    if (self.executionDone) return;
    [self.executeSpinner startAnimation:nil];
    [self.executeStatus setStringValue:@"Running Setup Core..."];
    self.executionDone = NO;
    self.executionSuccess = NO;

    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        BOOL ok = [self runApply];
        dispatch_async(dispatch_get_main_queue(), ^{
            self.executionDone = YES;
            self.executionSuccess = ok;
            [self.executeSpinner stopAnimation:nil];
            [self.executeStatus setStringValue:ok ? @"Completed successfully." : @"Setup failed."];
            [self showStep:DomSetupStepComplete];
        });
    });
}

- (BOOL)runApply {
    dsu_macos_bridge_paths_t paths;
    char core_path[512];
    char adapter_path[512];
    char inv_path[512];
    char plan_path[512];
    char state_path[512];
    const char *state_arg = NULL;
    NSString *scope = @"user";
    NSString *op = @"install";
    NSString *componentsCsv = nil;
    dsu_invocation_t inv;
    dsu_macos_cli_args_t call_args;
    dsu_u64 digest = 0u;
    int rc;

    if (self.scope == DSU_MANIFEST_INSTALL_SCOPE_SYSTEM) scope = @"system";
    if (self.scope == DSU_MANIFEST_INSTALL_SCOPE_PORTABLE) scope = @"portable";
    if (self.operation == DSU_INVOCATION_OPERATION_UPGRADE) op = @"upgrade";
    if (self.operation == DSU_INVOCATION_OPERATION_REPAIR) op = @"repair";
    if (self.operation == DSU_INVOCATION_OPERATION_UNINSTALL) op = @"uninstall";

    memset(&call_args, 0, sizeof(call_args));
    call_args.deterministic = 1;
    call_args.platform = [self.platform UTF8String];
    call_args.ui_mode = "gui";
    call_args.frontend_id = "gui-macos";
    call_args.scope = [scope UTF8String];
    call_args.operation = [op UTF8String];
    call_args.install_root = [self.installRoot UTF8String];

    if (self.installMode == DSU_MACOS_UI_INSTALL_MODE_CUSTOM) {
        NSMutableArray *ids = [[NSMutableArray alloc] init];
        for (DomSetupComponent *comp in self.components) {
            if (comp.selected && comp.componentId.length > 0) {
                [ids addObject:comp.componentId];
            }
        }
        if ([ids count] > 0) {
            componentsCsv = [ids componentsJoinedByString:@","];
            call_args.components_csv = [componentsCsv UTF8String];
        }
        call_args.policy_shortcuts = self.enableShortcuts ? 1 : 0;
        call_args.policy_file_assoc = self.enableFileAssoc ? 1 : 0;
        call_args.policy_url_handlers = self.enableUrlHandlers ? 1 : 0;
    }

    dsu_invocation_init(&inv);
    if (!dsu_macos_build_invocation(&call_args, [self.platform UTF8String], "gui", "gui-macos", &inv)) {
        dsu_macos_log_error("failed to build invocation");
        dsu_invocation_destroy(NULL, &inv);
        return NO;
    }

    dsu__default_temp_path("dominium-invocation.tlv", inv_path, sizeof(inv_path));
    dsu__default_temp_path("dominium-plan.tlv", plan_path, sizeof(plan_path));

    if (!dsu_macos_write_invocation(&inv, inv_path, &digest)) {
        dsu_macos_log_error("failed to write invocation");
        dsu_invocation_destroy(NULL, &inv);
        return NO;
    }
    dsu_macos_log_info("invocation digest64: 0x%016llx", (unsigned long long)digest);

    memset(&paths, 0, sizeof(paths));
    paths.manifest_path = [self.manifestPath UTF8String];
    paths.core_exe_path = dsu__resolve_core_path([self.argv0 UTF8String], core_path, sizeof(core_path));
    paths.adapter_exe_path = dsu__resolve_adapter_path([self.argv0 UTF8String], adapter_path, sizeof(adapter_path));

    if (self.operation != DSU_INVOCATION_OPERATION_INSTALL) {
        if (self.detectedStatePath && self.detectedStatePath.length > 0) {
            state_arg = [self.detectedStatePath UTF8String];
        } else if (self.installRoot && self.installRoot.length > 0) {
            if (dsu__build_state_path([self.installRoot UTF8String], state_path, sizeof(state_path))) {
                state_arg = state_path;
            }
        }
    }

    rc = dsu_macos_bridge_plan(&paths, inv_path, plan_path, state_arg, 1, 0, 0);
    if (rc != 0) {
        dsu_macos_log_error("plan failed");
        dsu_invocation_destroy(NULL, &inv);
        return NO;
    }

    rc = dsu_macos_bridge_apply_plan(&paths, plan_path, 1, 0, 0, 0);
    if (rc != 0) {
        dsu_macos_log_error("apply failed");
        dsu_invocation_destroy(NULL, &inv);
        return NO;
    }

    if (self.installRoot && self.installRoot.length > 0) {
        dsu__build_state_path([self.installRoot UTF8String], state_path, sizeof(state_path));
        if (self.operation == DSU_INVOCATION_OPERATION_UNINSTALL) {
            (void)dsu__run_platform_unregister(&paths, state_path, 1, 0);
        } else {
            (void)dsu__run_platform_register(&paths, state_path, 1, 0);
        }
    }

    dsu_invocation_destroy(NULL, &inv);
    return YES;
}

- (void)showAlert:(NSString *)message {
    NSAlert *alert = [[NSAlert alloc] init];
    [alert setMessageText:@"Dominium Setup"];
    [alert setInformativeText:message ?: @"Unknown error."];
    [alert addButtonWithTitle:@"OK"];
    [alert runModal];
}

@end

int main(int argc, char **argv) {
    dsu_macos_cli_args_t args;
    if (!dsu_macos_args_parse(argc, argv, &args)) {
        dsu__usage(stderr);
        return 2;
    }
    if (args.want_help) {
        dsu__usage(stdout);
        return 0;
    }
    if (args.want_version) {
        fprintf(stdout, "%s %s\n", DSU_MACOS_GUI_NAME, DSU_MACOS_GUI_VERSION);
        return 0;
    }
    if (args.log_path) {
        dsu_macos_log_set_file(args.log_path);
    }
    if (args.export_invocation || args.apply_invocation || args.run_plan ||
        args.run_apply || args.non_interactive || args.use_defaults) {
        return dsu__run_non_interactive(&args, argv[0]);
    }

    @autoreleasepool {
        DomSetupController *controller = [[DomSetupController alloc] initWithArgs:&args argv0:argv[0]];
        NSApplication *app = [NSApplication sharedApplication];
        [app setActivationPolicy:NSApplicationActivationPolicyRegular];
        [app setDelegate:controller];
        [app run];
    }
    return 0;
}
