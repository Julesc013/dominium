/*
FILE: source/dominium/game/runtime/dom_cosmo_graph.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_cosmo_graph
RESPONSIBILITY: Implements deterministic cosmos graph registry.
*/
#include "runtime/dom_cosmo_graph.h"

#include <cstring>

#include "domino/io/container.h"

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

#define DOM_COSMO_U32_FOURCC(a,b,c,d) \
    ((u32)(a) | ((u32)(b) << 8) | ((u32)(c) << 16) | ((u32)(d) << 24))

enum {
    DOM_COSMO_CHUNK_SEED = DOM_COSMO_U32_FOURCC('S','E','E','D'),
    DOM_COSMO_CHUNK_ENTY = DOM_COSMO_U32_FOURCC('E','N','T','Y'),
    DOM_COSMO_CHUNK_EDGE = DOM_COSMO_U32_FOURCC('E','D','G','E'),
    DOM_COSMO_CHUNK_FORN = DOM_COSMO_U32_FOURCC('F','O','R','N')
};

enum {
    DOM_COSMO_TLV_FOREIGN = 0x0001u
};

static const u32 kCosmoSeedPayloadSize = 16u;
static const u32 kCosmoEntityHeaderSize = 24u;
static const u32 kCosmoEdgeRecordSize = 44u;

static bool kind_valid(u32 kind) {
    return kind == dom::DOM_COSMO_KIND_FILAMENT ||
           kind == dom::DOM_COSMO_KIND_CLUSTER ||
           kind == dom::DOM_COSMO_KIND_GALAXY ||
           kind == dom::DOM_COSMO_KIND_SYSTEM;
}

static u32 expected_parent_kind(u32 kind) {
    switch (kind) {
    case dom::DOM_COSMO_KIND_CLUSTER:
        return dom::DOM_COSMO_KIND_FILAMENT;
    case dom::DOM_COSMO_KIND_GALAXY:
        return dom::DOM_COSMO_KIND_CLUSTER;
    case dom::DOM_COSMO_KIND_SYSTEM:
        return dom::DOM_COSMO_KIND_GALAXY;
    default:
        break;
    }
    return 0u;
}

static int compute_id(const char *stable_id, u64 *out_id) {
    if (!stable_id || !stable_id[0] || !out_id) {
        return dom::DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    return dom_id_hash64(stable_id, (u32)std::strlen(stable_id), out_id) == DOM_SPACETIME_OK
               ? dom::DOM_COSMO_GRAPH_OK
               : dom::DOM_COSMO_GRAPH_ERR;
}

static int find_entity_index(const std::vector<dom::dom_cosmo_entity> &list, u64 id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id == id) {
            return (int)i;
        }
    }
    return -1;
}

static int find_edge_index(const std::vector<dom::dom_cosmo_edge> &list, u64 id) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].id == id) {
            return (int)i;
        }
    }
    return -1;
}

static u64 fnv1a64_update(u64 h, const unsigned char *data, size_t len) {
    size_t i;
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= 1099511628211ull;
    }
    return h;
}

static u64 edge_id_hash(u64 src_id,
                        u64 dst_id,
                        u64 duration_ticks,
                        u32 cost,
                        u64 event_table_id) {
    unsigned char buf[8];
    u64 h = 14695981039346656037ull;

    dtlv_le_write_u64(buf, src_id);
    h = fnv1a64_update(h, buf, 8u);
    dtlv_le_write_u64(buf, dst_id);
    h = fnv1a64_update(h, buf, 8u);
    dtlv_le_write_u64(buf, duration_ticks);
    h = fnv1a64_update(h, buf, 8u);
    dtlv_le_write_u32(buf, cost);
    h = fnv1a64_update(h, buf, 4u);
    dtlv_le_write_u64(buf, event_table_id);
    h = fnv1a64_update(h, buf, 8u);
    return h;
}

static void insert_sorted_entity(std::vector<dom::dom_cosmo_entity> &list,
                                 const dom::dom_cosmo_entity &ent) {
    size_t i = 0u;
    for (; i < list.size(); ++i) {
        if (ent.id < list[i].id) {
            break;
        }
    }
    list.insert(list.begin() + (std::vector<dom::dom_cosmo_entity>::difference_type)i, ent);
}

