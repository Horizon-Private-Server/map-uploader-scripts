#!/bin/sh

FILE="/var/www/static/downloads/maps/dl/version"
OFFSET=0  # byte offset where the 32-bit int is stored

# --- Read 4 bytes and convert to decimal (little-endian) ---
val=$(dd if="$FILE" bs=1 skip=$OFFSET count=4 2>/dev/null | od -An -t u4)
val=$(echo $val)  # trim spaces

# --- Add 1 ---
newval=$((val + 1))
echo "$val => $newval"

# --- Prompt user ---
read -p "Confirm write? (y/n): " confirm
if [ "$confirm" = "y" ]; then
    # Convert decimal back to 4-byte little-endian hex
    hex=$(printf "%08x" $newval)
    # Break hex into bytes in little-endian order
    bytes=$(echo $hex | sed 's/../\\x&/g' | awk '{print substr($0,7,4) substr($0,3,4)}')

    # Write the new 4 bytes
    printf "0: %.8x" $newval | sed -E 's/0: (..)(..)(..)(..)/0: \4\3\2\1/' | xxd -r -g0 > $FILE

    # --- Read 4 bytes and convert to decimal (little-endian) ---
    val=$(dd if="$FILE" bs=1 skip=$OFFSET count=4 2>/dev/null | od -An -t u4)
    val=$(echo $val)  # trim spaces
    echo "Done $val"
else
    echo "Aborted."
fi
