#!/usr/bin/env python3
"""
Script to fix image formatting in blog posts
"""

import os
import re

def fix_image_formatting(filepath):
    """Fix image formatting in a blog post."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if this file has the formatting issue
    if 'image: "' in content and '![' in content:
        # Find the frontmatter end
        frontmatter_matches = list(re.finditer(r'^---$', content, re.MULTILINE))
        if len(frontmatter_matches) < 2:
            return False
        
        frontmatter_end = frontmatter_matches[1].end()
        
        # Split content
        frontmatter = content[:frontmatter_end]
        post_content = content[frontmatter_end:]
        
        # Check if image is misplaced
        if '\n![' in frontmatter:
            # Extract the misplaced image
            image_pattern = r'\n(\!\[.*?\]\(.*?\))\n(\*.*?\*)?'
            image_match = re.search(image_pattern, frontmatter)
            
            if image_match:
                # Remove from frontmatter
                frontmatter = frontmatter.replace(image_match.group(0), '')
                
                # Add to beginning of post content
                image_line = image_match.group(1)
                caption_line = image_match.group(2) if image_match.group(2) else ""
                
                # Improve alt text based on filename
                if 'battery' in filepath.lower() or 'lithium' in filepath.lower():
                    image_line = re.sub(r'\!\[.*?\]', '![Advanced Battery Storage Technology]', image_line)
                    caption_line = "*Advanced battery storage and recycling technology*"
                elif 'wind' in filepath.lower() or 'offshore' in filepath.lower():
                    image_line = re.sub(r'\!\[.*?\]', '![Offshore Wind Technology]', image_line)
                    caption_line = "*Offshore wind turbines generating clean energy*"
                elif 'solar' in filepath.lower() or 'perovskite' in filepath.lower():
                    image_line = re.sub(r'\!\[.*?\]', '![Advanced Solar Technology]', image_line)
                    caption_line = "*Advanced solar panel and photovoltaic technology*"
                elif 'ev' in filepath.lower() or 'charging' in filepath.lower():
                    image_line = re.sub(r'\!\[.*?\]', '![EV Charging Infrastructure]', image_line)
                    caption_line = "*Electric vehicle charging infrastructure*"
                elif 'ai' in filepath.lower() or 'smart' in filepath.lower() or 'grid' in filepath.lower():
                    image_line = re.sub(r'\!\[.*?\]', '![Smart Grid Technology]', image_line)
                    caption_line = "*Smart grid and energy management systems*"
                else:
                    image_line = re.sub(r'\!\[.*?\]', '![Renewable Energy Technology]', image_line)
                    caption_line = "*Renewable energy technology and infrastructure*"
                
                # Insert at beginning of post content
                post_content = f'\n\n{image_line}\n{caption_line}\n' + post_content
                
                # Write back
                new_content = frontmatter + post_content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"Fixed image formatting in {os.path.basename(filepath)}")
                return True
    
    return False

def main():
    posts_dir = '_posts'
    posts_fixed = 0
    
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(posts_dir, filename)
            if fix_image_formatting(filepath):
                posts_fixed += 1
    
    print(f"\nFixed {posts_fixed} posts")

if __name__ == '__main__':
    main()
