#ifndef DSK_CONTRACTS_H
#define DSK_CONTRACTS_H

#include "dsk_error.h"
#include "dsk_tlv.h"

/* Manifest tags (0x1000 range) */
#define DSK_TLV_TAG_MANIFEST_PRODUCT_ID 0x1001u
#define DSK_TLV_TAG_MANIFEST_VERSION 0x1002u
#define DSK_TLV_TAG_MANIFEST_BUILD_ID 0x1003u
#define DSK_TLV_TAG_MANIFEST_SUPPORTED_TARGETS 0x1004u
#define DSK_TLV_TAG_MANIFEST_COMPONENTS 0x1005u
#define DSK_TLV_TAG_MANIFEST_ALLOWED_SPLATS 0x1006u
#define DSK_TLV_TAG_MANIFEST_TARGET_RULES 0x1007u
#define DSK_TLV_TAG_MANIFEST_LAYOUT_TEMPLATES 0x1008u
#define DSK_TLV_TAG_MANIFEST_UNINSTALL_RULES 0x1009u
#define DSK_TLV_TAG_MANIFEST_REPAIR_RULES 0x100Au
#define DSK_TLV_TAG_MANIFEST_MIGRATION_RULES 0x100Bu
#define DSK_TLV_TAG_MANIFEST_SPLAT_OVERRIDES 0x100Cu

#define DSK_TLV_TAG_MANIFEST_PLATFORM_TARGETS DSK_TLV_TAG_MANIFEST_SUPPORTED_TARGETS

#define DSK_TLV_TAG_PLATFORM_ENTRY 0x1101u
#define DSK_TLV_TAG_ALLOWED_SPLAT_ENTRY 0x1102u

#define DSK_TLV_TAG_COMPONENT_ENTRY 0x1201u
#define DSK_TLV_TAG_COMPONENT_ID 0x1202u
#define DSK_TLV_TAG_COMPONENT_KIND 0x1203u
#define DSK_TLV_TAG_COMPONENT_DEFAULT_SELECTED 0x1204u
#define DSK_TLV_TAG_COMPONENT_DEPS 0x1205u
#define DSK_TLV_TAG_COMPONENT_CONFLICTS 0x1206u
#define DSK_TLV_TAG_COMPONENT_ARTIFACTS 0x1207u
#define DSK_TLV_TAG_COMPONENT_VERSION 0x1208u
#define DSK_TLV_TAG_COMPONENT_SUPPORTED_TARGETS 0x1209u
#define DSK_TLV_TAG_COMPONENT_DEP_ENTRY 0x1210u
#define DSK_TLV_TAG_COMPONENT_CONFLICT_ENTRY 0x1211u
#define DSK_TLV_TAG_COMPONENT_TARGET_ENTRY 0x1212u

#define DSK_TLV_TAG_ARTIFACT_ENTRY 0x1220u
#define DSK_TLV_TAG_ARTIFACT_HASH 0x1221u
#define DSK_TLV_TAG_ARTIFACT_SIZE 0x1222u
#define DSK_TLV_TAG_ARTIFACT_PATH 0x1223u
#define DSK_TLV_TAG_ARTIFACT_ID 0x1224u
#define DSK_TLV_TAG_ARTIFACT_SOURCE_PATH 0x1225u
#define DSK_TLV_TAG_ARTIFACT_DIGEST64 0x1226u
#define DSK_TLV_TAG_ARTIFACT_LAYOUT_TEMPLATE_ID 0x1227u

#define DSK_TLV_TAG_ARTIFACT_SOURCE DSK_TLV_TAG_ARTIFACT_SOURCE_PATH

#define DSK_TLV_TAG_LAYOUT_TEMPLATE_ENTRY 0x1301u
#define DSK_TLV_TAG_LAYOUT_TEMPLATE_ID 0x1302u
#define DSK_TLV_TAG_LAYOUT_TEMPLATE_TARGET_ROOT 0x1303u
#define DSK_TLV_TAG_LAYOUT_TEMPLATE_PATH_PREFIX 0x1304u

/* Request tags (0x2000 range) */
#define DSK_TLV_TAG_REQUEST_OPERATION 0x2001u
#define DSK_TLV_TAG_REQUEST_REQUESTED_COMPONENTS 0x2002u
#define DSK_TLV_TAG_REQUEST_EXCLUDED_COMPONENTS 0x2003u
#define DSK_TLV_TAG_REQUEST_INSTALL_SCOPE 0x2004u
#define DSK_TLV_TAG_REQUEST_PREFERRED_INSTALL_ROOT 0x2005u
#define DSK_TLV_TAG_REQUEST_UI_MODE 0x2006u
#define DSK_TLV_TAG_REQUEST_REQUESTED_SPLAT_ID 0x2007u
#define DSK_TLV_TAG_REQUEST_POLICY_FLAGS 0x2008u
#define DSK_TLV_TAG_REQUEST_TARGET_PLATFORM_TRIPLE 0x2009u
#define DSK_TLV_TAG_REQUEST_REQUIRED_CAPS 0x200Au
#define DSK_TLV_TAG_REQUEST_PROHIBITED_CAPS 0x200Bu
#define DSK_TLV_TAG_REQUEST_OWNERSHIP_PREFERENCE 0x200Cu
#define DSK_TLV_TAG_REQUEST_PAYLOAD_ROOT 0x200Du

