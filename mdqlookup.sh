#!/usr/bin/env bash

ENTITYID=${1:?EntityID not specified. Usage: $0 <entityid> [ mdqendpoint ]}
MDQENDPOINT=${2:-${MDQENDPOINT:-http://mdq.ukfederation.org.uk/entities/}}
CURLOPTS=${CURLOPTS:-'-s'}
USERAGENT="getentity.sh+curl on $(uname -sm)"

# From https://stackoverflow.com/questions/296536/how-to-urlencode-data-for-curl-command
rawurlencode() {
  local string="${1}"
  local strlen=${#string}
  local encoded=""
  local pos c o

  for (( pos=0 ; pos<strlen ; pos++ )); do
     c=${string:$pos:1}
     case "$c" in
        [-_.~a-zA-Z0-9] ) o="${c}" ;;
        * )               printf -v o '%%%02x' "'$c"
     esac
     encoded+="${o}"
  done
  echo "${encoded}"    # You can either set a return variable (FASTER) 
  REPLY="${encoded}"   #+or echo the result (EASIER)... or both... :p
}

curl $CURLOPTS -A "$USERAGENT" -H 'Content-type: application/samlmetadata+xml' $MDQENDPOINT$(rawurlencode $ENTITYID)