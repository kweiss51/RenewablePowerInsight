#!/usr/bin/env python3
"""
Fix duplicate Key Statistics sections in blog posts
"""
import os
import re
import glob

def fix_duplicate_key_statistics():
    """Remove duplicate Key Statistics sections from blog posts"""
    posts_dir = '/Users/kyleweiss/Documents/GitHub/RenewablePowerInsight/_posts'
    
    # Get all markdown files
    post_files = glob.glob(os.path.join(posts_dir, '*.md'))
    
    fixes_made = 0
    
    for post_file in post_files:
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Find all Key Statistics sections
            key_stats_pattern = r'## Key Statistics:.*?(?=\n## |$)'
            matches = re.findall(key_stats_pattern, content, re.DOTALL)
            
            if len(matches) > 1:
                print(f"Found {len(matches)} Key Statistics sections in {os.path.basename(post_file)}")
                
                # Keep only the last (most complete) Key Statistics section
                # Remove all but the last occurrence
                for i in range(len(matches) - 1):
                    content = content.replace(matches[i], '', 1)
                
                # Clean up any double newlines left behind
                content = re.sub(r'\n\n\n+', '\n\n', content)
                
                # Write back to file if content changed
                if content != original_content:
                    with open(post_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixes_made += 1
                    print(f"Fixed {os.path.basename(post_file)}")
                    
        except Exception as e:
            print(f"Error processing {post_file}: {e}")
    
    print(f"\nFixed {fixes_made} files with duplicate Key Statistics sections")

if __name__ == "__main__":
    fix_duplicate_key_statistics()
