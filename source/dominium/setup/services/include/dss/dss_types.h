#ifndef DSS_TYPES_H
#define DSS_TYPES_H

#include "dsk/dsk_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Export macro (static library by default). */
#if defined(_WIN32) || defined(__CYGWIN__)
# if defined(DSS_BUILD_DLL)
#  define DSS_API __declspec(dllexport)
# elif defined(DSS_USE_DLL)
#  define DSS_API __declspec(dllimport)
# else
#  define DSS_API
# endif
#else
# define DSS_API
#endif

typedef dsk_i8 dss_i8;
typedef dsk_u8 dss_u8;
typedef dsk_i16 dss_i16;
typedef dsk_u16 dss_u16;
typedef dsk_i32 dss_i32;
typedef dsk_u32 dss_u32;
typedef dsk_i64 dss_i64;
typedef dsk_u64 dss_u64;

typedef dsk_bool dss_bool;
#define DSS_TRUE DSK_TRUE
#define DSS_FALSE DSK_FALSE

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSS_TYPES_H */