#define DSK_TLV_TAG_REQUEST_REQUESTED_SPLAT DSK_TLV_TAG_REQUEST_REQUESTED_SPLAT_ID
#define DSK_TLV_TAG_REQUEST_PLATFORM_TRIPLE DSK_TLV_TAG_REQUEST_TARGET_PLATFORM_TRIPLE

#define DSK_TLV_TAG_REQUESTED_COMPONENT_ENTRY 0x2010u
#define DSK_TLV_TAG_EXCLUDED_COMPONENT_ENTRY 0x2011u

/* Installed state tags (0x3000 range) */
#define DSK_TLV_TAG_STATE_PRODUCT_ID 0x3001u
#define DSK_TLV_TAG_STATE_INSTALLED_VERSION 0x3002u
#define DSK_TLV_TAG_STATE_SELECTED_SPLAT 0x3003u
#define DSK_TLV_TAG_STATE_INSTALL_SCOPE 0x3004u
#define DSK_TLV_TAG_STATE_INSTALL_ROOT 0x3005u
#define DSK_TLV_TAG_STATE_INSTALLED_COMPONENTS 0x3006u
#define DSK_TLV_TAG_STATE_MANIFEST_DIGEST64 0x3007u
#define DSK_TLV_TAG_STATE_REQUEST_DIGEST64 0x3008u
#define DSK_TLV_TAG_STATE_INSTALL_ROOTS 0x3009u
#define DSK_TLV_TAG_STATE_OWNERSHIP 0x300Au
#define DSK_TLV_TAG_STATE_ARTIFACTS 0x300Bu
#define DSK_TLV_TAG_STATE_REGISTRATIONS 0x300Cu
#define DSK_TLV_TAG_STATE_PREV_STATE_DIGEST64 0x300Du

#define DSK_TLV_TAG_STATE_COMPONENT_ENTRY 0x3010u
#define DSK_TLV_TAG_STATE_INSTALL_ROOT_ENTRY 0x3011u

#define DSK_TLV_TAG_STATE_ARTIFACT_ENTRY 0x3020u
#define DSK_TLV_TAG_STATE_ARTIFACT_ROOT_ID 0x3021u
#define DSK_TLV_TAG_STATE_ARTIFACT_PATH 0x3022u
#define DSK_TLV_TAG_STATE_ARTIFACT_DIGEST64 0x3023u
#define DSK_TLV_TAG_STATE_ARTIFACT_SIZE 0x3024u

#define DSK_TLV_TAG_STATE_REG_ENTRY 0x3030u
#define DSK_TLV_TAG_STATE_REG_KIND 0x3031u
#define DSK_TLV_TAG_STATE_REG_VALUE 0x3032u
#define DSK_TLV_TAG_STATE_REG_STATUS 0x3033u

/* Audit tags (0x4000 range) */
#define DSK_TLV_TAG_AUDIT_RUN_ID 0x4001u
#define DSK_TLV_TAG_AUDIT_MANIFEST_DIGEST64 0x4002u
#define DSK_TLV_TAG_AUDIT_REQUEST_DIGEST64 0x4003u
#define DSK_TLV_TAG_AUDIT_SELECTED_SPLAT 0x4004u
#define DSK_TLV_TAG_AUDIT_SELECTION 0x4005u
#define DSK_TLV_TAG_AUDIT_OPERATION 0x4006u
#define DSK_TLV_TAG_AUDIT_RESULT 0x4007u
#define DSK_TLV_TAG_AUDIT_EVENTS 0x4008u
#define DSK_TLV_TAG_AUDIT_SPLAT_CAPS_DIGEST64 0x4009u
#define DSK_TLV_TAG_AUDIT_RESOLVED_SET_DIGEST64 0x400Au
#define DSK_TLV_TAG_AUDIT_PLAN_DIGEST64 0x400Bu
#define DSK_TLV_TAG_AUDIT_REFUSALS 0x400Cu

#define DSK_TLV_TAG_AUDIT_SELECTION_REASON DSK_TLV_TAG_AUDIT_SELECTION

