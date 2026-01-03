/*
FILE: tools/ui_preview_host/macos/ui_preview_host_macos.cpp
MODULE: Dominium tools
RESPONSIBILITY: macOS UI preview host (native DUI backend + hot reload).
*/
#include <stdio.h>
#include <string.h>
#include <string>
#include <vector>

#include "dui/dui_api_v1.h"
#include "ui_preview_common.h"

#if !defined(__APPLE__)

int main(int argc, char** argv)
{
    (void)argc;
    (void)argv;
    printf("dominium-ui-preview-host-macos: not supported on this platform.\n");
    return 0;
}

#else

#include <fcntl.h>
#include <sys/event.h>
#include <sys/types.h>
#include <unistd.h>

extern "C" const void* dom_dui_macos_get_api(u32 requested_abi);
extern "C" const void* dom_dui_null_get_api(u32 requested_abi);

struct PreviewOptions {
    std::string ui_path;
    std::string targets;
    std::string log_path;
    int watch;
    int show_help;
    PreviewOptions() : ui_path(), targets(), log_path(), watch(0), show_help(0) {}
};

struct MacWatcher {
    int kq;
    std::vector<int> fds;

    MacWatcher() : kq(-1) {}

    void clear()
    {
        for (size_t i = 0u; i < fds.size(); ++i) {
            close(fds[i]);
        }
        fds.clear();
        if (kq >= 0) {
            close(kq);
        }
        kq = -1;
    }

    bool init(const std::vector<std::string>& dirs)
    {
        clear();
        kq = kqueue();
        if (kq < 0) {
            return false;
        }
        for (size_t i = 0u; i < dirs.size(); ++i) {
            int fd = open(dirs[i].c_str(), O_EVTONLY);
            if (fd < 0) {
                continue;
            }
            struct kevent ev;
            EV_SET(&ev,
                   fd,
                   EVFILT_VNODE,
                   EV_ADD | EV_CLEAR,
                   NOTE_WRITE | NOTE_DELETE | NOTE_RENAME | NOTE_EXTEND | NOTE_ATTRIB,
                   0,
                   0);
            if (kevent(kq, &ev, 1, NULL, 0, NULL) == 0) {
                fds.push_back(fd);
            } else {
                close(fd);
            }
        }
        return !fds.empty();
    }

    bool poll(int timeout_ms)
    {
        struct kevent ev;
        struct timespec ts;
        int n;
        if (kq < 0) {
            return false;
        }
        ts.tv_sec = timeout_ms / 1000;
        ts.tv_nsec = (timeout_ms % 1000) * 1000000;
        n = kevent(kq, NULL, 0, &ev, 1, &ts);
        return n > 0;
    }
};

struct PreviewHost {
    const dui_api_v1* api;
    dui_context* ctx;
    dui_window* win;
    dui_action_api_v1* action_api;
    dui_native_api_v1* native_api;
    int width;
    int height;
    int use_null;

    UiPreviewLog log;
    UiPreviewActionRegistry actions;
    UiPreviewTargets targets;
    UiPreviewActionContext action_ctx;
    UiPreviewDoc doc;
    std::string ui_path;
    std::string registry_path;
};

static void preview_print_help(void)
{
    printf("Dominium UI Preview Host (macOS)\n");
    printf("Usage:\n");
    printf("  dominium-ui-preview-host-macos --ui <path/to/ui_doc.tlv> [--targets <list>] [--watch] [--log <path>]\n");
    printf("Options:\n");
    printf("  --ui <path>       Path to ui_doc.tlv (required)\n");
    printf("  --targets <list>  Comma-separated backend/tier list for validation\n");
    printf("  --watch           Enable hot reload on file changes\n");
    printf("  --log <path>      Write log output to file\n");
}

static int preview_starts_with(const std::string& s, const char* prefix)
{
    size_t n = prefix ? strlen(prefix) : 0u;
    if (!prefix || s.size() < n) {
        return 0;
    }
    return s.compare(0u, n, prefix) == 0;
}

