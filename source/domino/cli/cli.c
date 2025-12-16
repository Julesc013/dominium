/*
FILE: source/domino/cli/cli.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / cli/cli
RESPONSIBILITY: Implements `cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "domino/cli/cli.h"
#include "domino/version.h"

static int d_cli_is_long_option(const char* arg) {
    return (arg && arg[0] == '-' && arg[1] == '-' && arg[2] != '\0') ? 1 : 0;
}

static void d_cli_copy_string(const char* src, char* dst, size_t cap) {
    size_t len;
    if (!dst || cap == 0) {
        return;
    }
    if (!src) {
        dst[0] = '\0';
        return;
    }
    len = strlen(src);
    if (len >= cap) {
        len = cap - 1u;
    }
    memcpy(dst, src, len);
    dst[len] = '\0';
}

int d_cli_tokenize(int argc, const char** argv, d_cli_args* out_args) {
    d_cli_token* tokens;
    int          capacity;
    int          count;
    int          i;

    if (!out_args) {
        return D_CLI_ERR_STATE;
    }
    out_args->argc = argc;
    out_args->argv = argv;
    out_args->tokens = NULL;
    out_args->token_count = 0;

    if (argc <= 0) {
        return D_CLI_OK;
    }

    capacity = argc;
    tokens = (d_cli_token*)malloc(sizeof(d_cli_token) * (size_t)capacity);
    if (!tokens) {
        return D_CLI_ERR_NOMEM;
    }

    count = 0;
    for (i = 0; i < argc; ++i) {
        const char* arg = argv[i];
        if (d_cli_is_long_option(arg)) {
            const char* key_start = arg + 2;
            const char* eq = strchr(key_start, '=');
            tokens[count].is_positional = 0;
            tokens[count].key = key_start;
            tokens[count].arg_index = i;
            tokens[count].value = "";
            tokens[count].has_value = 0;
            if (eq) {
                tokens[count].key_len = (int)(eq - key_start);
                tokens[count].has_value = 1;
                tokens[count].value = eq + 1;
            } else {
                tokens[count].key_len = (int)strlen(key_start);
                if ((i + 1) < argc && !d_cli_is_long_option(argv[i + 1])) {
                    tokens[count].has_value = 1;
                    tokens[count].value = argv[i + 1];
                    i += 1; /* consume value */
                }
            }
            count += 1;
        } else {
            tokens[count].is_positional = 1;
            tokens[count].key = (const char*)0;
            tokens[count].key_len = 0;
            tokens[count].value = arg;
            tokens[count].has_value = 1;
            tokens[count].arg_index = i;
            count += 1;
        }
    }

    out_args->tokens = tokens;
    out_args->token_count = count;
    return D_CLI_OK;
}

void d_cli_args_dispose(d_cli_args* args) {
    if (!args) {
        return;
    }
    if (args->tokens) {
        free(args->tokens);
    }
    args->tokens = NULL;
    args->token_count = 0;
}

int d_cli_match_key(const d_cli_token* tok, const char* key) {
    size_t len;
    if (!tok || !key || tok->is_positional || !tok->key) {
        return 0;
    }
    len = strlen(key);
    if ((int)len != tok->key_len) {
        return 0;
    }
    return (strncmp(tok->key, key, len) == 0) ? 1 : 0;
}

const d_cli_token* d_cli_find_option(const d_cli_args* args, const char* key) {
    int i;
    if (!args || !args->tokens || !key) {
        return NULL;
    }
    for (i = 0; i < args->token_count; ++i) {
        if (d_cli_match_key(&args->tokens[i], key)) {
            return &args->tokens[i];
        }
    }
    return NULL;
}

const d_cli_token* d_cli_get_positional(const d_cli_args* args, int index) {
    int i;
    int count = 0;
    if (!args || !args->tokens || index < 0) {
        return NULL;
    }
    for (i = 0; i < args->token_count; ++i) {
        if (args->tokens[i].is_positional) {
            if (count == index) {
                return &args->tokens[i];
            }
            count += 1;
        }
    }
    return NULL;
}

int d_cli_count_positionals(const d_cli_args* args) {
    int i;
    int count = 0;
    if (!args || !args->tokens) {
        return 0;
    }
    for (i = 0; i < args->token_count; ++i) {
        if (args->tokens[i].is_positional) {
            count += 1;
        }
    }
    return count;
}

