#define main det_packets_inner_main
#include "../../source/tests/pkt_determinism_test.c"
#undef main

int main(void) {
    return det_packets_inner_main();
}

