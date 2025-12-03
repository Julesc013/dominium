#ifndef DOM_CORE_TYPES_H
#define DOM_CORE_TYPES_H

/* C89-friendly integer aliases (long long used as an extension for 64-bit) */
typedef unsigned char      dom_u8;
typedef signed   char      dom_i8;
typedef unsigned short     dom_u16;
typedef signed   short     dom_i16;
typedef unsigned int       dom_u32;
typedef signed   int       dom_i32;
typedef unsigned long long dom_u64;
typedef signed   long long dom_i64;

typedef dom_u8 dom_bool8; /* 0/1 */

/* Fixed-point simulation types */
typedef dom_i32 dom_q16_16;
typedef dom_i64 dom_q32_32;

/* Generic error/result code */
typedef dom_i32 dom_err_t;

/* Compile-time assertion (C89-compatible) */
#define DOM_STATIC_ASSERT(cond, name) typedef char dom_static_assert_##name[(cond) ? 1 : -1]

#endif /* DOM_CORE_TYPES_H */
