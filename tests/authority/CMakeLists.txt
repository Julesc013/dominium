add_executable(authority_claims_tests
    authority_claims_tests.cpp
    ${CMAKE_SOURCE_DIR}/server/authority/dom_server_authority.cpp
)
target_include_directories(authority_claims_tests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${DOMINIUM_ENGINE_INCLUDE_DIR}
    ${DOMINIUM_GAME_INCLUDE_DIR}
)
target_link_libraries(authority_claims_tests PRIVATE
    dominium_game
    libs::contracts
)
set_target_properties(authority_claims_tests PROPERTIES
    CXX_STANDARD 98
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
add_test(NAME authority_claims COMMAND authority_claims_tests)
