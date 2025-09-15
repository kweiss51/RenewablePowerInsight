#!/usr/bin/env python3
"""
Navigation Link Verification Script

This script verifies that all navigation links across the website now use relative paths
and tests that the target files exist to prevent 404 errors.
"""

import os
import re
from pathlib import Path

def find_links_in_html(content):
    """
    Extract all href links from HTML content using regex
    
    Args:
        content: HTML content as string
    
    Returns:
        List of href values
    """
    # Pattern to match href attributes
    pattern = r'href\s*=\s*["\']([^"\']*)["\']'
    matches = re.findall(pattern, content, re.IGNORECASE)
    return matches

def verify_navigation_links(base_dir):
    """
    Verify all navigation links in HTML files
    
    Args:
        base_dir: Base directory of the website
    """
    print(f"Verifying navigation links in: {base_dir}")
    print("=" * 60)
    
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(base_dir):
        # Skip certain directories
        skip_dirs = {'__pycache__', '.git', 'node_modules', '.vscode', 'ml_models'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"Found {len(html_files)} HTML files to verify")
    print("=" * 60)
    
    total_links = 0
    broken_links = 0
    fixed_links = 0
    absolute_paths = 0
    
    for html_file in sorted(html_files):
        print(f"\nChecking: {os.path.relpath(html_file, base_dir)}")
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all links
            links = find_links_in_html(content)
            file_dir = os.path.dirname(html_file)
            
            for href in links:
                total_links += 1
                
                # Skip external links, email links, and anchors
                if (href.startswith('http') or 
                    href.startswith('mailto:') or 
                    href.startswith('#') or
                    href.startswith('tel:')):
                    continue
                
                # Check if it's an absolute path (which we want to avoid)
                if href.startswith('/'):
                    print(f"  ⚠️  Still has absolute path: {href}")
                    absolute_paths += 1
                    continue
                
                # For relative paths, check if target exists
                if not href.startswith('http'):
                    # Resolve relative path
                    target_path = os.path.normpath(os.path.join(file_dir, href))
                    
                    if os.path.exists(target_path):
                        fixed_links += 1
                        print(f"  ✓ Valid link: {href}")
                    else:
                        print(f"  ✗ Broken link: {href} -> {target_path}")
                        broken_links += 1
                        
                        # Suggest fix if it's a common pattern
                        if '/index.html' not in href and not href.endswith('.html'):
                            suggested = href.rstrip('/') + '/index.html'
                            suggested_path = os.path.normpath(os.path.join(file_dir, suggested))
                            if os.path.exists(suggested_path):
                                print(f"    💡 Suggestion: {suggested}")
        
        except Exception as e:
            print(f"  ✗ Error processing file: {e}")
            broken_links += 1
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total HTML files: {len(html_files)}")
    print(f"Total links checked: {total_links}")
    print(f"✓ Working relative links: {fixed_links}")
    print(f"⚠️  Remaining absolute paths: {absolute_paths}")
    print(f"✗ Broken links: {broken_links}")
    
    if total_links > 0:
        success_rate = (fixed_links / total_links) * 100
        print(f"Success rate: {success_rate:.1f}%")
    
    if absolute_paths == 0 and broken_links == 0:
        print("\n🎉 All navigation links are working correctly!")
        print("The 404 error issue should now be resolved.")
    elif absolute_paths > 0:
        print(f"\n⚠️  Found {absolute_paths} absolute paths that may cause 404 errors.")
        print("These should be converted to relative paths.")
    else:
        print(f"\n⚠️  Found {broken_links} broken links that need attention.")

def main():
    """Main function"""
    base_dir = os.getcwd()
    verify_navigation_links(base_dir)

if __name__ == "__main__":
    main()
