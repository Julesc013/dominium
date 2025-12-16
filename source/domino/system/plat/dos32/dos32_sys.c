/*
FILE: source/domino/system/plat/dos32/dos32_sys.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/dos32/dos32_sys
RESPONSIBILITY: Implements `dos32_sys`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dos32_sys.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <dirent.h>

#if defined(__DJGPP__)
#include <dpmi.h>
#include <go32.h>
#include <sys/movedata.h>
#include <sys/nearptr.h>
#include <sys/segments.h>
#include <sys/time.h>
#include <pc.h>
#endif

#if defined(_WIN32) || defined(__DJGPP__)
#include <conio.h>
#endif

#define DOS32_EVENT_QUEUE_CAP 32
#define DOS32_FALLBACK_W 640
#define DOS32_FALLBACK_H 480
#define DOS32_FALLBACK_BPP 8

dos32_global_t g_dos32;

/*----------------------------------------------------------------------
 * Helpers
 *----------------------------------------------------------------------*/
#if defined(__DJGPP__)
#pragma pack(push, 1)
typedef struct vbe_info_block_t {
    char     signature[4];
    uint16_t version;
    uint32_t oem_string_ptr;
    uint32_t capabilities;
    uint32_t video_mode_ptr;
    uint16_t total_memory;
    uint16_t oem_software_rev;
    uint32_t oem_vendor_name_ptr;
    uint32_t oem_product_name_ptr;
    uint32_t oem_product_rev_ptr;
    uint8_t  reserved[222];
    uint8_t  oem_data[256];
} vbe_info_block_t;

typedef struct vbe_mode_info_t {
    uint16_t attributes;
    uint8_t  winA;
    uint8_t  winB;
    uint16_t granularity;
    uint16_t winsize;
    uint16_t segmentA;
    uint16_t segmentB;
    uint32_t winFuncPtr;
    uint16_t pitch;
    uint16_t xres;
    uint16_t yres;
    uint8_t  wChar;
    uint8_t  yChar;
    uint8_t  planes;
    uint8_t  bpp;
    uint8_t  banks;
    uint8_t  memoryModel;
    uint8_t  bankSize;
    uint8_t  imagePages;
    uint8_t  reserved0;

    uint8_t  redMaskSize;
    uint8_t  redMaskPos;
    uint8_t  greenMaskSize;
    uint8_t  greenMaskPos;
    uint8_t  blueMaskSize;
    uint8_t  blueMaskPos;
    uint8_t  rsvMaskSize;
    uint8_t  rsvMaskPos;
    uint8_t  directColorModeInfo;

    uint32_t physbase;
    uint32_t offscreen;
    uint16_t offscreen_size;

    uint16_t linBytesPerScanLine;
    uint8_t  bankedNumImages;
    uint8_t  linNumImages;
    uint8_t  linRedMaskSize;
    uint8_t  linRedMaskPos;
    uint8_t  linGreenMaskSize;
    uint8_t  linGreenMaskPos;
    uint8_t  linBlueMaskSize;
    uint8_t  linBlueMaskPos;
    uint8_t  linRsvMaskSize;
    uint8_t  linRsvMaskPos;
    uint32_t maxPixelClock;
    uint8_t  reserved1[190];
} vbe_mode_info_t;
#pragma pack(pop)
#endif /* __DJGPP__ */

static const dsys_caps g_dos32_caps = { "dos32", 1u, true, true, false, false };

static void dos32_reset_state(void)
{
    memset(&g_dos32, 0, sizeof(g_dos32));
}

static void dos32_push_event(const dsys_event* ev)
{
    int next;

    if (!ev) {
        return;
    }
    next = (g_dos32.ev_tail + 1) % DOS32_EVENT_QUEUE_CAP;
    if (next == g_dos32.ev_head) {
        return;
    }
    g_dos32.event_queue[g_dos32.ev_tail] = *ev;
    g_dos32.ev_tail = next;
}

static bool dos32_pop_event(dsys_event* ev)
{
    if (g_dos32.ev_head == g_dos32.ev_tail) {
        return false;
    }
    if (ev) {
        *ev = g_dos32.event_queue[g_dos32.ev_head];
    }
    g_dos32.ev_head = (g_dos32.ev_head + 1) % DOS32_EVENT_QUEUE_CAP;
    return true;
}

