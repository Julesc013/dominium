/*
FILE: source/dominium/launcher/core/src/artifact/launcher_sha256.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / sha256
RESPONSIBILITY: Implements SHA-256 for artifact store verification (no OS headers).
*/

#include "launcher_sha256.h"

#include <cstring>

namespace dom {
namespace launcher_core {

namespace {

typedef struct Sha256Ctx {
    u32 h[8];
    u64 total_len;
    u32 buf_len;
    unsigned char buf[64];
} Sha256Ctx;

static const launcher_fs_api_v1* get_fs(const launcher_services_api_v1* services) {
    void* iface = 0;
    if (!services || !services->query_interface) {
        return 0;
    }
    if (services->query_interface(LAUNCHER_IID_FS_V1, &iface) != 0) {
        return 0;
    }
    return (const launcher_fs_api_v1*)iface;
}

static u32 rotr32(u32 x, u32 n) {
    return (u32)((x >> n) | (x << (32u - n)));
}

static u32 ch(u32 x, u32 y, u32 z) {
    return (u32)((x & y) ^ ((~x) & z));
}

static u32 maj(u32 x, u32 y, u32 z) {
    return (u32)((x & y) ^ (x & z) ^ (y & z));
}

static u32 bsig0(u32 x) {
    return (u32)(rotr32(x, 2u) ^ rotr32(x, 13u) ^ rotr32(x, 22u));
}

static u32 bsig1(u32 x) {
    return (u32)(rotr32(x, 6u) ^ rotr32(x, 11u) ^ rotr32(x, 25u));
}

static u32 ssig0(u32 x) {
    return (u32)(rotr32(x, 7u) ^ rotr32(x, 18u) ^ (x >> 3u));
}

static u32 ssig1(u32 x) {
    return (u32)(rotr32(x, 17u) ^ rotr32(x, 19u) ^ (x >> 10u));
}

static u32 read_be_u32(const unsigned char* p) {
    return (u32)(((u32)p[0] << 24u) | ((u32)p[1] << 16u) | ((u32)p[2] << 8u) | ((u32)p[3]));
}

static void write_be_u32(unsigned char* out, u32 v) {
    out[0] = (unsigned char)((v >> 24u) & 0xFFu);
    out[1] = (unsigned char)((v >> 16u) & 0xFFu);
    out[2] = (unsigned char)((v >> 8u) & 0xFFu);
    out[3] = (unsigned char)(v & 0xFFu);
}

static void sha256_init(Sha256Ctx& c) {
    c.h[0] = 0x6a09e667u;
    c.h[1] = 0xbb67ae85u;
    c.h[2] = 0x3c6ef372u;
    c.h[3] = 0xa54ff53au;
    c.h[4] = 0x510e527fu;
    c.h[5] = 0x9b05688cu;
    c.h[6] = 0x1f83d9abu;
    c.h[7] = 0x5be0cd19u;
    c.total_len = 0ull;
    c.buf_len = 0u;
    std::memset(c.buf, 0, sizeof(c.buf));
}

static void sha256_compress(Sha256Ctx& c, const unsigned char block[64]) {
    static const u32 k[64] = {
        0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u, 0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
        0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u, 0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
        0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu, 0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
        0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u, 0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
        0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u, 0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
        0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u, 0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
        0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u, 0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
        0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u, 0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u
    };
    u32 w[64];
    u32 a, b, cc, d, e, f, g, h;
    u32 t1, t2;
    int i;

    for (i = 0; i < 16; ++i) {
        w[i] = read_be_u32(block + (size_t)(i * 4));
    }
    for (i = 16; i < 64; ++i) {
        w[i] = (u32)(ssig1(w[i - 2]) + w[i - 7] + ssig0(w[i - 15]) + w[i - 16]);
    }

    a = c.h[0];
    b = c.h[1];
    cc = c.h[2];
    d = c.h[3];
    e = c.h[4];
    f = c.h[5];
    g = c.h[6];
    h = c.h[7];

    for (i = 0; i < 64; ++i) {
        t1 = (u32)(h + bsig1(e) + ch(e, f, g) + k[i] + w[i]);
        t2 = (u32)(bsig0(a) + maj(a, b, cc));
        h = g;
        g = f;
        f = e;
        e = (u32)(d + t1);
        d = cc;
        cc = b;
        b = a;
        a = (u32)(t1 + t2);
    }

    c.h[0] = (u32)(c.h[0] + a);
    c.h[1] = (u32)(c.h[1] + b);
    c.h[2] = (u32)(c.h[2] + cc);
    c.h[3] = (u32)(c.h[3] + d);
    c.h[4] = (u32)(c.h[4] + e);
    c.h[5] = (u32)(c.h[5] + f);
    c.h[6] = (u32)(c.h[6] + g);
    c.h[7] = (u32)(c.h[7] + h);
}

static void sha256_update(Sha256Ctx& c, const unsigned char* data, size_t len) {
    size_t i = 0u;
    if (!data || len == 0u) {
        return;
    }

    c.total_len += (u64)len;

    if (c.buf_len > 0u) {
        while (i < len && c.buf_len < 64u) {
            c.buf[c.buf_len++] = data[i++];
        }
        if (c.buf_len == 64u) {
            sha256_compress(c, c.buf);
            c.buf_len = 0u;
        }
    }

    while (i + 64u <= len) {
        sha256_compress(c, data + i);
        i += 64u;
    }

    while (i < len) {
        c.buf[c.buf_len++] = data[i++];
    }
}

static void sha256_final(Sha256Ctx& c, unsigned char out[32]) {
    unsigned char pad[128];
    size_t pad_len;
    u64 bit_len = (u64)(c.total_len * 8ull);
    unsigned char len_be[8];
    size_t i;

    std::memset(pad, 0, sizeof(pad));
    pad[0] = 0x80u;

    if (c.buf_len < 56u) {
        pad_len = (size_t)(56u - c.buf_len);
    } else {
        pad_len = (size_t)(64u + 56u - c.buf_len);
    }

    /* length is appended as big-endian u64 */
    for (i = 0u; i < 8u; ++i) {
        len_be[7u - i] = (unsigned char)((bit_len >> (u64)(i * 8u)) & 0xFFull);
    }

    sha256_update(c, pad, pad_len);
    sha256_update(c, len_be, 8u);

    for (i = 0u; i < 8u; ++i) {
        write_be_u32(out + (i * 4u), c.h[i]);
    }
}

} /* namespace */

void launcher_sha256_bytes(const unsigned char* data,
                           size_t size,
                           unsigned char out_hash[LAUNCHER_SHA256_BYTES]) {
    Sha256Ctx c;
    if (!out_hash) {
        return;
    }
    sha256_init(c);
    sha256_update(c, data, size);
    sha256_final(c, out_hash);
}

bool launcher_sha256_file(const launcher_services_api_v1* services,
                          const std::string& path,
                          std::vector<unsigned char>& out_hash_bytes,
                          u64& out_size_bytes) {
    const launcher_fs_api_v1* fs = get_fs(services);
    void* fh;
    unsigned char buf[8192];
    size_t got;
    Sha256Ctx c;

    out_hash_bytes.clear();
    out_size_bytes = 0ull;
    if (!fs || !fs->file_open || !fs->file_read || !fs->file_close) {
        return false;
    }
    fh = fs->file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }

    sha256_init(c);
    for (;;) {
        got = fs->file_read(fh, buf, sizeof(buf));
        if (got == 0u) {
            break;
        }
        out_size_bytes += (u64)got;
        sha256_update(c, buf, got);
    }

    (void)fs->file_close(fh);

    out_hash_bytes.resize(LAUNCHER_SHA256_BYTES);
    sha256_final(c, &out_hash_bytes[0]);
    return true;
}

} /* namespace launcher_core */
} /* namespace dom */

