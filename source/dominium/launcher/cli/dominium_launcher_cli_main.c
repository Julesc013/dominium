#include <stddef.h>
#include <stdio.h>
#include <string.h>

#include "dominium/launch_api.h"
#include "dominium/product_info.h"

int main(int argc, char** argv)
{
    int i;
    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--introspect-json") == 0) {
            dominium_print_product_info_json(dom_get_product_info_launcher(), stdout);
            return 0;
        }
    }
    /* Later: parse args for specific view/instance actions. */
    return dominium_launcher_run(NULL);
}
