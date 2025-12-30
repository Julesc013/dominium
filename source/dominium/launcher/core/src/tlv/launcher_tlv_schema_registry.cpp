/*
FILE: source/dominium/launcher/core/src/tlv/launcher_tlv_schema_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tlv
RESPONSIBILITY: Registers launcher TLV schemas with the shared core_tlv_schema registry.
*/

#include "launcher_tlv_schema_registry.h"

#include "dominium/core_tlv_schema.h"

#include "launcher_audit.h"
#include "launcher_handshake.h"
#include "launcher_instance.h"
#include "launcher_pack_manifest.h"
#include "launcher_selection_summary.h"
#include "launcher_tools_registry.h"
#include "launcher_tlv.h"
#include "launcher_tlv_migrations.h"

namespace dom {
namespace launcher_core {

namespace {

static err_t tlv_err_invalid_args(void) {
    return err_make((u16)ERRD_COMMON,
                    (u16)ERRC_COMMON_INVALID_ARGS,
                    (u32)ERRF_FATAL,
                    (u32)ERRMSG_COMMON_INVALID_ARGS);
}

static err_t tlv_err_parse(void) {
    return err_make((u16)ERRD_TLV,
                    (u16)ERRC_TLV_PARSE_FAILED,
                    (u32)ERRF_INTEGRITY,
                    (u32)ERRMSG_TLV_PARSE_FAILED);
}

static err_t tlv_err_integrity(void) {
    return err_make((u16)ERRD_TLV,
                    (u16)ERRC_TLV_INTEGRITY,
                    (u32)ERRF_INTEGRITY,
                    (u32)ERRMSG_TLV_INTEGRITY);
}

static err_t tlv_err_schema(u32 version) {
    err_t err = err_make((u16)ERRD_TLV,
                         (u16)ERRC_TLV_SCHEMA_VERSION,
                         (u32)(ERRF_POLICY_REFUSAL | ERRF_NOT_SUPPORTED),
                         (u32)ERRMSG_TLV_SCHEMA_VERSION);
    err_add_detail_u32(&err, (u32)ERR_DETAIL_KEY_SCHEMA_VERSION, version);
    return err;
}

static err_t tlv_write_bytes(const core_tlv_schema_sink* sink,
                             const unsigned char* data,
                             u32 size) {
    if (!sink || !sink->write) {
        return tlv_err_invalid_args();
    }
    if (size > 0u && !data) {
        return tlv_err_invalid_args();
    }
    if (size > 0u && sink->write(sink->user, data, size) != 0) {
        return err_make((u16)ERRD_COMMON,
                        (u16)ERRC_COMMON_INTERNAL,
                        (u32)ERRF_FATAL,
                        (u32)ERRMSG_COMMON_INTERNAL);
    }
    return err_ok();
}

static err_t tlv_identity_migrate(u32 from_version,
                                  u32 to_version,
                                  const unsigned char* data,
                                  u32 size,
                                  const core_tlv_schema_sink* sink) {
    if (from_version != to_version) {
        return tlv_err_schema(from_version);
    }
    return tlv_write_bytes(sink, data, size);
}

static err_t tlv_read_schema_version(const unsigned char* data,
                                     u32 size,
                                     u32 default_version,
                                     u32* out_version) {
    u32 version = 0u;
    if (!data || size == 0u || !out_version) {
        return tlv_err_invalid_args();
    }
    if (!tlv_read_schema_version_or_default(data, (size_t)size, version, default_version)) {
        return tlv_err_parse();
    }
    *out_version = version;
    return err_ok();
}

static err_t validate_instance_manifest(const unsigned char* data,
                                        u32 size,
                                        u32* out_version) {
    err_t err;
    LauncherInstanceManifest manifest;
    u32 version = 0u;
    err = tlv_read_schema_version(data,
                                  size,
                                  launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST),
                                  &version);
    if (!err_is_ok(&err)) {
        return err;
    }
    if (!launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST, version)) {
        return tlv_err_schema(version);
    }
    if (!launcher_instance_manifest_from_tlv_bytes_ex(data, (size_t)size, manifest, &err)) {
        return err_is_ok(&err) ? tlv_err_parse() : err;
    }
    if (out_version) {
        *out_version = version;
    }
    return err_ok();
}

static err_t migrate_instance_manifest(u32 from_version,
                                       u32 to_version,
                                       const unsigned char* data,
                                       u32 size,
                                       const core_tlv_schema_sink* sink) {
    LauncherInstanceManifest manifest;
    std::vector<unsigned char> bytes;
    if (!sink || !sink->write) {
        return tlv_err_invalid_args();
    }
    if (from_version == to_version) {
        return tlv_write_bytes(sink, data, size);
    }
    if (!launcher_instance_manifest_migrate_tlv(from_version, to_version, data, size, manifest)) {
        return tlv_err_schema(from_version);
    }
    if (!launcher_instance_manifest_to_tlv_bytes(manifest, bytes)) {
        return tlv_err_parse();
    }
    return tlv_write_bytes(sink,
                           bytes.empty() ? (const unsigned char*)0 : &bytes[0],
                           (u32)bytes.size());
}

static err_t validate_pack_manifest(const unsigned char* data,
                                    u32 size,
                                    u32* out_version) {
    err_t err;
    LauncherPackManifest manifest;
    u32 version = 0u;
    err = tlv_read_schema_version(data,
                                  size,
                                  launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_PACK_MANIFEST),
                                  &version);
    if (!err_is_ok(&err)) {
        return err;
    }
    if (!launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_PACK_MANIFEST, version)) {
        return tlv_err_schema(version);
    }
    if (!launcher_pack_manifest_from_tlv_bytes(data, (size_t)size, manifest)) {
        return tlv_err_parse();
    }
    if (!launcher_pack_manifest_validate(manifest, 0)) {
        return tlv_err_integrity();
    }
    if (out_version) {
        *out_version = version;
    }
    return err_ok();
}

