#!/usr/bin/env python3
"""
Blog Image Updater - Replace placeholder images with actual post header images
"""

import os
import re
import glob
from datetime import datetime

def extract_header_image_from_post(post_path):
    """Extract the first image URL from a blog post"""
    try:
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the first image in the post content
        img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
        matches = re.findall(img_pattern, content)
        
        if matches:
            # Return the first image URL
            return matches[0]
        return None
    except Exception as e:
        print(f"Error reading post {post_path}: {e}")
        return None

def extract_post_info_from_blog_page():
    """Extract all post information from the blog index page"""
    blog_path = '/Users/kyleweiss/Documents/GitHub/RenewablePowerInsight/blog/index.html'
    
    try:
        with open(blog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all article cards with their links and images
        articles = []
        
        # Pattern to match grid articles (updated structure)
        article_pattern = r'<article class="grid-article".*?<img src="([^"]+)".*?<a href="([^"]+)".*?>(.*?)</a>'
        matches = re.findall(article_pattern, content, re.DOTALL)
        
        for match in matches:
            current_img, post_link, title = match
            articles.append({
                'link': post_link.strip(),
                'current_img': current_img.strip(), 
                'title': title.strip(),
                'is_placeholder': 'placeholder' in current_img
            })
        
        return articles
    except Exception as e:
        print(f"Error reading blog page: {e}")
        return []

def update_blog_page_images():
    """Update placeholder images in the blog page with actual header images"""
    print("🔄 Updating blog page placeholder images...")
    
    # Get all post info from blog page
    articles = extract_post_info_from_blog_page()
    placeholder_articles = [a for a in articles if a['is_placeholder']]
    
    print(f"Found {len(placeholder_articles)} articles with placeholder images")
    
    # Get actual posts to match against
    posts_dir = '/Users/kyleweiss/Documents/GitHub/RenewablePowerInsight/posts'
    all_posts = []
    
    for category in ['general', 'solar', 'wind', 'battery', 'policy', 'grid-tech', 'markets']:
        category_path = os.path.join(posts_dir, category)
        if os.path.exists(category_path):
            posts = glob.glob(os.path.join(category_path, '*.html'))
            all_posts.extend(posts)
    
    print(f"Found {len(all_posts)} total posts")
    
    # Read blog page content
    blog_path = '/Users/kyleweiss/Documents/GitHub/RenewablePowerInsight/blog/index.html'
    with open(blog_path, 'r', encoding='utf-8') as f:
        blog_content = f.read()
    
    updated_count = 0
    
    # For each placeholder article, find corresponding post and update image
    for article in placeholder_articles:
        # Try to find matching post by title or URL  
        post_filename = None
        if '../posts/' in article['link']:
            # Extract filename from URL path
            post_filename = os.path.basename(article['link'])
        
        if post_filename:
            # Find the actual post file
            matching_post = None
            for post_path in all_posts:
                if post_filename == os.path.basename(post_path):
                    matching_post = post_path
                    break
            
            if matching_post:
                # Extract header image from the post
                header_image = extract_header_image_from_post(matching_post)
                
                if header_image and header_image != article['current_img'] and 'placeholder' not in header_image:
                    # Update the blog page content - replace first occurrence in this article
                    old_img_src = article['current_img']
                    new_img_src = header_image
                    
                    # Find and replace the specific image tag
                    old_img_pattern = re.escape(old_img_src)
                    if re.search(old_img_pattern, blog_content):
                        blog_content = re.sub(old_img_pattern, new_img_src, blog_content, count=1)
                        updated_count += 1
                        print(f"✅ Updated image for: {article['title'][:50]}...")
                        print(f"   {old_img_src} -> {new_img_src}")
                else:
                    if not header_image:
                        print(f"⚠️  No header image found for: {article['title'][:50]}...")
                    elif 'placeholder' in header_image:
                        print(f"⚠️  Header image is also placeholder for: {article['title'][:50]}...")
    
    if updated_count > 0:
        # Write updated content back to blog page
        with open(blog_path, 'w', encoding='utf-8') as f:
            f.write(blog_content)
        
        print(f"\n🎉 Successfully updated {updated_count} placeholder images in blog page!")
    else:
        print("\n✅ No placeholder images needed updating.")
    
    return updated_count

def main():
    """Main function to update blog images"""
    print("🚀 Blog Image Updater Starting...")
    print("=" * 50)
    
    updated = update_blog_page_images()
    
    print("\n" + "=" * 50)
    print(f"🏁 Blog Image Update Complete!")
    print(f"📊 Images updated: {updated}")
    print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
