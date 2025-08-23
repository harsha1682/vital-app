import streamlit as st #type: ignore
import pandas as pd #type: ignore
import plotly.express as px #type: ignore
import plotly.graph_objects as go #type: ignore
from datetime import datetime, timedelta
import random
import time

def generate_sample_data():
        # Sample report data
    reports = [
        {"name": "Blood Analysis Report", "type": "Lab Report", "date": "2024-08-20", "status": "Completed", "priority": "High"},
        {"name": "Cardiovascular Assessment", "type": "Heart Report", "date": "2024-08-19", "status": "Processing", "priority": "High"},
        {"name": "Medication Adherence Report", "type": "Medication Report", "date": "2024-08-18", "status": "Completed", "priority": "Medium"},
        {"name": "Monthly Health Summary", "type": "General Report", "date": "2024-08-15", "status": "Completed", "priority": "Low"},
        {"name": "Diabetic Monitoring Report", "type": "Metabolic Report", "date": "2024-08-14", "status": "Pending", "priority": "High"},
        {"name": "Sleep Pattern Analysis", "type": "Wellness Report", "date": "2024-08-12", "status": "Completed", "priority": "Medium"},
    ]
        
    # Sample health metrics
    dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
    metrics = {
        "Date": dates,
        "Heart Rate": [random.randint(65, 85) for _ in dates],
        "Blood Pressure (Systolic)": [random.randint(110, 130) for _ in dates],
        "Blood Pressure (Diastolic)": [random.randint(70, 85) for _ in dates],
        "Weight": [random.uniform(70, 75) for _ in dates]
    }
        
    return reports, pd.DataFrame(metrics)


st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    .report-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .report-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .status-completed { background-color: #d1fae5; color: #065f46; }
    .status-processing { background-color: #fef3c7; color: #92400e; }
    .status-pending { background-color: #dbeafe; color: #1e40af; }
    .sidebar-nav {
        padding: 1rem 0;
    }
    .nav-item {
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .nav-item:hover {
        background-color: #f3f4f6;
    }
    .nav-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)



def run_reports_page():
    st.markdown('<h1 class="main-header">📋 Medical Reports</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Auto-generated medical reports and analytics</p>', unsafe_allow_html=True)
    
    
    
    
    reports_data, health_metrics = generate_sample_data()
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Total Reports</h3>
            <h1>24</h1>
            <p>+3 this month</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>✅ Completed</h3>
            <h1>18</h1>
            <p>75% completion rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⏳ In Progress</h3>
            <h1>4</h1>
            <p>Expected by tomorrow</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🔄 Auto-Generated</h3>
            <h1>21</h1>
            <p>87% automated</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Auto-Generate New Report Section
    st.markdown("### 🤖 Generate New Report")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        report_type = st.selectbox(
            "Select Report Type:",
            ["Blood Analysis", "Cardiovascular Assessment", "Medication Review", "Health Summary", "Diagnostic Report"]
        )
    
    with col2:
        date_range = st.selectbox(
            "Data Range:",
            ["Last 7 days", "Last 30 days", "Last 90 days", "Custom Range"]
        )
    
    with col3:
        if st.button("🚀 Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                st.success(f"✅ {report_type} report generated successfully!")
    
    st.markdown("---")
    
    # Reports List and Charts
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Recent Reports")
        
        for report in reports_data:
            status_class = f"status-{report['status'].lower()}"
            priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
            
            st.markdown(f"""
            <div class="report-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                    <h4 style="margin: 0; color: #1f2937;">{report['name']}</h4>
                    <span class="status-badge {status_class}">{report['status']}</span>
                </div>
                <p style="color: #6b7280; margin: 0.25rem 0; font-size: 0.875rem;">
                    {priority_emoji[report['priority']]} {report['type']} • {report['date']}
                </p>
                <div style="margin-top: 1rem;">
                    <button style="background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer; margin-right: 0.5rem;">View Report</button>
                    <button style="background: #f3f4f6; color: #374151; border: none; padding: 0.5rem 1rem; border-radius: 6px; cursor: pointer;">Download</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📈 Health Trends")
        
        # Heart Rate Trend
        fig_hr = px.line(
            health_metrics, 
            x='Date', 
            y='Heart Rate',
            title='Heart Rate Trend (30 days)',
            color_discrete_sequence=['#667eea']
        )
        fig_hr.update_layout(
            height=300,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig_hr, use_container_width=True)
        
        # Blood Pressure Chart
        fig_bp = go.Figure()
        fig_bp.add_trace(go.Scatter(
            x=health_metrics['Date'],
            y=health_metrics['Blood Pressure (Systolic)'],
            name='Systolic',
            line=dict(color='#ef4444')
        ))
        fig_bp.add_trace(go.Scatter(
            x=health_metrics['Date'],
            y=health_metrics['Blood Pressure (Diastolic)'],
            name='Diastolic',
            line=dict(color='#3b82f6')
        ))
        fig_bp.update_layout(
            title='Blood Pressure Trend',
            height=300,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig_bp, use_container_width=True)
    