static bool preview_parse_args(const std::vector<std::string>& args, PreviewOptions& out, std::string& err)
{
    err.clear();
    for (size_t i = 0u; i < args.size(); ++i) {
        const std::string& a = args[i];
        if (a == "--help" || a == "-h") {
            out.show_help = 1;
            return true;
        }
        if (a == "--watch") {
            out.watch = 1;
            continue;
        }
        if (a == "--ui" && (i + 1u) < args.size()) {
            out.ui_path = args[++i];
            continue;
        }
        if (a == "--targets" && (i + 1u) < args.size()) {
            out.targets = args[++i];
            continue;
        }
        if (a == "--log" && (i + 1u) < args.size()) {
            out.log_path = args[++i];
            continue;
        }
        if (preview_starts_with(a, "--ui=")) {
            out.ui_path = a.substr(5u);
            continue;
        }
        if (preview_starts_with(a, "--targets=")) {
            out.targets = a.substr(10u);
            continue;
        }
        if (preview_starts_with(a, "--log=")) {
            out.log_path = a.substr(6u);
            continue;
        }
        err = std::string("unknown_arg:") + a;
        return false;
    }
    return true;
}

static bool preview_load_registry(PreviewHost& host)
{
    std::string err;
    host.actions.clear();
    host.registry_path = ui_preview_guess_registry_path(host.ui_path);
    if (!host.registry_path.empty()) {
        if (!ui_preview_load_action_registry(host.registry_path, host.actions, err)) {
            host.log.line(std::string("registry: load failed (") + err + ")");
            return false;
        }
        host.log.line(std::string("registry: ") + host.registry_path);
        return true;
    }
    host.log.line("registry: not found (using fallback action ids)");
    return false;
}

static bool preview_rebuild(PreviewHost& host, int reload_doc)
{
    domui_diag diag;
    if (reload_doc) {
        if (!ui_preview_load_doc(host.ui_path.c_str(), host.doc, host.log, &diag)) {
            ui_preview_log_diag(host.log, diag);
            return false;
        }
        preview_load_registry(host);
    }
    if (!ui_preview_build_layout(host.doc, host.width, host.height, &diag)) {
        ui_preview_log_diag(host.log, diag);
    }
    if (!ui_preview_build_schema(host.doc, host.actions)) {
        host.log.line("preview: failed to build schema");
        return false;
    }
    (void)ui_preview_build_state(host.doc);
    if (host.win) {
        host.api->set_schema_tlv(host.win,
                                 host.doc.schema.empty() ? (const void*)0 : &host.doc.schema[0],
                                 (u32)host.doc.schema.size());
        host.api->set_state_tlv(host.win,
                                host.doc.state.empty() ? (const void*)0 : &host.doc.state[0],
                                (u32)host.doc.state.size());
        (void)host.api->render(host.win);
    }
    if (!ui_preview_validate_doc(host.doc, host.targets, &diag)) {
        ui_preview_log_diag(host.log, diag);
    } else if (diag.warning_count() > 0u) {
        ui_preview_log_diag(host.log, diag);
    }
    return true;
}

