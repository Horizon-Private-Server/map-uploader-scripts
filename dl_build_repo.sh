#!/bin/bash

BASE_PATH="${1%/}"
GAME=dl
MAPS_DIR=$BASE_PATH/$GAME/
OUT_ZIP=$BASE_PATH/dl_custom_maps.zip
INDEX_PATH=$BASE_PATH/index_dl_ntsc.txt

if [ ! -d "$1" ]; then
    echo "missing path to map repository"
    echo "ie /var/www/static/downloads/maps"
    exit 0
fi

echo "building $BASE_PATH"

cd $BASE_PATH

# Zip Individual Maps
find "$MAPS_DIR" -type f -name "*.version" | sort | while read -r version_file; do
    # Get base name without extension
    base="${version_file%.version}"
    filename=$(basename "$base")

    # Collect all files that share the base name
    # files_to_zip=("$base".*)  # glob matches all files like base.*

    # Create zip named after the base
    echo "$filename.zip"
    file="$MAPS_DIR/$filename.zip"
    rm -rf "$file"
    zip -q "$file" "$GAME/${filename}."* -x '*.zip' '*.dzo.*' '*.sha1'
    sha1sum "$file" | awk '{print $1}' | xxd -r -p > "$file.sha1"

    echo "$filename.dzo.zip"
    file="$MAPS_DIR/$filename.dzo.zip"
    rm -rf "$file"
    zip -q "$file" "$GAME/${filename}."* -x '*.zip' '*.sha1'
done

# Build Mega Zip
echo "$(basename $OUT_ZIP)"
cd $BASE_PATH
rm -rf "$OUT_ZIP"
zip -rq "$OUT_ZIP" "$GAME" horizon_cmaps_readme.txt horizon_unix_update_cmaps.sh horizon_windows_update_cmaps.ps1 -x "$GAME/*.zip" "$GAME/*.dzo.*" "$GAME/*.sha1"

# Build Index File
rm -rf $INDEX_PATH
find "$MAPS_DIR" -type f -name "*.version" | sort | while read -r version_file; do
    # Get base name without extension
    base="${version_file%.version}"
    filename=$(basename "$base")
    mapname=$(dd if="$version_file" bs=1 skip=16 count=32 status=none | tr -d '\0' | head -c 32)
    mapversion=$(echo $(dd if="$version_file" bs=1 skip=0 count=4 2>/dev/null | od -An -t u4))

    echo "found $version_file | $mapname | $mapversion"
    echo "$filename|$mapname|$mapversion" >> $INDEX_PATH
done

echo "done"
