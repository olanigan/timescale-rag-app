# Claude Development Guide - pgvector-app

## Project Overview
This is a high-performance RAG (Retrieval-Augmented Generation) solution built with PostgreSQL's pgvectorscale extension and Python. The application demonstrates advanced vector search capabilities with hybrid search functionality, combining semantic search with intelligent answer generation.

### Core Purpose
- Vector embedding and storage using PostgreSQL with pgvectorscale
- Semantic similarity search with cosine distance
- RAG-based question answering with context synthesis
- Multi-provider LLM support (OpenAI, Anthropic)
- Advanced filtering capabilities (metadata, predicates, time-based)

## Technology Stack

### Core Dependencies
- **Database**: PostgreSQL with pgvectorscale extension (via TimescaleDB)
- **Vector Operations**: timescale-vector library
- **LLM Integration**: OpenAI (primary), Anthropic (secondary)
- **Data Processing**: pandas for data manipulation
- **Configuration**: pydantic for settings management
- **Environment**: python-dotenv for configuration
- **Structured Outputs**: instructor for LLM response parsing

### Development Environment
- **Python**: 3.7+
- **Docker**: Docker Compose for database setup
- **Database GUI**: TablePlus or similar PostgreSQL client recommended

## Architecture Patterns

### Design Principles
1. **Separation of Concerns**: Clear separation between data layer, services, and configuration
2. **Factory Pattern**: LLMFactory for multi-provider LLM support
3. **Settings Management**: Centralized configuration with environment variable support
4. **Structured Responses**: Pydantic models for type-safe data handling
5. **Logging**: Comprehensive logging throughout the application

### Key Components
- `VectorStore`: Core database operations and vector search
- `LLMFactory`: Multi-provider LLM client management
- `Synthesizer`: RAG response generation with structured outputs
- `Settings`: Centralized configuration management

## Development Commands

### Environment Setup
```bash
# 1. Copy environment template
cp app/example.env .env
# Edit .env file to add your OpenAI API key

# 2. Start database
cd docker && docker compose up -d

# 3. Install dependencies  
pip install -r requirements.txt

# 4. Initialize data
cd app && python insert_vectors.py

# 5. Test search
python similarity_search.py
```

### Database Operations
```bash
# Connect to database (using TablePlus or similar)
# Host: localhost, Port: 5432, User: postgres, Password: password, Database: postgres

# The application will automatically:
# - Create tables via vec.create_tables()
# - Create DiskANN index via vec.create_index()
# - Handle vector operations through timescale-vector client
```

## Configuration Management

### Environment Variables
Required in `.env` file:
- `OPENAI_API_KEY`: OpenAI API key for embeddings and LLM
- `TIMESCALE_SERVICE_URL`: PostgreSQL connection string (default provided)

### Settings Structure
- `OpenAISettings`: API configuration and model selection
- `DatabaseSettings`: Database connection parameters
- `VectorStoreSettings`: Table name, dimensions, partitioning
- `Settings`: Main configuration aggregator

## Key Implementation Patterns

### Vector Operations
- **Embedding Model**: text-embedding-3-small (1536 dimensions)
- **Similarity Metric**: Cosine distance (lower = more similar)
- **Indexing**: DiskANN-inspired index for performance
- **Time Partitioning**: UUID v1 with time-based partitioning

### Search Capabilities
- **Basic Search**: Simple text-to-vector similarity
- **Metadata Filtering**: Dictionary-based equality filters
- **Predicate Filtering**: Complex logical conditions (>, <, ==, !=, &, |)
- **Time-based Filtering**: Date range queries using UUID timestamps
- **Hybrid Results**: Structured DataFrame output with metadata expansion

### LLM Integration
- **Multi-Provider Support**: OpenAI (primary), Anthropic (secondary)
- **Structured Outputs**: instructor library for type-safe responses
- **Error Handling**: Retry logic and comprehensive error management
- **Response Models**: Pydantic models for consistent output structure

## Development Guidelines

### Code Style
- Use type hints throughout
- Follow pydantic patterns for configuration
- Implement comprehensive logging
- Use pandas for data manipulation
- Structure responses with pydantic BaseModel

### Testing Approach
- Test vector operations with sample data
- Verify search functionality across different filter types
- Test LLM integration with multiple providers
- Validate configuration loading

### Common Operations
```python
# Initialize vector store
vec = VectorStore()

# Basic search
results = vec.search("What are shipping options?", limit=3)

# Filtered search
results = vec.search(
    "shipping question",
    metadata_filter={"category": "Shipping"}
)

# Predicate search
predicates = client.Predicates("category", "==", "Shipping")
results = vec.search("question", predicates=predicates)

# Generate response
response = Synthesizer.generate_response(
    question="user question",
    context=search_results
)
```

### Performance Considerations
- Use DiskANN index for large datasets (10k+ vectors)
- Consider batch operations for bulk insertions
- Monitor embedding generation costs and latency
- Implement proper connection pooling for production

## Troubleshooting

### Common Issues
1. **Database Connection**: Ensure Docker container is running
2. **API Keys**: Verify OpenAI API key in .env file
3. **Dependencies**: Check all packages installed from requirements.txt
4. **Index Creation**: May take time for large datasets

### Debugging
- Check logs for embedding generation timing
- Verify search results with distance scores
- Test with known FAQ dataset entries
- Use database GUI to inspect stored vectors

## Extension Points
- Add more LLM providers via LLMFactory
- Implement different embedding models
- Add more sophisticated filtering logic
- Enhance response synthesis with additional context
- Implement caching for frequent queries

## Security Notes
- Keep API keys in environment variables only
- Use proper database credentials in production
- Implement rate limiting for API calls
- Consider data privacy for stored embeddings