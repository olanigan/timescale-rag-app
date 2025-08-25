# Streamlit RAG Showcase

Interactive web application demonstrating the pgvector-app RAG solution with real-time vector search, database exploration, and AI response generation.

## Features

### 📊 Dataset Explorer
- Live PostgreSQL database connection
- Table schema visualization
- Sample data preview
- Database statistics and metrics

### 🔍 Vector Search
- Interactive semantic search
- Multiple filter types (basic, metadata, predicate, time-based)
- Real-time similarity scoring
- Search result visualization

### 🤖 RAG Pipeline
- Step-by-step pipeline demonstration
- Query processing and embedding generation
- Context retrieval with vector search
- AI response generation with timing
- Performance metrics and visualization

### ⚙️ Configuration
- API key management (OpenAI, Anthropic)
- Model selection and settings
- Database connection configuration
- Advanced performance tuning

### 📈 Analytics Dashboard
- System performance metrics
- Usage trends and patterns
- Search analytics and quality metrics
- System health monitoring

## Architecture

```
streamlit_app/
├── app.py                 # Main navigation hub
├── pages/                 # Streamlit page modules
│   ├── 01_📊_Dataset_Explorer.py
│   ├── 02_🔍_Vector_Search.py
│   ├── 03_🤖_RAG_Pipeline.py
│   ├── 04_⚙️_Configuration.py
│   └── 05_📈_Analytics.py
└── components/            # Reusable UI components
    ├── database_viewer.py
    ├── search_interface.py
    ├── rag_demo.py
    └── metrics_dashboard.py
```

## Setup Instructions

### Prerequisites
1. **PostgreSQL with pgvectorscale**: Ensure Docker container is running
2. **Python Environment**: Python 3.7+ with required dependencies
3. **API Keys**: OpenAI and/or Anthropic API keys in `.env` file

### Installation

1. **Install Dependencies**
   ```bash
   cd /path/to/rag-bench/pgvector-app
   python3 -m pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   # Ensure Docker container is running
   cd docker && docker compose up -d

   # Initialize data (if not already done)
   cd app && python insert_vectors.py
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment template
   cp app/example.env .env

   # Edit .env file with your API keys
   # OPENAI_API_KEY=your_openai_key_here
   # ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

### Running the Application

1. **Start the Streamlit App**
   ```bash
   cd streamlit_app
   python3 -m streamlit run app.py
   ```

2. **Access the Application**
   - Open browser to `http://localhost:8501`
   - Navigate through the different sections using the sidebar

## Usage Guide

### Navigation
- Use the numbered pages in the sidebar for different features
- Each page is self-contained with its own functionality
- Connection status is shown in the sidebar

### Key Workflows

1. **Explore Data**: Start with Dataset Explorer to understand the data structure
2. **Test Search**: Use Vector Search to experiment with different query types
3. **Run RAG Pipeline**: Experience the complete RAG process step-by-step
4. **Monitor Performance**: Check Analytics for system metrics and usage patterns
5. **Configure Settings**: Adjust API keys and model preferences in Configuration

### Performance Tips
- Vector searches typically complete in <100ms with DiskANN indexing
- Use appropriate similarity thresholds for your use case
- Monitor API rate limits in the Analytics dashboard
- Cache frequently accessed data for better performance

## Technical Details

### Database Integration
- Direct connection to PostgreSQL with pgvectorscale
- Real-time queries with proper error handling
- Support for complex filtering and aggregation

### AI Model Support
- OpenAI GPT models (primary)
- Anthropic Claude models (secondary)
- Automatic fallback and error handling
- Structured response generation with instructor

### Vector Operations
- 1536-dimensional embeddings (text-embedding-3-small)
- Cosine similarity scoring
- DiskANN indexing for performance
- Time-based partitioning for scalability

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure Docker container is running: `docker compose ps`
   - Check PostgreSQL logs: `docker compose logs postgres`
   - Verify connection string in `.env`

2. **API Key Errors**
   - Check API key format and validity
   - Verify account has sufficient credits
   - Check rate limits and usage quotas

3. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path includes the project root
   - Verify Streamlit version compatibility

4. **Performance Issues**
   - Check database index status
   - Monitor memory usage
   - Review query patterns in Analytics

### Debug Mode
Run with debug logging:
```bash
cd streamlit_app
python3 -c "import streamlit as st; st.set_option('server.headless', True)"
python3 -m streamlit run app.py --logger.level=debug
```

## Development

### Adding New Features
1. Create new page in `pages/` directory
2. Follow naming convention: `NN_📊_Feature_Name.py`
3. Import existing components from `components/`
4. Add navigation in main `app.py`

### Component Development
- Place reusable components in `components/` directory
- Follow class-based structure with `render()` method
- Handle errors gracefully with user-friendly messages
- Use consistent styling and layout patterns

### Testing
- Test each page independently
- Verify database connections work correctly
- Check API integrations with valid/invalid keys
- Validate performance under different loads

## Contributing

1. Follow the existing code structure and naming conventions
2. Add comprehensive error handling
3. Include user-friendly documentation
4. Test thoroughly before submitting changes

## License

This project follows the same license as the parent pgvector-app project.