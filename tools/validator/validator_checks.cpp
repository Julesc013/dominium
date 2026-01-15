/*
FILE: source/dominium/tools/validator/validator_checks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/validator
RESPONSIBILITY: Implements bundle validation checks and report formatting.
*/
#include "validator_checks.h"

#include <cstdio>
#include <string>
#include <vector>

#include "dom_feature_epoch.h"

namespace dom {
namespace tools {
namespace {

static void append_json_escaped(std::string &out, const std::string &in) {
    size_t i;
    for (i = 0u; i < in.size(); ++i) {
        const unsigned char c = (unsigned char)in[i];
        switch (c) {
        case '\\': out += "\\\\"; break;
        case '"': out += "\\\""; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default:
            if (c < 0x20u) {
                char buf[8];
                std::snprintf(buf, sizeof(buf), "\\u%04x", (unsigned)c);
                out += buf;
            } else {
                out.push_back((char)c);
            }
            break;
        }
    }
}

static void require_chunk(dom_universe_bundle *bundle,
                          u32 type_id,
                          const char *label,
                          DomToolDiagnostics &diag) {
    const unsigned char *payload = 0;
    u32 size = 0u;
    u16 version = 0u;
    int rc = dom_universe_bundle_get_chunk(bundle, type_id, &payload, &size, &version);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        std::string msg = "missing_chunk:";
        msg += (label ? label : "unknown");
        diag.error(msg);
    }
}

} // namespace

bool validator_check_bundle(dom_universe_bundle *bundle,
                            DomToolDiagnostics &diag,
                            dom_universe_bundle_identity *out_id) {
    dom_universe_bundle_identity id;
    int rc;

    if (!bundle) {
        diag.error("bundle_null");
        return false;
    }
    rc = dom_universe_bundle_get_identity(bundle, &id);
    if (rc != DOM_UNIVERSE_BUNDLE_OK) {
        diag.error("identity_missing");
        return false;
    }

    if (!id.universe_id || id.universe_id_len == 0u) {
        diag.error("identity.universe_id_missing");
    }
    if (!id.instance_id || id.instance_id_len == 0u) {
        diag.error("identity.instance_id_missing");
    }
    if (id.ups == 0u) {
        diag.error("identity.ups_invalid");
    }
    if (id.feature_epoch == 0u) {
        diag.error("identity.feature_epoch_invalid");
    } else if (!dom_feature_epoch_supported(id.feature_epoch)) {
        diag.error("identity.feature_epoch_unsupported");
    }
    if (id.content_graph_hash == 0ull) {
        diag.warn("identity.content_graph_hash_zero");
    }
    if (id.sim_flags_hash == 0ull) {
        diag.warn("identity.sim_flags_hash_zero");
    }

    require_chunk(bundle, DOM_UNIVERSE_CHUNK_TIME, "TIME", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_COSM, "COSM", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_SYSM, "SYSM", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_BODS, "BODS", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_FRAM, "FRAM", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_TOPB, "TOPB", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_ORBT, "ORBT", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_SOVR, "SOVR", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_MEDB, "MEDB", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_WEAT, "WEAT", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_AERP, "AERP", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_AERS, "AERS", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_CNST, "CNST", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_STAT, "STAT", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_ROUT, "ROUT", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_TRAN, "TRAN", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_PROD, "PROD", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_MECO, "MECO", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_MEVT, "MEVT", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_FACT, "FACT", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_AISC, "AISC", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_CELE, "CELE", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_VESL, "VESL", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_SURF, "SURF", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_LOCL, "LOCL", diag);
    require_chunk(bundle, DOM_UNIVERSE_CHUNK_RNG,  "RNG", diag);

    if (out_id) {
        *out_id = id;
    }
    return !diag.has_errors();
}

std::string validator_report_json(const DomToolDiagnostics &diag,
                                  const dom_universe_bundle_identity *id,
                                  bool ok) {
    std::string out;
    size_t i;
    out.reserve(512u);
    out += "{";
    out += "\"ok\":";
    out += ok ? "true" : "false";

    if (id) {
        out += ",\"instance_id\":\"";
        if (id->instance_id && id->instance_id_len > 0u) {
            append_json_escaped(out, std::string(id->instance_id, id->instance_id_len));
        }
        out += "\"";
        out += ",\"universe_id\":\"";
        if (id->universe_id && id->universe_id_len > 0u) {
            append_json_escaped(out, std::string(id->universe_id, id->universe_id_len));
        }
        out += "\"";
    }

    out += ",\"errors\":[";
    for (i = 0u; i < diag.messages().size(); ++i) {
        const DomToolMessage &msg = diag.messages()[i];
        if (msg.severity != DOM_TOOL_ERROR) {
            continue;
        }
        if (out[out.size() - 1u] != '[') {
            out += ",";
        }
        out += "\"";
        append_json_escaped(out, msg.text);
        out += "\"";
    }
    out += "]";

    out += ",\"warnings\":[";
    for (i = 0u; i < diag.messages().size(); ++i) {
        const DomToolMessage &msg = diag.messages()[i];
        if (msg.severity != DOM_TOOL_WARNING) {
            continue;
        }
        if (out[out.size() - 1u] != '[') {
            out += ",";
        }
        out += "\"";
        append_json_escaped(out, msg.text);
        out += "\"";
    }
    out += "]";
    out += "}";
    return out;
}

} // namespace tools
} // namespace dom
