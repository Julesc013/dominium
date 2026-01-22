/*
Minimal server entrypoint with MP0 loopback/local modes.
*/
#include "domino/control.h"
#include "domino/build_info.h"
#include "domino/caps.h"
#include "domino/config_base.h"
#include "domino/gfx.h"
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"
#include "dominium/session/mp0_session.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void print_help(void)
{
    printf("usage: server [options]\n");
    printf("options:\n");
    printf("  --help                      Show this help\n");
    printf("  --version                   Show product version\n");
    printf("  --build-info                Show build info + control capabilities\n");
    printf("  --status                    Show active control layers\n");
    printf("  --smoke                     Run deterministic CLI smoke\n");
    printf("  --selftest                  Alias for --smoke\n");
    printf("  --control-enable=K1,K2       Enable control capabilities (canonical keys)\n");
    printf("  --control-registry <path>    Override control registry path\n");
    printf("  --mp0-loopback               Run MP0 loopback demo\n");
    printf("  --mp0-server-auth            Run MP0 server-auth demo\n");
}

static void print_version(const char* product_version)
{
    printf("server %s\n", product_version);
}

static void print_build_info(const char* product_name, const char* product_version)
{
    printf("product=%s\n", product_name);
    printf("product_version=%s\n", product_version);
    printf("engine_version=%s\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("build_id=%s\n", DOM_BUILD_ID);
    printf("git_hash=%s\n", DOM_GIT_HASH);
    printf("toolchain_id=%s\n", DOM_TOOLCHAIN_ID);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\n");
    printf("protocol_control_caps=CONTROL_CAPS@1.0.0\n");
    printf("protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0\n");
    printf("abi_dom_build_info=%u\n", (unsigned int)DOM_BUILD_INFO_ABI_VERSION);
    printf("abi_dom_caps=%u\n", (unsigned int)DOM_CAPS_ABI_VERSION);
    printf("api_dsys=%u\n", 1u);
    printf("api_dgfx=%u\n", (unsigned int)DGFX_PROTOCOL_VERSION);
}

static void print_control_caps(const dom_control_caps* caps)
{
    const dom_registry* reg = dom_control_caps_registry(caps);
    u32 i;
    u32 enabled = dom_control_caps_enabled_count(caps);
#if DOM_CONTROL_HOOKS
    printf("control_hooks=enabled\n");
#else
    printf("control_hooks=removed\n");
#endif
    printf("control_caps_enabled=%u\n", (unsigned int)enabled);
    if (!reg) {
        return;
    }
    for (i = 0u; i < reg->count; ++i) {
        const dom_registry_entry* entry = &reg->entries[i];
        if (dom_control_caps_is_enabled(caps, entry->id)) {
            printf("control_cap=%s\n", entry->key);
        }
    }
}

static int enable_control_list(dom_control_caps* caps, const char* list)
{
    char buf[512];
    size_t len;
    char* token;
    if (!list || !caps) {
        return 0;
    }
    len = strlen(list);
    if (len >= sizeof(buf)) {
        return -1;
    }
    memcpy(buf, list, len + 1u);
    token = buf;
    while (token) {
        char* comma = strchr(token, ',');
        if (comma) {
            *comma = '\0';
        }
        if (*token) {
            if (dom_control_caps_enable_key(caps, token) != DOM_CONTROL_OK) {
                return -1;
            }
        }
        token = comma ? (comma + 1u) : (char*)0;
    }
    return 0;
}

static int mp0_build_state(dom_mp0_state* state)
{
    (void)dom_mp0_state_init(state, 0);
    state->consumption.params.consumption_interval = 5;
    state->consumption.params.hunger_max = 2;
    state->consumption.params.thirst_max = 2;
    if (dom_mp0_register_cohort(state, 1u, 1u, 100u, 101u, 201u, 301u) != 0) {
        return -1;
    }
    if (dom_mp0_register_cohort(state, 2u, 1u, 100u, 102u, 202u, 302u) != 0) {
        return -2;
    }
    if (dom_mp0_set_needs(state, 1u, 0u, 0u, 1u) != 0) {
        return -3;
    }
    if (dom_mp0_set_needs(state, 2u, 5u, 5u, 1u) != 0) {
        return -4;
    }
    if (dom_mp0_bind_controller(state, 1u, 101u) != 0) {
        return -5;
    }
    return 0;
}

static int mp0_build_commands(dom_mp0_command_queue* queue, dom_mp0_command* storage)
{
    survival_production_action_input gather;
    life_cmd_continuation_select cont;

    dom_mp0_command_queue_init(queue, storage, DOM_MP0_MAX_COMMANDS);
    memset(&gather, 0, sizeof(gather));
    gather.cohort_id = 2u;
    gather.type = SURVIVAL_ACTION_GATHER_FOOD;
    gather.start_tick = 0;
    gather.duration_ticks = 5;
    gather.output_food = 4u;
    gather.provenance_ref = 900u;
    if (dom_mp0_command_add_production(queue, 0, &gather) != 0) {
        return -1;
    }

    memset(&cont, 0, sizeof(cont));
    cont.controller_id = 1u;
    cont.policy_id = LIFE_POLICY_S1;
    cont.target_person_id = 102u;
    cont.action = LIFE_CONT_ACTION_TRANSFER;
    if (dom_mp0_command_add_continuation(queue, 15, &cont) != 0) {
        return -2;
    }
    dom_mp0_command_sort(queue);
    return 0;
}

static int mp0_run_server_auth(void)
{
    dom_mp0_state server;
    dom_mp0_state client;
    dom_mp0_command_queue queue;
    dom_mp0_command storage[DOM_MP0_MAX_COMMANDS];
    u64 hash_server;
    u64 hash_client;

    if (mp0_build_commands(&queue, storage) != 0) {
        return 1;
    }
    if (mp0_build_state(&server) != 0) {
        return 1;
    }
    if (mp0_build_state(&client) != 0) {
        return 1;
    }
    (void)dom_mp0_run(&server, &queue, 30);
    dom_mp0_copy_authoritative(&server, &client);
    hash_server = dom_mp0_hash_state(&server);
    hash_client = dom_mp0_hash_state(&client);
    printf("MP0 server-auth hash: %llu (client %llu)\n",
           (unsigned long long)hash_server,
           (unsigned long long)hash_client);
    return (hash_server == hash_client) ? 0 : 1;
}

static int mp0_run_loopback(void)
{
    dom_mp0_state state;
    dom_mp0_command_queue queue;
    dom_mp0_command storage[DOM_MP0_MAX_COMMANDS];
    u64 hash_state;

    if (mp0_build_commands(&queue, storage) != 0) {
        return 1;
    }
    if (mp0_build_state(&state) != 0) {
        return 1;
    }
    (void)dom_mp0_run(&state, &queue, 30);
    hash_state = dom_mp0_hash_state(&state);
    printf("MP0 loopback hash: %llu\n", (unsigned long long)hash_state);
    return 0;
}

int main(int argc, char** argv)
{
    const char* control_registry_path = "data/registries/control_capabilities.registry";
    const char* control_enable = 0;
    int want_help = 0;
    int want_version = 0;
    int want_build_info = 0;
    int want_status = 0;
    int want_loopback = 0;
    int want_server_auth = 0;
    int want_smoke = 0;
    int want_selftest = 0;
    dom_control_caps control_caps;
    int control_loaded = 0;
    int i;
    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            want_help = 1;
            continue;
        }
        if (strcmp(argv[i], "--version") == 0) {
            want_version = 1;
            continue;
        }
        if (strcmp(argv[i], "--build-info") == 0) {
            want_build_info = 1;
            continue;
        }
        if (strcmp(argv[i], "--status") == 0) {
            want_status = 1;
            continue;
        }
        if (strcmp(argv[i], "--smoke") == 0) {
            want_smoke = 1;
            continue;
        }
        if (strcmp(argv[i], "--selftest") == 0) {
            want_selftest = 1;
            continue;
        }
        if (strcmp(argv[i], "--control-registry") == 0 && i + 1 < argc) {
            control_registry_path = argv[i + 1];
            i += 1;
            continue;
        }
        if (strncmp(argv[i], "--control-enable=", 17) == 0) {
            control_enable = argv[i] + 17;
            continue;
        }
        if (strcmp(argv[i], "--control-enable") == 0 && i + 1 < argc) {
            control_enable = argv[i + 1];
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--mp0-loopback") == 0) {
            want_loopback = 1;
        }
        if (strcmp(argv[i], "--mp0-server-auth") == 0) {
            want_server_auth = 1;
        }
    }
    if (want_help) {
        print_help();
        return 0;
    }
    if (want_version) {
        print_version(DOMINIUM_GAME_VERSION);
        return 0;
    }
    if (want_smoke || want_selftest) {
        want_loopback = 1;
    }
    if (want_build_info || want_status || control_enable) {
        if (dom_control_caps_init(&control_caps, control_registry_path) != DOM_CONTROL_OK) {
            fprintf(stderr, "server: failed to load control registry: %s\n", control_registry_path);
            return 2;
        }
        control_loaded = 1;
        if (enable_control_list(&control_caps, control_enable) != 0) {
            fprintf(stderr, "server: invalid control capability list\n");
            dom_control_caps_free(&control_caps);
            return 2;
        }
    }
    if (want_build_info) {
        print_build_info("server", DOMINIUM_GAME_VERSION);
        if (control_loaded) {
            print_control_caps(&control_caps);
            dom_control_caps_free(&control_caps);
        }
        return 0;
    }
    if (want_status) {
        if (!control_loaded) {
            if (dom_control_caps_init(&control_caps, control_registry_path) == DOM_CONTROL_OK) {
                control_loaded = 1;
            } else {
                fprintf(stderr, "server: failed to load control registry: %s\n", control_registry_path);
                return 2;
            }
        }
        print_control_caps(&control_caps);
        dom_control_caps_free(&control_caps);
        return 0;
    }
    if (want_loopback) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return mp0_run_loopback();
    }
    if (want_server_auth) {
        if (control_loaded) {
            dom_control_caps_free(&control_caps);
        }
        return mp0_run_server_auth();
    }
    printf("Dominium server stub. Use --help.\\n");
    if (control_loaded) {
        dom_control_caps_free(&control_caps);
    }
    return 0;
}
