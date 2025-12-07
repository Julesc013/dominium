cmake_minimum_required(VERSION 3.15)

add_executable(dom_launcher_cli launcher_cli.c)
target_include_directories(dom_launcher_cli PRIVATE ${CMAKE_SOURCE_DIR}/include)
target_link_libraries(dom_launcher_cli PRIVATE dom_platform dom_core dom_app_mode)

add_executable(dom_setup_cli setup_cli.c)
target_include_directories(dom_setup_cli PRIVATE ${CMAKE_SOURCE_DIR}/include)
target_link_libraries(dom_setup_cli PRIVATE dom_platform dom_core dom_app_mode)

add_executable(dom_game_cli game_cli.c)
target_include_directories(dom_game_cli PRIVATE ${CMAKE_SOURCE_DIR}/include)
target_link_libraries(dom_game_cli PRIVATE dom_platform dom_core dom_app_mode dom_rend)
