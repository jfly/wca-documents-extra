#!/bin/bash

cd $(dirname "${0}")

PDF_NAME="${1}"
TEX_ENCODING="${2}"
LATEX_COMMAND="${3}"

BUILD_DIR="build"
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

TEX_FILE="${BUILD_DIR}/${PDF_NAME}-2013.tex"

cp "files/WCA_logo_with_text.eps" "build/"

if [ -f "${TEX_FILE}" ]; then rm "${TEX_FILE}"; fi
cat "templates/tex_documentclass.tex" >> "${TEX_FILE}"
cat "templates/encoding/${TEX_ENCODING}.tex" >> "${TEX_FILE}"
cat "templates/tex_header.tex" >> "${TEX_FILE}"
pandoc -t latex ../wca-documents/wca-regulations-2013.md >> "${TEX_FILE}"
cat "templates/tex_middle.tex" >> "${TEX_FILE}"
pandoc -t latex ../wca-documents/wca-guidelines-2013.md >> "${TEX_FILE}"
cat "templates/tex_footer.tex" >> "${TEX_FILE}"

"${LATEX_COMMAND}" -halt-on-error -output-directory="${BUILD_DIR}" "${TEX_FILE}"