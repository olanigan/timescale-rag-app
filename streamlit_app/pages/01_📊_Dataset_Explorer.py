"""
Dataset Explorer Page

Interactive PostgreSQL data viewer for the FAQ dataset.
Shows table schema, sample data, and database statistics.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add the parent directory to the path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.vector_store import VectorStore

st.set_page_config(
    page_title="Dataset Explorer - RAG Showcase",
    page_icon="📊",
    layout="wide"
)

def main():
    """Dataset Explorer main page"""
    st.title("📊 Dataset Explorer")
    st.markdown("Explore the FAQ dataset stored in PostgreSQL with pgvectorscale")

    # Initialize database connection
    try:
        vec_store = VectorStore()
        st.success("✅ Connected to database")
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        st.info("💡 Make sure Docker container is running and .env is configured")
        return

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Data Preview",
        "🔍 Schema Info",
        "📈 Statistics",
        "🔗 Raw Query"
    ])

    with tab1:
        show_data_preview(vec_store)

    with tab2:
        show_schema_info(vec_store)

    with tab3:
        show_statistics(vec_store)

    with tab4:
        show_raw_query(vec_store)

def show_data_preview(vec_store):
    """Show sample data from the embeddings table"""
    st.subheader("Sample Data Preview")

    col1, col2 = st.columns([1, 3])

    with col1:
        limit = st.slider("Number of records", 5, 50, 10)
        show_embedding = st.checkbox("Show embedding vectors", value=False)

    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()

    try:
        # Get sample data
        query = f"""
        SELECT
            id,
            metadata,
            LEFT(contents, 200) as contents_preview,
            CASE WHEN {show_embedding} THEN embedding ELSE NULL END as embedding
        FROM embeddings
        ORDER BY id
        LIMIT {limit}
        """

        # Note: This is a simplified query - in practice you'd use vec_store methods
        # For now, showing the structure
        st.info("🔧 Data preview functionality will be implemented with direct SQL queries")

        # Placeholder for actual data display
        st.markdown("**Sample data will be displayed here once connected**")

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def show_schema_info(vec_store):
    """Show database schema information"""
    st.subheader("Database Schema")

    st.markdown("""
    ### Table: embeddings
    ```sql
    CREATE TABLE embeddings (
        id UUID PRIMARY KEY,
        metadata JSONB,
        contents TEXT,
        embedding vector(1536)
    );
    ```

    ### Indexes
    - **DiskANN Index**: For fast vector similarity search
    - **Time-based Partitioning**: 7-day partitions on UUID v1 timestamps
    """)

    # Show index information
    st.subheader("Index Details")
    st.info("🔧 Index information will be queried from database")

def show_statistics(vec_store):
    """Show database statistics"""
    st.subheader("Database Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Records", "Loading...")

    with col2:
        st.metric("Vector Dimensions", "1536")

    with col3:
        st.metric("Index Type", "DiskANN")

    st.info("🔧 Statistics will be calculated from database queries")

def show_raw_query(vec_store):
    """Allow raw SQL queries for advanced users"""
    st.subheader("Raw SQL Query")
    st.warning("⚠️ Advanced users only - Direct SQL access")

    query = st.text_area(
        "SQL Query",
        value="SELECT COUNT(*) FROM embeddings;",
        height=100
    )

    if st.button("Execute Query"):
        try:
            st.info("🔧 Raw query functionality will be implemented with psycopg2")
            st.code(f"Query: {query}")
        except Exception as e:
            st.error(f"Query error: {str(e)}")

if __name__ == "__main__":
    main()