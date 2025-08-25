# Data Flow Analysis - pgvector-app

## End-to-End Data Flow

### Complete RAG Pipeline

```
┌─────────────┐
│ CSV Source  │ (FAQ Dataset)
│ question;   │
│ answer;     │
│ category    │
└──────┬──────┘
       │ pd.read_csv()
       ▼
┌─────────────┐
│ DataFrame   │ (Raw Data)
│ Processing  │
└──────┬──────┘
       │ apply(prepare_record)
       ▼
┌─────────────┐      ┌──────────────┐
│ Record      │◄────►│   OpenAI     │
│ Preparation │      │ Embeddings   │
│             │      │ text-embed-  │
│ UUID        │      │ 3-small      │
│ Metadata    │      │ (1536-dim)   │
│ Contents    │      └──────────────┘
└──────┬──────┘
       │ vec.upsert()
       ▼
┌─────────────────────────────────┐
│        PostgreSQL               │
│      + pgvectorscale            │
│                                 │
│ Table: embeddings               │
│ ├── id (UUID v1)               │
│ ├── metadata (JSONB)           │
│ ├── contents (TEXT)            │
│ └── embedding (vector[1536])   │
│                                 │
│ Indexes:                       │
│ └── DiskANN (vectorscale)      │
└─────────────┬───────────────────┘
              │ vec.search()
              ▼
       ┌─────────────┐
       │   Vector    │
       │   Search    │
       │ (Similarity)│
       └──────┬──────┘
              │ cosine distance
              ▼
       ┌─────────────┐
       │ Search      │
       │ Results     │
       │ (DataFrame) │
       └──────┬──────┘
              │ context formatting
              ▼
       ┌─────────────┐      ┌──────────────┐
       │ Synthesizer │◄────►│    LLM       │
       │ (RAG Logic) │      │ (GPT-4o)     │
       └──────┬──────┘      └──────────────┘
              │ structured response
              ▼
       ┌─────────────┐
       │ Final       │
       │ Response    │
       │ (Pydantic)  │
       └─────────────┘
```

## Data Ingestion Flow (insert_vectors.py)

### Step-by-Step Process

```
1. CSV Loading:
┌─────────────────────────────────┐
│ pd.read_csv("faq_dataset.csv")  │
│ separator: ";"                  │
│ columns: [question, answer,     │
│           category]             │
└─────────────┬───────────────────┘
              │
              ▼
2. Record Preparation:
┌─────────────────────────────────┐
│ def prepare_record(row):        │
│   content = f"Question: {q}     │
│             Answer: {a}"        │
│   embedding = get_embedding()   │
│   return {                      │
│     id: UUID v1,               │
│     metadata: {...},           │
│     contents: content,         │
│     embedding: vector          │
│   }                            │
└─────────────┬───────────────────┘
              │
              ▼
3. Embedding Generation:
┌─────────────────────────────────┐
│ OpenAI API Call:               │
│ - model: text-embedding-3-small │
│ - input: processed text        │
│ - output: 1536-dim vector      │
│ - timing: logged per call      │
└─────────────┬───────────────────┘
              │
              ▼
4. Database Storage:
┌─────────────────────────────────┐
│ TimescaleVector Operations:    │
│ 1. vec.create_tables()         │
│ 2. vec.create_index()          │
│ 3. vec.upsert(records_df)      │
└─────────────────────────────────┘
```

### Data Transformation Details

#### Raw CSV Format
```
question;answer;category
"What are your shipping options?";"We offer standard...";"Shipping"
```

#### Processed Record Format
```python
{
    "id": "8ab544ae-766a-11ef-81cb-decf757b836d",  # UUID v1 with timestamp
    "metadata": {
        "category": "Shipping",
        "created_at": "2024-09-15T10:30:00"
    },
    "contents": "Question: What are your shipping options?\nAnswer: We offer standard (3-5 business days) and express (1-2 business days) shipping options.",
    "embedding": [0.1234, -0.5678, ...] # 1536 dimensions
}
```

#### Database Schema Mapping
```sql
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    metadata JSONB,
    contents TEXT,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Search Flow (similarity_search.py)

### Query Processing Pipeline

```
1. Query Input:
┌─────────────────────────────────┐
│ user_query = "shipping options" │
└─────────────┬───────────────────┘
              │
              ▼
2. Query Embedding:
┌─────────────────────────────────┐
│ query_vector = vec.get_embedding│
│ (user_query)                   │
│ - Same model as ingestion      │
│ - 1536-dimensional output      │
└─────────────┬───────────────────┘
              │
              ▼
3. Vector Search:
┌─────────────────────────────────┐
│ results = vec.search(           │
│   query_text,                  │
│   limit=5,                     │
│   filters=...,                 │
│   predicates=...               │
│ )                              │
└─────────────┬───────────────────┘
              │
              ▼
4. Result Processing:
┌─────────────────────────────────┐
│ DataFrame with columns:        │
│ - id, content, embedding,      │
│ - distance, category,          │
│ - created_at                   │
└─────────────────────────────────┘
```

### Search Filtering Options

#### Basic Search
```python
results = vec.search("What are shipping options?", limit=3)
# Pure vector similarity, no filters
```

#### Metadata Filtering
```python
metadata_filter = {"category": "Shipping"}
results = vec.search(query, metadata_filter=metadata_filter)
# Equality-based filtering on JSONB fields
```

#### Predicate Filtering  
```python
# Single predicate
predicates = client.Predicates("category", "==", "Shipping")

