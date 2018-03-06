#
# Find LIBLZMA
#
#  LIBLZMA_INCLUDE_DIR - where to find lzma.h, etc.
#  LIBLZMA_LIBRARY     - List of libraries when using liblzma.
#  LIBLZMA_FOUND       - True if liblzma found.

FIND_PATH(LIBLZMA_INCLUDE_DIR lzma.h)

FIND_LIBRARY(LIBLZMA_LIBRARY NAMES lzma)

# handle the QUIETLY and REQUIRED arguments and set LIBLZMA_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(LZMA DEFAULT_MSG LIBLZMA_LIBRARY LIBLZMA_INCLUDE_DIR)

MARK_AS_ADVANCED(LIBLZMA_LIBRARY LIBLZMA_INCLUDE_DIR)

