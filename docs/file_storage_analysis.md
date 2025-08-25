# File Storage Analysis - pgvector-app

## Storage Architecture Overview

This RAG application implements a **hybrid storage strategy** combining file-based data sources with PostgreSQL vector storage. The system handles different types of data persistence for various purposes.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Storage Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────┐ │
│  │  File       │    │  Database    │    │   Configuration     │ │
│  │ Storage     │───▶│   Storage    │◄──►│     Storage         │ │
│  │ (CSV)       │    │(PostgreSQL)  │    │   (.env files)      │ │
│  │             │    │              │    │                     │ │
│  └─────────────┘    └──────────────┘    └─────────────────────┘ │
│                                                                 │
│      Source Data       Vector Storage        Runtime Config    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Storage Components Analysis

### 1. Source Data Storage (File-Based)

#### CSV Data Storage
**Location**: `data/faq_dataset.csv`

**Purpose**: Source dataset for FAQ content ingestion

**Format Analysis**:
```csv
question;answer;category
"What are your shipping options?";"We offer standard...;"Shipping"
"How can I track my order?";"You can track...;"Order Management" 
```

**Storage Characteristics**:
- **Format**: Semicolon-separated values (CSV with ; delimiter)
- **Encoding**: UTF-8 (inferred)
- **Size**: Small dataset (~10 entries for demonstration)
- **Structure**: Structured with consistent schema
- **Persistence**: Static file, manually maintained

**Access Pattern**:
```python
# Read-only access during ingestion
df = pd.read_csv("../data/faq_dataset.csv", sep=";")
```

**Storage Considerations**:
- **Scalability**: Limited by file system and memory constraints
- **Concurrency**: Single-reader access pattern
- **Backup**: File system backup required
- **Version Control**: Tracked in git repository

### 2. Vector Database Storage

#### PostgreSQL with pgvectorscale
**Location**: Docker container with persistent volume

**Storage Architecture**:
```
Docker Container: timescaledb
├── PostgreSQL Database: postgres
│   ├── Extensions:
│   │   ├── vector (pgvector)
│   │   ├── timescale (TimescaleDB)
│   │   └── vectorscale (pgvectorscale)
│   └── Tables:
│       └── embeddings
│           ├── Data Storage
│           │   ├── id (UUID) - 16 bytes
│           │   ├── metadata (JSONB) - variable
│           │   ├── contents (TEXT) - variable  
│           │   └── embedding (vector[1536]) - ~6KB
│           └── Indexes
│               ├── DiskANN Index (vectorscale)
│               └── Time-based partitioning
└── Persistent Volume: timescaledb_data
```

**Storage Specifications**:
- **Vector Dimensions**: 1536 (OpenAI text-embedding-3-small)
- **Vector Storage**: ~6KB per embedding (1536 * 4 bytes float32)
- **Metadata Storage**: JSONB with category and timestamp
- **Content Storage**: Full text of questions and answers
- **Indexing**: DiskANN for vector similarity search

**Volume Configuration**:
```yaml
# docker/docker-compose.yml
volumes:
  - timescaledb_data:/var/lib/postgresql/data

volumes:
  timescaledb_data:
    # Docker managed volume for persistence
```

#### Database Schema Details
```sql
-- Table structure (inferred)
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    metadata JSONB,
    contents TEXT,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Partitioning strategy
SELECT create_hypertable('embeddings', 'created_at', 
                        chunk_time_interval => INTERVAL '7 days');

-- Vector index for similarity search  
CREATE INDEX ON embeddings USING diskann (embedding vector_cosine_ops);
```

### 3. Configuration Storage

#### Environment Variables
**Location**: `.env` file (not tracked in git)

**Storage Pattern**:
```bash
# .env structure
OPENAI_API_KEY=sk-proj-...
TIMESCALE_SERVICE_URL=postgres://postgres:password@localhost:5432/postgres
```

**Access Pattern**:
```python
# Runtime loading via python-dotenv
load_dotenv(dotenv_path="./.env")
api_key = os.getenv("OPENAI_API_KEY")
```

**Security Considerations**:
- **File Permissions**: Should be readable only by application user
- **Version Control**: Excluded via .gitignore
- **Template**: `example.env` provides structure without secrets

#### Application Configuration
**Location**: In-memory via pydantic Settings

**Pattern**:
```python
@lru_cache()
def get_settings() -> Settings:
    return Settings()
    
# Cached singleton pattern prevents repeated file reads
```

