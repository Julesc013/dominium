/*
FILE: source/domino/core/core_internal.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/core_internal
RESPONSIBILITY: Defines internal contract for `core_internal`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_CORE_INTERNAL_H
#define DOMINO_CORE_INTERNAL_H

#include <stddef.h>
#include <stdint.h>
#include "domino/core.h"
#include "domino/pkg.h"
#include "domino/inst.h"
#include "domino/event.h"
#include "domino/view.h"
#include "domino/model_table.h"
#include "domino/model_tree.h"
#include "domino/sim.h"
#include "domino/canvas.h"
#include "domino/sys.h"
#include "domino/mod.h"

#define DOM_MAX_PACKAGES 32
#define DOM_MAX_INSTANCES 16
#define DOM_MAX_EVENT_HANDLERS 64
#define DOM_MAX_VIEWS 16
#define DOM_MAX_TABLES 16
#define DOM_MAX_TABLE_COLS 16
#define DOM_MAX_TREE_MODELS 8
#define DOM_MAX_SIM_STATES DOM_MAX_INSTANCES
#define DOM_MAX_LAUNCHER_EXT 8

typedef struct dom_event_sub_entry {
    dom_event_kind    kind;
    dom_event_handler fn;
    void*             user;
} dom_event_sub_entry;

typedef struct dom_package_record {
    dom_package_info info;
    int              is_official;
    char             dep_names[DOM_MAX_PACKAGE_DEPS][64];
    uint32_t         dep_name_count;
} dom_package_record;

typedef struct dom_instance_record {
    dom_instance_info info;
} dom_instance_record;

typedef struct dom_sim_instance_state {
    dom_instance_id id;
    uint64_t        ticks;
    uint64_t        sim_time_usec;
    uint32_t        dt_usec;
    uint32_t        ups;
    bool            paused;
} dom_sim_instance_state;

typedef struct dom_table_def {
    const char* id;
    uint32_t    col_count;
    const char* col_ids[DOM_MAX_TABLE_COLS];
} dom_table_def;

struct dom_core_t {
    uint32_t api_version;
    uint64_t tick_counter;

    dom_package_record packages[DOM_MAX_PACKAGES];
    uint32_t           package_count;
    dom_package_id     next_package_id;

    dom_instance_record instances[DOM_MAX_INSTANCES];
    uint32_t            instance_count;
    dom_instance_id     next_instance_id;

    dom_table_def tables[DOM_MAX_TABLES];
    uint32_t      table_count;
    const char* tree_models[DOM_MAX_TREE_MODELS];
    uint32_t    tree_model_count;

    dom_view_desc views[DOM_MAX_VIEWS];
    uint32_t      view_count;

    dom_event_sub_entry event_subs[DOM_MAX_EVENT_HANDLERS];
    uint32_t            event_sub_count;

    dom_sim_instance_state sim_states[DOM_MAX_SIM_STATES];
    uint32_t               sim_state_count;

    dom_launcher_ext_v1 launcher_exts[DOM_MAX_LAUNCHER_EXT];
    uint32_t            launcher_ext_count;
};

void dom_event__publish(dom_core* core, const dom_event* ev);
void dom_core__scan_packages(dom_core* core);
void dom_core__scan_instances(dom_core* core);

void dom_table__register(dom_core* core,
                         const char* id,
                         const char** col_ids,
                         uint32_t col_count);

/* shared helpers */
void dom_copy_string(char* dst, size_t cap, const char* src);
bool dom_path_join(char* dst, size_t cap, const char* a, const char* b);
bool dom_path_join3(char* dst, size_t cap, const char* a, const char* b, const char* c);
bool dom_path_last_segment(const char* path, char* out, size_t cap);
bool dom_fs_read_text(const char* path, char* buf, size_t cap, size_t* out_len);
bool dom_fs_write_text(const char* path, const char* text);
bool dom_fs_file_exists(const char* path);
bool dom_fs_dir_exists(const char* path);
bool dom_fs_mkdirs(const char* path);
bool dom_fs_copy_file(const char* src, const char* dst);
bool dom_fs_copy_tree(const char* src, const char* dst);
bool dom_fs_remove_tree(const char* path);

#endif /* DOMINO_CORE_INTERNAL_H */
