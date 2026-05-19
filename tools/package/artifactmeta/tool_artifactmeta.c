/*
Artifact metadata generator (sidecar JSON).
*/
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "domino/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include "dom_contracts/version.h"

#include <errno.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DOM_META_SCHEMA_VERSION 1
#define DOM_META_SIDECAR_HASH_BASIS "json_without_sidecar_sha256"

typedef struct dom_sha256_ctx {
    u32 h[8];
    u64 total_len;
    u32 buf_len;
    unsigned char buf[64];
} dom_sha256_ctx;

static u32 dom_sha256_rotr32(u32 x, u32 n)
{
    return (u32)((x >> n) | (x << (32u - n)));
}

static u32 dom_sha256_ch(u32 x, u32 y, u32 z)
{
    return (u32)((x & y) ^ ((~x) & z));
}

static u32 dom_sha256_maj(u32 x, u32 y, u32 z)
{
    return (u32)((x & y) ^ (x & z) ^ (y & z));
}

static u32 dom_sha256_bsig0(u32 x)
{
    return (u32)(dom_sha256_rotr32(x, 2u) ^ dom_sha256_rotr32(x, 13u) ^ dom_sha256_rotr32(x, 22u));
}

static u32 dom_sha256_bsig1(u32 x)
{
    return (u32)(dom_sha256_rotr32(x, 6u) ^ dom_sha256_rotr32(x, 11u) ^ dom_sha256_rotr32(x, 25u));
}

static u32 dom_sha256_ssig0(u32 x)
{
    return (u32)(dom_sha256_rotr32(x, 7u) ^ dom_sha256_rotr32(x, 18u) ^ (x >> 3u));
}

static u32 dom_sha256_ssig1(u32 x)
{
    return (u32)(dom_sha256_rotr32(x, 17u) ^ dom_sha256_rotr32(x, 19u) ^ (x >> 10u));
}

static u32 dom_sha256_read_be_u32(const unsigned char* p)
{
    return (u32)(((u32)p[0] << 24u) | ((u32)p[1] << 16u) | ((u32)p[2] << 8u) | ((u32)p[3]));
}

static void dom_sha256_write_be_u32(unsigned char* out, u32 v)
{
    out[0] = (unsigned char)((v >> 24u) & 0xFFu);
    out[1] = (unsigned char)((v >> 16u) & 0xFFu);
    out[2] = (unsigned char)((v >> 8u) & 0xFFu);
    out[3] = (unsigned char)(v & 0xFFu);
}

static void dom_sha256_init(dom_sha256_ctx* c)
{
    if (!c) {
        return;
    }
    c->h[0] = 0x6a09e667u;
    c->h[1] = 0xbb67ae85u;
    c->h[2] = 0x3c6ef372u;
    c->h[3] = 0xa54ff53au;
    c->h[4] = 0x510e527fu;
    c->h[5] = 0x9b05688cu;
    c->h[6] = 0x1f83d9abu;
    c->h[7] = 0x5be0cd19u;
    c->total_len = 0u;
    c->buf_len = 0u;
    memset(c->buf, 0, sizeof(c->buf));
}

static void dom_sha256_compress(dom_sha256_ctx* c, const unsigned char block[64])
{
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

    if (!c || !block) {
        return;
    }

    for (i = 0; i < 16; ++i) {
        w[i] = dom_sha256_read_be_u32(block + (size_t)(i * 4));
    }
    for (i = 16; i < 64; ++i) {
        w[i] = (u32)(dom_sha256_ssig1(w[i - 2]) + w[i - 7] + dom_sha256_ssig0(w[i - 15]) + w[i - 16]);
    }

    a = c->h[0];
    b = c->h[1];
    cc = c->h[2];
    d = c->h[3];
    e = c->h[4];
    f = c->h[5];
    g = c->h[6];
    h = c->h[7];

    for (i = 0; i < 64; ++i) {
        t1 = (u32)(h + dom_sha256_bsig1(e) + dom_sha256_ch(e, f, g) + k[i] + w[i]);
        t2 = (u32)(dom_sha256_bsig0(a) + dom_sha256_maj(a, b, cc));
        h = g;
        g = f;
        f = e;
        e = (u32)(d + t1);
        d = cc;
        cc = b;
        b = a;
        a = (u32)(t1 + t2);
    }

    c->h[0] = (u32)(c->h[0] + a);
    c->h[1] = (u32)(c->h[1] + b);
    c->h[2] = (u32)(c->h[2] + cc);
    c->h[3] = (u32)(c->h[3] + d);
    c->h[4] = (u32)(c->h[4] + e);
    c->h[5] = (u32)(c->h[5] + f);
    c->h[6] = (u32)(c->h[6] + g);
    c->h[7] = (u32)(c->h[7] + h);
}