#define DSK_TLV_TAG_AUDIT_CANDIDATES 0x4101u
#define DSK_TLV_TAG_AUDIT_REJECTIONS 0x4102u
#define DSK_TLV_TAG_AUDIT_SELECTED_ID 0x4103u
#define DSK_TLV_TAG_AUDIT_CANDIDATE_ENTRY 0x4104u
#define DSK_TLV_TAG_AUDIT_CANDIDATE_ID 0x4105u
#define DSK_TLV_TAG_AUDIT_CANDIDATE_CAPS_DIGEST64 0x4106u
#define DSK_TLV_TAG_AUDIT_SELECTED_REASON 0x4107u

#define DSK_TLV_TAG_AUDIT_CHOSEN DSK_TLV_TAG_AUDIT_SELECTED_ID

#define DSK_TLV_TAG_AUDIT_REJECTION_ENTRY 0x4110u
#define DSK_TLV_TAG_AUDIT_REJECTION_ID 0x4111u
#define DSK_TLV_TAG_AUDIT_REJECTION_CODE 0x4112u
#define DSK_TLV_TAG_AUDIT_REJECTION_DETAIL 0x4113u

#define DSK_TLV_TAG_AUDIT_REFUSAL_ENTRY 0x4120u
#define DSK_TLV_TAG_AUDIT_REFUSAL_CODE 0x4121u
#define DSK_TLV_TAG_AUDIT_REFUSAL_DETAIL 0x4122u

#define DSK_TLV_TAG_AUDIT_EVENT_ENTRY 0x4201u
#define DSK_TLV_TAG_AUDIT_EVENT_ID 0x4202u
#define DSK_TLV_TAG_AUDIT_EVENT_ERR_DOMAIN 0x4203u
#define DSK_TLV_TAG_AUDIT_EVENT_ERR_CODE 0x4204u
#define DSK_TLV_TAG_AUDIT_EVENT_ERR_SUBCODE 0x4205u
#define DSK_TLV_TAG_AUDIT_EVENT_ERR_FLAGS 0x4206u

#define DSK_TLV_TAG_RESULT_OK 0x4301u
#define DSK_TLV_TAG_RESULT_DOMAIN 0x4302u
#define DSK_TLV_TAG_RESULT_CODE 0x4303u
#define DSK_TLV_TAG_RESULT_SUBCODE 0x4304u
#define DSK_TLV_TAG_RESULT_FLAGS 0x4305u

#define DSK_TLV_TAG_AUDIT_JOB_OUTCOMES 0x4401u
#define DSK_TLV_TAG_AUDIT_JOB_ENTRY 0x4402u
#define DSK_TLV_TAG_AUDIT_JOB_ID 0x4403u
#define DSK_TLV_TAG_AUDIT_JOB_KIND 0x4404u
#define DSK_TLV_TAG_AUDIT_JOB_STATUS 0x4405u

/* Job journal tags (0x6000 range) */
#define DSK_TLV_TAG_JOB_RUN_ID 0x6001u
#define DSK_TLV_TAG_JOB_PLAN_DIGEST64 0x6002u
#define DSK_TLV_TAG_JOB_SELECTED_SPLAT_ID 0x6003u
#define DSK_TLV_TAG_JOB_STAGE_ROOT 0x6004u
#define DSK_TLV_TAG_JOB_CHECKPOINTS 0x6005u
#define DSK_TLV_TAG_JOB_ROLLBACK_REF 0x6006u
#define DSK_TLV_TAG_JOB_LAST_ERROR 0x6007u
#define DSK_TLV_TAG_JOB_PLAN_BYTES 0x6008u

#define DSK_TLV_TAG_JOB_CHECKPOINT_ENTRY 0x6010u
#define DSK_TLV_TAG_JOB_CHECKPOINT_ID 0x6011u
#define DSK_TLV_TAG_JOB_CHECKPOINT_STATUS 0x6012u
#define DSK_TLV_TAG_JOB_CHECKPOINT_LAST_STEP 0x6013u

#define DSK_TLV_TAG_JOB_ERR_DOMAIN 0x6020u
#define DSK_TLV_TAG_JOB_ERR_CODE 0x6021u
#define DSK_TLV_TAG_JOB_ERR_SUBCODE 0x6022u
#define DSK_TLV_TAG_JOB_ERR_FLAGS 0x6023u

/* Enumerations */
#define DSK_OPERATION_INSTALL 1u
#define DSK_OPERATION_REPAIR 2u
#define DSK_OPERATION_UNINSTALL 3u
#define DSK_OPERATION_VERIFY 4u
#define DSK_OPERATION_STATUS 5u
#define DSK_OPERATION_UPGRADE 6u

