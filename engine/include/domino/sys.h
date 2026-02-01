/*
FILE: include/domino/sys.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / sys
RESPONSIBILITY: Defines the public contract for `sys` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_SYS_H_INCLUDED
#define DOMINO_SYS_H_INCLUDED

/* Domino System / Platform API - C89 friendly */

#include <stddef.h>
#include "domino/abi.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Core types
 *------------------------------------------------------------*/

typedef struct domino_sys_context domino_sys_context;

/* domino_sys_profile: Public type used by `sys`. */
typedef enum {
    DOMINO_SYS_PROFILE_AUTO = 0,
    DOMINO_SYS_PROFILE_TINY,
    DOMINO_SYS_PROFILE_REDUCED,
    DOMINO_SYS_PROFILE_FULL
} domino_sys_profile;

/* domino_os_kind: Public type used by `sys`. */
typedef enum {
    DOMINO_OS_DOS,
    DOMINO_OS_WINDOWS,
    DOMINO_OS_MAC,
    DOMINO_OS_UNIX,
    DOMINO_OS_ANDROID,
    DOMINO_OS_CPM,
    DOMINO_OS_UNKNOWN
} domino_os_kind;

/* domino_cpu_kind: Public type used by `sys`. */
typedef enum {
    DOMINO_CPU_X86_16,
    DOMINO_CPU_X86_32,
    DOMINO_CPU_X86_64,
    DOMINO_CPU_ARM_32,
    DOMINO_CPU_ARM_64,
    DOMINO_CPU_M68K,
    DOMINO_CPU_PPC,
    DOMINO_CPU_OTHER
} domino_cpu_kind;

/* domino_sys_platform_info: Public type used by `sys`. */
typedef struct domino_sys_platform_info {
    domino_os_kind     os;
    domino_cpu_kind    cpu;
    domino_sys_profile profile;

    unsigned int is_legacy   : 1; /* DOS16, Win16, Mac Classic, CP/M */
    unsigned int has_threads : 1;
    unsigned int has_fork    : 1;
    unsigned int has_unicode : 1;
} domino_sys_platform_info;

/* domino_sys_desc: Public type used by `sys`. */
typedef struct domino_sys_desc {
    domino_sys_profile profile_hint;
    /* future: logging callbacks, allocators, etc. */
} domino_sys_desc;

/* Backend selection (string-based, runtime hint) */
int dom_sys_select_backend(const char* name); /* "win32", "sdl2", "x11", "wayland", "posix_headless", "dos16", ... */

/*------------------------------------------------------------
 * Init / shutdown
 *------------------------------------------------------------*/
int  domino_sys_init(const domino_sys_desc* desc, domino_sys_context** out_ctx);
/* Purpose: Shutdown sys.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void domino_sys_shutdown(domino_sys_context* ctx);

/* Purpose: Get platform info.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void domino_sys_get_platform_info(domino_sys_context* ctx,
                                  domino_sys_platform_info* out_info);

/*------------------------------------------------------------
 * Paths
 *------------------------------------------------------------*/
typedef struct domino_sys_paths {
    char install_root[260]; /* root of installation: contains program/, data/, user/, state/ */
    char program_root[260]; /* program/ */
    char data_root[260];    /* data/   (official content) */
    char user_root[260];    /* user/   (unofficial content) */
    char state_root[260];   /* state/  (instances, saves, logs) */
    char temp_root[260];    /* temp/cache */
} domino_sys_paths;

/* Purpose: Get paths.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_sys_get_paths(domino_sys_context* ctx,
                         domino_sys_paths* out_paths);

/*------------------------------------------------------------
 * Filesystem
 *------------------------------------------------------------*/
typedef struct domino_sys_file domino_sys_file;

