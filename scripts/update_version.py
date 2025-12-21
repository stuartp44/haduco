#!/usr/bin/env python3
"""Update version in manifest.json for semantic-release."""
import json
import sys
from pathlib import Path


def update_version(new_version: str) -> None:
    """Update the version in manifest.json."""
    manifest_path = Path(__file__).parent.parent / "custom_components" / "duco_ventilation_sun_control" / "manifest.json"
    
    if not manifest_path.exists():
        print(f"Error: manifest.json not found at {manifest_path}")
        sys.exit(1)
    
    # Read current manifest
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # Update version
    old_version = manifest.get("version", "unknown")
    manifest["version"] = new_version
    
    # Write updated manifest
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")  # Add newline at end of file
    
    print(f"Updated version from {old_version} to {new_version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: update_version.py <version>")
        sys.exit(1)
    
    update_version(sys.argv[1])
