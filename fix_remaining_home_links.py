#!/usr/bin/env python3
"""
Final Home Link Fixer for Renewable Power Insight Website

This script fixes remaining "/" home page links throughout the site.
"""

import os
import re
from pathlib import Path

def get_relative_path_prefix(file_path, base_dir):
    """Calculate the correct relative path prefix based on file depth"""
    relative_path = os.path.relpath(file_path, base_dir)
    depth = len(Path(relative_path).parts) - 1  # -1 for filename
    
    if depth == 0:
        return ""  # Files in root directory  
    else:
        return "../" * depth  # Files in subdirectories

def fix_home_links_comprehensive(file_path, base_dir):
    """Fix all remaining home page links"""
    print(f"Processing: {os.path.relpath(file_path, base_dir)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        prefix = get_relative_path_prefix(file_path, base_dir)
        
        # Determine correct home path
        if prefix:
            home_path = f"{prefix}index.html"
        else:
            home_path = "index.html"
        
        # Skip the main index.html file to avoid self-referencing issues
        filename = os.path.basename(file_path)
        if filename == 'index.html' and prefix == "":
            print(f"  → Skipping main index.html")
            return False
        
        # Fix all variations of home links
        home_patterns = [
            # Standard home links in navigation
            (r'<a\s+([^>]*\s+)?href="/"(\s[^>]*)?>([^<]*)</a>', f'<a \\1href="{home_path}"\\2>\\3</a>'),
            (r'<a\s+href="/"(\s[^>]*)?>([^<]*)</a>', f'<a href="{home_path}"\\1>\\2</a>'),
            
            # Simple href="/" patterns
            (r'href="/"(?=\s|>)', f'href="{home_path}"'),
            
            # Breadcrumb home links  
            (r'"item":\s*"/"', f'"item": "{home_path}"'),
            
            # Return to homepage links
            (r'<a\s+href="/"([^>]*)>Return to Homepage</a>', f'<a href="{home_path}"\\1>Return to Homepage</a>'),
        ]
        
        changes_made = False
        for pattern, replacement in home_patterns:
            old_content = content
            content = re.sub(pattern, replacement, content)
            if content != old_content:
                changes_made = True
                print(f"  ✓ Fixed home link pattern")
        
        # Write back if changes were made
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  → Updated file")
            return True
        else:
            print(f"  → No changes needed")
            return False
            
    except Exception as e:
        print(f"  ✗ Error processing file: {e}")
        return False

def main():
    """Main function"""
    
    base_dir = os.getcwd()
    print(f"Fixing remaining home links in: {base_dir}")
    print("=" * 60)
    
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        skip_dirs = {'__pycache__', '.git', 'node_modules', '.vscode', 'ml_models'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"Found {len(html_files)} HTML files")
    print("=" * 60)
    
    files_changed = 0
    for html_file in sorted(html_files):
        if fix_home_links_comprehensive(html_file, base_dir):
            files_changed += 1
        print()
    
    print("=" * 60)
    print(f"Home link fixing complete!")
    print(f"Files changed: {files_changed}")

if __name__ == "__main__":
    main()
