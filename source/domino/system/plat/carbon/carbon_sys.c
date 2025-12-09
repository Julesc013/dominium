#include "carbon_sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

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

static void carbon_push_event(const dsys_event* ev);
static bool carbon_copy_path(const char* src, char* buf, size_t buf_size);
static void carbon_join_path(char* dst, size_t cap, const char* base, const char* leaf);
static bool carbon_fsref_to_path(const FSRef* ref, char* buf, size_t buf_size);
static bool carbon_cfurl_to_path(CFURLRef url, char* buf, size_t buf_size);
static bool carbon_get_folder(OSType type, char* buf, size_t buf_size, const char* leaf);

static pascal OSStatus carbon_app_event_handler(EventHandlerCallRef next,
                                                EventRef event,
                                                void* user_data);
static pascal OSStatus carbon_window_event_handler(EventHandlerCallRef next,
                                                   EventRef event,
                                                   void* user_data);

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
    next = (g_carbon.event_tail + 1) % 64;
    if (next == g_carbon.event_head) {
        return;
    }
    g_carbon.event_queue[g_carbon.event_tail] = *ev;
    g_carbon.event_tail = next;
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

static pascal OSStatus carbon_app_event_handler(EventHandlerCallRef next,
                                                EventRef event,
                                                void* user_data)
{
    UInt32 cls;
    UInt32 kind;
    dsys_event ev;
    HICommand cmd;

    (void)next;
    (void)user_data;

    cls = GetEventClass(event);
    kind = GetEventKind(event);

    memset(&ev, 0, sizeof(ev));

    if (cls == kEventClassApplication && kind == kEventAppQuit) {
        ev.type = DSYS_EVENT_QUIT;
        carbon_push_event(&ev);
        return noErr;
    }

    if (cls == kEventClassCommand && kind == kEventCommandProcess) {
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
                return noErr;
            }
        }
    }

    return eventNotHandledErr;
}

static pascal OSStatus carbon_window_event_handler(EventHandlerCallRef next,
                                                   EventRef event,
                                                   void* user_data)
{
    UInt32 cls;
    UInt32 kind;
    dsys_window* win;
    dsys_event ev;

    (void)next;
    win = (dsys_window*)user_data;

    cls = GetEventClass(event);
    kind = GetEventKind(event);

    memset(&ev, 0, sizeof(ev));

    if (cls == kEventClassWindow) {
        if (kind == kEventWindowClose) {
            ev.type = DSYS_EVENT_QUIT;
            carbon_push_event(&ev);
            return noErr;
        } else if (kind == kEventWindowBoundsChanged && win) {
            Rect bounds;
            short w;
            short h;
            GetWindowBounds(win->window_ref, kWindowContentRgn, &bounds);
            w = (short)(bounds.right - bounds.left);
            h = (short)(bounds.bottom - bounds.top);
            win->width = (int32_t)w;
            win->height = (int32_t)h;
            ev.type = DSYS_EVENT_WINDOW_RESIZED;
            ev.payload.window.width = win->width;
            ev.payload.window.height = win->height;
            carbon_push_event(&ev);
            return noErr;
        }
    } else if (cls == kEventClassMouse && win) {
        if (kind == kEventMouseMoved || kind == kEventMouseDragged) {
            HIPoint pt;
            if (GetEventParameter(event,
                                  kEventParamWindowMouseLocation,
                                  typeHIPoint,
                                  NULL,
                                  sizeof(pt),
                                  NULL,
                                  &pt) == noErr) {
                ev.type = DSYS_EVENT_MOUSE_MOVE;
                ev.payload.mouse_move.x = (int32_t)pt.x;
                ev.payload.mouse_move.y = (int32_t)pt.y;
                ev.payload.mouse_move.dx = ev.payload.mouse_move.x - win->last_x;
                ev.payload.mouse_move.dy = ev.payload.mouse_move.y - win->last_y;
                win->last_x = ev.payload.mouse_move.x;
                win->last_y = ev.payload.mouse_move.y;
                carbon_push_event(&ev);
                return noErr;
            }
        } else if (kind == kEventMouseDown || kind == kEventMouseUp) {
            UInt32 button;
            if (GetEventParameter(event,
                                  kEventParamMouseButton,
                                  typeMouseButton,
                                  NULL,
                                  sizeof(button),
                                  NULL,
                                  &button) == noErr) {
                ev.type = DSYS_EVENT_MOUSE_BUTTON;
                ev.payload.mouse_button.button = (int32_t)button;
                ev.payload.mouse_button.pressed = (kind == kEventMouseDown) ? true : false;
                ev.payload.mouse_button.clicks = 1;
                carbon_push_event(&ev);
                return noErr;
            }
        } else if (kind == kEventMouseWheelMoved) {
            SInt32 delta;
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
                return noErr;
            }
        }
    } else if (cls == kEventClassKeyboard) {
        UInt32 code;
        if (GetEventParameter(event,
                              kEventParamKeyCode,
                              typeUInt32,
                              NULL,
                              sizeof(code),
                              NULL,
                              &code) == noErr) {
            if (kind == kEventRawKeyDown) {
                ev.type = DSYS_EVENT_KEY_DOWN;
                ev.payload.key.key = (int32_t)code;
                ev.payload.key.repeat = false;
                carbon_push_event(&ev);
                return noErr;
            } else if (kind == kEventRawKeyRepeat) {
                ev.type = DSYS_EVENT_KEY_DOWN;
                ev.payload.key.key = (int32_t)code;
                ev.payload.key.repeat = true;
                carbon_push_event(&ev);
                return noErr;
            } else if (kind == kEventRawKeyUp) {
                ev.type = DSYS_EVENT_KEY_UP;
                ev.payload.key.key = (int32_t)code;
                ev.payload.key.repeat = false;
                carbon_push_event(&ev);
                return noErr;
            }
        }
    }

    return eventNotHandledErr;
}

