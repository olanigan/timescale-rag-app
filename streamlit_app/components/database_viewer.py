"""
Database Viewer Component

Reusable component for displaying database tables and schema information.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add the parent directory to the path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.vector_store import VectorStore

class DatabaseViewer:
    """Component for database visualization and exploration"""

    def __init__(self, vec_store=None):
        """Initialize the database viewer"""
        self.vec_store = vec_store or VectorStore()

    def render_table_preview(self, table_name="embeddings", limit=10):
        """Render a preview of the specified table"""
        st.subheader(f"📋 {table_name.title()} Table Preview")

        try:
            # This would be replaced with actual database queries
            st.info("🔧 Table preview will be implemented with direct SQL queries")

            # Placeholder columns
            columns = ["id", "metadata", "contents", "embedding"]
            sample_data = pd.DataFrame(columns=columns)

            st.dataframe(sample_data, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading table preview: {str(e)}")

    def render_schema_info(self):
        """Render database schema information"""
        st.subheader("🔍 Database Schema")

        schema_info = {
            "Table Name": "embeddings",
            "Primary Key": "id (UUID v1)",
            "Columns": [
                {"name": "id", "type": "UUID", "description": "Time-ordered unique identifier"},
                {"name": "metadata", "type": "JSONB", "description": "Flexible metadata storage"},
                {"name": "contents", "type": "TEXT", "description": "Document content"},
                {"name": "embedding", "type": "vector(1536)", "description": "OpenAI embedding vector"}
            ],
            "Indexes": [
                {"name": "embeddings_embedding_idx", "type": "DiskANN", "description": "Vector similarity search"},
                {"name": "embeddings_time_idx", "type": "Time-based", "description": "7-day partitioning"}
            ]
        }

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Table Information**")
            st.write(f"**Name:** {schema_info['Table Name']}")
            st.write(f"**Primary Key:** {schema_info['Primary Key']}")

        with col2:
            st.markdown("**Indexing**")
            for idx in schema_info['Indexes']:
                st.write(f"**{idx['name']}:** {idx['type']}")

        st.markdown("**Column Details**")
        for col in schema_info['Columns']:
            with st.expander(f"📊 {col['name']} ({col['type']})"):
                st.write(f"**Description:** {col['description']}")

    def render_statistics(self):
        """Render database statistics"""
        st.subheader("📈 Database Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Records", "Loading...")

        with col2:
            st.metric("Vector Dimensions", "1536")

        with col3:
            st.metric("Index Size", "Loading...")

        with col4:
            st.metric("Last Updated", "Loading...")

        st.info("🔧 Statistics will be calculated from database queries")

    def render_query_interface(self):
        """Render raw SQL query interface"""
        st.subheader("🔧 Raw SQL Query")

        with st.expander("⚠️ Advanced Query Interface", expanded=False):
            st.warning("This is for advanced users. Incorrect queries may affect performance.")

            query = st.text_area(
                "SQL Query",
                value="SELECT COUNT(*) FROM embeddings;",
                height=100
            )

            if st.button("Execute Query"):
                try:
                    st.info("🔧 Query execution will be implemented with psycopg2")
                    st.code(f"Query: {query}")
                except Exception as e:
                    st.error(f"Query error: {str(e)}")

    def render(self):
        """Main render method for the database viewer"""
        st.markdown("### 🗄️ Database Explorer")

        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Data Preview",
            "🔍 Schema",
            "📈 Statistics",
            "🔧 Query"
        ])

        with tab1:
            self.render_table_preview()

        with tab2:
            self.render_schema_info()

        with tab3:
            self.render_statistics()

        with tab4:
            self.render_query_interface()