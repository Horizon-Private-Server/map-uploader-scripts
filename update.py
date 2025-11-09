#!/usr/bin/env python3
import os
import glob
import argparse
import shutil

def increment_first_byte(path):
    with open(path, "rb+") as f:
        # read first byte
        first = f.read(1)
        if not first:
            return  # skip empty files
        value = first[0]
        # increment with wraparound
        new_value = (value + 1) % 256
        # move back to start and overwrite
        f.seek(0)
        f.write(bytes([new_value]))

def get_version_byte(path):
    """Get the first byte value from a version file."""
    try:
        with open(path, "rb") as f:
            first = f.read(1)
            if not first:
                return 0
            return first[0]
    except FileNotFoundError:
        return 0

def normalize_new_dir_filenames(new_dir: str, latest_dir: str) -> None:
    """
    Pre-step to align filenames in new_dir with latest_dir.

    For every file in new_dir, if replacing underscores with spaces yields a name
    that exists in latest_dir (case-insensitive match), rename the file in
    new_dir to that exact name (including the latest_dir's casing). This helps
    ensure version checks and updates target the correct files.
    """
    try:
        latest_names = {name.lower(): name for name in os.listdir(latest_dir)}
    except FileNotFoundError:
        # If latest_dir doesn't exist yet, nothing to normalize
        return

    try:
        new_names = list(os.listdir(new_dir))
    except FileNotFoundError:
        return

    for name in new_names:
        # Only consider files (skip directories) and names with underscores
        src_path = os.path.join(new_dir, name)
        if not os.path.isfile(src_path):
            continue

        if "_" not in name:
            continue

        candidate = name.replace("_", " ")
        target_actual = latest_names.get(candidate.lower())
        if not target_actual:
            # No match in latest_dir after underscore->space conversion
            continue

        dst_path = os.path.join(new_dir, target_actual)
        if src_path == dst_path:
            # Already correct
            continue

        if os.path.exists(dst_path):
            # Avoid overwriting an existing file in new_dir
            print(f"Skip rename (target exists): {name} -> {target_actual}")
            continue

        try:
            os.rename(src_path, dst_path)
            print(f"Renamed to match latest: {name} -> {target_actual}")
        except OSError as e:
            print(f"Failed to rename {name} -> {target_actual}: {e}")

def check_command(new_dir, latest_dir):
    """Compare new_dir with latest_dir and show differences."""
    # Normalize filenames in new_dir to match latest_dir naming
    normalize_new_dir_filenames(new_dir, latest_dir)
    new_versions = glob.glob(os.path.join(new_dir, "*.version"))
    
    print(f"Checking differences between {new_dir} and {latest_dir}")
    print("=" * 60)
    
    for new_version_path in new_versions:
        version_filename = os.path.basename(new_version_path)
        latest_version_path = os.path.join(latest_dir, version_filename)
        
        new_version = get_version_byte(new_version_path)
        latest_version = get_version_byte(latest_version_path)
        
        if os.path.exists(latest_version_path):
            if new_version != latest_version:
                print(f"{version_filename}: NEW={new_version}, CURRENT={latest_version}")
            else:
                print(f"{version_filename}: Same version ({new_version})")
        else:
            print(f"{version_filename}: NEW FILE (version={new_version})")

def update_command(new_dir, latest_dir):
    """Update version files and copy all files from new_dir to latest_dir."""
    # Normalize filenames in new_dir to match latest_dir naming
    normalize_new_dir_filenames(new_dir, latest_dir)
    new_versions = glob.glob(os.path.join(new_dir, "*.version"))
    
    print(f"Updating maps from {new_dir} to {latest_dir}")
    print("=" * 60)
    
    # First, update version files
    for new_version_path in new_versions:
        version_filename = os.path.basename(new_version_path)
        latest_version_path = os.path.join(latest_dir, version_filename)
        
        latest_version = get_version_byte(latest_version_path)
        new_version = (latest_version + 1) % 256

        # Update the version file
        # with open(new_version_path, "rb+") as f:
        #     f.seek(0)
            # Intentionally disabled actual write of incremented version per request
            # f.write(bytes([new_version]))

        #print(f"Updated {version_filename}: version {latest_version} → {new_version} (write disabled)")
    
    # Then copy all files from new_dir to latest_dir
    print("\nCopying files...")
    all_files = glob.glob(os.path.join(new_dir, "*"))
    
    # Ensure latest_dir exists
    os.makedirs(latest_dir, exist_ok=True)
    
    for file_path in all_files:
        if os.path.isfile(file_path):
            filename = os.path.basename(file_path)
            dest_path = os.path.join(latest_dir, filename)
            shutil.copy2(file_path, dest_path)
            print(f"Copied {filename}")

def main():
    parser = argparse.ArgumentParser(description="Map uploader utility for managing map versions")
    parser.add_argument("new_dir", help="Temporary folder of new maps to update")
    parser.add_argument("latest_dir", help="Map directory of currently available maps")
    parser.add_argument("command", choices=["check", "update"], 
                       help="Command to run: 'check' compares directories, 'update' increments versions and copies files")
    
    args = parser.parse_args()
    
    # Validate directories
    if not os.path.exists(args.new_dir):
        print(f"Error: new_dir '{args.new_dir}' does not exist")
        return 1
    
    if args.command == "check":
        check_command(args.new_dir, args.latest_dir)
    elif args.command == "update":
        update_command(args.new_dir, args.latest_dir)
    
    return 0

if __name__ == "__main__":
    main()