static void dom_sha256_update(dom_sha256_ctx* c, const unsigned char* data, size_t len)
{
    size_t i;
    if (!c || !data || len == 0u) {
        return;
    }
    c->total_len += (u64)len;

    i = 0u;
    if (c->buf_len > 0u) {
        while (i < len && c->buf_len < 64u) {
            c->buf[c->buf_len++] = data[i++];
        }
        if (c->buf_len == 64u) {
            dom_sha256_compress(c, c->buf);
            c->buf_len = 0u;
        }
    }

    while (i + 64u <= len) {
        dom_sha256_compress(c, data + i);
        i += 64u;
    }

    while (i < len) {
        c->buf[c->buf_len++] = data[i++];
    }
}

static void dom_sha256_final(dom_sha256_ctx* c, unsigned char out[32])
{
    unsigned char pad[128];
    size_t pad_len;
    u64 bit_len;
    unsigned char len_be[8];
    size_t i;

    if (!c || !out) {
        return;
    }

    bit_len = (u64)(c->total_len * 8u);
    memset(pad, 0, sizeof(pad));
    pad[0] = 0x80u;

    if (c->buf_len < 56u) {
        pad_len = (size_t)(56u - c->buf_len);
    } else {
        pad_len = (size_t)(64u + 56u - c->buf_len);
    }

    for (i = 0u; i < 8u; ++i) {
        len_be[7u - i] = (unsigned char)((bit_len >> (u64)(i * 8u)) & 0xFFu);
    }

    dom_sha256_update(c, pad, pad_len);
    dom_sha256_update(c, len_be, 8u);

    for (i = 0u; i < 8u; ++i) {
        dom_sha256_write_be_u32(out + (i * 4u), c->h[i]);
    }
}

static void dom_sha256_bytes(const unsigned char* data, size_t len, unsigned char out_hash[32])
{
    dom_sha256_ctx c;
    if (!out_hash) {
        return;
    }
    dom_sha256_init(&c);
    if (data && len > 0u) {
        dom_sha256_update(&c, data, len);
    }
    dom_sha256_final(&c, out_hash);
}

static int dom_sha256_file(const char* path, unsigned char out_hash[32], u64* out_size)
{
    FILE* fh;
    unsigned char buf[8192];
    size_t got;
    dom_sha256_ctx c;
    u64 total;

    if (!path || !out_hash || !out_size) {
        return 0;
    }

    fh = fopen(path, "rb");
    if (!fh) {
        return 0;
    }

    dom_sha256_init(&c);
    total = 0u;
    for (;;) {
        got = fread(buf, 1u, sizeof(buf), fh);
        if (got > 0u) {
            dom_sha256_update(&c, buf, got);
            total += (u64)got;
        }
        if (got < sizeof(buf)) {
            if (ferror(fh)) {
                fclose(fh);
                return 0;
            }
            break;
        }
    }
    fclose(fh);

    dom_sha256_final(&c, out_hash);
    *out_size = total;
    return 1;
}

static void dom_sha256_hex(const unsigned char hash[32], char out_hex[65])
{
    static const char* hex = "0123456789abcdef";
    size_t i;
    if (!hash || !out_hex) {
        return;
    }
    for (i = 0u; i < 32u; ++i) {
        out_hex[i * 2u] = hex[(hash[i] >> 4u) & 0xFu];
        out_hex[i * 2u + 1u] = hex[hash[i] & 0xFu];
    }
    out_hex[64] = '\0';
}

typedef struct dom_str_builder {
    char* data;
    size_t len;
    size_t cap;
} dom_str_builder;

static void dom_sb_init(dom_str_builder* sb)
{
    if (!sb) {
        return;
    }
    sb->data = 0;
    sb->len = 0u;
    sb->cap = 0u;
}

