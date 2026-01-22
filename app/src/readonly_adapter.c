/*
Read-only adapter implementation.
*/
#include "dominium/app/readonly_adapter.h"

#include <string.h>

static void dom_app_ro_set_error(dom_app_readonly_adapter* ro, const char* msg)
{
    if (!ro) {
        return;
    }
    if (!msg) {
        ro->last_error[0] = '\0';
        return;
    }
    strncpy(ro->last_error, msg, sizeof(ro->last_error) - 1u);
    ro->last_error[sizeof(ro->last_error) - 1u] = '\0';
}

void dom_app_ro_init(dom_app_readonly_adapter* ro)
{
    if (!ro) {
        return;
    }
    memset(ro, 0, sizeof(*ro));
    ro->last_error[0] = '\0';
}

int dom_app_ro_open(dom_app_readonly_adapter* ro,
                    const dom_app_compat_expect* expect,
                    dom_app_compat_report* report)
{
    dom_core_desc desc;
    dom_app_compat_report local_report;
    dom_tree_node_id root;

    if (!ro) {
        return 0;
    }

    dom_app_ro_set_error(ro, "");

    if (!report) {
        dom_app_compat_report_init(&local_report, "app");
        report = &local_report;
    }
    if (!dom_app_compat_check(expect, report)) {
        dom_app_ro_set_error(ro, report->message);
        return 0;
    }

    memset(&desc, 0, sizeof(desc));
    desc.api_version = 1u;

    ro->core = dom_core_create(&desc);
    if (!ro->core) {
        dom_app_ro_set_error(ro, "core_create failed");
        return 0;
    }

    ro->has_packages_tree = dom_tree_get_root(ro->core, "packages_tree", &root) ? 1 : 0;
    {
        dom_table_meta meta;
        memset(&meta, 0, sizeof(meta));
        ro->has_packages_table = dom_table_get_meta(ro->core, "packages_table", &meta) ? 1 : 0;
        memset(&meta, 0, sizeof(meta));
        ro->has_instances_table = dom_table_get_meta(ro->core, "instances_table", &meta) ? 1 : 0;
        memset(&meta, 0, sizeof(meta));
        ro->has_mods_table = dom_table_get_meta(ro->core, "mods_table", &meta) ? 1 : 0;
    }

    return 1;
}

void dom_app_ro_close(dom_app_readonly_adapter* ro)
{
    if (!ro) {
        return;
    }
    if (ro->core) {
        dom_core_destroy(ro->core);
        ro->core = 0;
    }
}

const char* dom_app_ro_last_error(const dom_app_readonly_adapter* ro)
{
    if (!ro || ro->last_error[0] == '\0') {
        return "ok";
    }
    return ro->last_error;
}

dom_app_ro_status dom_app_ro_get_core_info(dom_app_readonly_adapter* ro,
                                           dom_app_ro_core_info* out)
{
    dom_query query;
    dom_query_core_info_out core_out;

    if (!ro || !ro->core || !out) {
        return DOM_APP_RO_ERROR;
    }

    memset(&core_out, 0, sizeof(core_out));
    memset(&query, 0, sizeof(query));
    query.id = DOM_QUERY_CORE_INFO;
    query.out = &core_out;
    query.out_size = sizeof(core_out);

    if (!dom_core_query(ro->core, &query)) {
        dom_app_ro_set_error(ro, "core_info query failed");
        return DOM_APP_RO_ERROR;
    }

    out->struct_size = sizeof(*out);
    out->struct_version = DOM_APP_RO_SCHEMA_VERSION;
    out->api_version = core_out.api_version;
    out->package_count = core_out.package_count;
    out->instance_count = core_out.instance_count;
    return DOM_APP_RO_OK;
}

dom_app_ro_status dom_app_ro_get_sim_state(dom_app_readonly_adapter* ro,
                                           dom_instance_id inst,
                                           dom_sim_state* out)
{
    dom_query query;
    dom_query_sim_state_in sim_in;
    dom_query_sim_state_out sim_out;

    if (!ro || !ro->core || !out) {
        return DOM_APP_RO_ERROR;
    }

    memset(&sim_in, 0, sizeof(sim_in));
    memset(&sim_out, 0, sizeof(sim_out));
    memset(&query, 0, sizeof(query));
    sim_in.id = inst;
    query.id = DOM_QUERY_SIM_STATE;
    query.in = &sim_in;
    query.in_size = sizeof(sim_in);
    query.out = &sim_out;
    query.out_size = sizeof(sim_out);

    if (!dom_core_query(ro->core, &query)) {
        dom_app_ro_set_error(ro, "sim_state query failed");
        return DOM_APP_RO_ERROR;
    }

    *out = sim_out.state;
    return DOM_APP_RO_OK;
}

typedef struct dom_app_ro_tree_walk {
    dom_app_readonly_adapter* ro;
    dom_app_ro_tree_node* nodes;
    uint32_t cap;
    uint32_t count;
    uint32_t truncated;
    int error;
} dom_app_ro_tree_walk;

