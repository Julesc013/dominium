function(dom_ide_generate_codewarrior out_dir project_name sources_var)
    file(MAKE_DIRECTORY "${out_dir}")
    set(_import_list "")
    foreach(_src IN LISTS ${sources_var})
        file(RELATIVE_PATH _rel "${CMAKE_SOURCE_DIR}" "${_src}")
        file(TO_CMAKE_PATH "${_rel}" _rel)
        string(APPEND _import_list "${_rel}\n")
    endforeach()
    file(WRITE "${out_dir}/${project_name}_import_list.txt" "${_import_list}")

    set(DOM_IDE_CW_PROJECT_NAME "${project_name}")
    configure_file(
        "${CMAKE_SOURCE_DIR}/cmake/ide/templates/codewarrior/codewarrior_project.mcp.in"
        "${out_dir}/${project_name}.mcp"
        @ONLY
    )
    dom_ide_append_warning("codewarrior_stub_project")
endfunction()
