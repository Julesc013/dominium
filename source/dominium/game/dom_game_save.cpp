#include "dom_game_save.h"

#include <vector>
#include <cstdlib>
#include <cstring>

extern "C" {
#include "domino/sys.h"
#include "sim/d_sim_hash.h"
}

namespace dom {

namespace {

enum {
    TAG_INSTANCE = 1u,
    TAG_CHUNK    = 2u
};

static void free_blob(d_tlv_blob &blob);

static bool write_block(void *fh, const unsigned char *data, size_t len) {
    if (!fh) {
        return false;
    }
    if (len == 0u) {
        return true;
    }
    return dsys_file_write(fh, data, len) == len;
}

static bool build_save_blob(d_world *world, std::vector<unsigned char> &out) {
    d_tlv_blob inst_blob;
    u32 i;

    if (!world) {
        return false;
    }

    out.clear();
    inst_blob.ptr = (unsigned char *)0;
    inst_blob.len = 0u;

    if (d_serialize_save_instance_all(world, &inst_blob) != 0) {
        return false;
    }

    {
        const u32 tag_instance = TAG_INSTANCE;
        const u32 inst_len = inst_blob.len;
        const size_t base = out.size();
        out.resize(base + 8u + static_cast<size_t>(inst_blob.len));
        std::memcpy(&out[base], &tag_instance, sizeof(u32));
        std::memcpy(&out[base + 4u], &inst_len, sizeof(u32));
        if (inst_blob.len > 0u) {
            std::memcpy(&out[base + 8u], inst_blob.ptr, inst_blob.len);
        }
    }

    for (i = 0u; i < world->chunk_count; ++i) {
        d_chunk *chunk = &world->chunks[i];
        d_tlv_blob chunk_blob;
        u32 chunk_tag = TAG_CHUNK;
        u32 payload_len;
        i32 cx = chunk->cx;
        i32 cy = chunk->cy;
        u32 chunk_id = chunk->chunk_id;
        u32 flags = (u32)chunk->flags;

        chunk_blob.ptr = (unsigned char *)0;
        chunk_blob.len = 0u;
        if (d_serialize_save_chunk_all(world, chunk, &chunk_blob) != 0) {
            free_blob(inst_blob);
            return false;
        }

        payload_len = (u32)(sizeof(cx) + sizeof(cy) + sizeof(chunk_id) + sizeof(flags) + chunk_blob.len);
        {
            const size_t base = out.size();
            out.resize(base + 8u + static_cast<size_t>(payload_len));
            std::memcpy(&out[base], &chunk_tag, sizeof(u32));
            std::memcpy(&out[base + 4u], &payload_len, sizeof(u32));
            std::memcpy(&out[base + 8u], &cx, sizeof(cx));
            std::memcpy(&out[base + 8u + sizeof(cx)], &cy, sizeof(cy));
            std::memcpy(&out[base + 8u + sizeof(cx) + sizeof(cy)], &chunk_id, sizeof(chunk_id));
            std::memcpy(&out[base + 8u + sizeof(cx) + sizeof(cy) + sizeof(chunk_id)], &flags, sizeof(flags));
            if (chunk_blob.len > 0u) {
                std::memcpy(&out[base + 8u + sizeof(cx) + sizeof(cy) + sizeof(chunk_id) + sizeof(flags)],
                            chunk_blob.ptr, chunk_blob.len);
            }
        }

        free_blob(chunk_blob);
    }

    free_blob(inst_blob);
    return true;
}

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

static void free_blob(d_tlv_blob &blob) {
    if (blob.ptr) {
        free(blob.ptr);
        blob.ptr = (unsigned char *)0;
        blob.len = 0u;
    }
}

static bool verify_save_hash(d_world *world, const std::string &path) {
    d_world *tmp;
    d_world_hash h0;
    d_world_hash h1;
    if (!world) {
        return false;
    }
    tmp = d_world_create(&world->meta);
    if (!tmp) {
        return false;
    }
    if (!game_load_world(tmp, path)) {
        d_world_destroy(tmp);
        return false;
    }
    h0 = d_sim_hash_world(world);
    h1 = d_sim_hash_world(tmp);
    d_world_destroy(tmp);
    if (h0 != h1) {
        ::printf("Save verify: hash mismatch (0x%016llx vs 0x%016llx)\n",
         (unsigned long long)h0,
         (unsigned long long)h1);

        return false;
    }
    return true;
}

} // namespace

bool game_save_world_blob(
    d_world                       *world,
    std::vector<unsigned char>    &out
) {
    return build_save_blob(world, out);
}

bool game_load_world_blob(
    d_world                  *world,
    const unsigned char      *data,
    size_t                    size
) {
    u32 offset;

    if (!world || (!data && size > 0u)) {
        return false;
    }

    offset = 0u;
    while (offset + 8u <= size) {
        u32 tag;
        u32 len;

        std::memcpy(&tag, data + offset, sizeof(u32));
        std::memcpy(&len, data + offset + 4u, sizeof(u32));
        offset += 8u;
        if (len > size - offset) {
            return false;
        }

        if (tag == TAG_INSTANCE) {
            d_tlv_blob blob;
            blob.ptr = const_cast<unsigned char *>(data + offset);
            blob.len = len;
            if (d_serialize_load_instance_all(world, &blob) != 0) {
                return false;
            }
        } else if (tag == TAG_CHUNK) {
            d_tlv_blob chunk_blob;
            d_chunk *chunk;
            const size_t meta_size = sizeof(i32) + sizeof(i32) + sizeof(u32) + sizeof(u32);
            i32 cx = 0;
            i32 cy = 0;
            u32 chunk_id = 0u;
            u32 flags = 0u;

            if (len < meta_size) {
                return false;
            }
            std::memcpy(&cx, data + offset, sizeof(i32));
            std::memcpy(&cy, data + offset + sizeof(i32), sizeof(i32));
            std::memcpy(&chunk_id, data + offset + sizeof(i32) * 2, sizeof(u32));
            std::memcpy(&flags, data + offset + sizeof(i32) * 2 + sizeof(u32), sizeof(u32));

            chunk = d_world_get_or_create_chunk(world, cx, cy);
            if (!chunk) {
                return false;
            }
            chunk->chunk_id = chunk_id;
            chunk->flags = (u16)flags;

            chunk_blob.ptr = const_cast<unsigned char *>(data + offset + meta_size);
            chunk_blob.len = len - (u32)meta_size;
            if (d_serialize_load_chunk_all(world, chunk, &chunk_blob) != 0) {
                return false;
            }
        }

        offset += len;
    }

    return offset == size;
}

bool game_save_world(
    d_world             *world,
    const std::string   &path
) {
    void *fh;
    std::vector<unsigned char> blob;

    if (!world || path.empty()) {
        return false;
    }
    if (!build_save_blob(world, blob)) {
        return false;
    }

    fh = dsys_file_open(path.c_str(), "wb");
    if (!fh) {
        return false;
    }
    if (!write_block(fh, &blob[0], blob.size())) {
        dsys_file_close(fh);
        return false;
    }
    dsys_file_close(fh);
    if (!verify_save_hash(world, path)) {
        return false;
    }
    return true;
}

bool game_load_world(
    d_world             *world,
    const std::string   &path
) {
    std::vector<unsigned char> data;

    if (!world || path.empty()) {
        return false;
    }
    if (!read_file(path, data)) {
        return false;
    }
    return game_load_world_blob(world,
                               data.empty() ? (const unsigned char *)0 : &data[0],
                               data.size());
}

} // namespace dom
