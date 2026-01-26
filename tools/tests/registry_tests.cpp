/*
FILE: tools/tests/registry_tests.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / tests
RESPONSIBILITY: Validates registry determinism for CODEHYGIENE.
ALLOWED DEPENDENCIES: engine public headers + libs/contracts public headers.
FORBIDDEN DEPENDENCIES: game internals; GUI/TUI APIs.
DETERMINISM: Deterministic registry ordering and hashes.
*/
#include "domino/registry.h"
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"

#include <stdio.h>
#include <string.h>

#ifndef DOMINIUM_LAW_TARGETS_REGISTRY_PATH
#define DOMINIUM_LAW_TARGETS_REGISTRY_PATH "data/registries/law_targets.registry"
#endif

#define DOMINIUM_LAW_TARGETS_EXPECT_COUNT 49u
#define DOMINIUM_LAW_TARGETS_EXPECT_HASH  3333277067u
#define DOMINIUM_LAW_TARGETS_ID_AUTH_CAPABILITY_GRANT 3u
#define DOMINIUM_LAW_TARGETS_ID_EXEC_AUTH_TASK 21u
#define DOMINIUM_LAW_TARGETS_ID_LIFE_DEATH 29u
#define DOMINIUM_LAW_TARGETS_ID_TOOL_TELEPORT 45u
#define DOMINIUM_LAW_TARGETS_ID_WAR_ENGAGEMENT 49u

static void print_version_banner(void)
{
    printf("engine_version=%s\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\n");
}

static int assert_key_id(dom_registry* reg, const char* key, u32 expected)
{
    u32 id = dom_registry_id_from_key(reg, key);
    const char* round_trip = dom_registry_key_from_id(reg, expected);
    if (id != expected) {
        fprintf(stderr, "registry_tests: id mismatch for %s (got %u, expected %u)\n",
                key, (unsigned int)id, (unsigned int)expected);
        return 0;
    }
    if (!round_trip || strcmp(round_trip, key) != 0) {
        fprintf(stderr, "registry_tests: key mismatch for id %u (got %s, expected %s)\n",
                (unsigned int)expected, round_trip ? round_trip : "(null)", key);
        return 0;
    }
    return 1;
}

int main(void)
{
    dom_registry reg;
    dom_registry_result res;
    int ok = 1;

    print_version_banner();

    res = dom_registry_load_file(DOMINIUM_LAW_TARGETS_REGISTRY_PATH, &reg);
    if (res != DOM_REGISTRY_OK) {
        fprintf(stderr, "registry_tests: failed to load registry (%d)\n", (int)res);
        return 2;
    }

    if (dom_registry_count(&reg) != DOMINIUM_LAW_TARGETS_EXPECT_COUNT) {
        fprintf(stderr, "registry_tests: count mismatch (got %u, expected %u)\n",
                (unsigned int)dom_registry_count(&reg),
                (unsigned int)DOMINIUM_LAW_TARGETS_EXPECT_COUNT);
        ok = 0;
    }
    if (dom_registry_hash(&reg) != DOMINIUM_LAW_TARGETS_EXPECT_HASH) {
        fprintf(stderr, "registry_tests: hash mismatch (got %u, expected %u)\n",
                (unsigned int)dom_registry_hash(&reg),
                (unsigned int)DOMINIUM_LAW_TARGETS_EXPECT_HASH);
        ok = 0;
    }

    ok = ok && assert_key_id(&reg, "AUTH.CAPABILITY_GRANT", DOMINIUM_LAW_TARGETS_ID_AUTH_CAPABILITY_GRANT);
    ok = ok && assert_key_id(&reg, "EXEC.AUTH_TASK", DOMINIUM_LAW_TARGETS_ID_EXEC_AUTH_TASK);
    ok = ok && assert_key_id(&reg, "LIFE.DEATH", DOMINIUM_LAW_TARGETS_ID_LIFE_DEATH);
    ok = ok && assert_key_id(&reg, "TOOL.TELEPORT", DOMINIUM_LAW_TARGETS_ID_TOOL_TELEPORT);
    ok = ok && assert_key_id(&reg, "WAR.ENGAGEMENT", DOMINIUM_LAW_TARGETS_ID_WAR_ENGAGEMENT);

    dom_registry_free(&reg);
    return ok ? 0 : 2;
}
