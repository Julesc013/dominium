#ifndef DSU_EXE_LOG_H_INCLUDED
#define DSU_EXE_LOG_H_INCLUDED

#include <stdarg.h>

#ifdef __cplusplus
extern "C" {
#endif

void dsu_exe_log_set_file(const char *path);
void dsu_exe_log_info(const char *fmt, ...);
void dsu_exe_log_error(const char *fmt, ...);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_EXE_LOG_H_INCLUDED */
