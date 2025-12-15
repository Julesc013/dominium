#define main det_graph_inner_main
#include "../../source/tests/graph_toolkit_determinism_test.c"
#undef main

int main(void) {
    return det_graph_inner_main();
}