static void dom_sb_free(dom_str_builder* sb)
{
    if (!sb) {
        return;
    }
    free(sb->data);
    sb->data = 0;
    sb->len = 0u;
    sb->cap = 0u;
}

static int dom_sb_reserve(dom_str_builder* sb, size_t add)
{
    size_t need;
    size_t new_cap;
    char* next;
    if (!sb) {
        return 0;
    }
    need = sb->len + add + 1u;
    if (need <= sb->cap) {
        return 1;
    }
    new_cap = (sb->cap > 0u) ? sb->cap : 256u;
    while (new_cap < need) {
        new_cap *= 2u;
    }
    next = (char*)realloc(sb->data, new_cap);
    if (!next) {
        return 0;
    }
    sb->data = next;
    sb->cap = new_cap;
    return 1;
}

static int dom_sb_append_n(dom_str_builder* sb, const char* text, size_t len)
{
    if (!sb || !text) {
        return 0;
    }
    if (!dom_sb_reserve(sb, len)) {
        return 0;
    }
    memcpy(sb->data + sb->len, text, len);
    sb->len += len;
    sb->data[sb->len] = '\0';
    return 1;
}

static int dom_sb_append(dom_str_builder* sb, const char* text)
{
    if (!text) {
        return 0;
    }
    return dom_sb_append_n(sb, text, strlen(text));
}

static int dom_sb_appendf(dom_str_builder* sb, const char* fmt, ...)
{
    char stack_buf[256];
    char* heap_buf;
    va_list args;
    int needed;
    int ok;
    if (!sb || !fmt) {
        return 0;
    }
    va_start(args, fmt);
    needed = vsnprintf(stack_buf, sizeof(stack_buf), fmt, args);
    va_end(args);
    if (needed < 0) {
        return 0;
    }
    if ((size_t)needed < sizeof(stack_buf)) {
        return dom_sb_append_n(sb, stack_buf, (size_t)needed);
    }
    heap_buf = (char*)malloc((size_t)needed + 1u);
    if (!heap_buf) {
        return 0;
    }
    va_start(args, fmt);
    vsnprintf(heap_buf, (size_t)needed + 1u, fmt, args);
    va_end(args);
    ok = dom_sb_append_n(sb, heap_buf, (size_t)needed);
    free(heap_buf);
    return ok;
}

static int dom_sb_append_json_string(dom_str_builder* sb, const char* text)
{
    const unsigned char* p;
    if (!sb) {
        return 0;
    }
    if (!dom_sb_append(sb, "\"")) {
        return 0;
    }
    p = (const unsigned char*)(text ? text : "");
    while (*p) {
        unsigned char c = *p++;
        switch (c) {
        case '\\':
            if (!dom_sb_append(sb, "\\\\")) {
                return 0;
            }
            break;
        case '\"':
            if (!dom_sb_append(sb, "\\\"")) {
                return 0;
            }
            break;
        case '\b':
            if (!dom_sb_append(sb, "\\b")) {
                return 0;
            }
            break;
        case '\f':
            if (!dom_sb_append(sb, "\\f")) {
                return 0;
            }
            break;
        case '\n':
            if (!dom_sb_append(sb, "\\n")) {
                return 0;
            }
            break;
        case '\r':
            if (!dom_sb_append(sb, "\\r")) {
                return 0;
            }
            break;
        case '\t':
            if (!dom_sb_append(sb, "\\t")) {
                return 0;
            }
            break;
        default:
            if (c < 0x20u) {
                if (!dom_sb_appendf(sb, "\\u%04x", (unsigned int)c)) {
                    return 0;
                }
            } else {
                char buf[2];
                buf[0] = (char)c;
                buf[1] = '\0';
                if (!dom_sb_append(sb, buf)) {
                    return 0;
                }
            }
            break;
        }
    }
    return dom_sb_append(sb, "\"");
}

static void dom_normalize_path(const char* src, char* dst, size_t cap)
{
    size_t i;
    if (!dst || cap == 0u) {
        return;
    }
    if (!src) {
        dst[0] = '\0';
        return;
    }
    i = 0u;
    while (src[i] && (i + 1u) < cap) {
        char c = src[i];
        dst[i] = (c == '\\') ? '/' : c;
        ++i;
    }
    dst[i] = '\0';
}

