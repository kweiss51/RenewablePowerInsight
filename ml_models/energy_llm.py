"""
Energy Language Model Architecture
Custom GPT-style transformer model specialized for energy domain
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import math
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnergyLLMConfig:
    """Configuration for Energy Language Model"""
    vocab_size: int = 50000
    max_sequence_length: int = 512
    hidden_size: int = 768
    num_hidden_layers: int = 12
    num_attention_heads: int = 12
    intermediate_size: int = 3072
    hidden_dropout_prob: float = 0.1
    attention_probs_dropout_prob: float = 0.1
    max_position_embeddings: int = 512
    layer_norm_epsilon: float = 1e-12
    pad_token_id: int = 0
    bos_token_id: int = 1
    eos_token_id: int = 2
    
    # Energy domain specific
    energy_domain_size: int = 10  # Number of energy domain embeddings
    use_domain_embeddings: bool = True
    use_positional_encoding: bool = True
    
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}

class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism"""
    
    def __init__(self, config: EnergyLLMConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = self.hidden_size // self.num_attention_heads
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        
        self.query = nn.Linear(self.hidden_size, self.all_head_size)
        self.key = nn.Linear(self.hidden_size, self.all_head_size)
        self.value = nn.Linear(self.hidden_size, self.all_head_size)
        
        self.dropout = nn.Dropout(config.attention_probs_dropout_prob)
        self.dense = nn.Linear(self.hidden_size, self.hidden_size)
        self.layer_norm = nn.LayerNorm(self.hidden_size, eps=config.layer_norm_epsilon)
    
    def transpose_for_scores(self, x):
        new_x_shape = x.size()[:-1] + (self.num_attention_heads, self.attention_head_size)
        x = x.view(*new_x_shape)
        return x.permute(0, 2, 1, 3)
    
    def forward(self, hidden_states, attention_mask=None):
        mixed_query_layer = self.query(hidden_states)
        mixed_key_layer = self.key(hidden_states)
        mixed_value_layer = self.value(hidden_states)
        
        query_layer = self.transpose_for_scores(mixed_query_layer)
        key_layer = self.transpose_for_scores(mixed_key_layer)
        value_layer = self.transpose_for_scores(mixed_value_layer)
        
        # Compute attention scores
        attention_scores = torch.matmul(query_layer, key_layer.transpose(-1, -2))
        attention_scores = attention_scores / math.sqrt(self.attention_head_size)
        
        # Apply attention mask
        if attention_mask is not None:
            attention_scores = attention_scores + attention_mask
        
        # Apply causal mask for autoregressive generation
        seq_length = hidden_states.size(1)
        causal_mask = torch.tril(torch.ones(seq_length, seq_length, device=hidden_states.device))
        causal_mask = causal_mask.view(1, 1, seq_length, seq_length)
        attention_scores = attention_scores.masked_fill(causal_mask == 0, float('-inf'))
        
        attention_probs = F.softmax(attention_scores, dim=-1)
        attention_probs = self.dropout(attention_probs)
        
        context_layer = torch.matmul(attention_probs, value_layer)
        context_layer = context_layer.permute(0, 2, 1, 3).contiguous()
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.view(*new_context_layer_shape)
        
        # Apply output projection and residual connection
        attention_output = self.dense(context_layer)
        attention_output = self.dropout(attention_output)
        attention_output = self.layer_norm(attention_output + hidden_states)
        
        return attention_output

class FeedForward(nn.Module):
    """Position-wise feed-forward network"""
    
    def __init__(self, config: EnergyLLMConfig):
        super().__init__()
        self.dense_1 = nn.Linear(config.hidden_size, config.intermediate_size)
        self.intermediate_act_fn = nn.GELU()
        self.dense_2 = nn.Linear(config.intermediate_size, config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_epsilon)
    
    def forward(self, hidden_states):
        residual = hidden_states
        hidden_states = self.dense_1(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        hidden_states = self.dense_2(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.layer_norm(hidden_states + residual)
        return hidden_states

class TransformerBlock(nn.Module):
    """Single transformer block"""
    
    def __init__(self, config: EnergyLLMConfig):
        super().__init__()
        self.attention = MultiHeadAttention(config)
        self.feed_forward = FeedForward(config)
    
    def forward(self, hidden_states, attention_mask=None):
        attention_output = self.attention(hidden_states, attention_mask)
        layer_output = self.feed_forward(attention_output)
        return layer_output

class EnergyLLMEmbeddings(nn.Module):
    """Embeddings for Energy LLM including domain-specific embeddings"""
    
    def __init__(self, config: EnergyLLMConfig):
        super().__init__()
        self.config = config
        
        # Token embeddings
        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size, padding_idx=config.pad_token_id)
        
        # Position embeddings
        if config.use_positional_encoding:
            self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        
        # Energy domain embeddings
        if config.use_domain_embeddings:
            self.domain_embeddings = nn.Embedding(config.energy_domain_size, config.hidden_size)
        
        self.layer_norm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_epsilon)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    
    def forward(self, input_ids, position_ids=None, domain_ids=None):
        seq_length = input_ids.size(1)
        device = input_ids.device
        
        # Token embeddings
        inputs_embeds = self.word_embeddings(input_ids)
        
        # Position embeddings
        if self.config.use_positional_encoding:
            if position_ids is None:
                position_ids = torch.arange(seq_length, dtype=torch.long, device=device)
                position_ids = position_ids.unsqueeze(0).expand_as(input_ids)
            position_embeds = self.position_embeddings(position_ids)
            embeddings = inputs_embeds + position_embeds
        else:
            embeddings = inputs_embeds
        
        # Domain embeddings for energy-specific context
        if self.config.use_domain_embeddings and domain_ids is not None:
            domain_embeds = self.domain_embeddings(domain_ids)
            embeddings = embeddings + domain_embeds
        
        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)
        
        return embeddings

