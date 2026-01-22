add_executable(piracy_base_free_tests
    piracy_base_free_tests.cpp
    ${CMAKE_SOURCE_DIR}/server/authority/dom_server_authority.cpp
)
target_include_directories(piracy_base_free_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(piracy_base_free_tests PRIVATE
    dominium_game
    launcher_core
    libs::contracts
)
set_target_properties(piracy_base_free_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME piracy_base_free COMMAND piracy_base_free_tests)
