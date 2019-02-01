#!/bin/bash

# echo -n 'entityID!username!salt' | openssl dgst -binary -sha1 | openssl base64
_USAGE="Usage: $0 <input> [ <salt> | ENV:SALT ]"

ENTITYID=${ENTITYID:-https://test.ukfederation.org.uk/entity}
SOURCEID=${SOURCEID:-${1:?$_USAGE}}
SALT=${SALT:-${2:?$_USAGE}}

INPUT="${ENTITYID}!${SOURCEID}!${SALT}"

echo "Input: $INPUT"
echo -n "$INPUT" | openssl dgst -binary -sha1 | openssl base64