class EnergyLanguageModel(nn.Module):
    """Custom Energy Language Model based on transformer architecture"""
    
    def __init__(self, config: EnergyLLMConfig):
        super().__init__()
        self.config = config
        
        # Embeddings
        self.embeddings = EnergyLLMEmbeddings(config)
        
        # Transformer layers
        self.transformer_blocks = nn.ModuleList([
            TransformerBlock(config) for _ in range(config.num_hidden_layers)
        ])
        
        # Language modeling head
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # Energy domain classifier (auxiliary task)
        if config.use_domain_embeddings:
            self.domain_classifier = nn.Linear(config.hidden_size, config.energy_domain_size)
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        """Initialize weights"""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.LayerNorm):
            torch.nn.init.zeros_(module.bias)
            torch.nn.init.ones_(module.weight)
    
    def forward(self, input_ids, attention_mask=None, domain_ids=None, labels=None):
        # Get embeddings
        hidden_states = self.embeddings(input_ids, domain_ids=domain_ids)
        
        # Apply attention mask
        if attention_mask is not None:
            attention_mask = attention_mask[:, None, None, :]
            attention_mask = (1.0 - attention_mask) * -10000.0
        
        # Pass through transformer blocks
        for transformer_block in self.transformer_blocks:
            hidden_states = transformer_block(hidden_states, attention_mask)
        
        # Language modeling logits
        lm_logits = self.lm_head(hidden_states)
        
        # Domain classification logits (auxiliary task)
        domain_logits = None
        if self.config.use_domain_embeddings:
            # Use pooled representation for domain classification
            pooled_output = hidden_states.mean(dim=1)
            domain_logits = self.domain_classifier(pooled_output)
        
        # Calculate losses
        loss = None
        if labels is not None:
            # Language modeling loss
            shift_logits = lm_logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss_fct = nn.CrossEntropyLoss()
            lm_loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
            
            loss = lm_loss
            
            # Add domain classification loss if available
            if domain_logits is not None and domain_ids is not None:
                domain_loss = loss_fct(domain_logits, domain_ids)
                loss = lm_loss + 0.1 * domain_loss  # Weight domain loss lower
        
        return {
            'loss': loss,
            'logits': lm_logits,
            'domain_logits': domain_logits,
            'hidden_states': hidden_states
        }
    
    def generate(self, input_ids, max_length=100, temperature=0.8, top_k=50, top_p=0.9, do_sample=True):
        """Generate text using the model"""
        self.eval()
        device = input_ids.device
        batch_size = input_ids.size(0)
        
        generated = input_ids
        
        with torch.no_grad():
            for _ in range(max_length):
                outputs = self.forward(generated)
                logits = outputs['logits']
                
                # Get logits for next token
                next_token_logits = logits[:, -1, :] / temperature
                
                if do_sample:
                    # Top-k filtering
                    if top_k > 0:
                        indices_to_remove = next_token_logits < torch.topk(next_token_logits, top_k)[0][..., -1, None]
                        next_token_logits[indices_to_remove] = float('-inf')
                    
                    # Top-p filtering
                    if top_p < 1.0:
                        sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                        sorted_indices_to_remove = cumulative_probs > top_p
                        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                        sorted_indices_to_remove[..., 0] = 0
                        
                        indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                        next_token_logits[indices_to_remove] = float('-inf')
                    
                    # Sample
                    probs = F.softmax(next_token_logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)
                else:
                    # Greedy decoding
                    next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
                
                # Append to generated sequence
                generated = torch.cat([generated, next_token], dim=-1)
                
                # Stop if EOS token is generated
                if next_token.item() == self.config.eos_token_id:
                    break
        
        return generated
    
    def save_pretrained(self, save_directory):
        """Save model and config"""
        save_path = Path(save_directory)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save model state
        torch.save(self.state_dict(), save_path / "pytorch_model.bin")
        
        # Save config
        with open(save_path / "config.json", 'w') as f:
            json.dump(self.config.to_dict(), f, indent=2)
        
        logger.info(f"Model saved to {save_directory}")
    
    @classmethod
    def from_pretrained(cls, model_directory):
        """Load model from directory"""
        model_path = Path(model_directory)
        
        # Load config
        with open(model_path / "config.json", 'r') as f:
            config_dict = json.load(f)
        
        config = EnergyLLMConfig(**config_dict)
        
        # Create model
        model = cls(config)
        
        # Load state dict
        state_dict = torch.load(model_path / "pytorch_model.bin", map_location='cpu')
        model.load_state_dict(state_dict)
        
        logger.info(f"Model loaded from {model_directory}")
        return model
    
    def get_model_size(self):
        """Calculate model size in parameters"""
        total_params = sum(p.numel() for p in self.parameters())
        trainable_params = sum(p.numel() for p in self.parameters() if p.requires_grad)
        
        return {
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'model_size_mb': total_params * 4 / (1024 * 1024)  # Assuming float32
        }

