#!/usr/bin/env bash
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${1:-$ROOT/dist/appimage-baseline}"
BASELINE_IMAGE="registry.access.redhat.com/ubi9/python-311@sha256:7b6cb58d3ff034df7b300800bd89a469d9bd2f739d43250d76b9c9e805307ab5"
BASELINE_GLIBC="glibc 2.34"
BASELINE_PYTHON="/usr/bin/python3.11"
BASELINE_PYTHON_VERSION="3.11.13"

fail() {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: $*" >&2
    exit 2
}

for command in podman git find sha256sum stat id; do
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

podman run --rm -i \
    --userns=keep-id \
    --user "$(id -u):$(id -g)" \
    --security-opt label=disable \
    --entrypoint /bin/bash \
    --env HOME=/tmp/dirue-home \
    --env PYTHONDONTWRITEBYTECODE=1 \
    --env SOURCE_DATE_EPOCH="$SOURCE_DATE_EPOCH" \
    --env DIRUE_BASELINE_GLIBC="$BASELINE_GLIBC" \
    --env DIRUE_BASELINE_PYTHON="$BASELINE_PYTHON" \
    --env DIRUE_BASELINE_PYTHON_VERSION="$BASELINE_PYTHON_VERSION" \
    --volume "$ROOT:/workspace:ro" \
    --volume "$OUT:/output:rw" \
    "$BASELINE_IMAGE" \
    -s <<'CONTAINER'
set -eu

actual_glibc="$(getconf GNU_LIBC_VERSION 2>/dev/null || true)"
[ "$actual_glibc" = "$DIRUE_BASELINE_GLIBC" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: expected $DIRUE_BASELINE_GLIBC, got $actual_glibc" >&2
    exit 3
}

python_bin="$DIRUE_BASELINE_PYTHON"
[ -x "$python_bin" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: pinned Python executable missing" >&2
    exit 3
}

python_version="$($python_bin -c 'import platform; print(platform.python_version())')"
[ "$python_version" = "$DIRUE_BASELINE_PYTHON_VERSION" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: expected Python $DIRUE_BASELINE_PYTHON_VERSION, got $python_version" >&2
    exit 3
}

shared="$($python_bin -c 'import sysconfig; print(sysconfig.get_config_var("Py_ENABLE_SHARED") or 0)')"
[ "$shared" = "1" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: pinned Python does not provide shared libpython" >&2
    exit 3
}

libpython="$($python_bin -c 'import os, sysconfig; print(os.path.join(sysconfig.get_config_var("LIBDIR") or "", sysconfig.get_config_var("LDLIBRARY") or ""))')"
[ -f "$libpython" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: shared libpython was not found" >&2
    exit 3
}

missing_modules="$($python_bin - <<'PY'
import importlib

required = ("_ssl", "bz2", "ctypes", "lzma", "venv", "zlib")
missing = []
for name in required:
    try:
        importlib.import_module(name)
    except Exception:
        missing.append(name)
print(",".join(missing))
PY
)"
[ -z "$missing_modules" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: pinned Python missing modules: $missing_modules" >&2
    exit 3
}

$python_bin -m pip --version >/dev/null 2>&1 || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: pinned Python pip is unavailable" >&2
    exit 3
}

for command in curl sha256sum stat; do
    command -v "$command" >/dev/null 2>&1 || {
        echo "APPIMAGE_BASELINE_BUILD=FAIL: missing container build command: $command" >&2
        exit 3
    }
done

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
echo "APPIMAGE_BASELINE_PYTHON=$BASELINE_PYTHON_VERSION"
echo "APPIMAGE_BASELINE_PYTHON_BIN=$BASELINE_PYTHON"
echo "APPIMAGE_BASELINE_SOURCE_DATE_EPOCH=$SOURCE_DATE_EPOCH"
echo "APPIMAGE_BASELINE_ARTIFACT=$HOST_ARTIFACT"
echo "APPIMAGE_BASELINE_SHA256=$HOST_HASH"
echo "APPIMAGE_BASELINE_SIZE=$HOST_SIZE"
echo "APPIMAGE_BASELINE_BUILD=PASS"
