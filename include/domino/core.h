/*
FILE: include/domino/core.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core
RESPONSIBILITY: Defines the public contract for `core` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
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

typedef enum dom_status {
    DOM_STATUS_OK = 0,
    DOM_STATUS_ERROR = -1,
    DOM_STATUS_INVALID_ARGUMENT = -2,
    DOM_STATUS_UNSUPPORTED = -3,
    DOM_STATUS_NOT_FOUND = -4
} dom_status;

typedef struct dom_core_t dom_core;

typedef struct dom_core_desc {
    uint32_t api_version;
} dom_core_desc;

typedef uint32_t dom_cmd_id;
typedef uint32_t dom_query_id;

enum {
    DOM_CMD_NOP = 0u,

    DOM_CMD_PKG_INSTALL  = 0x00010000u,
    DOM_CMD_PKG_UNINSTALL = 0x00010001u,

    DOM_CMD_INST_CREATE = 0x00020000u,
    DOM_CMD_INST_UPDATE = 0x00020001u,
    DOM_CMD_INST_DELETE = 0x00020002u,

    DOM_CMD_SIM_TICK = 0x00030000u
};

enum {
    DOM_QUERY_CORE_INFO = 0u,

    DOM_QUERY_PKG_LIST = 0x00010000u,
    DOM_QUERY_PKG_INFO = 0x00010001u,

    DOM_QUERY_INST_LIST = 0x00020000u,
    DOM_QUERY_INST_INFO = 0x00020001u,

    DOM_QUERY_SIM_STATE = 0x00030000u
};

typedef struct dom_cmd {
    dom_cmd_id  id;
    const void* data;
    size_t      size;
} dom_cmd;

typedef struct dom_query {
    dom_query_id id;
    const void*  in;
    size_t       in_size;
    void*        out;
    size_t       out_size;
} dom_query;

typedef struct dom_cmd_pkg_install {
    const char* source_path;
} dom_cmd_pkg_install;

typedef struct dom_cmd_pkg_uninstall {
    dom_package_id id;
} dom_cmd_pkg_uninstall;

typedef struct dom_cmd_inst_create {
    dom_instance_info info;
} dom_cmd_inst_create;

typedef struct dom_cmd_inst_update {
    dom_instance_info info;
} dom_cmd_inst_update;

typedef struct dom_cmd_inst_delete {
    dom_instance_id id;
} dom_cmd_inst_delete;

typedef struct dom_cmd_sim_tick {
    dom_instance_id id;
    uint32_t        ticks;
} dom_cmd_sim_tick;

typedef struct dom_query_core_info_out {
    uint32_t struct_size;
    uint32_t struct_version;
    uint32_t api_version;
    uint32_t package_count;
    uint32_t instance_count;
} dom_query_core_info_out;

typedef struct dom_query_pkg_list_out {
    dom_package_info* items;
    uint32_t          max_items;
    uint32_t          count;
} dom_query_pkg_list_out;

typedef struct dom_query_pkg_info_in {
    dom_package_id id;
} dom_query_pkg_info_in;

typedef struct dom_query_pkg_info_out {
    dom_package_id  id;
    dom_package_info info;
} dom_query_pkg_info_out;

typedef struct dom_query_inst_list_out {
    dom_instance_info* items;
    uint32_t           max_items;
    uint32_t           count;
} dom_query_inst_list_out;

typedef struct dom_query_inst_info_in {
    dom_instance_id id;
} dom_query_inst_info_in;

typedef struct dom_query_inst_info_out {
    dom_instance_id  id;
    dom_instance_info info;
} dom_query_inst_info_out;

typedef struct dom_query_sim_state_in {
    dom_instance_id id;
} dom_query_sim_state_in;

typedef struct dom_query_sim_state_out {
    dom_instance_id id;
    dom_sim_state   state;
} dom_query_sim_state_out;

dom_core* dom_core_create(const dom_core_desc* desc);
void      dom_core_destroy(dom_core* core);
bool      dom_core_execute(dom_core* core, const dom_cmd* cmd);
bool      dom_core_query(dom_core* core, dom_query* q);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_CORE_H_INCLUDED */