static int dom_ascii_ieq(const char* a, const char* b)
{
    unsigned char ca;
    unsigned char cb;
    if (!a || !b) {
        return 0;
    }
    while (*a && *b) {
        ca = (unsigned char)*a++;
        cb = (unsigned char)*b++;
        if (ca >= 'A' && ca <= 'Z') {
            ca = (unsigned char)(ca - 'A' + 'a');
        }
        if (cb >= 'A' && cb <= 'Z') {
            cb = (unsigned char)(cb - 'A' + 'a');
        }
        if (ca != cb) {
            return 0;
        }
    }
    return (*a == '\0' && *b == '\0');
}

static int dom_ascii_ends_with(const char* text, const char* suffix)
{
    size_t len_text;
    size_t len_suffix;
    size_t i;
    if (!text || !suffix) {
        return 0;
    }
    len_text = strlen(text);
    len_suffix = strlen(suffix);
    if (len_suffix == 0u || len_suffix > len_text) {
        return 0;
    }
    for (i = 0u; i < len_suffix; ++i) {
        char a = text[len_text - len_suffix + i];
        char b = suffix[i];
        if (a >= 'A' && a <= 'Z') {
            a = (char)(a - 'A' + 'a');
        }
        if (b >= 'A' && b <= 'Z') {
            b = (char)(b - 'A' + 'a');
        }
        if (a != b) {
            return 0;
        }
    }
    return 1;
}

static void dom_basename_no_ext(const char* path, char* out, size_t cap, char* raw_name, size_t raw_cap)
{
    const char* base;
    const char* slash;
    size_t len;
    if (!out || cap == 0u) {
        return;
    }
    base = path ? path : "";
    slash = strrchr(base, '/');
    if (slash) {
        base = slash + 1;
    }
    slash = strrchr(base, '\\');
    if (slash) {
        base = slash + 1;
    }
    if (raw_name && raw_cap > 0u) {
        strncpy(raw_name, base, raw_cap - 1u);
        raw_name[raw_cap - 1u] = '\0';
    }
    strncpy(out, base, cap - 1u);
    out[cap - 1u] = '\0';
    len = strlen(out);
    if (len > 0u && dom_ascii_ends_with(out, ".exe")) {
        out[len - 4u] = '\0';
    }
}

static const char* dom_infer_product(const char* base_name)
{
    char buf[64];
    size_t i;
    size_t len;
    if (!base_name || !base_name[0]) {
        return "unknown";
    }
    len = strlen(base_name);
    if (len >= sizeof(buf)) {
        len = sizeof(buf) - 1u;
    }
    for (i = 0u; i < len; ++i) {
        char c = base_name[i];
        if (c >= 'A' && c <= 'Z') {
            c = (char)(c - 'A' + 'a');
        }
        buf[i] = c;
    }
    buf[len] = '\0';
    if (strncmp(buf, "dominium-", 9) == 0) {
        memmove(buf, buf + 9, strlen(buf + 9) + 1u);
    } else if (strncmp(buf, "dominium_", 9) == 0) {
        memmove(buf, buf + 9, strlen(buf + 9) + 1u);
    }
    if (dom_ascii_ieq(buf, "client")) {
        return "client";
    }
    if (dom_ascii_ieq(buf, "server")) {
        return "server";
    }
    if (dom_ascii_ieq(buf, "launcher")) {
        return "launcher";
    }
    if (dom_ascii_ieq(buf, "setup")) {
        return "setup";
    }
    if (dom_ascii_ieq(buf, "tools")) {
        return "tools";
    }
    return "unknown";
}

static const char* dom_default_product_version(const char* product)
{
    if (!product) {
        return DOMINIUM_VERSION_SEMVER;
    }
    if (dom_ascii_ieq(product, "client") || dom_ascii_ieq(product, "server")) {
        return DOMINIUM_GAME_VERSION;
    }
    if (dom_ascii_ieq(product, "launcher")) {
        return DOMINIUM_LAUNCHER_VERSION;
    }
    if (dom_ascii_ieq(product, "setup")) {
        return DOMINIUM_SETUP_VERSION;
    }
    if (dom_ascii_ieq(product, "tools")) {
        return DOMINIUM_TOOLS_VERSION;
    }
    return DOMINIUM_VERSION_SEMVER;
}

