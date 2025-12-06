#ifndef DOM_CORE_TYPES_H
#define DOM_CORE_TYPES_H

#include <stddef.h>

typedef unsigned char      u8;
typedef signed char        i8;
typedef unsigned short     u16;
typedef signed short       i16;
typedef unsigned int       u32;
typedef signed int         i32;

#if defined(_MSC_VER)
typedef unsigned __int64   u64;
typedef signed __int64     i64;
#else
typedef unsigned long long u64;
typedef signed long long   i64;
#endif

typedef int b32;
#define TRUE 1
#define FALSE 0

#endif /* DOM_CORE_TYPES_H */