/* Purpose: Fopen sys.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
domino_sys_file* domino_sys_fopen(domino_sys_context* ctx,
                                  const char* path,
                                  const char* mode);
/* Purpose: Fread sys.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
size_t domino_sys_fread(domino_sys_context* ctx,
                        void* buf, size_t size, size_t nmemb,
                        domino_sys_file* f);
/* Purpose: Fwrite sys.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
size_t domino_sys_fwrite(domino_sys_context* ctx,
                         const void* buf, size_t size, size_t nmemb,
                         domino_sys_file* f);
/* Purpose: Fclose sys.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int    domino_sys_fclose(domino_sys_context* ctx,
                         domino_sys_file* f);

/* Purpose: File exists.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_sys_file_exists(domino_sys_context* ctx,
                           const char* path);
/* Purpose: Mkdirs sys.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_sys_mkdirs(domino_sys_context* ctx,
                      const char* path);

/*------------------------------------------------------------
 * Directory iteration
 *------------------------------------------------------------*/
typedef struct domino_sys_dir_iter domino_sys_dir_iter;

/* Purpose: Open sys dir.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
domino_sys_dir_iter* domino_sys_dir_open(domino_sys_context* ctx,
                                         const char* path);
/* Purpose: Dir next.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_sys_dir_next(domino_sys_context* ctx,
                        domino_sys_dir_iter* it,
                        char* name_out, size_t cap,
                        int* is_dir_out);
/* Purpose: Close sys dir.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void domino_sys_dir_close(domino_sys_context* ctx,
                          domino_sys_dir_iter* it);

/*------------------------------------------------------------
 * Time
 *------------------------------------------------------------*/
double         domino_sys_time_seconds(domino_sys_context* ctx);  /* monotonic if possible */
/* Purpose: Time millis.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
unsigned long  domino_sys_time_millis(domino_sys_context* ctx);
/* Purpose: Sleep millis.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void           domino_sys_sleep_millis(domino_sys_context* ctx,
                                       unsigned long ms);

/*------------------------------------------------------------
 * Processes
 *------------------------------------------------------------*/
typedef struct domino_sys_process domino_sys_process;

/* domino_sys_process_desc: Public type used by `sys`. */
typedef struct domino_sys_process_desc {
    const char* path;         /* executable path */
    const char* const* argv;  /* null-terminated argv */
    const char* working_dir;  /* optional */
} domino_sys_process_desc;

/* Purpose: Process spawn.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_sys_process_spawn(domino_sys_context* ctx,
                             const domino_sys_process_desc* desc,
                             domino_sys_process** out_proc);

/* Purpose: Process wait.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int domino_sys_process_wait(domino_sys_context* ctx,
                            domino_sys_process* proc,
                            int* exit_code_out);

/* Purpose: Destroy sys process.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void domino_sys_process_destroy(domino_sys_context* ctx,
                                domino_sys_process* proc);

/*------------------------------------------------------------
 * Logging
 *------------------------------------------------------------*/
typedef enum {
    DOMINO_LOG_DEBUG,
    DOMINO_LOG_INFO,
    DOMINO_LOG_WARN,
    DOMINO_LOG_ERROR
} domino_log_level;

/* Purpose: Log sys.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void domino_sys_log(domino_sys_context* ctx,
                    domino_log_level level,
                    const char* subsystem,
                    const char* message);

/*------------------------------------------------------------
 * Terminal API
 *------------------------------------------------------------*/
typedef struct domino_term_context domino_term_context;

/* domino_term_desc: Public type used by `sys`. */
typedef struct domino_term_desc {
    int use_alternate_buffer; /* if available on platform */
} domino_term_desc;

/* Purpose: Init term.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int  domino_term_init(domino_sys_context* sys,
                      const domino_term_desc* desc,
                      domino_term_context** out_term);
/* Purpose: Shutdown term.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void domino_term_shutdown(domino_term_context* term);

/* Purpose: Write term.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int  domino_term_write(domino_term_context* term,
                       const char* bytes,
                       size_t len);

/* Purpose: Line domino term read.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int  domino_term_read_line(domino_term_context* term,
                           char* buf,
                           size_t cap);

/*------------------------------------------------------------
 * New Domino system ABI (dsys_*)
 *------------------------------------------------------------*/
typedef struct dsys_context    dsys_context;
/* dsys_window: Public type used by `sys`. */
typedef struct dsys_window_t   dsys_window;
/* dsys_process: Public type used by `sys`. */
typedef struct dsys_process_t  dsys_process;
/* dsys_dir_iter: Public type used by `sys`. */
typedef struct dsys_dir_iter_t dsys_dir_iter;

