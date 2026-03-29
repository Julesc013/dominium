/*
FILE: source/dominium/launcher/core/src/tlv/launcher_tlv_migrations.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / tlv
RESPONSIBILITY: Implements TLV schema registry and migration dispatch.
*/

#include "launcher_tlv_migrations.h"

#include "launcher_audit.h"
#include "launcher_artifact_store.h"
#include "launcher_instance.h"
#include "launcher_instance_config.h"
#include "launcher_instance_known_good.h"
#include "launcher_instance_launch_history.h"
#include "launcher_instance_payload_refs.h"
#include "launcher_instance_tx.h"
#include "launcher_pack_manifest.h"
#include "launcher_prelaunch.h"
#include "launcher_profile.h"

namespace dom {
namespace launcher_core {

namespace {

static bool migrate_instance_manifest_bytes(u32 from_version,
                                            u32 to_version,
                                            const unsigned char* data,
                                            size_t size,
                                            std::vector<unsigned char>& out_bytes) {
    LauncherInstanceManifest m;
    if (!launcher_instance_manifest_migrate_tlv(from_version, to_version, data, size, m)) {
        return false;
    }
    return launcher_instance_manifest_to_tlv_bytes(m, out_bytes);
}

struct SchemaEntry {
    LauncherTlvSchemaSpec spec;
    launcher_tlv_migrate_bytes_fn migrate_bytes;
};

static const SchemaEntry kSchemas[] = {
    /* Audit / profile */
    {{(u32)LAUNCHER_TLV_SCHEMA_AUDIT_LOG, "audit_log", 1u, (u32)LAUNCHER_AUDIT_TLV_VERSION}, (launcher_tlv_migrate_bytes_fn)0},
    {{(u32)LAUNCHER_TLV_SCHEMA_PROFILE, "profile", 1u, (u32)LAUNCHER_PROFILE_TLV_VERSION}, (launcher_tlv_migrate_bytes_fn)0},

    /* Instance state */
    {{(u32)LAUNCHER_TLV_SCHEMA_INSTANCE_MANIFEST, "instance_manifest", 1u, (u32)LAUNCHER_INSTANCE_MANIFEST_TLV_VERSION},
     migrate_instance_manifest_bytes},
    {{(u32)LAUNCHER_TLV_SCHEMA_INSTANCE_CONFIG, "instance_config", 1u, (u32)LAUNCHER_INSTANCE_CONFIG_TLV_VERSION},
     (launcher_tlv_migrate_bytes_fn)0},
    {{(u32)LAUNCHER_TLV_SCHEMA_INSTANCE_KNOWN_GOOD, "instance_known_good", 1u, (u32)LAUNCHER_INSTANCE_KNOWN_GOOD_TLV_VERSION},
     (launcher_tlv_migrate_bytes_fn)0},
    {{(u32)LAUNCHER_TLV_SCHEMA_INSTANCE_LAUNCH_HISTORY, "instance_launch_history", 1u, (u32)LAUNCHER_INSTANCE_LAUNCH_HISTORY_TLV_VERSION},
     (launcher_tlv_migrate_bytes_fn)0},
    {{(u32)LAUNCHER_TLV_SCHEMA_INSTANCE_PAYLOAD_REFS, "instance_payload_refs", 1u, (u32)LAUNCHER_INSTANCE_PAYLOAD_REFS_TLV_VERSION},
     (launcher_tlv_migrate_bytes_fn)0},
    {{(u32)LAUNCHER_TLV_SCHEMA_INSTANCE_TX, "instance_tx", 1u, (u32)LAUNCHER_INSTANCE_TX_TLV_VERSION}, (launcher_tlv_migrate_bytes_fn)0},

    /* Artifact store / packs */
    {{(u32)LAUNCHER_TLV_SCHEMA_ARTIFACT_METADATA, "artifact_metadata", 1u, (u32)LAUNCHER_ARTIFACT_METADATA_TLV_VERSION},
     (launcher_tlv_migrate_bytes_fn)0},
    {{(u32)LAUNCHER_TLV_SCHEMA_PACK_MANIFEST, "pack_manifest", 1u, (u32)LAUNCHER_PACK_MANIFEST_TLV_VERSION}, (launcher_tlv_migrate_bytes_fn)0},

    /* Prelaunch */
    {{(u32)LAUNCHER_TLV_SCHEMA_RESOLVED_LAUNCH_CONFIG, "resolved_launch_config", 1u, (u32)LAUNCHER_RESOLVED_LAUNCH_CONFIG_TLV_VERSION},
     (launcher_tlv_migrate_bytes_fn)0},
};

static const SchemaEntry* find_entry(u32 schema_id) {
    size_t i;
    for (i = 0u; i < sizeof(kSchemas) / sizeof(kSchemas[0]); ++i) {
        if (kSchemas[i].spec.schema_id == schema_id) {
            return &kSchemas[i];
        }
    }
    return (const SchemaEntry*)0;
}

} /* namespace */

size_t launcher_tlv_schema_count(void) {
    return sizeof(kSchemas) / sizeof(kSchemas[0]);
}

const LauncherTlvSchemaSpec* launcher_tlv_schema_at(size_t index) {
    if (index >= launcher_tlv_schema_count()) {
        return (const LauncherTlvSchemaSpec*)0;
    }
    return &kSchemas[index].spec;
}

const LauncherTlvSchemaSpec* launcher_tlv_schema_find(u32 schema_id) {
    const SchemaEntry* e = find_entry(schema_id);
    return e ? &e->spec : (const LauncherTlvSchemaSpec*)0;
}

const char* launcher_tlv_schema_name(u32 schema_id) {
    const LauncherTlvSchemaSpec* s = launcher_tlv_schema_find(schema_id);
    return s ? s->name : "unknown";
}

u32 launcher_tlv_schema_min_version(u32 schema_id) {
    const LauncherTlvSchemaSpec* s = launcher_tlv_schema_find(schema_id);
    return s ? s->min_version : 0u;
}

u32 launcher_tlv_schema_current_version(u32 schema_id) {
    const LauncherTlvSchemaSpec* s = launcher_tlv_schema_find(schema_id);
    return s ? s->current_version : 0u;
}

bool launcher_tlv_schema_accepts_version(u32 schema_id, u32 disk_version) {
    const SchemaEntry* e = find_entry(schema_id);
    if (!e) {
        return false;
    }

    if (disk_version == e->spec.current_version) {
        return true;
    }
    if (disk_version < e->spec.current_version) {
        if (disk_version < e->spec.min_version) {
            return false;
        }
        return e->migrate_bytes != (launcher_tlv_migrate_bytes_fn)0;
    }

    /* disk_version > current_version */
    return false;
}

bool launcher_tlv_schema_migrate_bytes(u32 schema_id,
                                       u32 from_version,
                                       u32 to_version,
                                       const unsigned char* data,
                                       size_t size,
                                       std::vector<unsigned char>& out_bytes) {
    const SchemaEntry* e = find_entry(schema_id);
    if (!e) {
        return false;
    }
    if (!e->migrate_bytes) {
        return false;
    }
    if (to_version != e->spec.current_version) {
        return false;
    }
    if (from_version == to_version) {
        out_bytes.clear();
        if (data && size > 0u) {
            out_bytes.assign(data, data + size);
        }
        return true;
    }
    if (from_version > to_version) {
        return false;
    }
    if (from_version < e->spec.min_version) {
        return false;
    }
    return e->migrate_bytes(from_version, to_version, data, size, out_bytes);
}

} /* namespace launcher_core */
} /* namespace dom */

