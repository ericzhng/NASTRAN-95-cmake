
cmake_minimum_required(VERSION 3.20)
project(Nastran95 Fortran)

# Set the default Fortran compiler
set(CMAKE_Fortran_COMPILER gfortran CACHE STRING "Fortran compiler")

# Set the Fortran compilation flags depending on the compiler
if (CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
  # users can use -O1 or -g; currently other optimizations will not work
  set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -g -fno-range-check -fno-automatic -fallow-invalid-boz -fallow-argument-mismatch -fdec")
  # set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -fno-stack-arrays -Ofast -O3 -w -fno-range-check -fno-automatic -std=legacy -fallow-invalid-boz")
  # set(CMAKE_Fortran_FLAGS_DEBUG "-g")
  # set(CMAKE_Fortran_FLAGS_RELEASE "-Ofast -march=native")
elseif (CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
  set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} /Qipo /O3 /MP /integer-size=64 /Qdiag-disable:10448 /Qdiag-disable:warn")
endif()

function(efile out_var)
  set(options)
  set(oneValueArgs GLOB)
  set(multiValueArgs EXCLUDE)
  cmake_parse_arguments(EFILE "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  # Use file(GLOB ...) to collect all files matching the provided patterns
  file(GLOB_RECURSE temp_files CONFIGURE_DEPENDS ${EFILE_GLOB})

  # Apply exclusions
  foreach(exclude_pattern ${EFILE_EXCLUDE})
    # Filtering out files from the list that match the exclude patterns
    list(FILTER temp_files EXCLUDE REGEX "${exclude_pattern}")
  endforeach()

  # Set the results to the output variable
  set(${out_var} "${temp_files}" PARENT_SCOPE)
endfunction()


# Collect source files
# efile(BD_SOURCES GLOB "src/bd/*.f" EXCLUDE "bd/semdbd.f")
efile(BD_SOURCES GLOB "src/bd/*.f")
efile(MDS_SOURCES GLOB "src/mds/*.f" EXCLUDE chkfil.f)
efile(MIS_SOURCES GLOB "src/mis/*.f")

foreach(SRC_FILE ${MIS_SOURCES})
  set_source_files_properties(${SRC_FILE} PROPERTIES Fortran_PREPROCESS OFF)
endforeach()

# Create object libraries
add_library(nasmis_obj OBJECT ${MIS_SOURCES})
add_library(nasmds_obj OBJECT ${MDS_SOURCES})
add_library(nasbd_obj OBJECT ${BD_SOURCES})

# Combine object libraries into a single library
add_library(nas $<TARGET_OBJECTS:nasmis_obj>
                $<TARGET_OBJECTS:nasmds_obj>
                $<TARGET_OBJECTS:nasbd_obj>)
set_target_properties(nas PROPERTIES
  ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/lib
  Fortran_FLAGS "${FORTRAN_FLAGS}"
)

# Create executables
add_executable(nastran "src/nastrn.f" $<TARGET_OBJECTS:nasbd_obj>)
target_include_directories(nastran PRIVATE src/mds src/mis)
target_link_libraries(nastran PRIVATE nas)
set_target_properties(nastran PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin
  Fortran_FLAGS "${FORTRAN_FLAGS}"
)

add_executable(nasthelp "src/nasthelp.f")
set_target_properties(nasthelp PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin
  Fortran_FLAGS "${FORTRAN_FLAGS}"
)

add_executable(nastplot "src/nastplot.f")
set_target_properties(nastplot PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin
  Fortran_FLAGS "${FORTRAN_FLAGS}"
)

add_executable(ff "src/ff.f")
target_link_libraries(ff PRIVATE nas)
set_target_properties(ff PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin
  Fortran_FLAGS "${FORTRAN_FLAGS}"
)

add_executable(chkfil "src/chkfil.f")
set_target_properties(chkfil PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/bin
  Fortran_FLAGS "${FORTRAN_FLAGS}"
)

# Add custom commands for NASINFO and documentation files
add_custom_command(OUTPUT NASINFO
                   COMMAND ${CMAKE_COMMAND} -E create_symlink tests/rf/NASINFO NASINFO
                   COMMENT "Creating symlink for NASINFO")

file(GLOB DOCTXT docs/um/*.TXT)
foreach(FILE ${DOCTXT})
  get_filename_component(FILENAME ${FILE} NAME)
  add_custom_command(OUTPUT ${PROJECT_BINARY_DIR}/bin/${FILENAME}
                     COMMAND ${CMAKE_COMMAND} -E create_symlink ${FILE} ${PROJECT_BINARY_DIR}/bin/${FILENAME}
                     COMMENT "Creating symlink for ${FILENAME}")
endforeach()
