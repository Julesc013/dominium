/*
Read-only formatting helpers (text/JSON) shared by client/tools.
*/
#include "dominium/app/readonly_format.h"

#include <ctype.h>
#include <stdio.h>
#include <string.h>

static void dom_app_print_json_string(const char* s)
{
    const unsigned char* p = (const unsigned char*)(s ? s : "");
    putchar('\"');
    while (*p) {
        unsigned char c = *p++;
        switch (c) {
        case '\\\\': putchar('\\\\'); putchar('\\\\'); break;
        case '\"':  putchar('\\\\'); putchar('\"'); break;
        case '\\b': putchar('\\\\'); putchar('b'); break;
        case '\\f': putchar('\\\\'); putchar('f'); break;
        case '\\n': putchar('\\\\'); putchar('n'); break;
        case '\\r': putchar('\\\\'); putchar('r'); break;
        case '\\t': putchar('\\\\'); putchar('t'); break;
        default:
            if (c < 0x20) {
                printf("\\\\u%04x", (unsigned int)c);
            } else {
                putchar((int)c);
            }
            break;
        }
    }
    putchar('\"');
}

int dom_app_parse_output_format(const char* value, dom_app_output_format* out)
{
    char buf[16];
    size_t len;
    size_t i;
    if (!value || !out) {
        return 0;
    }
    len = strlen(value);
    if (len == 0u || len >= sizeof(buf)) {
        return 0;
    }
    for (i = 0u; i < len; ++i) {
        buf[i] = (char)tolower((unsigned char)value[i]);
    }
    buf[len] = '\\0';
    if (strcmp(buf, "text") == 0) {
        *out = DOM_APP_FORMAT_TEXT;
        return 1;
    }
    if (strcmp(buf, "json") == 0) {
        *out = DOM_APP_FORMAT_JSON;
        return 1;
    }
    return 0;
}

static void dom_app_print_core_info_text(const dom_app_ro_core_info* info)
{
    if (!info) {
        return;
    }
    printf("core_api_version=%u\n", (unsigned int)info->api_version);
    printf("core_package_count=%u\n", (unsigned int)info->package_count);
    printf("core_instance_count=%u\n", (unsigned int)info->instance_count);
}

static void dom_app_print_topology_text(const char* tree_id,
                                        const dom_app_ro_tree_node* nodes,
                                        uint32_t count,
                                        uint32_t truncated)
{
    uint32_t i;
    printf("topology_tree=%s\n", tree_id ? tree_id : "");
    printf("topology_nodes=%u\n", (unsigned int)count);
    printf("topology_truncated=%u\n", (unsigned int)truncated);
    for (i = 0u; i < count; ++i) {
        const dom_app_ro_tree_node* node = &nodes[i];
        printf("topology_node id=%u parent=%u depth=%u children=%u label=%s\n",
               (unsigned int)node->id,
               (unsigned int)node->parent,
               (unsigned int)node->depth,
               (unsigned int)node->child_count,
               node->label);
    }
}

static void dom_app_print_topology_json(const char* tree_id,
                                        const dom_app_ro_tree_node* nodes,
                                        uint32_t count,
                                        uint32_t truncated)
{
    uint32_t i;
    printf("\"topology\":{");
    printf("\"tree_id\":");
    dom_app_print_json_string(tree_id ? tree_id : "");
    printf(",\"truncated\":%u", (unsigned int)truncated);
    printf(",\"nodes\":[");
    for (i = 0u; i < count; ++i) {
        const dom_app_ro_tree_node* node = &nodes[i];
        if (i > 0u) {
            putchar(',');
        }
        printf("{\"id\":%u,\"parent\":%u,\"depth\":%u,\"child_count\":%u,\"label\":",
               (unsigned int)node->id,
               (unsigned int)node->parent,
               (unsigned int)node->depth,
               (unsigned int)node->child_count);
        dom_app_print_json_string(node->label);
        putchar('}');
    }
    printf("]}");
}

void dom_app_ro_print_topology_bundle(dom_app_output_format format,
                                      const dom_app_ro_core_info* info,
                                      const char* tree_id,
                                      const dom_app_ro_tree_node* nodes,
                                      uint32_t count,
                                      uint32_t truncated)
{
    if (format == DOM_APP_FORMAT_JSON) {
        printf("{\"core_info\":{");
        if (info) {
            printf("\"api_version\":%u,\"package_count\":%u,\"instance_count\":%u",
                   (unsigned int)info->api_version,
                   (unsigned int)info->package_count,
                   (unsigned int)info->instance_count);
        }
        printf("},");
        dom_app_print_topology_json(tree_id, nodes, count, truncated);
        printf("}\n");
        return;
    }
    if (info) {
        dom_app_print_core_info_text(info);
    }
    dom_app_print_topology_text(tree_id, nodes, count, truncated);
}

void dom_app_ro_print_inspector_bundle(dom_app_output_format format,
                                       const dom_app_ro_core_info* info,
                                       const char* tree_id,
                                       const dom_app_ro_tree_node* nodes,
                                       uint32_t count,
                                       uint32_t truncated,
                                       int snapshots_supported,
                                       int events_supported,
                                       int replay_supported)
{
    if (format == DOM_APP_FORMAT_JSON) {
        printf("{\"core_info\":{");
        if (info) {
            printf("\"api_version\":%u,\"package_count\":%u,\"instance_count\":%u",
                   (unsigned int)info->api_version,
                   (unsigned int)info->package_count,
                   (unsigned int)info->instance_count);
        }
        printf("},");
        dom_app_print_topology_json(tree_id, nodes, count, truncated);
        printf(",\"snapshot\":{\"supported\":%s}",
               snapshots_supported ? "true" : "false");
        printf(",\"events\":{\"supported\":%s}",
               events_supported ? "true" : "false");
        printf(",\"replay\":{\"supported\":%s}",
               replay_supported ? "true" : "false");
        printf("}\n");
        return;
    }
    if (info) {
        dom_app_print_core_info_text(info);
    }
    dom_app_print_topology_text(tree_id, nodes, count, truncated);
    printf("snapshot_supported=%u\n", snapshots_supported ? 1u : 0u);
    printf("events_supported=%u\n", events_supported ? 1u : 0u);
    printf("replay_supported=%u\n", replay_supported ? 1u : 0u);
}
