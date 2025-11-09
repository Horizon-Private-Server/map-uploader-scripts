#!/bin/bash

BASE_PATH=/var/www/static/downloads/maps
GAME=uya
MAPS_DIR=$GAME
OUT_NTSC_ZIP=$BASE_PATH/${GAME}_custom_maps_ntsc.zip
OUT_PAL_ZIP=$BASE_PATH/${GAME}_custom_maps_pal.zip
NTSC_INDEX_PATH=$BASE_PATH/index_${GAME}_ntsc.txt
PAL_INDEX_PATH=$BASE_PATH/index_${GAME}_pal.txt

cd $BASE_PATH
rm -rf $OUT_NTSC_ZIP
rm -rf $OUT_PAL_ZIP

# Zip Individual Maps
find "$MAPS_DIR" -type f -name "*.version" | sort | while read -r version_file; do
    # Get base name without extension
    base="${version_file%.version}"
    filename=$(basename "$base")

    # zip ntsc
    if [ -e "$base.wad" ] || [ -e "$base.world" ]; then
        echo "$filename.ntsc.zip"
        files=("$base".*)
        file="$MAPS_DIR/$filename.ntsc.zip"
        rm -rf "$file"
        zip -q "$file" "$GAME/${filename}."* -x '*.zip' '*.pal.*'

	# add to mega
	zip -q "$OUT_NTSC_ZIP" "${files[@]}" -x '*.zip' '*.pal.*'
    fi

    # zip pal
    if [ -e "$base.pal.wad" ] || [ -e "$base.pal.world" ]; then
        echo "$filename.pal.zip"
        files=("$base".pal.*)
        file="$MAPS_DIR/$filename.pal.zip"
        rm -rf "$file"
        zip -q "$file" "$version_file" "$GAME/${filename}.pal."* -x '*.zip'

	# add to mega
	zip -q "$OUT_PAL_ZIP" "$version_file" "${files[@]}" -x '*.zip'
    fi
done

# Add Update Scripts
zip -q "$OUT_NTSC_ZIP" "horizon_cmaps_readme.txt" "horizon_unix_update_cmaps.sh" "horizon_windows_update_cmaps.ps1"
zip -q "$OUT_PAL_ZIP" "horizon_cmaps_readme.txt" "horizon_unix_update_cmaps.sh" "horizon_windows_update_cmaps.ps1"

# Build Index File
rm -rf $NTSC_INDEX_PATH
rm -rf $PAL_INDEX_PATH
find "$MAPS_DIR" -type f -name "*.version" | sort | while read -r version_file; do

    # Get base name without extension
    base="${version_file%.version}"
    filename=$(basename "$base")
    mapname=$(dd if="$version_file" bs=1 skip=16 count=32 status=none | tr -d '\0' | head -c 32)
    mapversion=$(echo $(dd if="$version_file" bs=1 skip=0 count=4 2>/dev/null | od -An -t u4))


    # add to ntsc
    if [ -e "$base.wad" ] || [ -e "$base.world" ]; then
        echo "found ntsc $version_file | $mapname | $mapversion"
        echo "$filename|$mapname|$mapversion" >> $NTSC_INDEX_PATH
    fi

    # add to pal
    if [ -e "$base.pal.wad" ] || [ -e "$base.pal.world" ]; then
        echo "found pal $version_file | $mapname | $mapversion"
        echo "$filename|$mapname|$mapversion" >> $PAL_INDEX_PATH
    fi
done

echo "done"