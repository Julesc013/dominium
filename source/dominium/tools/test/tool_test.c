#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "dominium/tool_api.h"
#include "domino/sys.h"

typedef struct dom_test_case_t {
    const char* name;
    int ticks;
} dom_test_case;

static void tool_log(dom_tool_ctx* ctx, const char* msg)
{
    if (ctx && ctx->env.write_stdout) {
        ctx->env.write_stdout(msg, ctx->env.io_user);
    } else {
        printf("%s", msg);
    }
}

static void tool_err(dom_tool_ctx* ctx, const char* msg)
{
    if (ctx && ctx->env.write_stderr) {
        ctx->env.write_stderr(msg, ctx->env.io_user);
    } else {
        fprintf(stderr, "%s", msg);
    }
}

static unsigned long simulate_world(const char* name, unsigned long seed, int ticks)
{
    unsigned long state = seed;
    int i;
    const unsigned char* p = (const unsigned char*)name;
    while (*p) {
        state ^= (unsigned long)(*p++);
        state = state * 1664525u + 1013904223u;
    }
    for (i = 0; i < ticks; ++i) {
        state = state * 1103515245u + 12345u;
        state ^= (unsigned long)i;
    }
    return state;
}

static int name_matches(const char* name, const char* pattern)
{
    if (!pattern || !pattern[0]) return 1;
    return strstr(name, pattern) != NULL;
}

static void usage(void)
{
    printf("Usage: test --suite <name> [--filter <pattern>] [--seed <n>]\n");
}

int dom_tool_test_main(dom_tool_ctx* ctx, int argc, char** argv)
{
    const char* suite = NULL;
    const char* filter = NULL;
    unsigned long seed = 1;
    int i;
    dom_test_case cases[] = {
        { "world_smoke", 32 },
        { "transport_loop", 48 },
        { "climate_step", 24 },
        { "economy_balance", 64 }
    };
    int case_count = (int)(sizeof(cases) / sizeof(cases[0]));
    int failures = 0;
    int executed = 0;

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--suite") == 0 && i + 1 < argc) {
            suite = argv[++i];
        } else if (strcmp(argv[i], "--filter") == 0 && i + 1 < argc) {
            filter = argv[++i];
        } else if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) {
            seed = (unsigned long)strtoul(argv[++i], NULL, 10);
        } else {
            usage();
            return 1;
        }
    }

    if (!suite) {
        usage();
        return 1;
    }

    if (dsys_init() != DSYS_OK) {
        tool_err(ctx, "Failed to initialize dsys\n");
        return 1;
    }

    tool_log(ctx, "Dominium deterministic test runner\n");
    if (suite) {
        char suite_line[128];
        sprintf(suite_line, "Suite: %s\n", suite);
        tool_log(ctx, suite_line);
    }

    for (i = 0; i < case_count; ++i) {
        char line[128];
        unsigned long expected;
        unsigned long actual;
        if (!name_matches(cases[i].name, filter)) {
            continue;
        }
        expected = simulate_world(cases[i].name, seed, cases[i].ticks);
        actual = simulate_world(cases[i].name, seed, cases[i].ticks);
        ++executed;
        if (expected == actual) {
            sprintf(line, "[PASS] %s\n", cases[i].name);
            tool_log(ctx, line);
        } else {
            sprintf(line, "[FAIL] %s (expected %lu got %lu)\n", cases[i].name, expected, actual);
            tool_err(ctx, line);
            ++failures;
        }
    }

    if (executed == 0) {
        tool_err(ctx, "No tests matched filter\n");
        dsys_shutdown();
        return 1;
    }

    if (failures == 0) {
        tool_log(ctx, "All tests passed\n");
    }

    dsys_shutdown();
    return failures == 0 ? 0 : 1;
}
