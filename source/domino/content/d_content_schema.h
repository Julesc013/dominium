/* TLV schema definitions for content protos (C89). */
#ifndef D_CONTENT_SCHEMA_H
#define D_CONTENT_SCHEMA_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"

/* Schema IDs (id encodes kind; version fixed to 1 for now). */
#define D_TLV_SCHEMA_MATERIAL_V1        0x0101u
#define D_TLV_SCHEMA_ITEM_V1            0x0102u
#define D_TLV_SCHEMA_CONTAINER_V1       0x0103u
#define D_TLV_SCHEMA_PROCESS_V1         0x0104u
#define D_TLV_SCHEMA_DEPOSIT_V1         0x0105u
#define D_TLV_SCHEMA_STRUCTURE_V1       0x0106u
#define D_TLV_SCHEMA_VEHICLE_V1         0x0107u
#define D_TLV_SCHEMA_SPLINE_V1          0x0108u
#define D_TLV_SCHEMA_JOB_TEMPLATE_V1    0x0109u
#define D_TLV_SCHEMA_BUILDING_V1        0x010Au
#define D_TLV_SCHEMA_BLUEPRINT_V1       0x010Bu
#define D_TLV_SCHEMA_PACK_V1            0x0201u
#define D_TLV_SCHEMA_MOD_V1             0x0202u

/* Field tags per schema (all 32-bit tags). */
#define D_FIELD_MATERIAL_ID         0x01u
#define D_FIELD_MATERIAL_NAME       0x02u
#define D_FIELD_MATERIAL_TAGS       0x03u
#define D_FIELD_MATERIAL_DENSITY    0x04u
#define D_FIELD_MATERIAL_HARDNESS   0x05u
#define D_FIELD_MATERIAL_MELTING    0x06u
#define D_FIELD_MATERIAL_PERMEABILITY 0x07u
#define D_FIELD_MATERIAL_POROSITY     0x08u
#define D_FIELD_MATERIAL_THERMAL      0x09u
#define D_FIELD_MATERIAL_EROSION      0x0Au

#define D_FIELD_ITEM_ID             0x01u
#define D_FIELD_ITEM_NAME           0x02u
#define D_FIELD_ITEM_MATERIAL       0x03u
#define D_FIELD_ITEM_TAGS           0x04u
#define D_FIELD_ITEM_UNIT_MASS      0x05u
#define D_FIELD_ITEM_UNIT_VOLUME    0x06u

#define D_FIELD_CONTAINER_ID        0x01u
#define D_FIELD_CONTAINER_NAME      0x02u
#define D_FIELD_CONTAINER_TAGS      0x03u
#define D_FIELD_CONTAINER_MAX_VOLUME 0x04u
#define D_FIELD_CONTAINER_MAX_MASS  0x05u
#define D_FIELD_CONTAINER_SLOTS     0x06u
#define D_FIELD_CONTAINER_PACKING_MODE 0x07u
#define D_FIELD_CONTAINER_PARAMS    0x08u

#define D_FIELD_PROCESS_ID          0x01u
#define D_FIELD_PROCESS_NAME        0x02u
#define D_FIELD_PROCESS_TAGS        0x03u
#define D_FIELD_PROCESS_PARAMS      0x04u
#define D_FIELD_PROCESS_BASE_DURATION 0x05u
#define D_FIELD_PROCESS_IO_TERM     0x06u /* repeated; payload is TLV fields */

/* Nested fields inside D_FIELD_PROCESS_IO_TERM payload. */
#define D_FIELD_PROCESS_IO_KIND     0x01u /* u16 */
#define D_FIELD_PROCESS_IO_ITEM_ID  0x02u /* u32 */
#define D_FIELD_PROCESS_IO_RATE     0x03u /* q16_16 */
#define D_FIELD_PROCESS_IO_FLAGS    0x04u /* u16 */

#define D_FIELD_DEPOSIT_ID          0x01u
#define D_FIELD_DEPOSIT_NAME        0x02u
#define D_FIELD_DEPOSIT_MATERIAL    0x03u
#define D_FIELD_DEPOSIT_MODEL       0x04u
#define D_FIELD_DEPOSIT_TAGS        0x05u
#define D_FIELD_DEPOSIT_PARAMS      0x06u

#define D_FIELD_STRUCTURE_ID        0x01u
#define D_FIELD_STRUCTURE_NAME      0x02u
#define D_FIELD_STRUCTURE_TAGS      0x03u
#define D_FIELD_STRUCTURE_LAYOUT    0x04u
#define D_FIELD_STRUCTURE_IO        0x05u
#define D_FIELD_STRUCTURE_PROCESSES 0x06u