static void insert_sorted_edge(std::vector<dom::dom_cosmo_edge> &list,
                               const dom::dom_cosmo_edge &edge) {
    size_t i = 0u;
    for (; i < list.size(); ++i) {
        if (edge.id < list[i].id) {
            break;
        }
    }
    list.insert(list.begin() + (std::vector<dom::dom_cosmo_edge>::difference_type)i, edge);
}

static int append_foreign(std::vector<dom::dom_cosmo_foreign_chunk> &list,
                          u32 type_id,
                          u16 version,
                          u16 flags,
                          const unsigned char *payload,
                          u32 payload_len) {
    dom::dom_cosmo_foreign_chunk foreign;
    foreign.type_id = type_id;
    foreign.version = version;
    foreign.flags = flags;
    if (payload_len == 0u) {
        foreign.payload.clear();
    } else {
        if (!payload) {
            return dom::DOM_COSMO_GRAPH_INVALID_FORMAT;
        }
        foreign.payload.assign(payload, payload + payload_len);
    }
    list.push_back(foreign);
    return dom::DOM_COSMO_GRAPH_OK;
}

static int parse_foreign_chunk(std::vector<dom::dom_cosmo_foreign_chunk> &list,
                               const unsigned char *payload,
                               u32 payload_len) {
    u32 offset = 0u;
    u32 tag = 0u;
    const unsigned char *pl = 0;
    u32 pl_len = 0u;
    int rc;

    while ((rc = dtlv_tlv_next(payload, payload_len, &offset, &tag, &pl, &pl_len)) == 0) {
        if (tag != DOM_COSMO_TLV_FOREIGN) {
            continue;
        }
        if (!pl || pl_len < 16u) {
            return dom::DOM_COSMO_GRAPH_INVALID_FORMAT;
        }
        {
            u64 size64 = dtlv_le_read_u64(pl + 8u);
            u32 size = (size64 > 0xffffffffull) ? 0xffffffffu : (u32)size64;
            if (pl_len != (16u + size)) {
                return dom::DOM_COSMO_GRAPH_INVALID_FORMAT;
            }
            rc = append_foreign(list,
                                dtlv_le_read_u32(pl + 0u),
                                dtlv_le_read_u16(pl + 4u),
                                dtlv_le_read_u16(pl + 6u),
                                pl + 16u,
                                size);
            if (rc != dom::DOM_COSMO_GRAPH_OK) {
                return rc;
            }
        }
    }

    if (rc < 0) {
        return dom::DOM_COSMO_GRAPH_INVALID_FORMAT;
    }
    return dom::DOM_COSMO_GRAPH_OK;
}

} // namespace

