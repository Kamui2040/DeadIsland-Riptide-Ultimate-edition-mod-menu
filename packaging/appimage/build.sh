#!/usr/bin/env bash
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${1:-$ROOT/dist/appimage}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
APP_ID="io.github.Kamui2040.DIRUELinux"
COMMON="$ROOT/packaging/common"
PYINSTALLER_VERSION="6.22.2"
PYSIDE_VERSION="6.11.1"
APPIMAGE_GLIBC_BASELINE="2.34"
APPIMAGETOOL_VERSION="1.9.1"
APPIMAGETOOL_URL="https://github.com/AppImage/appimagetool/releases/download/1.9.1/appimagetool-x86_64.AppImage"
APPIMAGETOOL_SHA256="ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0"
APPIMAGE_RUNTIME_TAG="20251108"
APPIMAGE_RUNTIME_URL="https://github.com/AppImage/type2-runtime/releases/download/20251108/runtime-x86_64"
APPIMAGE_RUNTIME_SHA256="2fca8b443c92510f1483a883f60061ad09b46b978b2631c807cd873a47ec260d"

fail() {
    echo "APPIMAGE_BUILD=FAIL: $*" >&2
    exit 2
}

for command in "$PYTHON_BIN" curl sha256sum stat; do
    command -v "$command" >/dev/null 2>&1 || fail "missing build command: $command"
done

case "$(uname -m)" in
    x86_64|amd64) ;;
    *) fail "hardening build currently supports x86_64 builders only" ;;
esac

verify_sha256() {
    path="$1"
    expected="$2"
    actual="$(sha256sum "$path" | awk '{print $1}')"
    if [ "$actual" != "$expected" ]; then
        echo "APPIMAGE_BUILD=FAIL: digest mismatch for $(basename "$path")" >&2
        echo "EXPECTED=$expected" >&2
        echo "ACTUAL=$actual" >&2
        exit 3
    fi
}

download_verified() {
    url="$1"
    expected="$2"
    destination="$3"
    curl --proto '=https' --tlsv1.2 --fail --location --retry 3 --retry-delay 2 \
        "$url" --output "$destination"
    verify_sha256 "$destination" "$expected"
}

WORK="$(mktemp -d "${TMPDIR:-/tmp}/dirue-appimage.XXXXXX")"
cleanup() {
    rm -rf "$WORK"
}
trap cleanup EXIT HUP INT TERM

VENV="$WORK/venv"
"$PYTHON_BIN" -m venv "$VENV"
"$VENV/bin/python" -m pip install \
    --disable-pip-version-check \
    --no-cache-dir \
    "PyInstaller==$PYINSTALLER_VERSION" \
    "PySide6==$PYSIDE_VERSION"

VERSION="$(PYTHONPATH="$ROOT/src" "$VENV/bin/python" -c 'import dirue; print(dirue.__version__)')"

mkdir -p "$WORK/pyinstaller" "$WORK/spec" "$WORK/dist"
"$VENV/bin/pyinstaller" \
    --clean \
    --noconfirm \
    --windowed \
    --onedir \
    --name dirue-linux \
    --paths "$ROOT/src" \
    --workpath "$WORK/pyinstaller" \
    --specpath "$WORK/spec" \
    --distpath "$WORK/dist" \
    "$ROOT/packaging/appimage/entrypoint.py"

APPDIR="$WORK/DIRUELinux.AppDir"
mkdir -p \
    "$APPDIR/usr/lib/dirue-linux" \
    "$APPDIR/usr/bin" \
    "$APPDIR/usr/share/applications" \
    "$APPDIR/usr/share/metainfo" \
    "$APPDIR/usr/share/icons/hicolor/scalable/apps"

cp -a "$WORK/dist/dirue-linux/." "$APPDIR/usr/lib/dirue-linux/"
ln -s ../lib/dirue-linux/dirue-linux "$APPDIR/usr/bin/dirue-linux"

cat >"$APPDIR/AppRun" <<'APP_RUN'
#!/bin/sh
APPDIR="${APPDIR:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}"
exec "$APPDIR/usr/bin/dirue-linux" "$@"
APP_RUN
chmod 0755 "$APPDIR/AppRun"

install -Dm644 "$COMMON/$APP_ID.desktop" "$APPDIR/usr/share/applications/$APP_ID.desktop"
cp "$COMMON/$APP_ID.desktop" "$APPDIR/$APP_ID.desktop"
install -Dm644 "$COMMON/$APP_ID.metainfo.xml" "$APPDIR/usr/share/metainfo/$APP_ID.metainfo.xml"
install -Dm644 "$COMMON/$APP_ID.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/$APP_ID.svg"
ln -s "usr/share/icons/hicolor/scalable/apps/$APP_ID.svg" "$APPDIR/$APP_ID.svg"
ln -s "$APP_ID.svg" "$APPDIR/.DirIcon"

