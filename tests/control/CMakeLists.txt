add_executable(control_disabled_determinism_tests
    disabled/control_disabled_determinism_tests.cpp
)
target_include_directories(control_disabled_determinism_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(control_disabled_determinism_tests PRIVATE dominium_game)
target_link_libraries(control_disabled_determinism_tests PRIVATE libs::contracts)
target_compile_definitions(control_disabled_determinism_tests PRIVATE
    DOMINIUM_CONTROL_REGISTRY_PATH="${CMAKE_SOURCE_DIR}/data/registries/control_capabilities.registry"
)
set_target_properties(control_disabled_determinism_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME control_disabled_determinism COMMAND control_disabled_determinism_tests)

add_executable(control_non_interference_tests
    interference/control_non_interference_tests.cpp
)
target_include_directories(control_non_interference_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(control_non_interference_tests PRIVATE dominium_game)
target_link_libraries(control_non_interference_tests PRIVATE libs::contracts)
target_compile_definitions(control_non_interference_tests PRIVATE
    DOMINIUM_CONTROL_REGISTRY_PATH="${CMAKE_SOURCE_DIR}/data/registries/control_capabilities.registry"
)
set_target_properties(control_non_interference_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME control_non_interference COMMAND control_non_interference_tests)

add_executable(control_capability_registry_tests
    capability/control_capability_registry_tests.cpp
)
target_include_directories(control_capability_registry_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(control_capability_registry_tests PRIVATE dominium_game)
target_link_libraries(control_capability_registry_tests PRIVATE libs::contracts)
target_compile_definitions(control_capability_registry_tests PRIVATE
    DOMINIUM_CONTROL_REGISTRY_PATH="${CMAKE_SOURCE_DIR}/data/registries/control_capabilities.registry"
)
set_target_properties(control_capability_registry_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME control_registry COMMAND control_capability_registry_tests)

add_executable(control_refusal_tests
    capability/control_refusal_tests.cpp
)
target_include_directories(control_refusal_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(control_refusal_tests PRIVATE dominium_game)
target_link_libraries(control_refusal_tests PRIVATE libs::contracts)
target_compile_definitions(control_refusal_tests PRIVATE
    DOMINIUM_CONTROL_REGISTRY_PATH="${CMAKE_SOURCE_DIR}/data/registries/control_capabilities.registry"
)
set_target_properties(control_refusal_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME control_refusal COMMAND control_refusal_tests)

add_executable(control_audit_disclosure_tests
    audit/control_audit_disclosure_tests.cpp
)
target_include_directories(control_audit_disclosure_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(control_audit_disclosure_tests PRIVATE dominium_game)
target_link_libraries(control_audit_disclosure_tests PRIVATE libs::contracts)
target_compile_definitions(control_audit_disclosure_tests PRIVATE
    DOMINIUM_CONTROL_REGISTRY_PATH="${CMAKE_SOURCE_DIR}/data/registries/control_capabilities.registry"
)
set_target_properties(control_audit_disclosure_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME control_audit_disclosure COMMAND control_audit_disclosure_tests)

add_executable(control_removed_hooks_tests
    portability/control_removed_hooks_tests.cpp
    ${CMAKE_SOURCE_DIR}/engine/modules/core/dom_control.c
)
target_include_directories(control_removed_hooks_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
)
target_link_libraries(control_removed_hooks_tests PRIVATE libs::contracts)
target_compile_definitions(control_removed_hooks_tests PRIVATE
    DOM_CONTROL_HOOKS=0
)
set_target_properties(control_removed_hooks_tests PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME control_removed_hooks COMMAND control_removed_hooks_tests)
