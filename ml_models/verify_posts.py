#!/usr/bin/env python3

import os
import re
from pathlib import Path

def count_links_and_images(file_path):
    """Count links and images using the same method as validation"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count images
    image_count = len(re.findall(r'<img[^>]+>', content))
    
    # Count external links (http/https links)
    external_link_count = len(re.findall(r'href="https?://[^"]*"', content))
    
    return image_count, external_link_count

def verify_all_posts():
    """Verify all posts in the posts directory and its category subfolders"""
    posts_dir = Path("../posts")
    
    print("=== ACCURATE POST VERIFICATION ===")
    
    all_valid = True
    total_posts = 0
    
    # Check both root directory and category subdirectories
    for category_folder in ["solar", "wind", "battery", "grid-tech", "markets", "policy", "general"]:
        category_path = posts_dir / category_folder
        if category_path.exists():
            html_files = list(category_path.glob("*.html"))
            if html_files:
                print(f"\n📁 {category_folder.upper()} Category:")
                for html_file in html_files:
                    images, links = count_links_and_images(html_file)
                    
                    is_valid = images >= 1 and 3 <= links <= 5
                    if not is_valid:
                        all_valid = False
                    
                    status = "✅ VALID" if is_valid else "❌ INVALID"
                    print(f"  {status} - {html_file.name} - Images: {images}, Links: {links}")
                    total_posts += 1
    
    # Also check root directory for any remaining files
    root_html_files = list(posts_dir.glob("*.html"))
    if root_html_files:
        print(f"\n📁 ROOT Directory (to be migrated):")
        for html_file in root_html_files:
            images, links = count_links_and_images(html_file)
            
            is_valid = images >= 1 and 3 <= links <= 5
            if not is_valid:
                all_valid = False
            
            status = "✅ VALID" if is_valid else "❌ INVALID"
            print(f"  {status} - {html_file.name} - Images: {images}, Links: {links}")
            total_posts += 1
    
    print(f"\n📊 SUMMARY: {total_posts} total posts")
    print(f"{'✅ ALL POSTS VALID' if all_valid else '❌ SOME POSTS INVALID'}")
    return all_valid

if __name__ == "__main__":
    verify_all_posts()