"$VENV/bin/python" "$ROOT/packaging/appimage/check_appdir.py" "$APPDIR"

APPIMAGETOOL="${APPIMAGETOOL:-$WORK/appimagetool-x86_64.AppImage}"
if [ ! -e "$APPIMAGETOOL" ]; then
    download_verified "$APPIMAGETOOL_URL" "$APPIMAGETOOL_SHA256" "$APPIMAGETOOL"
else
    verify_sha256 "$APPIMAGETOOL" "$APPIMAGETOOL_SHA256"
fi
chmod 0755 "$APPIMAGETOOL"

APPIMAGE_RUNTIME="${APPIMAGE_RUNTIME:-$WORK/runtime-x86_64}"
if [ ! -e "$APPIMAGE_RUNTIME" ]; then
    download_verified "$APPIMAGE_RUNTIME_URL" "$APPIMAGE_RUNTIME_SHA256" "$APPIMAGE_RUNTIME"
else
    verify_sha256 "$APPIMAGE_RUNTIME" "$APPIMAGE_RUNTIME_SHA256"
fi

mkdir -p "$OUT"
ARTIFACT="$OUT/DIRUE-Linux-$VERSION-x86_64.AppImage"
rm -f "$ARTIFACT"

ARCH=x86_64 VERSION="$VERSION" APPIMAGE_EXTRACT_AND_RUN=1 \
    "$APPIMAGETOOL" --runtime-file "$APPIMAGE_RUNTIME" "$APPDIR" "$ARTIFACT"
chmod 0755 "$ARTIFACT"

EXTRACT="$WORK/extracted"
mkdir -p "$EXTRACT"
(
    cd "$EXTRACT"
    "$ARTIFACT" --appimage-extract >/dev/null
)
"$VENV/bin/python" "$ROOT/packaging/appimage/check_appdir.py" "$EXTRACT/squashfs-root"

if ! AUDIT_OUTPUT="$(
    "$VENV/bin/python" "$ROOT/packaging/appimage/audit_glibc.py" \
        --max "$APPIMAGE_GLIBC_BASELINE" \
        "$ARTIFACT" \
        "$EXTRACT/squashfs-root"
)"; then
    fail "finished AppImage failed GLIBC compatibility audit"
fi

AUDIT_FILES="$(printf '%s\n' "$AUDIT_OUTPUT" | sed -n 's/^GLIBC_ELF_FILES=//p' | tail -n 1)"
AUDIT_MAX="$(printf '%s\n' "$AUDIT_OUTPUT" | sed -n 's/^GLIBC_MAX_REQUIRED=//p' | tail -n 1)"
AUDIT_STATUS="$(printf '%s\n' "$AUDIT_OUTPUT" | sed -n 's/^GLIBC_AUDIT=//p' | tail -n 1)"

[ "$AUDIT_STATUS" = "PASS" ] || fail "finished AppImage GLIBC audit did not report PASS"
case "$AUDIT_FILES" in
    ''|*[!0-9]*) fail "finished AppImage GLIBC audit returned invalid ELF count" ;;
esac
[ "$AUDIT_FILES" -gt 0 ] || fail "finished AppImage GLIBC audit found no ELF payloads"
[ -n "$AUDIT_MAX" ] || fail "finished AppImage GLIBC audit returned no maximum version"

HASH="$(sha256sum "$ARTIFACT" | awk '{print $1}')"
SIZE="$(stat -c '%s' "$ARTIFACT")"
BUILD_GLIBC="$(getconf GNU_LIBC_VERSION 2>/dev/null || printf 'unknown')"

echo "APPIMAGE_ARTIFACT=$ARTIFACT"
echo "APPIMAGE_VERSION=$VERSION"
echo "APPIMAGE_SHA256=$HASH"
echo "APPIMAGE_SIZE=$SIZE"
echo "APPIMAGE_APPIMAGETOOL=$APPIMAGETOOL_VERSION"
echo "APPIMAGE_RUNTIME_TAG=$APPIMAGE_RUNTIME_TAG"
echo "APPIMAGE_BUILD_GLIBC=$BUILD_GLIBC"
echo "APPIMAGE_TARGET_GLIBC=$APPIMAGE_GLIBC_BASELINE"
echo "APPIMAGE_ELF_FILES=$AUDIT_FILES"
echo "APPIMAGE_MAX_REQUIRED_GLIBC=$AUDIT_MAX"
echo "APPIMAGE_GLIBC_AUDIT=PASS"
echo "APPIMAGE_BUILD=PASS"
