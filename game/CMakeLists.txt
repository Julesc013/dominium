cmake_minimum_required(VERSION 3.16)

add_library(dominium_game STATIC
    dominium_game_stub.c
    core/dom_interest_set.c
    core/dom_interest_sources.c
    core/dom_interest_macro.c
    core/dom_fidelity.c
    core/dom_data_validate.c
    core/dom_epistemic.c
    core/life/ability_packages.cpp
    core/life/control_authority.cpp
    core/life/continuation_policy.cpp
    core/life/controller_binding.cpp
    core/life/life_events_stub.cpp
)
add_custom_target(game_include_sanity
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/verify_includes_sanity.py
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Checking include boundaries for game sources"
)
add_dependencies(dominium_game game_include_sanity)
target_include_directories(dominium_game
    PUBLIC
        ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(dominium_game
    PUBLIC
        domino_engine
)
set_target_properties(dominium_game PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_library(game::dominium ALIAS dominium_game)
