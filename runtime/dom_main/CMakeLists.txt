cmake_minimum_required(VERSION 3.15)

add_executable(dom_main
    main.cpp
    runtime_app.cpp
    runtime_display.cpp
    runtime_display_cli.cpp
    runtime_display_tui.cpp
    runtime_display_gui.cpp
    runtime_display_headless.cpp
)

target_include_directories(dom_main
    PRIVATE
        ${CMAKE_SOURCE_DIR}/engine
        ${CMAKE_SOURCE_DIR}/shared/include
        ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(dom_main
    PRIVATE
        dom_engine
        dom_shared
)

target_compile_features(dom_main PRIVATE cxx_std_98)

if(MINGW)
    target_link_options(dom_main PRIVATE -static -static-libstdc++ -static-libgcc -Wl,-Bstatic -lwinpthread -Wl,-Bdynamic)
    dom_copy_mingw_runtime(dom_main)
endif()