/* dsys_result: Public type used by `sys`. */
typedef enum dsys_result {
    DSYS_OK = 0,
    DSYS_ERR,
    DSYS_ERR_NOT_FOUND,
    DSYS_ERR_IO,
    DSYS_ERR_UNSUPPORTED
} dsys_result;

/* message: Public type used by `sys`. */
typedef void (*dsys_log_fn)(const char* message);

/* dsys_caps: Public type used by `sys`. */
typedef struct dsys_caps {
    const char* name;
    uint32_t    ui_modes;
    bool        has_windows;
    bool        has_mouse;
    bool        has_gamepad;
    bool        has_high_res_timer;
} dsys_caps;

/* Purpose: Init dsys.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dsys_result dsys_init(void);
/* Purpose: Shutdown dsys.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void        dsys_shutdown(void);
/* Purpose: Caps dsys get.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dsys_caps   dsys_get_caps(void);

/* Purpose: Callback dsys set log.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void        dsys_set_log_callback(dsys_log_fn fn);

/* Time */
uint64_t dsys_time_now_us(void);
/* Purpose: Ms dsys sleep.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void     dsys_sleep_ms(uint32_t ms);

/* Window */
typedef enum dsys_window_mode {
    DWIN_MODE_WINDOWED = 0,
    DWIN_MODE_FULLSCREEN,
    DWIN_MODE_BORDERLESS
} dsys_window_mode;

/* dsys_window_desc: Public type used by `sys`. */
typedef struct dsys_window_desc {
    int32_t          x;
    int32_t          y;
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
} dsys_window_desc;

/* dsys_window_state: Public type used by `sys`. */
typedef struct dsys_window_state {
    bool should_close;
    bool focused;
    bool minimized;
    bool maximized;
    bool occluded;
} dsys_window_state;

/* Purpose: Create window.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dsys_window* dsys_window_create(const dsys_window_desc* desc);
/* Purpose: Destroy window.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         dsys_window_destroy(dsys_window* win);
/* Purpose: Mode dsys window set.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         dsys_window_set_mode(dsys_window* win, dsys_window_mode mode);
/* Purpose: Size dsys window set.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         dsys_window_set_size(dsys_window* win, int32_t w, int32_t h);
/* Purpose: Size dsys window get.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         dsys_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
/* Purpose: Handle dsys window get native.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void*        dsys_window_get_native_handle(dsys_window* win);
/* Purpose: Close window should.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int          dsys_window_should_close(dsys_window* win);
/* Purpose: Present dsys window.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         dsys_window_present(dsys_window* win);
/* Purpose: Show dsys window.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         dsys_window_show(dsys_window* win);
/* Purpose: Hide dsys window.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         dsys_window_hide(dsys_window* win);
/* Purpose: State dsys window get.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         dsys_window_get_state(dsys_window* win, dsys_window_state* out_state);
/* Purpose: Framebuffer size dsys window get.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void         dsys_window_get_framebuffer_size(dsys_window* win, int32_t* w, int32_t* h);
/* Purpose: Dpi scale dsys window get.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
float        dsys_window_get_dpi_scale(dsys_window* win);
/* Purpose: Window id dsys window get.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
uint32_t     dsys_window_get_id(dsys_window* win);

/* Input events */
typedef enum dsys_event_type {
    DSYS_EVENT_QUIT = 0,
    DSYS_EVENT_WINDOW_RESIZED,
    DSYS_EVENT_DPI_CHANGED,
    DSYS_EVENT_KEY_DOWN,
    DSYS_EVENT_KEY_UP,
    DSYS_EVENT_TEXT_INPUT,
    DSYS_EVENT_MOUSE_MOVE,
    DSYS_EVENT_MOUSE_BUTTON,
    DSYS_EVENT_MOUSE_WHEEL,
    DSYS_EVENT_GAMEPAD_BUTTON,
    DSYS_EVENT_GAMEPAD_AXIS
} dsys_event_type;