# Complex predicates
predicates = (
    client.Predicates("category", "==", "Electronics") & 
    client.Predicates("price", "<", 1000)
) | client.Predicates("category", "==", "Books")

results = vec.search(query, predicates=predicates)
```

#### Time-based Filtering
```python
time_range = (datetime(2024, 9, 1), datetime(2024, 9, 30))
results = vec.search(query, time_range=time_range)
# Uses UUID v1 timestamp component for filtering
```

## Response Generation Flow

### RAG Synthesis Process

```
1. Context Preparation:
┌─────────────────────────────────┐
│ search_results (DataFrame)     │
│     ↓                          │
│ dataframe_to_json()            │
│     ↓                          │
│ JSON context string            │
└─────────────┬───────────────────┘
              │
              ▼
2. Message Construction:
┌─────────────────────────────────┐
│ messages = [                   │
│   {role: "system",             │
│    content: SYSTEM_PROMPT},    │
│   {role: "user",               │
│    content: user_question},    │
│   {role: "assistant",          │
│    content: context}           │
│ ]                              │
└─────────────┬───────────────────┘
              │
              ▼
3. LLM Processing:
┌─────────────────────────────────┐
│ LLMFactory("openai")           │
│     ↓                          │
│ instructor integration         │
│     ↓                          │
│ structured completion          │
└─────────────┬───────────────────┘
              │
              ▼
4. Response Validation:
┌─────────────────────────────────┐
│ SynthesizedResponse:           │
│ - thought_process: List[str]   │
│ - answer: str                  │
│ - enough_context: bool         │
└─────────────────────────────────┘
```

### Context Processing Details

#### Search Results Format
```python
# Raw search results (List of tuples)
[
    ("uuid1", {"category": "Shipping"}, "Question: ...", [0.1, 0.2, ...], 0.234),
    ("uuid2", {"category": "Shipping"}, "Question: ...", [0.3, 0.4, ...], 0.456),
]

# Processed DataFrame
   id        content                    category  distance
0  uuid1     Question: ...Answer: ...   Shipping  0.234
1  uuid2     Question: ...Answer: ...   Shipping  0.456

# Context JSON for LLM
[
  {
    "content": "Question: What are shipping options?\nAnswer: We offer standard...",
    "category": "Shipping"
  },
  {
    "content": "Question: How can I track my order?\nAnswer: You can track...",  
    "category": "Order Management"
  }
]
```

## State Management Patterns

### Configuration State
```python
# Singleton pattern with caching
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Used throughout application
settings = get_settings()  # Always same instance
```

### Database Connection State
```python
# Per-instance connection management
class VectorStore:
    def __init__(self):
        self.vec_client = client.Sync(
            service_url,
            table_name,
            embedding_dimensions
        )
        # Connection persists for instance lifetime
```

### LLM Client State  
```python
# Factory-managed client instances
class LLMFactory:
    def __init__(self, provider):
        self.client = self._initialize_client()
        # Provider-specific client cached in instance
```

## Data Flow Performance Characteristics

### Embedding Generation
- **Latency**: ~50-200ms per text (network dependent)
- **Throughput**: Rate-limited by OpenAI API
- **Caching**: No caching implemented (stateless)
- **Optimization**: Batch processing in insert_vectors.py

### Vector Search  
- **Latency**: <10ms for most queries (with index)
- **Throughput**: High (PostgreSQL optimized)
- **Scaling**: DiskANN index performance improves with dataset size
- **Memory**: Managed by PostgreSQL buffer pools

### Response Generation
- **Latency**: ~1-5s depending on LLM provider and complexity
- **Throughput**: Limited by LLM API rate limits
- **Context Size**: Limited by token windows
- **Structure**: Guaranteed via instructor validation

## Error Handling Patterns

### Database Operations
```python
try:
    self.vec_client.upsert(records)
    logging.info(f"Inserted {len(records)} records")
except Exception as e:
    logging.error(f"Upsert failed: {e}")
    raise
```

### API Integration
```python  
# Built into LLMFactory
completion_params = {
    "max_retries": self.settings.max_retries,
    # ... other params
}
# instructor handles OpenAI API retries
```

### Validation Errors
```python
# Pydantic automatic validation
class SynthesizedResponse(BaseModel):
    answer: str = Field(description="...")
    # Raises ValidationError if invalid
```

## Data Persistence Patterns

### Vector Storage
- **Strategy**: Immediate persistence via TimescaleVector
- **Durability**: PostgreSQL ACID compliance  
- **Backup**: Standard PostgreSQL backup procedures
- **Partitioning**: Time-based partitioning (7-day intervals)

### Configuration Persistence
- **Strategy**: Environment variables + .env files
- **Runtime**: In-memory caching with @lru_cache
- **Changes**: Require application restart

### Temporary Data
- **DataFrames**: In-memory processing only
- **Search Results**: Not cached (stateless operations)
- **LLM Responses**: Immediate consumption, not stored