static dsys_result carbon_init(void)
{
    EventTypeSpec app_events[2];

    memset(&g_carbon, 0, sizeof(g_carbon));
    g_carbon.initialized = 1;

    app_events[0].eventClass = kEventClassCommand;
    app_events[0].eventKind = kEventCommandProcess;
    app_events[1].eventClass = kEventClassApplication;
    app_events[1].eventKind = kEventAppQuit;

    g_carbon.app_event_upp = NewEventHandlerUPP(carbon_app_event_handler);
    g_carbon.win_event_upp = NewEventHandlerUPP(carbon_window_event_handler);

    if (g_carbon.app_event_upp) {
        InstallApplicationEventHandler(g_carbon.app_event_upp,
                                       2,
                                       app_events,
                                       NULL,
                                       &g_carbon.app_event_ref);
    }

    return DSYS_OK;
}

static void carbon_shutdown(void)
{
    if (g_carbon.main_window) {
        DisposeWindow(g_carbon.main_window);
        g_carbon.main_window = NULL;
    }

    if (g_carbon.win_event_ref) {
        RemoveEventHandler(g_carbon.win_event_ref);
        g_carbon.win_event_ref = NULL;
    }
    if (g_carbon.app_event_ref) {
        RemoveEventHandler(g_carbon.app_event_ref);
        g_carbon.app_event_ref = NULL;
    }
    if (g_carbon.win_event_upp) {
        DisposeEventHandlerUPP(g_carbon.win_event_upp);
        g_carbon.win_event_upp = NULL;
    }
    if (g_carbon.app_event_upp) {
        DisposeEventHandlerUPP(g_carbon.app_event_upp);
        g_carbon.app_event_upp = NULL;
    }

    g_carbon.initialized = 0;
    g_carbon.event_head = 0;
    g_carbon.event_tail = 0;
}

static dsys_caps carbon_get_caps(void)
{
    return g_carbon_caps;
}

static uint64_t carbon_time_now_us(void)
{
    UnsignedWide now;
    Nanoseconds  ns;
    uint64_t     value;

    now = UpTime();
    ns = AbsoluteToNanoseconds(now);
    value = ((uint64_t)ns.hi << 32) | (uint64_t)ns.lo;
    return value / 1000u;
}

static void carbon_sleep_ms(uint32_t ms)
{
    uint64_t start;
    uint64_t target;

    start = carbon_time_now_us();
    target = start + ((uint64_t)ms * 1000u);
    while (carbon_time_now_us() < target) {
        EventRef evref;
        if (ReceiveNextEvent(0, NULL, kEventDurationNoWait, true, &evref) == noErr) {
            SendEventToEventTarget(evref, GetEventDispatcherTarget());
            ReleaseEvent(evref);
        }
    }
}

