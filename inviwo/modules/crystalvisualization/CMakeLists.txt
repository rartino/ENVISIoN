#--------------------------------------------------------------------
# Inviwo crystalvisualization Module
ivw_module(crystalvisualization)

#--------------------------------------------------------------------
# Add header files
set(HEADER_FILES
    #${CMAKE_CURRENT_SOURCE_DIR}/crystalvisualizationprocessor.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/coordinatereader.h
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/structuremesh.h
)
ivw_group("Header Files" ${HEADER_FILES})

#--------------------------------------------------------------------
# Add source files
set(SOURCE_FILES
    #${CMAKE_CURRENT_SOURCE_DIR}/crystalvisualizationprocessor.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/coordinatereader.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/processors/structuremesh.cpp
)
ivw_group("Source Files" ${SOURCE_FILES})


#--------------------------------------------------------------------
# Add shaders
set(SHADER_FILES
    #${CMAKE_CURRENT_SOURCE_DIR}/glsl/crystalvisualizationprocessor.frag
)
ivw_group("Shader Files" ${SHADER_FILES})


#--------------------------------------------------------------------
# Add Unittests
set(TEST_FILES
	#${CMAKE_CURRENT_SOURCE_DIR}/tests/unittests/crystalvisualization-test.cpp
)
ivw_add_unittest(${TEST_FILES})

#--------------------------------------------------------------------
# Create module
ivw_create_module(${SOURCE_FILES} ${HEADER_FILES} ${SHADER_FILES})

#--------------------------------------------------------------------
# Add shader directory to pack
# ivw_add_to_module_pack(${CMAKE_CURRENT_SOURCE_DIR}/glsl)