static const char* dom_default_sku(const char* product)
{
    if (!product || !product[0]) {
        return "unspecified";
    }
    if (dom_ascii_ieq(product, "client")) {
        return "modern_desktop";
    }
    if (dom_ascii_ieq(product, "server")) {
        return "headless_server";
    }
    if (dom_ascii_ieq(product, "launcher")) {
        return "modern_desktop";
    }
    if (dom_ascii_ieq(product, "setup")) {
        return "modern_desktop";
    }
    if (dom_ascii_ieq(product, "tools")) {
        return "devtools";
    }
    return "unspecified";
}

static const char* dom_resolve_sku(const char* product, const char* override_sku)
{
    if (override_sku && override_sku[0]) {
        return override_sku;
    }
    if (DOM_BUILD_SKU[0] && strcmp(DOM_BUILD_SKU, "auto") != 0) {
        return DOM_BUILD_SKU;
    }
    return dom_default_sku(product);
}

static const char* dom_detect_renderer(void)
{
    int count = 0;
    const char* name = "none";
    if (DOM_BACKEND_SOFT) {
        count += 1;
        name = "soft";
    }
    if (DOM_BACKEND_NULL) {
        count += 1;
        name = "null";
    }
    if (DOM_BACKEND_DX9) {
        count += 1;
        name = "dx9";
    }
    if (DOM_BACKEND_DX11) {
        count += 1;
        name = "dx11";
    }
    if (DOM_BACKEND_GL1) {
        count += 1;
        name = "gl1";
    }
    if (DOM_BACKEND_GL2) {
        count += 1;
        name = "gl2";
    }
    if (DOM_BACKEND_VK1) {
        count += 1;
        name = "vk1";
    }
    if (DOM_BACKEND_METAL) {
        count += 1;
        name = "metal";
    }
    if (count > 1) {
        return "multi";
    }
    return name;
}

typedef struct dom_meta_input {
    const char* input_path;
    const char* input_name;
    u64 input_size;
    const char* artifact_sha256;
    const char* product;
    const char* product_version;
    const char* sku;
    const char* os;
    const char* arch;
    const char* renderer;
    const char* config;
    const char* artifact_name;
} dom_meta_input;

