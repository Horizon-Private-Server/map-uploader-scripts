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

def check_command(new_dir, latest_dir):
    """Compare new_dir with latest_dir and show differences."""
    new_versions = glob.glob(os.path.join(new_dir, "*.version"))
    latest_versions = glob.glob(os.path.join(latest_dir, "*.version"))
    
    print(f"Checking differences between {new_dir} and {latest_dir}")
    print("=" * 60)
    
    # Compare new maps with latest
    print("NEW vs LATEST comparison:")
    for new_version_path in new_versions:
        version_filename = os.path.basename(new_version_path)
        latest_version_path = os.path.join(latest_dir, version_filename)
        
        new_version = get_version_byte(new_version_path)
        latest_version = get_version_byte(latest_version_path)
        
        if os.path.exists(latest_version_path):
            if new_version != latest_version:
                print(f"  {version_filename}: NEW={new_version}, LATEST={latest_version}")
            else:
                print(f"  {version_filename}: Same version ({new_version})")
        else:
            print(f"  {version_filename}: NEW FILE (version={new_version})")
    
    # List all maps in latest_dir
    print(f"\nAll maps in {latest_dir}:")
    if latest_versions:
        for latest_version_path in sorted(latest_versions):
            version_filename = os.path.basename(latest_version_path)
            latest_version = get_version_byte(latest_version_path)
            print(f"  {version_filename}: version {latest_version}")
    else:
        print("  (No maps found)")

def update_command(new_dir, latest_dir):
    """Update version files and copy all files from new_dir to latest_dir."""
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
        with open(new_version_path, "rb+") as f:
            f.seek(0)
            f.write(bytes([new_version]))
        
        print(f"Updated {version_filename}: version {latest_version} → {new_version}")
    
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

