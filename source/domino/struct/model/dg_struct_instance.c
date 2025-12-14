/* STRUCT instance authoring model (C89). */
#include "struct/model/dg_struct_instance.h"

#include <stdlib.h>
#include <string.h>

static int dg_struct_u64_array_reserve(u64 **arr, u32 *cap, u32 needed) {
    u64 *p;
    u32 new_cap;
    if (!arr || !cap) return -1;
    if (needed <= *cap) return 0;
    new_cap = (*cap) ? (*cap) : 4u;
    while (new_cap < needed) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = needed;
            break;
        }
        new_cap *= 2u;
    }
    p = (u64 *)realloc(*arr, sizeof(u64) * (size_t)new_cap);
    if (!p) return -2;
    *arr = p;
    *cap = new_cap;
    return 0;
}

static u32 dg_struct_u64_array_lower_bound(const u64 *arr, u32 count, u64 v) {
    u32 lo = 0u;
    u32 hi = count;
    u32 mid;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (arr[mid] >= v) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static int dg_struct_u64_array_insert_unique(u64 **arr, u32 *count, u32 *cap, u64 v) {
    u32 idx;
    if (!arr || !count || !cap) return -1;
    if (v == 0u) return -2;
    idx = dg_struct_u64_array_lower_bound(*arr, *count, v);
    if (idx < *count && (*arr)[idx] == v) return 0;
    if (dg_struct_u64_array_reserve(arr, cap, (*count) + 1u) != 0) return -3;
    if (idx < *count) {
        memmove(&(*arr)[idx + 1u], &(*arr)[idx], sizeof(u64) * (size_t)((*count) - idx));
    }
    (*arr)[idx] = v;
    *count += 1u;
    return 0;
}

void dg_struct_instance_init(dg_struct_instance *s) {
    if (!s) return;
    memset(s, 0, sizeof(*s));
    dg_anchor_clear(&s->anchor);
    s->local_pose = dg_pose_identity();
}

void dg_struct_instance_free(dg_struct_instance *s) {
    if (!s) return;
    if (s->volume_ids) free(s->volume_ids);
    if (s->enclosure_ids) free(s->enclosure_ids);
    if (s->surface_template_ids) free(s->surface_template_ids);
    if (s->socket_ids) free(s->socket_ids);
    if (s->carrier_intent_ids) free(s->carrier_intent_ids);
    if (s->overrides.ptr) free(s->overrides.ptr);
    dg_struct_instance_init(s);
}

void dg_struct_instance_clear(dg_struct_instance *s) {
    dg_struct_instance_free(s);
}

int dg_struct_instance_set_overrides_copy(dg_struct_instance *s, const unsigned char *bytes, u32 len) {
    unsigned char *buf;
    if (!s) return -1;
    if (s->overrides.ptr) {
        free(s->overrides.ptr);
        s->overrides.ptr = (unsigned char *)0;
        s->overrides.len = 0u;
    }
    if (!bytes || len == 0u) return 0;
    buf = (unsigned char *)malloc((size_t)len);
    if (!buf) return -2;
    memcpy(buf, bytes, (size_t)len);
    s->overrides.ptr = buf;
    s->overrides.len = len;
    return 0;
}

int dg_struct_instance_add_volume(dg_struct_instance *s, dg_struct_volume_id volume_id) {
    if (!s) return -1;
    return dg_struct_u64_array_insert_unique(
        (u64 **)&s->volume_ids, &s->volume_count, &s->volume_capacity, (u64)volume_id
    );
}

int dg_struct_instance_add_enclosure(dg_struct_instance *s, dg_struct_enclosure_id enclosure_id) {
    if (!s) return -1;
    return dg_struct_u64_array_insert_unique(
        (u64 **)&s->enclosure_ids, &s->enclosure_count, &s->enclosure_capacity, (u64)enclosure_id
    );
}

int dg_struct_instance_add_surface_template(dg_struct_instance *s, dg_struct_surface_template_id surface_template_id) {
    if (!s) return -1;
    return dg_struct_u64_array_insert_unique(
        (u64 **)&s->surface_template_ids, &s->surface_template_count, &s->surface_template_capacity, (u64)surface_template_id
    );
}

int dg_struct_instance_add_socket(dg_struct_instance *s, dg_struct_socket_id socket_id) {
    if (!s) return -1;
    return dg_struct_u64_array_insert_unique(
        (u64 **)&s->socket_ids, &s->socket_count, &s->socket_capacity, (u64)socket_id
    );
}

int dg_struct_instance_add_carrier_intent(dg_struct_instance *s, dg_struct_carrier_intent_id carrier_intent_id) {
    if (!s) return -1;
    return dg_struct_u64_array_insert_unique(
        (u64 **)&s->carrier_intent_ids, &s->carrier_intent_count, &s->carrier_intent_capacity, (u64)carrier_intent_id
    );
}

int dg_struct_instance_validate(const dg_struct_instance *s) {
    u32 i;
    if (!s) return -1;
    if (s->id == 0u) return -2;
    if (s->footprint_id == 0u) return -3;
    if (s->volume_count == 0u) return -4;

    for (i = 1u; i < s->volume_count; ++i) {
        if (s->volume_ids[i - 1u] >= s->volume_ids[i]) return -10;
    }
    for (i = 1u; i < s->enclosure_count; ++i) {
        if (s->enclosure_ids[i - 1u] >= s->enclosure_ids[i]) return -11;
    }
    for (i = 1u; i < s->surface_template_count; ++i) {
        if (s->surface_template_ids[i - 1u] >= s->surface_template_ids[i]) return -12;
    }
    for (i = 1u; i < s->socket_count; ++i) {
        if (s->socket_ids[i - 1u] >= s->socket_ids[i]) return -13;
    }
    for (i = 1u; i < s->carrier_intent_count; ++i) {
        if (s->carrier_intent_ids[i - 1u] >= s->carrier_intent_ids[i]) return -14;
    }

    return 0;
}

