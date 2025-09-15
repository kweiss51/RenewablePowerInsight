#!/usr/bin/env python3

import os
import shutil
from pathlib import Path
from automated_blog_generator import AutomatedBlogGenerator

def migrate_existing_posts():
    """Migrate existing posts to category subfolders"""
    
    posts_dir = Path("../posts")
    generator = AutomatedBlogGenerator(str(posts_dir))
    
    print("📁 Migrating existing posts to category folders...")
    
    # Get all HTML files in the root posts directory
    html_files = [f for f in posts_dir.iterdir() if f.is_file() and f.suffix == '.html']
    
    for html_file in html_files:
        print(f"📄 Processing: {html_file.name}")
        
        # Read the file to determine category
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title and content for categorization
            # Look for the title in the HTML
            import re
            title_match = re.search(r'<h1 class="post-title">([^<]+)</h1>', content)
            if not title_match:
                title_match = re.search(r'<title>([^<]+)</title>', content)
            
            title = title_match.group(1) if title_match else html_file.stem
            
            # Remove HTML tags for content analysis
            text_content = re.sub(r'<[^>]+>', ' ', content)
            
            # Categorize using the generator's logic
            category = generator.categorize_content(title, text_content)
            category_folder = generator.get_category_folder(category)
            
            # Move file to appropriate category folder
            destination = posts_dir / category_folder / html_file.name
            
            print(f"   📂 Category: {category} → {category_folder}")
            print(f"   🔄 Moving to: {destination}")
            
            shutil.move(str(html_file), str(destination))
            print(f"   ✅ Migrated successfully")
            
        except Exception as e:
            print(f"   ❌ Error migrating {html_file.name}: {e}")
        
        print()
    
    print("🎉 Migration completed!")

if __name__ == "__main__":
    migrate_existing_posts()
