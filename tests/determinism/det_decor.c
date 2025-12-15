#define main det_decor_inner_main
#include "../domino_decor/test_dg_decor_compile_determinism.c"
#undef main

int main(void) {
    return det_decor_inner_main();
}

