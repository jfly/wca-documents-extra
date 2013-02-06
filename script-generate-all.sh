#!/bin/bash

HTML_FRAGMENT="0"
if [ "$#" -lt "2" ]
then
  HTML_FRAGMENT="${1}"
fi

rm -rf ./upload

./script-generate-language.sh "${HTML_FRAGMENT}" english

./script-generate-language.sh "${HTML_FRAGMENT}" german
./script-generate-language.sh "${HTML_FRAGMENT}" indonesian
./script-generate-language.sh "${HTML_FRAGMENT}" russian
./script-generate-language.sh "${HTML_FRAGMENT}" chinese
./script-generate-language.sh "${HTML_FRAGMENT}" hungarian

tar -zcf upload.tgz upload/

cd wca-documents
git checkout master