namespace dom {

dom_cosmo_graph_config::dom_cosmo_graph_config()
    : struct_size(sizeof(dom_cosmo_graph_config)),
      struct_version(DOM_COSMO_GRAPH_CONFIG_VERSION),
      max_entities(0u),
      max_edges(0u) {
}

dom_cosmo_entity::dom_cosmo_entity()
    : id(0ull),
      parent_id(0ull),
      kind(0u),
      stable_id() {
}

dom_cosmo_edge::dom_cosmo_edge()
    : id(0ull),
      src_id(0ull),
      dst_id(0ull),
      duration_ticks(0ull),
      cost(0u),
      event_table_id(0ull) {
}

dom_cosmo_edge_params::dom_cosmo_edge_params()
    : duration_ticks(0ull),
      cost(0u),
      event_table_id(0ull) {
}

dom_cosmo_foreign_chunk::dom_cosmo_foreign_chunk()
    : type_id(0u),
      version(0u),
      flags(0u),
      payload() {
}

dom_cosmo_graph::dom_cosmo_graph()
    : struct_size(sizeof(dom_cosmo_graph)),
      struct_version(1u),
      seed(0ull),
      config(),
      entities(),
      edges(),
      foreign() {
}

int dom_cosmo_graph_init(dom_cosmo_graph *graph,
                         u64 seed,
                         const dom_cosmo_graph_config *config) {
    if (!graph) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    graph->struct_size = sizeof(dom_cosmo_graph);
    graph->struct_version = 1u;
    graph->seed = seed;
    graph->entities.clear();
    graph->edges.clear();
    graph->foreign.clear();
    if (config) {
        graph->config = *config;
    } else {
        graph->config = dom_cosmo_graph_config();
    }
    return DOM_COSMO_GRAPH_OK;
}

int dom_cosmo_graph_add_entity(dom_cosmo_graph *graph,
                               u32 kind,
                               const char *stable_id,
                               u64 parent_id,
                               u64 *out_id) {
    dom_cosmo_entity ent;
    u64 id = 0ull;

    if (!graph || !stable_id || !stable_id[0]) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    if (!kind_valid(kind)) {
        return DOM_COSMO_GRAPH_INVALID_KIND;
    }
    if (compute_id(stable_id, &id) != DOM_COSMO_GRAPH_OK) {
        return DOM_COSMO_GRAPH_ERR;
    }
    if (find_entity_index(graph->entities, id) >= 0) {
        return DOM_COSMO_GRAPH_DUPLICATE_ID;
    }
    if (graph->config.max_entities > 0u &&
        graph->entities.size() >= graph->config.max_entities) {
        return DOM_COSMO_GRAPH_ERR;
    }

    ent.id = id;
    ent.parent_id = parent_id;
    ent.kind = kind;
    ent.stable_id = stable_id;

    insert_sorted_entity(graph->entities, ent);
    if (out_id) {
        *out_id = id;
    }
    return DOM_COSMO_GRAPH_OK;
}

int dom_cosmo_graph_add_travel_edge(dom_cosmo_graph *graph,
                                    u64 src_id,
                                    u64 dst_id,
                                    const dom_cosmo_edge_params *params,
                                    u64 *out_edge_id) {
    dom_cosmo_edge edge;
    u64 id;

    if (!graph || !params) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    if (src_id == 0ull || dst_id == 0ull || src_id == dst_id) {
        return DOM_COSMO_GRAPH_INVALID_EDGE;
    }
    if (params->duration_ticks == 0ull) {
        return DOM_COSMO_GRAPH_INVALID_EDGE;
    }
    if (find_entity_index(graph->entities, src_id) < 0 ||
        find_entity_index(graph->entities, dst_id) < 0) {
        return DOM_COSMO_GRAPH_NOT_FOUND;
    }
    if (graph->config.max_edges > 0u &&
        graph->edges.size() >= graph->config.max_edges) {
        return DOM_COSMO_GRAPH_ERR;
    }

    id = edge_id_hash(src_id, dst_id, params->duration_ticks, params->cost, params->event_table_id);
    if (find_edge_index(graph->edges, id) >= 0) {
        return DOM_COSMO_GRAPH_DUPLICATE_ID;
    }

    edge.id = id;
    edge.src_id = src_id;
    edge.dst_id = dst_id;
    edge.duration_ticks = params->duration_ticks;
    edge.cost = params->cost;
    edge.event_table_id = params->event_table_id;
    insert_sorted_edge(graph->edges, edge);

    if (out_edge_id) {
        *out_edge_id = id;
    }
    return DOM_COSMO_GRAPH_OK;
}

int dom_cosmo_graph_validate(const dom_cosmo_graph *graph,
                             std::vector<std::string> *out_errors) {
    size_t i;
    if (out_errors) {
        out_errors->clear();
    }
    if (!graph) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }

