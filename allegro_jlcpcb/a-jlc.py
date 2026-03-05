#!/usr/bin/env python3
"""
Simple file renaming script with clear filename mappings.
"""

import os
import sys

# Clear mapping from input filenames to output patterns
# The *project_name* placeholder will be replaced with user input
FILE_MAPPINGS = {
    "BOTTOM.art":   "*project_name*_bottom.BOT",
    "OUTLINE.art":  "*project_name*_outline.FAB",
    "SMBT.art":     "*project_name*_smbt.SMB",
    "SMTP.art":     "*project_name*_smbt.SMT",
    "SPBT.art":     "*project_name*_spbt.SPB",
    "SPTP.art":     "*project_name*_sptp.SPT",
    "SSBT.art":     "*project_name*_ssbt.SSB",
    "SSTP.art":     "*project_name*_sstp.SST",
    "TOP.art":      "*project_name*_top.TOP",
}


def main():
    # Get project name from user
    project_name = input("Enter project name: ").strip()
    if not project_name:
        print("Error: Project name cannot be empty")
        sys.exit(1)

    # Process each file mapping
    renamed_count = 0
    for old_name, new_pattern in FILE_MAPPINGS.items():
        # Replace placeholder with actual project name
        new_name = new_pattern.replace("*project_name*", project_name)

        # Check if source file exists
        if os.path.exists(old_name):
            # Rename the file
            try:
                os.rename(old_name, new_name)
                print(f"✓ Renamed: {old_name} -> {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"✗ Failed to rename {old_name}: {e}")
        else:
            print(f"- Skipped: {old_name} (file not found)")

    # Summary
    print(f"\nRenamed {renamed_count} file(s)")


if __name__ == "__main__":
    main()