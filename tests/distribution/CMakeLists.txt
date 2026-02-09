add_executable(distribution_single_package_tests
    distribution_single_package_tests.c
)
target_include_directories(distribution_single_package_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
)
target_link_libraries(distribution_single_package_tests PRIVATE
    libs::contracts
)
set_target_properties(distribution_single_package_tests PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME distribution_single_package COMMAND distribution_single_package_tests)

find_package(Python3 REQUIRED COMPONENTS Interpreter)

dom_add_testx(NAME distribution_zero_pack
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/distribution_zero_pack_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME distribution_max_bundle
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/distribution_max_bundle_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME distribution_profile_recommendations
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/distribution_profile_recommendation_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME distribution_lockfile_determinism
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/distribution_lockfile_determinism_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME distribution_pack_transition
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/distribution_pack_transition_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME distribution_legacy_pack
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/distribution_legacy_pack_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME distribution_platform_portability_consistency
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/platform_portability_consistency_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME distribution_legacy_platform_profiles
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/distribution_legacy_platform_profiles_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME distribution_prealpha_pack_policy
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/distribution_prealpha_pack_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME distribution_determinism_performance_baseline
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/distribution_determinism_performance_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

dom_add_testx(NAME distribution_sdk_profile_contracts
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/distribution_sdk_profile_tests.py
        --repo-root ${CMAKE_SOURCE_DIR}
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

add_executable(distribution_sdk_engine_compile_smoke
    sdk_engine_compile_smoke.c
)
target_include_directories(distribution_sdk_engine_compile_smoke PRIVATE
    ${CMAKE_SOURCE_DIR}/engine/include
    ${CMAKE_BINARY_DIR}/generated/include
)
target_link_libraries(distribution_sdk_engine_compile_smoke PRIVATE
    domino_engine
)
set_target_properties(distribution_sdk_engine_compile_smoke PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
dom_add_testx(NAME distribution_sdk_engine_compile_smoke
    COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR} --config $<CONFIG> --target distribution_sdk_engine_compile_smoke
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)

add_executable(distribution_sdk_game_compile_smoke
    sdk_game_compile_smoke.cpp
)
target_include_directories(distribution_sdk_game_compile_smoke PRIVATE
    ${CMAKE_SOURCE_DIR}/engine/include
    ${CMAKE_SOURCE_DIR}/game/include
    ${CMAKE_BINARY_DIR}/generated/include
)
target_link_libraries(distribution_sdk_game_compile_smoke PRIVATE
    domino_engine
    dominium_game
)
set_target_properties(distribution_sdk_game_compile_smoke PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
dom_add_testx(NAME distribution_sdk_game_compile_smoke
    COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR} --config $<CONFIG> --target distribution_sdk_game_compile_smoke
    LABELS ${DOM_TESTX_LABEL_PORTABILITY}
)
