#!/usr/bin/env python3

import os
import sys
from automated_blog_generator import AutomatedBlogGenerator

def test_validation():
    """Test the validation function"""
    posts_dir = "../posts"
    generator = AutomatedBlogGenerator(posts_dir)
    
    print("=== Testing Validation Function ===")
    
    # Get all HTML files in posts directory
    for filename in os.listdir(posts_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(posts_dir, filename)
            print(f"\n--- {filename} ---")
            
            validation = generator.validate_post_quality(filepath)
            print(f"Valid: {validation['is_valid']}")
            print(f"Images: {validation['image_count']}")
            print(f"External links: {validation['external_link_count']}")
            
            if validation['errors']:
                print("Errors:")
                for error in validation['errors']:
                    print(f"  - {error}")

if __name__ == "__main__":
    test_validation()
