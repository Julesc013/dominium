/*
FILE: source/dominium/launcher/core/include/launcher_core_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/core (foundation) / api
RESPONSIBILITY: Launcher core entrypoints and the launcher services facade (C ABI, versioned, capability-gated).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS headers, UI toolkit headers, renderer assumptions.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes/NULL pointers; no exceptions across ABI boundaries.
DETERMINISM: Core decisions are deterministic given explicit inputs; no hidden OS time or randomness is used.
VERSIONING / ABI / DATA FORMAT NOTES: Facade structs use `DOM_ABI_HEADER` and `query_interface` per `docs/SPEC_ABI_TEMPLATES.md`.
EXTENSION POINTS: Extend via new IIDs + capability bits; skip-unknown TLV for persistence.
*/
#ifndef DOMINIUM_LAUNCHER_CORE_LAUNCHER_CORE_API_H
#define DOMINIUM_LAUNCHER_CORE_LAUNCHER_CORE_API_H

#include <stddef.h>

#include "domino/abi.h"
#include "domino/baseline.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Launcher services facade (C ABI)
 *------------------------------------------------------------*/

typedef u64 launcher_services_caps;

#define LAUNCHER_SERVICES_CAP_FILESYSTEM   ((launcher_services_caps)1u << 0u)
#define LAUNCHER_SERVICES_CAP_NETWORKING   ((launcher_services_caps)1u << 1u)
#define LAUNCHER_SERVICES_CAP_PROCESS      ((launcher_services_caps)1u << 2u)
#define LAUNCHER_SERVICES_CAP_HASHING      ((launcher_services_caps)1u << 3u)
#define LAUNCHER_SERVICES_CAP_ARCHIVE      ((launcher_services_caps)1u << 4u)
#define LAUNCHER_SERVICES_CAP_TIME         ((launcher_services_caps)1u << 5u)

/* Interface IDs (IIDs) for query_interface. */
#define LAUNCHER_IID_FS_V1     ((dom_iid)0x4C465331u) /* 'LFS1' */
#define LAUNCHER_IID_NET_V1    ((dom_iid)0x4C4E4554u) /* 'LNET' */
#define LAUNCHER_IID_PROC_V1   ((dom_iid)0x4C505243u) /* 'LPRC' */
#define LAUNCHER_IID_HASH_V1   ((dom_iid)0x4C485348u) /* 'LHSH' */
#define LAUNCHER_IID_ARCH_V1   ((dom_iid)0x4C415243u) /* 'LARC' */
#define LAUNCHER_IID_TIME_V1   ((dom_iid)0x4C54494Du) /* 'LTIM' */

typedef enum launcher_fs_path_kind_e {
    LAUNCHER_FS_PATH_NONE = 0,
    LAUNCHER_FS_PATH_STATE = 1,
    LAUNCHER_FS_PATH_AUDIT = 2
} launcher_fs_path_kind;

/* launcher_fs_api_v1: Filesystem capability (C89, no OS headers). */
typedef struct launcher_fs_api_v1 {
    DOM_ABI_HEADER;

    bool   (*get_path)(launcher_fs_path_kind kind, char* buf, size_t buf_size);

    void*  (*file_open)(const char* path, const char* mode);
    size_t (*file_read)(void* fh, void* buf, size_t size);
    size_t (*file_write)(void* fh, const void* buf, size_t size);
    int    (*file_seek)(void* fh, long offset, int origin);
    long   (*file_tell)(void* fh);
    int    (*file_close)(void* fh);
} launcher_fs_api_v1;

/* launcher_time_api_v1: Monotonic time capability. */
typedef struct launcher_time_api_v1 {
    DOM_ABI_HEADER;
    u64 (*now_us)(void);
} launcher_time_api_v1;

/* launcher_process_api_v1: Process spawn capability (opaque handles). */
typedef struct launcher_process launcher_process;

typedef struct launcher_process_desc_v1 {
    u32 struct_size;
    u32 struct_version;
    const char* path;            /* executable path */
    const char* const* argv;     /* argv array (borrowed) */
    u32 argv_count;
    const char* workdir;         /* optional */
} launcher_process_desc_v1;

typedef struct launcher_process_api_v1 {
    DOM_ABI_HEADER;
    launcher_process* (*spawn)(const launcher_process_desc_v1* desc);
    int               (*wait)(launcher_process* p);
    void              (*destroy)(launcher_process* p);
} launcher_process_api_v1;

/* launcher_hash_api_v1: Hashing/crypto capability (minimal for foundation). */
typedef struct launcher_hash_api_v1 {
    DOM_ABI_HEADER;
    u64 (*fnv1a64)(const void* data, u32 len);
} launcher_hash_api_v1;

/* launcher_archive_api_v1: Archive extraction capability (reserved; not implemented in foundation). */
typedef struct launcher_archive_api_v1 {
    DOM_ABI_HEADER;
    void* reserved0;
    void* reserved1;
} launcher_archive_api_v1;

/* launcher_net_api_v1: Networking capability (reserved; not implemented in foundation). */
typedef struct launcher_net_api_v1 {
    DOM_ABI_HEADER;
    void* reserved0;
    void* reserved1;
} launcher_net_api_v1;

/* launcher_services_api_v1: Root facade that exposes capability bits and query_interface. */
typedef struct launcher_services_api_v1 {
    DOM_ABI_HEADER;
    launcher_services_caps (*get_caps)(void);
    dom_query_interface_fn  query_interface;
} launcher_services_api_v1;

/* Null backend (headless-friendly). */
const launcher_services_api_v1* launcher_services_null_v1(void);

/*------------------------------------------------------------
 * Launcher core entrypoints (C ABI wrapper over C++98 implementation)
 *------------------------------------------------------------*/

typedef struct launcher_core launcher_core;

#define LAUNCHER_CORE_DESC_VERSION 1u
typedef struct launcher_core_desc_v1 {
    u32 struct_size;
    u32 struct_version;

    const launcher_services_api_v1* services; /* required (may be null backend) */

    const char* audit_output_path;  /* optional; if NULL core uses a default in CWD */
    const char* selected_profile_id;/* optional; used for audit */

    const char* const* argv;        /* optional; recorded in audit as inputs */
    u32 argv_count;
} launcher_core_desc_v1;

launcher_core* launcher_core_create(const launcher_core_desc_v1* desc);
void           launcher_core_destroy(launcher_core* core);

/* Null/headless smoke helpers (required by prompt). */
int launcher_core_load_null_profile(launcher_core* core);
int launcher_core_create_empty_instance(launcher_core* core, const char* instance_id);

/* Audit enrichment (deterministic; no side effects). */
int launcher_core_add_reason(launcher_core* core, const char* reason);
int launcher_core_select_profile_id(launcher_core* core, const char* profile_id, const char* why);
int launcher_core_set_version_string(launcher_core* core, const char* version_string);
int launcher_core_set_build_id(launcher_core* core, const char* build_id);
int launcher_core_set_git_hash(launcher_core* core, const char* git_hash);
int launcher_core_add_selected_backend(launcher_core* core,
                                       u32 subsystem_id,
                                       const char* subsystem_name,
                                       const char* backend_name,
                                       u32 determinism_grade,
                                       u32 perf_class,
                                       u32 priority,
                                       u32 chosen_by_override);

/* Finalize + persist audit TLV. Returns 0 on success, -1 on failure. */
int launcher_core_emit_audit(launcher_core* core, int exit_result);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LAUNCHER_CORE_LAUNCHER_CORE_API_H */
