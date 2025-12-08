#ifndef DOMINO_SYS_H_INCLUDED
#define DOMINO_SYS_H_INCLUDED

/* Domino System / Platform API - C89 friendly */

#include <stddef.h>
#include <stdint.h>

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
typedef struct dsys_file       dsys_file;
typedef struct dsys_dir_iter   dsys_dir_iter;
typedef struct dsys_process    dsys_process;

typedef enum dsys_profile {
    DSYS_PROFILE_AUTO = 0,
    DSYS_PROFILE_MINIMAL,
    DSYS_PROFILE_STANDARD,
    DSYS_PROFILE_FULL
} dsys_profile;

typedef enum dsys_os_kind {
    DSYS_OS_UNKNOWN = 0,
    DSYS_OS_WINDOWS,
    DSYS_OS_MAC,
    DSYS_OS_UNIX,
    DSYS_OS_ANDROID,
    DSYS_OS_DOS,
    DSYS_OS_CPM
} dsys_os_kind;

typedef enum dsys_cpu_kind {
    DSYS_CPU_UNKNOWN = 0,
    DSYS_CPU_X86_16,
    DSYS_CPU_X86_32,
    DSYS_CPU_X86_64,
    DSYS_CPU_ARM_32,
    DSYS_CPU_ARM_64,
    DSYS_CPU_PPC,
    DSYS_CPU_M68K,
    DSYS_CPU_OTHER
} dsys_cpu_kind;

typedef enum dsys_log_level {
    DSYS_LOG_DEBUG = 0,
    DSYS_LOG_INFO  = 1,
    DSYS_LOG_WARN  = 2,
    DSYS_LOG_ERROR = 3
} dsys_log_level;

typedef void (*dsys_log_fn)(void* user,
                            dsys_log_level level,
                            const char* category,
                            const char* message);

#define DSYS_PLATFORM_FLAG_HAS_THREADS 0x00000001u
#define DSYS_PLATFORM_FLAG_HAS_FORK    0x00000002u
#define DSYS_PLATFORM_FLAG_HAS_UNICODE 0x00000004u
#define DSYS_PLATFORM_FLAG_IS_LEGACY   0x00000008u

typedef struct dsys_platform_info {
    uint32_t      struct_size;
    uint32_t      struct_version;
    dsys_os_kind  os;
    dsys_cpu_kind cpu;
    uint32_t      pointer_size;
    uint32_t      page_size;
    uint32_t      flags;
} dsys_platform_info;

typedef struct dsys_paths {
    uint32_t struct_size;
    uint32_t struct_version;
    char install_root[260];
    char program_root[260];
    char data_root[260];
    char user_root[260];
    char state_root[260];
    char temp_root[260];
} dsys_paths;

typedef struct dsys_desc {
    uint32_t    struct_size;
    uint32_t    struct_version;
    dsys_profile profile;
    dsys_log_fn log_fn;
    void*       log_user;
} dsys_desc;

int  dsys_create(const dsys_desc* desc, dsys_context** out_sys);
void dsys_destroy(dsys_context* sys);

int dsys_get_platform_info(dsys_context* sys, dsys_platform_info* out_info);
int dsys_get_paths(dsys_context* sys, dsys_paths* out_paths);
int dsys_set_log_hook(dsys_context* sys, dsys_log_fn log_fn, void* user_data);

uint64_t dsys_time_ticks(dsys_context* sys);
double   dsys_time_seconds(dsys_context* sys);
void     dsys_sleep_millis(dsys_context* sys, uint32_t millis);

int dsys_file_exists(dsys_context* sys, const char* path);
int dsys_mkdirs(dsys_context* sys, const char* path);

dsys_file* dsys_file_open(dsys_context* sys, const char* path, const char* mode);
size_t     dsys_file_read(dsys_file* file, void* buffer, size_t bytes);
size_t     dsys_file_write(dsys_file* file, const void* buffer, size_t bytes);
void       dsys_file_close(dsys_file* file);

dsys_dir_iter* dsys_dir_open(dsys_context* sys, const char* path);
int            dsys_dir_next(dsys_dir_iter* it, char* name_out, size_t cap, int* is_dir_out);
void           dsys_dir_close(dsys_dir_iter* it);

typedef struct dsys_process_desc {
    uint32_t    struct_size;
    uint32_t    struct_version;
    const char* path;
    const char* const* argv;
    const char* working_dir;
} dsys_process_desc;

int  dsys_process_spawn(dsys_context* sys, const dsys_process_desc* desc, dsys_process** out_proc);
int  dsys_process_wait(dsys_process* proc, int* exit_code_out);
void dsys_process_destroy(dsys_process* proc);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_SYS_H_INCLUDED */
