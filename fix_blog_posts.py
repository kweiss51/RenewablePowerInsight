#!/usr/bin/env python3
"""
Fix individual blog post file navigation paths
"""

import os
import glob

def fix_blog_post_paths():
    """Fix navigation paths in individual blog post files"""
    
    # Find all blog post HTML files in subdirectories
    patterns = [
        'posts/*/*.html',
        'posts/*.html'  # Also check for any files directly in posts/
    ]
    
    for pattern in patterns:
        files = glob.glob(pattern)
        for file_path in files:
            print(f"Checking: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Determine the correct prefix based on file location
                if file_path.count('/') == 2:  # posts/category/file.html
                    prefix = "../../"
                elif file_path.count('/') == 1:  # posts/file.html
                    prefix = "../"
                else:
                    continue
                
                # Fix common incorrect paths
                replacements = [
                    ('href="../style.css"', f'href="{prefix}style.css"'),
                    ('href="../index.html"', f'href="{prefix}index.html"'),
                ]
                
                for old, new in replacements:
                    if old in content:
                        content = content.replace(old, new)
                        print(f"  ✓ Fixed: {old} -> {new}")
                
                # Write back if changes were made
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  → Updated file")
                else:
                    print(f"  → No changes needed")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")

if __name__ == "__main__":
    fix_blog_post_paths()
    print("Done fixing blog post paths!")
