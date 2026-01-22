add_executable(services_expiry_tests
    services_expiry_tests.cpp
    ${CMAKE_SOURCE_DIR}/server/authority/dom_server_authority.cpp
)
target_include_directories(services_expiry_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(services_expiry_tests PRIVATE
    dominium_game
    libs::contracts
)
set_target_properties(services_expiry_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME services_expiry COMMAND services_expiry_tests)