static uint32_t dos32_calc_pitch(uint32_t width, uint32_t bpp)
{
    uint32_t pitch;
    pitch = width * (bpp / 8u);
    return pitch;
}

static void dos32_set_defaults(void)
{
    g_dos32.fb_width = DOS32_FALLBACK_W;
    g_dos32.fb_height = DOS32_FALLBACK_H;
    g_dos32.fb_bpp = DOS32_FALLBACK_BPP;
    g_dos32.pitch = dos32_calc_pitch((uint32_t)g_dos32.fb_width, (uint32_t)g_dos32.fb_bpp);
    g_dos32.lfb_size = g_dos32.pitch * (uint32_t)g_dos32.fb_height;
}

#if defined(__DJGPP__)
static int dos32_set_text_mode(void)
{
    __dpmi_regs regs;
    memset(&regs, 0, sizeof(regs));
    regs.h.ah = 0x00;
    regs.h.al = 0x03;
    return __dpmi_int(0x10, &regs);
}

static int dos32_try_set_vesa_mode(uint16_t mode, vbe_mode_info_t* out_info)
{
    __dpmi_regs regs;
    unsigned int   rm_seg;
    int           sel;
    int           ok;

    if (!out_info) {
        return 0;
    }

    rm_seg = 0;
    sel = __dpmi_allocate_dos_memory((sizeof(vbe_mode_info_t) + 15) / 16, (int*)&rm_seg);
    if (sel < 0) {
        return 0;
    }

    memset(&regs, 0, sizeof(regs));
    regs.x.ax = 0x4F01;
    regs.x.cx = mode;
    regs.x.es = rm_seg;
    regs.x.di = 0;
    ok = (__dpmi_int(0x10, &regs) == 0 && regs.h.ah == 0x00);
    if (ok) {
        dosmemget(rm_seg << 4, sizeof(vbe_mode_info_t), out_info);
    }

    __dpmi_free_dos_memory(sel);
    if (!ok) {
        return 0;
    }

    memset(&regs, 0, sizeof(regs));
    regs.x.ax = 0x4F02;
    regs.x.bx = mode | 0x4000; /* request linear framebuffer */
    if (__dpmi_int(0x10, &regs) != 0 || regs.h.ah != 0x00) {
        return 0;
    }
    return 1;
}

static int dos32_map_lfb(uint32_t phys, uint32_t size, void** out)
{
    __dpmi_meminfo mi;

    if (!out) {
        return 0;
    }

    mi.address = phys;
    mi.size = size;
    if (__dpmi_physical_address_mapping(&mi) != 0) {
        return 0;
    }
    *out = (void*)mi.address;
    return 1;
}
#endif /* __DJGPP__ */

static void dos32_setup_video(void)
{
#if defined(__DJGPP__)
    vbe_mode_info_t info;
    if (dos32_try_set_vesa_mode(0x101u, &info)) {
        g_dos32.fb_width = (int32_t)info.xres;
        g_dos32.fb_height = (int32_t)info.yres;
        g_dos32.fb_bpp = (int32_t)info.bpp;
        g_dos32.pitch = info.linBytesPerScanLine ? (uint32_t)info.linBytesPerScanLine
                                                 : dos32_calc_pitch((uint32_t)info.xres, (uint32_t)info.bpp);
        g_dos32.lfb_size = g_dos32.pitch * (uint32_t)g_dos32.fb_height;
        g_dos32.vesa_mode = 0x101u;
        if (!dos32_map_lfb(info.physbase, g_dos32.lfb_size, &g_dos32.lfb)) {
            dos32_set_defaults();
        }
    } else {
        /* fallback: mode 13h */
        __dpmi_regs regs;
        memset(&regs, 0, sizeof(regs));
        regs.h.ah = 0x00;
        regs.h.al = 0x13;
        __dpmi_int(0x10, &regs);
        g_dos32.fb_width = 320;
        g_dos32.fb_height = 200;
        g_dos32.fb_bpp = 8;
        g_dos32.pitch = dos32_calc_pitch(320u, 8u);
        g_dos32.lfb_size = g_dos32.pitch * (uint32_t)g_dos32.fb_height;
        if (!dos32_map_lfb(0xA0000UL, g_dos32.lfb_size, &g_dos32.lfb)) {
            dos32_set_defaults();
        }
    }
#else
    /* hosted fallback: allocate a dummy linear framebuffer */
    dos32_set_defaults();
    g_dos32.lfb = malloc(g_dos32.lfb_size);
    if (g_dos32.lfb) {
        memset(g_dos32.lfb, 0, g_dos32.lfb_size);
    }
#endif
}

