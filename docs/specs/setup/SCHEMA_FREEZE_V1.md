Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup Schema Freeze v1

This document freezes v1 schemas for Setup TLV contracts. Any change to the
schema constants listed here requires updating this file and the schema hash.

schema_hash: b5ff1447b4bcca5933fa5060325f86187d423bc6b01c748ac418979e9bfb0158

## Versioning rules
- Framed TLV header uses the v1 framing format (magic/version/endian/header_size/payload_size/header_crc).
- Unknown tags must be skipped deterministically.
- New fields must be optional and skip-unknown safe.
- Incompatible changes require a new major schema (v2).

## install_manifest.tlv v1 (DSK_TLV_TAG_MANIFEST_*)

Root tags (0x1000 range):
- 0x1001 product_id
- 0x1002 version
- 0x1003 build_id
- 0x1004 supported_targets
- 0x1005 components
- 0x1006 allowed_splats
- 0x1007 target_rules
- 0x1008 layout_templates
- 0x1009 uninstall_rules
- 0x100A repair_rules
- 0x100B migration_rules
- 0x100C splat_overrides

Entries (0x1100 range):
- 0x1101 platform_entry
- 0x1102 allowed_splat_entry

Component tags (0x1200 range):
- 0x1201 component_entry
- 0x1202 component_id
- 0x1203 component_kind
- 0x1204 component_default_selected
- 0x1205 component_deps
- 0x1206 component_conflicts
- 0x1207 component_artifacts
- 0x1208 component_version
- 0x1209 component_supported_targets
- 0x1210 component_dep_entry
- 0x1211 component_conflict_entry
- 0x1212 component_target_entry

Artifact tags (0x1220 range):
- 0x1220 artifact_entry
- 0x1221 artifact_hash
- 0x1222 artifact_size
- 0x1223 artifact_path
- 0x1224 artifact_id
- 0x1225 artifact_source_path
- 0x1226 artifact_digest64
- 0x1227 artifact_layout_template_id

Layout template tags (0x1300 range):
- 0x1301 layout_template_entry
- 0x1302 layout_template_id
- 0x1303 layout_template_target_root
- 0x1304 layout_template_path_prefix

## install_request.tlv v1 (DSK_TLV_TAG_REQUEST_*)

Root tags (0x2000 range):
- 0x2001 operation
- 0x2002 requested_components
- 0x2003 excluded_components
- 0x2004 install_scope
- 0x2005 preferred_install_root
- 0x2006 ui_mode
- 0x2007 requested_splat_id
- 0x2008 policy_flags
- 0x2009 target_platform_triple
- 0x200A required_caps
- 0x200B prohibited_caps
- 0x200C ownership_preference
- 0x200D payload_root
- 0x200E frontend_id

Entries (0x2010 range):
- 0x2010 requested_component_entry
- 0x2011 excluded_component_entry

Enums:
- operation: install=1, repair=2, uninstall=3, verify=4, status=5, upgrade=6, import_legacy=7
- install_scope: user=1, system=2, portable=3
- ui_mode: gui=1, tui=2, cli=3
- ownership: any=0, portable=1, pkg=2, steam=3
- policy_flags: deterministic=0x1, offline=0x2, legacy_mode=0x4, verify_only=0x8

## install_plan.tlv v1 (DSK_TLV_TAG_PLAN_*)

Root tags (0x5000 range):
- 0x5001 product_id
- 0x5002 product_version
- 0x5003 selected_splat_id
- 0x5004 selected_splat_caps_digest64
- 0x5005 operation
- 0x5006 install_scope
- 0x5007 install_roots
- 0x5008 manifest_digest64
- 0x5009 request_digest64
- 0x500A resolved_set_digest64
- 0x500B plan_digest64
- 0x500C resolved_components
- 0x500D job_graph
- 0x500E file_ops
- 0x500F registrations
- 0x5011 payload_root
- 0x5012 frontend_id
- 0x5013 target_platform_triple

Entries:
- 0x5010 install_root_entry
- 0x5101 component_entry
- 0x5102 component_id
- 0x5103 component_version
- 0x5104 component_kind
- 0x5105 component_source
- 0x5201 step_entry
- 0x5202 step_id
- 0x5203 step_kind
- 0x5204 step_component_id
- 0x5205 step_artifact_id
- 0x5206 step_target_root_id
- 0x5207 step_intent
- 0x5301 file_op_entry
- 0x5302 file_op_kind
- 0x5303 file_op_from
- 0x5304 file_op_to
- 0x5305 file_op_ownership
- 0x5306 file_op_digest64
- 0x5307 file_op_size
- 0x5308 file_op_target_root_id
- 0x5401 reg_shortcuts
- 0x5402 reg_file_assocs
- 0x5403 reg_url_handlers
- 0x5410 reg_shortcut_entry
- 0x5411 reg_file_assoc_entry
- 0x5412 reg_url_handler_entry

Plan enums:
- component_source: default=1, user=2, dependency=3, installed=4
- step_kind: stage_artifact=1, verify_hashes=2, commit_swap=3, register_actions=4, write_state=5, write_audit=6
- file_op_kind: copy=1, extract=2, remove=3, mkdir=4

