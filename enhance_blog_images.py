#!/usr/bin/env python3
"""
Enhanced Blog Image Visibility Fixer

This script ensures all blog post thumbnails are properly visible and loading correctly.
"""

import os
import re

def add_image_visibility_css():
    """Add CSS to ensure images are always visible"""
    
    css_file = "/Users/kyleweiss/Documents/GitHub/RenewablePowerInsight/style.css"
    
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if our enhanced image CSS is already present
    if "/* Enhanced Image Visibility */" in content:
        print("Enhanced image CSS already present")
        return
    
    # Add enhanced image CSS
    enhanced_css = '''
/* Enhanced Image Visibility */
.article-image {
    background: var(--gray-50);
    border: 1px solid var(--gray-100);
}

.article-image img {
    display: block !important;
    max-width: 100%;
    height: 100%;
    object-fit: cover;
    background: var(--gray-100);
}

/* Ensure SVG images render properly */
.article-image img[src$=".svg"] {
    width: 100% !important;
    height: 100% !important;
}

/* Loading state for images */
.article-image::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 40px;
    height: 40px;
    border: 3px solid var(--gray-200);
    border-top: 3px solid var(--primary-green);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    z-index: 1;
}

.article-image img:not([src=""]) + .article-image::before {
    display: none;
}

@keyframes spin {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}
'''
    
    # Insert the CSS before the media queries
    media_query_pos = content.find("/* ===== MEDIA QUERIES =====")
    if media_query_pos != -1:
        content = content[:media_query_pos] + enhanced_css + "\n" + content[media_query_pos:]
        
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ Added enhanced image visibility CSS")
    else:
        print("❌ Could not find insertion point for CSS")

def add_image_loading_script():
    """Add JavaScript to ensure images load properly"""
    
    blog_file = "/Users/kyleweiss/Documents/GitHub/RenewablePowerInsight/blog/index.html"
    
    with open(blog_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if script is already present
    if "imageLoadingScript" in content:
        print("Image loading script already present")
        return
    
    # Add script before closing body tag
    script = '''
<script id="imageLoadingScript">
document.addEventListener('DOMContentLoaded', function() {
    // Force reload any failed images
    const images = document.querySelectorAll('.article-image img');
    
    images.forEach(function(img) {
        // Add load event handler
        img.addEventListener('load', function() {
            console.log('Image loaded successfully:', this.src);
            this.style.opacity = '1';
        });
        
        // Add error handler  
        img.addEventListener('error', function() {
            console.log('Image failed to load, retrying:', this.src);
            // Try reloading the image once
            const originalSrc = this.src;
            this.src = '';
            setTimeout(() => {
                this.src = originalSrc;
            }, 100);
        });
        
        // Ensure image is visible
        img.style.display = 'block';
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease';
        
        // Force reload if src is already set but not visible
        if (img.complete && img.naturalWidth === 0) {
            const src = img.src;
            img.src = '';
            img.src = src;
        } else if (img.complete) {
            img.style.opacity = '1';
        }
    });
    
    // Log image status
    console.log(`Blog page loaded with ${images.length} images`);
});
</script>

'''
    
    # Insert before closing body tag
    body_end = content.rfind('</body>')
    if body_end != -1:
        content = content[:body_end] + script + content[body_end:]
        
        with open(blog_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ Added image loading JavaScript")
    else:
        print("❌ Could not find closing body tag")

def main():
    print("=" * 60)
    print("ENHANCED BLOG IMAGE VISIBILITY FIXER")
    print("=" * 60)
    
    # Add enhanced CSS
    print("Adding enhanced image visibility CSS...")
    add_image_visibility_css()
    
    # Add loading script
    print("Adding image loading JavaScript...")
    add_image_loading_script()
    
    print("\n" + "=" * 60)
    print("ENHANCEMENTS COMPLETE!")
    print("=" * 60)
    print("✓ Enhanced CSS for better image visibility")
    print("✓ Added JavaScript for reliable image loading")
    print("✓ Images should now be clearly visible when scrolling")
    print("\nRefresh your browser to see the improvements!")

if __name__ == "__main__":
    main()