static dsys_window* carbon_window_create(const dsys_window_desc* desc)
{
    dsys_window_desc local_desc;
    Rect             bounds;
    WindowRef        win_ref;
    OSStatus         err;
    dsys_window*     win;
    EventTypeSpec    win_events[10];
    CFStringRef      title;
    UInt32           event_count;

    if (desc) {
        local_desc = *desc;
    } else {
        local_desc.x = 0;
        local_desc.y = 0;
        local_desc.width = 800;
        local_desc.height = 600;
        local_desc.mode = DWIN_MODE_WINDOWED;
    }

    SetRect(&bounds,
            0,
            0,
            (short)((local_desc.width > 0) ? local_desc.width : 800),
            (short)((local_desc.height > 0) ? local_desc.height : 600));

    win_ref = NULL;
    err = CreateNewWindow(kDocumentWindowClass,
                          kWindowStandardDocumentAttributes | kWindowStandardHandlerAttribute,
                          &bounds,
                          &win_ref);
    if (err != noErr || !win_ref) {
        return NULL;
    }

    MoveWindow(win_ref, (short)local_desc.x, (short)local_desc.y, true);

    title = CFStringCreateWithCString(kCFAllocatorDefault, "Domino", kCFStringEncodingUTF8);
    if (title) {
        SetWindowTitleWithCFString(win_ref, title);
        CFRelease(title);
    }

    win_events[0].eventClass = kEventClassWindow;
    win_events[0].eventKind = kEventWindowClose;
    win_events[1].eventClass = kEventClassWindow;
    win_events[1].eventKind = kEventWindowBoundsChanged;
    win_events[2].eventClass = kEventClassMouse;
    win_events[2].eventKind = kEventMouseDown;
    win_events[3].eventClass = kEventClassMouse;
    win_events[3].eventKind = kEventMouseUp;
    win_events[4].eventClass = kEventClassMouse;
    win_events[4].eventKind = kEventMouseMoved;
    win_events[5].eventClass = kEventClassMouse;
    win_events[5].eventKind = kEventMouseDragged;
    win_events[6].eventClass = kEventClassMouse;
    win_events[6].eventKind = kEventMouseWheelMoved;
    win_events[7].eventClass = kEventClassKeyboard;
    win_events[7].eventKind = kEventRawKeyDown;
    win_events[8].eventClass = kEventClassKeyboard;
    win_events[8].eventKind = kEventRawKeyUp;
    win_events[9].eventClass = kEventClassKeyboard;
    win_events[9].eventKind = kEventRawKeyRepeat;
    event_count = (UInt32)(sizeof(win_events) / sizeof(win_events[0]));

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        DisposeWindow(win_ref);
        return NULL;
    }
    memset(win, 0, sizeof(*win));
    win->window_ref = win_ref;
    win->width = local_desc.width;
    win->height = local_desc.height;
    win->last_x = 0;
    win->last_y = 0;
    win->mode = local_desc.mode;

    if (g_carbon.win_event_upp) {
        EventHandlerRef ref;
        InstallWindowEventHandler(win_ref,
                                  g_carbon.win_event_upp,
                                  event_count,
                                  win_events,
                                  win,
                                  &ref);
        g_carbon.win_event_ref = ref;
    }

    ShowWindow(win_ref);
    g_carbon.main_window = win_ref;
    carbon_window_set_mode(win, local_desc.mode);
    carbon_window_get_size(win, NULL, NULL);
    return win;
}

static void carbon_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (g_carbon.win_event_ref) {
        RemoveEventHandler(g_carbon.win_event_ref);
        g_carbon.win_event_ref = NULL;
    }
    if (win->window_ref) {
        DisposeWindow(win->window_ref);
        if (g_carbon.main_window == win->window_ref) {
            g_carbon.main_window = NULL;
        }
    }
    free(win);
}