/* window: Public type used by `sys`. */
typedef struct dsys_event {
    dsys_event_type type;
    uint64_t        timestamp_us;
    dsys_window*    window;
    uint32_t        window_id;
    union {
        struct { int32_t width; int32_t height; } window;
        struct { float scale; } dpi;
        struct { int32_t key; bool repeat; } key;
        struct { char text[8]; } text;
        struct { int32_t x; int32_t y; int32_t dx; int32_t dy; } mouse_move;
        struct { int32_t button; bool pressed; int32_t clicks; } mouse_button;
        struct { int32_t delta_x; int32_t delta_y; } mouse_wheel;
        struct { int32_t button; bool pressed; int32_t gamepad; } gamepad_button;
        struct { int32_t axis; int32_t gamepad; float value; } gamepad_axis;
    } payload;
} dsys_event;

/* Purpose: Event dsys poll.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool dsys_poll_event(dsys_event* out);

/* Purpose: Inject event into the runtime queue (for TUI/internal events).
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` if the queue is full.
 */
bool dsys_inject_event(const dsys_event* ev);

/* Shutdown lifecycle */
typedef enum dsys_shutdown_reason {
    DSYS_SHUTDOWN_NONE = 0,
    DSYS_SHUTDOWN_SIGNAL,
    DSYS_SHUTDOWN_CONSOLE,
    DSYS_SHUTDOWN_WINDOW,
    DSYS_SHUTDOWN_APP_REQUEST
} dsys_shutdown_reason;

/* Purpose: Install lifecycle/signal handlers.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void dsys_lifecycle_init(void);
/* Purpose: Uninstall lifecycle/signal handlers.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void dsys_lifecycle_shutdown(void);
/* Purpose: Request shutdown (set flag only; safe for signal handlers).
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void dsys_lifecycle_request_shutdown(dsys_shutdown_reason reason);
/* Purpose: Check whether shutdown was requested.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` if shutdown was requested.
 */
bool dsys_lifecycle_shutdown_requested(void);
/* Purpose: Read last shutdown reason.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
dsys_shutdown_reason dsys_lifecycle_shutdown_reason(void);
/* Purpose: Reason text.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: String label for reason.
 */
const char* dsys_lifecycle_shutdown_reason_text(dsys_shutdown_reason reason);

/* Filesystem */
typedef enum dsys_path_kind {
    DSYS_PATH_APP_ROOT = 0,
    DSYS_PATH_USER_DATA,
    DSYS_PATH_USER_CONFIG,
    DSYS_PATH_USER_CACHE,
    DSYS_PATH_TEMP
} dsys_path_kind;

/* Purpose: Path dsys get.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool   dsys_get_path(dsys_path_kind kind, char* buf, size_t buf_size);

/* Purpose: Open file.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void*  dsys_file_open(const char* path, const char* mode);
/* Purpose: Read file.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
size_t dsys_file_read(void* fh, void* buf, size_t size);
/* Purpose: Write file.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
size_t dsys_file_write(void* fh, const void* buf, size_t size);
/* Purpose: Seek dsys file.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int    dsys_file_seek(void* fh, long offset, int origin);
/* Purpose: Tell dsys file.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
long   dsys_file_tell(void* fh);
/* Purpose: Close file.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int    dsys_file_close(void* fh);

/* dsys_dir_entry: Public type used by `sys`. */
typedef struct dsys_dir_entry {
    char name[260];
    bool is_dir;
} dsys_dir_entry;

/* Purpose: Open dir.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dsys_dir_iter* dsys_dir_open(const char* path);
/* Purpose: Next dsys dir.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: `true` on success; `false` on failure.
 */
bool           dsys_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
/* Purpose: Close dir.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void           dsys_dir_close(dsys_dir_iter* it);

/* Processes */
typedef struct dsys_process_desc {
    const char*        exe;
    const char* const* argv;
    uint32_t           flags;
} dsys_process_desc;

/* Purpose: Spawn dsys process.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Non-NULL on success; NULL on failure or when not found.
 */
dsys_process* dsys_process_spawn(const dsys_process_desc* desc);
/* Purpose: Wait dsys process.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int           dsys_process_wait(dsys_process* p);
/* Purpose: Destroy process.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void          dsys_process_destroy(dsys_process* p);

/*------------------------------------------------------------
 * Raw input feed (platform native; deterministic ordering only)
 *------------------------------------------------------------*/
