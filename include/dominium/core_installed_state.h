/*
FILE: include/dominium/core_installed_state.h
MODULE: Dominium
PURPOSE: Shared installed_state.tlv schema + helpers (setup -> launcher handoff).
*/
#ifndef DOMINIUM_CORE_INSTALLED_STATE_H
#define DOMINIUM_CORE_INSTALLED_STATE_H

extern "C" {
#include "domino/core/types.h"
}

#include "dominium/core_err.h"
#include "dominium/core_tlv.h"

/* Installed state tags (0x3000 range). */
#define CORE_TLV_TAG_INSTALLED_STATE_PRODUCT_ID 0x3001u
#define CORE_TLV_TAG_INSTALLED_STATE_INSTALLED_VERSION 0x3002u
#define CORE_TLV_TAG_INSTALLED_STATE_SELECTED_SPLAT 0x3003u
#define CORE_TLV_TAG_INSTALLED_STATE_INSTALL_SCOPE 0x3004u
#define CORE_TLV_TAG_INSTALLED_STATE_INSTALL_ROOT 0x3005u
#define CORE_TLV_TAG_INSTALLED_STATE_COMPONENTS 0x3006u
#define CORE_TLV_TAG_INSTALLED_STATE_MANIFEST_DIGEST64 0x3007u
#define CORE_TLV_TAG_INSTALLED_STATE_REQUEST_DIGEST64 0x3008u
#define CORE_TLV_TAG_INSTALLED_STATE_INSTALL_ROOTS 0x3009u
#define CORE_TLV_TAG_INSTALLED_STATE_OWNERSHIP 0x300Au
#define CORE_TLV_TAG_INSTALLED_STATE_ARTIFACTS 0x300Bu
#define CORE_TLV_TAG_INSTALLED_STATE_REGISTRATIONS 0x300Cu
#define CORE_TLV_TAG_INSTALLED_STATE_PREV_STATE_DIGEST64 0x300Du
#define CORE_TLV_TAG_INSTALLED_STATE_IMPORT_SOURCE 0x300Eu
#define CORE_TLV_TAG_INSTALLED_STATE_IMPORT_DETAILS 0x300Fu
#define CORE_TLV_TAG_INSTALLED_STATE_VERSION 0x3013u
#define CORE_TLV_TAG_INSTALLED_STATE_MIGRATIONS 0x3014u

#define CORE_TLV_TAG_INSTALLED_STATE_COMPONENT_ENTRY 0x3010u
#define CORE_TLV_TAG_INSTALLED_STATE_INSTALL_ROOT_ENTRY 0x3011u
#define CORE_TLV_TAG_INSTALLED_STATE_IMPORT_DETAIL_ENTRY 0x3012u
#define CORE_TLV_TAG_INSTALLED_STATE_MIGRATION_ENTRY 0x3015u

#define CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_ENTRY 0x3020u
#define CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_ROOT_ID 0x3021u
#define CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_PATH 0x3022u
#define CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_DIGEST64 0x3023u
#define CORE_TLV_TAG_INSTALLED_STATE_ARTIFACT_SIZE 0x3024u

#define CORE_TLV_TAG_INSTALLED_STATE_REG_ENTRY 0x3030u
#define CORE_TLV_TAG_INSTALLED_STATE_REG_KIND 0x3031u
#define CORE_TLV_TAG_INSTALLED_STATE_REG_VALUE 0x3032u
#define CORE_TLV_TAG_INSTALLED_STATE_REG_STATUS 0x3033u

#ifdef __cplusplus
#include <string>
#include <vector>

namespace dom {
namespace core_installed_state {

enum { CORE_INSTALLED_STATE_TLV_VERSION = CORE_TLV_FRAMED_VERSION };

struct InstalledStateArtifact {
    u32 target_root_id;
    std::string path;
    u64 digest64;
    u64 size;
};

struct InstalledStateRegistration {
    u16 kind;
    u16 status;
    std::string value;
};

struct InstalledState {
    std::string product_id;
    std::string installed_version;
    std::string selected_splat;
    u16 install_scope;
    std::string install_root;
    std::vector<std::string> install_roots;
    u16 ownership;
    std::vector<std::string> installed_components;
    std::vector<InstalledStateArtifact> artifacts;
    std::vector<InstalledStateRegistration> registrations;
    u64 manifest_digest64;
    u64 request_digest64;
    u64 previous_state_digest64;
    std::string import_source;
    std::vector<std::string> import_details;
    u32 state_version;
    std::vector<std::string> migration_applied;
};

void installed_state_clear(InstalledState* state);
err_t installed_state_parse(const unsigned char* data,
                            u32 size,
                            InstalledState* out_state);
err_t installed_state_write(const InstalledState* state,
                            core_tlv_framed_buffer_t* out_buf);

} /* namespace core_installed_state */
} /* namespace dom */
#endif /* __cplusplus */

#endif /* DOMINIUM_CORE_INSTALLED_STATE_H */
