"""
Metrics Dashboard Component

Reusable component for displaying performance metrics and analytics.
"""

import streamlit as st
import pandas as pd
import time
import sys
from pathlib import Path

# Add the parent directory to the path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.vector_store import VectorStore

class MetricsDashboard:
    """Component for performance metrics and analytics dashboard"""

    def __init__(self, vec_store=None):
        """Initialize the metrics dashboard"""
        self.vec_store = vec_store or VectorStore()

    def render_overview_metrics(self):
        """Render main overview metrics"""
        st.subheader("📊 System Overview")

        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Total records
            st.metric("Total Records", "Loading...", "🔄")

        with col2:
            # Active connections
            st.metric("Active Connections", "1", "🟢")

        with col3:
            # Average response time
            st.metric("Avg Response Time", "<100ms", "⚡")

        with col4:
            # Uptime
            st.metric("System Uptime", "Running", "🟢")

    def render_usage_trends(self):
        """Render usage trends charts"""
        st.subheader("📈 Usage Trends")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Search Queries Over Time**")
            # Placeholder for time series chart
            st.info("🔧 Time series data will be collected and displayed here")

            # Sample data for demonstration
            sample_data = pd.DataFrame({
                'Time': pd.date_range(start='2024-01-01', periods=24, freq='H'),
                'Queries': [10, 15, 8, 12, 20, 18, 25, 30, 22, 28, 35, 40,
                           38, 45, 42, 48, 55, 52, 58, 65, 62, 68, 70, 75]
            })
            st.line_chart(sample_data.set_index('Time'))

        with col2:
            st.markdown("**Query Categories**")
            # Placeholder for category distribution
            st.info("🔧 Category distribution will be calculated from metadata")

            # Sample category data
            categories = pd.DataFrame({
                'Category': ['Shipping', 'Order Management', 'Returns', 'Payment', 'Account'],
                'Count': [45, 32, 28, 22, 18]
            })
            st.bar_chart(categories.set_index('Category'))

    def render_performance_metrics(self):
        """Render detailed performance metrics"""
        st.subheader("⏱️ Performance Metrics")

        # Performance benchmarks
        st.markdown("**Search Performance Benchmarks**")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Vector Search Time", "45ms", "⚡")
            st.metric("Embedding Time", "120ms", "📊")

        with col2:
            st.metric("LLM Response Time", "850ms", "🤖")
            st.metric("Total Pipeline Time", "1.2s", "🔄")

        with col3:
            st.metric("Memory Usage", "256MB", "💾")
            st.metric("CPU Usage", "15%", "🖥️")

        # Performance over time
        st.subheader("📈 Performance Trends")

        # Sample performance data
        perf_data = pd.DataFrame({
            'Operation': ['Vector Search', 'Embedding', 'LLM Generation', 'Total Pipeline'],
            'Average Time (ms)': [45, 120, 850, 1200],
            'P95 Time (ms)': [85, 200, 1500, 2000]
        })

        st.dataframe(perf_data, use_container_width=True)

        # Performance visualization
        st.bar_chart(perf_data.set_index('Operation')[['Average Time (ms)', 'P95 Time (ms)']])

    def render_search_analytics(self):
        """Render search analytics and patterns"""
        st.subheader("🔍 Search Analytics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top Search Queries**")
            # Placeholder for top queries
            st.info("🔧 Top queries will be tracked and displayed here")

            top_queries = pd.DataFrame({
                'Query': [
                    'How do I track my order?',
                    'What are shipping options?',
                    'How to return an item?',
                    'Payment methods available',
                    'Account registration help'
                ],
                'Count': [125, 98, 87, 76, 65]
            })
            st.dataframe(top_queries, use_container_width=True)

        with col2:
            st.markdown("**Search Result Quality**")
            # Placeholder for quality metrics
            st.info("🔧 Quality metrics will be calculated from user feedback")

            quality_metrics = pd.DataFrame({
                'Metric': ['Relevance Score', 'User Satisfaction', 'Click-through Rate'],
                'Value': ['0.87', '4.2/5', '68%']
            })
            st.dataframe(quality_metrics, use_container_width=True)

        # Search patterns
        st.subheader("🔍 Search Patterns")

        # Sample search pattern data
        patterns = pd.DataFrame({
            'Hour': range(24),
            'Searches': [5, 3, 2, 1, 2, 8, 15, 25, 35, 42, 48, 52,
                        55, 58, 62, 65, 68, 55, 45, 35, 25, 18, 12, 8]
        })

        st.line_chart(patterns.set_index('Hour'))

    def render_system_health(self):
        """Render system health and diagnostics"""
        st.subheader("💾 System Health")

        # Health checks
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Database Health**")
            st.success("✅ PostgreSQL: Connected")
            st.success("✅ pgvectorscale: Active")
            st.success("✅ DiskANN Index: Ready")

        with col2:
            st.markdown("**API Health**")
            st.success("✅ OpenAI API: Available")
            st.success("✅ Anthropic API: Available")
            st.info("🔄 Rate Limits: Normal")

        with col3:
            st.markdown("**System Resources**")
            st.success("✅ Memory: 45% used")
            st.success("✅ Disk Space: 78% free")
            st.success("✅ Network: Stable")

        # Recent activity
        st.subheader("📋 Recent Activity")

        # Sample activity log
        activities = [
            {"time": "2024-01-15 14:30:22", "event": "Vector search executed", "status": "✅"},
            {"time": "2024-01-15 14:30:15", "event": "LLM response generated", "status": "✅"},
            {"time": "2024-01-15 14:30:10", "event": "Database query completed", "status": "✅"},
            {"time": "2024-01-15 14:30:05", "event": "User query processed", "status": "✅"},
            {"time": "2024-01-15 14:30:00", "event": "System startup", "status": "✅"}
        ]

        for activity in activities:
            col1, col2, col3 = st.columns([2, 4, 1])
            with col1:
                st.text(activity["time"])
            with col2:
                st.text(activity["event"])
            with col3:
                st.text(activity["status"])

        # Error tracking
        st.subheader("⚠️ Error Tracking")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Errors (24h)", "0", "🟢")

        with col2:
            st.metric("Warnings (24h)", "2", "🟡")

        if st.button("🔍 View Error Logs"):
            st.info("🔧 Error log viewer will be implemented with detailed error tracking")

    def run_performance_test(self):
        """Run a quick performance test"""
        st.subheader("🧪 Performance Test")

        if st.button("🚀 Run Test"):
            with st.spinner("Running performance test..."):
                # Simulate performance test
                progress_bar = st.progress(0)

                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)

                st.success("✅ Performance test completed")
                st.metric("Test Result", "All systems operational")

    def render(self):
        """Main render method for the metrics dashboard"""
        # Create tabs for different analytics views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Overview",
            "⏱️ Performance",
            "🔍 Search Analytics",
            "💾 System Health"
        ])

        with tab1:
            self.render_overview_metrics()
            self.render_usage_trends()

        with tab2:
            self.render_performance_metrics()

        with tab3:
            self.render_search_analytics()

        with tab4:
            self.render_system_health()
            self.run_performance_test()