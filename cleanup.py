#!/usr/bin/env python3
"""
Cleanup Script for GenerativeAI Project

This script removes all generated files (sessions and artifacts) while preserving
the folder structure with .gitkeep files.

Usage:
    python cleanup.py [--dry-run] [--sessions] [--artifacts] [--all]

Options:
    --dry-run     Show what would be deleted without actually deleting
    --sessions    Delete only session files
    --artifacts   Delete only generated artifacts (CFG/DFG images)
    --all         Delete both sessions and artifacts (default)
"""

import os
import sys
import glob
from pathlib import Path


def delete_files(pattern: str, description: str, dry_run: bool = False) -> int:
    """
    Delete files matching the given pattern.
    
    Args:
        pattern: Glob pattern to match files
        description: Description for logging
        dry_run: If True, only show what would be deleted
        
    Returns:
        Number of files deleted (or would be deleted)
    """
    files = glob.glob(pattern, recursive=True)
    
    # Filter out .gitkeep files
    files = [f for f in files if not f.endswith('.gitkeep')]
    
    if not files:
        print(f"✅ No {description} to delete")
        return 0
    
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Found {len(files)} {description}:")
    
    deleted_count = 0
    for file_path in files:
        file_size = os.path.getsize(file_path)
        size_str = f"{file_size / 1024:.1f}KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f}MB"
        
        print(f"  {'[WOULD DELETE]' if dry_run else '[DELETING]'} {file_path} ({size_str})")
        
        if not dry_run:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"    ❌ Error: {e}")
    
    if dry_run:
        print(f"{'[DRY RUN] ' if dry_run else ''}Would delete {len(files)} {description}")
    else:
        print(f"✅ Deleted {deleted_count} {description}")
    
    return deleted_count


def cleanup_sessions(dry_run: bool = False) -> int:
    """Delete all session JSON files."""
    return delete_files(
        "sessions/*.json",
        "session files",
        dry_run
    )


def cleanup_artifacts(dry_run: bool = False) -> int:
    """Delete all generated CFG and DFG images."""
    cfg_count = delete_files(
        "generated_artifacts/cfg/*.png",
        "CFG images",
        dry_run
    )
    
    dfg_count = delete_files(
        "generated_artifacts/dfg/*.png",
        "DFG images",
        dry_run
    )
    
    return cfg_count + dfg_count


def main():
    """Main cleanup function."""
    # Parse command line arguments
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    sessions_only = "--sessions" in args
    artifacts_only = "--artifacts" in args
    clean_all = "--all" in args or not (sessions_only or artifacts_only)
    
    # Show help
    if "--help" in args or "-h" in args:
        print(__doc__)
        return
    
    print("=" * 70)
    print("🧹 GenerativeAI Project Cleanup")
    print("=" * 70)
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be actually deleted")
    
    total_deleted = 0
    
    # Cleanup sessions
    if clean_all or sessions_only:
        print("\n📁 Cleaning up session files...")
        total_deleted += cleanup_sessions(dry_run)
    
    # Cleanup artifacts
    if clean_all or artifacts_only:
        print("\n🖼️  Cleaning up generated artifacts...")
        total_deleted += cleanup_artifacts(dry_run)
    
    # Summary
    print("\n" + "=" * 70)
    if dry_run:
        print(f"✨ [DRY RUN] Would delete {total_deleted} files total")
        print("\nRun without --dry-run to actually delete the files:")
        print("  python cleanup.py")
    else:
        print(f"✨ Cleanup complete! Deleted {total_deleted} files total")
        print("\n✅ Folder structure preserved with .gitkeep files")
    print("=" * 70)


if __name__ == "__main__":
    try:
        # Change to script directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