#define D_FIELD_VEHICLE_ID          0x01u
#define D_FIELD_VEHICLE_NAME        0x02u
#define D_FIELD_VEHICLE_TAGS        0x03u
#define D_FIELD_VEHICLE_PARAMS      0x04u

#define D_FIELD_SPLINE_ID           0x01u
#define D_FIELD_SPLINE_NAME         0x02u
#define D_FIELD_SPLINE_TAGS         0x03u
#define D_FIELD_SPLINE_PARAMS       0x04u
#define D_FIELD_SPLINE_TYPE         0x05u
#define D_FIELD_SPLINE_FLAGS        0x06u
#define D_FIELD_SPLINE_BASE_SPEED   0x07u
#define D_FIELD_SPLINE_MAX_GRADE    0x08u
#define D_FIELD_SPLINE_CAPACITY     0x09u

#define D_FIELD_JOB_ID              0x01u
#define D_FIELD_JOB_NAME            0x02u
#define D_FIELD_JOB_PURPOSE         0x03u
#define D_FIELD_JOB_TAGS            0x04u
#define D_FIELD_JOB_PROCESS_ID      0x05u
#define D_FIELD_JOB_STRUCTURE_ID    0x06u
#define D_FIELD_JOB_SPLINE_PROFILE_ID 0x07u
#define D_FIELD_JOB_REQUIREMENTS    0x08u
#define D_FIELD_JOB_REWARDS         0x09u

#define D_FIELD_BUILDING_ID         0x01u
#define D_FIELD_BUILDING_NAME       0x02u
#define D_FIELD_BUILDING_TAGS       0x03u
#define D_FIELD_BUILDING_SHELL      0x04u
#define D_FIELD_BUILDING_PARAMS     0x05u

#define D_FIELD_BLUEPRINT_ID        0x01u
#define D_FIELD_BLUEPRINT_NAME      0x02u
#define D_FIELD_BLUEPRINT_TAGS      0x03u
#define D_FIELD_BLUEPRINT_PAYLOAD   0x04u

#define D_FIELD_PACK_ID             0x01u
#define D_FIELD_PACK_VERSION        0x02u
#define D_FIELD_PACK_NAME           0x03u
#define D_FIELD_PACK_DESCRIPTION    0x04u
#define D_FIELD_PACK_CONTENT        0x05u

#define D_FIELD_MOD_ID              0x01u
#define D_FIELD_MOD_VERSION         0x02u
#define D_FIELD_MOD_NAME            0x03u
#define D_FIELD_MOD_DESCRIPTION     0x04u
#define D_FIELD_MOD_DEPS            0x05u
#define D_FIELD_MOD_CONTENT         0x06u

struct d_proto_material_s;
struct d_proto_item_s;
struct d_proto_container_s;
struct d_proto_process_s;
struct d_proto_deposit_s;
struct d_proto_structure_s;
struct d_proto_vehicle_s;
struct d_proto_spline_profile_s;
struct d_proto_job_template_s;
struct d_proto_building_s;
struct d_proto_blueprint_s;
struct d_proto_pack_manifest_s;
struct d_proto_mod_manifest_s;

/* Register all schema validators with the TLV schema registry. */
int d_content_schema_register_all(void);

/* Parse helpers; return 0 on success. */
int d_content_schema_parse_material_v1(const d_tlv_blob *blob, struct d_proto_material_s *out);
int d_content_schema_parse_item_v1(const d_tlv_blob *blob, struct d_proto_item_s *out);
int d_content_schema_parse_container_v1(const d_tlv_blob *blob, struct d_proto_container_s *out);
int d_content_schema_parse_process_v1(const d_tlv_blob *blob, struct d_proto_process_s *out);
int d_content_schema_parse_deposit_v1(const d_tlv_blob *blob, struct d_proto_deposit_s *out);
int d_content_schema_parse_structure_v1(const d_tlv_blob *blob, struct d_proto_structure_s *out);
int d_content_schema_parse_vehicle_v1(const d_tlv_blob *blob, struct d_proto_vehicle_s *out);
int d_content_schema_parse_spline_v1(const d_tlv_blob *blob, struct d_proto_spline_profile_s *out);
int d_content_schema_parse_job_template_v1(const d_tlv_blob *blob, struct d_proto_job_template_s *out);
int d_content_schema_parse_building_v1(const d_tlv_blob *blob, struct d_proto_building_s *out);
int d_content_schema_parse_blueprint_v1(const d_tlv_blob *blob, struct d_proto_blueprint_s *out);
int d_content_schema_parse_pack_v1(const d_tlv_blob *blob, struct d_proto_pack_manifest_s *out);
int d_content_schema_parse_mod_v1(const d_tlv_blob *blob, struct d_proto_mod_manifest_s *out);

#endif /* D_CONTENT_SCHEMA_H */
