"""
AI Blog Post Generator
Generates engaging blog posts from scraped energy news
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import openai
from dotenv import load_dotenv
import logging

# Add ml_models to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'ml_models'))

load_dotenv()
logger = logging.getLogger(__name__)

class BlogPostGenerator:
    def __init__(self, use_custom_llm: bool = True, model_path: Optional[str] = None):
        self.use_custom_llm = use_custom_llm
        self.custom_llm = None
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Try to load custom Energy LLM first
        if use_custom_llm:
            try:
                from inference import EnergyLLMInference
                
                # Use provided model path or look for trained models
                if model_path:
                    llm_path = model_path
                else:
                    # Look for trained models
                    possible_paths = [
                        Path(__file__).parent.parent / 'ml_models' / 'model_checkpoints' / 'best_model',
                        Path(__file__).parent.parent / 'ml_models' / 'model_checkpoints' / 'final_model',
                    ]
                    
                    llm_path = None
                    for path in possible_paths:
                        if path.exists():
                            llm_path = path
                            break
                
                if llm_path and Path(llm_path).exists():
                    self.custom_llm = EnergyLLMInference(str(llm_path))
                    logger.info(f"✅ Loaded custom Energy LLM from {llm_path}")
                else:
                    logger.warning("🔄 Custom Energy LLM not found, falling back to OpenAI")
                    self.use_custom_llm = False
                    
            except ImportError as e:
                logger.warning(f"📦 Custom LLM dependencies not available: {e}")
                self.use_custom_llm = False
            except Exception as e:
                logger.warning(f"⚠️ Failed to load custom Energy LLM: {e}")
                self.use_custom_llm = False
        
        # Setup OpenAI fallback
        if not self.use_custom_llm and self.openai_api_key:
            openai.api_key = self.openai_api_key
        
    def analyze_trending_topics(self, articles: List[Dict]) -> List[Dict]:
        """Analyze articles to identify the hottest topics"""
        topic_counts = {}
        topic_articles = {}
        
        for article in articles:
            keyword = article['keyword']
            if keyword not in topic_counts:
                topic_counts[keyword] = 0
                topic_articles[keyword] = []
            
            topic_counts[keyword] += 1
            topic_articles[keyword].append(article)
        
        # Sort by frequency and recency
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        
        trending_topics = []
        for topic, count in sorted_topics[:5]:  # Top 5 topics
            trending_topics.append({
                'topic': topic,
                'article_count': count,
                'articles': topic_articles[topic][:3],  # Top 3 articles per topic
                'trend_score': count * 10  # Simple scoring
            })
        
        return trending_topics
    
    def generate_blog_post(self, topic_data: Dict) -> Dict:
        """Generate a blog post for a trending topic"""
        topic = topic_data['topic']
        articles = topic_data['articles']
        
        # Create context from articles
        context = f"Topic: {topic}\\n\\n"
        for i, article in enumerate(articles, 1):
            context += f"Article {i}:\\n"
            context += f"Title: {article['title']}\\n"
            context += f"Summary: {article.get('summary', 'No summary available')}\\n\\n"
        
        # SEO-optimized prompt based on best practices
        prompt = f"""
        Write an SEO-optimized, engaging blog post about {topic} that drives traffic and conversions.
        
        Context from recent news:
        {context}
        
        SEO & Traffic Optimization Requirements:
        - Target keyword: "{topic}" (use naturally throughout, avoid keyword stuffing)
        - Write compelling headline with primary keyword near the beginning (under 60 characters)
        - Create engaging meta description (under 105 characters) with call-to-action
        - Use clear structure with H2, H3 headings that include secondary keywords
        - Write 1200-1800 words for better search ranking
        - Include transition words (however, therefore, moreover, furthermore, etc.)
        - Add actionable insights that address user pain points
        - Include internal linking opportunities (mention related energy topics)
        - Use storytelling and emotional connection
        - End with strong call-to-action
        - Include expert insights and credible information
        - Use short paragraphs (2-3 sentences max) for readability
        - Add numbered or bulleted lists for scannability
        - Include relevant emojis strategically (not overusing)
        
        Content Structure:
        1. Hook introduction that addresses search intent
        2. Clear problem/opportunity statement
        3. Main content with subheadings
        4. Practical implications and actionable advice
        5. Expert insights and future predictions
        6. Strong conclusion with call-to-action
        
        Writing Style:
        - Professional but conversational tone
        - Write for humans first, SEO second
        - Use active voice and strong verbs
        - Include specific statistics and data when possible
        - Address reader directly ("you", "your")
        
        Format the response as:
        HEADLINE: [SEO-optimized headline with primary keyword, under 60 characters]
        
        META_DESCRIPTION: [Compelling meta description under 105 characters with CTA]
        
        CONTENT: [Full SEO-optimized blog post content with proper headings and structure]
        
        TAGS: [Primary keyword, secondary keywords, related energy terms]
        
        INTERNAL_LINKS: [Suggest 3-5 related energy topics for internal linking]
        """
        
        try:
            # Use custom Energy LLM if available
            if self.use_custom_llm and self.custom_llm:
                return self._generate_with_custom_llm(topic_data)
            
            # Fallback to OpenAI
            if self.openai_api_key:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert energy industry blogger who writes engaging, informative content about renewable energy and sustainability trends."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                
                # Parse the response
                blog_post = self.parse_ai_response(content, topic, articles)
                
            else:
                # Fallback: Generate basic blog post without AI
                blog_post = self.generate_fallback_post(topic, articles)
                
        except Exception as e:
            print(f"Error generating blog post with AI: {e}")
            blog_post = self.generate_fallback_post(topic, articles)
        
        return blog_post
    
    def parse_ai_response(self, content: str, topic: str, articles: List[Dict]) -> Dict:
        """Parse AI response into structured blog post"""
        lines = content.split('\\n')
        
        headline = ""
        meta_description = ""
        blog_content = ""
        tags = []
        internal_links = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("HEADLINE:"):
                headline = line.replace("HEADLINE:", "").strip()
                current_section = "headline"
            elif line.startswith("META_DESCRIPTION:"):
                meta_description = line.replace("META_DESCRIPTION:", "").strip()
                current_section = "meta_description"
            elif line.startswith("CONTENT:"):
                current_section = "content"
                content_start = line.replace("CONTENT:", "").strip()
                if content_start:
                    blog_content = content_start + "\\n"
            elif line.startswith("TAGS:"):
                tag_line = line.replace("TAGS:", "").strip()
                tags = [tag.strip() for tag in tag_line.split(",") if tag.strip()]
                current_section = "tags"
            elif line.startswith("INTERNAL_LINKS:"):
                links_line = line.replace("INTERNAL_LINKS:", "").strip()
                internal_links = [link.strip() for link in links_line.split(",") if link.strip()]
                current_section = "internal_links"
            elif current_section == "content" and line:
                blog_content += line + "\\n"
        
        # SEO-optimized URL slug
        slug = self._create_seo_slug(headline or topic)
        
        # Calculate reading time (average 200 words per minute)
        word_count = len(blog_content.split())
        reading_time = max(1, round(word_count / 200))
        
        return {
            'headline': headline or f"🌱 Latest Developments in {topic}",
            'meta_description': meta_description or f"Discover the latest trends and insights in {topic}. Get expert analysis and actionable tips for renewable energy.",
            'content': blog_content.strip() or self._generate_fallback_content(topic, articles),
            'tags': tags or [topic.lower(), 'renewable energy', 'clean tech', 'sustainability'],
            'internal_links': internal_links or [],
            'topic': topic,
            'slug': slug,
            'word_count': word_count,
            'reading_time': reading_time,
            'author': "RenewablePowerInsight Team",
            'published_date': datetime.now().strftime('%Y-%m-%d'),
            'seo_optimized': True
        }
    
    def _generate_with_custom_llm(self, topic_data: Dict) -> Dict:
        """Generate blog post using custom Energy LLM"""
        topic = topic_data['topic']
        articles = topic_data['articles']
        
        # Extract key points from articles
        key_points = []
        for article in articles:
            if 'summary' in article and article['summary']:
                key_points.append(article['summary'][:100])  # Truncate for brevity
            else:
                # Extract key points from title
                key_points.append(article['title'])
        
        # Limit to most important points
        key_points = key_points[:4]
        
        try:
            # Generate blog post using custom LLM
            blog_data = self.custom_llm.generate_blog_post(
                title=f"Breaking: Latest Developments in {topic.title()}",
                key_points=key_points,
                target_length=1200,
                style='analytical'
            )
            
            # Generate meta description
            meta_description = self.custom_llm.generate_text(
                f"Write a compelling meta description (under 105 characters) for a blog post about {topic}",
                max_length=50,
                style='factual'
            )
            
            # Generate tags
            tags_text = self.custom_llm.generate_text(
                f"List 5-7 SEO keywords and tags for a blog post about {topic}",
                max_length=100,
                style='factual'
            )
            
            # Parse tags
            tags = [tag.strip() for tag in tags_text.replace(',', ' ').split() if tag.strip()]
            tags = list(set(tags))[:7]  # Remove duplicates and limit
            
            # Create blog post structure
            blog_post = {
                'headline': blog_data['title'],
                'meta_description': meta_description[:105],  # Ensure length limit
                'content': blog_data['full_text'],
                'tags': tags + [topic],  # Include original topic
                'internal_links': [
                    'renewable energy trends',
                    'sustainable technology',
                    'clean energy investment',
                    'green technology innovation'
                ],
                'slug': self._create_seo_slug(blog_data['title']),
                'topic': topic,
                'source_articles': len(articles),
                'ai_generated': True,
                'generation_method': 'custom_energy_llm',
                'created_at': datetime.now().isoformat(),
                'word_count': len(blog_data['full_text'].split()),
                'reading_time': max(1, len(blog_data['full_text'].split()) // 200),
                'author': "RenewablePowerInsight AI",
                'published_date': datetime.now().strftime('%Y-%m-%d'),
                'seo_optimized': True
            }
            
            logger.info(f"✅ Generated blog post using custom Energy LLM: {blog_post['headline'][:50]}...")
            return blog_post
            
        except Exception as e:
            logger.error(f"❌ Error generating with custom LLM: {e}")
            # Fallback to template
            return self.generate_fallback_post(topic, articles)
    
    def _create_seo_slug(self, text: str) -> str:
        """Create SEO-friendly URL slug"""
        import re
        # Convert to lowercase and replace spaces with hyphens
        slug = text.lower()
        # Remove special characters except spaces and hyphens
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        # Replace multiple spaces/hyphens with single hyphen
        slug = re.sub(r'[\s-]+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        # Limit length for SEO
        return slug[:60]
    
    def _generate_fallback_content(self, topic: str, articles: List[Dict]) -> str:
        """Generate fallback content when AI is not available"""
        content = f"## Latest Updates in {topic.title()}\\n\\n"
        content += f"The {topic} sector continues to evolve rapidly with significant developments that are shaping the future of renewable energy.\\n\\n"
        
        if articles:
            content += "### Recent Headlines\\n\\n"
            for i, article in enumerate(articles[:3], 1):
                content += f"{i}. **{article['title']}**\\n"
                if article.get('summary'):
                    content += f"   {article['summary']}\\n\\n"
        
        content += "### Why This Matters\\n\\n"
        content += f"These developments in {topic} represent crucial steps toward a more sustainable energy future. As the industry continues to innovate, we're seeing unprecedented growth in clean technology adoption.\\n\\n"
        
        content += "### Looking Ahead\\n\\n"
        content += "Stay tuned for more updates on this rapidly evolving sector. The future of renewable energy depends on continued innovation and investment in these critical technologies."
        
        return content
    
    def generate_fallback_post(self, topic: str, articles: List[Dict]) -> Dict:
        """Generate a SEO-optimized basic blog post without AI"""
        headline = f"🔥 Breaking: Latest Developments in {topic.title()}"
        
        # SEO-optimized meta description
        meta_description = f"Stay updated with the latest {topic} news and trends. Expert insights and analysis on renewable energy developments."
        
        # Generate structured content
        content = f"## {topic.title()}: Current Market Trends and Insights\\n\\n"
        content += f"The renewable energy sector, particularly in {topic}, is experiencing remarkable growth and innovation. Here's what you need to know about the latest developments.\\n\\n"
        
        if articles:
            content += "### 🗞️ Latest Headlines\\n\\n"
            for i, article in enumerate(articles[:5], 1):
                content += f"**{i}. {article['title']}**\\n\\n"
                if article.get('summary'):
                    content += f"{article['summary']}\\n\\n"
                    
        content += f"### 💡 Key Insights for {topic.title()}\\n\\n"
        content += "- Market growth continues to accelerate\\n"
        content += "- Technology costs are decreasing significantly\\n"
        content += "- Government policies are becoming more supportive\\n"
        content += "- Investment opportunities are expanding\\n\\n"
        
        content += "### 🎯 What This Means for You\\n\\n"
        content += f"Whether you're an investor, business owner, or simply interested in sustainable energy, these {topic} developments offer important insights into the future of clean technology.\\n\\n"
        
        content += "### 🔮 Looking Ahead\\n\\n"
        content += f"The {topic} sector is poised for continued growth. Stay informed about these trends to make the most of emerging opportunities in renewable energy.\\n\\n"
        
        content += "**Ready to learn more?** Subscribe to our newsletter for the latest renewable energy insights and market analysis."
        
        # Calculate metrics
        word_count = len(content.split())
        reading_time = max(1, round(word_count / 200))
        slug = self._create_seo_slug(headline)
        
        return {
            'headline': headline,
            'meta_description': meta_description,
            'content': content,
            'tags': [topic.lower(), 'renewable energy', 'clean tech', 'sustainability', 'market trends'],
            'internal_links': ['solar power', 'wind energy', 'energy storage', 'green technology'],
            'topic': topic,
            'slug': slug,
            'word_count': word_count,
            'reading_time': reading_time,
            'author': "RenewablePowerInsight Team",
            'published_date': datetime.now().strftime('%Y-%m-%d'),
            'seo_optimized': True,
            'source_articles': [article.get('link', '') for article in articles if article.get('link')]
        }
        
        content = f"""