static err_t validate_audit_log(const unsigned char* data,
                                u32 size,
                                u32* out_version) {
    err_t err;
    LauncherAuditLog audit;
    u32 version = 0u;
    err = tlv_read_schema_version(data,
                                  size,
                                  launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_AUDIT_LOG),
                                  &version);
    if (!err_is_ok(&err)) {
        return err;
    }
    if (!launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_AUDIT_LOG, version)) {
        return tlv_err_schema(version);
    }
    if (!launcher_audit_from_tlv_bytes(data, (size_t)size, audit)) {
        return tlv_err_parse();
    }
    if (out_version) {
        *out_version = version;
    }
    return err_ok();
}

static err_t validate_handshake(const unsigned char* data,
                                u32 size,
                                u32* out_version) {
    err_t err;
    LauncherHandshake hs;
    u32 version = 0u;
    err = tlv_read_schema_version(data, size, (u32)LAUNCHER_HANDSHAKE_TLV_VERSION, &version);
    if (!err_is_ok(&err)) {
        return err;
    }
    if (version != (u32)LAUNCHER_HANDSHAKE_TLV_VERSION) {
        return tlv_err_schema(version);
    }
    if (!launcher_handshake_from_tlv_bytes(data, (size_t)size, hs)) {
        return tlv_err_parse();
    }
    if (out_version) {
        *out_version = version;
    }
    return err_ok();
}

static err_t validate_selection_summary(const unsigned char* data,
                                        u32 size,
                                        u32* out_version) {
    err_t err;
    LauncherSelectionSummary s;
    u32 version = 0u;
    err = tlv_read_schema_version(data, size, (u32)LAUNCHER_SELECTION_SUMMARY_TLV_VERSION, &version);
    if (!err_is_ok(&err)) {
        return err;
    }
    if (version != (u32)LAUNCHER_SELECTION_SUMMARY_TLV_VERSION) {
        return tlv_err_schema(version);
    }
    if (!launcher_selection_summary_from_tlv_bytes(data, (size_t)size, s)) {
        return tlv_err_parse();
    }
    if (out_version) {
        *out_version = version;
    }
    return err_ok();
}

static err_t validate_tools_registry(const unsigned char* data,
                                     u32 size,
                                     u32* out_version) {
    err_t err;
    LauncherToolsRegistry reg;
    u32 version = 0u;
    err = tlv_read_schema_version(data, size, (u32)LAUNCHER_TOOLS_REGISTRY_TLV_VERSION, &version);
    if (!err_is_ok(&err)) {
        return err;
    }
    if (version != (u32)LAUNCHER_TOOLS_REGISTRY_TLV_VERSION) {
        return tlv_err_schema(version);
    }
    if (!launcher_tools_registry_from_tlv_bytes(data, (size_t)size, reg)) {
        return tlv_err_parse();
    }
    if (out_version) {
        *out_version = version;
    }
    return err_ok();
}

