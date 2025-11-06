#!/usr/bin/env python3
"""
Script to add reference_path field to dataset JSON entries.

Usage:
    python add_reference_paths.py <path_to_json_file>

Example:
    python add_reference_paths.py /path/to/dataset.json
"""

import json
import sys
import os
from pathlib import Path


def add_reference_paths(json_file_path):
    """
    Add reference_path field to each entry in the JSON file.
    
    Args:
        json_file_path: Path to the JSON file to process
    """
    # Read the JSON file
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file: {e}")
        sys.exit(1)
    
    # Validate that data is a list
    if not isinstance(data, list):
        print("Error: JSON file must contain an array of entries.")
        sys.exit(1)
    
    # Process each entry
    entries_modified = 0
    for entry in data:
        if not isinstance(entry, dict):
            print(f"Warning: Skipping non-dictionary entry: {entry}")
            continue
        
        if 'media_path' not in entry:
            print(f"Warning: Entry missing 'media_path' field: {entry}")
            continue
        
        # Extract filename from media_path
        media_path = entry['media_path']
        filename = os.path.basename(media_path)
        
        # Add reference_path field
        entry['reference_path'] = f"reference_videos/{filename}"
        entries_modified += 1
    
    # Write back to the JSON file
    try:
        with open(json_file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Successfully updated {entries_modified} entries in '{json_file_path}'")
        print(f"✓ Added 'reference_path' field to all entries")
    except Exception as e:
        print(f"Error: Failed to write to file: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python add_reference_paths.py <path_to_json_file>")
        print("\nExample:")
        print("  python add_reference_paths.py /path/to/dataset.json")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    # Confirm before proceeding
    print(f"This will modify the file: {json_file_path}")
    print("The script will add 'reference_path' field to each entry.")
    print("\nProcessing...")
    
    add_reference_paths(json_file_path)


if __name__ == "__main__":
    main()


