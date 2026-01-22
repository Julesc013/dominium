add_executable(tourist_non_interference_tests
    tourist_non_interference_tests.cpp
    ${CMAKE_SOURCE_DIR}/server/authority/dom_server_authority.cpp
)
target_include_directories(tourist_non_interference_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(tourist_non_interference_tests PRIVATE
    dominium_game
    libs::contracts
)
set_target_properties(tourist_non_interference_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME tourist_non_interference COMMAND tourist_non_interference_tests)