    for (i = 0u; i < graph->entities.size(); ++i) {
        const dom_cosmo_entity &ent = graph->entities[i];
        const u32 parent_kind = expected_parent_kind(ent.kind);
        const int parent_index = (ent.parent_id == 0ull)
                                     ? -1
                                     : find_entity_index(graph->entities, ent.parent_id);

        if (!kind_valid(ent.kind)) {
            if (out_errors) {
                out_errors->push_back("invalid_kind");
            }
            return DOM_COSMO_GRAPH_INVALID_KIND;
        }
        if (ent.kind == DOM_COSMO_KIND_FILAMENT) {
            if (ent.parent_id != 0ull) {
                if (out_errors) {
                    out_errors->push_back("filament_has_parent");
                }
                return DOM_COSMO_GRAPH_INVALID_PARENT;
            }
        } else {
            if (ent.parent_id == 0ull || parent_index < 0) {
                if (out_errors) {
                    out_errors->push_back("missing_parent");
                }
                return DOM_COSMO_GRAPH_INVALID_PARENT;
            }
            if (parent_kind != graph->entities[(size_t)parent_index].kind) {
                if (out_errors) {
                    out_errors->push_back("parent_kind_mismatch");
                }
                return DOM_COSMO_GRAPH_INVALID_PARENT;
            }
        }

        {
            size_t guard = 0u;
            u64 cur = ent.parent_id;
            while (cur != 0ull && guard < graph->entities.size()) {
                if (cur == ent.id) {
                    if (out_errors) {
                        out_errors->push_back("cycle_detected");
                    }
                    return DOM_COSMO_GRAPH_CYCLE;
                }
                {
                    int idx = find_entity_index(graph->entities, cur);
                    if (idx < 0) {
                        break;
                    }
                    cur = graph->entities[(size_t)idx].parent_id;
                }
                guard += 1u;
            }
        }
    }

    for (i = 0u; i < graph->edges.size(); ++i) {
        const dom_cosmo_edge &edge = graph->edges[i];
        if (edge.src_id == 0ull || edge.dst_id == 0ull ||
            edge.src_id == edge.dst_id || edge.duration_ticks == 0ull) {
            if (out_errors) {
                out_errors->push_back("invalid_edge");
            }
            return DOM_COSMO_GRAPH_INVALID_EDGE;
        }
        if (find_entity_index(graph->entities, edge.src_id) < 0 ||
            find_entity_index(graph->entities, edge.dst_id) < 0) {
            if (out_errors) {
                out_errors->push_back("edge_missing_entity");
            }
            return DOM_COSMO_GRAPH_NOT_FOUND;
        }
    }

    return DOM_COSMO_GRAPH_OK;
}

int dom_cosmo_graph_iterate(const dom_cosmo_graph *graph,
                            u32 kind,
                            dom_cosmo_iter_fn fn,
                            void *user) {
    size_t i;
    if (!graph || !fn) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    for (i = 0u; i < graph->entities.size(); ++i) {
        const dom_cosmo_entity &ent = graph->entities[i];
        if (kind == 0u || ent.kind == kind) {
            fn(&ent, user);
        }
    }
    return DOM_COSMO_GRAPH_OK;
}

const dom_cosmo_entity *dom_cosmo_graph_get_entity(const dom_cosmo_graph *graph, u64 id) {
    int idx;
    if (!graph || id == 0ull) {
        return 0;
    }
    idx = find_entity_index(graph->entities, id);
    if (idx < 0) {
        return 0;
    }
    return &graph->entities[(size_t)idx];
}

const dom_cosmo_edge *dom_cosmo_graph_get_edge(const dom_cosmo_graph *graph, u64 id) {
    int idx;
    if (!graph || id == 0ull) {
        return 0;
    }
    idx = find_edge_index(graph->edges, id);
    if (idx < 0) {
        return 0;
    }
    return &graph->edges[(size_t)idx];
}

u64 dom_cosmo_graph_hash(const dom_cosmo_graph *graph) {
    u64 h = 14695981039346656037ull;
    size_t i;
    if (!graph) {
        return 0ull;
    }
    for (i = 0u; i < graph->entities.size(); ++i) {
        const dom_cosmo_entity &ent = graph->entities[i];
        h ^= ent.id;
        h *= 1099511628211ull;
        h ^= ent.parent_id;
        h *= 1099511628211ull;
        h ^= (u64)ent.kind;
        h *= 1099511628211ull;
    }
    for (i = 0u; i < graph->edges.size(); ++i) {
        const dom_cosmo_edge &edge = graph->edges[i];
        h ^= edge.id;
        h *= 1099511628211ull;
        h ^= edge.src_id;
        h *= 1099511628211ull;
        h ^= edge.dst_id;
        h *= 1099511628211ull;
        h ^= edge.duration_ticks;
        h *= 1099511628211ull;
        h ^= (u64)edge.cost;
        h *= 1099511628211ull;
        h ^= edge.event_table_id;
        h *= 1099511628211ull;
    }
    h ^= graph->seed;
    h *= 1099511628211ull;
    return h;
}

