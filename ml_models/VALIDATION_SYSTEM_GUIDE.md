# Blog Post Quality Validation System

## Overview
The automated blog generator now includes a comprehensive quality validation system that ensures every generated post meets the required standards before being saved. If a post doesn't meet the requirements, the system automatically regenerates it up to 3 times.

## Quality Requirements

### ✅ Required Standards
1. **Images**: At least 1 relevant hero image
2. **External Links**: Exactly 3-5 functioning external authority links
3. **Content Structure**: Proper HTML formatting and navigation
4. **SEO Optimization**: Proper meta tags and URL structure

## Validation Process

### 1. Post Generation
- Content is generated with topic-specific formatting
- Hero image is automatically selected based on content keywords
- 3-5 external links are embedded throughout the content
- Full HTML structure is created

### 2. Quality Validation
After each post is generated, the system:
- Counts images using regex: `<img[^>]+>`
- Counts external links using regex: `href="https?://[^"]*"`
- Validates against requirements (1+ images, 3-5 links)
- Reports validation results

### 3. Regeneration Logic
- **Success**: Post meets requirements → saved and reported as complete
- **Failure**: Post fails validation → deleted and regenerated (up to 3 attempts)
- **Max Attempts**: After 3 failed attempts → keeps last version with warning

## Example Output
```
📝 Generating post (attempt 1/3): Solar Panel Efficiency Breakthroughs
✅ Post validation passed: 1 images, 3 external links
```

Or in case of failure:
```
📝 Generating post (attempt 1/3): Solar Panel Efficiency Breakthroughs
❌ Post validation failed (attempt 1/3):
   - Insufficient external links: found 2, need 3-5
🔄 Regenerating with more link attempts...
```

## Implementation Details

### Validation Function
```python
def validate_post_quality(self, file_path: str) -> Dict[str, any]:
    # Reads HTML file and validates:
    # - Image count >= 1
    # - External link count between 3-5
    # - Returns detailed validation results
```

### Enhanced Link Embedding
- More aggressive insertion point detection
- Expanded keyword anchor text options
- Target of 4 links (middle of 3-5 range) for better reliability
- Fallback strategies for difficult content

### Error Handling
- Graceful handling of validation errors
- Detailed error reporting for debugging
- Automatic cleanup of failed posts

## Authority Link Sources
Links are selected from vetted government and industry sources:
- **Government**: EPA, DOE, NREL, Energy Star
- **Research**: National Labs, ARPA-E, Climate.gov
- **Industry**: Clean energy organizations and standards bodies

## Benefits
1. **Consistency**: All posts meet the same high standards
2. **Reliability**: Automatic regeneration ensures quality
3. **SEO Value**: Proper link count and structure
4. **User Experience**: Professional appearance with images
5. **Authority Building**: Links to trusted sources

## File Structure
- `automated_blog_generator.py`: Main generator with validation
- `verify_posts.py`: Standalone verification script
- `test_validation.py`: Validation function testing

## Usage
The validation system is automatically enabled in all blog generation modes:
- `--mode daily`: Generates 3 validated posts
- `--mode weekly`: Generates 3 validated posts  
- `--mode custom`: Generates 1 validated post with specified topic