typedef enum dsys_input_event_type {
    DSYS_INPUT_EVENT_NONE = 0,
    DSYS_INPUT_EVENT_KEY_DOWN,
    DSYS_INPUT_EVENT_KEY_UP,
    DSYS_INPUT_EVENT_TEXT,
    DSYS_INPUT_EVENT_MOUSE_MOVE,
    DSYS_INPUT_EVENT_MOUSE_BUTTON,
    DSYS_INPUT_EVENT_MOUSE_WHEEL,
    DSYS_INPUT_EVENT_CONTROLLER_BUTTON,
    DSYS_INPUT_EVENT_CONTROLLER_AXIS,
    DSYS_INPUT_EVENT_TOUCH
} dsys_input_event_type;

/* key: Public type used by `sys`. */
typedef struct dsys_input_event {
    dsys_input_event_type type;
    union {
        struct { int32_t keycode; int32_t repeat; int32_t translated; } key;
        struct { char text[16]; } text;
        struct { int32_t x; int32_t y; int32_t dx; int32_t dy; } mouse_move;
        struct { int32_t button; int32_t pressed; int32_t x; int32_t y; int32_t clicks; } mouse_button;
        struct { int32_t delta_x; int32_t delta_y; } mouse_wheel;
        struct { int32_t gamepad; int32_t control; int32_t value; int32_t is_axis; } controller;
        struct { int32_t id; int32_t x; int32_t y; int32_t state; } touch;
    } payload;
} dsys_input_event;

/* Purpose: Raw dsys input poll.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int dsys_input_poll_raw(dsys_input_event* ev);

/*------------------------------------------------------------
 * IME (Input Method Editor)
 *------------------------------------------------------------*/
typedef struct dsys_ime_event {
    char composition[128];
    char committed[128];
    int  has_composition;
    int  has_commit;
} dsys_ime_event;

/* Purpose: Start dsys ime.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void dsys_ime_start(void);
/* Purpose: Stop dsys ime.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void dsys_ime_stop(void);
/* Purpose: Cursor dsys ime set.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 */
void dsys_ime_set_cursor(int32_t x, int32_t y);
/* Purpose: Poll dsys ime.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
int  dsys_ime_poll(dsys_ime_event* ev);

/*------------------------------------------------------------
 * Versioned DSYS facade vtables (v1)
 *------------------------------------------------------------*/

/* Interface IDs (u32 constants) */
#define DSYS_PROTOCOL_VERSION 1u
#define DSYS_IID_CORE_API_V1     ((dom_iid)0x44535901u)
#define DSYS_IID_FS_API_V1       ((dom_iid)0x44535902u)
#define DSYS_IID_TIME_API_V1     ((dom_iid)0x44535903u)
#define DSYS_IID_PROCESS_API_V1  ((dom_iid)0x44535904u)
#define DSYS_IID_DYNLIB_API_V1   ((dom_iid)0x44535905u)
#define DSYS_IID_WINDOW_API_V1   ((dom_iid)0x44535906u)
#define DSYS_IID_INPUT_API_V1    ((dom_iid)0x44535907u)
#define DSYS_IID_THREAD_API_V1   ((dom_iid)0x44535908u)
#define DSYS_IID_ATOMIC_API_V1   ((dom_iid)0x44535909u)
#define DSYS_IID_NET_API_V1      ((dom_iid)0x4453590Au)
#define DSYS_IID_AUDIOIO_API_V1  ((dom_iid)0x4453590Bu)
#define DSYS_IID_CLIPTEXT_API_V1 ((dom_iid)0x4453590Cu)
#define DSYS_IID_WINDOW_EX_API_V1 ((dom_iid)0x4453590Du)
#define DSYS_IID_ERROR_API_V1     ((dom_iid)0x4453590Eu)
#define DSYS_IID_CURSOR_API_V1    ((dom_iid)0x4453590Fu)
#define DSYS_IID_DRAGDROP_API_V1  ((dom_iid)0x44535910u)
#define DSYS_IID_GAMEPAD_API_V1   ((dom_iid)0x44535911u)
#define DSYS_IID_POWER_API_V1     ((dom_iid)0x44535912u)

