#ifndef DOMINO_SYS_H_INCLUDED
#define DOMINO_SYS_H_INCLUDED

/* Domino System / Platform API - C89 friendly */

#include <stddef.h>
#include "domino/baseline.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Core types
 *------------------------------------------------------------*/

typedef struct domino_sys_context domino_sys_context;

typedef enum {
    DOMINO_SYS_PROFILE_AUTO = 0,
    DOMINO_SYS_PROFILE_TINY,
    DOMINO_SYS_PROFILE_REDUCED,
    DOMINO_SYS_PROFILE_FULL
} domino_sys_profile;

typedef enum {
    DOMINO_OS_DOS,
    DOMINO_OS_WINDOWS,
    DOMINO_OS_MAC,
    DOMINO_OS_UNIX,
    DOMINO_OS_ANDROID,
    DOMINO_OS_CPM,
    DOMINO_OS_UNKNOWN
} domino_os_kind;

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

typedef struct domino_sys_platform_info {
    domino_os_kind     os;
    domino_cpu_kind    cpu;
    domino_sys_profile profile;

    unsigned int is_legacy   : 1; /* DOS16, Win16, Mac Classic, CP/M */
    unsigned int has_threads : 1;
    unsigned int has_fork    : 1;
    unsigned int has_unicode : 1;
} domino_sys_platform_info;

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
void domino_sys_shutdown(domino_sys_context* ctx);

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

int domino_sys_get_paths(domino_sys_context* ctx,
                         domino_sys_paths* out_paths);

/*------------------------------------------------------------
 * Filesystem
 *------------------------------------------------------------*/
typedef struct domino_sys_file domino_sys_file;

domino_sys_file* domino_sys_fopen(domino_sys_context* ctx,
                                  const char* path,
                                  const char* mode);
size_t domino_sys_fread(domino_sys_context* ctx,
                        void* buf, size_t size, size_t nmemb,
                        domino_sys_file* f);
size_t domino_sys_fwrite(domino_sys_context* ctx,
                         const void* buf, size_t size, size_t nmemb,
                         domino_sys_file* f);
int    domino_sys_fclose(domino_sys_context* ctx,
                         domino_sys_file* f);

int domino_sys_file_exists(domino_sys_context* ctx,
                           const char* path);
int domino_sys_mkdirs(domino_sys_context* ctx,
                      const char* path);

/*------------------------------------------------------------
 * Directory iteration
 *------------------------------------------------------------*/
typedef struct domino_sys_dir_iter domino_sys_dir_iter;

domino_sys_dir_iter* domino_sys_dir_open(domino_sys_context* ctx,
                                         const char* path);
int domino_sys_dir_next(domino_sys_context* ctx,
                        domino_sys_dir_iter* it,
                        char* name_out, size_t cap,
                        int* is_dir_out);
void domino_sys_dir_close(domino_sys_context* ctx,
                          domino_sys_dir_iter* it);

/*------------------------------------------------------------
 * Time
 *------------------------------------------------------------*/
double         domino_sys_time_seconds(domino_sys_context* ctx);  /* monotonic if possible */
unsigned long  domino_sys_time_millis(domino_sys_context* ctx);
void           domino_sys_sleep_millis(domino_sys_context* ctx,
                                       unsigned long ms);

/*------------------------------------------------------------
 * Processes
 *------------------------------------------------------------*/
typedef struct domino_sys_process domino_sys_process;

typedef struct domino_sys_process_desc {
    const char* path;         /* executable path */
    const char* const* argv;  /* null-terminated argv */
    const char* working_dir;  /* optional */
} domino_sys_process_desc;

int domino_sys_process_spawn(domino_sys_context* ctx,
                             const domino_sys_process_desc* desc,
                             domino_sys_process** out_proc);

int domino_sys_process_wait(domino_sys_context* ctx,
                            domino_sys_process* proc,
                            int* exit_code_out);

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

void domino_sys_log(domino_sys_context* ctx,
                    domino_log_level level,
                    const char* subsystem,
                    const char* message);

/*------------------------------------------------------------
 * Terminal API
 *------------------------------------------------------------*/
typedef struct domino_term_context domino_term_context;

typedef struct domino_term_desc {
    int use_alternate_buffer; /* if available on platform */
} domino_term_desc;

int  domino_term_init(domino_sys_context* sys,
                      const domino_term_desc* desc,
                      domino_term_context** out_term);
void domino_term_shutdown(domino_term_context* term);

int  domino_term_write(domino_term_context* term,
                       const char* bytes,
                       size_t len);

int  domino_term_read_line(domino_term_context* term,
                           char* buf,
                           size_t cap);

/*------------------------------------------------------------
 * New Domino system ABI (dsys_*)
 *------------------------------------------------------------*/
