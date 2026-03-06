# Token Generation in LLMs

## Core Components

### 1. Input Processing

- Input tokens → embedding layer
- Each layer: QKV calculation from same embeddings
- Multi-head self-attention processes all tokens
- Residual connections + layer norm
- Output: encoded representations

### 2. Generation Loop (Autoregressive)

**Key insight:** Generate one token at a time

```
Input: "The cat sat"
Step 1: Predict next token → "on"
Step 2: Input: "The cat sat on" → Predict "the"
Step 3: Input: "The cat sat on the" → Predict "mat"
```

### 3. The Mask Problem

**Purpose:** Prevent tokens from "seeing" future tokens

- During training: mask future positions
- During inference: causal mask (only see past tokens)
- This is why generation is sequential

### 4. KV Cache - THE CRITICAL OPTIMIZATION

**Problem:** Recomputing QKV for all previous tokens is expensive
**Solution:** Cache QK values from previous tokens

```
Without KV Cache:
Step 1: Compute QKV for ["The", "cat", "sat"] 
Step 2: Compute QKV for ["The", "cat", "sat", "on"] ← recompute!
Step 3: Compute QKV for ["The", "cat", "sat", "on", "the"] ← recompute!

With KV Cache:
Step 1: Compute QKV for ["The", "cat", "sat"], store in cache
Step 2: Compute QKV only for new token "on", reuse cached QKV
Step 3: Compute QKV only for new token "the", reuse cached QKV
```

**Result:** O(n²) → O(n) complexity for generation

### 5. Final Output

- Linear layer predicts next token probabilities
- Sample or argmax to get token
- Add to sequence, repeat

## Detailed Forward Pass

### Input Embedding

- Token IDs → embedding lookup (vocab_size × d_model)
- Add positional encoding (tell model where each token is)

### One Transformer Layer

```
Input: X (seq_len, d_model)

1. Self-Attention:
   Q = X @ W_q    (seq_len, d_model) → (seq_len, d_k)
   K = X @ W_k    (seq_len, d_model) → (seq_len, d_k)  
   V = X @ W_v    (seq_len, d_model) → (seq_len, d_v)

   Attention(Q,K,V) = softmax(QK^T / √d_k) @ V
   Output: (seq_len, d_v)

2. Residual + LayerNorm:
   X = LayerNorm(X + AttentionOutput)

3. Feed-Forward:
   X = GELU(X @ W_1) @ W_2   (d_model → 4×d_model → d_model)

4. Residual + LayerNorm:
   X = LayerNorm(X + FFOutput)
```

Repeat for N layers (typically 12, 24, or 32).

### Output Head

- Final layer norm

- Linear projection: (seq_len, d_model) → (seq_len, vocab_size)

- Softmax → probability distribution over next token

- KV cache is biggest memory bottleneck

- Batching strategies optimize multiple requests

- Most inference research focuses on cache optimization

## The Generation Loop

```python
tokens = tokenize("The cat sat")  # [464, 3797, 3298]

for i in range(max_new_tokens):
    # Forward pass: (current_seq_len, d_model) → (current_seq_len, vocab_size)
    logits = transformer(tokens)

    # Get prediction for NEXT token (last position)
    next_token_logits = logits[-1, :]

    # Convert to token
    next_token = argmax(next_token_logits)  # or sampling

    # Append to sequence
    tokens.append(next_token)

    # Stop if we hit EOS (end-of-sequence) token
    if next_token == EOS_TOKEN:
        break
```

### Why This Is Expensive

- **Every token requires a full forward pass**
- **Each pass processes ALL previous tokens**
- **Attention is O(n²)** - grows quadratically with sequence length
- **For 100 new tokens:** 100 forward passes, each getting slower

### Training vs Inference Difference

|              | Training                  | Inference           |
| ------------ | ------------------------- | ------------------- |
| Input        | Full sequence             | One token at a time |
| Parallel     | Yes (process all at once) | No (sequential)     |
| Speed        | Fast                      | Slow                |
| Optimization | FLOPs                     | Memory & latency    |

## Why This Matters for Research

- Inference is memory-bound, not compute-bound
- KV cache was invented to fix the redundant computation
- Batching, quantization, speculative decoding all target this bottleneck
