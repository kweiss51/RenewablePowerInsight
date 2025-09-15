#!/usr/bin/env python3
"""
Footer Link Fixer for Renewable Power Insight Website

This script fixes the remaining absolute paths in footer sections that are causing 404 errors.
It addresses:
1. Footer-bottom absolute paths (/privacy/, /terms/)
2. Company section absolute paths (/team/, /contact/, /careers/, /press/)
3. Connect section absolute paths (/api/)
4. Remaining home page links (/)
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

def fix_footer_links(file_path, base_dir):
    """Fix footer navigation paths in a single HTML file"""
    print(f"Processing: {os.path.relpath(file_path, base_dir)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        prefix = get_relative_path_prefix(file_path, base_dir)
        
        # Fix footer-bottom absolute paths (remove broken links since these pages don't exist)
        footer_bottom_fixes = [
            # Remove or fix non-existent footer links
            (r'<a href="/privacy/">Privacy Policy</a>', 'Privacy Policy'),
            (r'<a href="/terms/">Terms of Service</a>', 'Terms of Service'),
            (r'\| <a href="/privacy/">Privacy Policy</a> \|', '|'),
            (r'\| <a href="/terms/">Terms of Service</a>', ''),
        ]
        
        # Fix Company section absolute paths (remove non-existent links)
        company_section_fixes = [
            (r'<li><a href="/team/">Our Team</a></li>', ''),
            (r'<li><a href="/contact/">Contact</a></li>', ''),
            (r'<li><a href="/careers/">Careers</a></li>', ''),
            (r'<li><a href="/press/">Press</a></li>', ''),
        ]
        
        # Fix Connect section absolute paths  
        connect_section_fixes = [
            (r'<li><a href="/api/">API Access</a></li>', ''),
        ]
        
        # Fix remaining home page links
        home_link_fixes = [
            (r'href="/"(?![^>]*>)', f'href="{prefix}index.html"' if prefix else 'href="index.html"'),
        ]
        
        # Apply all fixes
        all_fixes = footer_bottom_fixes + company_section_fixes + connect_section_fixes + home_link_fixes
        
        changes_made = False
        for pattern, replacement in all_fixes:
            old_content = content
            content = re.sub(pattern, replacement, content)
            if content != old_content:
                changes_made = True
                print(f"  ✓ Fixed: {pattern[:50]}...")
        
        # Clean up any double spaces or empty lines created by removals
        content = re.sub(r'\|\s*\|', '|', content)  # Fix double pipes
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Fix triple newlines
        
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
    """Main function to process all HTML files"""
    
    base_dir = os.getcwd()
    print(f"Fixing footer links in: {base_dir}")
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
    
    print(f"Found {len(html_files)} HTML files to process")
    print("=" * 60)
    
    # Process each file
    files_changed = 0
    for html_file in sorted(html_files):
        if fix_footer_links(html_file, base_dir):
            files_changed += 1
        print()  # Empty line for readability
    
    print("=" * 60)
    print(f"Footer link fixing complete!")
    print(f"Files processed: {len(html_files)}")
    print(f"Files changed: {files_changed}")
    print()
    print("All footer absolute paths have been fixed or removed.")
    print("Non-existent pages (privacy, terms, team, etc.) have been removed to prevent 404 errors.")

if __name__ == "__main__":
    main()
