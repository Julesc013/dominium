#include <stdio.h>
#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/rng.h"

static u32 checksum_u32(const u32* data, u32 count) {
    u32 hash = 2166136261u; /* FNV-like start */
    u32 i;
    for (i = 0; i < count; ++i) {
        hash ^= data[i];
        hash *= 16777619u;
    }
    return hash;
}

static u32 test_rng(void) {
    d_rng_state rng;
    u32 seq[16];
    u32 i;
    d_rng_seed(&rng, 12345u);
    for (i = 0; i < 16; ++i) {
        seq[i] = d_rng_next_u32(&rng);
    }
    return checksum_u32(seq, 16);
}

static u32 test_q16_16(void) {
    q16_16 a = d_q16_16_from_int(3);
    q16_16 b = d_q16_16_from_int(-2);
    q16_16 c = d_q16_16_mul(a, b); /* -6.0 */
    q16_16 d = d_q16_16_div(c, d_q16_16_from_int(3)); /* -2.0 */

    u32 vals[4];
    vals[0] = (u32)a;
    vals[1] = (u32)b;
    vals[2] = (u32)c;
    vals[3] = (u32)d;
    return checksum_u32(vals, 4);
}

static u32 test_q4_12(void) {
    q4_12 a = d_q4_12_from_int(1);
    q4_12 b = d_q4_12_from_int(2);
    q4_12 c = d_q4_12_mul(a, b); /* 2.0 */
    q4_12 d = d_q4_12_sub(c, d_q4_12_from_int(3)); /* -1.0 */

    u32 vals[4];
    vals[0] = (u32)a;
    vals[1] = (u32)b;
    vals[2] = (u32)c;
    vals[3] = (u32)d;
    return checksum_u32(vals, 4);
}

static u32 test_q24_8(void) {
    q24_8 a = d_q24_8_from_int(123);
    q24_8 b = d_q24_8_from_int(-45);
    q24_8 c = d_q24_8_add(a, b);
    q24_8 d = d_q24_8_mul(c, d_q24_8_from_int(2));

    u32 vals[4];
    vals[0] = (u32)a;
    vals[1] = (u32)b;
    vals[2] = (u32)c;
    vals[3] = (u32)d;
    return checksum_u32(vals, 4);
}

static u32 test_q48_16(void) {
    q48_16 a = d_q48_16_from_int(1000000);  /* 1e6 */
    q48_16 b = d_q48_16_from_int(-3);
    q48_16 c = d_q48_16_mul(a, b);          /* -3e6 */
    q48_16 d = d_q48_16_div(c, d_q48_16_from_int(2)); /* -1.5e6 */

    u32 vals[8];
    vals[0] = (u32)(a & 0xFFFFFFFFu);
    vals[1] = (u32)(a >> 32);
    vals[2] = (u32)(b & 0xFFFFFFFFu);
    vals[3] = (u32)(b >> 32);
    vals[4] = (u32)(c & 0xFFFFFFFFu);
    vals[5] = (u32)(c >> 32);
    vals[6] = (u32)(d & 0xFFFFFFFFu);
    vals[7] = (u32)(d >> 32);
    return checksum_u32(vals, 8);
}

int main(void) {
    u32 rng_hash = test_rng();
    u32 q16_hash = test_q16_16();
    u32 q4_hash = test_q4_12();
    u32 q24_hash = test_q24_8();
    u32 q48_hash = test_q48_16();

    printf("domino_numeric_test:\n");
    printf("  rng_hash  = %08X\n", (unsigned int)rng_hash);
    printf("  q16_hash  = %08X\n", (unsigned int)q16_hash);
    printf("  q4_hash   = %08X\n", (unsigned int)q4_hash);
    printf("  q24_hash  = %08X\n", (unsigned int)q24_hash);
    printf("  q48_hash  = %08X\n", (unsigned int)q48_hash);

    return 0;
}
