/*
FILE: source/dominium/launcher/core/include/launcher_job.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / job
RESPONSIBILITY: Resumable job journaling + execution wrapper for long launcher operations.
ALLOWED DEPENDENCIES: C++98 standard headers and `include/domino/**` base types; launcher core models/services.
FORBIDDEN DEPENDENCIES: OS headers, renderer/UI headers, and any Plan 8 contract changes.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Returns bool + err_t (deterministic); no exceptions required.
DETERMINISM: Job graph + journal TLVs are deterministic; no filesystem enumeration ordering required.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_JOB_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_JOB_H

#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "dominium/core_job.h"
#include "dominium/core_err.h"

#include "launcher_core_api.h"
#include "launcher_prelaunch.h"

namespace dom {
namespace launcher_core {

/*------------------------------------------------------------
 * Job input model (TLV-backed, append-only).
 *------------------------------------------------------------*/
enum { LAUNCHER_JOB_INPUT_TLV_VERSION = 1u };

struct LauncherJobPackChange {
    u32 content_type;
    std::string pack_id;
    u32 has_enabled;
    u32 enabled;
    u32 has_update_policy;
    u32 update_policy;

    LauncherJobPackChange();
};

struct LauncherJobInput {
    u32 schema_version;
    u32 job_type; /* core_job_type */

    std::string instance_id;
    std::string path;     /* import/export root, diag out path */
    std::string aux_path; /* script path or auxiliary root */
    std::string aux_id;   /* format or auxiliary id */

    u32 mode;  /* job-specific mode */
    u32 flags; /* job-specific flags */

    LauncherLaunchOverrides overrides; /* launch-prepare overrides */
    std::vector<LauncherJobPackChange> pack_changes; /* pack apply */

    LauncherJobInput();
};

bool launcher_job_input_to_tlv_bytes(const LauncherJobInput& in,
                                     std::vector<unsigned char>& out_bytes);
bool launcher_job_input_from_tlv_bytes(const unsigned char* data,
                                       size_t size,
                                       LauncherJobInput& out_in);

/*------------------------------------------------------------
 * Job execution (creates journal if needed, runs/resumes steps).
 *------------------------------------------------------------*/
bool launcher_job_run(const launcher_services_api_v1* services,
                      const LauncherJobInput& input,
                      const std::string& state_root_override,
                      core_job_state& out_state,
                      err_t* out_err,
                      LauncherAuditLog* out_audit);

bool launcher_job_resume(const launcher_services_api_v1* services,
                         const std::string& state_root_override,
                         const std::string& instance_id,
                         u64 job_id,
                         core_job_state& out_state,
                         err_t* out_err,
                         LauncherAuditLog* out_audit);

bool launcher_job_state_load(const launcher_services_api_v1* services,
                             const std::string& state_root_override,
                             const std::string& instance_id,
                             u64 job_id,
                             core_job_state& out_state);

/* Launch-prep helper: runs job and returns a prelaunch plan when successful. */
bool launcher_job_run_launch_prepare(const launcher_services_api_v1* services,
                                     const std::string& instance_id,
                                     const std::string& state_root_override,
                                     const LauncherLaunchOverrides& overrides,
                                     LauncherPrelaunchPlan& out_plan,
                                     err_t* out_err);

} /* namespace launcher_core */
} /* namespace dom */

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_JOB_H */