static err_t validate_caps_snapshot(const unsigned char* data,
                                    u32 size,
                                    u32* out_version) {
    err_t err;
    u32 version = 0u;
    err = tlv_read_schema_version(data, size, 1u, &version);
    if (!err_is_ok(&err)) {
        return err;
    }
    if (version != 1u) {
        return tlv_err_schema(version);
    }
    if (out_version) {
        *out_version = version;
    }
    return err_ok();
}

static err_t validate_bundle_meta(const unsigned char* data,
                                  u32 size,
                                  u32* out_version) {
    return validate_caps_snapshot(data, size, out_version);
}

static err_t validate_bundle_index(const unsigned char* data,
                                   u32 size,
                                   u32* out_version) {
    return validate_caps_snapshot(data, size, out_version);
}

} /* namespace */

int launcher_register_tlv_schemas(void) {
    core_tlv_schema_entry entries[] = {
        {CORE_TLV_SCHEMA_LAUNCHER_INSTANCE_MANIFEST,
         "launcher.instance_manifest",
         (u32)LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION,
         launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST),
         (u32)LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION,
         validate_instance_manifest,
         migrate_instance_manifest},

        {CORE_TLV_SCHEMA_LAUNCHER_PACK_MANIFEST,
         "launcher.pack_manifest",
         (u32)LAUNCHER_PACK_MANIFEST_TLV_VERSION,
         launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_PACK_MANIFEST),
         (u32)LAUNCHER_PACK_MANIFEST_TLV_VERSION,
         validate_pack_manifest,
         tlv_identity_migrate},

        {CORE_TLV_SCHEMA_LAUNCHER_AUDIT_LOG,
         "launcher.audit_log",
         (u32)LAUNCHER_AUDIT_TLV_VERSION,
         launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_AUDIT_LOG),
         (u32)LAUNCHER_AUDIT_TLV_VERSION,
         validate_audit_log,
         tlv_identity_migrate},

        {CORE_TLV_SCHEMA_LAUNCHER_HANDSHAKE,
         "launcher.handshake",
         (u32)LAUNCHER_HANDSHAKE_TLV_VERSION,
         (u32)LAUNCHER_HANDSHAKE_TLV_VERSION,
         (u32)LAUNCHER_HANDSHAKE_TLV_VERSION,
         validate_handshake,
         tlv_identity_migrate},

        {CORE_TLV_SCHEMA_LAUNCHER_SELECTION_SUMMARY,
         "launcher.selection_summary",
         (u32)LAUNCHER_SELECTION_SUMMARY_TLV_VERSION,
         (u32)LAUNCHER_SELECTION_SUMMARY_TLV_VERSION,
         (u32)LAUNCHER_SELECTION_SUMMARY_TLV_VERSION,
         validate_selection_summary,
         tlv_identity_migrate},

        {CORE_TLV_SCHEMA_LAUNCHER_TOOLS_REGISTRY,
         "launcher.tools_registry",
         (u32)LAUNCHER_TOOLS_REGISTRY_TLV_VERSION,
         (u32)LAUNCHER_TOOLS_REGISTRY_TLV_VERSION,
         (u32)LAUNCHER_TOOLS_REGISTRY_TLV_VERSION,
         validate_tools_registry,
         tlv_identity_migrate},

        {CORE_TLV_SCHEMA_LAUNCHER_CAPS_SNAPSHOT,
         "launcher.caps_snapshot",
         1u,
         1u,
         1u,
         validate_caps_snapshot,
         tlv_identity_migrate},

        {CORE_TLV_SCHEMA_DIAG_BUNDLE_META,
         "diagnostics.bundle_meta",
         1u,
         1u,
         1u,
         validate_bundle_meta,
         tlv_identity_migrate},

        {CORE_TLV_SCHEMA_DIAG_BUNDLE_INDEX,
         "diagnostics.bundle_index",
         1u,
         1u,
         1u,
         validate_bundle_index,
         tlv_identity_migrate}
    };

    size_t i;
    int ok = 1;
    for (i = 0u; i < sizeof(entries) / sizeof(entries[0]); ++i) {
        core_tlv_schema_result res = core_tlv_schema_register(&entries[i]);
        if (res != CORE_TLV_SCHEMA_OK && res != CORE_TLV_SCHEMA_ERR_CONFLICT) {
            ok = 0;
        }
    }
    return ok;
}

} /* namespace launcher_core */
} /* namespace dom */
