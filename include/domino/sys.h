#ifndef DOMINO_SYS_H
#define DOMINO_SYS_H

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

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_SYS_H */