/* Extension names for dsys_query_extension (name + version). */
#define DSYS_EXTENSION_WINDOW_EX "dsys.window_ex"
#define DSYS_EXTENSION_ERROR     "dsys.error"
#define DSYS_EXTENSION_CLIPTEXT  "dsys.cliptext"
#define DSYS_EXTENSION_CURSOR    "dsys.cursor"
#define DSYS_EXTENSION_DRAGDROP  "dsys.dragdrop"
#define DSYS_EXTENSION_GAMEPAD   "dsys.gamepad"
#define DSYS_EXTENSION_POWER     "dsys.power"
#define DSYS_EXTENSION_TEXT_INPUT "dsys.text_input"
#define DSYS_EXTENSION_WINDOW_MODE "dsys.window_mode"
#define DSYS_EXTENSION_DPI "dsys.dpi"

#define DSYS_EXTENSION_WINDOW_EX_VERSION 1u
#define DSYS_EXTENSION_ERROR_VERSION 1u
#define DSYS_EXTENSION_CLIPTEXT_VERSION 1u
#define DSYS_EXTENSION_CURSOR_VERSION 1u
#define DSYS_EXTENSION_DRAGDROP_VERSION 1u
#define DSYS_EXTENSION_GAMEPAD_VERSION 1u
#define DSYS_EXTENSION_POWER_VERSION 1u
#define DSYS_EXTENSION_TEXT_INPUT_VERSION 1u
#define DSYS_EXTENSION_WINDOW_MODE_VERSION 1u
#define DSYS_EXTENSION_DPI_VERSION 1u

/* dsys_core_api_v1: Public type used by `sys`. */
typedef struct dsys_core_api_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;

    /* lifecycle */
    dsys_result (*init)(void);
    void        (*shutdown)(void);
    dsys_caps   (*get_caps)(void);

    /* logging (optional; may be NULL) */
    void (*set_log_callback)(dsys_log_fn fn);
} dsys_core_api_v1;

/* dsys_time_api_v1: Public type used by `sys`. */
typedef struct dsys_time_api_v1 {
    DOM_ABI_HEADER;
    uint64_t (*time_now_us)(void);
    void     (*sleep_ms)(uint32_t ms);
} dsys_time_api_v1;

/* dsys_fs_api_v1: Public type used by `sys`. */
typedef struct dsys_fs_api_v1 {
    DOM_ABI_HEADER;
    bool   (*get_path)(dsys_path_kind kind, char* buf, size_t buf_size);

    void*  (*file_open)(const char* path, const char* mode);
    size_t (*file_read)(void* fh, void* buf, size_t size);
    size_t (*file_write)(void* fh, const void* buf, size_t size);
    int    (*file_seek)(void* fh, long offset, int origin);
    long   (*file_tell)(void* fh);
    int    (*file_close)(void* fh);

    dsys_dir_iter* (*dir_open)(const char* path);
    bool           (*dir_next)(dsys_dir_iter* it, dsys_dir_entry* out);
    void           (*dir_close)(dsys_dir_iter* it);
} dsys_fs_api_v1;

/* dsys_process_api_v1: Public type used by `sys`. */
typedef struct dsys_process_api_v1 {
    DOM_ABI_HEADER;
    dsys_process* (*spawn)(const dsys_process_desc* desc);
    int           (*wait)(dsys_process* p);
    void          (*destroy)(dsys_process* p);
} dsys_process_api_v1;

/* dsys_dynlib_api_v1: Public type used by `sys`. */
typedef struct dsys_dynlib_api_v1 {
    DOM_ABI_HEADER;
    void* (*open)(const char* path);
    void  (*close)(void* lib);
    void* (*sym)(void* lib, const char* name);
} dsys_dynlib_api_v1;

