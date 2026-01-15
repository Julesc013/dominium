/*
FILE: source/dominium/setup/core/src/util/dsu_util_sha256.c
MODULE: Dominium Setup
PURPOSE: SHA-256 implementation for payload/file hashing (Plan S-4).
*/
#include "dsu_util_internal.h"

#include <stdio.h>
#include <string.h>

typedef struct dsu__sha256_ctx_t {
    dsu_u32 h[8];
    dsu_u32 len_hi;
    dsu_u32 len_lo;
    dsu_u8 buf[64];
    dsu_u32 buf_len;
} dsu__sha256_ctx_t;

static dsu_u32 dsu__rotr32(dsu_u32 x, dsu_u32 n) { return (x >> n) | (x << (32u - n)); }
static dsu_u32 dsu__ch(dsu_u32 x, dsu_u32 y, dsu_u32 z) { return (x & y) ^ (~x & z); }
static dsu_u32 dsu__maj(dsu_u32 x, dsu_u32 y, dsu_u32 z) { return (x & y) ^ (x & z) ^ (y & z); }
static dsu_u32 dsu__bsig0(dsu_u32 x) { return dsu__rotr32(x, 2u) ^ dsu__rotr32(x, 13u) ^ dsu__rotr32(x, 22u); }
static dsu_u32 dsu__bsig1(dsu_u32 x) { return dsu__rotr32(x, 6u) ^ dsu__rotr32(x, 11u) ^ dsu__rotr32(x, 25u); }
static dsu_u32 dsu__ssig0(dsu_u32 x) { return dsu__rotr32(x, 7u) ^ dsu__rotr32(x, 18u) ^ (x >> 3u); }
static dsu_u32 dsu__ssig1(dsu_u32 x) { return dsu__rotr32(x, 17u) ^ dsu__rotr32(x, 19u) ^ (x >> 10u); }

static void dsu__sha256_init(dsu__sha256_ctx_t *c) {
    if (!c) return;
    c->h[0] = 0x6a09e667u;
    c->h[1] = 0xbb67ae85u;
    c->h[2] = 0x3c6ef372u;
    c->h[3] = 0xa54ff53au;
    c->h[4] = 0x510e527fu;
    c->h[5] = 0x9b05688cu;
    c->h[6] = 0x1f83d9abu;
    c->h[7] = 0x5be0cd19u;
    c->len_hi = 0u;
    c->len_lo = 0u;
    c->buf_len = 0u;
}

static void dsu__sha256_len_add(dsu__sha256_ctx_t *c, dsu_u32 bytes) {
    dsu_u32 bits = bytes << 3;
    dsu_u32 lo = c->len_lo;
    c->len_lo += bits;
    if (c->len_lo < lo) {
        c->len_hi += 1u;
    }
    c->len_hi += (bytes >> 29);
}

static void dsu__sha256_transform(dsu__sha256_ctx_t *c, const dsu_u8 block[64]) {
    static const dsu_u32 K[64] = {
        0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,
        0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,
        0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
        0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,
        0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,
        0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
        0x19a4c116u,0x1e376c08u,0x2748774cu,0x34b0bcb5u,0x391c0cb3u,0x4ed8aa4au,0x5b9cca4fu,0x682e6ff3u,
        0x748f82eeu,0x78a5636fu,0x84c87814u,0x8cc70208u,0x90befffau,0xa4506cebu,0xbef9a3f7u,0xc67178f2u
    };
    dsu_u32 w[64];
    dsu_u32 a, b, c0, d, e, f, g, h;
    dsu_u32 i;

    for (i = 0u; i < 16u; ++i) {
        dsu_u32 j = i * 4u;
        w[i] = ((dsu_u32)block[j] << 24)
             | ((dsu_u32)block[j + 1u] << 16)
             | ((dsu_u32)block[j + 2u] << 8)
             | (dsu_u32)block[j + 3u];
    }
    for (i = 16u; i < 64u; ++i) {
        w[i] = dsu__ssig1(w[i - 2u]) + w[i - 7u] + dsu__ssig0(w[i - 15u]) + w[i - 16u];
    }

    a = c->h[0];
    b = c->h[1];
    c0 = c->h[2];
    d = c->h[3];
    e = c->h[4];
    f = c->h[5];
    g = c->h[6];
    h = c->h[7];

    for (i = 0u; i < 64u; ++i) {
        dsu_u32 t1 = h + dsu__bsig1(e) + dsu__ch(e, f, g) + K[i] + w[i];
        dsu_u32 t2 = dsu__bsig0(a) + dsu__maj(a, b, c0);
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c0;
        c0 = b;
        b = a;
        a = t1 + t2;
    }

    c->h[0] += a;
    c->h[1] += b;
    c->h[2] += c0;
    c->h[3] += d;
    c->h[4] += e;
    c->h[5] += f;
    c->h[6] += g;
    c->h[7] += h;
}

