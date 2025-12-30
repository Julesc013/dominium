#ifndef DSK_PLAN_H
#define DSK_PLAN_H

#include "dsk_contract_plan.h"
#include "dsk_contracts.h"
#include "dsk_error.h"
#include "dsk_splat_caps.h"
#include "dsk_types.h"

#ifdef __cplusplus
#include <string>
#include <vector>

struct dsk_plan_step_t {
    dsk_u32 step_id;
    dsk_u16 step_kind;
    std::string component_id;
    std::string artifact_id;
    dsk_u32 target_root_id;
    std::vector<dsk_u8> intent_tlv;
};

struct dsk_plan_file_op_t {
    dsk_u16 op_kind;
    std::string from_path;
    std::string to_path;
    dsk_u16 ownership;
    dsk_u64 digest64;
    dsk_u64 size;
};

struct dsk_plan_registration_t {
    std::vector<std::string> shortcuts;
    std::vector<std::string> file_associations;
    std::vector<std::string> url_handlers;
};

struct dsk_resolved_component_t {
    std::string component_id;
    std::string component_version;
    std::string kind;
    dsk_u16 source;
};

struct dsk_resolved_set_t {
    std::vector<dsk_resolved_component_t> components;
    dsk_u64 digest64;
};

struct dsk_plan_t {
    std::string product_id;
    std::string product_version;
    std::string selected_splat_id;
    dsk_u64 selected_splat_caps_digest64;
    dsk_u16 operation;
    dsk_u16 install_scope;
    std::vector<std::string> install_roots;
    dsk_u64 manifest_digest64;
    dsk_u64 request_digest64;
    dsk_u64 resolved_set_digest64;
    dsk_u64 plan_digest64;
    std::vector<dsk_resolved_component_t> resolved_components;
    std::vector<dsk_plan_step_t> ordered_steps;
    std::vector<dsk_plan_file_op_t> file_ops;
    dsk_plan_registration_t registrations;
};

DSK_API void dsk_plan_clear(dsk_plan_t *plan);
DSK_API dsk_status_t dsk_plan_parse(const dsk_u8 *data, dsk_u32 size, dsk_plan_t *out_plan);
DSK_API dsk_status_t dsk_plan_write(const dsk_plan_t *plan, dsk_tlv_buffer_t *out_buf);
DSK_API dsk_status_t dsk_plan_validate(const dsk_plan_t *plan);
DSK_API dsk_u64 dsk_plan_payload_digest(const dsk_plan_t *plan);
DSK_API dsk_status_t dsk_plan_dump_json(const dsk_plan_t *plan, std::string *out_json);
DSK_API dsk_status_t dsk_plan_build(const dsk_manifest_t &manifest,
                                    const dsk_request_t &request,
                                    const std::string &selected_splat_id,
                                    const dsk_splat_caps_t &splat_caps,
                                    dsk_u64 splat_caps_digest64,
                                    const dsk_resolved_set_t &resolved,
                                    dsk_u64 manifest_digest64,
                                    dsk_u64 request_digest64,
                                    dsk_plan_t *out_plan);

#endif /* __cplusplus */

#endif /* DSK_PLAN_H */
