/*
FILE: source/dominium/launcher/core/src/profile/launcher_profile.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / profile
RESPONSIBILITY: Implements launcher profile model + TLV persistence.
*/

#include "launcher_profile.h"

#include "launcher_tlv.h"
#include "launcher_tlv_migrations.h"

namespace dom {
namespace launcher_core {

namespace {
enum {
    TAG_PROFILE_ID = 2u,
    TAG_ALLOWED_BACKEND = 3u,
    TAG_POLICY_FLAGS = 4u,
    TAG_DET_CONSTRAINTS = 5u
};

enum {
    TAG_ALLOW_SUBSYSTEM_KEY = 1u,
    TAG_ALLOW_BACKEND_NAME = 2u
};
}

LauncherProfile::LauncherProfile()
    : schema_version(LAUNCHER_PROFILE_TLV_VERSION),
      profile_id(),
      allowed_backends(),
      policy_flags(0u),
      determinism_constraints(0u) {
}

LauncherProfile launcher_profile_make_null(void) {
    LauncherProfile p;
    p.profile_id = "null";
    p.policy_flags = 0u;
    p.determinism_constraints = 0u;
    return p;
}

bool launcher_profile_to_tlv_bytes(const LauncherProfile& profile,
                                   std::vector<unsigned char>& out_bytes) {
    TlvWriter w;
    size_t i;

    w.add_u32(LAUNCHER_TLV_TAG_SCHEMA_VERSION, LAUNCHER_PROFILE_TLV_VERSION);
    w.add_string(TAG_PROFILE_ID, profile.profile_id);
    w.add_u32(TAG_POLICY_FLAGS, profile.policy_flags);
    w.add_u32(TAG_DET_CONSTRAINTS, profile.determinism_constraints);

    for (i = 0u; i < profile.allowed_backends.size(); ++i) {
        TlvWriter entry;
        entry.add_string(TAG_ALLOW_SUBSYSTEM_KEY, profile.allowed_backends[i].subsystem_key);
        entry.add_string(TAG_ALLOW_BACKEND_NAME, profile.allowed_backends[i].backend_name);
        w.add_container(TAG_ALLOWED_BACKEND, entry.bytes());
    }

    out_bytes = w.bytes();
    return true;
}

bool launcher_profile_from_tlv_bytes(const unsigned char* data,
                                     size_t size,
                                     LauncherProfile& out_profile) {
    TlvReader r(data, size);
    TlvRecord rec;
    u32 version = 0u;

    out_profile = LauncherProfile();
    if (!tlv_read_schema_version_or_default(data, size, version, launcher_tlv_schema_min_version(LAUNCHER_TLV_SCHEMA_PROFILE))) {
        return false;
    }
    if (!launcher_tlv_schema_accepts_version(LAUNCHER_TLV_SCHEMA_PROFILE, version)) {
        return false;
    }
    out_profile.schema_version = launcher_tlv_schema_current_version(LAUNCHER_TLV_SCHEMA_PROFILE);

    while (r.next(rec)) {
        switch (rec.tag) {
        case LAUNCHER_TLV_TAG_SCHEMA_VERSION:
            break;
        case TAG_PROFILE_ID:
            out_profile.profile_id = tlv_read_string(rec.payload, rec.len);
            break;
        case TAG_POLICY_FLAGS: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                out_profile.policy_flags = v;
            }
            break;
        }
        case TAG_DET_CONSTRAINTS: {
            u32 v;
            if (tlv_read_u32_le(rec.payload, rec.len, v)) {
                out_profile.determinism_constraints = v;
            }
            break;
        }
        case TAG_ALLOWED_BACKEND: {
            LauncherBackendAllow allow;
            TlvReader er(rec.payload, (size_t)rec.len);
            TlvRecord e;
            while (er.next(e)) {
                if (e.tag == TAG_ALLOW_SUBSYSTEM_KEY) {
                    allow.subsystem_key = tlv_read_string(e.payload, e.len);
                } else if (e.tag == TAG_ALLOW_BACKEND_NAME) {
                    allow.backend_name = tlv_read_string(e.payload, e.len);
                } else {
                    /* skip unknown */
                }
            }
            if (!allow.subsystem_key.empty() || !allow.backend_name.empty()) {
                out_profile.allowed_backends.push_back(allow);
            }
            break;
        }
        default:
            /* skip unknown tags */
            break;
        }
    }
    return true;
}

bool launcher_profile_migrate_tlv(u32 /*from_version*/,
                                  u32 /*to_version*/,
                                  const unsigned char* /*data*/,
                                  size_t /*size*/,
                                  LauncherProfile& /*out_profile*/) {
    /* Defined but not implemented in foundation. */
    return false;
}

} /* namespace launcher_core */
} /* namespace dom */
