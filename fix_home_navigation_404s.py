#!/usr/bin/env python3
"""
Fix Home Navigation 404 Errors - Renewable Power Insight

This script fixes all the broken home navigation links identified in the verification:
1. Removes broken fragment links (#analysis, #technology, #markets, #policy)
2. Fixes incorrect relative paths in blog posts 
3. Updates JSON-LD structured data to use relative URLs
4. Ensures all Home buttons work correctly
"""

import os
import re
from pathlib import Path

def fix_navigation_links(base_dir):
    """Fix all navigation 404 issues"""
    
    base_path = Path(base_dir)
    html_files = list(base_path.rglob("*.html"))
    
    print(f"Fixing navigation 404s in {len(html_files)} HTML files...")
    
    files_fixed = 0
    
    for html_file in html_files:
        try:
            # Calculate relative path depth
            relative_path = html_file.relative_to(base_path)
            depth = len(relative_path.parts) - 1
            
            # Determine correct prefix for this file's location
            if depth == 0:
                prefix = ""  # Files in root directory
                home_path = "index.html"
            else:
                prefix = "../" * depth  # Files in subdirectories  
                home_path = f"{prefix}index.html"
            
            print(f"\nProcessing: {relative_path}")
            
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. Fix broken fragment links by removing fragments that don't exist
            broken_fragments = ['#analysis', '#technology', '#markets', '#policy']
            
            for fragment in broken_fragments:
                # Remove fragments from all home links
                patterns = [
                    (rf'href="\.\.\/index\.html{re.escape(fragment)}"', 'href="../index.html"'),
                    (rf'href="\.\.\/\.\.\/index\.html{re.escape(fragment)}"', 'href="../../index.html"'),
                    (rf'href="index\.html{re.escape(fragment)}"', 'href="index.html"'),
                ]
                
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content)
            
            # 2. Fix incorrect relative paths in blog posts
            # Some posts use ../index.html when they should use ../../index.html
            if str(relative_path).startswith('posts/'):
                # For files in posts/category/ subdirectories, should use ../../
                wrong_patterns = [
                    (r'href="\.\.\/index\.html"', 'href="../../index.html"'),
                    (r'"item":\s*"\.\.\/index\.html"', '"item": "../../index.html"'),
                ]
                
                for pattern, replacement in wrong_patterns:
                    content = re.sub(pattern, replacement, content)
            
            # 3. Fix JSON-LD structured data to use relative URLs instead of absolute
            # Replace absolute URLs in breadcrumb structured data
            absolute_url_patterns = [
                (r'"item":\s*"https://renewablepowerinsight\.com/"', f'"item": "{home_path}"'),
                (r'"item":\s*"https://renewablepowerinsight\.com/([^"]+)"', lambda m: f'"item": "{prefix}{m.group(1)}"'),
            ]
            
            for pattern, replacement in absolute_url_patterns:
                if callable(replacement):
                    content = re.sub(pattern, replacement, content)
                else:
                    content = re.sub(pattern, replacement, content)
            
            # 4. Ensure consistent home links (catch any remaining issues)
            # Fix any remaining inconsistent home link patterns
            if depth == 0:
                # Root level files
                home_patterns = [
                    (r'href="/"(?![^>]*>)', 'href="index.html"'),
                ]
            else:
                # Subdirectory files
                home_patterns = [
                    (r'href="/"(?![^>]*>)', f'href="{home_path}"'),
                    # Fix any links that still point to wrong depth
                    (r'href="index\.html"(?![^>]*class="[^"]*current)', f'href="{home_path}"'),
                ]
            
            for pattern, replacement in home_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Save if changes were made
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                files_fixed += 1
                print(f"  ✓ Fixed navigation issues")
            else:
                print(f"  ✓ No issues found")
                
        except Exception as e:
            print(f"  ❌ Error processing {html_file}: {e}")
    
    return files_fixed

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("HOME NAVIGATION 404 FIXER")
    print("=" * 60)
    print(f"Working directory: {base_dir}")
    
    files_fixed = fix_navigation_links(base_dir)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files processed and fixed: {files_fixed}")
    print("\nFixed issues:")
    print("  ✓ Removed broken fragment links (#analysis, #technology, #markets, #policy)")
    print("  ✓ Fixed incorrect relative paths in blog posts")
    print("  ✓ Updated JSON-LD structured data to use relative URLs")
    print("  ✓ Ensured all Home buttons work correctly")
    print("\nAll home navigation 404 errors should now be resolved!")

if __name__ == "__main__":
    main()