/* dsys_window_api_v1: Public type used by `sys`. */
typedef struct dsys_window_api_v1 {
    DOM_ABI_HEADER;
    dsys_window* (*create)(const dsys_window_desc* desc);
    void         (*destroy)(dsys_window* win);
    void         (*set_mode)(dsys_window* win, dsys_window_mode mode);
    void         (*set_size)(dsys_window* win, int32_t w, int32_t h);
    void         (*get_size)(dsys_window* win, int32_t* w, int32_t* h);
    void*        (*get_native_handle)(dsys_window* win);
    int          (*should_close)(dsys_window* win);
    void         (*present)(dsys_window* win);
} dsys_window_api_v1;

/* dsys_window_ex_api_v1: Public type used by `sys`. */
typedef struct dsys_window_ex_api_v1 {
    DOM_ABI_HEADER;
    void  (*show)(dsys_window* win);
    void  (*hide)(dsys_window* win);
    void  (*get_state)(dsys_window* win, dsys_window_state* out_state);
    void  (*get_framebuffer_size)(dsys_window* win, int32_t* w, int32_t* h);
    float (*get_dpi_scale)(dsys_window* win);
} dsys_window_ex_api_v1;

/* dsys_input_api_v1: Public type used by `sys`. */
typedef struct dsys_input_api_v1 {
    DOM_ABI_HEADER;
    bool (*poll_event)(dsys_event* out);
    int  (*poll_raw)(dsys_input_event* ev);

    void (*ime_start)(void);
    void (*ime_stop)(void);
    void (*ime_set_cursor)(int32_t x, int32_t y);
    int  (*ime_poll)(dsys_ime_event* ev);
} dsys_input_api_v1;

/* dsys_thread_api_v1: Public type used by `sys`. */
typedef struct dsys_thread_api_v1 {
    DOM_ABI_HEADER;
    void* reserved0;
    void* reserved1;
} dsys_thread_api_v1;

/* dsys_atomic_api_v1: Public type used by `sys`. */
typedef struct dsys_atomic_api_v1 {
    DOM_ABI_HEADER;
    void* reserved0;
    void* reserved1;
} dsys_atomic_api_v1;

/* dsys_net_api_v1: Public type used by `sys`. */
typedef struct dsys_net_api_v1 {
    DOM_ABI_HEADER;
    void* reserved0;
    void* reserved1;
} dsys_net_api_v1;

/* dsys_audioio_api_v1: Public type used by `sys`. */
typedef struct dsys_audioio_api_v1 {
    DOM_ABI_HEADER;
    void* reserved0;
    void* reserved1;
} dsys_audioio_api_v1;

/* dsys_cliptext_api_v1: Public type used by `sys`. */
typedef struct dsys_cliptext_api_v1 {
    DOM_ABI_HEADER;
    dsys_result (*get_text)(char* buf, size_t cap);
    dsys_result (*set_text)(const char* text);
} dsys_cliptext_api_v1;

/* dsys_cursor_shape: Public type used by `sys`. */
typedef enum dsys_cursor_shape {
    DSYS_CURSOR_ARROW = 0,
    DSYS_CURSOR_IBEAM,
    DSYS_CURSOR_HAND,
    DSYS_CURSOR_SIZE_H,
    DSYS_CURSOR_SIZE_V,
    DSYS_CURSOR_SIZE_ALL
} dsys_cursor_shape;

/* dsys_cursor_api_v1: Public type used by `sys`. */
typedef struct dsys_cursor_api_v1 {
    DOM_ABI_HEADER;
    dsys_result (*set_cursor)(dsys_window* win, dsys_cursor_shape shape);
    dsys_result (*show_cursor)(dsys_window* win, bool visible);
    dsys_result (*confine_cursor)(dsys_window* win, bool confined);
    dsys_result (*set_relative_mode)(dsys_window* win, bool enabled);
} dsys_cursor_api_v1;

/* dsys_dragdrop_api_v1: Public type used by `sys`. */
typedef struct dsys_dragdrop_api_v1 {
    DOM_ABI_HEADER;
    void* reserved0;
    void* reserved1;
} dsys_dragdrop_api_v1;

/* dsys_gamepad_api_v1: Public type used by `sys`. */
typedef struct dsys_gamepad_api_v1 {
    DOM_ABI_HEADER;
    void* reserved0;
    void* reserved1;
} dsys_gamepad_api_v1;