void d_cli_instance_reset(d_cli_instance* inst) {
    if (!inst) {
        return;
    }
    inst->present = 0;
    inst->id[0] = '\0';
}

int d_cli_extract_instance(const d_cli_args* args, d_cli_instance* inst) {
    const d_cli_token* tok;
    if (!inst) {
        return D_CLI_ERR_STATE;
    }
    d_cli_instance_reset(inst);
    tok = d_cli_find_option(args, "instance");
    if (tok && tok->has_value && tok->value) {
        d_cli_copy_string(tok->value, inst->id, sizeof(inst->id));
        inst->present = 1;
        return D_CLI_OK;
    }
    return D_CLI_OK;
}

static d_cli_command* d_cli_find_command(d_cli* cli, const char* name) {
    int i;
    size_t len;
    if (!cli || !name) {
        return NULL;
    }
    len = strlen(name);
    for (i = 0; i < cli->command_count; ++i) {
        const d_cli_command* cmd = &cli->commands[i];
        if (cmd->name && strlen(cmd->name) == len &&
            strncmp(cmd->name, name, len) == 0) {
            return &cli->commands[i];
        }
    }
    return NULL;
}

static const d_cli_command* d_cli_find_command_const(const d_cli* cli,
                                                     const char* name) {
    return d_cli_find_command((d_cli*)cli, name);
}

void d_cli_init(d_cli* cli, const char* program, const char* version) {
    if (!cli) {
        return;
    }
    cli->program = program;
    cli->version = version ? version : DOMINO_VERSION_STRING;
    cli->commands = NULL;
    cli->command_count = 0;
    cli->command_capacity = 0;
    d_cli_instance_reset(&cli->instance);
}

void d_cli_shutdown(d_cli* cli) {
    if (!cli) {
        return;
    }
    if (cli->commands) {
        free(cli->commands);
    }
    cli->commands = NULL;
    cli->command_count = 0;
    cli->command_capacity = 0;
    d_cli_instance_reset(&cli->instance);
}

int d_cli_register(d_cli* cli,
                   const char* name,
                   const char* help,
                   d_cli_handler handler,
                   void* userdata) {
    d_cli_command* cmd;
    d_cli_command* new_array;
    int new_cap;

    if (!cli || !name || !handler) {
        return D_CLI_ERR_STATE;
    }
    if (d_cli_find_command(cli, name)) {
        return D_CLI_ERR_STATE;
    }

    if (cli->command_count == cli->command_capacity) {
        new_cap = (cli->command_capacity == 0) ? 4 : (cli->command_capacity * 2);
        new_array = (d_cli_command*)realloc(cli->commands,
                                            sizeof(d_cli_command) * (size_t)new_cap);
        if (!new_array) {
            return D_CLI_ERR_NOMEM;
        }
        cli->commands = new_array;
        cli->command_capacity = new_cap;
    }

    cmd = &cli->commands[cli->command_count++];
    cmd->name = name;
    cmd->help = help ? help : "";
    cmd->handler = handler;
    cmd->userdata = userdata;
    return D_CLI_OK;
}

static void d_cli_print_usage(const d_cli* cli) {
    const char* program = (cli && cli->program) ? cli->program : "program";
    int i;
    printf("Usage: %s <command> [args]\n", program);
    printf("Commands:\n");
    if (cli) {
        for (i = 0; i < cli->command_count; ++i) {
            const d_cli_command* cmd = &cli->commands[i];
            printf("  %-12s %s\n", cmd->name ? cmd->name : "(null)",
                   cmd->help ? cmd->help : "");
        }
    }
}

static int d_cli_builtin_help(int argc, const char** argv, void* userdata) {
    d_cli* cli = (d_cli*)userdata;
    if (!cli) {
        return D_CLI_ERR_STATE;
    }
    if (argc > 0 && argv && argv[0]) {
        const d_cli_command* cmd = d_cli_find_command_const(cli, argv[0]);
        if (cmd) {
            printf("%s: %s\n", cmd->name ? cmd->name : "(unknown)",
                   cmd->help ? cmd->help : "");
            return D_CLI_OK;
        }
        printf("Unknown command '%s'\n", argv[0]);
        return D_CLI_UNKNOWN_COMMAND;
    }
    d_cli_print_usage(cli);
    return D_CLI_OK;
}