## installed_state.tlv v1 (CORE_TLV_TAG_INSTALLED_STATE_*)

Root tags (0x3000 range):
- 0x3001 product_id
- 0x3002 installed_version
- 0x3003 selected_splat
- 0x3004 install_scope
- 0x3005 install_root
- 0x3006 components
- 0x3007 manifest_digest64
- 0x3008 request_digest64
- 0x3009 install_roots
- 0x300A ownership
- 0x300B artifacts
- 0x300C registrations
- 0x300D prev_state_digest64
- 0x300E import_source
- 0x300F import_details
- 0x3013 state_version
- 0x3014 migrations

Entries:
- 0x3010 component_entry
- 0x3011 install_root_entry
- 0x3012 import_detail_entry
- 0x3015 migration_entry

Artifacts (0x3020 range):
- 0x3020 artifact_entry
- 0x3021 artifact_root_id
- 0x3022 artifact_path
- 0x3023 artifact_digest64
- 0x3024 artifact_size

Registrations (0x3030 range):
- 0x3030 reg_entry
- 0x3031 reg_kind
- 0x3032 reg_value
- 0x3033 reg_status

## setup_audit.tlv v1 (DSK_TLV_TAG_AUDIT_*)

Root tags (0x4000 range):
- 0x4001 run_id
- 0x4002 manifest_digest64
- 0x4003 request_digest64
- 0x4004 selected_splat
- 0x4005 selection
- 0x4006 operation
- 0x4007 result
- 0x4008 events
- 0x4009 splat_caps_digest64
- 0x400A resolved_set_digest64
- 0x400B plan_digest64
- 0x400C refusals
- 0x400D frontend_id
- 0x400E platform_triple
- 0x400F import_source
- 0x4010 import_details
- 0x4011 import_detail_entry

Selection tags:
- 0x4101 candidates
- 0x4102 rejections
- 0x4103 selected_id
- 0x4104 candidate_entry
- 0x4105 candidate_id
- 0x4106 candidate_caps_digest64
- 0x4107 selected_reason
- 0x4110 rejection_entry
- 0x4111 rejection_id
- 0x4112 rejection_code
- 0x4113 rejection_detail

Refusal tags:
- 0x4120 refusal_entry
- 0x4121 refusal_code
- 0x4122 refusal_detail

Event tags:
- 0x4201 event_entry
- 0x4202 event_id
- 0x4203 event_err_domain
- 0x4204 event_err_code
- 0x4205 event_err_subcode
- 0x4206 event_err_flags
- 0x4207 event_err_msg_id
- 0x4208 event_err_detail

Result tags:
- 0x4301 result_ok
- 0x4302 result_domain
- 0x4303 result_code
- 0x4304 result_subcode
- 0x4305 result_flags
- 0x4306 result_msg_id
- 0x4307 result_err_detail

Job outcome tags:
- 0x4401 job_outcomes
- 0x4402 job_entry
- 0x4403 job_id
- 0x4404 job_kind
- 0x4405 job_status

Audit event IDs (DSK_AUDIT_EVENT_*):
- BEGIN, PARSE_MANIFEST_OK/FAIL, PARSE_REQUEST_OK/FAIL, SPLAT_SELECT_OK/FAIL, WRITE_STATE_OK/FAIL, END
- SPLAT_DEPRECATED
- IMPORT_BEGIN, IMPORT_PARSE_OK/FAIL, IMPORT_WRITE_STATE_OK/FAIL, IMPORT_END

## job_journal.tlv v1 (DSK_TLV_TAG_JOB_*)

Root tags (0x6000 range):
- 0x6001 run_id
- 0x6002 plan_digest64
- 0x6003 selected_splat_id
- 0x6004 stage_root
- 0x6005 checkpoints
- 0x6006 rollback_ref
- 0x6007 last_error
- 0x6008 plan_bytes

Checkpoint tags:
- 0x6010 checkpoint_entry
- 0x6011 checkpoint_id
- 0x6012 checkpoint_status
- 0x6013 checkpoint_last_step

Error tags:
- 0x6020 err_domain
- 0x6021 err_code
- 0x6022 err_subcode
- 0x6023 err_flags
- 0x6024 err_msg_id
- 0x6025 err_detail

## txn_journal.tlv v1 (DSS_TLV_TAG_TXN_*)

Root tags (0x7000 range):
- 0x7001 plan_digest64
- 0x7002 stage_root
- 0x7003 steps

Step tags:
- 0x7010 step_entry
- 0x7011 step_id
- 0x7012 step_kind
- 0x7013 step_src
- 0x7014 step_dst
- 0x7015 step_rollback_kind
- 0x7016 step_rollback_src
- 0x7017 step_rollback_dst

Transaction step kinds:
- mkdir=1, copy_file=2, extract_archive=3, atomic_rename=4, dir_swap=5, delete_file=6, remove_dir=7

## Extension guidance for v2
- Add new tags with new IDs, keep v1 tags stable.
- Gate incompatible behavior on major version bump.
- Update audit + refusal codes for any new validation logic.