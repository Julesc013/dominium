add_executable(engine_smoke_test
    engine_smoke_test.c
)
target_link_libraries(engine_smoke_test PRIVATE engine::domino)
set_target_properties(engine_smoke_test PROPERTIES
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
add_test(NAME engine_smoke COMMAND engine_smoke_test)
