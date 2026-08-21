#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_HEAD="365ae0a1377c7d404aa8bf8acef4d512cea7e89a"
PYTHON_VERSION="3.11.16"
REL="CERTIFICATES/prolate/item2_circle/b_tube_v2_1"

STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="${TMPDIR:-/tmp}/btube-v2.1-local-audit-${STAMP}.log"
ROUTE_CERT="${TMPDIR:-/tmp}/btube-route-consistency-${STAMP}.json"

exec > >(tee -a "$LOG") 2>&1

step() { printf '\n==== %s ====\n' "$*"; }
die()  { printf '\nFAIL: %s\nLOG: %s\n' "$*" "$LOG" >&2; exit 1; }

trap 'rc=$?; printf "\nSTOP: command failed (exit=%s) at line %s\nLOG: %s\n" "$rc" "$LINENO" "$LOG" >&2; exit "$rc"' ERR

step "Locate repository"
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "Run this script from inside geometric-dual-topology."
cd "$ROOT"
printf 'ROOT=%s\n' "$ROOT"

step "Pin exact commit"
HEAD="$(git rev-parse HEAD)"
printf 'HEAD=%s\n' "$HEAD"
[[ "$HEAD" == "$EXPECTED_HEAD" ]] || die "HEAD mismatch. Expected $EXPECTED_HEAD"

step "Require clean tracked/untracked tree"
if [[ -n "$(git status --porcelain)" ]]; then
    git status --short
    die "Repository is not clean."
fi
echo "GIT_CLEAN=PASS"

step "Select Python ${PYTHON_VERSION}"
command -v pyenv >/dev/null 2>&1 || die "pyenv is not available."
export PYENV_VERSION="$PYTHON_VERSION"
python --version
python -m pip --version
[[ "$(python -c 'import sys; print(".".join(map(str,sys.version_info[:3])))')" == "$PYTHON_VERSION" ]] || die "Python version mismatch."

step "Install/verify hash-locked dependency"
python -m pip install --disable-pip-version-check \
    --require-hashes --only-binary=:all: \
    -r "$REL/requirements-calibration.txt"

step "Compile Python sources"
(
    cd "$REL"
    export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/btube-pycache-${STAMP}"
    find . -name '*.py' -print0 | sort -z | xargs -0 python -m py_compile
)
echo "PY_COMPILE=PASS"

step "Run unit tests"
(
    cd "$REL"
    python -m unittest discover -s tests -v
)
echo "UNIT_TESTS=PASS"

step "Generate routed-backend consistency certificate"
rm -f "$ROUTE_CERT"
(
    cd "$REL"
    python route_consistency.py \
        --out "$ROUTE_CERT" \
        --source-head "$HEAD"
)
[[ -s "$ROUTE_CERT" ]] || die "Route-consistency certificate was not created."
echo "ROUTE_CERT_GENERATE=PASS"
sha256sum "$ROUTE_CERT"

step "Fresh independent verification of route certificate"
(
    cd "$REL"
    python route_consistency_verify.py \
        --certificate "$ROUTE_CERT" \
        --source-head "$HEAD"
)
echo "ROUTE_CERT_VERIFY=PASS"

step "Check binding gate (read-only)"
set +e
(
    cd "$REL"
    python calibration.py verify-config
)
VERIFY_RC=$?
set -e

if [[ "$VERIFY_RC" -eq 0 ]]; then
    echo "VERIFY_CONFIG=PASS"
    echo
    echo "SAFE_STOP=Binding gate is open."
    echo "No calibration run was started by this script."
else
    echo "VERIFY_CONFIG=BLOCKED (exit=$VERIFY_RC)"
    echo
    echo "SAFE_STOP=The repository's fail-closed binding gate is still closed."
    echo "This script intentionally does NOT modify config.calibration.json and does NOT start calibration."
fi

step "Final repository cleanliness"
LEFTOVER="$(git status --porcelain)"
if [[ -n "$LEFTOVER" ]]; then
    printf '%s\n' "$LEFTOVER"
    die "Repository changed during audit."
fi
echo "GIT_CLEAN_AFTER=PASS"

printf '\n========== SUMMARY ==========\n'
printf 'HEAD=%s\n' "$HEAD"
printf 'ROUTE_CERT=%s\n' "$ROUTE_CERT"
printf 'ROUTE_CERT_SHA256='
sha256sum "$ROUTE_CERT" | awk '{print $1}'
printf 'VERIFY_CONFIG_EXIT=%s\n' "$VERIFY_RC"
printf 'LOG=%s\n' "$LOG"
printf '=============================\n'
