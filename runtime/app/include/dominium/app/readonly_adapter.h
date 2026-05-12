/*
Read-only adapter for engine/game access in app layer.
*/
#ifndef DOMINIUM_APP_READONLY_ADAPTER_H
#define DOMINIUM_APP_READONLY_ADAPTER_H

#include <stddef.h>
#include <stdint.h>

#include "domino/core.h"
#include "domino/model_table.h"
#include "domino/model_tree.h"
#include "domino/sim.h"

#include "dominium/app/compat_report.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_APP_RO_SCHEMA_VERSION 1u

typedef enum dom_app_ro_status {
    DOM_APP_RO_OK = 0,
    DOM_APP_RO_UNSUPPORTED = -1,
    DOM_APP_RO_ERROR = -2
} dom_app_ro_status;

typedef struct dom_app_ro_core_info {
    uint32_t struct_size;
    uint32_t struct_version;
    uint32_t api_version;
    uint32_t package_count;
    uint32_t instance_count;
} dom_app_ro_core_info;

typedef struct dom_app_ro_tree_node {
    uint32_t         struct_size;
    uint32_t         struct_version;
    dom_tree_node_id id;
    dom_tree_node_id parent;
    uint32_t         depth;
    uint32_t         child_count;
    char             label[128];
} dom_app_ro_tree_node;

typedef struct dom_app_ro_tree_info {
    uint32_t struct_size;
    uint32_t struct_version;
    uint32_t count;
    uint32_t truncated;
} dom_app_ro_tree_info;

typedef struct dom_app_readonly_adapter {
    dom_core* core;
    int       has_packages_tree;
    int       has_packages_table;
    int       has_instances_table;
    int       has_mods_table;
    char      last_error[160];
} dom_app_readonly_adapter;

void              dom_app_ro_init(dom_app_readonly_adapter* ro);
int               dom_app_ro_open(dom_app_readonly_adapter* ro,
                                  const dom_app_compat_expect* expect,
                                  dom_app_compat_report* report);
void              dom_app_ro_close(dom_app_readonly_adapter* ro);
const char*       dom_app_ro_last_error(const dom_app_readonly_adapter* ro);

dom_app_ro_status dom_app_ro_get_core_info(dom_app_readonly_adapter* ro,
                                           dom_app_ro_core_info* out);
dom_app_ro_status dom_app_ro_get_sim_state(dom_app_readonly_adapter* ro,
                                           dom_instance_id inst,
                                           dom_sim_state* out);

dom_app_ro_status dom_app_ro_get_tree(dom_app_readonly_adapter* ro,
                                      const char* tree_id,
                                      dom_app_ro_tree_node* nodes,
                                      uint32_t cap,
                                      dom_app_ro_tree_info* out_info);

dom_app_ro_status dom_app_ro_table_meta(dom_app_readonly_adapter* ro,
                                        const char* table_id,
                                        dom_table_meta* out);
dom_app_ro_status dom_app_ro_table_cell(dom_app_readonly_adapter* ro,
                                        const char* table_id,
                                        uint32_t row,
                                        uint32_t col,
                                        char* buf,
                                        size_t buf_size);

int dom_app_ro_has_packages_tree(const dom_app_readonly_adapter* ro);
int dom_app_ro_has_table(const dom_app_readonly_adapter* ro, const char* table_id);

int dom_app_ro_snapshots_supported(void);
int dom_app_ro_events_supported(void);
int dom_app_ro_replay_supported(void);

dom_app_ro_status dom_app_ro_authority_token(char* buf, size_t buf_size);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_READONLY_ADAPTER_H */
