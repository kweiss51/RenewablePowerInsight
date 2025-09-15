#!/usr/bin/env python3
"""
Quick Blog Post Generator - Simple CLI interface for creating automated blog posts
Usage: python quick_post.py "Post Title" [category]
"""

import sys
import os
from pathlib import Path

# Add ml_models directory to path
sys.path.append(str(Path(__file__).parent))

from blog_automation_controller import BlogAutomationController

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_post.py \"Post Title\" [category]")
        print("\nExample: python quick_post.py \"Solar Panel Innovations 2025\"")
        print("Example: python quick_post.py \"Wind Energy Developments\" \"Wind Energy\"")
        print("\nAvailable categories:")
        print("- Solar Energy")
        print("- Wind Energy") 
        print("- Energy Storage")
        print("- Energy Policy")
        print("- Clean Technology")
        print("- Energy Markets")
        sys.exit(1)
    
    title = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"🚀 Quick Blog Post Generator")
    print(f"📝 Title: {title}")
    if category:
        print(f"📂 Category: {category}")
    print("=" * 60)
    
    # Initialize controller
    controller = BlogAutomationController("../posts")
    
    # Create the post
    result = controller.create_automated_post(
        title=title,
        category=category
    )
    
    if result['success']:
        print(f"\n🎉 SUCCESS! Post created and integrated into website")
        print(f"📁 File: {result['post_filename']}")
        print(f"🔗 URL: {result['post_url']}")
    else:
        print(f"\n❌ FAILED: {result['error_message']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
