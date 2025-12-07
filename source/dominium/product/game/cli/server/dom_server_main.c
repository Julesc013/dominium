#include <stdio.h>

#include "dom_core_version.h"

int main(void)
{
    printf("dom_server %s (build %u) stub\n",
           dom_version_full(),
           (unsigned)dom_version_build_number());
    return 0;
}
