set -e
FILE=${1:?Need input file}
EXTRA_OPTS=${2}

TMPDIR=$(mktemp -d)
PID=$$

split -d -p "-----BEGIN" "${FILE}" "${TMPDIR}/$$-"

for f in $(ls ${TMPDIR}/$$-*)
do
	openssl x509 -subject -issuer -dates -fingerprint ${EXTRA_OPTS} -in "$f"
	echo "-------"
done

rm -f "${TMPDIR}"/"$$"-*
rmdir "${TMPDIR}"
