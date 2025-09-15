#!/usr/bin/env python3
"""
Simple Energy Content Inference Engine
Generates blog posts using the trained energy domain model
Automatically saves posts to the website posts folder
"""

import torch
import torch.nn.functional as F
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config
import json
import logging
import random
from pathlib import Path
from typing import List, Dict, Optional
import re

# Import our automated blog generator
from .automated_blog_generator import AutomatedBlogGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnergyInference:
    def __init__(self, model_path: str = 'ml_models/model_checkpoints'):
        """Initialize the inference engine"""
        self.model_path = Path(model_path)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize the automated blog generator
        posts_dir = Path(__file__).parent.parent / "posts"
        self.blog_generator = AutomatedBlogGenerator(str(posts_dir))
        
        # Energy-specific prompts and templates
        self.energy_topics = [
            "renewable energy", "solar power", "wind energy", "hydroelectric power",
            "geothermal energy", "energy storage", "battery technology", "smart grid",
            "electric vehicles", "energy efficiency", "carbon capture", "nuclear power",
            "biomass energy", "energy policy", "sustainability", "clean technology"
        ]
        
        self.content_templates = [
            "Recent developments in {} show promising advances",
            "The future of {} looks increasingly bright",
            "Industry experts predict {} will transform",
            "New research in {} reveals significant potential",
            "Government initiatives in {} are driving innovation",
            "Market trends indicate {} is experiencing rapid growth"
        ]
        
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and tokenizer"""
        try:
            # Try to load the fine-tuned model
            model_file = self.model_path / 'best_model.pth'
            
            if model_file.exists():
                logger.info("Loading fine-tuned energy model...")
                
                # Load tokenizer (use GPT-2 base)
                self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
                # Load model configuration and weights
                config = GPT2Config.from_pretrained('gpt2')
                self.model = GPT2LMHeadModel(config)
                
                # Load trained weights
                checkpoint = torch.load(model_file, map_location=self.device)
                if 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)
                
                self.model.to(self.device)
                self.model.eval()
                
                logger.info("✅ Fine-tuned model loaded successfully")
                
            else:
                logger.warning("No fine-tuned model found, using base GPT-2")
                self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.model = GPT2LMHeadModel.from_pretrained('gpt2')
                self.model.to(self.device)
                self.model.eval()
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.info("Falling back to base GPT-2 model")
            
            # Fallback to base model
            self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = GPT2LMHeadModel.from_pretrained('gpt2')
            self.model.to(self.device)
            self.model.eval()
    
    def generate_content(self, prompt: str, max_length: int = 800, temperature: float = 0.8) -> str:
        """Generate content based on a prompt"""
        try:
            # Ensure prompt is energy-related
            energy_prompt = self._enhance_prompt(prompt)
            
            # Tokenize input
            inputs = self.tokenizer.encode(energy_prompt, return_tensors='pt', max_length=512, truncation=True)
            inputs = inputs.to(self.device)
            
            # Generate with controlled parameters
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=min(max_length + len(inputs[0]), 1024),
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,
                    repetition_penalty=1.2,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    num_return_sequences=1
                )
            
            # Decode generated text
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the original prompt and clean up
            content = generated_text[len(energy_prompt):].strip()
            content = self._clean_generated_content(content)
            
            # Ensure minimum length
            if len(content.split()) < 100:
                # Generate additional content
                extended_prompt = f"{energy_prompt}\n\n{content}\n\nFurthermore,"
                return self._generate_extended_content(extended_prompt, max_length)
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return self._generate_fallback_content(prompt)
    
    def _enhance_prompt(self, prompt: str) -> str:
        """Enhance the prompt with energy-specific context"""
        energy_context = random.choice([
            "In the rapidly evolving energy sector,",
            "Recent advances in renewable energy technology show that",
            "The global transition to clean energy demonstrates that",
            "Energy industry analysis reveals that",
            "According to recent energy market research,"
        ])
        
        # Ensure the prompt mentions energy if it doesn't already
        if not any(topic in prompt.lower() for topic in ['energy', 'power', 'electric', 'renewable', 'solar', 'wind']):
            enhanced_prompt = f"{energy_context} {prompt} in the energy sector"
        else:
            enhanced_prompt = f"{energy_context} {prompt}"
        
        return enhanced_prompt
    
    def _clean_generated_content(self, content: str) -> str:
        """Clean and format the generated content"""
        # Remove incomplete sentences at the end
        sentences = content.split('.');
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            sentences = sentences[:-1]
        
        content = '. '.join(sentences).strip()
        if content and not content.endswith('.'): 
            content += '.'
        
        # Remove excessive repetition
        content = re.sub(r'(.{20,}?)\1{2,}', r'\1', content)
        
        # Ensure proper capitalization
        content = '. '.join(sentence.strip().capitalize() for sentence in content.split('.') if sentence.strip())
        
        return content
    
    def _generate_extended_content(self, prompt: str, max_length: int) -> str:
        """Generate extended content for short outputs"""
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors='pt', max_length=512, truncation=True)
            inputs = inputs.to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=min(max_length + len(inputs[0]), 1024),
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.3,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            content = generated_text[len(prompt):].strip()
            return self._clean_generated_content(content)
            
        except Exception as e:
            logger.error(f"Error generating extended content: {e}")
            return self._generate_fallback_content("energy technology developments")
    
    def _generate_fallback_content(self, topic: str) -> str:
        """Generate fallback content when model fails"""
        templates = [
            f"The {topic} sector continues to evolve rapidly with new innovations emerging regularly. Industry experts emphasize the importance of sustainable development and technological advancement. Recent market analysis shows significant growth potential in this area. Investment in research and development remains crucial for long-term success. Stakeholders across the industry are collaborating to address current challenges and unlock new opportunities. The future outlook appears promising with continued focus on efficiency and environmental responsibility.",
            
            f"Recent developments in {topic} demonstrate the industry's commitment to innovation and sustainability. Market leaders are investing heavily in next-generation technologies that promise to transform the landscape. Regulatory support and policy initiatives are creating favorable conditions for growth. Consumer demand for clean and efficient solutions continues to drive market expansion. Research institutions and private companies are working together to accelerate technological breakthroughs. The convergence of digital technologies and traditional energy systems is opening new possibilities for optimization and performance improvement."
        ]
        
        return random.choice(templates)
    
    def generate_blog_post(self, topic: str, target_length: int = 600) -> Dict[str, str]:
        """Generate a complete blog post with title and content"""
        try:
            # Generate title
            title_prompt = f"Blog post title about {topic} in energy sector:";
            title = self.generate_content(title_prompt, max_length=50, temperature=0.7);
            title = title.split('\n')[0].strip();
            if not title:
                title = f"Energy Insights: {topic.title()}";
            
            # Generate main content
            content_prompt = f"Write a comprehensive blog post about {topic} covering recent developments, market trends, and future outlook";
            content = self.generate_content(content_prompt, max_length=target_length, temperature=0.8);
            
            # Structure the content
            structured_content = self._structure_blog_content(content, topic);
            
            return {
                'title': title,
                'content': structured_content,
                'topic': topic,
                'word_count': len(structured_content.split())
            }
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}");
            return {
                'title': f"Energy Update: {topic.title()}",
                'content': self._generate_fallback_content(topic),
                'topic': topic,
                'word_count': len(self._generate_fallback_content(topic).split())
            }
    
    def generate_and_save_blog_post(self, topic: str, target_length: int = 600, category: str = None) -> Dict[str, str]:
        """Generate a blog post and automatically save it to the posts folder"""
        print(f"🤖 Generating blog post about: {topic}")
        
        # Generate the blog post content
        blog_data = self.generate_blog_post(topic, target_length)
        
        # Save to posts folder using the automated blog generator
        try:
            post_info = self.blog_generator.create_blog_post(
                title=blog_data['title'],
                content=blog_data['content'],
                custom_category=category
            )
            
            # Combine the blog data with post info
            result = {**blog_data, **post_info}
            
            print(f"✅ Blog post saved successfully!")
            print(f"   📄 Title: {result['title']}")
            print(f"   📁 File: {result['filename']}")
            print(f"   🔗 URL: {result['url']}")
            print(f"   📂 Category: {result['category']}")
            print(f"   📝 Words: {result['word_count']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error saving blog post: {e}")
            return blog_data
    
    def batch_generate_posts(self, topics: List[str], target_length: int = 600) -> List[Dict[str, str]]:
        """Generate multiple blog posts and save them all"""
        print(f"🚀 Starting batch generation of {len(topics)} blog posts...")
        
        generated_posts = []
        
        for i, topic in enumerate(topics, 1):
            print(f"\n📝 Generating post {i}/{len(topics)}: {topic}")
            
            post_result = self.generate_and_save_blog_post(topic, target_length)
            generated_posts.append(post_result)
            
            # Small delay between generations to avoid overwhelming the system
            import time
            time.sleep(1)
        
        print(f"\n🎉 Batch generation complete! Generated {len(generated_posts)} posts.")
        return generated_posts
    
    def _structure_blog_content(self, content: str, topic: str) -> str:
        """Structure the blog content with proper formatting"""
        # Split content into paragraphs
        sentences = content.split('. ');
        paragraphs = [];
        current_paragraph = [];
        
        for i, sentence in enumerate(sentences):
            current_paragraph.append(sentence.strip());
            
            # Create new paragraph every 3-4 sentences
            if len(current_paragraph) >= 3 or (i > 0 and i % 4 == 0):
                paragraph_text = '. '.join(current_paragraph);
                if not paragraph_text.endswith('.'): 
                    paragraph_text += '.';
                paragraphs.append(paragraph_text);
                current_paragraph = [];
        
        # Add remaining sentences
        if current_paragraph:
            paragraph_text = '. '.join(current_paragraph);
            if not paragraph_text.endswith('.'): 
                paragraph_text += '.';
            paragraphs.append(paragraph_text);
        
        # Join paragraphs with double newlines
        structured_content = '\n\n'.join(paragraphs);
        
        # Add a conclusion if content is substantial
        if len(structured_content.split()) > 200:
            conclusion = f"\n\nThe developments in {topic} continue to shape the energy landscape, offering new opportunities for sustainable growth and innovation. As the industry evolves, stakeholders must remain adaptable and forward-thinking to capitalize on emerging trends and technologies."
            structured_content += conclusion;
        
        return structured_content

def main():
    """Test the inference engine"""
    print("🚀 Testing Energy Content Inference Engine...")
    
    inference = EnergyInference();
    
    test_topics = [
        "solar power innovations",
        "energy storage solutions",
        "electric vehicle infrastructure"
    ];
    
    for topic in test_topics:
        print(f"\n📝 Generating blog post about: {topic}");
        post = inference.generate_blog_post(topic);
        print(f"Title: {post['title']}");
        print(f"Word Count: {post['word_count']}");
        print(f"Content Preview: {post['content'][:200]}...");
        print("-" * 50);

if __name__ == "__main__":
    main()

import torch
import torch.nn.functional as F
from pathlib import Path
import json
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class EnergyLLMInference:
    """Inference engine for Energy Language Model"""
    
    def __init__(self, model_path: str, device: Optional[str] = None):
        """
        Initialize inference engine
        
        Args:
            model_path: Path to trained model directory
            device: Device to run inference on ('cpu', 'cuda', or None for auto)
        """
        self.model_path = Path(model_path)
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Initializing Energy LLM Inference on {self.device}")
        
        # Load model and tokenizer
        self.model = None
        self.tokenizer = None
        self.config = None
        self._load_model()
        
        # Energy-specific prompts and templates
        self.energy_prompts = {
            'news_analysis': "Analyze the following energy industry development:",
            'market_trends': "Discuss current trends in the energy market regarding:",
            'technology_review': "Provide an overview of this energy technology:",
            'policy_impact': "Explain the impact of this energy policy:",
            'renewable_focus': "Discuss renewable energy aspects of:",
            'investment_analysis': "Analyze the investment potential in:",
            'sustainability': "Evaluate the sustainability implications of:",
            'grid_infrastructure': "Discuss grid infrastructure implications of:",
            'energy_storage': "Analyze energy storage considerations for:",
            'carbon_emissions': "Evaluate carbon emission impacts of:"
        }
        
        # Generation parameters for different use cases
        self.generation_configs = {
            'creative': {
                'temperature': 0.9,
                'top_k': 50,
                'top_p': 0.9,
                'do_sample': True,
                'repetition_penalty': 1.1
            },
            'analytical': {
                'temperature': 0.7,
                'top_k': 40,
                'top_p': 0.8,
                'do_sample': True,
                'repetition_penalty': 1.2
            },
            'factual': {
                'temperature': 0.3,
                'top_k': 20,
                'top_p': 0.7,
                'do_sample': True,
                'repetition_penalty': 1.3
            },
            'conservative': {
                'temperature': 0.1,
                'top_k': 10,
                'top_p': 0.5,
                'do_sample': False,
                'repetition_penalty': 1.2
            }
        }
    
    def _load_model(self):
        """Load the trained model and tokenizer"""
        try:
            # Import here to avoid startup errors if not installed
            from transformers import AutoTokenizer
            from energy_llm import EnergyLanguageModel
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            logger.info(f"Loaded tokenizer with vocab size: {len(self.tokenizer)}")
            
            # Load model
            self.model = EnergyLanguageModel.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            
            # Load config if available
            config_path = self.model_path / "config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            
            logger.info("Model loaded successfully")
            
        except ImportError as e:
            logger.error(f"Required packages not installed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def generate_text(
        self,
        prompt: str,
        max_length: int = 512,
        style: str = 'analytical',
        energy_context: Optional[str] = None,
        custom_params: Optional[Dict] = None
    ) -> str:
        """
        Generate text using the Energy LLM
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            style: Generation style ('creative', 'analytical', 'factual', 'conservative')
            energy_context: Optional energy domain context to prepend
            custom_params: Custom generation parameters
            
        Returns:
            Generated text
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Check initialization.")
        
        # Prepare full prompt
        full_prompt = self._prepare_prompt(prompt, energy_context)
        
        # Get generation parameters
        gen_params = self.generation_configs.get(style, self.generation_configs['analytical'])
        if custom_params:
            gen_params.update(custom_params)
        
        # Tokenize input
        input_ids = self.tokenizer.encode(
            full_prompt,
            return_tensors='pt',
            truncation=True,
            max_length=self.model.config.max_position_embeddings - max_length
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids,
                max_length=input_ids.shape[1] + max_length,
                pad_token_id=self.tokenizer.eos_token_id,
                **gen_params
            )
        
        # Decode and clean
        generated_text = self.tokenizer.decode(
            generated_ids[0],
            skip_special_tokens=True
        )
        
        # Extract only the new content
        new_content = generated_text[len(full_prompt):].strip()
        
        return self._post_process_text(new_content)
    
    def _prepare_prompt(self, prompt: str, energy_context: Optional[str] = None) -> str:
        """Prepare the full prompt with energy context"""
        if energy_context and energy_context in self.energy_prompts:
            context_prompt = self.energy_prompts[energy_context]
            return f"{context_prompt} {prompt}"
        return prompt
    
    def _post_process_text(self, text: str) -> str:
        """Post-process generated text"""
        # Remove incomplete sentences at the end
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 1 and sentences[-1].strip() and not sentences[-1].strip().endswith(('.', '!', '?')):
            text = '.'.join(sentences[:-1]) + '.'
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove repetitive patterns
        text = self._remove_repetitions(text)
        
        return text
    
    def _remove_repetitions(self, text: str, max_repeat: int = 3) -> str:
        """Remove repetitive phrases"""
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            # Check for repetitive patterns
            if i >= max_repeat:
                recent_words = words[i-max_repeat:i]
                if recent_words.count(word) >= max_repeat:
                    continue
            result.append(word)
        
        return ' '.join(result)
    
    def generate_blog_post(
        self,
        title: str,
        key_points: List[str],
        target_length: int = 800,
        style: str = 'analytical'
    ) -> Dict[str, str]:
        """
        Generate a complete blog post about energy topics
        
        Args:
            title: Blog post title
            key_points: List of key points to cover
            target_length: Target length in words
            style: Writing style
            
        Returns:
            Dictionary with blog post sections
        """
        blog_post = {
            'title': title,
            'introduction': '',
            'body_sections': [],
            'conclusion': '',
            'full_text': ''
        }
        
        # Generate introduction
        intro_prompt = f"Write an engaging introduction for a blog post titled '{title}' that covers the following key points: {', '.join(key_points[:3])}"
        blog_post['introduction'] = self.generate_text(
            intro_prompt,
            max_length=150,
            style=style,
            energy_context='news_analysis'
        )
        
        # Generate body sections for each key point
        for i, point in enumerate(key_points):
            section_prompt = f"Write a detailed section about: {point}. This is part of a blog post about {title}."
            section_text = self.generate_text(
                section_prompt,
                max_length=200,
                style=style,
                energy_context='technology_review' if 'technology' in point.lower() else 'market_trends'
            )
            blog_post['body_sections'].append({
                'heading': point,
                'content': section_text
            })
        
        # Generate conclusion
        conclusion_prompt = f"Write a conclusion for a blog post about '{title}' that summarizes the key insights about: {', '.join(key_points)}"
        blog_post['conclusion'] = self.generate_text(
            conclusion_prompt,
            max_length=150,
            style=style,
            energy_context='market_trends'
        )
        
        # Assemble full text
        full_text_parts = [
            f"# {blog_post['title']}\n\n",
            blog_post['introduction'] + "\n\n"
        ]
        
        for section in blog_post['body_sections']:
            full_text_parts.extend([
                f"## {section['heading']}\n\n",
                section['content'] + "\n\n"
            ])
        
        full_text_parts.extend([
            "## Conclusion\n\n",
            blog_post['conclusion']
        ])
        
        blog_post['full_text'] = ''.join(full_text_parts)
        
        return blog_post
    
    def analyze_energy_news(self, news_text: str, analysis_type: str = 'comprehensive') -> Dict[str, str]:
        """
        Analyze energy news and provide insights
        
        Args:
            news_text: Raw news text to analyze
            analysis_type: Type of analysis ('summary', 'impact', 'trends', 'comprehensive')
            
        Returns:
            Analysis results
        """
        analysis_prompts = {
            'summary': "Provide a concise summary of this energy news:",
            'impact': "Analyze the potential impact of this energy development:",
            'trends': "Identify key trends and implications from this energy news:",
            'comprehensive': "Provide a comprehensive analysis of this energy development including market impact, technological implications, and future trends:"
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts['comprehensive'])
        analysis_text = self.generate_text(
            f"{prompt}\n\n{news_text}",
            max_length=400,
            style='analytical',
            energy_context='news_analysis'
        )
        
        return {
            'analysis_type': analysis_type,
            'original_text': news_text,
            'analysis': analysis_text,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_energy_insights(self, topic: str, insight_type: str = 'market_trends') -> str:
        """
        Generate insights about specific energy topics
        
        Args:
            topic: Energy topic to analyze
            insight_type: Type of insights ('market_trends', 'technology_review', 'policy_impact', etc.)
            
        Returns:
            Generated insights
        """
        if insight_type not in self.energy_prompts:
            insight_type = 'market_trends'
        
        prompt = f"Provide detailed insights about: {topic}"
        
        return self.generate_text(
            prompt,
            max_length=300,
            style='analytical',
            energy_context=insight_type
        )
    
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """
        Generate text for multiple prompts
        
        Args:
            prompts: List of prompts
            **kwargs: Generation parameters
            
        Returns:
            List of generated texts
        """
        results = []
        
        for prompt in prompts:
            try:
                result = self.generate_text(prompt, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error generating text for prompt '{prompt[:50]}...': {e}")
                results.append(f"Error generating text: {str(e)}")
        
        return results
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        if self.model is None:
            return {"status": "Model not loaded"}
        
        info = {
            "model_path": str(self.model_path),
            "device": self.device,
            "vocab_size": len(self.tokenizer) if self.tokenizer else None,
            "max_length": getattr(self.model.config, 'max_position_embeddings', None),
            "model_size": self.model.get_model_size() if hasattr(self.model, 'get_model_size') else None
        }
        
        if self.config:
            info["training_config"] = self.config
        
        return info

def load_energy_llm(model_path: str, device: Optional[str] = None) -> EnergyLLMInference:
    """
    Convenience function to load Energy LLM for inference
    
    Args:
        model_path: Path to trained model
        device: Device to use
        
    Returns:
        EnergyLLMInference instance
    """
    return EnergyLLMInference(model_path, device)

# Example usage
if __name__ == "__main__":
    # Example usage (requires trained model)
    try:
        # Load model
        llm = load_energy_llm("model_checkpoints/best_model")
        
        # Generate text
        result = llm.generate_text(
            "The future of solar energy technology",
            style='analytical',
            energy_context='technology_review'
        )
        
        print("Generated text:")
        print(result)
        
        # Generate blog post
        blog = llm.generate_blog_post(
            "Renewable Energy Investment Trends 2024",
            [
                "Solar power cost reductions",
                "Wind energy capacity growth",
                "Battery storage innovations",
                "Policy support mechanisms"
            ]
        )
        
        print("\nGenerated blog post:")
        print(blog['full_text'])
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have a trained model and required packages installed.")
