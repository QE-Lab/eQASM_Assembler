project(qisa-as CXX)

cmake_minimum_required(VERSION 3.1)

IF (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")
  ## Add support for C++11
  add_definitions(-std=c++11 -O0 )
ENDIF (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")

find_package(BISON REQUIRED)
find_package(FLEX REQUIRED)
find_package(PythonInterp 3 REQUIRED)

set(QISA_OPCODE_CONFIG_FILE "${PROJECT_SOURCE_DIR}/qisa_opcodes.qmap")

# Teach cmake how to generate the instruction declarations
# using the 'gen_qisa_instructions' python script.
add_custom_command(
  OUTPUT
    ${PROJECT_BINARY_DIR}/qisa_opcode_defs.inc
  COMMAND ${PYTHON_EXECUTABLE}
    ${PROJECT_SOURCE_DIR}/scripts/gen_qisa_instructions.py
    ARGS
      -d ${QISA_OPCODE_CONFIG_FILE}
      -co ${PROJECT_BINARY_DIR}/qisa_opcode_defs.inc
  DEPENDS
    ${QISA_OPCODE_CONFIG_FILE}
    ${PROJECT_SOURCE_DIR}/scripts/gen_qisa_instructions.py
  COMMENT "[Generating instruction declarations]"
  WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
)

BISON_TARGET(qisa_parser
             qisa_parser.yy
             ${CMAKE_CURRENT_BINARY_DIR}/qisa_parser.tab.cc)

IF (WIN32)
  SET(FLEX_OPTIONS "--wincompat")
ENDIF (WIN32)

FLEX_TARGET(qisa_lexer
            qisa_lexer.l
            ${CMAKE_CURRENT_BINARY_DIR}/qisa_lexer.yy.cc
	    COMPILE_FLAGS ${FLEX_OPTIONS})

ADD_FLEX_BISON_DEPENDENCY(qisa_lexer qisa_parser)

INCLUDE_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR})


# Generate the library that will be used by the main program as well as for exposing the assembler driver interface.
add_library(qisa-as-lib
  SHARED
  qisa_driver.h
  qisa_driver.cpp
  ${PROJECT_BINARY_DIR}/qisa_opcode_defs.inc
  qisa_qmap_parser.h
  qisa_qmap_parser.cpp

  qisa_parser.yy
  qisa_lexer.l
  ${QISA_OPCODE_CONFIG_FILE}
  ${FLEX_qisa_lexer_OUTPUTS}
  ${BISON_qisa_parser_OUTPUTS}
)

add_executable(qisa-as main.cpp)
target_link_libraries(qisa-as qisa-as-lib)

set_property(TARGET qisa-as qisa-as-lib
             PROPERTY CXX_STANDARD 14)


# We use Swig to expose the assembler driver interface to Python

FIND_PACKAGE(SWIG REQUIRED)
INCLUDE(${SWIG_USE_FILE})

FIND_PACKAGE(PythonLibs REQUIRED)
INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_PATH})

SET(CMAKE_SWIG_FLAGS "")
SET(CMAKE_SWIG_OUTDIR "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")

SET_SOURCE_FILES_PROPERTIES(qisa-as-swig.i PROPERTIES CPLUSPLUS ON)
SET_SOURCE_FILES_PROPERTIES(qisa-as-swig.i PROPERTIES SWIG_FLAGS "-includeall")
SWIG_ADD_MODULE(pyQisaAs python qisa-as-swig.i)
SWIG_LINK_LIBRARIES(pyQisaAs ${PYTHON_LIBRARIES} qisa-as-lib)

# Install section.
IF (QISA_AS_INSTALL_FOR_SETUP_PY)
  # Tailored for installation using setup.py, that installs the python
  # libraries in an intermediate staging area.
  # Note that the qisa-as executable is intentionally not installed.
  INSTALL(TARGETS qisa-as-lib ${SWIG_MODULE_pyQisaAs_REAL_NAME}
    DESTINATION ${CMAKE_INSTALL_PREFIX})
  INSTALL(FILES "${CMAKE_CURRENT_BINARY_DIR}/pyQisaAs.py" DESTINATION ${CMAKE_INSTALL_PREFIX})

ELSE (QISA_AS_INSTALL_FOR_SETUP_PY)

  # Normal installation.
  INSTALL(TARGETS qisa-as qisa-as-lib ${SWIG_MODULE_pyQisaAs_REAL_NAME}
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin)

  INSTALL(FILES "${CMAKE_CURRENT_BINARY_DIR}/pyQisaAs.py"
    DESTINATION lib)
ENDIF (QISA_AS_INSTALL_FOR_SETUP_PY)
