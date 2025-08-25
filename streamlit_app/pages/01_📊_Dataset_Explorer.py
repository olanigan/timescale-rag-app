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
from components.database_viewer import DatabaseViewer

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

    # Initialize database viewer component
    db_viewer = DatabaseViewer(vec_store)

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Data Preview",
        "🔍 Schema Info",
        "📈 Statistics",
        "🔗 Raw Query"
    ])

    with tab1:
        # Add controls for data preview
        col1, col2 = st.columns([1, 3])

        with col1:
            limit = st.slider("Number of records", 5, 50, 10)
            show_embedding = st.checkbox("Show embedding vectors", value=False)
            # Store in session state for the component to access
            st.session_state['show_embeddings'] = show_embedding

        with col2:
            if st.button("🔄 Refresh Data"):
                st.rerun()

        db_viewer.render_table_preview(limit=limit)

    with tab2:
        db_viewer.render_schema_info()

    with tab3:
        db_viewer.render_statistics()

    with tab4:
        db_viewer.render_query_interface()



if __name__ == "__main__":
    main()