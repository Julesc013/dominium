#include "client_models_server.h"

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

static int compare_server(const client_server_record* a, const client_server_record* b)
{
    int c;
    c = strcmp(a->server_id, b->server_id);
    if (c != 0) return c;
    c = strcmp(a->provider, b->provider);
    if (c != 0) return c;
    return strcmp(a->address, b->address);
}

static void copy_server(client_server_record* dst, const client_server_record* src)
{
    memset(dst, 0, sizeof(*dst));
    copy_text(dst->provider, sizeof(dst->provider), src->provider);
    copy_text(dst->server_id, sizeof(dst->server_id), src->server_id);
    copy_text(dst->address, sizeof(dst->address), src->address);
    copy_text(dst->protocol_version, sizeof(dst->protocol_version), src->protocol_version);
    copy_text(dst->capability_hash, sizeof(dst->capability_hash), src->capability_hash);
    copy_text(dst->refusal_reason, sizeof(dst->refusal_reason), src->refusal_reason);
}

void client_server_model_init(client_server_model* model)
{
    if (!model) {
        return;
    }
    memset(model, 0, sizeof(*model));
}

int client_server_model_merge(client_server_model* model, const client_server_record* incoming, u32 incoming_count)
{
    u32 i;
    if (!model || !incoming) {
        return 0;
    }
    for (i = 0u; i < incoming_count; ++i) {
        u32 j;
        int replaced = 0;
        if (!incoming[i].server_id[0]) {
            continue;
        }
        for (j = 0u; j < model->count; ++j) {
            if (strcmp(model->records[j].server_id, incoming[i].server_id) == 0 &&
                strcmp(model->records[j].provider, incoming[i].provider) == 0) {
                copy_server(&model->records[j], &incoming[i]);
                replaced = 1;
                break;
            }
        }
        if (!replaced) {
            if (model->count >= CLIENT_SERVER_MODEL_MAX_RECORDS) {
                return 0;
            }
            copy_server(&model->records[model->count++], &incoming[i]);
        }
    }

    /* Stable insertion sort keeps output deterministic across provider merge order. */
    for (i = 1u; i < model->count; ++i) {
        client_server_record key = model->records[i];
        u32 j = i;
        while (j > 0u && compare_server(&model->records[j - 1u], &key) > 0) {
            model->records[j] = model->records[j - 1u];
            j -= 1u;
        }
        model->records[j] = key;
    }
    return 1;
}

const client_server_record* client_server_model_at(const client_server_model* model, u32 index)
{
    if (!model || index >= model->count) {
        return 0;
    }
    return &model->records[index];
}

u32 client_server_model_count(const client_server_model* model)
{
    return model ? model->count : 0u;
}

u64 client_server_model_digest(const client_server_model* model)
{
    const u64 fnv_offset = 1469598103934665603ull;
    const u64 fnv_prime = 1099511628211ull;
    u64 hash = fnv_offset;
    u32 i;
    if (!model) {
        return 0ull;
    }
    for (i = 0u; i < model->count; ++i) {
        const unsigned char* p = (const unsigned char*)model->records[i].server_id;
        while (p && *p) {
            hash ^= (u64)(*p++);
            hash *= fnv_prime;
        }
        p = (const unsigned char*)model->records[i].provider;
        while (p && *p) {
            hash ^= (u64)(*p++);
            hash *= fnv_prime;
        }
        p = (const unsigned char*)model->records[i].address;
        while (p && *p) {
            hash ^= (u64)(*p++);
            hash *= fnv_prime;
        }
        hash ^= 0xffu;
        hash *= fnv_prime;
    }
    return hash;
}
