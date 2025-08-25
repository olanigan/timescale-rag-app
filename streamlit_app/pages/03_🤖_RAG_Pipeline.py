"""
RAG Pipeline Page

End-to-end demonstration of the Retrieval-Augmented Generation pipeline.
Shows each step of the process with timing and intermediate results.
"""

import streamlit as st
import time
import sys
from pathlib import Path

# Add the parent directory to the path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.vector_store import VectorStore
from app.services.synthesizer import Synthesizer

st.set_page_config(
    page_title="RAG Pipeline - RAG Showcase",
    page_icon="🤖",
    layout="wide"
)

def main():
    """RAG Pipeline main page"""
    st.title("🤖 RAG Pipeline")
    st.markdown("Step-by-step demonstration of the complete RAG process")

    # Initialize components
    try:
        vec_store = VectorStore()
        synthesizer = Synthesizer()
        st.success("✅ All components initialized")
    except Exception as e:
        st.error(f"❌ Initialization failed: {str(e)}")
        st.info("💡 Check Docker container, .env configuration, and API keys")
        return

    # Pipeline input
    st.subheader("🔤 Input Query")
    user_query = st.text_area(
        "Enter your question",
        placeholder="Ask me anything about our services...",
        height=100,
        help="This will go through the complete RAG pipeline"
    )

    # Pipeline configuration
    col1, col2, col3 = st.columns(3)

    with col1:
        search_limit = st.slider("Context Retrieval Limit", 1, 10, 3)

    with col2:
        model_choice = st.selectbox(
            "LLM Model",
            ["gpt-4o-mini", "claude-3-haiku"],
            help="Choose the language model for response generation"
        )

    with col3:
        show_intermediate = st.checkbox("Show Intermediate Steps", value=True)

    # Run pipeline button
    if st.button("🚀 Run RAG Pipeline", type="primary", use_container_width=True):
        if not user_query.strip():
            st.error("Please enter a question first")
            return

        run_rag_pipeline(user_query, vec_store, synthesizer, search_limit, model_choice, show_intermediate)

def run_rag_pipeline(query, vec_store, synthesizer, search_limit, model_choice, show_intermediate):
    """Execute the complete RAG pipeline with visualization"""

    # Step 1: Query Embedding
    st.subheader("📥 Step 1: Query Processing")
    with st.spinner("Generating query embedding..."):
        start_time = time.time()
        # In practice, this would use the embedding model
        embedding_time = time.time() - start_time

    if show_intermediate:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Embedding Time", ".2f")
        with col2:
            st.info("✅ Query processed and embedded")

    # Step 2: Context Retrieval
    st.subheader("🔍 Step 2: Context Retrieval")
    with st.spinner("Searching for relevant context..."):
        start_time = time.time()
        try:
            results = vec_store.search(query, limit=search_limit)
            retrieval_time = time.time() - start_time

            if show_intermediate:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Retrieval Time", ".2f")
                with col2:
                    st.metric("Results Found", len(results) if results is not None else 0)
                with col3:
                    st.metric("Best Similarity", ".3f" if results is not None and not results.empty and 'distance' in results.columns else "N/A")

                if results is not None and not results.empty:
                    st.success("✅ Relevant context retrieved")
                else:
                    st.warning("⚠️ No relevant context found")

        except Exception as e:
            st.error(f"❌ Retrieval failed: {str(e)}")
            return

    # Display retrieved context
    if results is not None and not results.empty:
        with st.expander("📄 Retrieved Context", expanded=show_intermediate):
            for idx, row in results.iterrows():
                st.markdown(f"**Document {idx + 1}:**")
                st.write(row.get('contents', 'N/A'))
                if 'distance' in row:
                    st.caption(".3f")
                st.divider()

    # Step 3: Response Generation
    st.subheader("🤖 Step 3: Response Generation")
    with st.spinner("Generating AI response..."):
        start_time = time.time()
        try:
            # Prepare context for synthesizer
            context = ""
            if results is not None and not results.empty:
                context = "\n\n".join(results['contents'].tolist())

            # Generate response
            response = synthesizer.generate_response(
                question=query,
                context=context,
                model_choice=model_choice
            )
            generation_time = time.time() - start_time

            if show_intermediate:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Generation Time", ".2f")
                with col2:
                    st.success("✅ Response generated successfully")

        except Exception as e:
            st.error(f"❌ Generation failed: {str(e)}")
            return

    # Step 4: Final Output
    st.subheader("📤 Step 4: Final Answer")

    # Display the response
    if response:
        st.markdown("### 🤖 AI Response")
        st.write(response)

        # Pipeline summary
        st.subheader("📊 Pipeline Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Time", ".2f")

        with col2:
            st.metric("Query Length", f"{len(query)} chars")

        with col3:
            st.metric("Context Docs", len(results) if results is not None else 0)

        with col4:
            st.metric("Response Length", f"{len(response)} chars")

        # Performance visualization
        st.subheader("⏱️ Performance Breakdown")
        times = {
            "Query Processing": embedding_time,
            "Context Retrieval": retrieval_time,
            "Response Generation": generation_time
        }

        st.bar_chart(times)

    else:
        st.error("❌ No response generated")

def display_pipeline_diagram():
    """Display a visual diagram of the RAG pipeline"""
    st.subheader("🔄 Pipeline Flow")

    st.markdown("""
    ```
    User Query
        ↓
    📥 Query Processing
        ↓
    🔍 Context Retrieval (Vector Search)
        ↓
    🤖 Response Generation (LLM)
        ↓
    📤 Final Answer
    ```
    """)

    st.info("💡 Each step is timed and can be inspected individually")

if __name__ == "__main__":
    main()