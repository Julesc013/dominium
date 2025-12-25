/*
FILE: tools/dist_seed/dist_seed_state.c
MODULE: Dominium build tooling
PURPOSE: Generate a minimal DSU installed_state.dsustate for dist seeding.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct buf_t {
    unsigned char *data;
    unsigned long len;
    unsigned long cap;
} buf_t;

static void buf_free(buf_t *b) {
    if (!b) {
        return;
    }
    free(b->data);
    b->data = NULL;
    b->len = 0ul;
    b->cap = 0ul;
}

static int buf_reserve(buf_t *b, unsigned long add) {
    unsigned long need;
    unsigned long new_cap;
    unsigned char *p;
    if (!b) {
        return 0;
    }
    if (add == 0ul) {
        return 1;
    }
    need = b->len + add;
    if (need < b->len) {
        return 0;
    }
    if (need <= b->cap) {
        return 1;
    }
    new_cap = (b->cap == 0ul) ? 256ul : b->cap;
    while (new_cap < need) {
        if (new_cap > 0x7FFFFFFFul) {
            new_cap = need;
            break;
        }
        new_cap *= 2ul;
    }
    p = (unsigned char *)realloc(b->data, (size_t)new_cap);
    if (!p) {
        return 0;
    }
    b->data = p;
    b->cap = new_cap;
    return 1;
}

static int buf_append(buf_t *b, const void *bytes, unsigned long n) {
    if (!b) {
        return 0;
    }
    if (n == 0ul) {
        return 1;
    }
    if (!bytes) {
        return 0;
    }
    if (!buf_reserve(b, n)) {
        return 0;
    }
    memcpy(b->data + b->len, bytes, (size_t)n);
    b->len += n;
    return 1;
}

static int buf_put_u16le(buf_t *b, unsigned short v) {
    unsigned char tmp[2];
    tmp[0] = (unsigned char)(v & 0xFFu);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFu);
    return buf_append(b, tmp, 2ul);
}

static int buf_put_u32le(buf_t *b, unsigned long v) {
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFul);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFul);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFul);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFul);
    return buf_append(b, tmp, 4ul);
}

static int buf_put_u64le_zero(buf_t *b) {
    unsigned char tmp[8];
    memset(tmp, 0, sizeof(tmp));
    return buf_append(b, tmp, 8ul);
}

static int buf_put_tlv(buf_t *b, unsigned short type, const void *payload, unsigned long payload_len) {
    if (!buf_put_u16le(b, type)) {
        return 0;
    }
    if (!buf_put_u32le(b, payload_len)) {
        return 0;
    }
    return buf_append(b, payload, payload_len);
}

static int buf_put_tlv_u32(buf_t *b, unsigned short type, unsigned long v) {
    unsigned char tmp[4];
    tmp[0] = (unsigned char)(v & 0xFFul);
    tmp[1] = (unsigned char)((v >> 8) & 0xFFul);
    tmp[2] = (unsigned char)((v >> 16) & 0xFFul);
    tmp[3] = (unsigned char)((v >> 24) & 0xFFul);
    return buf_put_tlv(b, type, tmp, 4ul);
}

static int buf_put_tlv_u8(buf_t *b, unsigned short type, unsigned char v) {
    return buf_put_tlv(b, type, &v, 1ul);
}

static int buf_put_tlv_u64_zero(buf_t *b, unsigned short type) {
    unsigned char tmp[8];
    memset(tmp, 0, sizeof(tmp));
    return buf_put_tlv(b, type, tmp, 8ul);
}

static int buf_put_tlv_str(buf_t *b, unsigned short type, const char *s) {
    unsigned long n;
    if (!s) {
        s = "";
    }
    n = (unsigned long)strlen(s);
    return buf_put_tlv(b, type, s, n);
}

static unsigned long header_checksum32_base(const unsigned char hdr[20]) {
    unsigned long sum = 0ul;
    unsigned long i;
    for (i = 0ul; i < 16ul; ++i) {
        sum += (unsigned long)hdr[i];
    }
    return sum;
}

static int wrap_file(buf_t *out_file, const unsigned char magic[4], unsigned short version, const buf_t *payload) {
    unsigned char hdr[20];
    unsigned long checksum;
    if (!out_file || !magic || !payload) {
        return 0;
    }
    memset(out_file, 0, sizeof(*out_file));
    memset(hdr, 0, sizeof(hdr));
    hdr[0] = magic[0];
    hdr[1] = magic[1];
    hdr[2] = magic[2];
    hdr[3] = magic[3];
    hdr[4] = (unsigned char)(version & 0xFFu);
    hdr[5] = (unsigned char)((version >> 8) & 0xFFu);
    hdr[6] = 0xFEu;
    hdr[7] = 0xFFu;
    hdr[8] = 20u;
    hdr[9] = 0u;
    hdr[10] = 0u;
    hdr[11] = 0u;
    hdr[12] = (unsigned char)(payload->len & 0xFFul);
    hdr[13] = (unsigned char)((payload->len >> 8) & 0xFFul);
    hdr[14] = (unsigned char)((payload->len >> 16) & 0xFFul);
    hdr[15] = (unsigned char)((payload->len >> 24) & 0xFFul);
    checksum = header_checksum32_base(hdr);
    hdr[16] = (unsigned char)(checksum & 0xFFul);
    hdr[17] = (unsigned char)((checksum >> 8) & 0xFFul);
    hdr[18] = (unsigned char)((checksum >> 16) & 0xFFul);
    hdr[19] = (unsigned char)((checksum >> 24) & 0xFFul);
    if (!buf_append(out_file, hdr, 20ul)) {
        return 0;
    }
    if (!buf_append(out_file, payload->data, payload->len)) {
        return 0;
    }
    return 1;
}

static int write_bytes_file(const char *path, const unsigned char *bytes, unsigned long len) {
    FILE *f;
    size_t n;
    if (!path || (!bytes && len != 0ul)) {
        return 0;
    }
    f = fopen(path, "wb");
    if (!f) {
        return 0;
    }
    n = (size_t)len;
    if (n != 0u) {
        if (fwrite(bytes, 1u, n, f) != n) {
            fclose(f);
            return 0;
        }
    }
    if (fclose(f) != 0) {
        return 0;
    }
    return 1;
}

static int write_state_file(const char *out_path,
                            const char *install_root,
                            const char *product_id,
                            const char *product_version,
                            const char *build_channel,
                            const char *platform,
                            unsigned char scope) {
    const unsigned short T_ROOT = 0x0001u;
    const unsigned short T_ROOT_VER = 0x0002u;
    const unsigned short T_PRODUCT_ID = 0x0010u;
    const unsigned short T_PRODUCT_VER = 0x0011u;
    const unsigned short T_BUILD_CHANNEL = 0x0012u;
    const unsigned short T_INSTALL_INSTANCE_ID = 0x0013u;
    const unsigned short T_PLATFORM = 0x0020u;
    const unsigned short T_SCOPE = 0x0021u;
    const unsigned short T_INSTALL_ROOT = 0x0022u;
    const unsigned short T_INSTALL_ROOT_ITEM = 0x0023u;
    const unsigned short T_IR_VER = 0x0024u;
    const unsigned short T_IR_ROLE = 0x0025u;
    const unsigned short T_IR_PATH = 0x0026u;
    const unsigned short T_MANIFEST_DIGEST64 = 0x0030u;
    const unsigned short T_RESOLVED_DIGEST64 = 0x0031u;
    const unsigned short T_PLAN_DIGEST64 = 0x0032u;
    const unsigned short T_LAST_OPERATION = 0x0060u;
    const unsigned short T_LAST_JOURNAL_ID = 0x0061u;

    buf_t root;
    buf_t payload;
    buf_t file;
    buf_t ir;
    unsigned char magic[4];

    if (!out_path || !install_root || !product_id || !product_version || !platform) {
        return 0;
    }
    if (product_id[0] == '\0' || product_version[0] == '\0' || install_root[0] == '\0' || platform[0] == '\0') {
        return 0;
    }

    memset(&root, 0, sizeof(root));
    memset(&payload, 0, sizeof(payload));
    memset(&file, 0, sizeof(file));
    memset(&ir, 0, sizeof(ir));
    magic[0] = 'D';
    magic[1] = 'S';
    magic[2] = 'U';
    magic[3] = 'S';

    if (!buf_put_tlv_u32(&root, T_ROOT_VER, 2ul)) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_ID, product_id)) goto fail;
    if (!buf_put_tlv_str(&root, T_PRODUCT_VER, product_version)) goto fail;
    if (!buf_put_tlv_str(&root, T_BUILD_CHANNEL, build_channel ? build_channel : "")) goto fail;
    if (!buf_put_tlv_str(&root, T_PLATFORM, platform)) goto fail;
    if (!buf_put_tlv_u8(&root, T_SCOPE, scope)) goto fail;
    if (!buf_put_tlv_u64_zero(&root, T_INSTALL_INSTANCE_ID)) goto fail;
    if (!buf_put_tlv_str(&root, T_INSTALL_ROOT, install_root)) goto fail;
    if (!buf_put_tlv_u64_zero(&root, T_MANIFEST_DIGEST64)) goto fail;
    if (!buf_put_tlv_u64_zero(&root, T_RESOLVED_DIGEST64)) goto fail;
    if (!buf_put_tlv_u64_zero(&root, T_PLAN_DIGEST64)) goto fail;
    if (!buf_put_tlv_u8(&root, T_LAST_OPERATION, 0u)) goto fail;
    if (!buf_put_tlv_u64_zero(&root, T_LAST_JOURNAL_ID)) goto fail;

    if (!buf_put_tlv_u32(&ir, T_IR_VER, 1ul)) goto fail;
    if (!buf_put_tlv_u8(&ir, T_IR_ROLE, 0u)) goto fail;
    if (!buf_put_tlv_str(&ir, T_IR_PATH, install_root)) goto fail;
    if (!buf_put_tlv(&root, T_INSTALL_ROOT_ITEM, ir.data, ir.len)) goto fail;

    if (!buf_put_tlv(&payload, T_ROOT, root.data, root.len)) goto fail;
    if (!wrap_file(&file, magic, 2u, &payload)) goto fail;

    if (!write_bytes_file(out_path, file.data, file.len)) goto fail;

    buf_free(&root);
    buf_free(&payload);
    buf_free(&file);
    buf_free(&ir);
    return 1;

fail:
    buf_free(&root);
    buf_free(&payload);
    buf_free(&file);
    buf_free(&ir);
    return 0;
}

static void print_usage(const char *exe) {
    const char *name = exe ? exe : "dominium-dist-seed";
    fprintf(stderr,
            "usage: %s --out <path> --install-root <path> --product-id <id> --product-version <ver> --platform <triple> [--build-channel <name>] [--scope <0|1|2>]\n",
            name);
}

static int parse_u8(const char *s, unsigned char *out) {
    unsigned long v;
    char *end = NULL;
    if (!s || !out) {
        return 0;
    }
    v = strtoul(s, &end, 10);
    if (!end || *end != '\0' || v > 255ul) {
        return 0;
    }
    *out = (unsigned char)v;
    return 1;
}

int main(int argc, char **argv) {
    const char *out_path = NULL;
    const char *install_root = NULL;
    const char *product_id = "dominium";
    const char *product_version = "0.0.0";
    const char *build_channel = "dev";
    const char *platform = "any-any";
    unsigned char scope = 0u;
    int i;

    for (i = 1; i < argc; ++i) {
        const char *arg = argv[i];
        if (!arg) {
            continue;
        }
        if (strncmp(arg, "--out=", 6) == 0) {
            out_path = arg + 6;
        } else if (strcmp(arg, "--out") == 0 && (i + 1) < argc) {
            out_path = argv[++i];
        } else if (strncmp(arg, "--install-root=", 15) == 0) {
            install_root = arg + 15;
        } else if (strcmp(arg, "--install-root") == 0 && (i + 1) < argc) {
            install_root = argv[++i];
        } else if (strncmp(arg, "--product-id=", 13) == 0) {
            product_id = arg + 13;
        } else if (strcmp(arg, "--product-id") == 0 && (i + 1) < argc) {
            product_id = argv[++i];
        } else if (strncmp(arg, "--product-version=", 18) == 0) {
            product_version = arg + 18;
        } else if (strcmp(arg, "--product-version") == 0 && (i + 1) < argc) {
            product_version = argv[++i];
        } else if (strncmp(arg, "--build-channel=", 16) == 0) {
            build_channel = arg + 16;
        } else if (strcmp(arg, "--build-channel") == 0 && (i + 1) < argc) {
            build_channel = argv[++i];
        } else if (strncmp(arg, "--platform=", 11) == 0) {
            platform = arg + 11;
        } else if (strcmp(arg, "--platform") == 0 && (i + 1) < argc) {
            platform = argv[++i];
        } else if (strncmp(arg, "--scope=", 8) == 0) {
            if (!parse_u8(arg + 8, &scope)) {
                print_usage(argv[0]);
                return 2;
            }
        } else if (strcmp(arg, "--scope") == 0 && (i + 1) < argc) {
            if (!parse_u8(argv[++i], &scope)) {
                print_usage(argv[0]);
                return 2;
            }
        } else if (strcmp(arg, "--help") == 0 || strcmp(arg, "-h") == 0) {
            print_usage(argv[0]);
            return 0;
        } else {
            print_usage(argv[0]);
            return 2;
        }
    }

    if (!out_path || !install_root) {
        print_usage(argv[0]);
        return 2;
    }

    if (!write_state_file(out_path,
                          install_root,
                          product_id,
                          product_version,
                          build_channel,
                          platform,
                          scope)) {
        fprintf(stderr, "dist seed: failed to write %s\n", out_path);
        return 1;
    }
    return 0;
}