static void dos32_teardown_video(void)
{
#if defined(__DJGPP__)
    dos32_set_text_mode();
#else
    if (g_dos32.lfb) {
        free(g_dos32.lfb);
    }
#endif
    g_dos32.lfb = NULL;
}

static int dos32_kbhit_nonblock(void)
{
#if defined(__DJGPP__) || defined(_WIN32)
    return kbhit();
#else
    return 0;
#endif
}

static int dos32_getch_nonblock(void)
{
#if defined(__DJGPP__) || defined(_WIN32)
    return getch();
#else
    return -1;
#endif
}

static void dos32_poll_keyboard(void)
{
    while (1) {
        int ch;
        dsys_event ev;

        if (!dos32_kbhit_nonblock()) {
            break;
        }
        ch = dos32_getch_nonblock();
        if (ch < 0) {
            break;
        }
        memset(&ev, 0, sizeof(ev));
        ev.type = DSYS_EVENT_KEY_DOWN;
        ev.payload.key.key = (int32_t)ch;
        ev.payload.key.repeat = false;
        dos32_push_event(&ev);

        memset(&ev, 0, sizeof(ev));
        if (ch == 27) {
            ev.type = DSYS_EVENT_QUIT;
        } else {
            ev.type = DSYS_EVENT_KEY_UP;
            ev.payload.key.key = (int32_t)ch;
            ev.payload.key.repeat = false;
        }
        dos32_push_event(&ev);
    }
}

static void dos32_poll_mouse(void)
{
#if defined(__DJGPP__)
    __dpmi_regs regs;
    int         buttons;
    int         x;
    int         y;
    int         changed_buttons;

    memset(&regs, 0, sizeof(regs));
    regs.x.ax = 0x0003;
    if (__dpmi_int(0x33, &regs) != 0) {
        return;
    }
    buttons = (int)regs.x.bx;
    x = (int)regs.x.cx;
    y = (int)regs.x.dx;

    if (x != g_dos32.mouse_x || y != g_dos32.mouse_y) {
        dsys_event ev;
        memset(&ev, 0, sizeof(ev));
        ev.type = DSYS_EVENT_MOUSE_MOVE;
        ev.payload.mouse_move.x = x;
        ev.payload.mouse_move.y = y;
        ev.payload.mouse_move.dx = x - g_dos32.mouse_x;
        ev.payload.mouse_move.dy = y - g_dos32.mouse_y;
        dos32_push_event(&ev);
        g_dos32.mouse_x = x;
        g_dos32.mouse_y = y;
    }

    changed_buttons = buttons ^ g_dos32.mouse_buttons;
    if (changed_buttons != 0) {
        int i;
        for (i = 0; i < 3; ++i) {
            int mask;
            mask = 1 << i;
            if (changed_buttons & mask) {
                dsys_event ev;
                memset(&ev, 0, sizeof(ev));
                ev.type = DSYS_EVENT_MOUSE_BUTTON;
                ev.payload.mouse_button.button = i + 1;
                ev.payload.mouse_button.pressed = (buttons & mask) ? true : false;
                ev.payload.mouse_button.clicks = 1;
                dos32_push_event(&ev);
            }
        }
        g_dos32.mouse_buttons = buttons;
    }
#else
    /* mouse unsupported on hosted fallback */
#endif
}

static uint64_t dos32_time_now_us_internal(void)
{
#if defined(__DJGPP__)
    return (uclock() * 1000000ULL) / (uint64_t)UCLOCKS_PER_SEC;
#else
    clock_t c;
    if (CLOCKS_PER_SEC == 0) {
        return 0u;
    }
    c = clock();
    return ((uint64_t)c * 1000000ULL) / (uint64_t)CLOCKS_PER_SEC;
#endif
}

