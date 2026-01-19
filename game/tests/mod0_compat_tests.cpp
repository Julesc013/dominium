/*
MOD0 compatibility and safe-mode tests.
*/
#include "dominium/mods/mod_manifest.h"
#include "dominium/mods/mod_graph_resolver.h"
#include "dominium/mods/mod_safe_mode.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int parse_manifest(const char* text, mod_manifest* out_manifest) {
    mod_manifest_error err;
    if (mod_manifest_parse_text(text, out_manifest, &err) != 0) {
        fprintf(stderr, "Manifest parse error line %u: %s\n", err.line, err.message);
        return 1;
    }
    return 0;
}

static int test_ordering_deterministic(void) {
    mod_manifest mods[3];
    mod_graph graph;
    mod_graph_refusal refusal;
    const char* mod_a =
        "mod_id=mod.a\n"
        "mod_version=1.0.0\n"
        "dependency=mod.b@1.0.0-1.0.0\n"
        "payload_hash=fnv1a64:0000000000000001\n";
    const char* mod_b =
        "mod_id=mod.b\n"
        "mod_version=1.0.0\n"
        "payload_hash=fnv1a64:0000000000000002\n";
    const char* mod_c =
        "mod_id=mod.c\n"
        "mod_version=1.0.0\n"
        "payload_hash=fnv1a64:0000000000000003\n";

    EXPECT(parse_manifest(mod_c, &mods[0]) == 0, "parse mod c");
    EXPECT(parse_manifest(mod_a, &mods[1]) == 0, "parse mod a");
    EXPECT(parse_manifest(mod_b, &mods[2]) == 0, "parse mod b");

    EXPECT(mod_graph_build(&graph, mods, 3u, &refusal) == 0, "graph build");
    EXPECT(mod_graph_resolve(&graph, &refusal) == 0, "graph resolve");
    EXPECT(strcmp(graph.mods[graph.order[0]].mod_id, "mod.b") == 0, "order[0] should be mod.b");
    EXPECT(strcmp(graph.mods[graph.order[1]].mod_id, "mod.a") == 0, "order[1] should be mod.a");
    EXPECT(strcmp(graph.mods[graph.order[2]].mod_id, "mod.c") == 0, "order[2] should be mod.c");
    return 0;
}

static int test_conflict_refusal(void) {
    mod_manifest mods[2];
    mod_graph graph;
    mod_graph_refusal refusal;
    const char* mod_a =
        "mod_id=mod.a\n"
        "mod_version=1.0.0\n"
        "conflict=mod.b@1.0.0-1.0.0\n"
        "payload_hash=fnv1a64:0000000000000004\n";
    const char* mod_b =
        "mod_id=mod.b\n"
        "mod_version=1.0.0\n"
        "payload_hash=fnv1a64:0000000000000005\n";

    EXPECT(parse_manifest(mod_a, &mods[0]) == 0, "parse mod a");
    EXPECT(parse_manifest(mod_b, &mods[1]) == 0, "parse mod b");
    EXPECT(mod_graph_build(&graph, mods, 2u, &refusal) == 0, "graph build");
    EXPECT(mod_graph_resolve(&graph, &refusal) != 0, "graph resolve should fail");
    EXPECT(refusal.code == MOD_GRAPH_ERR_CONFLICT, "expected conflict refusal");
    return 0;
}

static int test_missing_dependency(void) {
    mod_manifest mods[1];
    mod_graph graph;
    mod_graph_refusal refusal;
    const char* mod_a =
        "mod_id=mod.a\n"
        "mod_version=1.0.0\n"
        "dependency=mod.b@1.0.0-1.0.0\n"
        "payload_hash=fnv1a64:0000000000000006\n";

    EXPECT(parse_manifest(mod_a, &mods[0]) == 0, "parse mod a");
    EXPECT(mod_graph_build(&graph, mods, 1u, &refusal) == 0, "graph build");
    EXPECT(mod_graph_resolve(&graph, &refusal) != 0, "graph resolve should fail");
    EXPECT(refusal.code == MOD_GRAPH_ERR_MISSING_DEP, "expected missing dep refusal");
    return 0;
}

