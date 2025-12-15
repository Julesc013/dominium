#define main det_struct_inner_main
#include "../domino_struct/test_dg_struct_compile_determinism.c"
#undef main

int main(void) {
    return det_struct_inner_main();
}

