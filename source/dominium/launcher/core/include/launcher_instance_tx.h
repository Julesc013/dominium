/*
FILE: source/dominium/launcher/core/include/launcher_instance_tx.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / instance_tx
RESPONSIBILITY: Transaction state machine for instance mutations (prepare/stage/verify/commit/rollback) with staging-only writes.
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher core manifest/TLV/types; services facade.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/false; no exceptions required.
DETERMINISM: Explicit state transitions; no filesystem enumeration ordering is relied upon.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_TX_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_TX_H

#include <string>

extern "C" {
#include "launcher_core_api.h"
}

#include "dominium/core_err.h"

#include "launcher_instance.h"
#include "launcher_instance_ops.h"
#include "launcher_instance_payload_refs.h"

namespace dom {
namespace launcher_core {

struct LauncherAuditLog; /* forward-declared; see launcher_audit.h */

enum LauncherInstanceTxOpType {
    LAUNCHER_INSTANCE_TX_OP_INSTALL = 1u,
    LAUNCHER_INSTANCE_TX_OP_UPDATE = 2u,
    LAUNCHER_INSTANCE_TX_OP_REMOVE = 3u,
    LAUNCHER_INSTANCE_TX_OP_VERIFY = 4u,
    LAUNCHER_INSTANCE_TX_OP_REPAIR = 5u,
    LAUNCHER_INSTANCE_TX_OP_ROLLBACK = 6u
};

enum LauncherInstanceTxPhase {
    LAUNCHER_INSTANCE_TX_PHASE_NONE = 0u,
    LAUNCHER_INSTANCE_TX_PHASE_PREPARE = 1u,
    LAUNCHER_INSTANCE_TX_PHASE_STAGE = 2u,
    LAUNCHER_INSTANCE_TX_PHASE_VERIFY = 3u,
    LAUNCHER_INSTANCE_TX_PHASE_COMMIT = 4u,
    LAUNCHER_INSTANCE_TX_PHASE_ROLLBACK = 5u,
    LAUNCHER_INSTANCE_TX_PHASE_DONE = 6u
};

/* transaction.tlv schema version. */
enum { LAUNCHER_INSTANCE_TX_TLV_VERSION = 1u };

/* transaction.tlv root records:
 * - `LAUNCHER_TLV_TAG_SCHEMA_VERSION` (u32)
 * - `LAUNCHER_INSTANCE_TX_TLV_TAG_TX_ID` (u64)
 * - `LAUNCHER_INSTANCE_TX_TLV_TAG_INSTANCE_ID` (string)
 * - `LAUNCHER_INSTANCE_TX_TLV_TAG_OP_TYPE` (u32)
 * - `LAUNCHER_INSTANCE_TX_TLV_TAG_PHASE` (u32)
 * - `LAUNCHER_INSTANCE_TX_TLV_TAG_BEFORE_MANIFEST_HASH64` (u64)
 * - `LAUNCHER_INSTANCE_TX_TLV_TAG_AFTER_MANIFEST_HASH64` (u64)
 */
enum LauncherInstanceTxTlvTag {
    LAUNCHER_INSTANCE_TX_TLV_TAG_TX_ID = 2u,
    LAUNCHER_INSTANCE_TX_TLV_TAG_INSTANCE_ID = 3u,
    LAUNCHER_INSTANCE_TX_TLV_TAG_OP_TYPE = 4u,
    LAUNCHER_INSTANCE_TX_TLV_TAG_PHASE = 5u,
    LAUNCHER_INSTANCE_TX_TLV_TAG_BEFORE_MANIFEST_HASH64 = 6u,
    LAUNCHER_INSTANCE_TX_TLV_TAG_AFTER_MANIFEST_HASH64 = 7u
};

struct LauncherInstanceTx {
    u32 schema_version;
    u64 tx_id;
    std::string instance_id;
    std::string state_root;

    u32 op_type;
    u32 phase;

    u64 before_manifest_hash64;
    u64 after_manifest_hash64;

    LauncherInstanceManifest before_manifest;
    LauncherInstanceManifest after_manifest;

    LauncherInstanceTx();
};

/* Loads transaction.tlv if present for an instance (staging only). */
bool launcher_instance_tx_load(const launcher_services_api_v1* services,
                               const std::string& instance_id,
                               const std::string& state_root_override,
                               LauncherInstanceTx& out_tx);

/* Clears partial staging for an instance if present.
 * Safe to call on every run; does not modify live instance state.
 */
bool launcher_instance_tx_recover_staging(const launcher_services_api_v1* services,
                                          const std::string& instance_id,
                                          const std::string& state_root_override,
                                          LauncherAuditLog* audit);

/* Prepare: loads the live manifest, creates a transaction id, and persists transaction.tlv with phase=prepare. */
bool launcher_instance_tx_prepare(const launcher_services_api_v1* services,
                                  const std::string& instance_id,
                                  const std::string& state_root_override,
                                  u32 op_type,
                                  LauncherInstanceTx& out_tx,
                                  LauncherAuditLog* audit);

/* Stage: writes staged manifest to `staging/manifest.tlv` and updates transaction.tlv to phase=stage. */
bool launcher_instance_tx_stage(const launcher_services_api_v1* services,
                                LauncherInstanceTx& tx,
                                LauncherAuditLog* audit);
bool launcher_instance_tx_stage_ex(const launcher_services_api_v1* services,
                                   LauncherInstanceTx& tx,
                                   LauncherAuditLog* audit,
                                   err_t* out_err);

/* Verify: verifies all enabled artifacts in `after_manifest` against the artifact store and
 * writes `staging/payload_refs.tlv` for commit.
 */
bool launcher_instance_tx_verify(const launcher_services_api_v1* services,
                                 LauncherInstanceTx& tx,
                                 LauncherAuditLog* audit);

/* Commit: atomically swaps staged manifest/payload_refs into place and archives prior state under `previous/`. */
bool launcher_instance_tx_commit(const launcher_services_api_v1* services,
                                 LauncherInstanceTx& tx,
                                 LauncherAuditLog* audit);
bool launcher_instance_tx_commit_ex(const launcher_services_api_v1* services,
                                    LauncherInstanceTx& tx,
                                    LauncherAuditLog* audit,
                                    err_t* out_err);

/* Rollback: discards staged files and marks transaction done (live instance remains untouched). */
bool launcher_instance_tx_rollback(const launcher_services_api_v1* services,
                                   LauncherInstanceTx& tx,
                                   LauncherAuditLog* audit);
bool launcher_instance_tx_rollback_ex(const launcher_services_api_v1* services,
                                      LauncherInstanceTx& tx,
                                      LauncherAuditLog* audit,
                                      err_t* out_err);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_INSTANCE_TX_H */