/*----------------------------------------------------------------------
 * Backend vtable
 *----------------------------------------------------------------------*/
static dsys_result dos32_init(void);
static void        dos32_shutdown(void);
static dsys_caps   dos32_get_caps(void);

static uint64_t dos32_time_now_us(void);
static void     dos32_sleep_ms(uint32_t ms);

static dsys_window* dos32_window_create(const dsys_window_desc* desc);
static void         dos32_window_destroy(dsys_window* win);
static void         dos32_window_set_mode(dsys_window* win, dsys_window_mode mode);
static void         dos32_window_set_size(dsys_window* win, int32_t w, int32_t h);
static void         dos32_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
static void*        dos32_window_get_native_handle(dsys_window* win);

static bool dos32_poll_event(dsys_event* ev);

static bool   dos32_get_path(dsys_path_kind kind, char* buf, size_t buf_size);
static void*  dos32_file_open(const char* path, const char* mode);
static size_t dos32_file_read(void* fh, void* buf, size_t size);
static size_t dos32_file_write(void* fh, const void* buf, size_t size);
static int    dos32_file_seek(void* fh, long offset, int origin);
static long   dos32_file_tell(void* fh);
static int    dos32_file_close(void* fh);

static dsys_dir_iter* dos32_dir_open(const char* path);
static bool           dos32_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
static void           dos32_dir_close(dsys_dir_iter* it);

static dsys_process* dos32_process_spawn(const dsys_process_desc* desc);
static int           dos32_process_wait(dsys_process* p);
static void          dos32_process_destroy(dsys_process* p);

static const dsys_backend_vtable g_dos32_vtable = {
    dos32_init,
    dos32_shutdown,
    dos32_get_caps,
    dos32_time_now_us,
    dos32_sleep_ms,
    dos32_window_create,
    dos32_window_destroy,
    dos32_window_set_mode,
    dos32_window_set_size,
    dos32_window_get_size,
    dos32_window_get_native_handle,
    dos32_poll_event,
    dos32_get_path,
    dos32_file_open,
    dos32_file_read,
    dos32_file_write,
    dos32_file_seek,
    dos32_file_tell,
    dos32_file_close,
    dos32_dir_open,
    dos32_dir_next,
    dos32_dir_close,
    dos32_process_spawn,
    dos32_process_wait,
    dos32_process_destroy
};

static dsys_result dos32_init(void)
{
    if (g_dos32.initialized) {
        return DSYS_OK;
    }

    dos32_reset_state();
    dos32_set_defaults();
    dos32_setup_video();
    g_dos32.ev_head = 0;
    g_dos32.ev_tail = 0;
    g_dos32.initialized = 1;
    return DSYS_OK;
}

static void dos32_shutdown(void)
{
    if (!g_dos32.initialized) {
        return;
    }
    if (g_dos32.main_window) {
        free(g_dos32.main_window);
        g_dos32.main_window = NULL;
    }
    dos32_teardown_video();
    g_dos32.main_window = NULL;
    dos32_reset_state();
}

static dsys_caps dos32_get_caps(void)
{
    return g_dos32_caps;
}

static uint64_t dos32_time_now_us(void)
{
    return dos32_time_now_us_internal();
}

static void dos32_sleep_ms(uint32_t ms)
{
    uint64_t start;
    uint64_t target;

    start = dos32_time_now_us_internal();
    target = start + ((uint64_t)ms * 1000ULL);
    while (dos32_time_now_us_internal() < target) {
        /* busy wait to remain single-threaded/deterministic */
    }
}

static dsys_window* dos32_window_create(const dsys_window_desc* desc)
{
    dsys_window* win;

    if (g_dos32.main_window) {
        return g_dos32.main_window;
    }

    win = (dsys_window*)malloc(sizeof(dsys_window));
    if (!win) {
        return NULL;
    }
    memset(win, 0, sizeof(*win));

    win->framebuffer = g_dos32.lfb;
    win->width = g_dos32.fb_width;
    win->height = g_dos32.fb_height;
    win->pitch = (int32_t)g_dos32.pitch;
    win->bpp = g_dos32.fb_bpp;
    win->mode = DWIN_MODE_FULLSCREEN;
    if (desc && desc->mode == DWIN_MODE_WINDOWED) {
        win->mode = desc->mode;
    }

    g_dos32.main_window = win;
    return win;
}

