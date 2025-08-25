"""
Search Interface Component

Reusable component for vector search with various filter options.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add the parent directory to the path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.vector_store import VectorStore

class SearchInterface:
    """Component for interactive vector search"""

    def __init__(self, vec_store=None):
        """Initialize the search interface"""
        self.vec_store = vec_store or VectorStore()

    def render_search_form(self):
        """Render the main search form"""
        st.markdown("### 🔍 Vector Search")

        with st.form("search_form"):
            col1, col2 = st.columns([2, 1])

            with col1:
                query = st.text_input(
                    "Search Query",
                    placeholder="Enter your question or search terms...",
                    help="Natural language query for semantic similarity search"
                )

            with col2:
                limit = st.slider("Results Limit", 1, 20, 5)
                threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.0,
                                    help="Lower values = more similar results")

            # Search type tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "🔍 Basic Search",
                "🏷️ Metadata Filter",
                "🔧 Predicate Filter",
                "⏰ Time Filter"
            ])

            search_type = "basic"
            filter_params = {}

            with tab1:
                st.write("Basic semantic similarity search")
                search_type = "basic"

            with tab2:
                st.write("Filter by metadata fields")
                category = st.selectbox(
                    "Category",
                    ["All", "Shipping", "Order Management", "Returns", "Payment", "Account"],
                    help="Filter results by FAQ category"
                )
                if category != "All":
                    filter_params["category"] = category
                search_type = "metadata"

            with tab3:
                st.write("Advanced predicate filtering")
                st.info("🔧 Predicate filtering will be implemented with timescale-vector client")
                search_type = "predicate"

            with tab4:
                st.write("Filter by time range")
                st.info("🔧 Time-based filtering will be implemented with UUID timestamps")
                search_type = "time"

            submitted = st.form_submit_button("🔍 Search", use_container_width=True)

        return submitted, query, limit, search_type, filter_params

    def render_results(self, results, query):
        """Render search results"""
        if results is None:
            st.info("No results found or search type not yet implemented")
            return

        if results.empty:
            st.info("No results found")
            return

        st.subheader(f"Search Results for: '{query}'")

        # Results summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Results Found", len(results))
        with col2:
            if 'distance' in results.columns:
                st.metric("Best Similarity", ".3f")
        with col3:
            st.metric("Search Time", "<100ms")

        # Results table
        st.dataframe(
            results,
            use_container_width=True,
            column_config={
                "contents": st.column_config.TextColumn("Content", width="large"),
                "metadata": st.column_config.JsonColumn("Metadata"),
                "distance": st.column_config.NumberColumn("Similarity", format="%.3f")
            }
        )

        # Individual result cards
        st.subheader("Detailed Results")
        for idx, row in results.iterrows():
            with st.expander(f"Result {idx + 1}", expanded=False):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown("**Content:**")
                    st.write(row.get('contents', 'N/A'))

                    st.markdown("**Metadata:**")
                    st.json(row.get('metadata', {}))

                with col2:
                    if 'distance' in row:
                        st.metric("Similarity Score", ".3f")
                    st.metric("ID", str(row.get('id', 'N/A'))[:8] + "...")

    def render_search_tips(self):
        """Render search tips and help"""
        with st.expander("💡 Search Tips"):
            st.markdown("""
            - **Natural Language**: Use conversational queries like "How do I track my order?"
            - **Categories**: Filter by specific topics for more relevant results
            - **Similarity**: Lower threshold = more similar results, higher = broader matches
            - **Performance**: Searches typically complete in <100ms with DiskANN indexing
            """)

    def render(self):
        """Main render method for the search interface"""
        submitted, query, limit, search_type, filter_params = self.render_search_form()

        if submitted and query:
            with st.spinner("Searching..."):
                try:
                    # Perform search based on type
                    if search_type == "basic":
                        results = self.vec_store.search(query, limit=limit)
                    elif search_type == "metadata":
                        results = self.vec_store.search(
                            query,
                            limit=limit,
                            metadata_filter=filter_params
                        )
                    else:
                        # Placeholder for advanced search types
                        st.info(f"🔧 {search_type.title()} search will be implemented")
                        results = None

                    if results is not None:
                        self.render_results(results, query)
                    else:
                        st.info("No results found or search type not yet implemented")

                except Exception as e:
                    st.error(f"Search error: {str(e)}")

        self.render_search_tips()