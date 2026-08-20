#!/usr/bin/env bash
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT="${1:-$ROOT/dist/appimage}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PYINSTALLER_VERSION="6.22.2"
PYSIDE_VERSION="6.11.1"
APPIMAGETOOL_URL="${APPIMAGETOOL_URL:-https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage}"

for command in "$PYTHON_BIN" curl sha256sum; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "APPIMAGE_BUILD=FAIL: missing build command: $command" >&2
        exit 2
    fi
done

case "$(uname -m)" in
    x86_64|amd64) ;;
    *)
        echo "APPIMAGE_BUILD=FAIL: proof currently supports x86_64 builders only" >&2
        exit 2
        ;;
esac

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
    "$APPDIR/usr/share/icons/hicolor/scalable/apps"

cp -a "$WORK/dist/dirue-linux/." "$APPDIR/usr/lib/dirue-linux/"
ln -s ../lib/dirue-linux/dirue-linux "$APPDIR/usr/bin/dirue-linux"

cat >"$APPDIR/AppRun" <<'APP_RUN'
#!/bin/sh
APPDIR="${APPDIR:-$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)}"
exec "$APPDIR/usr/bin/dirue-linux" "$@"
APP_RUN
chmod 0755 "$APPDIR/AppRun"

install -Dm644 \
    "$ROOT/packaging/appimage/dirue-linux.desktop" \
    "$APPDIR/usr/share/applications/dirue-linux.desktop"
cp "$ROOT/packaging/appimage/dirue-linux.desktop" "$APPDIR/dirue-linux.desktop"

install -Dm644 \
    "$ROOT/packaging/appimage/dirue-linux.svg" \
    "$APPDIR/usr/share/icons/hicolor/scalable/apps/dirue-linux.svg"
ln -s usr/share/icons/hicolor/scalable/apps/dirue-linux.svg "$APPDIR/dirue-linux.svg"

"$VENV/bin/python" "$ROOT/packaging/appimage/check_appdir.py" "$APPDIR"

APPIMAGETOOL="${APPIMAGETOOL:-}"
if [ -z "$APPIMAGETOOL" ]; then
    APPIMAGETOOL="$WORK/appimagetool-x86_64.AppImage"
    curl --fail --location --retry 3 --retry-delay 2 \
        "$APPIMAGETOOL_URL" \
        --output "$APPIMAGETOOL"
    chmod 0755 "$APPIMAGETOOL"
fi

if [ ! -x "$APPIMAGETOOL" ]; then
    echo "APPIMAGE_BUILD=FAIL: appimagetool is not executable" >&2
    exit 3
fi

mkdir -p "$OUT"
ARTIFACT="$OUT/DIRUE-Linux-$VERSION-x86_64.AppImage"
rm -f "$ARTIFACT"

ARCH=x86_64 VERSION="$VERSION" APPIMAGE_EXTRACT_AND_RUN=1 \
    "$APPIMAGETOOL" "$APPDIR" "$ARTIFACT"
chmod 0755 "$ARTIFACT"

EXTRACT="$WORK/extracted"
mkdir -p "$EXTRACT"
(
    cd "$EXTRACT"
    "$ARTIFACT" --appimage-extract >/dev/null
)
"$VENV/bin/python" "$ROOT/packaging/appimage/check_appdir.py" "$EXTRACT/squashfs-root"

HASH="$(sha256sum "$ARTIFACT" | awk '{print $1}')"
SIZE="$(stat -c '%s' "$ARTIFACT")"

echo "APPIMAGE_ARTIFACT=$ARTIFACT"
echo "APPIMAGE_VERSION=$VERSION"
echo "APPIMAGE_SHA256=$HASH"
echo "APPIMAGE_SIZE=$SIZE"
echo "APPIMAGE_BUILD=PASS"
