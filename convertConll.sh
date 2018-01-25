#!/bin/bash

set -e # fail fast

MY_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" > /dev/null && pwd )"
source "${MY_DIR}/config.sh"

if [ $# -lt 3 -o $# -gt 3 ]; then
   echo "USAGE: `basename "${0}"` <input-file> <output-dir>"
   exit 1
fi

if [ `uname -m` != "x86_64" ]; then
   echo -n "\nNOTE: You should really be running this on a 64-bit architecture."
   # give the user the chance to CTRL-C here...
   for dot in 1 2 3 4 5 6; do
       sleep 1
       echo -n "."
   done
   echo
fi

# location of input file. must be absolute path
INPUT_FILE="${1}"

# where to write the output
OUTPUT_DIR="${2}"

# unique row numbers to name the converted files
ROWNUM="${3}"

POS_TAGGED="${OUTPUT_DIR}/pos.tagged"
TEST_PARSED_FILE="${OUTPUT_DIR}/conll"

bash ${MY_DIR}/tokenizeAndPosTag.sh ${INPUT_FILE} ${OUTPUT_DIR}

echo "**********************************************************************"
echo "Converting postagged input to conll."
# convert to conll so Malt can read it
time ${JAVA_HOME_BIN}/java -classpath ${CLASSPATH} \
    edu.cmu.cs.lti.ark.fn.data.prep.formats.ConvertFormat \
    --input ${POS_TAGGED} \
    --inputFormat pos \
    --output ${POS_TAGGED}.conll \
    --outputFormat conll
echo "Done converting postagged input to conll."

echo "**********************************************************************"
echo "Running MaltParser...."
pushd ${SEMAFOR_HOME}/scripts/maltparser-1.7.2
time ${JAVA_HOME_BIN}/java -Xmx2g \
    -jar maltparser-1.7.2.jar \
    -w ${MALT_MODEL_DIR} \
    -c engmalt.linear-1.7 \
    -i ${POS_TAGGED}.conll \
    -o ${TEST_PARSED_FILE}_${ROWNUM}
echo "Finished running MaltParser."
echo "**********************************************************************"
echo
echo