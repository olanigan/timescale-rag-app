"""
RAG Demo Component

Reusable component for demonstrating the RAG pipeline step-by-step.
"""

import streamlit as st
import time
import sys
from pathlib import Path

# Add the parent directory to the path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.vector_store import VectorStore
from app.services.synthesizer import Synthesizer

class RAGDemo:
    """Component for RAG pipeline demonstration"""

    def __init__(self, vec_store=None, synthesizer=None):
        """Initialize the RAG demo"""
        self.vec_store = vec_store or VectorStore()
        self.synthesizer = synthesizer or Synthesizer()

    def render_pipeline_input(self):
        """Render the pipeline input section"""
        st.markdown("### 🔤 Pipeline Input")

        user_query = st.text_area(
            "Enter your question",
            placeholder="Ask me anything about our services...",
            height=100,
            help="This will go through the complete RAG pipeline"
        )

        return user_query

    def render_pipeline_config(self):
        """Render pipeline configuration options"""
        st.markdown("### ⚙️ Pipeline Configuration")

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

        return search_limit, model_choice, show_intermediate

    def render_pipeline_diagram(self):
        """Render a visual diagram of the RAG pipeline"""
        st.markdown("### 🔄 Pipeline Flow")

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

    def run_pipeline_step(self, step_name, step_function, show_intermediate, **kwargs):
        """Run a single pipeline step with timing and visualization"""
        st.subheader(f"📥 Step: {step_name}")

        with st.spinner(f"Running {step_name.lower()}..."):
            start_time = time.time()
            result = step_function(**kwargs)
            step_time = time.time() - start_time

            if show_intermediate:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f"{step_name} Time", ".2f")
                with col2:
                    st.success(f"✅ {step_name} completed")

        return result, step_time

    def render_context_display(self, results, show_intermediate):
        """Render retrieved context"""
        if results is not None and not results.empty:
            with st.expander("📄 Retrieved Context", expanded=show_intermediate):
                for idx, row in results.iterrows():
                    st.markdown(f"**Document {idx + 1}:**")
                    st.write(row.get('contents', 'N/A'))
                    if 'distance' in row:
                        st.caption(".3f")
                    st.divider()

    def render_final_output(self, response, pipeline_stats):
        """Render the final pipeline output"""
        st.subheader("📤 Final Answer")

        if response:
            st.markdown("### 🤖 AI Response")
            st.write(response)

            # Pipeline summary
            st.subheader("📊 Pipeline Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Time", ".2f")

            with col2:
                st.metric("Query Length", f"{pipeline_stats.get('query_length', 0)} chars")

            with col3:
                st.metric("Context Docs", pipeline_stats.get('context_count', 0))

            with col4:
                st.metric("Response Length", f"{len(response)} chars")

            # Performance visualization
            st.subheader("⏱️ Performance Breakdown")
            times = pipeline_stats.get('step_times', {})
            if times:
                st.bar_chart(times)

        else:
            st.error("❌ No response generated")

    def execute_pipeline(self, query, search_limit, model_choice, show_intermediate):
        """Execute the complete RAG pipeline"""
        pipeline_stats = {
            'query_length': len(query),
            'step_times': {},
            'context_count': 0
        }

        # Step 1: Query Processing
        def process_query():
            # In practice, this would use the embedding model
            return "query_processed"

        _, embedding_time = self.run_pipeline_step(
            "Query Processing", process_query, show_intermediate
        )
        pipeline_stats['step_times']['Query Processing'] = embedding_time

        # Step 2: Context Retrieval
        def retrieve_context():
            try:
                results = self.vec_store.search(query, limit=search_limit)
                pipeline_stats['context_count'] = len(results) if results is not None else 0
                return results
            except Exception as e:
                st.error(f"❌ Retrieval failed: {str(e)}")
                return None

        results, retrieval_time = self.run_pipeline_step(
            "Context Retrieval", retrieve_context, show_intermediate
        )
        pipeline_stats['step_times']['Context Retrieval'] = retrieval_time

        # Display retrieved context
        self.render_context_display(results, show_intermediate)

        # Step 3: Response Generation
        def generate_response():
            try:
                # Prepare context for synthesizer
                context = ""
                if results is not None and not results.empty:
                    context = "\n\n".join(results['contents'].tolist())

                # Generate response
                response = self.synthesizer.generate_response(
                    question=query,
                    context=context,
                    model_choice=model_choice
                )
                return response
            except Exception as e:
                st.error(f"❌ Generation failed: {str(e)}")
                return None

        response, generation_time = self.run_pipeline_step(
            "Response Generation", generate_response, show_intermediate
        )
        pipeline_stats['step_times']['Response Generation'] = generation_time

        # Calculate total time
        total_time = sum(pipeline_stats['step_times'].values())
        pipeline_stats['total_time'] = total_time

        return response, pipeline_stats

    def render(self):
        """Main render method for the RAG demo"""
        # Input and configuration
        user_query = self.render_pipeline_input()

        col1, col2 = st.columns([2, 1])
        with col1:
            search_limit, model_choice, show_intermediate = self.render_pipeline_config()
        with col2:
            self.render_pipeline_diagram()

        # Run pipeline button
        if st.button("🚀 Run RAG Pipeline", type="primary", use_container_width=True):
            if not user_query.strip():
                st.error("Please enter a question first")
                return

            response, pipeline_stats = self.execute_pipeline(
                user_query, search_limit, model_choice, show_intermediate
            )

            self.render_final_output(response, pipeline_stats)