static int dom_build_metadata_json(dom_str_builder* sb,
                                   const dom_meta_input* meta,
                                   const char* sidecar_sha256)
{
    int ok = 1;
    if (!sb || !meta) {
        return 0;
    }
    ok = ok && dom_sb_append(sb, "{");
    ok = ok && dom_sb_appendf(sb, "\"schema_version\":%d,", DOM_META_SCHEMA_VERSION);

    ok = ok && dom_sb_append(sb, "\"artifact\":{");
    ok = ok && dom_sb_append(sb, "\"path\":");
    ok = ok && dom_sb_append_json_string(sb, meta->input_path);
    ok = ok && dom_sb_append(sb, ",\"file_name\":");
    ok = ok && dom_sb_append_json_string(sb, meta->input_name);
    ok = ok && dom_sb_appendf(sb, ",\"size\":%llu", (unsigned long long)meta->input_size);
    ok = ok && dom_sb_append(sb, ",\"sha256\":");
    ok = ok && dom_sb_append_json_string(sb, meta->artifact_sha256);
    ok = ok && dom_sb_append(sb, "},");

    ok = ok && dom_sb_append(sb, "\"identity\":{");
    ok = ok && dom_sb_append(sb, "\"product\":");
    ok = ok && dom_sb_append_json_string(sb, meta->product);
    ok = ok && dom_sb_append(sb, ",\"product_version\":");
    ok = ok && dom_sb_append_json_string(sb, meta->product_version);
    ok = ok && dom_sb_appendf(sb, ",\"build_number\":%u", (unsigned int)DOM_BUILD_NUMBER);
    ok = ok && dom_sb_append(sb, ",\"build_id\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_BUILD_ID);
    ok = ok && dom_sb_append(sb, ",\"git_hash\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_GIT_HASH);
    ok = ok && dom_sb_append(sb, ",\"sku\":");
    ok = ok && dom_sb_append_json_string(sb, meta->sku);
    ok = ok && dom_sb_append(sb, ",\"os\":");
    ok = ok && dom_sb_append_json_string(sb, meta->os);
    ok = ok && dom_sb_append(sb, ",\"arch\":");
    ok = ok && dom_sb_append_json_string(sb, meta->arch);
    ok = ok && dom_sb_append(sb, ",\"renderer\":");
    ok = ok && dom_sb_append_json_string(sb, meta->renderer);
    ok = ok && dom_sb_append(sb, ",\"config\":");
    ok = ok && dom_sb_append_json_string(sb, meta->config);
    ok = ok && dom_sb_append(sb, ",\"artifact_name\":");
    ok = ok && dom_sb_append_json_string(sb, meta->artifact_name);
    ok = ok && dom_sb_append(sb, "},");

    ok = ok && dom_sb_append(sb, "\"versions\":{");
    ok = ok && dom_sb_append(sb, "\"engine\":");
    ok = ok && dom_sb_append_json_string(sb, DOMINO_VERSION_STRING);
    ok = ok && dom_sb_append(sb, ",\"game\":");
    ok = ok && dom_sb_append_json_string(sb, DOMINIUM_GAME_VERSION);
    ok = ok && dom_sb_append(sb, "},");

    ok = ok && dom_sb_append(sb, "\"protocols\":{");
    ok = ok && dom_sb_append(sb, "\"law_targets\":");
    ok = ok && dom_sb_append_json_string(sb, "LAW_TARGETS@1.4.0");
    ok = ok && dom_sb_append(sb, ",\"control_caps\":");
    ok = ok && dom_sb_append_json_string(sb, "CONTROL_CAPS@1.0.0");
    ok = ok && dom_sb_append(sb, ",\"authority_tokens\":");
    ok = ok && dom_sb_append_json_string(sb, "AUTHORITY_TOKEN@1.0.0");
    ok = ok && dom_sb_append(sb, "},");

    ok = ok && dom_sb_append(sb, "\"abi\":{");
    ok = ok && dom_sb_appendf(sb, "\"dom_build_info\":%u", (unsigned int)DOM_BUILD_INFO_ABI_VERSION);
    ok = ok && dom_sb_appendf(sb, ",\"dom_caps\":%u", (unsigned int)DOM_CAPS_ABI_VERSION);
    ok = ok && dom_sb_append(sb, "},");

    ok = ok && dom_sb_append(sb, "\"api\":{");
    ok = ok && dom_sb_appendf(sb, "\"dsys\":%u", 1u);
    ok = ok && dom_sb_appendf(sb, ",\"dgfx\":%u", (unsigned int)DGFX_PROTOCOL_VERSION);
    ok = ok && dom_sb_append(sb, "},");

    ok = ok && dom_sb_append(sb, "\"toolchain\":{");
    ok = ok && dom_sb_append(sb, "\"id\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_ID);
    ok = ok && dom_sb_append(sb, ",\"family\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_FAMILY);
    ok = ok && dom_sb_append(sb, ",\"version\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_VERSION);
    ok = ok && dom_sb_append(sb, ",\"stdlib\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_STDLIB);
    ok = ok && dom_sb_append(sb, ",\"runtime\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_RUNTIME);
    ok = ok && dom_sb_append(sb, ",\"link\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_LINK);
    ok = ok && dom_sb_append(sb, ",\"target\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_TARGET);
    ok = ok && dom_sb_append(sb, ",\"os\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_OS);
    ok = ok && dom_sb_append(sb, ",\"arch\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_ARCH);
    ok = ok && dom_sb_append(sb, ",\"os_floor\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_OS_FLOOR);
    ok = ok && dom_sb_append(sb, ",\"config\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_CONFIG);
    ok = ok && dom_sb_append(sb, "},");

    ok = ok && dom_sb_append(sb, "\"dependencies\":{");
    ok = ok && dom_sb_append(sb, "\"packs_required\":[]");
    ok = ok && dom_sb_append(sb, ",\"runtime\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_TOOLCHAIN_RUNTIME);
    ok = ok && dom_sb_append(sb, "},");

    ok = ok && dom_sb_append(sb, "\"hashes\":{");
    ok = ok && dom_sb_append(sb, "\"artifact_sha256\":");
    ok = ok && dom_sb_append_json_string(sb, meta->artifact_sha256);
    ok = ok && dom_sb_append(sb, ",\"sidecar_sha256\":");
    ok = ok && dom_sb_append_json_string(sb, sidecar_sha256 ? sidecar_sha256 : "");
    ok = ok && dom_sb_append(sb, ",\"sidecar_hash_basis\":");
    ok = ok && dom_sb_append_json_string(sb, DOM_META_SIDECAR_HASH_BASIS);
    ok = ok && dom_sb_append(sb, "}");

    ok = ok && dom_sb_append(sb, "}\n");
    return ok;
}

static void print_help(void)
{
    printf("usage: dom_tool_artifactmeta --input <path> --output <path> [options]\n");
    printf("options:\n");
    printf("  --help                   Show this help\n");
    printf("  --format <json>          Output format (json only)\n");
    printf("  --product <name>         Product name (client|server|launcher|setup|tools)\n");
    printf("  --product-version <v>    Product semantic version override\n");
    printf("  --sku <sku>              SKU override\n");
    printf("  --renderer <name>        Renderer field override\n");
    printf("  --os <name>              Target OS token override\n");
    printf("  --arch <name>            Target arch token override\n");
    printf("  --config <name>          Build config override\n");
}

int main(int argc, char** argv)
{
    const char* input = 0;
    const char* output = 0;
    const char* format = "json";
    const char* product_override = 0;
    const char* product_version_override = 0;
    const char* sku_override = 0;
    const char* renderer_override = 0;
    const char* os_override = 0;
    const char* arch_override = 0;
    const char* config_override = 0;
    char input_norm[512];
    char input_base[128];
    char input_raw[128];
    char artifact_name[256];
    unsigned char hash_raw[32];
    char hash_hex[65];
    unsigned char sidecar_raw[32];
    char sidecar_hex[65];
    u64 input_size = 0u;
    const char* product;
    const char* product_version;
    const char* sku;
    const char* renderer;
    const char* os;
    const char* arch;
    const char* config;
    dom_str_builder sb;
    dom_meta_input meta;
    FILE* fh;
    int i;

    for (i = 1; i < argc; ++i) {
        const char* arg = argv[i];
        if (!arg) {
            continue;
        }
        if (strcmp(arg, "--help") == 0 || strcmp(arg, "-h") == 0) {
            print_help();
            return 0;
        }
        if (strncmp(arg, "--input=", 8) == 0) {
            input = arg + 8;
            continue;
        }
        if (strcmp(arg, "--input") == 0 && i + 1 < argc) {
            input = argv[++i];
            continue;
        }
        if (strncmp(arg, "--output=", 9) == 0) {
            output = arg + 9;
            continue;
        }
        if (strcmp(arg, "--output") == 0 && i + 1 < argc) {
            output = argv[++i];
            continue;
        }
        if (strncmp(arg, "--format=", 9) == 0) {
            format = arg + 9;
            continue;
        }
        if (strcmp(arg, "--format") == 0 && i + 1 < argc) {
            format = argv[++i];
            continue;
        }
        if (strncmp(arg, "--product=", 10) == 0) {
            product_override = arg + 10;
            continue;
        }
        if (strcmp(arg, "--product") == 0 && i + 1 < argc) {
            product_override = argv[++i];
            continue;
        }
        if (strncmp(arg, "--product-version=", 18) == 0) {
            product_version_override = arg + 18;
            continue;
        }
        if (strcmp(arg, "--product-version") == 0 && i + 1 < argc) {
            product_version_override = argv[++i];
            continue;
        }
        if (strncmp(arg, "--sku=", 6) == 0) {
            sku_override = arg + 6;
            continue;
        }
        if (strcmp(arg, "--sku") == 0 && i + 1 < argc) {
            sku_override = argv[++i];
            continue;
        }
        if (strncmp(arg, "--renderer=", 11) == 0) {
            renderer_override = arg + 11;
            continue;
        }
        if (strcmp(arg, "--renderer") == 0 && i + 1 < argc) {
            renderer_override = argv[++i];
            continue;
        }
        if (strncmp(arg, "--os=", 5) == 0) {
            os_override = arg + 5;
            continue;
        }
        if (strcmp(arg, "--os") == 0 && i + 1 < argc) {
            os_override = argv[++i];
            continue;
        }
        if (strncmp(arg, "--arch=", 7) == 0) {
            arch_override = arg + 7;
            continue;
        }
        if (strcmp(arg, "--arch") == 0 && i + 1 < argc) {
            arch_override = argv[++i];
            continue;
        }
        if (strncmp(arg, "--config=", 9) == 0) {
            config_override = arg + 9;
            continue;
        }
        if (strcmp(arg, "--config") == 0 && i + 1 < argc) {
            config_override = argv[++i];
            continue;
        }
        fprintf(stderr, "dom_tool_artifactmeta: unknown arg '%s'\n", arg);
        return 2;
    }

    if (!input || !output) {
        print_help();
        return 2;
    }

    if (!format || !format[0] || !dom_ascii_ieq(format, "json")) {
        fprintf(stderr, "dom_tool_artifactmeta: unsupported format '%s'\n", format ? format : "");
        return 2;
    }

    dom_normalize_path(input, input_norm, sizeof(input_norm));
    dom_basename_no_ext(input, input_base, sizeof(input_base), input_raw, sizeof(input_raw));

    product = product_override ? product_override : dom_infer_product(input_base);
    product_version = product_version_override ? product_version_override : dom_default_product_version(product);
    sku = dom_resolve_sku(product, sku_override);
    renderer = renderer_override ? renderer_override : dom_detect_renderer();
    os = os_override ? os_override : DOM_TOOLCHAIN_OS;
    arch = arch_override ? arch_override : DOM_TOOLCHAIN_ARCH;
    config = config_override ? config_override : DOM_TOOLCHAIN_CONFIG;

    if (!dom_sha256_file(input, hash_raw, &input_size)) {
        fprintf(stderr, "dom_tool_artifactmeta: failed to read '%s' (%s)\n", input, strerror(errno));
        return 1;
    }
    dom_sha256_hex(hash_raw, hash_hex);

    if (!product || !product[0]) {
        product = "unknown";
    }
    if (!product_version || !product_version[0]) {
        product_version = "0.0.0";
    }
    if (!sku || !sku[0]) {
        sku = "unspecified";
    }
    if (!renderer || !renderer[0]) {
        renderer = "none";
    }
    if (!os || !os[0]) {
        os = "unknown";
    }
    if (!arch || !arch[0]) {
        arch = "unknown";
    }
    if (!config || !config[0]) {
        config = "unknown";
    }

    snprintf(artifact_name, sizeof(artifact_name),
             "%s-%s+build.%u-%s-%s-%s-%s",
             product,
             product_version,
             (unsigned int)DOM_BUILD_NUMBER,
             os,
             arch,
             renderer,
             config);

    memset(&meta, 0, sizeof(meta));
    meta.input_path = input_norm;
    meta.input_name = input_raw[0] ? input_raw : input_base;
    meta.input_size = input_size;
    meta.artifact_sha256 = hash_hex;
    meta.product = product;
    meta.product_version = product_version;
    meta.sku = sku;
    meta.os = os;
    meta.arch = arch;
    meta.renderer = renderer;
    meta.config = config;
    meta.artifact_name = artifact_name;

    dom_sb_init(&sb);
    if (!dom_build_metadata_json(&sb, &meta, "")) {
        fprintf(stderr, "dom_tool_artifactmeta: metadata build failed\n");
        dom_sb_free(&sb);
        return 1;
    }
    dom_sha256_bytes((const unsigned char*)sb.data, sb.len, sidecar_raw);
    dom_sha256_hex(sidecar_raw, sidecar_hex);
    dom_sb_free(&sb);

    dom_sb_init(&sb);
    if (!dom_build_metadata_json(&sb, &meta, sidecar_hex)) {
        fprintf(stderr, "dom_tool_artifactmeta: metadata build failed\n");
        dom_sb_free(&sb);
        return 1;
    }

    fh = fopen(output, "wb");
    if (!fh) {
        fprintf(stderr, "dom_tool_artifactmeta: failed to open '%s' (%s)\n", output, strerror(errno));
        dom_sb_free(&sb);
        return 1;
    }
    if (sb.len > 0u) {
        if (fwrite(sb.data, 1u, sb.len, fh) != sb.len) {
            fclose(fh);
            fprintf(stderr, "dom_tool_artifactmeta: failed to write '%s'\n", output);
            dom_sb_free(&sb);
            return 1;
        }
    }
    fclose(fh);
    dom_sb_free(&sb);
    return 0;
}
