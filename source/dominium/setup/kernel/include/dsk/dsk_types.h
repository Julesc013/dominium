#ifndef DSK_TYPES_H
#define DSK_TYPES_H

#include "dsk_forbidden_includes.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Export macro (static library by default). */
#if defined(_WIN32) || defined(__CYGWIN__)
# if defined(DSK_BUILD_DLL)
#  define DSK_API __declspec(dllexport)
# elif defined(DSK_USE_DLL)
#  define DSK_API __declspec(dllimport)
# else
#  define DSK_API
# endif
#else
# define DSK_API
#endif

/* Fixed-width integer types (C89/C++98-friendly). */
#if defined(_MSC_VER)
typedef signed __int8 dsk_i8;
typedef unsigned __int8 dsk_u8;
typedef signed __int16 dsk_i16;
typedef unsigned __int16 dsk_u16;
typedef signed __int32 dsk_i32;
typedef unsigned __int32 dsk_u32;
typedef signed __int64 dsk_i64;
typedef unsigned __int64 dsk_u64;
#elif defined(__clang__) || defined(__GNUC__)
typedef __INT8_TYPE__ dsk_i8;
typedef __UINT8_TYPE__ dsk_u8;
typedef __INT16_TYPE__ dsk_i16;
typedef __UINT16_TYPE__ dsk_u16;
typedef __INT32_TYPE__ dsk_i32;
typedef __UINT32_TYPE__ dsk_u32;
typedef __INT64_TYPE__ dsk_i64;
typedef __UINT64_TYPE__ dsk_u64;
#else
typedef signed char dsk_i8;
typedef unsigned char dsk_u8;
typedef signed short dsk_i16;
typedef unsigned short dsk_u16;
typedef signed long dsk_i32;
typedef unsigned long dsk_u32;
# error "dsk_types.h: no known 64-bit integer type for this toolchain"
#endif

typedef int dsk_bool;
#define DSK_TRUE 1
#define DSK_FALSE 0

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSK_TYPES_H */