## Data Flow and Storage Interactions

### Ingestion Pipeline Storage Flow

```
┌─────────────┐
│ CSV File    │ (data/faq_dataset.csv)
│ (Static)    │
└──────┬──────┘
       │ pd.read_csv()
       ▼
┌─────────────┐
│ DataFrame   │ (In-Memory)
│ (Temporary) │
└──────┬──────┘
       │ apply(prepare_record)
       ▼
┌─────────────┐      ┌──────────────┐
│ Record DF   │◄────►│   OpenAI     │ (External API)
│(In-Memory)  │      │  Embedding   │
└──────┬──────┘      │   Service    │
       │             └──────────────┘
       ▼ vec.upsert()
┌─────────────────────────────────┐
│      PostgreSQL Storage         │
│                                 │
│ ┌─────────────────────────────┐ │
│ │     embeddings table        │ │
│ │ ┌─────┬─────────┬─────────┐ │ │
│ │ │ id  │metadata │embedding│ │ │ 
│ │ │ ... │ ...     │ ...     │ │ │
│ │ └─────┴─────────┴─────────┘ │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │       DiskANN Index         │ │
│ │   (Vector Similarity)       │ │
│ └─────────────────────────────┘ │
│                                 │
│ ┌─────────────────────────────┐ │
│ │   Time-based Partitions     │ │
│ │     (7-day intervals)       │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
           │
           ▼
    ┌─────────────┐
    │  Docker     │
    │ Persistent  │
    │  Volume     │
    └─────────────┘
```

### Query Pipeline Storage Flow

```
┌─────────────┐
│ User Query  │ (Runtime String)
└──────┬──────┘
       │ get_embedding()
       ▼
┌─────────────┐      ┌──────────────┐
│ Query       │◄────►│   OpenAI     │ (External API)
│ Vector      │      │  Embedding   │
│(In-Memory)  │      │   Service    │
└──────┬──────┘      └──────────────┘
       │ vec.search()
       ▼
┌─────────────────────────────────┐
│     PostgreSQL Query            │
│                                 │
│ ┌─────────────────────────────┐ │
│ │   Vector Similarity Search  │ │
│ │     (DiskANN Index)         │ │
│ └─────────────────────────────┘ │
│              │                  │
│              ▼                  │
│ ┌─────────────────────────────┐ │
│ │    Result Set               │ │
│ │ (id, metadata, content,     │ │
│ │  embedding, distance)       │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
           │
           ▼
    ┌─────────────┐
    │ DataFrame   │ (In-Memory)
    │ (Results)   │
    └─────────────┘
```

## Storage Performance Analysis

### Vector Storage Performance

#### Storage Requirements
```
Per record storage calculation:
- UUID: 16 bytes
- JSONB metadata: ~100-500 bytes (varies by content)
- Contents (TEXT): ~100-2000 bytes (varies by Q&A length)
- Embedding vector: 1536 * 4 = 6144 bytes (float32)
- Total per record: ~6.5-8.5KB

For 1M records: ~6.5-8.5GB
```

#### Index Performance
- **DiskANN Index**: Optimized for large-scale similarity search
- **Build Time**: Increases with dataset size, one-time cost
- **Query Performance**: Sub-10ms for most similarity searches
- **Memory Usage**: Index cached in PostgreSQL shared buffers

#### Time Partitioning Benefits
- **Query Performance**: Time-based filtering very fast
- **Maintenance**: Easier partition pruning and archival
- **Storage**: Automated partition management
- **Backup**: Granular backup strategies possible

### File Storage Performance

#### CSV Reading Performance
```python
# Performance characteristics
df = pd.read_csv("../data/faq_dataset.csv", sep=";")
# - File size dependent (linear read time)
# - Memory usage: ~2x file size during processing
# - Single-threaded CSV parsing
```

#### Scaling Considerations
- **Small datasets**: Excellent performance (<1MB)
- **Medium datasets**: Good performance (1-100MB) 
- **Large datasets**: Consider chunked reading or database import

### Configuration Storage Performance

#### Environment Variable Loading
```python
# One-time cost at application startup
load_dotenv(dotenv_path="./.env")  # ~1ms for typical .env file

# Cached settings pattern eliminates repeated reads
@lru_cache()
def get_settings():  # Subsequent calls are ~0.001ms
```

## Storage Patterns and Best Practices

### 1. Data Persistence Patterns

