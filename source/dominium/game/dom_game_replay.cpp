#include "dom_game_replay.h"

#include <vector>
#include <cstdlib>
#include <cstring>

extern "C" {
#include "domino/sys.h"
}

namespace dom {

namespace {

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

static bool write_file(const std::string &path, const unsigned char *data, size_t len) {
    void *fh;
    size_t wrote;
    if (path.empty()) {
        return false;
    }
    fh = dsys_file_open(path.c_str(), "wb");
    if (!fh) {
        return false;
    }
    wrote = dsys_file_write(fh, data, len);
    dsys_file_close(fh);
    return wrote == len;
}

} // namespace

bool game_save_replay(const d_replay_context *ctx, const std::string &path) {
    d_tlv_blob blob;
    if (!ctx || path.empty()) {
        return false;
    }
    blob.ptr = (unsigned char *)0;
    blob.len = 0u;
    if (d_replay_serialize(ctx, &blob) != 0) {
        return false;
    }
    if (!blob.ptr || blob.len == 0u) {
        return false;
    }
    {
        const bool ok = write_file(path, blob.ptr, (size_t)blob.len);
        std::free(blob.ptr);
        blob.ptr = (unsigned char *)0;
        blob.len = 0u;
        return ok;
    }
}

bool game_load_replay(const std::string &path, d_replay_context *out_ctx) {
    std::vector<unsigned char> data;
    d_tlv_blob blob;
    if (path.empty() || !out_ctx) {
        return false;
    }
    if (!read_file(path, data)) {
        return false;
    }
    if (data.empty()) {
        return false;
    }
    blob.ptr = &data[0];
    blob.len = static_cast<u32>(data.size());
    return d_replay_deserialize(&blob, out_ctx) == 0;
}

u32 game_replay_last_tick(const d_replay_context *ctx) {
    u32 i;
    u32 max_tick = 0u;
    if (!ctx || !ctx->frames) {
        return 0u;
    }
    for (i = 0u; i < ctx->frame_count; ++i) {
        if (ctx->frames[i].tick_index > max_tick) {
            max_tick = ctx->frames[i].tick_index;
        }
    }
    return max_tick;
}

} // namespace dom

