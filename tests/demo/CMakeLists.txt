add_executable(demo_read_paths_tests
    demo_read_paths_tests.cpp
)
target_include_directories(demo_read_paths_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(demo_read_paths_tests PRIVATE
    dominium_game
    libs::contracts
)
set_target_properties(demo_read_paths_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME demo_read_paths COMMAND demo_read_paths_tests)
