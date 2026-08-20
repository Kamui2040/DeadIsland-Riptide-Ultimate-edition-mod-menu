#!/usr/bin/env bash
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${1:-$ROOT/dist/appimage-baseline}"
BASELINE_IMAGE="quay.io/pypa/manylinux_2_34_x86_64@sha256:64decb8ae4b373180c246525a755c0afb2ca136334f0d64b41cf5f229283a7b6"
BASELINE_GLIBC="glibc 2.34"
PYTHON_VERSION="3.11.16"
PYTHON_SOURCE_URL="https://www.python.org/ftp/python/3.11.16/Python-3.11.16.tar.xz"
PYTHON_SOURCE_SHA256="91bcdebfdde239a003ae93738a7fce0f9230fee5c4bc2b86f6e6e8c6f98aabe8"

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

podman run --rm -i \
    --userns=keep-id \
    --security-opt label=disable \
    --env HOME=/tmp/dirue-home \
    --env PYTHONDONTWRITEBYTECODE=1 \
    --env SOURCE_DATE_EPOCH="$SOURCE_DATE_EPOCH" \
    --env DIRUE_PYTHON_VERSION="$PYTHON_VERSION" \
    --env DIRUE_PYTHON_SOURCE_URL="$PYTHON_SOURCE_URL" \
    --env DIRUE_PYTHON_SOURCE_SHA256="$PYTHON_SOURCE_SHA256" \
    --volume "$ROOT:/workspace:ro" \
    --volume "$OUT:/output:rw" \
    "$BASELINE_IMAGE" \
    /bin/bash -s <<'CONTAINER'
set -eu

expected_glibc="glibc 2.34"
python_prefix="/tmp/dirue-python"
python_source="/tmp/dirue-python-source.tar.xz"
python_tree="/tmp/dirue-python-source"

actual_glibc="$(getconf GNU_LIBC_VERSION 2>/dev/null || true)"
[ "$actual_glibc" = "$expected_glibc" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: expected $expected_glibc, got $actual_glibc" >&2
    exit 3
}

for command in curl sha256sum tar make gcc; do
    command -v "$command" >/dev/null 2>&1 || {
        echo "APPIMAGE_BASELINE_BUILD=FAIL: missing container build command: $command" >&2
        exit 3
    }
done

rm -rf "$python_prefix" "$python_tree" "$python_source"
mkdir -p "$HOME" "$python_tree"

curl --proto '=https' --tlsv1.2 --fail --location --retry 3 --retry-delay 2 \
    "$DIRUE_PYTHON_SOURCE_URL" --output "$python_source"

actual_source_hash="$(sha256sum "$python_source" | awk '{print $1}')"
[ "$actual_source_hash" = "$DIRUE_PYTHON_SOURCE_SHA256" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: CPython source digest mismatch" >&2
    exit 3
}

tar -xJf "$python_source" -C "$python_tree" --strip-components=1
cd "$python_tree"

./configure \
    --prefix="$python_prefix" \
    --enable-shared \
    --with-ensurepip=install \
    >/dev/null

make -j2 >/dev/null
make install >/dev/null

export LD_LIBRARY_PATH="$python_prefix/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
python_bin="$python_prefix/bin/python3.11"

[ -x "$python_bin" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: shared CPython executable missing" >&2
    exit 3
}

python_version="$($python_bin -c 'import platform; print(platform.python_version())')"
[ "$python_version" = "$DIRUE_PYTHON_VERSION" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: expected Python $DIRUE_PYTHON_VERSION, got $python_version" >&2
    exit 3
}

shared="$($python_bin -c 'import sysconfig; print(sysconfig.get_config_var("Py_ENABLE_SHARED") or 0)')"
[ "$shared" = "1" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: compiled CPython is not shared" >&2
    exit 3
}

libpython="$($python_bin -c 'import os, sysconfig; print(os.path.join(sysconfig.get_config_var("LIBDIR") or "", sysconfig.get_config_var("LDLIBRARY") or ""))')"
[ -f "$libpython" ] || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: shared libpython was not installed" >&2
    exit 3
}

$python_bin -c 'import _ssl, bz2, ctypes, lzma, sqlite3, venv, zlib' || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: compiled CPython is missing required standard modules" >&2
    exit 3
}

$python_bin -m pip --version >/dev/null || {
    echo "APPIMAGE_BASELINE_BUILD=FAIL: compiled CPython pip bootstrap failed" >&2
    exit 3
}

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
echo "APPIMAGE_BASELINE_PYTHON=$PYTHON_VERSION"
echo "APPIMAGE_BASELINE_PYTHON_SOURCE_SHA256=$PYTHON_SOURCE_SHA256"
echo "APPIMAGE_BASELINE_SOURCE_DATE_EPOCH=$SOURCE_DATE_EPOCH"
echo "APPIMAGE_BASELINE_ARTIFACT=$HOST_ARTIFACT"
echo "APPIMAGE_BASELINE_SHA256=$HOST_HASH"
echo "APPIMAGE_BASELINE_SIZE=$HOST_SIZE"
echo "APPIMAGE_BASELINE_BUILD=PASS"
