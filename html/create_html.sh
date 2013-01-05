#!/bin/bash

set -e

VERSION="${1}"
MARKDOWN_PROGRAM="rdiscount" # Markdown.py and the python markdown package both don't handle the nested lists properly.

function htmlify {
  FILE="${1}"
  TITLE="${2}"
  SOURCE="${3}"

  rm "${FILE}"
  cat html_header_1.html >> "${FILE}"
  echo -n "${TITLE}" >> "${FILE}"
  cat html_header_2.html >> "${FILE}"
  "${MARKDOWN_PROGRAM}" "${SOURCE}" >> "${FILE}"
  cat html_footer.html >> "${FILE}"
}

cp "../wca-documents/wca-regulations-2013.md" "index.md"
cp "../wca-documents/wca-guidelines-2013.md" "guidelines.md"

pushd "../wca-documents" > /dev/null
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_VERSION=$(git rev-parse --short HEAD)
popd > /dev/null

./create_html.py \
  --regulations-file "index.md" \
  --guidelines-file "guidelines.md" \
  --git-branch "${GIT_BRANCH}" \
  --git-hash "${GIT_VERSION}"

htmlify "index.html"        "WCA Regulations 2013"    "index.md"
htmlify "guidelines.html"   "WCA Guidelines 2013"     "guidelines.md"
htmlify "history.html"      "WCA Regulations History" "history.md"
htmlify "translations.html" "WCA Translations"        "translations.md"
htmlify "scrambles.html"    "WCA Scrambles"           "scrambles.md"