#define DSK_INSTALL_SCOPE_USER 1u
#define DSK_INSTALL_SCOPE_SYSTEM 2u
#define DSK_INSTALL_SCOPE_PORTABLE 3u

#define DSK_UI_MODE_GUI 1u
#define DSK_UI_MODE_TUI 2u
#define DSK_UI_MODE_CLI 3u

#define DSK_POLICY_DETERMINISTIC 0x00000001u
#define DSK_POLICY_OFFLINE 0x00000002u
#define DSK_POLICY_LEGACY_MODE 0x00000004u
#define DSK_POLICY_VERIFY_ONLY 0x00000008u

#define DSK_OWNERSHIP_ANY 0u
#define DSK_OWNERSHIP_PORTABLE 1u
#define DSK_OWNERSHIP_PKG 2u
#define DSK_OWNERSHIP_STEAM 3u

#define DSK_REG_KIND_SHORTCUT 1u
#define DSK_REG_KIND_FILE_ASSOC 2u
#define DSK_REG_KIND_URL_HANDLER 3u

#define DSK_REG_STATUS_SKIPPED 1u
#define DSK_REG_STATUS_OK 2u
#define DSK_REG_STATUS_FAILED 3u

#ifdef __cplusplus
#include <string>
#include <vector>

struct dsk_artifact_t {
    std::string artifact_id;
    std::string hash;
    dsk_u64 digest64;
    dsk_u64 size;
    std::string source_path;
    std::string layout_template_id;
};

struct dsk_layout_template_t {
    std::string template_id;
    std::string target_root;
    std::string path_prefix;
};

struct dsk_manifest_component_t {
    std::string component_id;
    std::string component_version;
    std::string kind;
    dsk_bool default_selected;
    std::vector<std::string> deps;
    std::vector<std::string> conflicts;
    std::vector<std::string> supported_targets;
    std::vector<dsk_artifact_t> artifacts;
};

struct dsk_manifest_t {
    std::string product_id;
    std::string version;
    std::string build_id;
    std::vector<std::string> supported_targets;
    std::vector<std::string> allowed_splats;
    std::vector<dsk_layout_template_t> layout_templates;
    std::vector<dsk_manifest_component_t> components;
};

struct dsk_request_t {
    dsk_u16 operation;
    std::vector<std::string> requested_components;
    std::vector<std::string> excluded_components;
    dsk_u16 install_scope;
    std::string preferred_install_root;
    std::string payload_root;
    dsk_u16 ui_mode;
    std::string requested_splat_id;
    dsk_u32 policy_flags;
    dsk_u32 required_caps;
    dsk_u32 prohibited_caps;
    dsk_u16 ownership_preference;
    std::string target_platform_triple;
};

struct dsk_state_artifact_t {
    dsk_u32 target_root_id;
    std::string path;
    dsk_u64 digest64;
    dsk_u64 size;
};

struct dsk_state_registration_t {
    dsk_u16 kind;
    dsk_u16 status;
    std::string value;
};

struct dsk_installed_state_t {
    std::string product_id;
    std::string installed_version;
    std::string selected_splat;
    dsk_u16 install_scope;
    std::string install_root;
    std::vector<std::string> install_roots;
    dsk_u16 ownership;
    std::vector<std::string> installed_components;
    std::vector<dsk_state_artifact_t> artifacts;
    std::vector<dsk_state_registration_t> registrations;
    dsk_u64 manifest_digest64;
    dsk_u64 request_digest64;
    dsk_u64 previous_state_digest64;
};

DSK_API void dsk_manifest_clear(dsk_manifest_t *manifest);
DSK_API dsk_status_t dsk_manifest_parse(const dsk_u8 *data,
                                        dsk_u32 size,
                                        dsk_manifest_t *out_manifest);
DSK_API dsk_status_t dsk_manifest_write(const dsk_manifest_t *manifest,
                                        dsk_tlv_buffer_t *out_buf);

DSK_API void dsk_request_clear(dsk_request_t *request);
DSK_API dsk_status_t dsk_request_parse(const dsk_u8 *data,
                                       dsk_u32 size,
                                       dsk_request_t *out_request);
DSK_API dsk_status_t dsk_request_write(const dsk_request_t *request,
                                       dsk_tlv_buffer_t *out_buf);

DSK_API void dsk_installed_state_clear(dsk_installed_state_t *state);
DSK_API dsk_status_t dsk_installed_state_parse(const dsk_u8 *data,
                                               dsk_u32 size,
                                               dsk_installed_state_t *out_state);
DSK_API dsk_status_t dsk_installed_state_write(const dsk_installed_state_t *state,
                                               dsk_tlv_buffer_t *out_buf);
#endif

#endif /* DSK_CONTRACTS_H */