static bool preview_init_backend(PreviewHost& host)
{
    dui_window_desc_v1 desc;
    host.api = (const dui_api_v1*)dom_dui_macos_get_api(DUI_API_ABI_VERSION);
    host.use_null = 0;
    if (!host.api) {
        host.log.line("backend: macos api unavailable");
        return false;
    }
    if (host.api->create_context(&host.ctx) != DUI_OK) {
        host.log.line("backend: create_context failed");
        return false;
    }
    host.action_api = 0;
    host.native_api = 0;
    if (host.api->query_interface) {
        host.api->query_interface(DUI_IID_ACTION_API_V1, (void**)&host.action_api);
        host.api->query_interface(DUI_IID_NATIVE_API_V1, (void**)&host.native_api);
    }
    memset(&desc, 0, sizeof(desc));
    desc.abi_version = DUI_API_ABI_VERSION;
    desc.struct_size = (u32)sizeof(desc);
    desc.title = "Dominium UI Preview Host (macOS)";
    desc.width = 1024;
    desc.height = 720;
    if (host.api->create_window(host.ctx, &desc, &host.win) != DUI_OK) {
        host.log.line("backend: macos create_window failed");
        host.api->destroy_context(host.ctx);
        host.ctx = 0;
        host.api = (const dui_api_v1*)dom_dui_null_get_api(DUI_API_ABI_VERSION);
        if (!host.api || host.api->create_context(&host.ctx) != DUI_OK) {
            host.log.line("backend: null create_context failed");
            return false;
        }
        memset(&desc, 0, sizeof(desc));
        desc.abi_version = DUI_API_ABI_VERSION;
        desc.struct_size = (u32)sizeof(desc);
        desc.title = "Dominium UI Preview Host (null)";
        desc.width = 1024;
        desc.height = 720;
        if (host.api->create_window(host.ctx, &desc, &host.win) != DUI_OK) {
            host.log.line("backend: null create_window failed");
            return false;
        }
        host.use_null = 1;
        host.native_api = 0;
        host.action_api = 0;
    }
    host.width = desc.width;
    host.height = desc.height;
    host.action_ctx.log = &host.log;
    host.action_ctx.registry = &host.actions;
    if (host.action_api) {
        host.action_api->set_action_dispatch(host.ctx, ui_preview_action_dispatch, &host.action_ctx);
    }
    return true;
}

static void preview_shutdown(PreviewHost& host)
{
    if (host.api && host.win) {
        host.api->destroy_window(host.win);
        host.win = 0;
    }
    if (host.api && host.ctx) {
        host.api->destroy_context(host.ctx);
        host.ctx = 0;
    }
}

int main(int argc, char** argv)
{
    PreviewOptions opts;
    PreviewHost host;
    MacWatcher watcher;
    std::vector<std::string> args;
    std::vector<std::string> watch_dirs;
    std::string err;
    int running = 1;

    for (int i = 1; i < argc; ++i) {
        args.push_back(std::string(argv[i]));
    }
    if (!preview_parse_args(args, opts, err)) {
        printf("error: %s\n", err.c_str());
        preview_print_help();
        return 1;
    }
    if (opts.show_help) {
        preview_print_help();
        return 0;
    }
    if (opts.ui_path.empty()) {
        preview_print_help();
        return 1;
    }

    if (!opts.log_path.empty()) {
        host.log.open_file(opts.log_path);
    }
    host.log.line("preview: starting");
    host.ui_path = opts.ui_path;

    if (!ui_preview_parse_targets(opts.targets.c_str(), host.targets, err)) {
        host.log.line(std::string("targets: parse failed (") + err + ")");
    }

    if (!preview_init_backend(host)) {
        host.log.line("preview: backend init failed");
        preview_shutdown(host);
        return 1;
    }

    preview_load_registry(host);
    if (!preview_rebuild(host, 1)) {
        host.log.line("preview: initial load failed");
    }

    if (opts.watch) {
        ui_preview_collect_watch_dirs(host.ui_path, host.registry_path, watch_dirs);
        watcher.init(watch_dirs);
    }

    while (running) {
        host.api->pump(host.ctx);
        {
            dui_event_v1 ev;
            while (host.api->poll_event(host.ctx, &ev) > 0) {
                if (ev.type == (u32)DUI_EVENT_QUIT) {
                    running = 0;
                }
            }
        }
        if (opts.watch && watcher.poll(0)) {
            host.log.line("preview: change detected, reloading");
            preview_rebuild(host, 1);
        }
        usleep(16000);
    }

    watcher.clear();
    preview_shutdown(host);
    host.log.line("preview: shutdown");
    return 0;
}

#endif
