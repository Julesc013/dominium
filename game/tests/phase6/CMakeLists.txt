add_executable(dominium_life_continuation_tests
    ${CMAKE_CURRENT_LIST_DIR}/../life/dom_life_continuation_tests.cpp
)
target_link_libraries(dominium_life_continuation_tests PRIVATE dominium_game)
set_target_properties(dominium_life_continuation_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_life_continuation COMMAND dominium_life_continuation_tests)

add_executable(dominium_life_death_tests
    ${CMAKE_CURRENT_LIST_DIR}/../life/dom_life_death_pipeline_tests.cpp
)
target_link_libraries(dominium_life_death_tests PRIVATE dominium_game)
set_target_properties(dominium_life_death_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_life_death COMMAND dominium_life_death_tests)

add_executable(dominium_life_birth_tests
    ${CMAKE_CURRENT_LIST_DIR}/../life/dom_life_birth_tests.cpp
)
target_link_libraries(dominium_life_birth_tests PRIVATE dominium_game)
set_target_properties(dominium_life_birth_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_life_birth COMMAND dominium_life_birth_tests)

add_executable(dominium_life_remains_tests
    ${CMAKE_CURRENT_LIST_DIR}/../life/dom_life_remains_salvage_tests.cpp
)
target_link_libraries(dominium_life_remains_tests PRIVATE dominium_game)
set_target_properties(dominium_life_remains_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_life_remains COMMAND dominium_life_remains_tests)

add_executable(dominium_civ0a_survival_tests
    ${CMAKE_CURRENT_LIST_DIR}/../civ0a/dom_civ0a_survival_tests.cpp
)
target_link_libraries(dominium_civ0a_survival_tests PRIVATE dominium_game)
set_target_properties(dominium_civ0a_survival_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_civ0a_survival COMMAND dominium_civ0a_survival_tests)

add_executable(dominium_civ0_population_tests
    ${CMAKE_CURRENT_LIST_DIR}/../civ0/dom_civ0_population_tests.cpp
)
target_link_libraries(dominium_civ0_population_tests PRIVATE dominium_game)
set_target_properties(dominium_civ0_population_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_civ0_population COMMAND dominium_civ0_population_tests)

add_executable(dominium_civ1_city_infra_tests
    ${CMAKE_CURRENT_LIST_DIR}/../civ1/dom_civ1_city_infra_tests.cpp
)
target_link_libraries(dominium_civ1_city_infra_tests PRIVATE dominium_game)
set_target_properties(dominium_civ1_city_infra_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_civ1_city_infra COMMAND dominium_civ1_city_infra_tests)

add_executable(dominium_civ2_governance_tests
    ${CMAKE_CURRENT_LIST_DIR}/../civ2/civ2_governance_tests.cpp
)
target_link_libraries(dominium_civ2_governance_tests PRIVATE dominium_game)
set_target_properties(dominium_civ2_governance_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_civ2_governance COMMAND dominium_civ2_governance_tests)

add_executable(dominium_civ3_knowledge_tests
    ${CMAKE_CURRENT_LIST_DIR}/../civ3/dom_civ3_knowledge_tests.cpp
)
target_link_libraries(dominium_civ3_knowledge_tests PRIVATE dominium_game)
set_target_properties(dominium_civ3_knowledge_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_civ3_knowledge COMMAND dominium_civ3_knowledge_tests)

add_executable(dominium_civ4_scale_tests
    ${CMAKE_CURRENT_LIST_DIR}/../civ4/dom_civ4_scale_tests.cpp
)
target_link_libraries(dominium_civ4_scale_tests PRIVATE dominium_game)
set_target_properties(dominium_civ4_scale_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_civ4_scale COMMAND dominium_civ4_scale_tests)

add_executable(dominium_mp0_parity_tests
    ${CMAKE_CURRENT_LIST_DIR}/../mp0/dom_mp0_parity_tests.cpp
)
target_link_libraries(dominium_mp0_parity_tests PRIVATE dominium_game)
set_target_properties(dominium_mp0_parity_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME dominium_mp0_parity COMMAND dominium_mp0_parity_tests)