static void dos32_window_destroy(dsys_window* win)
{
    if (!win) {
        return;
    }
    if (win == g_dos32.main_window) {
        g_dos32.main_window = NULL;
    }
    free(win);
}

static void dos32_window_set_mode(dsys_window* win, dsys_window_mode mode)
{
    if (!win) {
        return;
    }
    win->mode = mode;
}

static void dos32_window_set_size(dsys_window* win, int32_t w, int32_t h)
{
    (void)win;
    (void)w;
    (void)h;
}

static void dos32_window_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    if (!win) {
        return;
    }
    if (w) {
        *w = win->width;
    }
    if (h) {
        *h = win->height;
    }
}

static void* dos32_window_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return (void*)win->framebuffer;
}

static bool dos32_poll_event(dsys_event* ev)
{
    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    dos32_poll_keyboard();
    dos32_poll_mouse();

    if (dos32_pop_event(ev)) {
        return true;
    }
    return false;
}

static bool dos32_get_path(dsys_path_kind kind, char* buf, size_t buf_size)
{
    const char* p;

    if (!buf || buf_size == 0u) {
        return false;
    }

    p = ".";
    switch (kind) {
    case DSYS_PATH_APP_ROOT:    p = "."; break;
    case DSYS_PATH_USER_DATA:   p = "."; break;
    case DSYS_PATH_USER_CONFIG: p = "."; break;
    case DSYS_PATH_USER_CACHE:  p = "."; break;
    case DSYS_PATH_TEMP:        p = "."; break;
    default: break;
    }

    strncpy(buf, p, buf_size);
    buf[buf_size - 1u] = '\0';
    return true;
}

static void* dos32_file_open(const char* path, const char* mode)
{
    return (void*)fopen(path, mode);
}

static size_t dos32_file_read(void* fh, void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fread(buf, 1u, size, fp);
}

static size_t dos32_file_write(void* fh, const void* buf, size_t size)
{
    FILE* fp;
    if (!fh || !buf || size == 0u) {
        return 0u;
    }
    fp = (FILE*)fh;
    return fwrite(buf, 1u, size, fp);
}

static int dos32_file_seek(void* fh, long offset, int origin)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fseek(fp, offset, origin);
}

static long dos32_file_tell(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1L;
    }
    fp = (FILE*)fh;
    return ftell(fp);
}

static int dos32_file_close(void* fh)
{
    FILE* fp;
    if (!fh) {
        return -1;
    }
    fp = (FILE*)fh;
    return fclose(fp);
}

static dsys_dir_iter* dos32_dir_open(const char* path)
{
    dsys_dir_iter* it;

    if (!path) {
        return NULL;
    }

    it = (dsys_dir_iter*)malloc(sizeof(dsys_dir_iter));
    if (!it) {
        return NULL;
    }
    memset(it, 0, sizeof(*it));
    it->dir = opendir(path);
    if (!it->dir) {
        free(it);
        return NULL;
    }
    return it;
}

static bool dos32_dir_next(dsys_dir_iter* it, dsys_dir_entry* out)
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
        if (ent->d_name[0] == '.' &&
            (ent->d_name[1] == '\0' ||
             (ent->d_name[1] == '.' && ent->d_name[2] == '\0'))) {
            continue;
        }
        strncpy(out->name, ent->d_name, sizeof(out->name) - 1u);
        out->name[sizeof(out->name) - 1u] = '\0';
        out->is_dir = false;
        return true;
    }
}

static void dos32_dir_close(dsys_dir_iter* it)
{
    if (!it) {
        return;
    }
    if (it->dir) {
        closedir(it->dir);
    }
    free(it);
}

static dsys_process* dos32_process_spawn(const dsys_process_desc* desc)
{
    (void)desc;
    return NULL;
}

static int dos32_process_wait(dsys_process* p)
{
    (void)p;
    return -1;
}

static void dos32_process_destroy(dsys_process* p)
{
    (void)p;
}

const dsys_backend_vtable* dsys_dos32_get_vtable(void)
{
    return &g_dos32_vtable;
}