static void dsu__sha256_update(dsu__sha256_ctx_t *c, const dsu_u8 *data, dsu_u32 len) {
    dsu_u32 i = 0u;
    if (!c || (!data && len != 0u)) return;
    dsu__sha256_len_add(c, len);
    while (i < len) {
        dsu_u32 n = 64u - c->buf_len;
        if (n > (len - i)) n = (len - i);
        memcpy(c->buf + c->buf_len, data + i, (size_t)n);
        c->buf_len += n;
        i += n;
        if (c->buf_len == 64u) {
            dsu__sha256_transform(c, c->buf);
            c->buf_len = 0u;
        }
    }
}

static void dsu__sha256_final(dsu__sha256_ctx_t *c, dsu_u8 out[32]) {
    dsu_u32 i;
    dsu_u32 hi;
    dsu_u32 lo;
    if (!c || !out) return;

    c->buf[c->buf_len++] = 0x80u;
    if (c->buf_len > 56u) {
        while (c->buf_len < 64u) c->buf[c->buf_len++] = 0u;
        dsu__sha256_transform(c, c->buf);
        c->buf_len = 0u;
    }
    while (c->buf_len < 56u) c->buf[c->buf_len++] = 0u;

    hi = c->len_hi;
    lo = c->len_lo;
    c->buf[56] = (dsu_u8)((hi >> 24) & 0xFFu);
    c->buf[57] = (dsu_u8)((hi >> 16) & 0xFFu);
    c->buf[58] = (dsu_u8)((hi >> 8) & 0xFFu);
    c->buf[59] = (dsu_u8)(hi & 0xFFu);
    c->buf[60] = (dsu_u8)((lo >> 24) & 0xFFu);
    c->buf[61] = (dsu_u8)((lo >> 16) & 0xFFu);
    c->buf[62] = (dsu_u8)((lo >> 8) & 0xFFu);
    c->buf[63] = (dsu_u8)(lo & 0xFFu);
    dsu__sha256_transform(c, c->buf);

    for (i = 0u; i < 8u; ++i) {
        out[i * 4u + 0u] = (dsu_u8)((c->h[i] >> 24) & 0xFFu);
        out[i * 4u + 1u] = (dsu_u8)((c->h[i] >> 16) & 0xFFu);
        out[i * 4u + 2u] = (dsu_u8)((c->h[i] >> 8) & 0xFFu);
        out[i * 4u + 3u] = (dsu_u8)(c->h[i] & 0xFFu);
    }
}

dsu_status_t dsu__sha256_file(const char *path, dsu_u8 out_sha256[32]) {
    FILE *f;
    unsigned char buf[32768];
    size_t n;
    dsu__sha256_ctx_t c;

    if (!path || !out_sha256) {
        return DSU_STATUS_INVALID_ARGS;
    }
    f = fopen(path, "rb");
    if (!f) {
        return DSU_STATUS_IO_ERROR;
    }
    dsu__sha256_init(&c);
    while ((n = fread(buf, 1u, sizeof(buf), f)) != 0u) {
        dsu__sha256_update(&c, (const dsu_u8 *)buf, (dsu_u32)n);
    }
    if (ferror(f)) {
        fclose(f);
        return DSU_STATUS_IO_ERROR;
    }
    if (fclose(f) != 0) {
        return DSU_STATUS_IO_ERROR;
    }
    dsu__sha256_final(&c, out_sha256);
    return DSU_STATUS_SUCCESS;
}

