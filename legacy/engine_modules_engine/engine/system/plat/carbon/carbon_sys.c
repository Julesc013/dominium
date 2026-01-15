/*
FILE: source/domino/system/plat/carbon/carbon_sys.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/carbon/carbon_sys
RESPONSIBILITY: Implements `carbon_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "carbon_sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#ifndef NULL
#define NULL ((void*)0)
#endif

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

static dsys_caps g_carbon_caps = { "carbon", 1u, true, true, false, true };
carbon_global_t  g_carbon;

static dsys_result carbon_init(void);
static void        carbon_shutdown(void);
static dsys_caps   carbon_get_caps(void);

static uint64_t carbon_time_now_us(void);
static void     carbon_sleep_ms(uint32_t ms);

static dsys_window* carbon_window_create(const dsys_window_desc* desc);
static void         carbon_window_destroy(dsys_window* win);
static void         carbon_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         carbon_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         carbon_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        carbon_window_get_native_handle(dsys_window* win);

static bool carbon_poll_event(dsys_event* ev);

static bool   carbon_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  carbon_file_open(const char* path, const char* mode);
static size_t carbon_file_read(void* fh, void* buf, size_t size);
static size_t carbon_file_write(void* fh, const void* buf, size_t size);
static int    carbon_file_seek(void* fh, long offset, int origin);
static long   carbon_file_tell(void* fh);
static int    carbon_file_close(void* fh);

static dsys_dir_iter* carbon_dir_open(const char* path);
static bool           carbon_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           carbon_dir_close(dsys_dir_iter* it);

static dsys_process* carbon_process_spawn(const dsys_process_desc* desc);
static int           carbon_process_wait(dsys_process* p);
static void          carbon_process_destroy(dsys_process* p);

static void     carbon_push_event(const dsys_event* ev);
static void     carbon_pump_events(void);
static void     carbon_translate_event(EventRef event);
static uint64_t carbon_now_raw_us(void);

static bool carbon_copy_path(const char* src, char* buf, size_t buf_size);
static void carbon_join_path(char* dst, size_t cap, const char* base, const char* leaf);
static bool carbon_fsref_to_path(const FSRef* ref, char* buf, size_t buf_size);
static bool carbon_cfurl_to_path(CFURLRef url, char* buf, size_t buf_size);
static bool carbon_get_folder(OSType type, char* buf, size_t buf_size, const char* leaf);

static const dsys_backend_vtable g_carbon_vtable = {
    carbon_init,
    carbon_shutdown,
    carbon_get_caps,
    carbon_time_now_us,
    carbon_sleep_ms,
    carbon_window_create,
    carbon_window_destroy,
    carbon_window_set_mode,
    carbon_window_set_size,
    carbon_window_get_size,
    carbon_window_get_native_handle,
    carbon_poll_event,
    carbon_get_path,
    carbon_file_open,
    carbon_file_read,
    carbon_file_write,
    carbon_file_seek,
    carbon_file_tell,
    carbon_file_close,
    carbon_dir_open,
    carbon_dir_next,
    carbon_dir_close,
    carbon_process_spawn,
    carbon_process_wait,
    carbon_process_destroy
};

static void carbon_push_event(const dsys_event* ev)
{
    int next;

    if (!ev) {
        return;
    }

    next = (g_carbon.q_tail + 1) % CARBON_EVENT_QUEUE_SIZE;
    if (next == g_carbon.q_head) {
        return;
    }

    g_carbon.queue[g_carbon.q_tail] = *ev;
    g_carbon.q_tail = next;
}

static dsys_result carbon_init(void)
{
    memset(&g_carbon, 0, sizeof(g_carbon));
    g_carbon.initialized = 1;
    g_carbon.q_head = 0;
    g_carbon.q_tail = 0;
    g_carbon.time_base_us = carbon_now_raw_us();
    g_carbon.last_mouse_x = 0;
    g_carbon.last_mouse_y = 0;
    g_carbon.mouse_pos_valid = 0;
    return DSYS_OK;
}

static void carbon_shutdown(void)
{
    if (g_carbon.main_window) {
        carbon_window_destroy(g_carbon.main_window);
    }
    memset(&g_carbon, 0, sizeof(g_carbon));
}

static dsys_caps carbon_get_caps(void)
{
    return g_carbon_caps;
}

static uint64_t carbon_now_raw_us(void)
{
    UnsignedWide now;
    Nanoseconds  ns;
    uint64_t     value;

    now = UpTime();
    ns = AbsoluteToNanoseconds(now);
    value = ((uint64_t)ns.hi << 32) | (uint64_t)ns.lo;
    return value / 1000u;
}

static uint64_t carbon_time_now_us(void)
{
    uint64_t now;
    now = carbon_now_raw_us();
    if (g_carbon.time_base_us != 0u) {
        return now - g_carbon.time_base_us;
    }
    return now;
}

static void carbon_sleep_ms(uint32_t ms)
{
    UInt32 ticks;
    ticks = (ms + 15u) / 16u;
    if (ticks == 0u) {
        ticks = 1u;
    }
    Delay((SInt32)ticks, NULL);
}

static dsys_window* carbon_window_create(const dsys_window_desc* desc)
{
    Rect         bounds;
    WindowRef    win_ref;
    OSStatus     err;
    dsys_window* win;
    CFStringRef  title;
    int32_t      width;
    int32_t      height;
    int32_t      x;
    int32_t      y;

    width = 800;
    height = 600;
    x = 100;
    y = 100;
    if (desc) {
        if (desc->width > 0) {
            width = desc->width;
        }
        if (desc->height > 0) {
            height = desc->height;
        }
        x = desc->x;
        y = desc->y;
    }

    SetRect(&bounds, (short)x, (short)y, (short)(x + width), (short)(y + height));

    win_ref = NULL;
    err = CreateNewWindow(kDocumentWindowClass,
                          kWindowStandardDocumentAttributes | kWindowStandardHandlerAttribute,
                          &bounds,
                          &win_ref);
    if (err != noErr || !win_ref) {
        return NULL;
    }

    MoveWindow(win_ref, (short)x, (short)y, true);

    title = CFStringCreateWithCString(kCFAllocatorDefault, "Domino", kCFStringEncodingUTF8);
    if (title) {
        SetWindowTitleWithCFString(win_ref, title);
        CFRelease(title);
    }

    ShowWindow(win_ref);
    ActivateWindow(win_ref);

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        DisposeWindow(win_ref);
        return NULL;
    }
    memset(win, 0, sizeof(*win));
    win->window = win_ref;
    win->width = width;
    win->height = height;
    win->mode = desc ? desc->mode : DWIN_MODE_WINDOWED;

    g_carbon.main_window = win;
    g_carbon.mouse_pos_valid = 0;

    carbon_window_get_size(win, NULL, NULL);
    carbon_window_set_mode(win, win->mode);
    return win;
}

static void carbon_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (win->window) {
        DisposeWindow(win->window);
    }
    if (g_carbon.main_window == win) {
        g_carbon.main_window = NULL;
    }
    free(win);
}

static void carbon_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    Rect screen;
    Rect bounds;

    if (!win || !win->window) {
        return;
    }

    if (mode == DWIN_MODE_FULLSCREEN || mode == DWIN_MODE_BORDERLESS) {
        GetAvailableWindowPositioningBounds(GetMainDevice(), &screen);
        SetWindowBounds(win->window, kWindowContentRgn, &screen);
        win->width = (int32_t)(screen.right - screen.left);
        win->height = (int32_t)(screen.bottom - screen.top);
    } else {
        GetWindowBounds(win->window, kWindowContentRgn, &bounds);
        win->width = (int32_t)(bounds.right - bounds.left);
        win->height = (int32_t)(bounds.bottom - bounds.top);
    }

    win->mode = mode;
}

static void carbon_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    Rect bounds;

    if (!win || !win->window) {
        return;
    }

    GetWindowBounds(win->window, kWindowContentRgn, &bounds);
    bounds.right = bounds.left + (short)w;
    bounds.bottom = bounds.top + (short)h;
    SetWindowBounds(win->window, kWindowContentRgn, &bounds);
    win->width = w;
    win->height = h;
}

static void carbon_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    Rect bounds;

    if (!win || !win->window) {
        return;
    }

    GetWindowBounds(win->window, kWindowContentRgn, &bounds);
    win->width = (int32_t)(bounds.right - bounds.left);
    win->height = (int32_t)(bounds.bottom - bounds.top);

    if (w) {
        *w = win->width;
    }
    if (h) {
        *h = win->height;
    }
}

static void* carbon_window_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return (void*)win->window;
}

static void carbon_pump_events(void)
{
    EventRef event;
    OSStatus err;

    event = NULL;
    for (;;) {
        err = ReceiveNextEvent(0, NULL, kEventDurationNoWait, true, &event);
        if (err == eventLoopTimedOutErr || err == eventNotHandledErr) {
            break;
        }
        if (err != noErr || !event) {
            break;
        }

        carbon_translate_event(event);
        SendEventToEventTarget(event, GetEventDispatcherTarget());
        ReleaseEvent(event);
        event = NULL;
    }
}

static void carbon_translate_event(EventRef event)
{
    UInt32     cls;
    UInt32     kind;
    dsys_event ev;

    cls = GetEventClass(event);
    kind = GetEventKind(event);

    memset(&ev, 0, sizeof(ev));

    if (cls == kEventClassKeyboard) {
        UInt32 code;
        code = 0;
        if (GetEventParameter(event,
                              kEventParamKeyCode,
                              typeUInt32,
                              NULL,
                              sizeof(code),
                              NULL,
                              &code) == noErr) {
            if (kind == kEventRawKeyDown || kind == kEventRawKeyRepeat) {
                ev.type = DSYS_EVENT_KEY_DOWN;
                ev.payload.key.key = (int32_t)code;
                ev.payload.key.repeat = (kind == kEventRawKeyRepeat) ? true : false;
                carbon_push_event(&ev);
                return;
            } else if (kind == kEventRawKeyUp) {
                ev.type = DSYS_EVENT_KEY_UP;
                ev.payload.key.key = (int32_t)code;
                ev.payload.key.repeat = false;
                carbon_push_event(&ev);
                return;
            }
        }
        return;
    }

    if (cls == kEventClassMouse) {
        if (kind == kEventMouseMoved || kind == kEventMouseDragged) {
            HIPoint pt;
            pt.x = 0.0f;
            pt.y = 0.0f;
            if (GetEventParameter(event,
                                  kEventParamWindowMouseLocation,
                                  typeHIPoint,
                                  NULL,
                                  sizeof(pt),
                                  NULL,
                                  &pt) == noErr) {
                int32_t x;
                int32_t y;
                x = (int32_t)pt.x;
                y = (int32_t)pt.y;
                ev.type = DSYS_EVENT_MOUSE_MOVE;
                ev.payload.mouse_move.x = x;
                ev.payload.mouse_move.y = y;
                if (g_carbon.mouse_pos_valid) {
                    ev.payload.mouse_move.dx = x - g_carbon.last_mouse_x;
                    ev.payload.mouse_move.dy = y - g_carbon.last_mouse_y;
                } else {
                    ev.payload.mouse_move.dx = 0;
                    ev.payload.mouse_move.dy = 0;
                }
                g_carbon.last_mouse_x = x;
                g_carbon.last_mouse_y = y;
                g_carbon.mouse_pos_valid = 1;
                carbon_push_event(&ev);
                return;
            }
        } else if (kind == kEventMouseDown || kind == kEventMouseUp) {
            UInt32 button;
            SInt32 clicks;
            button = 0u;
            clicks = 1;
            if (GetEventParameter(event,
                                  kEventParamMouseButton,
                                  typeMouseButton,
                                  NULL,
                                  sizeof(button),
                                  NULL,
                                  &button) == noErr) {
                GetEventParameter(event,
                                  kEventParamClickCount,
                                  typeSInt32,
                                  NULL,
                                  sizeof(clicks),
                                  NULL,
                                  &clicks);
                ev.type = DSYS_EVENT_MOUSE_BUTTON;
                ev.payload.mouse_button.button = (int32_t)button;
                ev.payload.mouse_button.pressed = (kind == kEventMouseDown) ? true : false;
                ev.payload.mouse_button.clicks = (int32_t)clicks;
                carbon_push_event(&ev);
                return;
            }
        } else if (kind == kEventMouseWheelMoved) {
            SInt32 delta;
            delta = 0;
            if (GetEventParameter(event,
                                  kEventParamMouseWheelDelta,
                                  typeSInt32,
                                  NULL,
                                  sizeof(delta),
                                  NULL,
                                  &delta) == noErr) {
                ev.type = DSYS_EVENT_MOUSE_WHEEL;
                ev.payload.mouse_wheel.delta_x = 0;
                ev.payload.mouse_wheel.delta_y = (int32_t)delta;
                carbon_push_event(&ev);
                return;
            }
        }
        return;
    }

    if (cls == kEventClassWindow) {
        WindowRef wref;
        wref = NULL;
        GetEventParameter(event,
                          kEventParamDirectObject,
                          typeWindowRef,
                          NULL,
                          sizeof(wref),
                          NULL,
                          &wref);

        if (kind == kEventWindowClose) {
            ev.type = DSYS_EVENT_QUIT;
            carbon_push_event(&ev);
            return;
        } else if (kind == kEventWindowBoundsChanged) {
            Rect    bounds;
            int32_t w;
            int32_t h;

            GetWindowBounds(wref, kWindowContentRgn, &bounds);
            w = (int32_t)(bounds.right - bounds.left);
            h = (int32_t)(bounds.bottom - bounds.top);

            if (g_carbon.main_window && g_carbon.main_window->window == wref) {
                g_carbon.main_window->width = w;
                g_carbon.main_window->height = h;
            }

            ev.type = DSYS_EVENT_WINDOW_RESIZED;
            ev.payload.window.width = w;
            ev.payload.window.height = h;
            carbon_push_event(&ev);
            return;
        }
        return;
    }

    if (cls == kEventClassApplication && kind == kEventAppQuit) {
        ev.type = DSYS_EVENT_QUIT;
        carbon_push_event(&ev);
        return;
    }

    if (cls == kEventClassCommand && kind == kEventCommandProcess) {
        HICommand cmd;
        memset(&cmd, 0, sizeof(cmd));
        if (GetEventParameter(event,
                              kEventParamDirectObject,
                              typeHICommand,
                              NULL,
                              sizeof(cmd),
                              NULL,
                              &cmd) == noErr) {
            if (cmd.commandID == kHICommandQuit) {
                ev.type = DSYS_EVENT_QUIT;
                carbon_push_event(&ev);
                return;
            }
        }
    }
}

static bool carbon_poll_event(dsys_event* out)
{
    carbon_pump_events();

    if (g_carbon.q_head != g_carbon.q_tail) {
        if (out) {
            *out = g_carbon.queue[g_carbon.q_head];
        }
        g_carbon.q_head = (g_carbon.q_head + 1) % CARBON_EVENT_QUEUE_SIZE;
        return true;
    }

    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return false;
}

static bool carbon_copy_path(const char* src, char* buf, size_t buf_size)
{
    size_t len;

    if (!src || !buf || buf_size == 0u) {
        return false;
    }

    len = strlen(src);
    if (len >= buf_size) {
        len = buf_size - 1u;
    }
    memcpy(buf, src, len);
    buf[len] = '\0';
    return true;
}

static void carbon_join_path(char* dst, size_t cap, const char* base, const char* leaf)
{
    size_t i;
    size_t j;

    if (!dst || cap == 0u) {
        return;
    }

    dst[0] = '\0';
    i = 0u;
    if (base) {
        while (base[i] != '\0' && i + 1u < cap) {
            dst[i] = base[i];
            ++i;
        }
        if (i > 0u && dst[i - 1u] != '/' && i + 1u < cap) {
            dst[i] = '/';
            ++i;
        }
    }

    j = 0u;
    if (leaf) {
        while (leaf[j] != '\0' && i + 1u < cap) {
            dst[i] = leaf[j];
            ++i;
            ++j;
        }
    }

    dst[i] = '\0';
}

static bool carbon_fsref_to_path(const FSRef* ref, char* buf, size_t buf_size)
{
    UInt8 path_buf[PATH_MAX];

    if (!ref || !buf || buf_size == 0u) {
        return false;
    }

    if (FSRefMakePath(ref, path_buf, sizeof(path_buf)) != noErr) {
        return false;
    }

    return carbon_copy_path((const char*)path_buf, buf, buf_size);
}

static bool carbon_cfurl_to_path(CFURLRef url, char* buf, size_t buf_size)
{
    CFStringRef cf_path;
    Boolean     ok;

    if (!url || !buf || buf_size == 0u) {
        return false;
    }

    cf_path = CFURLCopyFileSystemPath(url, kCFURLPOSIXPathStyle);
    if (!cf_path) {
        return false;
    }

    ok = CFStringGetCString(cf_path, buf, (CFIndex)buf_size, kCFStringEncodingUTF8);
    CFRelease(cf_path);
    return ok ? true : false;
}

static bool carbon_get_folder(OSType type, char* buf, size_t buf_size, const char* leaf)
{
    FSRef ref;
    char  base[PATH_MAX];
    char  joined[PATH_MAX];

    if (!buf || buf_size == 0u) {
        return false;
    }

    if (FSFindFolder(kUserDomain, type, true, &ref) != noErr) {
        return false;
    }
    if (!carbon_fsref_to_path(&ref, base, sizeof(base))) {
        return false;
    }

    if (leaf && leaf[0] != '\0') {
        carbon_join_path(joined, sizeof(joined), base, leaf);
        return carbon_copy_path(joined, buf, buf_size);
    }

    return carbon_copy_path(base, buf, buf_size);
}

static bool carbon_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    bool ok;

    if (!buf || buf_size == 0u) {
        return false;
    }

    buf[0] = '\0';
    ok = false;

    switch (kind) {
    case DSYS_PATH_APP_ROOT:
        {
            CFBundleRef bundle;
            bundle = CFBundleGetMainBundle();
            if (bundle) {
                CFURLRef url;
                url = CFBundleCopyBundleURL(bundle);
                if (url) {
                    ok = carbon_cfurl_to_path(url, buf, buf_size);
                    CFRelease(url);
                }
            }
            if (!ok) {
                char cwd[PATH_MAX];
                if (getcwd(cwd, sizeof(cwd)) != NULL) {
                    ok = carbon_copy_path(cwd, buf, buf_size);
                }
            }
        }
        break;

    case DSYS_PATH_USER_DATA:
        ok = carbon_get_folder(kApplicationSupportFolderType, buf, buf_size, "dominium");
        break;

    case DSYS_PATH_USER_CONFIG:
        ok = carbon_get_folder(kPreferencesFolderType, buf, buf_size, "dominium");
        break;

    case DSYS_PATH_USER_CACHE:
        ok = carbon_get_folder(kCachedDataFolderType, buf, buf_size, "dominium");
        break;

    case DSYS_PATH_TEMP:
        if (carbon_get_folder(kTemporaryFolderType, buf, buf_size, NULL)) {
            ok = true;
        } else {
            ok = carbon_copy_path("/tmp", buf, buf_size);
        }
        break;

    default:
        break;
    }

    if (!ok && buf_size > 0u) {
        buf[0] = '\0';
    }
    return ok;
}

static void* carbon_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t carbon_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t carbon_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int carbon_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long carbon_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int carbon_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* carbon_dir_open(const char* path)
{
    const char*   p;
    DIR*          dir;
    dsys_dir_iter* it;

    p = (path && path[0] != '\0') ? path : ".";
    dir = opendir(p);
    if (!dir) {
        return NULL;
    }

    it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
    if (!it) {
        closedir(dir);
        return NULL;
    }
    it->dir = dir;
    return it;
}

static bool carbon_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    struct dirent* ent;

    if (!it || !out || !it->dir) {
        return false;
    }

    for (;;) {
        ent = readdir(it->dir);
        if (!ent) {
            return false;
        }
        if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0) {
            continue;
        }
        break;
    }

    strncpy(out->name, ent->d_name, sizeof(out->name) - 1u);
    out->name[sizeof(out->name) - 1u] = '\0';
    out->is_dir = false;
#if defined(DT_DIR)
    if (ent->d_type == DT_DIR) {
        out->is_dir = true;
    }
#endif
    return true;
}

static void carbon_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    if (it->dir) {
        closedir(it->dir);
    }
    free(it);
}

static dsys_process* carbon_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int carbon_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void carbon_process_destroy(dsys_process* p)
{
    (void)p;
}

const dsys_backend_vtable* dsys_carbon_get_vtable(void)
{
    return &g_carbon_vtable;
}