static void carbon_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    Rect bounds;
    CGrafPtr port;

    if (!win || !win->window_ref) {
        return;
    }

    port = GetWindowPort(win->window_ref);
    if (mode == DWIN_MODE_FULLSCREEN || mode == DWIN_MODE_BORDERLESS) {
        Rect screen;
        GetAvailableWindowPositioningBounds(GetMainDevice(), &screen);
        MoveWindow(win->window_ref, screen.left, screen.top, true);
        SizeWindow(win->window_ref,
                   (short)(screen.right - screen.left),
                   (short)(screen.bottom - screen.top),
                   true);
        win->width = (int32_t)(screen.right - screen.left);
        win->height = (int32_t)(screen.bottom - screen.top);
    } else {
        GetWindowBounds(win->window_ref, kWindowContentRgn, &bounds);
        win->width = (int32_t)(bounds.right - bounds.left);
        win->height = (int32_t)(bounds.bottom - bounds.top);
    }

    if (port) {
        Rect port_bounds;
        GetPortBounds(port, &port_bounds);
        win->width = (int32_t)(port_bounds.right - port_bounds.left);
        win->height = (int32_t)(port_bounds.bottom - port_bounds.top);
    }

    win->mode = mode;
}

static void carbon_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    if (!win || !win->window_ref) {
        return;
    }
    SizeWindow(win->window_ref, (short)w, (short)h, true);
    win->width = w;
    win->height = h;
}

static void carbon_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    Rect bounds;

    if (!win || !win->window_ref) {
        return;
    }

    GetWindowBounds(win->window_ref, kWindowContentRgn, &bounds);
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
    return (void*)win->window_ref;
}

static bool carbon_poll_event(dsys_event* out)
{
    EventRef evref;
    OSStatus err;

    if (out) {
        memset(out, 0, sizeof(*out));
    }

    err = ReceiveNextEvent(0, NULL, kEventDurationNoWait, true, &evref);
    if (err == noErr) {
        SendEventToEventTarget(evref, GetEventDispatcherTarget());
        ReleaseEvent(evref);
    }

    if (g_carbon.event_head != g_carbon.event_tail && out) {
        *out = g_carbon.event_queue[g_carbon.event_head];
        g_carbon.event_head = (g_carbon.event_head + 1) % 64;
        return true;
    }

    return false;
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
        if (!carbon_get_folder(kTemporaryFolderType, buf, buf_size, NULL)) {
            ok = carbon_copy_path("/tmp", buf, buf_size);
        } else {
            ok = true;
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
    DIR* dir;
    dsys_dir_iter* it;

    if (!path) {
        return NULL;
    }

    dir = opendir(path);
    if (!dir) {
        return NULL;
    }

    it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
    if (!it) {
        closedir(dir);
        return NULL;
    }

    it->dir = dir;
    {
        size_t len;
        len = strlen(path);
        if (len >= sizeof(it->base)) {
            len = sizeof(it->base) - 1u;
        }
        memcpy(it->base, path, len);
        it->base[len] = '\0';
    }
    return it;
}

static bool carbon_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
{
    struct dirent* ent;

    if (!it || !out) {
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
        strncpy(out->name, ent->d_name, sizeof(out->name) - 1u);
        out->name[sizeof(out->name) - 1u] = '\0';
        out->is_dir = false;
#if defined(DT_DIR)
        if (ent->d_type == DT_DIR) {
            out->is_dir = true;
        } else if (ent->d_type == DT_UNKNOWN) {
            struct stat st;
            char        full[260];
            size_t      base_len;
            size_t      name_len;
            base_len = strlen(it->base);
            name_len = strlen(out->name);
            if (base_len + name_len + 2u < sizeof(full)) {
                memcpy(full, it->base, base_len);
                if (base_len > 0u && full[base_len - 1u] != '/') {
                    full[base_len] = '/';
                    base_len += 1u;
                }
                memcpy(full + base_len, out->name, name_len);
                full[base_len + name_len] = '\0';
                if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) {
                    out->is_dir = true;
                }
            }
        }
#else
        {
            struct stat st;
            char        full[260];
            size_t      base_len;
            size_t      name_len;
            base_len = strlen(it->base);
            name_len = strlen(out->name);
            if (base_len + name_len + 2u < sizeof(full)) {
                memcpy(full, it->base, base_len);
                if (base_len > 0u && full[base_len - 1u] != '/') {
                    full[base_len] = '/';
                    base_len += 1u;
                }
                memcpy(full + base_len, out->name, name_len);
                full[base_len + name_len] = '\0';
                if (stat(full, &st) == 0 && S_ISDIR(st.st_mode)) {
                    out->is_dir = true;
                }
            }
        }
#endif
        return true;
    }
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
