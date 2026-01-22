cmake_minimum_required(VERSION 3.16)

add_executable(dominium_client
    app/main_client.c
    ui/client_ui_compositor.c
    presentation/frame_graph_builder.cpp
    presentation/render_prep_system.cpp
)
target_link_libraries(dominium_client PRIVATE
    app::runtime
    domino_engine
    dominium_game
    libs::contracts
)
target_include_directories(dominium_client PRIVATE
    ${DOMINIUM_GENERATED_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/ui
)
set_target_properties(dominium_client PROPERTIES
    OUTPUT_NAME "client"
    LINKER_LANGUAGE CXX
    C_STANDARD 90
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)
