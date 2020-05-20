#!/bin/bash
# specify API details
API_METHOD="GET"
API_PATH='/api/v2/tags/Needs%20Review/indicators'
API_URL='https://c19ctc.threatconnect.com'${API_PATH}
# provide authentication details
API_SECRET='zTa86OD?u?U5YYoIyn2naSE1DhI3JhhpEzV0G1asLhzCAntBUfhkQ0aQnUXonJHC'
API_ID='49442269406862232007'
# create the signature
TIMESTAMP=`date +%s`
signature="${API_PATH}:${API_METHOD}:${TIMESTAMP}"
hmac_signature=$(echo -n ${signature} | openssl dgst -binary -sha256 -hmac ${API_SECRET} | base64)
authorization="TC ${API_ID}:${hmac_signature}"
# use this if python is not installed on your system
curl -s -i -H "Timestamp: ${TIMESTAMP}" -H "Authorization: ${authorization}" -X ${API_METHOD} "${API_URL}" 