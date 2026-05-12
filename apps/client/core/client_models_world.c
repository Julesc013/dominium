#include "client_models_world.h"

#include <string.h>

static void copy_text(char* out, size_t cap, const char* value)
{
    if (!out || cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (!value || !value[0]) {
        return;
    }
    strncpy(out, value, cap - 1u);
    out[cap - 1u] = '\0';
}

static int world_index_of(const client_world_model* model, const char* world_id)
{
    u32 i;
    if (!model || !world_id || !world_id[0]) {
        return -1;
    }
    for (i = 0u; i < model->count; ++i) {
        if (strcmp(model->records[i].world_id, world_id) == 0) {
            return (int)i;
        }
    }
    return -1;
}

void client_world_model_init(client_world_model* model)
{
    if (!model) {
        return;
    }
    memset(model, 0, sizeof(*model));
}

int client_world_model_add_or_replace(client_world_model* model, const client_world_record* record)
{
    int idx;
    client_world_record* dst = 0;
    if (!model || !record || !record->world_id[0]) {
        return 0;
    }
    idx = world_index_of(model, record->world_id);
    if (idx >= 0) {
        dst = &model->records[(u32)idx];
    } else {
        if (model->count >= CLIENT_WORLD_MODEL_MAX_RECORDS) {
            return 0;
        }
        dst = &model->records[model->count++];
    }
    memset(dst, 0, sizeof(*dst));
    copy_text(dst->world_id, sizeof(dst->world_id), record->world_id);
    copy_text(dst->metadata_path, sizeof(dst->metadata_path), record->metadata_path);
    copy_text(dst->pack_set_hash, sizeof(dst->pack_set_hash), record->pack_set_hash);
    copy_text(dst->schema_versions, sizeof(dst->schema_versions), record->schema_versions);
    copy_text(dst->last_build_identity, sizeof(dst->last_build_identity), record->last_build_identity);
    return 1;
}

int client_world_model_remove(client_world_model* model, const char* world_id)
{
    int idx;
    u32 i;
    if (!model || !world_id || !world_id[0]) {
        return 0;
    }
    idx = world_index_of(model, world_id);
    if (idx < 0) {
        return 0;
    }
    for (i = (u32)idx; (i + 1u) < model->count; ++i) {
        model->records[i] = model->records[i + 1u];
    }
    model->count -= 1u;
    memset(&model->records[model->count], 0, sizeof(model->records[model->count]));
    return 1;
}

const client_world_record* client_world_model_at(const client_world_model* model, u32 index)
{
    if (!model || index >= model->count) {
        return 0;
    }
    return &model->records[index];
}

u32 client_world_model_count(const client_world_model* model)
{
    return model ? model->count : 0u;
}

u64 client_world_model_digest(const client_world_model* model)
{
    const u64 fnv_offset = 1469598103934665603ull;
    const u64 fnv_prime = 1099511628211ull;
    u64 hash = fnv_offset;
    u32 i;
    const char* fields[5];
    u32 f;
    if (!model) {
        return 0ull;
    }
    for (i = 0u; i < model->count; ++i) {
        fields[0] = model->records[i].world_id;
        fields[1] = model->records[i].metadata_path;
        fields[2] = model->records[i].pack_set_hash;
        fields[3] = model->records[i].schema_versions;
        fields[4] = model->records[i].last_build_identity;
        for (f = 0u; f < 5u; ++f) {
            const unsigned char* p = (const unsigned char*)fields[f];
            while (p && *p) {
                hash ^= (u64)(*p++);
                hash *= fnv_prime;
            }
            hash ^= (u64)0xffu;
            hash *= fnv_prime;
        }
    }
    return hash;
}