# {headline}

## 📊 Current Trends

The energy sector is experiencing significant developments in {topic}. Recent news highlights several key trends that are shaping the future of this technology.

## 🔍 Key Developments

Based on recent reports, here are the major developments in {topic}:

"""
        
        for i, article in enumerate(articles, 1):
            content += f"### {i}. {article['title']}\\n\\n"
            if article.get('summary'):
                content += f"{article['summary']}\\n\\n"
            content += f"[Read more]({article['link']})\\n\\n"
        
        content += f"""
## 🚀 What This Means for the Future

These developments in {topic} represent important progress in the renewable energy sector. As technology continues to advance, we can expect to see more innovation and adoption in this space.

## 💡 Key Takeaways

- {topic.title()} continues to be a hot topic in energy news
- Multiple breakthrough developments are being reported
- The industry is moving toward more sustainable solutions
- Consumers and businesses should stay informed about these trends

Stay tuned for more updates on renewable energy developments!
"""
        
        return {
            'headline': headline,
            'content': content,
            'topic': topic,
            'tags': [topic, 'renewable energy', 'energy news', 'sustainability'],
            'source_articles': [article['link'] for article in articles],
            'generated_at': datetime.now().isoformat(),
            'word_count': len(content.split())
        }
    
    def generate_all_posts(self, articles: List[Dict]) -> List[Dict]:
        """Generate blog posts for all trending topics"""
        trending_topics = self.analyze_trending_topics(articles)
        blog_posts = []
        
        print("✍️ Generating blog posts...")
        
        for topic_data in trending_topics:
            print(f"  📝 Writing about: {topic_data['topic']}")
            blog_post = self.generate_blog_post(topic_data)
            blog_posts.append(blog_post)
        
        return blog_posts
    
    def save_blog_posts(self, posts: List[Dict], filename: str = None):
        """Save blog posts to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/blog_posts_{timestamp}.json"
        
        os.makedirs("data", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(posts)} blog posts to {filename}")
        return filename

if __name__ == "__main__":
    # Load latest articles
    import glob
    
    article_files = glob.glob("data/energy_articles_*.json")
    if article_files:
        latest_file = max(article_files)
        print(f"📖 Loading articles from {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        generator = BlogPostGenerator()
        posts = generator.generate_all_posts(articles)
        generator.save_blog_posts(posts)
    else:
        print("❌ No article files found. Run news_scraper.py first.")
    
    def generate_post_from_article(self, article: Dict) -> Optional[Dict]:
        """Generate a blog post from a single processed article"""
        try:
            # Convert processed article format to the expected format
            formatted_article = {
                'title': article.get('title', 'Energy News Update'),
                'summary': article.get('content', '')[:500] + '...',
                'url': article.get('url', ''),
                'source': article.get('source', 'Energy Research'),
                'date': article.get('date', datetime.now().isoformat()),
                'content': article.get('content', '')
            }
            
            # Generate blog post
            post = self.generate_post(formatted_article)
            return post
            
        except Exception as e:
            logger.error(f"Failed to generate post from article: {e}")
            return None
