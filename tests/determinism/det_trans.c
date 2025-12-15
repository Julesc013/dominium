#define main det_trans_inner_main
#include "../domino_trans/test_dg_trans_compile_determinism.c"
#undef main

int main(void) {
    return det_trans_inner_main();
}

