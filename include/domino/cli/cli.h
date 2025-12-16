/*
FILE: include/domino/cli/cli.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / cli/cli
RESPONSIBILITY: Defines the public contract for `cli` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_CLI_CLI_H_INCLUDED
#define DOMINO_CLI_CLI_H_INCLUDED

/* Domino CLI framework (C89)
 *
 * This layer provides a minimal, deterministic command-line interface used by
 * all Dominium products. It handles tokenizing argv, registering commands, and
 * dispatching handlers. Only libc + dsys may be used by callers.
 *
 * Features:
 *  - Tokenizer that understands:
 *      --key=value   -> key/value token
 *      --key value   -> key/value token (value consumed from next argv)
 *      <positional>  -> positional token
 *  - Command registry with built-in commands:
 *      help      : prints usage + commands
 *      version   : prints program/version string
 *      commands  : lists registered command names
 *  - Deterministic exit codes:
 *      0  : OK
 *      1  : bad usage
 *      2  : unknown command
 *      10-19 : internal CLI errors
 *  - Instance helper: optional --instance=<id> parsing, stored on the cli
 *    context for products that need instance-aware routing.
 *
 * Typical usage (product main):
 *
 *   d_cli cli;
 *   d_cli_init(&cli, argv[0], "0.1.0");
 *   d_cli_register(&cli, "run-headless", "...", run_headless_cmd, &state);
 *   return d_cli_dispatch(&cli, argc, (const char**)argv);
 *
 * Handlers receive argc/argv *after* the command name.
 */

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * Result / error codes
 *------------------------------------------------------------*/
enum {
    D_CLI_OK = 0,
    D_CLI_BAD_USAGE = 1,
    D_CLI_UNKNOWN_COMMAND = 2,
    D_CLI_ERR_NOMEM = 10,
    D_CLI_ERR_STATE = 11,
    D_CLI_ERR_NO_COMMAND = 12
};

/*------------------------------------------------------------
 * Tokenizer
 *------------------------------------------------------------*/
typedef struct d_cli_token {
    const char* key;        /* NULL for positional */
    const char* value;      /* positional string or option value */
    int         key_len;    /* length of key (for comparisons) */
    int         has_value;  /* 1 if value is present */
    int         is_positional;
    int         arg_index;  /* index in the argv array passed to tokenizer */
} d_cli_token;

typedef struct d_cli_args {
    int          argc;
    const char** argv;
    d_cli_token* tokens;
    int          token_count;
} d_cli_args;

/* Tokenize an argv array (does not copy strings; caller keeps argv alive). */
int  d_cli_tokenize(int argc, const char** argv, d_cli_args* out_args);
void d_cli_args_dispose(d_cli_args* args);

/* Token helpers */
const d_cli_token* d_cli_find_option(const d_cli_args* args, const char* key);
const d_cli_token* d_cli_get_positional(const d_cli_args* args, int index);
int  d_cli_count_positionals(const d_cli_args* args);
int  d_cli_match_key(const d_cli_token* tok, const char* key);

/*------------------------------------------------------------
 * Instance helper
 *------------------------------------------------------------*/
#define D_CLI_INSTANCE_ID_MAX 64
typedef struct d_cli_instance {
    int  present;
    char id[D_CLI_INSTANCE_ID_MAX];
} d_cli_instance;

void d_cli_instance_reset(d_cli_instance* inst);
int  d_cli_extract_instance(const d_cli_args* args, d_cli_instance* inst);

/*------------------------------------------------------------
 * Command registry / dispatcher
 *------------------------------------------------------------*/
typedef int (*d_cli_handler)(int argc, const char** argv, void* userdata);

typedef struct d_cli_command {
    const char*   name;
    const char*   help;
    d_cli_handler handler;
    void*         userdata;
} d_cli_command;

typedef struct d_cli {
    const char* program;   /* optional program name (argv[0]) */
    const char* version;   /* optional version string */

    d_cli_command* commands;
    int            command_count;
    int            command_capacity;

    d_cli_instance instance;
} d_cli;

void d_cli_init(d_cli* cli, const char* program, const char* version);
void d_cli_shutdown(d_cli* cli);

/* Registers a command. Returns 0 on success or D_CLI_ERR_* on failure. */
int  d_cli_register(d_cli* cli,
                    const char* name,
                    const char* help,
                    d_cli_handler handler,
                    void* userdata);

/* Dispatches based on the first positional argument (command name). */
int  d_cli_dispatch(d_cli* cli, int argc, const char** argv);

/* Accessors */
const d_cli_instance* d_cli_get_instance(const d_cli* cli);
const char*           d_cli_get_program(const d_cli* cli);
const char*           d_cli_get_version(const d_cli* cli);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CLI_CLI_H_INCLUDED */
