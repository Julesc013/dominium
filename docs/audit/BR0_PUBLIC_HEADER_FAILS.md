Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

BR-0 public header compile failures baseline.

Command: ctest --test-dir out/build/vs2026/verify -C Debug -R public_header_c89_compile --output-on-failure
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 202: public_header_c89_compile
1/1 Test #202: public_header_c89_compile ........   Passed    1.63 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   1.71 sec

Command: ctest --test-dir out/build/vs2026/verify -C Debug -R public_header_cpp98_compile --output-on-failure
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 203: public_header_cpp98_compile
1/1 Test #203: public_header_cpp98_compile ......   Passed    1.79 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   1.85 sec

Post-fix run: 2026-02-07
Command: ctest --test-dir out/build/vs2026/verify -C Debug -R public_header_c89_compile --output-on-failure
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 202: public_header_c89_compile
1/1 Test #202: public_header_c89_compile ........   Passed    1.60 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   1.66 sec

Command: ctest --test-dir out/build/vs2026/verify -C Debug -R public_header_cpp98_compile --output-on-failure
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 203: public_header_cpp98_compile
1/1 Test #203: public_header_cpp98_compile ......   Passed    1.53 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   1.59 sec

Post-fix run: 2026-02-07 (mod_hash.h warning suppression)
Command: ctest --test-dir out/build/vs2026/verify -C Debug -R public_header_c89_compile --output-on-failure
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 202: public_header_c89_compile
1/1 Test #202: public_header_c89_compile ........   Passed    1.73 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   1.79 sec

Command: ctest --test-dir out/build/vs2026/verify -C Debug -R public_header_cpp98_compile --output-on-failure
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 203: public_header_cpp98_compile
1/1 Test #203: public_header_cpp98_compile ......   Passed    1.92 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   2.00 sec

Failure observed during full TestX (testx_all): 2026-02-07
Command: cmake --build out/build/vs2026/verify --config Debug --target testx_all
Failure: public_header_c89_compile
Snippet:
  engine/include/domino/provenance.h: missing u32/u64/SimTick types
  engine/include/domino/render/gui_prim.h: C4115 warning for struct dcvs_t
  engine/include/domino/snapshot.h: dom_snapshot_query redefinition (typedef vs function)

Post-fix run: 2026-02-07 (provenance/gui_prim/snapshot fixes)
Command: ctest --test-dir out/build/vs2026/verify -C Debug -R public_header_c89_compile --output-on-failure
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 202: public_header_c89_compile
1/1 Test #202: public_header_c89_compile ........   Passed    1.67 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   1.75 sec

Failure observed during full TestX (testx_all): 2026-02-07
Command: cmake --build out/build/vs2026/verify --config Debug --target testx_all
Failure: public_header_c89_compile
Snippet:
  engine/include/domino/agent.h: dom_agent_history_query typedef vs function conflict
  engine/include/domino/dvehicle.h: anonymous union rejected in C89
  engine/include/domino/knowledge_state.h: missing u32 type (core/types include)

Post-fix run: 2026-02-07 (agent.h, dvehicle.h, knowledge_state.h fixes)
Command: ctest --test-dir out/build/vs2026/verify -C Debug -R public_header_c89_compile --output-on-failure
Test project C:/Inbox/Git Repos/dominium/out/build/vs2026/verify
    Start 202: public_header_c89_compile
1/1 Test #202: public_header_c89_compile ........   Passed    1.58 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   1.65 sec
