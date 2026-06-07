# RAG Cheat Sheet

## Pipeline Overview

```
Documents → Load → Chunk → Embed → Store → Retrieve → Generate
```

## This Kit's Implementation

| Step | File | Function |
|------|------|----------|
| Load | `services/rag_service.py` | `load_documents()` |
| Chunk | `services/rag_service.py` | `chunk_text()` |
| Embed | `services/llm_provider.py` | `provider.embed()` |
| Index | `services/rag_service.py` | `index_documents()` |
| Retrieve | `services/rag_service.py` | `retrieve()` |
| Generate | `services/rag_service.py` | `generate_answer()` |

## API Usage

```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Monad?", "top_k": 4}'
```

## Add Your Documents

1. Put `.md` or `.txt` files in `datasets/`
2. Update `load_documents()` to read your file
3. Restart backend (auto-indexes on startup)

## Chunk Size Guidelines

| Content Type | chunk_size | overlap |
|--------------|------------|---------|
| Code docs | 500-800 | 100 |
| General text | 1000 | 200 |
| Long articles | 1500 | 300 |

## Improve Retrieval

- Add metadata filters (topic, source)
- Use hybrid search (keyword + semantic)
- Re-rank top results with cross-encoder
- Swap in ChromaDB (already in requirements.txt)

## Prompt for Generation

```
Answer using ONLY the provided context.
If unsure, say "I don't know."
Context: {retrieved_chunks}
Question: {user_question}
```

## Hackathon Speed Tips

- Start with 3-5 curated docs in `datasets/`
- Mock embeddings work without API key
- Show sources in UI for judge credibility
