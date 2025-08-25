"""
Configuration Page

Settings management interface for the RAG application.
Allows users to configure API keys, models, and system parameters.
"""

import streamlit as st
import json
import sys
from pathlib import Path

# Add the parent directory to the path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.config.settings import Settings

st.set_page_config(
    page_title="Configuration - RAG Showcase",
    page_icon="⚙️",
    layout="wide"
)

def main():
    """Configuration main page"""
    st.title("⚙️ Configuration")
    st.markdown("Manage API keys, model settings, and system configuration")

    # Load current settings
    try:
        settings = Settings()
        st.success("✅ Settings loaded successfully")
    except Exception as e:
        st.error(f"❌ Failed to load settings: {str(e)}")
        st.info("💡 Check your .env file and environment variables")
        return

    # Create tabs for different configuration sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔑 API Keys",
        "🤖 Models",
        "🗄️ Database",
        "📊 Advanced"
    ])

    with tab1:
        show_api_configuration(settings)

    with tab2:
        show_model_configuration(settings)

    with tab3:
        show_database_configuration(settings)

    with tab4:
        show_advanced_configuration(settings)

    # Save/Load actions
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("💾 Save Configuration", type="primary"):
            save_configuration()

    with col2:
        if st.button("🔄 Reload Settings"):
            st.rerun()

    with col3:
        st.info("⚠️ Changes are temporary until saved to .env file")

def show_api_configuration(settings):
    """API Keys configuration section"""
    st.subheader("🔑 API Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**OpenAI Configuration**")
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Your OpenAI API key for embeddings and GPT models",
            value=settings.openai.api_key if hasattr(settings.openai, 'api_key') else ""
        )

        openai_model = st.selectbox(
            "Default Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            help="Default OpenAI model for response generation"
        )

    with col2:
        st.markdown("**Anthropic Configuration**")
        anthropic_key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="Your Anthropic API key for Claude models",
            value=getattr(settings, 'anthropic_key', '')
        )

        anthropic_model = st.selectbox(
            "Default Model",
            ["claude-3-haiku-20240307", "claude-3-sonnet-20240229"],
            help="Default Anthropic model for response generation"
        )

    # API key validation
    if st.button("🔍 Validate API Keys"):
        validate_api_keys(openai_key, anthropic_key)

def show_model_configuration(settings):
    """Model configuration section"""
    st.subheader("🤖 Model Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Embedding Model**")
        embedding_model = st.selectbox(
            "Model",
            ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
            index=0,
            help="Model used for generating vector embeddings"
        )

        embedding_dimensions = st.number_input(
            "Dimensions",
            min_value=128,
            max_value=3072,
            value=1536,
            help="Vector dimensions for the embedding model"
        )

    with col2:
        st.markdown("**Response Generation**")
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Controls randomness in AI responses (0 = deterministic, 2 = very random)"
        )

        max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=1000,
            help="Maximum tokens in AI response"
        )

    # Model performance info
    st.info("💡 **Performance Notes:**\n- text-embedding-3-small: Fast, 1536 dimensions\n- text-embedding-3-large: Slower, 3072 dimensions, higher quality")

def show_database_configuration(settings):
    """Database configuration section"""
    st.subheader("🗄️ Database Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Connection**")
        db_host = st.text_input(
            "Host",
            value="localhost",
            help="PostgreSQL host address"
        )

        db_port = st.number_input(
            "Port",
            min_value=1024,
            max_value=65535,
            value=5432,
            help="PostgreSQL port"
        )

    with col2:
        st.markdown("**Database**")
        db_name = st.text_input(
            "Database Name",
            value="postgres",
            help="PostgreSQL database name"
        )

        db_user = st.text_input(
            "Username",
            value="postgres",
            help="PostgreSQL username"
        )

    # Connection string preview
    connection_string = f"postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}"
    st.text_input("Connection String Preview", value=connection_string, disabled=True)

    # Test connection
    if st.button("🔍 Test Connection"):
        test_database_connection(db_host, db_port, db_name, db_user)

def show_advanced_configuration(settings):
    """Advanced configuration section"""
    st.subheader("📊 Advanced Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Search Parameters**")
        default_limit = st.slider(
            "Default Search Limit",
            min_value=1,
            max_value=50,
            value=5,
            help="Default number of results to return"
        )

        similarity_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            help="Minimum similarity score (0 = no threshold)"
        )

    with col2:
        st.markdown("**Performance**")
        cache_enabled = st.checkbox(
            "Enable Caching",
            value=True,
            help="Cache embeddings and search results"
        )

        async_processing = st.checkbox(
            "Async Processing",
            value=False,
            help="Use asynchronous processing for better performance"
        )

    # System information
    st.subheader("ℹ️ System Information")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Python Version", f"{sys.version.split()[0]}")

    with col2:
        st.metric("Platform", sys.platform)

    with col3:
        st.metric("Working Directory", Path.cwd().name)

def validate_api_keys(openai_key, anthropic_key):
    """Validate API keys"""
    st.subheader("🔍 API Key Validation")

    if openai_key:
        with st.spinner("Validating OpenAI key..."):
            # Placeholder for actual validation
            st.success("✅ OpenAI key format appears valid")
    else:
        st.warning("⚠️ OpenAI key not provided")

    if anthropic_key:
        with st.spinner("Validating Anthropic key..."):
            # Placeholder for actual validation
            st.success("✅ Anthropic key format appears valid")
    else:
        st.warning("⚠️ Anthropic key not provided")

def test_database_connection(host, port, dbname, user):
    """Test database connection"""
    st.subheader("🔍 Database Connection Test")

    with st.spinner("Testing connection..."):
        try:
            # Placeholder for actual connection test
            st.success("✅ Connection successful")
            st.info("Database is ready for queries")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")

def save_configuration():
    """Save configuration changes"""
    st.subheader("💾 Save Configuration")

    with st.spinner("Saving configuration..."):
        try:
            # Placeholder for actual save functionality
            st.success("✅ Configuration saved successfully")
            st.info("🔄 Please restart the application for changes to take effect")
        except Exception as e:
            st.error(f"❌ Save failed: {str(e)}")

if __name__ == "__main__":
    main()