static int dom_app_ro_tree_push(dom_app_ro_tree_walk* walk,
                                const dom_tree_node* node,
                                dom_tree_node_id id,
                                uint32_t depth)
{
    dom_app_ro_tree_node* dst;

    if (!walk || !node) {
        return 0;
    }
    if (walk->count >= walk->cap) {
        walk->truncated = 1u;
        return 0;
    }
    dst = &walk->nodes[walk->count++];
    memset(dst, 0, sizeof(*dst));
    dst->struct_size = sizeof(*dst);
    dst->struct_version = DOM_APP_RO_SCHEMA_VERSION;
    dst->id = id;
    dst->parent = node->parent;
    dst->depth = depth;
    dst->child_count = node->child_count;
    strncpy(dst->label, node->label, sizeof(dst->label) - 1u);
    dst->label[sizeof(dst->label) - 1u] = '\0';
    return 1;
}

static void dom_app_ro_tree_walk_nodes(dom_app_ro_tree_walk* walk,
                                       const char* tree_id,
                                       dom_tree_node_id id,
                                       uint32_t depth)
{
    dom_tree_node node;
    uint32_t i;
    dom_tree_node_id child_id;

    if (!walk || !walk->ro || walk->truncated) {
        return;
    }

    memset(&node, 0, sizeof(node));
    if (!dom_tree_get_node(walk->ro->core, tree_id, id, &node)) {
        dom_app_ro_set_error(walk->ro, "tree node query failed");
        walk->error = 1;
        return;
    }

    if (!dom_app_ro_tree_push(walk, &node, id, depth)) {
        return;
    }

    for (i = 0u; i < node.child_count; ++i) {
        if (!dom_tree_get_child(walk->ro->core, tree_id, id, i, &child_id)) {
            continue;
        }
        dom_app_ro_tree_walk_nodes(walk, tree_id, child_id, depth + 1u);
        if (walk->truncated) {
            return;
        }
    }
}

dom_app_ro_status dom_app_ro_get_tree(dom_app_readonly_adapter* ro,
                                      const char* tree_id,
                                      dom_app_ro_tree_node* nodes,
                                      uint32_t cap,
                                      dom_app_ro_tree_info* out_info)
{
    dom_tree_node_id root;
    dom_app_ro_tree_walk walk;

    if (!ro || !ro->core || !tree_id || !nodes || cap == 0u || !out_info) {
        return DOM_APP_RO_ERROR;
    }
    if (!dom_tree_get_root(ro->core, tree_id, &root)) {
        dom_app_ro_set_error(ro, "tree unsupported");
        return DOM_APP_RO_UNSUPPORTED;
    }

    memset(&walk, 0, sizeof(walk));
    walk.ro = ro;
    walk.nodes = nodes;
    walk.cap = cap;
    walk.count = 0u;
    walk.truncated = 0u;
    walk.error = 0;

    dom_app_ro_tree_walk_nodes(&walk, tree_id, root, 0u);

    if (walk.error) {
        return DOM_APP_RO_ERROR;
    }

    out_info->struct_size = sizeof(*out_info);
    out_info->struct_version = DOM_APP_RO_SCHEMA_VERSION;
    out_info->count = walk.count;
    out_info->truncated = walk.truncated;
    return DOM_APP_RO_OK;
}

dom_app_ro_status dom_app_ro_table_meta(dom_app_readonly_adapter* ro,
                                        const char* table_id,
                                        dom_table_meta* out)
{
    if (!ro || !ro->core || !table_id || !out) {
        return DOM_APP_RO_ERROR;
    }
    if (!dom_table_get_meta(ro->core, table_id, out)) {
        dom_app_ro_set_error(ro, "table unsupported");
        return DOM_APP_RO_UNSUPPORTED;
    }
    return DOM_APP_RO_OK;
}

dom_app_ro_status dom_app_ro_table_cell(dom_app_readonly_adapter* ro,
                                        const char* table_id,
                                        uint32_t row,
                                        uint32_t col,
                                        char* buf,
                                        size_t buf_size)
{
    if (!ro || !ro->core || !table_id || !buf || buf_size == 0u) {
        return DOM_APP_RO_ERROR;
    }
    if (!dom_table_get_cell(ro->core, table_id, row, col, buf, buf_size)) {
        dom_app_ro_set_error(ro, "table cell unavailable");
        return DOM_APP_RO_ERROR;
    }
    return DOM_APP_RO_OK;
}

int dom_app_ro_has_packages_tree(const dom_app_readonly_adapter* ro)
{
    return (ro && ro->has_packages_tree) ? 1 : 0;
}

int dom_app_ro_has_table(const dom_app_readonly_adapter* ro, const char* table_id)
{
    if (!ro || !table_id) {
        return 0;
    }
    if (strcmp(table_id, "packages_table") == 0) {
        return ro->has_packages_table;
    }
    if (strcmp(table_id, "instances_table") == 0) {
        return ro->has_instances_table;
    }
    if (strcmp(table_id, "mods_table") == 0) {
        return ro->has_mods_table;
    }
    return 0;
}

int dom_app_ro_snapshots_supported(void)
{
    return 0;
}

int dom_app_ro_events_supported(void)
{
    return 0;
}

int dom_app_ro_replay_supported(void)
{
    return 0;
}

dom_app_ro_status dom_app_ro_authority_token(char* buf, size_t buf_size)
{
    if (buf && buf_size > 0u) {
        buf[0] = '\0';
    }
    return DOM_APP_RO_UNSUPPORTED;
}
