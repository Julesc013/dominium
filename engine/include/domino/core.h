/*
FILE: include/domino/core.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core
RESPONSIBILITY: Defines the public contract for `core` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_CORE_H_INCLUDED
#define DOMINO_CORE_H_INCLUDED

#include <stddef.h>
#include "domino/baseline.h"
#include "domino/sys.h"
#include "domino/pkg.h"
#include "domino/inst.h"
#include "domino/sim.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Purpose: Common status codes used by core-facing APIs. */
typedef enum dom_status {
    DOM_STATUS_OK = 0,
    DOM_STATUS_ERROR = -1,
    DOM_STATUS_INVALID_ARGUMENT = -2,
    DOM_STATUS_UNSUPPORTED = -3,
    DOM_STATUS_NOT_FOUND = -4
} dom_status;

/* Purpose: Opaque core context created by `dom_core_create()` and released by `dom_core_destroy()`. */
typedef struct dom_core_t dom_core;

/* Purpose: Core creation parameters (POD). */
typedef struct dom_core_desc {
    uint32_t api_version;
} dom_core_desc;

/* Purpose: Command identifier used in `dom_cmd.id`. */
typedef uint32_t dom_cmd_id;
/* Purpose: Query identifier used in `dom_query.id`. */
typedef uint32_t dom_query_id;

/* Purpose: Command ids for `dom_core_execute()` (`dom_cmd.id`) and their payload structs. */
enum {
    DOM_CMD_NOP = 0u,

    DOM_CMD_PKG_INSTALL  = 0x00010000u,
    DOM_CMD_PKG_UNINSTALL = 0x00010001u,

    DOM_CMD_INST_CREATE = 0x00020000u,
    DOM_CMD_INST_UPDATE = 0x00020001u,
    DOM_CMD_INST_DELETE = 0x00020002u,

    DOM_CMD_SIM_TICK = 0x00030000u
};

/* Purpose: Query ids for `dom_core_query()` (`dom_query.id`) and their input/output structs. */
enum {
    DOM_QUERY_CORE_INFO = 0u,

    DOM_QUERY_PKG_LIST = 0x00010000u,
    DOM_QUERY_PKG_INFO = 0x00010001u,

    DOM_QUERY_INST_LIST = 0x00020000u,
    DOM_QUERY_INST_INFO = 0x00020001u,

    DOM_QUERY_SIM_STATE = 0x00030000u
};

/* Purpose: Command envelope for `dom_core_execute()`.
 *
 * Parameters:
 *   - id: Command selector (DOM_CMD_*).
 *   - data/size: Optional payload; interpretation is command-specific.
 */
typedef struct dom_cmd {
    dom_cmd_id  id;
    const void* data;
    size_t      size;
} dom_cmd;

/* Purpose: Query envelope for `dom_core_query()`.
 *
 * Parameters:
 *   - id: Query selector (DOM_QUERY_*).
 *   - in/in_size: Optional request payload (query-specific).
 *   - out/out_size: Optional response buffer (query-specific).
 */
typedef struct dom_query {
    dom_query_id id;
    const void*  in;
    size_t       in_size;
    void*        out;
    size_t       out_size;
} dom_query;

/* Purpose: Payload for `DOM_CMD_PKG_INSTALL` (installs a package from a source path). */
typedef struct dom_cmd_pkg_install {
    const char* source_path;
} dom_cmd_pkg_install;

/* Purpose: Payload for `DOM_CMD_PKG_UNINSTALL` (removes an installed package). */
typedef struct dom_cmd_pkg_uninstall {
    dom_package_id id;
} dom_cmd_pkg_uninstall;

/* Purpose: Payload for `DOM_CMD_INST_CREATE` (creates a new instance). */
typedef struct dom_cmd_inst_create {
    dom_instance_info info;
} dom_cmd_inst_create;

/* Purpose: Payload for `DOM_CMD_INST_UPDATE` (updates an existing instance). */
typedef struct dom_cmd_inst_update {
    dom_instance_info info;
} dom_cmd_inst_update;

/* Purpose: Payload for `DOM_CMD_INST_DELETE` (deletes an existing instance). */
typedef struct dom_cmd_inst_delete {
    dom_instance_id id;
} dom_cmd_inst_delete;

/* Purpose: Payload for `DOM_CMD_SIM_TICK` (advances simulation for an instance). */
typedef struct dom_cmd_sim_tick {
    dom_instance_id id;
    uint32_t        ticks;
} dom_cmd_sim_tick;

/* Purpose: Output payload for `DOM_QUERY_CORE_INFO`. */
typedef struct dom_query_core_info_out {
    uint32_t struct_size;
    uint32_t struct_version;
    uint32_t api_version;
    uint32_t package_count;
    uint32_t instance_count;
} dom_query_core_info_out;

/* Purpose: Output payload for `DOM_QUERY_PKG_LIST`. */
typedef struct dom_query_pkg_list_out {
    dom_package_info* items;
    uint32_t          max_items;
    uint32_t          count;
} dom_query_pkg_list_out;

/* Purpose: Input payload for `DOM_QUERY_PKG_INFO`. */
typedef struct dom_query_pkg_info_in {
    dom_package_id id;
} dom_query_pkg_info_in;

/* Purpose: Output payload for `DOM_QUERY_PKG_INFO`. */
typedef struct dom_query_pkg_info_out {
    dom_package_id  id;
    dom_package_info info;
} dom_query_pkg_info_out;

/* Purpose: Output payload for `DOM_QUERY_INST_LIST`. */
typedef struct dom_query_inst_list_out {
    dom_instance_info* items;
    uint32_t           max_items;
    uint32_t           count;
} dom_query_inst_list_out;

/* Purpose: Input payload for `DOM_QUERY_INST_INFO`. */
typedef struct dom_query_inst_info_in {
    dom_instance_id id;
} dom_query_inst_info_in;

/* Purpose: Output payload for `DOM_QUERY_INST_INFO`. */
typedef struct dom_query_inst_info_out {
    dom_instance_id  id;
    dom_instance_info info;
} dom_query_inst_info_out;

/* Purpose: Input payload for `DOM_QUERY_SIM_STATE`. */
typedef struct dom_query_sim_state_in {
    dom_instance_id id;
} dom_query_sim_state_in;

/* Purpose: Output payload for `DOM_QUERY_SIM_STATE`. */
typedef struct dom_query_sim_state_out {
    dom_instance_id id;
    dom_sim_state   state;
} dom_query_sim_state_out;

/* Purpose: Create a new core context.
 *
 * Parameters:
 *   - desc: Optional creation parameters; may be NULL.
 *
 * Returns:
 *   - Non-NULL core handle on success; NULL on allocation failure.
 *
 * Side effects:
 *   - Performs initial package/instance discovery as part of creation.
 */
dom_core* dom_core_create(const dom_core_desc* desc);

/* Purpose: Destroy a core context. Accepts NULL. */
void      dom_core_destroy(dom_core* core);

/* Purpose: Execute a command against the core.
 *
 * Returns:
 *   - true on success; false on validation failure or operation failure.
 */
bool      dom_core_execute(dom_core* core, const dom_cmd* cmd);

/* Purpose: Execute a query against the core.
 *
 * Parameters:
 *   - q: In/out query descriptor; query-specific payloads are provided via `q->in` and `q->out`.
 *
 * Returns:
 *   - true on success; false on validation failure or operation failure.
 */
bool      dom_core_query(dom_core* core, dom_query* q);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_CORE_H_INCLUDED */