static int d_cli_builtin_version(int argc, const char** argv, void* userdata) {
    d_cli* cli = (d_cli*)userdata;
    const char* program;
    const char* version;
    (void)argc;
    (void)argv;
    if (!cli) {
        return D_CLI_ERR_STATE;
    }
    program = cli->program ? cli->program : "program";
    version = cli->version ? cli->version : "(unknown)";
    printf("%s version %s\n", program, version);
    return D_CLI_OK;
}

static int d_cli_builtin_commands(int argc, const char** argv, void* userdata) {
    d_cli* cli = (d_cli*)userdata;
    int i;
    (void)argc;
    (void)argv;
    if (!cli) {
        return D_CLI_ERR_STATE;
    }
    for (i = 0; i < cli->command_count; ++i) {
        const d_cli_command* cmd = &cli->commands[i];
        if (cmd->name) {
            printf("%s\n", cmd->name);
        }
    }
    return D_CLI_OK;
}

static int d_cli_register_builtins(d_cli* cli) {
    int rc;
    if (!d_cli_find_command(cli, "help")) {
        rc = d_cli_register(cli, "help", "Show usage or help for a command",
                            d_cli_builtin_help, cli);
        if (rc != D_CLI_OK) return rc;
    }
    if (!d_cli_find_command(cli, "version")) {
        rc = d_cli_register(cli, "version", "Show version information",
                            d_cli_builtin_version, cli);
        if (rc != D_CLI_OK) return rc;
    }
    if (!d_cli_find_command(cli, "commands")) {
        rc = d_cli_register(cli, "commands", "List available commands",
                            d_cli_builtin_commands, cli);
        if (rc != D_CLI_OK) return rc;
    }
    return D_CLI_OK;
}

int d_cli_dispatch(d_cli* cli, int argc, const char** argv) {
    d_cli_args args;
    const d_cli_token* cmd_tok;
    d_cli_command* cmd;
    int rc;
    int trimmed_argc;
    const char** trimmed_argv;
    int cmd_argc;
    const char** cmd_argv;

    if (!cli) {
        return D_CLI_ERR_STATE;
    }
    rc = d_cli_register_builtins(cli);
    if (rc != D_CLI_OK) {
        return rc;
    }
    if (!cli->program && argc > 0) {
        cli->program = argv[0];
    }
    if (!cli->version) {
        cli->version = DOMINO_VERSION_STRING;
    }

    if (argc <= 1) {
        d_cli_print_usage(cli);
        return D_CLI_BAD_USAGE;
    }

    trimmed_argc = argc - 1;
    trimmed_argv = argv + 1;

    rc = d_cli_tokenize(trimmed_argc, trimmed_argv, &args);
    if (rc != D_CLI_OK) {
        return rc;
    }

    (void)d_cli_extract_instance(&args, &cli->instance);

    cmd_tok = d_cli_get_positional(&args, 0);
    if (!cmd_tok || !cmd_tok->value) {
        d_cli_args_dispose(&args);
        d_cli_print_usage(cli);
        return D_CLI_BAD_USAGE;
    }

    cmd = d_cli_find_command(cli, cmd_tok->value);
    if (!cmd) {
        fprintf(stderr, "Unknown command '%s'\n", cmd_tok->value);
        d_cli_args_dispose(&args);
        return D_CLI_UNKNOWN_COMMAND;
    }

    cmd_argv = trimmed_argv + cmd_tok->arg_index + 1;
    cmd_argc = trimmed_argc - (cmd_tok->arg_index + 1);

    rc = cmd->handler(cmd_argc, cmd_argv, cmd->userdata);

    d_cli_args_dispose(&args);
    return rc;
}

const d_cli_instance* d_cli_get_instance(const d_cli* cli) {
    if (!cli) {
        return NULL;
    }
    return &cli->instance;
}

const char* d_cli_get_program(const d_cli* cli) {
    if (!cli) {
        return NULL;
    }
    return cli->program;
}

const char* d_cli_get_version(const d_cli* cli) {
    if (!cli) {
        return NULL;
    }
    return cli->version;
}
