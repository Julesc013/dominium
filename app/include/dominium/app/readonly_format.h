/*
Read-only formatting helpers (text/JSON) shared by client/tools.
*/
#ifndef DOMINIUM_APP_READONLY_FORMAT_H
#define DOMINIUM_APP_READONLY_FORMAT_H

#include <stdint.h>

#include "dominium/app/readonly_adapter.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_app_output_format {
    DOM_APP_FORMAT_TEXT = 0,
    DOM_APP_FORMAT_JSON = 1
} dom_app_output_format;

int dom_app_parse_output_format(const char* value, dom_app_output_format* out);

void dom_app_ro_print_topology_bundle(dom_app_output_format format,
                                      const dom_app_ro_core_info* info,
                                      const char* tree_id,
                                      const dom_app_ro_tree_node* nodes,
                                      uint32_t count,
                                      uint32_t truncated);

void dom_app_ro_print_inspector_bundle(dom_app_output_format format,
                                       const dom_app_ro_core_info* info,
                                       const char* tree_id,
                                       const dom_app_ro_tree_node* nodes,
                                       uint32_t count,
                                       uint32_t truncated,
                                       int snapshots_supported,
                                       int events_supported,
                                       int replay_supported);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_APP_READONLY_FORMAT_H */