/* dsys_power_api_v1: Public type used by `sys`. */
typedef struct dsys_power_api_v1 {
    DOM_ABI_HEADER;
    void* reserved0;
    void* reserved1;
} dsys_power_api_v1;

/* dsys_text_input_api_v1: Public type used by `sys`. */
typedef struct dsys_text_input_api_v1 {
    DOM_ABI_HEADER;
    dsys_result (*start)(dsys_window* win);
    dsys_result (*stop)(dsys_window* win);
    dsys_result (*set_ime_cursor)(dsys_window* win, int32_t x, int32_t y);
    int         (*poll_ime)(dsys_ime_event* ev);
} dsys_text_input_api_v1;

/* dsys_window_mode_api_v1: Public type used by `sys`. */
typedef struct dsys_window_mode_api_v1 {
    DOM_ABI_HEADER;
    dsys_result      (*set_mode)(dsys_window* win, dsys_window_mode mode);
    dsys_window_mode (*get_mode)(dsys_window* win);
} dsys_window_mode_api_v1;

/* dsys_error_api_v1: Public type used by `sys`. */
typedef struct dsys_error_api_v1 {
    DOM_ABI_HEADER;
    dsys_result (*last_error_code)(void);
    const char* (*last_error_text)(void);
} dsys_error_api_v1;

/* Purpose: Api dsys get core.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dsys_result dsys_get_core_api(u32 requested_abi, dsys_core_api_v1* out);
/* Purpose: Query dsys extension by name + version.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: Extension table pointer or NULL.
 */
void*      dsys_query_extension(const char* name, u32 version);
/* Purpose: Last dsys error code.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
dsys_result dsys_last_error_code(void);
/* Purpose: Last dsys error text.
 * Parameters: See `docs/specs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/specs/CONTRACTS.md#Return Values / Errors`.
 */
const char* dsys_last_error_text(void);

#ifdef DOMINO_SYS_INTERNAL
/* dsys_backend_vtable: Public type used by `sys`. */
typedef struct dsys_backend_vtable_t {
    /* lifecycle */
    dsys_result (*init)(void);
    void        (*shutdown)(void);
    dsys_caps   (*get_caps)(void);

    /* time */
    uint64_t (*time_now_us)(void);
    void     (*sleep_ms)(uint32_t ms);

    /* window */
    dsys_window* (*window_create)(const dsys_window_desc* desc);
    void         (*window_destroy)(dsys_window* win);
    void         (*window_set_mode)(dsys_window* win, dsys_window_mode mode);
    void         (*window_set_size)(dsys_window* win, int32_t w, int32_t h);
    void         (*window_get_size)(dsys_window* win, int32_t* w, int32_t* h);
    void         (*window_show)(dsys_window* win);
    void         (*window_hide)(dsys_window* win);
    void         (*window_get_state)(dsys_window* win, dsys_window_state* out_state);
    void         (*window_get_framebuffer_size)(dsys_window* win, int32_t* w, int32_t* h);
    float        (*window_get_dpi_scale)(dsys_window* win);
    void*        (*window_get_native_handle)(dsys_window* win);

    /* events */
    bool (*poll_event)(dsys_event* ev);

    /* filesystem */
    bool   (*get_path)(dsys_path_kind kind, char* buf, size_t buf_size);
    void*  (*file_open)(const char* path, const char* mode);
    size_t (*file_read)(void* fh, void* buf, size_t size);
    size_t (*file_write)(void* fh, const void* buf, size_t size);
    int    (*file_seek)(void* fh, long offset, int origin);
    long   (*file_tell)(void* fh);
    int    (*file_close)(void* fh);

    dsys_dir_iter* (*dir_open)(const char* path);
    bool           (*dir_next)(dsys_dir_iter* it, dsys_dir_entry* out);
    void           (*dir_close)(dsys_dir_iter* it);

    /* processes */
    dsys_process* (*process_spawn)(const dsys_process_desc* desc);
    int           (*process_wait)(dsys_process* p);
    void          (*process_destroy)(dsys_process* p);
} dsys_backend_vtable;
#endif /* DOMINO_SYS_INTERNAL */

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_SYS_H_INCLUDED */