static int test_safe_mode_deterministic(void) {
    mod_manifest mods[2];
    mod_graph graph;
    mod_graph_refusal refusal;
    mod_compat_report reports[2];
    mod_safe_mode_result result;
    const char* mod_sim =
        "mod_id=mod.sim\n"
        "mod_version=1.0.0\n"
        "sim_affecting=1\n"
        "payload_hash=fnv1a64:0000000000000007\n";
    const char* mod_ui =
        "mod_id=mod.ui\n"
        "mod_version=1.0.0\n"
        "sim_affecting=0\n"
        "payload_hash=fnv1a64:0000000000000008\n";

    EXPECT(parse_manifest(mod_sim, &mods[0]) == 0, "parse sim mod");
    EXPECT(parse_manifest(mod_ui, &mods[1]) == 0, "parse ui mod");
    EXPECT(mod_graph_build(&graph, mods, 2u, &refusal) == 0, "graph build");
    EXPECT(mod_graph_resolve(&graph, &refusal) == 0, "graph resolve");

    reports[0].result = MOD_COMPAT_ACCEPT;
    reports[1].result = MOD_COMPAT_REFUSE;
    EXPECT(mod_safe_mode_apply(&graph, reports, 2u, MOD_SAFE_MODE_NON_SIM_ONLY, &result) == 0,
           "safe mode apply");
    EXPECT(result.entry_count == 2u, "safe mode entry count");
    EXPECT(result.entries[0].status == MOD_SAFE_STATUS_DISABLED_SAFE_MODE, "sim mod disabled");
    EXPECT(result.entries[1].status == MOD_SAFE_STATUS_DISABLED_INCOMPATIBLE, "ui mod disabled");
    return 0;
}

static int test_graph_hash_stable(void) {
    mod_manifest mods_a[2];
    mod_manifest mods_b[2];
    mod_graph graph_a;
    mod_graph graph_b;
    mod_graph_refusal refusal;
    mod_schema_version schemas[1];
    mod_feature_epoch epochs[1];
    mod_graph_identity_input input;
    u64 hash_a;
    u64 hash_b;

    const char* mod_a =
        "mod_id=mod.a\n"
        "mod_version=1.0.0\n"
        "payload_hash=fnv1a64:0000000000000009\n";
    const char* mod_b =
        "mod_id=mod.b\n"
        "mod_version=1.0.1\n"
        "payload_hash=fnv1a64:000000000000000a\n";

    EXPECT(parse_manifest(mod_a, &mods_a[0]) == 0, "parse mod a");
    EXPECT(parse_manifest(mod_b, &mods_a[1]) == 0, "parse mod b");
    EXPECT(parse_manifest(mod_b, &mods_b[0]) == 0, "parse mod b 2");
    EXPECT(parse_manifest(mod_a, &mods_b[1]) == 0, "parse mod a 2");

    EXPECT(mod_graph_build(&graph_a, mods_a, 2u, &refusal) == 0, "graph build a");
    EXPECT(mod_graph_resolve(&graph_a, &refusal) == 0, "graph resolve a");
    EXPECT(mod_graph_build(&graph_b, mods_b, 2u, &refusal) == 0, "graph build b");
    EXPECT(mod_graph_resolve(&graph_b, &refusal) == 0, "graph resolve b");

    memset(&schemas[0], 0, sizeof(schemas[0]));
    strcpy(schemas[0].schema_id, "schema.core");
    mod_semver_parse("1.0.0", &schemas[0].version);
    memset(&epochs[0], 0, sizeof(epochs[0]));
    strcpy(epochs[0].epoch_id, "epoch.core");
    epochs[0].epoch = 1u;

    input.schemas = schemas;
    input.schema_count = 1u;
    input.epochs = epochs;
    input.epoch_count = 1u;

    hash_a = mod_graph_identity_hash(&graph_a, &input);
    hash_b = mod_graph_identity_hash(&graph_b, &input);
    EXPECT(hash_a == hash_b, "graph hash mismatch");
    return 0;
}

int main(void) {
    if (test_ordering_deterministic() != 0) return 1;
    if (test_conflict_refusal() != 0) return 1;
    if (test_missing_dependency() != 0) return 1;
    if (test_safe_mode_deterministic() != 0) return 1;
    if (test_graph_hash_stable() != 0) return 1;
    return 0;
}
