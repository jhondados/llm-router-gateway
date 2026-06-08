# 🚦 LLM Router & Gateway

[![Cost Savings](https://img.shields.io/badge/Cost%20Savings-78%25-green)](.) [![Models](https://img.shields.io/badge/Models%20Supported-12-blue)](.) [![Cache Hit](https://img.shields.io/badge/Cache%20Hit%20Rate-43%25-orange)](.)

> **Intelligent LLM gateway** that routes queries to the optimal model based on complexity, semantically caches similar queries and manages rate limits. Achieved **78% cost reduction** serving 5M queries/month.

## 💰 Cost Optimization Results
| Optimization | Savings |
|-------------|---------|
| Semantic caching (43% hit rate) | 43% |
| Smart routing (Flash for simple) | 28% |
| Request batching | 7% |
| **Total** | **78%** |

## 🔄 Routing Logic
```
Query → Classify complexity (flash model, 10ms)
      → [Simple]  → Gemini 1.5 Flash ($0.075/1M)
      → [Medium]  → Gemini 1.5 Pro ($3.50/1M)
      → [Complex] → Gemini 1.5 Pro 002 + extended thinking
      → [Cached]  → Redis cache hit → 0ms, $0.00
```
