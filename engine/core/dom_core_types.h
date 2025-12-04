#ifndef DOM_CORE_TYPES_H
#define DOM_CORE_TYPES_H

/* C89-friendly integer aliases (long long used as an extension for 64-bit) */
typedef unsigned char      dom_u8;
typedef signed   char      dom_i8;
typedef unsigned short     dom_u16;
typedef signed   short     dom_i16;
typedef unsigned int       dom_u32;
typedef signed   int       dom_i32;
/* 64-bit integers: prefer compiler-specific types to stay C89-compatible. */
#if defined(_MSC_VER)
typedef unsigned __int64 dom_u64;
typedef signed   __int64 dom_i64;
#else
#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wlong-long"
#endif
typedef unsigned long long dom_u64;
typedef signed   long long dom_i64;
#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif
#endif

typedef dom_u8 dom_bool8; /* 0/1 */

/* Fixed-point simulation types */
typedef dom_i32 dom_q16_16;
typedef dom_i64 dom_q32_32;

/* Generic error/result code */
typedef dom_i32 dom_err_t;

/* Compile-time assertion (C89-compatible) */
#define DOM_STATIC_ASSERT(cond, name) typedef char dom_static_assert_##name[(cond) ? 1 : -1]

#endif /* DOM_CORE_TYPES_H */
