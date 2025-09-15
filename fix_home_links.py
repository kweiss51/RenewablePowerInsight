#!/usr/bin/env python3
"""
Fix remaining absolute path issues (home page links)
"""

import os
import re
from pathlib import Path

def fix_home_links():
    """Fix home page links to use relative paths"""
    
    base_dir = os.getcwd()
    
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        skip_dirs = {'__pycache__', '.git', 'node_modules', '.vscode', 'ml_models'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"Fixing home page links in {len(html_files)} HTML files...")
    
    files_changed = 0
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Calculate relative path to home
            relative_path = os.path.relpath(html_file, base_dir)
            depth = len(Path(relative_path).parts) - 1  # -1 for the filename
            
            if depth == 0:
                home_path = "index.html"  # Files in root directory
            else:
                home_path = "../" * depth + "index.html"  # Files in subdirectories
            
            # Replace home page links
            # But preserve self-referencing links on index.html
            if os.path.basename(html_file) == 'index.html' and depth == 0:
                # For the main index.html, keep href="/" as is since it refers to itself
                continue
            else:
                # Replace home links for all other files
                content = re.sub(r'href="/"(?![^>]*>)', f'href="{home_path}"', content)
            
            # Also fix the RSS feed link
            if depth == 0:
                feed_path = "feed.xml"
            else:
                feed_path = "../" * depth + "feed.xml"
            
            content = re.sub(r'href="/feed\.xml"', f'href="{feed_path}"', content)
            
            # Write back if changes were made
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Fixed: {os.path.relpath(html_file, base_dir)}")
                files_changed += 1
                
        except Exception as e:
            print(f"✗ Error processing {html_file}: {e}")
    
    print(f"\nDone! Fixed {files_changed} files.")

if __name__ == "__main__":
    fix_home_links()
