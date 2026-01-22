function(dom_ide_generate_legacy_vc71 out_dir project_name sources_var)
    file(MAKE_DIRECTORY "${out_dir}")
    set(_config_type "1")
    if(DOM_PRODUCT STREQUAL "engine" OR DOM_PRODUCT STREQUAL "game")
        set(_config_type "4")
    endif()

    set(_file_block "")
    foreach(_src IN LISTS ${sources_var})
        file(RELATIVE_PATH _rel "${CMAKE_SOURCE_DIR}" "${_src}")
        file(TO_CMAKE_PATH "${_rel}" _rel)
        string(APPEND _file_block "      <File RelativePath=\"${_rel}\" />\n")
    endforeach()

    string(MD5 _guid_raw "${project_name}")
    string(SUBSTRING "${_guid_raw}" 0 8 _g1)
    string(SUBSTRING "${_guid_raw}" 8 4 _g2)
    string(SUBSTRING "${_guid_raw}" 12 4 _g3)
    string(SUBSTRING "${_guid_raw}" 16 4 _g4)
    string(SUBSTRING "${_guid_raw}" 20 12 _g5)
    set(_guid "{${_g1}-${_g2}-${_g3}-${_g4}-${_g5}}")

    set(DOM_IDE_VC71_PROJECT_NAME "${project_name}")
    set(DOM_IDE_VC71_PROJECT_GUID "${_guid}")
    set(DOM_IDE_VC71_CONFIG_TYPE "${_config_type}")
    set(DOM_IDE_VC71_FILE_BLOCK "${_file_block}")
    configure_file(
        "${CMAKE_SOURCE_DIR}/cmake/ide/templates/vc71/vc71_project.vcproj.in"
        "${out_dir}/${project_name}.vcproj"
        @ONLY
    )
    configure_file(
        "${CMAKE_SOURCE_DIR}/cmake/ide/templates/vc71/vc71_solution.sln.in"
        "${out_dir}/${project_name}.sln"
        @ONLY
    )
endfunction()
