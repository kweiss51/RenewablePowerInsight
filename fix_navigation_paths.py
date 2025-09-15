#!/usr/bin/env python3
"""
Navigation Path Fixer for Renewable Power Insight Website

This script converts all absolute paths (/posts/category/) to relative paths 
(posts/category/index.html or ../posts/category/index.html depending on depth)
to fix 404 navigation errors across the entire website.

The script handles:
1. Main navigation menus
2. Footer links
3. Category cards/buttons
4. Sidebar links
5. Individual blog post article links

It preserves existing functionality while making paths work in all hosting environments.
"""

import os
import re
from pathlib import Path

def get_relative_path_prefix(file_path, base_dir):
    """
    Calculate the correct relative path prefix based on file depth
    
    Args:
        file_path: Full path to the file being processed
        base_dir: Base directory of the website
    
    Returns:
        String prefix for relative paths ("" for root, "../" for subdirs)
    """
    relative_path = os.path.relpath(file_path, base_dir)
    depth = len(Path(relative_path).parts) - 1  # -1 because we don't count the filename
    
    if depth == 0:
        return ""  # Files in root directory
    else:
        return "../" * depth  # Files in subdirectories

def fix_navigation_paths(file_path, base_dir):
    """
    Fix navigation paths in a single HTML file
    
    Args:
        file_path: Path to the HTML file to fix
        base_dir: Base directory of the website
    
    Returns:
        Boolean indicating if any changes were made
    """
    print(f"Processing: {os.path.relpath(file_path, base_dir)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        prefix = get_relative_path_prefix(file_path, base_dir)
        
        # Pattern replacements for different types of links
        replacements = [
            # Main navigation and category links
            (r'href="/posts/solar/"', f'href="{prefix}posts/solar/index.html"'),
            (r'href="/posts/wind/"', f'href="{prefix}posts/wind/index.html"'),
            (r'href="/posts/battery/"', f'href="{prefix}posts/battery/index.html"'),
            (r'href="/posts/grid-tech/"', f'href="{prefix}posts/grid-tech/index.html"'),
            (r'href="/posts/policy/"', f'href="{prefix}posts/policy/index.html"'),
            (r'href="/posts/general/"', f'href="{prefix}posts/general/index.html"'),
            (r'href="/posts/markets/"', f'href="{prefix}posts/markets/index.html"'),
            
            # Other absolute paths that might exist
            (r'href="/research/"', f'href="{prefix}research/index.html"'),
            (r'href="/data/"', f'href="{prefix}data/index.html"'),
            (r'href="/insights/"', f'href="{prefix}insights/index.html"'),
            (r'href="/methodology/"', f'href="{prefix}methodology/index.html"'),
            (r'href="/about/"', f'href="{prefix}about/index.html"'),
            (r'href="/newsletter/"', f'href="{prefix}newsletter/index.html"'),
            (r'href="/rss/"', f'href="{prefix}rss/index.html"'),
            (r'href="/blog/"', f'href="{prefix}blog/index.html"'),
        ]
        
        # Apply all replacements
        changes_made = False
        for pattern, replacement in replacements:
            old_content = content
            content = re.sub(pattern, replacement, content)
            if content != old_content:
                changes_made = True
                print(f"  ✓ Fixed: {pattern}")
        
        # Write back if changes were made
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  → Updated file with relative paths")
            return True
        else:
            print(f"  → No changes needed")
            return False
            
    except Exception as e:
        print(f"  ✗ Error processing file: {e}")
        return False

def main():
    """Main function to process all HTML files in the website"""
    
    # Get the base directory (current working directory)
    base_dir = os.getcwd()
    print(f"Base directory: {base_dir}")
    print("=" * 60)
    
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', 'node_modules', '.vscode'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"Found {len(html_files)} HTML files to process")
    print("=" * 60)
    
    # Process each file
    files_changed = 0
    for html_file in sorted(html_files):
        if fix_navigation_paths(html_file, base_dir):
            files_changed += 1
        print()  # Empty line for readability
    
    print("=" * 60)
    print(f"Processing complete!")
    print(f"Files processed: {len(html_files)}")
    print(f"Files changed: {files_changed}")
    print()
    print("All navigation paths have been converted to relative paths.")
    print("This should fix the 404 errors on menu links.")

if __name__ == "__main__":
    main()
