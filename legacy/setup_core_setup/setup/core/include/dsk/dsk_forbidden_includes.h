#ifndef DSK_FORBIDDEN_INCLUDES_H
#define DSK_FORBIDDEN_INCLUDES_H

#if defined(DSK_FORBID_OS_HEADERS)
#if defined(_WINDOWS_) || defined(_INC_WINDOWS)
#error "dsk_kernel must not include windows.h"
#endif
#if defined(_UNISTD_H) || defined(__UNISTD_H__)
#error "dsk_kernel must not include unistd.h"
#endif
#if defined(_SYS_STAT_H) || defined(__SYS_STAT_H__)
#error "dsk_kernel must not include sys/stat.h"
#endif
#if defined(_SYS_TYPES_H) || defined(__SYS_TYPES_H__)
#error "dsk_kernel must not include sys/types.h"
#endif
#endif /* DSK_FORBID_OS_HEADERS */

#endif /* DSK_FORBIDDEN_INCLUDES_H */