# Factory function to create different model sizes
def create_energy_llm(model_size='base', vocab_size=50000):
    """Create Energy LLM with different sizes"""
    
    configs = {
        'small': EnergyLLMConfig(
            vocab_size=vocab_size,
            hidden_size=512,
            num_hidden_layers=6,
            num_attention_heads=8,
            intermediate_size=2048
        ),
        'base': EnergyLLMConfig(
            vocab_size=vocab_size,
            hidden_size=768,
            num_hidden_layers=12,
            num_attention_heads=12,
            intermediate_size=3072
        ),
        'large': EnergyLLMConfig(
            vocab_size=vocab_size,
            hidden_size=1024,
            num_hidden_layers=24,
            num_attention_heads=16,
            intermediate_size=4096
        )
    }
    
    config = configs.get(model_size, configs['base'])
    model = EnergyLanguageModel(config)
    
    size_info = model.get_model_size()
    logger.info(f"Created {model_size} Energy LLM with {size_info['total_parameters']:,} parameters ({size_info['model_size_mb']:.1f}MB)")
    
    return model

if __name__ == "__main__":
    # Test model creation
    model = create_energy_llm('base')
    
    # Test forward pass
    batch_size, seq_length = 2, 128
    input_ids = torch.randint(0, 1000, (batch_size, seq_length))
    attention_mask = torch.ones_like(input_ids)
    
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        print(f"✅ Model test successful!")
        print(f"Output shape: {outputs['logits'].shape}")
        print(f"Model parameters: {model.get_model_size()}")
