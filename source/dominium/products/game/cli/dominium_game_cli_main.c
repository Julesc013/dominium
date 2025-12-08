#include <stdio.h>
#include <string.h>

#include "domino/mod.h"
#include "dominium/game_api.h"
#include "dominium/version.h"

static int dom_parse_arg(const char* arg, const char* prefix, char* out, size_t cap)
{
    size_t len;
    if (!arg || !prefix || !out || cap == 0) return 0;
    len = strlen(prefix);
    if (strncmp(arg, prefix, len) != 0) return 0;
    strncpy(out, arg + len, cap - 1);
    out[cap - 1] = '\0';
    return 1;
}

int main(int argc, char** argv)
{
    domino_instance_desc inst;
    int i;
    char instance_path[260];
    int has_path = 0;

    (void)argc;
    (void)argv;
    memset(&inst, 0, sizeof(inst));
    strncpy(inst.id, "default", sizeof(inst.id) - 1);
    strncpy(inst.label, "Default Instance", sizeof(inst.label) - 1);
    strncpy(inst.product_id, DOMINIUM_GAME_ID, sizeof(inst.product_id) - 1);
    dominium_game_get_version(&inst.product_version);

    for (i = 1; i < argc; ++i) {
        if (dom_parse_arg(argv[i], "--instance=", instance_path, sizeof(instance_path))) {
            has_path = 1;
        }
    }

    if (has_path) {
        if (domino_instance_load(instance_path, &inst) != 0) {
            printf("Failed to load instance: %s\n", instance_path);
            return 1;
        }
    }

    return dominium_game_run(&inst);
}
