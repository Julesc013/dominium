#include "dom_instance.h"

#include <cstdio>
#include <cstring>
#include <vector>

extern "C" {
#include "domino/sys.h"
}

namespace dom {

namespace {

enum {
    TAG_INSTANCE_ID            = 1u,
    TAG_WORLD_SEED             = 2u,
    TAG_WORLD_SIZE_M           = 3u,
    TAG_VERTICAL_MIN_M         = 4u,
    TAG_VERTICAL_MAX_M         = 5u,
    TAG_SUITE_VERSION          = 6u,
    TAG_CORE_VERSION           = 7u,
    TAG_PACK_ENTRY             = 20u,
    TAG_MOD_ENTRY              = 21u,
    TAG_LAST_PRODUCT           = 30u,
    TAG_LAST_PRODUCT_VERSION   = 31u
};

static bool read_file(const std::string &path, std::vector<unsigned char> &out) {
    void *fh;
    long size;
    size_t read_len;

    fh = dsys_file_open(path.c_str(), "rb");
    if (!fh) {
        return false;
    }

    if (dsys_file_seek(fh, 0L, SEEK_END) != 0) {
        dsys_file_close(fh);
        return false;
    }
    size = dsys_file_tell(fh);
    if (size <= 0L) {
        dsys_file_close(fh);
        return false;
    }
    if (dsys_file_seek(fh, 0L, SEEK_SET) != 0) {
        dsys_file_close(fh);
        return false;
    }

    out.resize(static_cast<size_t>(size));
    read_len = dsys_file_read(fh, &out[0], static_cast<size_t>(size));
    dsys_file_close(fh);
    if (read_len != static_cast<size_t>(size)) {
        out.clear();
        return false;
    }
    return true;
}

static bool write_file(const std::string &path, const std::vector<unsigned char> &data) {
    void *fh;
    size_t wrote;
    fh = dsys_file_open(path.c_str(), "wb");
    if (!fh) {
        return false;
    }
    wrote = 0u;
    if (!data.empty()) {
        wrote = dsys_file_write(fh, &data[0], data.size());
    }
    dsys_file_close(fh);
    return wrote == data.size();
}

static void append_tlv(std::vector<unsigned char> &out, unsigned tag,
                       const unsigned char *payload, unsigned payload_len) {
    size_t base = out.size();
    out.resize(base + 8u + payload_len);
    std::memcpy(&out[base], &tag, sizeof(unsigned));
    std::memcpy(&out[base + 4u], &payload_len, sizeof(unsigned));
    if (payload_len > 0u && payload) {
        std::memcpy(&out[base + 8u], payload, payload_len);
    }
}

static void append_u32(std::vector<unsigned char> &out, unsigned tag, unsigned value) {
    append_tlv(out, tag, reinterpret_cast<const unsigned char *>(&value), sizeof(unsigned));
}

static void append_s32(std::vector<unsigned char> &out, unsigned tag, int value) {
    append_tlv(out, tag, reinterpret_cast<const unsigned char *>(&value), sizeof(int));
}

static void append_string(std::vector<unsigned char> &out, unsigned tag, const std::string &value) {
    if (value.empty()) {
        append_tlv(out, tag, (const unsigned char *)0, 0u);
        return;
    }
    append_tlv(out, tag, reinterpret_cast<const unsigned char *>(value.c_str()),
               static_cast<unsigned>(value.size() + 1u)); /* include null terminator */
}

static void append_pack_ref(std::vector<unsigned char> &out, unsigned tag,
                            const std::string &id, unsigned version) {
    std::vector<unsigned char> payload;
    payload.resize(4u + id.size() + 1u);
    std::memcpy(&payload[0], &version, sizeof(unsigned));
    if (!id.empty()) {
        std::memcpy(&payload[4u], id.c_str(), id.size());
    }
    payload[payload.size() - 1u] = '\0';
    append_tlv(out, tag, &payload[0], static_cast<unsigned>(payload.size()));
}

static std::string string_from_payload(const unsigned char *ptr, unsigned len) {
    if (!ptr || len == 0u) {
        return std::string();
    }
    /* Drop trailing nulls to stay deterministic across encoders. */
    while (len > 0u && ptr[len - 1u] == '\0') {
        --len;
    }
    return std::string(reinterpret_cast<const char *>(ptr), reinterpret_cast<const char *>(ptr) + len);
}

static void parse_pack_ref(std::vector<PackRef> &out,
                           const unsigned char *ptr, unsigned len) {
    PackRef ref;
    if (!ptr || len < sizeof(unsigned)) {
        return;
    }
    std::memcpy(&ref.version, ptr, sizeof(unsigned));
    ref.id = string_from_payload(ptr + sizeof(unsigned), len - static_cast<unsigned>(sizeof(unsigned)));
    out.push_back(ref);
}

static void parse_mod_ref(std::vector<ModRef> &out,
                          const unsigned char *ptr, unsigned len) {
    ModRef ref;
    if (!ptr || len < sizeof(unsigned)) {
        return;
    }
    std::memcpy(&ref.version, ptr, sizeof(unsigned));
    ref.id = string_from_payload(ptr + sizeof(unsigned), len - static_cast<unsigned>(sizeof(unsigned)));
    out.push_back(ref);
}

static std::string instance_file_path(const Paths &paths, const std::string &id) {
    std::string inst_dir = join(paths.instances, id);
    return join(inst_dir, "instance.tlv");
}

} // namespace

bool InstanceInfo::load(const Paths &paths) {
    std::vector<unsigned char> data;
    size_t offset;
    const std::string path = instance_file_path(paths, id);
    if (id.empty()) {
        return false;
    }
    if (!read_file(path, data)) {
        return false;
    }

    packs.clear();
    mods.clear();
    world_seed = 0u;
    world_size_m = 0u;
    vertical_min_m = 0;
    vertical_max_m = 0;
    suite_version = 0u;
    core_version = 0u;
    last_product.clear();
    last_product_version.clear();

    offset = 0u;
    while (offset + 8u <= data.size()) {
        unsigned tag;
        unsigned len;
        std::memcpy(&tag, &data[offset], sizeof(unsigned));
        std::memcpy(&len, &data[offset + 4u], sizeof(unsigned));
        offset += 8u;
        if (len > data.size() - offset) {
            break;
        }

        const unsigned char *payload = &data[offset];
        switch (tag) {
        case TAG_INSTANCE_ID:
            id = string_from_payload(payload, len);
            break;
        case TAG_WORLD_SEED:
            if (len >= sizeof(unsigned)) {
                std::memcpy(&world_seed, payload, sizeof(unsigned));
            }
            break;
        case TAG_WORLD_SIZE_M:
            if (len >= sizeof(unsigned)) {
                std::memcpy(&world_size_m, payload, sizeof(unsigned));
            }
            break;
        case TAG_VERTICAL_MIN_M:
            if (len >= sizeof(int)) {
                std::memcpy(&vertical_min_m, payload, sizeof(int));
            }
            break;
        case TAG_VERTICAL_MAX_M:
            if (len >= sizeof(int)) {
                std::memcpy(&vertical_max_m, payload, sizeof(int));
            }
            break;
        case TAG_SUITE_VERSION:
            if (len >= sizeof(unsigned)) {
                std::memcpy(&suite_version, payload, sizeof(unsigned));
            }
            break;
        case TAG_CORE_VERSION:
            if (len >= sizeof(unsigned)) {
                std::memcpy(&core_version, payload, sizeof(unsigned));
            }
            break;
        case TAG_PACK_ENTRY:
            parse_pack_ref(packs, payload, len);
            break;
        case TAG_MOD_ENTRY:
            parse_mod_ref(mods, payload, len);
            break;
        case TAG_LAST_PRODUCT:
            last_product = string_from_payload(payload, len);
            break;
        case TAG_LAST_PRODUCT_VERSION:
            last_product_version = string_from_payload(payload, len);
            break;
        default:
            /* Unknown tag: skip for forward compatibility. */
            break;
        }
        offset += len;
    }

    return true;
}

bool InstanceInfo::save(const Paths &paths) const {
    std::vector<unsigned char> data;
    size_t i;
    const std::string path = instance_file_path(paths, id);
    if (id.empty()) {
        return false;
    }

    append_string(data, TAG_INSTANCE_ID, id);
    append_u32(data, TAG_WORLD_SEED, world_seed);
    append_u32(data, TAG_WORLD_SIZE_M, world_size_m);
    append_s32(data, TAG_VERTICAL_MIN_M, vertical_min_m);
    append_s32(data, TAG_VERTICAL_MAX_M, vertical_max_m);
    append_u32(data, TAG_SUITE_VERSION, suite_version);
    append_u32(data, TAG_CORE_VERSION, core_version);

    for (i = 0u; i < packs.size(); ++i) {
        append_pack_ref(data, TAG_PACK_ENTRY, packs[i].id, packs[i].version);
    }
    for (i = 0u; i < mods.size(); ++i) {
        append_pack_ref(data, TAG_MOD_ENTRY, mods[i].id, mods[i].version);
    }

    append_string(data, TAG_LAST_PRODUCT, last_product);
    append_string(data, TAG_LAST_PRODUCT_VERSION, last_product_version);

    return write_file(path, data);
}

} // namespace dom
