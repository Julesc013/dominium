#include "dsk/dsk_contracts.h"

#include <algorithm>

static dsk_status_t dsk_state_error(dsk_u16 code, dsk_u16 subcode) {
    return dsk_error_make(DSK_DOMAIN_KERNEL, code, subcode, DSK_ERROR_FLAG_USER_ACTIONABLE);
}

void dsk_installed_state_clear(dsk_installed_state_t *state) {
    if (!state) {
        return;
    }
    state->product_id.clear();
    state->installed_version.clear();
    state->selected_splat.clear();
    state->install_scope = 0u;
    state->install_root.clear();
    state->installed_components.clear();
    state->manifest_digest64 = 0u;
    state->request_digest64 = 0u;
}

static bool dsk_string_less(const std::string &a, const std::string &b) {
    return a < b;
}

dsk_status_t dsk_installed_state_write(const dsk_installed_state_t *state,
                                       dsk_tlv_buffer_t *out_buf) {
    dsk_tlv_builder_t *builder;
    dsk_status_t st;
    std::vector<std::string> components;
    dsk_u32 i;

    if (!state || !out_buf) {
        return dsk_state_error(DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE);
    }

    builder = dsk_tlv_builder_create();
    if (!builder) {
        return dsk_state_error(DSK_CODE_INTERNAL_ERROR, DSK_SUBCODE_NONE);
    }

    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_STATE_PRODUCT_ID, state->product_id.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_STATE_INSTALLED_VERSION, state->installed_version.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_STATE_SELECTED_SPLAT, state->selected_splat.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u16(builder, DSK_TLV_TAG_STATE_INSTALL_SCOPE, state->install_scope);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_string(builder, DSK_TLV_TAG_STATE_INSTALL_ROOT, state->install_root.c_str());
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_STATE_MANIFEST_DIGEST64, state->manifest_digest64);
    if (!dsk_error_is_ok(st)) goto done;
    st = dsk_tlv_builder_add_u64(builder, DSK_TLV_TAG_STATE_REQUEST_DIGEST64, state->request_digest64);
    if (!dsk_error_is_ok(st)) goto done;

    components = state->installed_components;
    std::sort(components.begin(), components.end(), dsk_string_less);
    if (!components.empty()) {
        dsk_tlv_builder_t *list_builder = dsk_tlv_builder_create();
        dsk_tlv_buffer_t list_payload;
        for (i = 0u; i < components.size(); ++i) {
            dsk_tlv_builder_add_string(list_builder, DSK_TLV_TAG_STATE_COMPONENT_ENTRY, components[i].c_str());
        }
        st = dsk_tlv_builder_finalize_payload(list_builder, &list_payload);
        dsk_tlv_builder_destroy(list_builder);
        if (!dsk_error_is_ok(st)) goto done;
        st = dsk_tlv_builder_add_container(builder,
                                           DSK_TLV_TAG_STATE_INSTALLED_COMPONENTS,
                                           list_payload.data,
                                           list_payload.size);
        dsk_tlv_buffer_free(&list_payload);
        if (!dsk_error_is_ok(st)) goto done;
    }

    st = dsk_tlv_builder_finalize(builder, out_buf);

done:
    dsk_tlv_builder_destroy(builder);
    return st;
}
