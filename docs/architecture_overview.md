# Architecture Overview - pgvector-app

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          RAG System Architecture                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────┐ │
│  │   Data      │    │   Vector     │    │     Response        │ │
│  │ Ingestion   │───▶│   Search     │───▶│   Generation        │ │
│  │             │    │              │    │                     │ │
│  └─────────────┘    └──────────────┘    └─────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

    ▲                        ▲                        ▲
    │                        │                        │
    ▼                        ▼                        ▼

┌──────────┐        ┌─────────────────┐        ┌─────────────┐
│ CSV Data │        │  PostgreSQL +   │        │ OpenAI GPT  │
│ (FAQ)    │        │ pgvectorscale   │        │ Anthropic   │
└──────────┘        └─────────────────┘        └─────────────┘
```

## Component Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                      Application Layer                           │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ insert_vectors  │  │similarity_search│  │    Example      │   │
│  │     .py         │  │      .py        │  │   Scripts       │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                                                                   │
├───────────────────────────────────────────────────────────────────┤
│                      Service Layer                               │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │  VectorStore    │  │  Synthesizer    │  │  LLMFactory     │   │
│  │    (Core)       │  │   (RAG Logic)   │  │(Multi-Provider) │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│                                                                   │
├───────────────────────────────────────────────────────────────────┤
│                    Configuration Layer                           │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐                        │
│  │   Settings      │  │  Environment    │                        │
│  │  (Pydantic)     │  │   Variables     │                        │
│  └─────────────────┘  └─────────────────┘                        │
│                                                                   │
├───────────────────────────────────────────────────────────────────┤
│                      Data Layer                                  │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐                        │
│  │  PostgreSQL     │  │   CSV Data      │                        │
│  │ + pgvectorscale │  │  (Source)       │                        │
│  └─────────────────┘  └─────────────────┘                        │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

```
┌─────────────┐
│ CSV Dataset │
│ (FAQ Data)  │
└──────┬──────┘
       │
       ▼ read_csv()
┌─────────────┐
│  DataFrame  │
│ Processing  │
└──────┬──────┘
       │
       ▼ prepare_record()
┌─────────────┐      ┌──────────────┐
│   OpenAI    │◀────▶│ Embedding    │
│ Embeddings  │      │ Generation   │
└─────────────┘      └──────┬───────┘
                            │
                            ▼ vector + metadata
                     ┌─────────────┐
                     │ PostgreSQL  │
                     │ Vector DB   │
                     └──────┬──────┘
                            │
                            ▼ similarity_search()
                     ┌─────────────┐
                     │   Vector    │
                     │   Search    │
                     └──────┬──────┘
                            │
                            ▼ context + question
                     ┌─────────────┐      ┌──────────────┐
                     │ Synthesizer │◀────▶│     LLM      │
                     │ (RAG Logic) │      │ (GPT/Claude) │
                     └──────┬──────┘      └──────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ Structured  │
                     │ Response    │
                     └─────────────┘
```

## Technology Stack Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   OpenAI    │  │  Anthropic  │  │  TimescaleDB │            │
│  │    API      │  │     API     │  │   (Docker)   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    Python Libraries                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ timescale-  │  │   pandas    │  │  pydantic   │            │
│  │   vector    │  │  (data)     │  │ (config)    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ instructor  │  │  psycopg    │  │ python-     │            │
│  │(structured) │  │(postgres)   │  │  dotenv     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Database Schema Architecture

```
PostgreSQL Database: postgres
├── Extensions
│   ├── vector (pgvector)
│   ├── timescale (TimescaleDB)
│   └── vectorscale (pgvectorscale)
│
└── Table: embeddings
    ├── id (UUID v1 - time-ordered)
    ├── metadata (JSONB)
    │   ├── category (string)
    │   └── created_at (ISO timestamp)
    ├── contents (TEXT) - original Q&A text
    ├── embedding (vector[1536]) - OpenAI embedding
    └── Indexes
        ├── DiskANN Index (vectorscale)
        └── Time-based partitioning (7-day intervals)
```

## Search & Retrieval Architecture

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼ get_embedding()
┌─────────────┐
│ Query Vector│
│ (1536-dim)  │
└──────┬──────┘
       │
       ▼ vector search
┌─────────────────────────────────────┐
│          Search Options             │
├─────────────────────────────────────┤
│ • Basic Similarity (cosine)         │
│ • Metadata Filtering (dict)         │
│ • Predicate Filtering (complex)     │
│ • Time-based Filtering (UUID)       │
│ • Hybrid Combinations               │
└──────┬──────────────────────────────┘
       │
       ▼ ranked results
┌─────────────┐
│ Search      │
│ Results     │
│ (DataFrame) │
└──────┬──────┘
       │
       ▼ context formatting
┌─────────────┐
│ Structured  │
│ Context     │
└─────────────┘
```

## Response Generation Architecture  

```
┌─────────────┐    ┌─────────────┐
│ User Query  │    │ Search      │
│             │    │ Results     │
└──────┬──────┘    └──────┬──────┘
       │                  │
       └─────────┬────────┘
                 │
                 ▼ combine
         ┌─────────────┐
         │  Messages   │
         │  Array      │
         └──────┬──────┘
                │
                ▼ LLMFactory
         ┌─────────────────┐
         │   Multi-LLM     │
         │   Provider      │
         │ ┌─────────────┐ │
         │ │   OpenAI    │ │
         │ │   (primary) │ │
         │ └─────────────┘ │
         │ ┌─────────────┐ │
         │ │  Anthropic  │ │
         │ │ (secondary) │ │
         │ └─────────────┘ │
         └──────┬──────────┘
                │
                ▼ instructor
         ┌─────────────┐
         │ Structured  │
         │ Response    │
         │ (Pydantic)  │
         └─────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Development Environment                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Docker    │  │   Python    │  │    Configuration        │  │
│  │ Container   │  │ Application │  │                         │  │
│  │             │  │             │  │  ┌─────────────────────┐ │  │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │  │       .env          │ │  │
│  │ │TimescaleDB│ │  │   App   │ │  │  │   OPENAI_API_KEY    │ │  │
│  │ │PostgreSQL │ │  │ Scripts │ │  │  │ TIMESCALE_SERVICE   │ │  │
│  │ │pgvectorscale│ │  │       │ │  │  │       _URL          │ │  │
│  │ └─────────┘ │  │ └─────────┘ │  │  └─────────────────────┘ │  │
│  │             │  │             │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                                                                 │
│       Port: 5432         Local Scripts          Environment     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Performance Considerations

### Index Strategy
- **DiskANN Index**: Optimized for large-scale vector similarity search
- **Time Partitioning**: 7-day intervals for time-based queries  
- **Metadata Indexing**: Automatic JSONB indexing for filters

### Scaling Points
- **Vector Dimensions**: Fixed at 1536 (OpenAI text-embedding-3-small)
- **Index Performance**: Significant improvements with 10k+ vectors
- **Memory Usage**: Managed by PostgreSQL buffer pools
- **API Rate Limits**: OpenAI embedding generation throttling

### Optimization Strategies
- Batch embedding generation for bulk operations
- Connection pooling for production deployments
- Caching strategies for frequent queries
- Index warm-up for consistent performance