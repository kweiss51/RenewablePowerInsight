#!/usr/bin/env python3
"""
Final Blog Image Thumbnail Fix

This script ensures ALL blog post thumbnails display properly when scrolling.
"""

import os
import re

def fix_all_blog_images():
    """Fix all image issues in blog page"""
    
    blog_file = "/Users/kyleweiss/Documents/GitHub/RenewablePowerInsight/blog/index.html"
    
    with open(blog_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fallback SVG for failed images (simple yellow square with sun icon)
    fallback_svg = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI0ZGQjAwMCIvPjx0ZXh0IHg9IjIwMCIgeT0iMTAwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iNDgiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj7imIU8L3RleHQ+PC9zdmc+"
    
    # Pattern to find all img tags in article-image divs
    img_pattern = r'(<div class="article-image">\s*<img[^>]*)(onerror="[^"]*")([^>]*>)'
    
    # Replace all onerror handlers
    def replace_onerror(match):
        before = match.group(1)
        after = match.group(3)
        
        # Add proper onload and onerror handlers
        new_handlers = f'onload="this.style.opacity=\'1\';" onerror="console.log(\'Image failed to load:\', this.src); this.src=\'{fallback_svg}\';" style="opacity: 0; transition: opacity 0.3s ease;"'
        
        return f"{before}{new_handlers}{after}"
    
    content = re.sub(img_pattern, replace_onerror, content)
    
    # Also fix any remaining onerror="this.style.display='none'" patterns
    content = re.sub(
        r'onerror="this\.style\.display=\'none\';[^"]*"',
        f'onerror="console.log(\'Image failed to load:\', this.src); this.src=\'{fallback_svg}\';"',
        content
    )
    
    # Ensure all images have opacity styling
    content = re.sub(
        r'(<img[^>]*src="[^"]*"[^>]*?)(?!.*style=)([^>]*>)',
        r'\1 style="opacity: 0; transition: opacity 0.3s ease;"\2',
        content
    )
    
    with open(blog_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Fixed all blog image thumbnails")

def add_css_fixes():
    """Add final CSS fixes"""
    
    css_file = "/Users/kyleweiss/Documents/GitHub/RenewablePowerInsight/style.css"
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure images are always visible
    if ".article-image img {" in content and "visibility: visible" not in content:
        content = re.sub(
            r'(\.article-image img \{[^}]*)',
            r'\1\n    visibility: visible !important;\n    opacity: 1 !important;',
            content
        )
        
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ Added CSS visibility fixes")

def main():
    print("=" * 60)
    print("FINAL BLOG THUMBNAIL VISIBILITY FIX")
    print("=" * 60)
    
    print("Fixing all blog image thumbnails...")
    fix_all_blog_images()
    
    print("Adding CSS visibility fixes...")
    add_css_fixes()
    
    print("\n" + "=" * 60)
    print("ALL FIXES COMPLETE!")
    print("=" * 60)
    print("✓ All blog post thumbnails should now be visible when scrolling")
    print("✓ Images have fallback handling for failed loads")
    print("✓ CSS ensures maximum visibility")
    print("\nRefresh your browser to see all images!")

if __name__ == "__main__":
    main()
