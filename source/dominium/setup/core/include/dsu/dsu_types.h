/*
FILE: source/dominium/setup/core/include/dsu/dsu_types.h
MODULE: Dominium Setup
PURPOSE: Baseline C89/C++98 types and status codes for the Setup Core ABI.
*/
#ifndef DSU_TYPES_H_INCLUDED
#define DSU_TYPES_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

/* Export macro (static library by default). */
#if defined(_WIN32) || defined(__CYGWIN__)
# if defined(DSU_BUILD_DLL)
#  define DSU_API __declspec(dllexport)
# elif defined(DSU_USE_DLL)
#  define DSU_API __declspec(dllimport)
# else
#  define DSU_API
# endif
#else
# define DSU_API
#endif

/* Fixed-width integer types (C89-visible; does not include <stdint.h>). */
#if defined(_MSC_VER)
typedef signed __int8 dsu_i8;
typedef unsigned __int8 dsu_u8;
typedef signed __int16 dsu_i16;
typedef unsigned __int16 dsu_u16;
typedef signed __int32 dsu_i32;
typedef unsigned __int32 dsu_u32;
typedef signed __int64 dsu_i64;
typedef unsigned __int64 dsu_u64;
#elif defined(__clang__) || defined(__GNUC__)
typedef __INT8_TYPE__ dsu_i8;
typedef __UINT8_TYPE__ dsu_u8;
typedef __INT16_TYPE__ dsu_i16;
typedef __UINT16_TYPE__ dsu_u16;
typedef __INT32_TYPE__ dsu_i32;
typedef __UINT32_TYPE__ dsu_u32;
typedef __INT64_TYPE__ dsu_i64;
typedef __UINT64_TYPE__ dsu_u64;
#else
typedef signed char dsu_i8;
typedef unsigned char dsu_u8;
typedef signed short dsu_i16;
typedef unsigned short dsu_u16;
typedef signed long dsu_i32;
typedef unsigned long dsu_u32;
# error "dsu_types.h: no known 64-bit integer type for this toolchain"
#endif

typedef int dsu_bool;
#define DSU_TRUE 1
#define DSU_FALSE 0

typedef enum dsu_status_t {
    DSU_STATUS_SUCCESS = 0,
    DSU_STATUS_INVALID_ARGS = 1,
    DSU_STATUS_IO_ERROR = 2,
    DSU_STATUS_PARSE_ERROR = 3,
    DSU_STATUS_UNSUPPORTED_VERSION = 4,
    DSU_STATUS_INTEGRITY_ERROR = 5,
    DSU_STATUS_INTERNAL_ERROR = 6,

    /* Resolution-specific failures (Plan S-3). */
    DSU_STATUS_MISSING_COMPONENT = 100,
    DSU_STATUS_UNSATISFIED_DEPENDENCY = 101,
    DSU_STATUS_VERSION_CONFLICT = 102,
    DSU_STATUS_EXPLICIT_CONFLICT = 103,
    DSU_STATUS_PLATFORM_INCOMPATIBLE = 104,
    DSU_STATUS_ILLEGAL_DOWNGRADE = 105,
    DSU_STATUS_INVALID_REQUEST = 106
} dsu_status_t;

#define DSU_OK DSU_STATUS_SUCCESS

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_TYPES_H_INCLUDED */