int dom_cosmo_graph_serialize(const dom_cosmo_graph *graph,
                              std::vector<unsigned char> *out_payload) {
    dtlv_writer writer;
    u64 entity_payload = 0ull;
    u64 edge_payload = 0ull;
    u64 foreign_payload = 0ull;
    u64 total_size;
    u32 chunk_count = 4u;
    size_t i;
    int rc;

    if (!graph || !out_payload) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }

    for (i = 0u; i < graph->entities.size(); ++i) {
        const std::string &stable_id = graph->entities[i].stable_id;
        if (stable_id.size() > 0xffffffffu) {
            return DOM_COSMO_GRAPH_INVALID_FORMAT;
        }
        entity_payload += (u64)kCosmoEntityHeaderSize + (u64)stable_id.size();
    }
    edge_payload = (u64)graph->edges.size() * (u64)kCosmoEdgeRecordSize;
    for (i = 0u; i < graph->foreign.size(); ++i) {
        u64 payload_size = (u64)graph->foreign[i].payload.size();
        if (payload_size > 0xffffffffull) {
            return DOM_COSMO_GRAPH_INVALID_FORMAT;
        }
        foreign_payload += 8u + 16u + payload_size;
    }

    total_size = (u64)DTLV_HEADER_SIZE_V1 +
                 (u64)kCosmoSeedPayloadSize +
                 entity_payload +
                 edge_payload +
                 foreign_payload +
                 (u64)chunk_count * (u64)DTLV_DIR_ENTRY_SIZE_V1;

    if (total_size > 0xffffffffull) {
        return DOM_COSMO_GRAPH_NO_MEMORY;
    }
    if (total_size > (u64)((size_t)-1)) {
        return DOM_COSMO_GRAPH_NO_MEMORY;
    }

    out_payload->assign((size_t)total_size, 0u);
    dtlv_writer_init(&writer);
    if (dtlv_writer_init_mem(&writer, &(*out_payload)[0], (u32)total_size) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_COSMO_GRAPH_NO_MEMORY;
    }

    rc = dtlv_writer_begin_chunk(&writer, DOM_COSMO_CHUNK_SEED, 1u, 0u);
    if (rc != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_COSMO_GRAPH_ERR;
    }
    {
        unsigned char seed_payload[kCosmoSeedPayloadSize];
        dtlv_le_write_u64(seed_payload, graph->seed);
        dtlv_le_write_u32(seed_payload + 8u, graph->config.max_entities);
        dtlv_le_write_u32(seed_payload + 12u, graph->config.max_edges);
        rc = dtlv_writer_write(&writer, seed_payload, kCosmoSeedPayloadSize);
    }
    if (rc != 0 || dtlv_writer_end_chunk(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_COSMO_GRAPH_ERR;
    }

    rc = dtlv_writer_begin_chunk(&writer, DOM_COSMO_CHUNK_ENTY, 1u, 0u);
    if (rc != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_COSMO_GRAPH_ERR;
    }
    for (i = 0u; i < graph->entities.size(); ++i) {
        const dom_cosmo_entity &ent = graph->entities[i];
        const u32 stable_len = (u32)ent.stable_id.size();
        unsigned char header[kCosmoEntityHeaderSize];
        dtlv_le_write_u64(header + 0u, ent.id);
        dtlv_le_write_u64(header + 8u, ent.parent_id);
        dtlv_le_write_u32(header + 16u, ent.kind);
        dtlv_le_write_u32(header + 20u, stable_len);
        rc = dtlv_writer_write(&writer, header, kCosmoEntityHeaderSize);
        if (rc != 0) {
            dtlv_writer_dispose(&writer);
            return DOM_COSMO_GRAPH_ERR;
        }
        if (stable_len != 0u) {
            rc = dtlv_writer_write(&writer, ent.stable_id.data(), stable_len);
            if (rc != 0) {
                dtlv_writer_dispose(&writer);
                return DOM_COSMO_GRAPH_ERR;
            }
        }
    }
    if (dtlv_writer_end_chunk(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_COSMO_GRAPH_ERR;
    }

    rc = dtlv_writer_begin_chunk(&writer, DOM_COSMO_CHUNK_EDGE, 1u, 0u);
    if (rc != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_COSMO_GRAPH_ERR;
    }
    for (i = 0u; i < graph->edges.size(); ++i) {
        const dom_cosmo_edge &edge = graph->edges[i];
        unsigned char record[kCosmoEdgeRecordSize];
        dtlv_le_write_u64(record + 0u, edge.id);
        dtlv_le_write_u64(record + 8u, edge.src_id);
        dtlv_le_write_u64(record + 16u, edge.dst_id);
        dtlv_le_write_u64(record + 24u, edge.duration_ticks);
        dtlv_le_write_u32(record + 32u, edge.cost);
        dtlv_le_write_u64(record + 36u, edge.event_table_id);
        rc = dtlv_writer_write(&writer, record, kCosmoEdgeRecordSize);
        if (rc != 0) {
            dtlv_writer_dispose(&writer);
            return DOM_COSMO_GRAPH_ERR;
        }
    }
    if (dtlv_writer_end_chunk(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_COSMO_GRAPH_ERR;
    }

    rc = dtlv_writer_begin_chunk(&writer, DOM_COSMO_CHUNK_FORN, 1u, 0u);
    if (rc != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_COSMO_GRAPH_ERR;
    }
    for (i = 0u; i < graph->foreign.size(); ++i) {
        const dom_cosmo_foreign_chunk &f = graph->foreign[i];
        std::vector<unsigned char> record;
        u64 payload_size = (u64)f.payload.size();
        if (payload_size > 0xffffffffull) {
            dtlv_writer_dispose(&writer);
            return DOM_COSMO_GRAPH_INVALID_FORMAT;
        }
        record.resize(16u + (size_t)payload_size);
        dtlv_le_write_u32(&record[0], f.type_id);
        dtlv_le_write_u16(&record[4], f.version);
        dtlv_le_write_u16(&record[6], f.flags);
        dtlv_le_write_u64(&record[8], payload_size);
        if (payload_size > 0u) {
            std::memcpy(&record[16], &f.payload[0], (size_t)payload_size);
        }
        rc = dtlv_writer_write_tlv(&writer,
                                   DOM_COSMO_TLV_FOREIGN,
                                   &record[0],
                                   (u32)record.size());
        if (rc != 0) {
            dtlv_writer_dispose(&writer);
            return DOM_COSMO_GRAPH_ERR;
        }
    }
    if (dtlv_writer_end_chunk(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_COSMO_GRAPH_ERR;
    }

    if (dtlv_writer_finalize(&writer) != 0) {
        dtlv_writer_dispose(&writer);
        return DOM_COSMO_GRAPH_ERR;
    }

    {
        u32 actual = dtlv_writer_mem_size(&writer);
        if (actual == 0u || actual > (u32)out_payload->size()) {
            dtlv_writer_dispose(&writer);
            return DOM_COSMO_GRAPH_ERR;
        }
        out_payload->resize((size_t)actual);
    }

    dtlv_writer_dispose(&writer);
    return DOM_COSMO_GRAPH_OK;
}

int dom_cosmo_graph_parse(dom_cosmo_graph *graph,
                          const unsigned char *payload,
                          u32 payload_len,
                          std::vector<std::string> *out_errors) {
    dtlv_reader reader;
    u32 count;
    u32 i;
    bool have_seed = false;
    bool have_enty = false;
    bool have_edge = false;
    bool have_forn = false;
    u64 seed = 0ull;
    dom_cosmo_graph_config config;
    std::vector<dom_cosmo_entity> parsed_entities;
    std::vector<dom_cosmo_edge> parsed_edges;
    std::vector<dom_cosmo_foreign_chunk> foreign;
    int rc = DOM_COSMO_GRAPH_OK;

    if (out_errors) {
        out_errors->clear();
    }
    if (!graph || (!payload && payload_len != 0u)) {
        return DOM_COSMO_GRAPH_INVALID_ARGUMENT;
    }
    if (payload_len == 0u) {
        return DOM_COSMO_GRAPH_INVALID_FORMAT;
    }

    dtlv_reader_init(&reader);
    if (dtlv_reader_init_mem(&reader, payload, payload_len) != 0) {
        dtlv_reader_dispose(&reader);
        return DOM_COSMO_GRAPH_INVALID_FORMAT;
    }

    count = dtlv_reader_chunk_count(&reader);
    for (i = 0u; i < count; ++i) {
        const dtlv_dir_entry *entry = dtlv_reader_chunk_at(&reader, i);
        const unsigned char *pl = 0;
        u32 pl_len = 0u;
        if (!entry) {
            continue;
        }
        if (dtlv_reader_chunk_memview(&reader, entry, &pl, &pl_len) != 0) {
            rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
            break;
        }
        switch (entry->type_id) {
            case DOM_COSMO_CHUNK_SEED: {
                if (have_seed) {
                    rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
                    break;
                }
                if (entry->version != 1u) {
                    rc = DOM_COSMO_GRAPH_MIGRATION_REQUIRED;
                    break;
                }
                if (!pl || (pl_len != 8u && pl_len != kCosmoSeedPayloadSize)) {
                    rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
                    break;
                }
                seed = dtlv_le_read_u64(pl);
                config = dom_cosmo_graph_config();
                if (pl_len == kCosmoSeedPayloadSize) {
                    config.max_entities = dtlv_le_read_u32(pl + 8u);
                    config.max_edges = dtlv_le_read_u32(pl + 12u);
                }
                have_seed = true;
                break;
            }
            case DOM_COSMO_CHUNK_ENTY: {
                u32 offset = 0u;
                if (have_enty) {
                    rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
                    break;
                }
                if (entry->version != 1u) {
                    rc = DOM_COSMO_GRAPH_MIGRATION_REQUIRED;
                    break;
                }
                while (offset < pl_len) {
                    u64 id;
                    u64 parent_id;
                    u32 kind;
                    u32 stable_len;
                    u64 computed;
                    if (pl_len - offset < kCosmoEntityHeaderSize) {
                        rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
                        break;
                    }
                    id = dtlv_le_read_u64(pl + offset);
                    parent_id = dtlv_le_read_u64(pl + offset + 8u);
                    kind = dtlv_le_read_u32(pl + offset + 16u);
                    stable_len = dtlv_le_read_u32(pl + offset + 20u);
                    offset += kCosmoEntityHeaderSize;
                    if (stable_len == 0u || stable_len > (pl_len - offset)) {
                        rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
                        break;
                    }
                    if (dom_id_hash64((const char *)(pl + offset),
                                      stable_len,
                                      &computed) != DOM_SPACETIME_OK) {
                        rc = DOM_COSMO_GRAPH_ERR;
                        break;
                    }
                    if (computed != id) {
                        rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
                        break;
                    }
                    {
                        dom_cosmo_entity ent;
                        ent.id = id;
                        ent.parent_id = parent_id;
                        ent.kind = kind;
                        ent.stable_id.assign((const char *)(pl + offset), stable_len);
                        parsed_entities.push_back(ent);
                    }
                    offset += stable_len;
                }
                if (rc != DOM_COSMO_GRAPH_OK) {
                    break;
                }
                have_enty = true;
                break;
            }
            case DOM_COSMO_CHUNK_EDGE: {
                u32 offset = 0u;
                if (have_edge) {
                    rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
                    break;
                }
                if (entry->version != 1u) {
                    rc = DOM_COSMO_GRAPH_MIGRATION_REQUIRED;
                    break;
                }
                if ((pl_len % kCosmoEdgeRecordSize) != 0u) {
                    rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
                    break;
                }
                while (offset < pl_len) {
                    dom_cosmo_edge edge;
                    u64 computed;
                    edge.id = dtlv_le_read_u64(pl + offset);
                    edge.src_id = dtlv_le_read_u64(pl + offset + 8u);
                    edge.dst_id = dtlv_le_read_u64(pl + offset + 16u);
                    edge.duration_ticks = dtlv_le_read_u64(pl + offset + 24u);
                    edge.cost = dtlv_le_read_u32(pl + offset + 32u);
                    edge.event_table_id = dtlv_le_read_u64(pl + offset + 36u);
                    computed = edge_id_hash(edge.src_id,
                                            edge.dst_id,
                                            edge.duration_ticks,
                                            edge.cost,
                                            edge.event_table_id);
                    if (computed != edge.id) {
                        rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
                        break;
                    }
                    parsed_edges.push_back(edge);
                    offset += kCosmoEdgeRecordSize;
                }
                if (rc != DOM_COSMO_GRAPH_OK) {
                    break;
                }
                have_edge = true;
                break;
            }
            case DOM_COSMO_CHUNK_FORN: {
                if (have_forn) {
                    rc = DOM_COSMO_GRAPH_INVALID_FORMAT;
                    break;
                }
                if (entry->version != 1u) {
                    rc = DOM_COSMO_GRAPH_MIGRATION_REQUIRED;
                    break;
                }
                rc = parse_foreign_chunk(foreign, pl, pl_len);
                if (rc != DOM_COSMO_GRAPH_OK) {
                    break;
                }
                have_forn = true;
                break;
            }
            default: {
                rc = append_foreign(foreign,
                                    entry->type_id,
                                    entry->version,
                                    entry->flags,
                                    pl,
                                    pl_len);
                if (rc != DOM_COSMO_GRAPH_OK) {
                    break;
                }
                break;
            }
        }
        if (rc != DOM_COSMO_GRAPH_OK) {
            break;
        }
    }

    dtlv_reader_dispose(&reader);
    if (rc != DOM_COSMO_GRAPH_OK) {
        return rc;
    }
    if (!have_enty || !have_edge) {
        return DOM_COSMO_GRAPH_INVALID_FORMAT;
    }

    {
        dom_cosmo_graph temp;
        dom_cosmo_graph_config *cfg_ptr = have_seed ? &config : 0;
        rc = dom_cosmo_graph_init(&temp, seed, cfg_ptr);
        if (rc != DOM_COSMO_GRAPH_OK) {
            return rc;
        }
        for (i = 0u; i < parsed_entities.size(); ++i) {
            const dom_cosmo_entity &ent = parsed_entities[i];
            u64 out_id = 0ull;
            rc = dom_cosmo_graph_add_entity(&temp,
                                            ent.kind,
                                            ent.stable_id.c_str(),
                                            ent.parent_id,
                                            &out_id);
            if (rc != DOM_COSMO_GRAPH_OK) {
                return rc;
            }
            if (out_id != ent.id) {
                return DOM_COSMO_GRAPH_INVALID_FORMAT;
            }
        }
        for (i = 0u; i < parsed_edges.size(); ++i) {
            const dom_cosmo_edge &edge = parsed_edges[i];
            dom_cosmo_edge_params params;
            u64 out_id = 0ull;
            params.duration_ticks = edge.duration_ticks;
            params.cost = edge.cost;
            params.event_table_id = edge.event_table_id;
            rc = dom_cosmo_graph_add_travel_edge(&temp,
                                                 edge.src_id,
                                                 edge.dst_id,
                                                 &params,
                                                 &out_id);
            if (rc != DOM_COSMO_GRAPH_OK) {
                return rc;
            }
            if (out_id != edge.id) {
                return DOM_COSMO_GRAPH_INVALID_FORMAT;
            }
        }
        rc = dom_cosmo_graph_validate(&temp, out_errors);
        if (rc != DOM_COSMO_GRAPH_OK) {
            return rc;
        }
        temp.foreign = foreign;
        *graph = temp;
    }

    return DOM_COSMO_GRAPH_OK;
}

} // namespace dom
