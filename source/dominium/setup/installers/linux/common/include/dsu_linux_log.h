#ifndef DSU_LINUX_LOG_H_INCLUDED
#define DSU_LINUX_LOG_H_INCLUDED

#include <stdarg.h>

#ifdef __cplusplus
extern "C" {
#endif

void dsu_linux_log_set_file(const char *path);
void dsu_linux_log_info(const char *fmt, ...);
void dsu_linux_log_error(const char *fmt, ...);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_LINUX_LOG_H_INCLUDED */
