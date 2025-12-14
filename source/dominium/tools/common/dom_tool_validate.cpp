#include "dom_tool_validate.h"

#include <cstring>

#include "dom_tool_tlv.h"
#include "dom_tool_engine.h"

extern "C" {
#include "content/d_content.h"
#include "content/d_content_schema.h"
#include "core/d_tlv_schema.h"
#include "policy/d_policy.h"
#include "research/d_research_state.h"
#include "job/d_job.h"
#include "struct/d_struct.h"
#include "vehicle/d_vehicle.h"
}

namespace dom {
namespace tools {

bool validate_schema_payload(u32 schema_id,
                             const std::vector<unsigned char> &payload,
                             std::string *err) {
    d_tlv_blob blob;
    int vrc;

    if (schema_id == 0u) {
        if (err) *err = "validate_schema_payload: schema_id=0";
        return false;
    }

    ensure_engine_content_initialized();

    blob.ptr = payload.empty() ? (unsigned char *)0 : (unsigned char *)&payload[0];
    blob.len = (u32)payload.size();
    vrc = d_tlv_schema_validate((d_tlv_schema_id)schema_id, 1u, &blob, (d_tlv_blob *)0);
    if (vrc != 0) {
        if (err) *err = "schema validation failed";
        return false;
    }
    return true;
}

bool validate_record_stream(const std::vector<unsigned char> &stream,
                            std::string *err) {
    d_tlv_blob blob;
    u32 off = 0u;
    u32 schema_id = 0u;
    d_tlv_blob payload;

    ensure_engine_content_initialized();

    blob.ptr = stream.empty() ? (unsigned char *)0 : (unsigned char *)&stream[0];
    blob.len = (u32)stream.size();

    while (1) {
        const int rc = tlv_next(&blob, &off, &schema_id, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            if (err) *err = "validate_record_stream: malformed TLV stream";
            return false;
        }

        if (schema_id == 0u) {
            if (err) *err = "validate_record_stream: record schema_id=0";
            return false;
        }

        std::vector<unsigned char> payload_vec;
        payload_vec.resize((size_t)payload.len);
        if (payload.len > 0u && payload.ptr) {
            std::memcpy(&payload_vec[0], payload.ptr, (size_t)payload.len);
        }

        if (!validate_schema_payload(schema_id, payload_vec, err)) {
            return false;
        }
    }

    return true;
}

bool validate_with_engine_content(const std::vector<unsigned char> &content_stream,
                                  std::string *err) {
    d_proto_pack_manifest man;
    d_tlv_blob blob;

    ensure_engine_content_initialized();

    d_content_reset();

    std::memset(&man, 0, sizeof(man));
    blob.ptr = content_stream.empty() ? (unsigned char *)0 : (unsigned char *)&content_stream[0];
    blob.len = (u32)content_stream.size();
    man.id = 1u;
    man.version = 1u;
    man.name = "tool_validation";
    man.description = (const char *)0;
    man.content_tlv = blob;

    if (d_content_load_pack(&man) != 0) {
        if (err) *err = "engine content load failed";
        return false;
    }

    if (d_content_validate_all() != 0) {
        if (err) *err = "d_content_validate_all failed";
        return false;
    }
    if (d_research_validate((const d_world *)0) != 0) {
        if (err) *err = "d_research_validate failed";
        return false;
    }
    if (d_policy_validate((const d_world *)0) != 0) {
        if (err) *err = "d_policy_validate failed";
        return false;
    }
    if (d_struct_validate((const d_world *)0) != 0) {
        if (err) *err = "d_struct_validate failed";
        return false;
    }
    if (d_vehicle_validate((const d_world *)0) != 0) {
        if (err) *err = "d_vehicle_validate failed";
        return false;
    }
    if (d_job_validate((const d_world *)0) != 0) {
        if (err) *err = "d_job_validate failed";
        return false;
    }

    return true;
}

} // namespace tools
} // namespace dom
