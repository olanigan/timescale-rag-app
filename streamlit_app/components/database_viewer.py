"""
Database Viewer Component

Reusable component for displaying database tables and schema information.
"""

import streamlit as st
import pandas as pd
import psycopg2
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the parent directory to the path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.vector_store import VectorStore

class DatabaseViewer:
    """Component for database visualization and exploration"""

    def __init__(self, vec_store=None):
        """Initialize the database viewer"""
        self.vec_store = vec_store or VectorStore()
        self.db_config = self._get_db_config()

    def _get_db_config(self) -> Dict[str, Any]:
        """Get database configuration from VectorStore"""
        try:
            # Access the database settings from the vector store
            settings = self.vec_store.settings
            db_settings = settings.database

            return {
                'host': 'localhost',
                'port': 5432,
                'database': 'postgres',
                'user': 'postgres',
                'password': 'password',
                'service_url': db_settings.service_url if hasattr(db_settings, 'service_url') else None
            }
        except Exception as e:
            st.error(f"Could not get database config: {e}")
            return {}

    def _get_connection(self):
        """Get database connection"""
        try:
            if self.db_config.get('service_url'):
                # Use service URL if available
                return psycopg2.connect(self.db_config['service_url'])
            else:
                # Use individual parameters
                return psycopg2.connect(
                    host=self.db_config.get('host', 'localhost'),
                    port=self.db_config.get('port', 5432),
                    database=self.db_config.get('database', 'postgres'),
                    user=self.db_config.get('user', 'postgres'),
                    password=self.db_config.get('password', 'password')
                )
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    def render_table_preview(self, table_name="embeddings", limit=10):
        """Render a preview of the specified table"""
        st.subheader(f"📋 {table_name.title()} Table Preview")

        conn = None
        try:
            conn = self._get_connection()
            if not conn:
                return

            with conn.cursor() as cursor:
                # Get sample data with optional embedding display
                if st.session_state.get('show_embeddings', False):
                    query = f"""
                    SELECT
                        id,
                        metadata,
                        LEFT(contents, 200) as contents_preview,
                        embedding::text as embedding
                    FROM {table_name}
                    ORDER BY id
                    LIMIT %s
                    """
                else:
                    query = f"""
                    SELECT
                        id,
                        metadata,
                        LEFT(contents, 200) as contents_preview,
                        CASE WHEN embedding IS NOT NULL THEN '[VECTOR DATA]' ELSE NULL END as embedding
                    FROM {table_name}
                    ORDER BY id
                    LIMIT %s
                    """

                cursor.execute(query, (limit,))
                rows = cursor.fetchall()

                if rows:
                    # Create DataFrame from rows
                    data = []
                    for row in rows:
                        data.append({
                            'id': str(row[0]),
                            'metadata': json.dumps(row[1], indent=2) if row[1] else '{}',
                            'contents_preview': str(row[2]) if row[2] else '',
                            'embedding': str(row[3]) if row[3] else ''
                        })

                    df = pd.DataFrame(data)

                    # Display the data
                    st.dataframe(df, use_container_width=True)

                    # Show total count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count_result = cursor.fetchone()
                    if count_result:
                        total_count = count_result[0]
                        st.info(f"Showing {len(rows)} of {total_count} total records")
                else:
                    st.info("No data found in the table")

        except Exception as e:
            st.error(f"Error loading table preview: {str(e)}")
        finally:
            if conn:
                conn.close()

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

        conn = None
        try:
            conn = self._get_connection()
            if not conn:
                return

            with conn.cursor() as cursor:
                # Get total records
                cursor.execute("SELECT COUNT(*) FROM embeddings")
                count_result = cursor.fetchone()
                total_records = count_result[0] if count_result else 0

                # Get categories distribution
                cursor.execute("""
                SELECT
                    metadata->>'category' as category,
                    COUNT(*) as count
                FROM embeddings
                WHERE metadata->>'category' IS NOT NULL
                GROUP BY metadata->>'category'
                ORDER BY count DESC
                """)
                categories = cursor.fetchall()

                # Get date range
                cursor.execute("""
                SELECT
                    MIN((metadata->>'created_at')::timestamp) as earliest,
                    MAX((metadata->>'created_at')::timestamp) as latest
                FROM embeddings
                WHERE metadata->>'created_at' IS NOT NULL
                """)
                date_range_result = cursor.fetchone()
                if date_range_result:
                    date_range = date_range_result
                else:
                    date_range = (None, None)

            # Display metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Records", f"{total_records:,}")

            with col2:
                st.metric("Vector Dimensions", "1536")

            with col3:
                st.metric("Categories", len(categories) if categories else 0)

            with col4:
                if date_range and date_range[0] is not None:
                    st.metric("Date Range", f"{date_range[0].strftime('%Y-%m-%d')}")
                else:
                    st.metric("Date Range", "N/A")

            # Category distribution
            if categories:
                st.subheader("📊 Category Distribution")
                cat_data = [{'Category': cat[0], 'Count': cat[1]} for cat in categories]
                cat_df = pd.DataFrame(cat_data)
                st.bar_chart(cat_df.set_index('Category'))

        except Exception as e:
            st.error(f"Error loading statistics: {str(e)}")
        finally:
            if conn:
                conn.close()

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
                conn = None
                try:
                    conn = self._get_connection()
                    if not conn:
                        return

                    with conn.cursor() as cursor:
                        cursor.execute(query)
                        results = cursor.fetchall()

                        if results:
                            # Convert to DataFrame for display
                            if cursor.description:
                                columns = [desc[0] for desc in cursor.description]
                                # Create DataFrame from dictionary to avoid type issues
                                data_dict = {col: [row[i] for row in results] for i, col in enumerate(columns)}
                                df = pd.DataFrame(data_dict)
                                st.dataframe(df, use_container_width=True)
                                st.info(f"Returned {len(results)} rows")
                            else:
                                st.info("Query executed successfully (no results to display)")
                        else:
                            st.info("Query executed successfully (no results)")

                except Exception as e:
                    st.error(f"Query error: {str(e)}")
                finally:
                    if conn:
                        conn.close()

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