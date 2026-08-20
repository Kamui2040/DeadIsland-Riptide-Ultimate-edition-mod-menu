#!/usr/bin/env bash
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${1:-$ROOT/dist/appimage-baseline}"
BASELINE_IMAGE="quay.io/pypa/manylinux_2_34_x86_64@sha256:64decb8ae4b373180c246525a755c0afb2ca136334f0d64b41cf5f229283a7b6"
BASELINE_GLIBC="glibc 2.34"
BASELINE_PYTHON="/opt/python/cp311-cp311/bin/python"

fail() {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: $*" >&2
    exit 2
}

for command in podman git find sha256sum stat; do
    command -v "$command" >/dev/null 2>&1 || fail "missing build command: $command"
done

case "$(uname -m)" in
    x86_64|amd64) ;;
    *) fail "baseline build supports x86_64 builders only" ;;
esac

mkdir -p "$OUT"
OUT="$(CDPATH= cd -- "$OUT" && pwd)"

if find "$OUT" -maxdepth 1 -type f -name '*.AppImage' -print -quit | grep -q .; then
    fail "output directory already contains an AppImage"
fi

SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git -C "$ROOT" log -1 --format=%ct HEAD)}"
case "$SOURCE_DATE_EPOCH" in
    ''|*[!0-9]*) fail "SOURCE_DATE_EPOCH must be an integer" ;;
esac

if ! podman image exists "$BASELINE_IMAGE" >/dev/null 2>&1; then
    podman pull "$BASELINE_IMAGE" >/dev/null || fail "failed to pull pinned baseline image"
fi

podman run --rm \
    --userns=keep-id \
    --security-opt label=disable \
    --env HOME=/tmp/dirue-home \
    --env PYTHONDONTWRITEBYTECODE=1 \
    --env SOURCE_DATE_EPOCH="$SOURCE_DATE_EPOCH" \
    --volume "$ROOT:/workspace:ro" \
    --volume "$OUT:/output:rw" \
    "$BASELINE_IMAGE" \
    /bin/bash -s <<'CONTAINER'
set -eu

expected_glibc="glibc 2.34"
python_bin="/opt/python/cp311-cp311/bin/python"

actual_glibc="$(getconf GNU_LIBC_VERSION 2>/dev/null || true)"
[ "$actual_glibc" = "$expected_glibc" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: expected $expected_glibc, got $actual_glibc" >&2
    exit 3
}

[ -x "$python_bin" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: pinned CPython 3.11 runtime missing" >&2
    exit 3
}

python_version="$($python_bin -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
[ "$python_version" = "3.11" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: expected Python 3.11, got $python_version" >&2
    exit 3
}

mkdir -p "$HOME"
cd /workspace
PYTHON_BIN="$python_bin" packaging/appimage/build.sh /output
CONTAINER

artifact_count="$(find "$OUT" -maxdepth 1 -type f -name '*.AppImage' -print | wc -l | tr -d '[:space:]')"
[ "$artifact_count" = "1" ] || fail "expected exactly one host-visible AppImage, found $artifact_count"

HOST_ARTIFACT="$(find "$OUT" -maxdepth 1 -type f -name '*.AppImage' -print -quit)"
[ -f "$HOST_ARTIFACT" ] || fail "host-visible AppImage was not found"
[ -x "$HOST_ARTIFACT" ] || fail "host-visible AppImage is not executable"

HOST_HASH="$(sha256sum "$HOST_ARTIFACT" | awk '{print $1}')"
HOST_SIZE="$(stat -c '%s' "$HOST_ARTIFACT")"

echo "APPIMAGE_BASELINE_IMAGE=$BASELINE_IMAGE"
echo "APPIMAGE_BASELINE_GLIBC=$BASELINE_GLIBC"
echo "APPIMAGE_BASELINE_PYTHON=3.11"
echo "APPIMAGE_BASELINE_SOURCE_DATE_EPOCH=$SOURCE_DATE_EPOCH"
echo "APPIMAGE_BASELINE_ARTIFACT=$HOST_ARTIFACT"
echo "APPIMAGE_BASELINE_SHA256=$HOST_HASH"
echo "APPIMAGE_BASELINE_SIZE=$HOST_SIZE"
echo "APPIMAGE_BASELINE_BUILD=PASS"
