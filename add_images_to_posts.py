#!/usr/bin/env python3
"""
Script to add images to all blog posts that don't have them yet.
"""

import os
import re

# Image mappings based on post topics
IMAGE_MAPPINGS = {
    # Solar/PV related
    'solar': "https://images.unsplash.com/photo-1509391366360-2e959784a276?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    'perovskite': "https://images.unsplash.com/photo-1509391366360-2e959784a276?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    
    # Wind related
    'wind': "https://images.unsplash.com/photo-1548337138-e87d889cc369?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    'offshore': "https://images.unsplash.com/photo-1548337138-e87d889cc369?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    
    # EV/Charging related
    'ev': "https://images.unsplash.com/photo-1593941707874-ef25b8b4a92b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    'charging': "https://images.unsplash.com/photo-1593941707874-ef25b8b4a92b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    
    # Battery/Storage related
    'battery': "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    'lithium': "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    'recycling': "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    
    # Smart Grid/AI related
    'ai': "https://images.unsplash.com/photo-1518709268805-4e9042af2176?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    'smart': "https://images.unsplash.com/photo-1518709268805-4e9042af2176?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    'grid': "https://images.unsplash.com/photo-1518709268805-4e9042af2176?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    
    # General renewable energy
    'renewable': "https://images.unsplash.com/photo-1466611653911-95081537e5b7?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
    'energy': "https://images.unsplash.com/photo-1466611653911-95081537e5b7?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
}

def get_image_for_post(filename, title, content):
    """Determine the best image for a post based on its content."""
    text = (filename + " " + title + " " + content).lower()
    
    # Check for specific keywords in order of specificity
    if any(word in text for word in ['perovskite', 'solar', 'photovoltaic', 'pv']):
        return IMAGE_MAPPINGS['solar']
    elif any(word in text for word in ['wind', 'offshore', 'turbine']):
        return IMAGE_MAPPINGS['wind']
    elif any(word in text for word in ['ev', 'charging', 'electric vehicle']):
        return IMAGE_MAPPINGS['ev']
    elif any(word in text for word in ['battery', 'lithium', 'recycling', 'storage']):
        return IMAGE_MAPPINGS['battery']
    elif any(word in text for word in ['ai', 'smart', 'grid', 'management']):
        return IMAGE_MAPPINGS['smart']
    else:
        return IMAGE_MAPPINGS['renewable']

def add_image_to_post(filepath):
    """Add image to a blog post if it doesn't have one."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if post already has an image
    if 'image:' in content or '![' in content:
        print(f"Skipping {os.path.basename(filepath)} - already has images")
        return False
    
    # Extract title from frontmatter
    title_match = re.search(r'title:\s*[\'"]?([^\'"]+)[\'"]?', content)
    title = title_match.group(1) if title_match else ""
    
    # Get appropriate image
    image_url = get_image_for_post(filepath, title, content[:500])
    
    # Find the end of frontmatter
    frontmatter_end = content.find('---', content.find('---') + 3)
    if frontmatter_end == -1:
        print(f"Skipping {os.path.basename(filepath)} - no valid frontmatter")
        return False
    
    # Add image to frontmatter
    frontmatter = content[:frontmatter_end]
    post_content = content[frontmatter_end:]
    
    # Add image field to frontmatter
    new_frontmatter = frontmatter + f'\nimage: "{image_url}"'
    
    # Find the first paragraph after frontmatter and add hero image
    post_lines = post_content.split('\n')
    content_start = 0
    for i, line in enumerate(post_lines):
        if line.strip() and not line.startswith('#') and not line.startswith('<!--'):
            content_start = i
            break
    
    # Create alt text based on topic
    alt_text = "Renewable energy technology"
    if 'solar' in image_url:
        alt_text = "Advanced solar panel technology"
    elif 'wind' in image_url:
        alt_text = "Offshore wind turbines generating clean energy"
    elif 'charging' in image_url:
        alt_text = "Electric vehicle charging infrastructure"
    elif 'battery' in image_url:
        alt_text = "Advanced battery storage technology"
    elif 'smart' in image_url:
        alt_text = "Smart grid and energy management systems"
    
    # Insert hero image
    hero_image = f'\n![{alt_text}]({image_url})\n*{alt_text}*\n'
    
    post_lines.insert(content_start, hero_image)
    new_post_content = '\n'.join(post_lines)
    
    # Write back to file
    new_content = new_frontmatter + new_post_content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Added image to {os.path.basename(filepath)}")
    return True

def main():
    posts_dir = '_posts'
    posts_updated = 0
    
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(posts_dir, filename)
            if add_image_to_post(filepath):
                posts_updated += 1
    
    print(f"\nUpdated {posts_updated} posts with images")

if __name__ == '__main__':
    main()