typedef struct dsys_context    dsys_context;
typedef struct dsys_window_t   dsys_window;
typedef struct dsys_process_t  dsys_process;
typedef struct dsys_dir_iter_t dsys_dir_iter;

typedef enum dsys_result {
    DSYS_OK = 0,
    DSYS_ERR,
    DSYS_ERR_NOT_FOUND,
    DSYS_ERR_IO,
    DSYS_ERR_UNSUPPORTED
} dsys_result;

typedef struct dsys_caps {
    const char* name;
    uint32_t    ui_modes;
    bool        has_windows;
    bool        has_mouse;
    bool        has_gamepad;
    bool        has_high_res_timer;
} dsys_caps;

dsys_result dsys_init(void);
void        dsys_shutdown(void);
dsys_caps   dsys_get_caps(void);

/* Time */
uint64_t dsys_time_now_us(void);
void     dsys_sleep_ms(uint32_t ms);

/* Window */
typedef enum dsys_window_mode {
    DWIN_MODE_WINDOWED = 0,
    DWIN_MODE_FULLSCREEN,
    DWIN_MODE_BORDERLESS
} dsys_window_mode;

typedef struct dsys_window_desc {
    int32_t          x;
    int32_t          y;
    int32_t          width;
    int32_t          height;
    dsys_window_mode mode;
} dsys_window_desc;

dsys_window* dsys_window_create(const dsys_window_desc* desc);
void         dsys_window_destroy(dsys_window* win);
void         dsys_window_set_mode(dsys_window* win, dsys_window_mode mode);
void         dsys_window_set_size(dsys_window* win, int32_t w, int32_t h);
void         dsys_window_get_size(dsys_window* win, int32_t* w, int32_t* h);
void*        dsys_window_get_native_handle(dsys_window* win);
int          dsys_window_should_close(dsys_window* win);
void         dsys_window_present(dsys_window* win);

/* Input events */
typedef enum dsys_event_type {
    DSYS_EVENT_QUIT = 0,
    DSYS_EVENT_WINDOW_RESIZED,
    DSYS_EVENT_KEY_DOWN,
    DSYS_EVENT_KEY_UP,
    DSYS_EVENT_TEXT_INPUT,
    DSYS_EVENT_MOUSE_MOVE,
    DSYS_EVENT_MOUSE_BUTTON,
    DSYS_EVENT_MOUSE_WHEEL,
    DSYS_EVENT_GAMEPAD_BUTTON,
    DSYS_EVENT_GAMEPAD_AXIS
} dsys_event_type;

typedef struct dsys_event {
    dsys_event_type type;
    union {
        struct { int32_t width; int32_t height; } window;
        struct { int32_t key; bool repeat; } key;
        struct { char text[8]; } text;
        struct { int32_t x; int32_t y; int32_t dx; int32_t dy; } mouse_move;
        struct { int32_t button; bool pressed; int32_t clicks; } mouse_button;
        struct { int32_t delta_x; int32_t delta_y; } mouse_wheel;
        struct { int32_t button; bool pressed; int32_t gamepad; } gamepad_button;
        struct { int32_t axis; int32_t gamepad; float value; } gamepad_axis;
    } payload;
} dsys_event;

bool dsys_poll_event(dsys_event* out);

/* Filesystem */
typedef enum dsys_path_kind {
    DSYS_PATH_APP_ROOT = 0,
    DSYS_PATH_USER_DATA,
    DSYS_PATH_USER_CONFIG,
    DSYS_PATH_USER_CACHE,
    DSYS_PATH_TEMP
} dsys_path_kind;

bool   dsys_get_path(dsys_path_kind kind, char* buf, size_t buf_size);

void*  dsys_file_open(const char* path, const char* mode);
size_t dsys_file_read(void* fh, void* buf, size_t size);
size_t dsys_file_write(void* fh, const void* buf, size_t size);
int    dsys_file_seek(void* fh, long offset, int origin);
long   dsys_file_tell(void* fh);
int    dsys_file_close(void* fh);

typedef struct dsys_dir_entry {
    char name[260];
    bool is_dir;
} dsys_dir_entry;

dsys_dir_iter* dsys_dir_open(const char* path);
bool           dsys_dir_next(dsys_dir_iter* it, dsys_dir_entry* out);
void           dsys_dir_close(dsys_dir_iter* it);

/* Processes */
typedef struct dsys_process_desc {
    const char*        exe;
    const char* const* argv;
    uint32_t           flags;
} dsys_process_desc;

dsys_process* dsys_process_spawn(const dsys_process_desc* desc);
int           dsys_process_wait(dsys_process* p);
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

void dsys_ime_start(void);
void dsys_ime_stop(void);
void dsys_ime_set_cursor(int32_t x, int32_t y);
int  dsys_ime_poll(dsys_ime_event* ev);

#ifdef DOMINO_SYS_INTERNAL
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