#### Immutable Source Data
```python
# CSV files treated as immutable source of truth
# Changes require manual file updates and re-ingestion
df = pd.read_csv("../data/faq_dataset.csv", sep=";")
```

#### Append-Only Vector Storage
```python
# Vector storage designed for append/upsert operations
vec.upsert(records_df)  # Handles both inserts and updates
```

#### Configuration as Code
```python
# Settings defined in code with environment overrides
class OpenAISettings(LLMSettings):
    default_model: str = Field(default="gpt-4o")  # Code default
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))  # Env override
```

### 2. Storage Security Patterns

#### Sensitive Data Isolation
```
Sensitive:     .env files (not in git)
Non-sensitive: Code configuration (in git)
Mixed:         Database (contains embeddings + API keys for connection)
```

#### Backup Strategies
```yaml
# Database backup via Docker volumes
docker run --rm -v timescaledb_data:/data -v $(pwd):/backup \
    alpine tar czf /backup/db-backup.tar.gz -C /data .

# Configuration backup (exclude secrets)
# Track example.env in git, not actual .env
```

### 3. Storage Optimization Patterns

#### Lazy Loading
```python
# Settings loaded on first access, cached thereafter
@lru_cache()
def get_settings() -> Settings:
    return Settings()  # Expensive operations cached
```

#### Batch Operations
```python
# Bulk operations preferred over individual inserts
records_df = df.apply(prepare_record, axis=1)
vec.upsert(records_df)  # Single batch operation
```

#### Index Strategy
```python  
# Index creation after bulk loading
vec.create_tables()
vec.create_index()  # DiskANN index created after data load
vec.upsert(records_df)
```

## Storage Monitoring and Maintenance

### Database Storage Monitoring

#### Disk Usage Queries
```sql
-- Monitor table size
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE tablename = 'embeddings';

-- Monitor index usage
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexname)) as size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE relname = 'embeddings';
```

#### Performance Monitoring
```sql
-- Query performance statistics
SELECT 
    query,
    mean_time,
    calls,
    total_time
FROM pg_stat_statements 
WHERE query LIKE '%embedding%'
ORDER BY mean_time DESC;
```

### File System Monitoring
```bash
# Monitor CSV file changes
ls -la data/faq_dataset.csv

# Monitor .env file permissions  
ls -la .env
# Should show: -rw------- (600 permissions)
```

## Storage Scaling Strategies

### Vertical Scaling
```yaml
# Increase database resources
services:
  timescaledb:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
```

### Horizontal Scaling Considerations

#### Read Replicas
```yaml
# Future: Read replica for query workloads
services:
  timescaledb-read:
    image: timescale/timescaledb-ha:pg16
    environment:
      - POSTGRES_MASTER_SERVICE=timescaledb
```

#### Sharding Strategies
```python
# Potential sharding by category or time
class VectorStoreSharded:
    def __init__(self, shard_key: str):
        self.shard_key = shard_key
        self.clients = {}  # Multiple database connections
```

### Storage Archival Strategies

#### Time-based Archival
```sql
-- Archive old partitions
SELECT drop_chunks('embeddings', INTERVAL '90 days');

-- Export to cold storage
COPY (SELECT * FROM embeddings 
      WHERE created_at < NOW() - INTERVAL '1 year') 
TO '/backup/old_embeddings.csv' CSV HEADER;
```

## Storage Extension Points

### Alternative Source Formats
```python
# Future support for additional formats
def load_data(source_type: str, path: str) -> pd.DataFrame:
    if source_type == "csv":
        return pd.read_csv(path, sep=";")
    elif source_type == "json":
        return pd.read_json(path)
    elif source_type == "parquet":
        return pd.read_parquet(path)
```

### Cloud Storage Integration
```python
# Future cloud storage support
class CloudStorageSettings(BaseModel):
    provider: str = "s3"  # s3, gcs, azure
    bucket: str = Field(default_factory=lambda: os.getenv("STORAGE_BUCKET"))
    credentials: str = Field(default_factory=lambda: os.getenv("CLOUD_CREDENTIALS"))
```

### Distributed Vector Storage
```python
# Future distributed storage support
class DistributedVectorStore:
    def __init__(self, nodes: List[str]):
        self.nodes = nodes
        self.clients = [client.Sync(node) for node in nodes]
    
    def search(self, query: str) -> List[Result]:
        # Distributed search across nodes
        pass
```