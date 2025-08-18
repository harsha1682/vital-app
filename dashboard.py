import streamlit as st #type: ignore
import mysql.connector #type: ignore
from mysql.connector import Error #type: ignore
import pandas as pd #type: ignore
from datetime import datetime, date, timedelta #type: ignore
import plotly.graph_objects as go #type: ignore
import plotly.express as px #type: ignore
import random #type: ignore
import numpy as np #type: ignore

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'vital_signs_db',
    'user': 'root',
    'password': 'H0ney123'
}

def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None



def get_user_profile(user_id):
    """Get user profile information"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
        SELECT username, email, age, weight, height, blood_type, allergies, diseases, created_at 
        FROM users WHERE id = %s
        """, (user_id,))
        profile = cursor.fetchone()
        cursor.close()
        connection.close()
        return profile
    return None

def get_latest_vital_signs(user_id):
    """Get latest vital signs for dashboard"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
        SELECT systolic_bp, diastolic_bp, heart_rate, temperature, glucose, water_balance, general_health
        FROM vital_signs WHERE user_id = %s ORDER BY date_recorded DESC LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result
    return None

def get_bp_history(user_id, days=7):
    """Get blood pressure history for the last N days"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
        SELECT date_recorded, systolic_bp, diastolic_bp
        FROM vital_signs 
        WHERE user_id = %s AND date_recorded >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        ORDER BY date_recorded ASC
        """, (user_id, days))
        
        records = cursor.fetchall()
        cursor.close()
        connection.close()
        return records
    return []

def generate_sample_data(user_id):
    """Generate sample vital signs data for demo purposes"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM vital_signs WHERE user_id = %s", (user_id,))
        count = cursor.fetchone()[0]
        
        if count == 0:  # Only generate if no data exists
            # Generate data for last 7 days
            for i in range(7):
                date_record = date.today() - timedelta(days=6-i)
                systolic = random.randint(110, 140)
                diastolic = random.randint(70, 90)
                heart_rate = random.randint(60, 100)
                temperature = round(random.uniform(36.0, 37.5), 1)
                glucose = random.randint(80, 120)
                water_balance = random.randint(35, 65)
                general_health = random.randint(50, 80)
                
                cursor.execute("""
                INSERT INTO vital_signs (user_id, date_recorded, systolic_bp, diastolic_bp, 
                heart_rate, temperature, glucose, water_balance, general_health)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, date_record, systolic, diastolic, heart_rate, temperature, 
                     glucose, water_balance, general_health))
            
            connection.commit()
        
        cursor.close()
        connection.close()

def load_dashboard_css():
    """Load custom CSS for dashboard"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default elements */
    .main > div {
        padding-top: 2rem;
    }
    
    header[data-testid="stHeader"] {
        display: none;
    }
    
    .stDeployButton {
        display: none;
    }
    
    /* Main dashboard background */
    .stApp {
        background: #f8fafc;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Sidebar logo */
    .sidebar-logo {
        display: flex;
        align-items: center;
        padding: 1.5rem 1rem;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    .sidebar-logo .logo-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        font-size: 1.5rem;
    }
    
    .sidebar-logo h2 {
        color: #1e293b;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
    }
    
    /* Navigation items */
    .nav-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0.5rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #64748b;
        text-decoration: none;
    }
    
    .nav-item:hover {
        background: #f1f5f9;
        color: #475569;
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .nav-item .nav-icon {
        margin-right: 12px;
        font-size: 1.2rem;
        width: 24px;
    }
    
    /* Main content */
    .main-content {
        padding: 0 2rem;
    }
    
    /* Header section */
    .dashboard-header {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    .welcome-section {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    
    .welcome-text h1 {
        color: #1e293b;
        font-size: 2rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .welcome-text .username {
        color: #3b82f6;
        font-weight: 600;
    }
    
    .welcome-text p {
        color: #64748b;
        font-size: 1rem;
        margin: 0 0 1rem 0;
    }
    
    .read-more {
        color: #3b82f6;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
    }
    
    .time-selector {
        background: #3b82f6;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: none;
        font-weight: 500;
        cursor: pointer;
    }
    
    /* Metrics grid */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card.heart-rate {
        border-left: 4px solid #ef4444;
    }
    
    .metric-card.temperature {
        border-left: 4px solid #06b6d4;
    }
    
    .metric-card.blood-pressure {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        border-left: none;
    }
    
    .metric-card.glucose {
        border-left: 4px solid #eab308;
    }
    
    .metric-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .metric-icon {
        font-size: 1.5rem;
        margin-right: 8px;
    }
    
    .metric-title {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0;
    }
    
    .metric-card.blood-pressure .metric-title {
        color: rgba(255, 255, 255, 0.9);
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0.25rem 0;
    }
    
    .metric-card.blood-pressure .metric-value {
        color: white;
    }
    
    .metric-subtitle {
        color: #64748b;
        font-size: 0.8rem;
        margin: 0;
    }
    
    .metric-card.blood-pressure .metric-subtitle {
        color: rgba(255, 255, 255, 0.8);
    }
    
    /* Bottom section */
    .bottom-section {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 2rem;
    }
    
    .health-metrics {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .circular-metric {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    .circular-progress {
        width: 120px;
        height: 120px;
        margin: 0 auto 1rem;
        position: relative;
    }
    
    .circular-progress svg {
        transform: rotate(-90deg);
    }
    
    .circular-progress .progress-bg {
        fill: none;
        stroke: #e2e8f0;
        stroke-width: 8;
    }
    
    .circular-progress .progress-fill {
        fill: none;
        stroke-width: 8;
        stroke-linecap: round;
        transition: stroke-dashoffset 0.5s ease;
    }
    
    .water-balance .progress-fill {
        stroke: #06b6d4;
    }
    
    .general-health .progress-fill {
        stroke: #eab308;
    }
    
    .circular-value {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .circular-title {
        color: #64748b;
        font-size: 1rem;
        font-weight: 500;
        margin: 0;
    }
    
    .circular-subtitle {
        color: #94a3b8;
        font-size: 0.8rem;
        margin: 0.25rem 0 0 0;
    }
    
    /* Chart section */
    .chart-section {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .chart-title {
        color: #1e293b;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
    }
    
    .chart-period {
        background: #f1f5f9;
        color: #475569;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        border: none;
        font-size: 0.9rem;
        cursor: pointer;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-content {
            padding: 0 1rem;
        }
        
        .bottom-section {
            grid-template-columns: 1fr;
        }
        
        .metrics-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_circular_progress(percentage, color="#06b6d4"):
    """Create SVG circular progress indicator"""
    radius = 54
    circumference = 2 * 3.14159 * radius
    offset = circumference - (percentage / 100) * circumference
    
    return f"""
    <svg width="120" height="120">
        <circle cx="60" cy="60" r="{radius}" class="progress-bg"></circle>
        <circle cx="60" cy="60" r="{radius}" class="progress-fill" 
                style="stroke: {color}; stroke-dasharray: {circumference}; stroke-dashoffset: {offset};"></circle>
    </svg>
    """

def dashboard_sidebar():
    """Create dashboard sidebar"""
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">🏥</div>
        <h2>HealthCare</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize dashboard page in session state if not exists
    if 'dashboard_page' not in st.session_state:
        st.session_state.dashboard_page = 'Dashboard'
    
    # Navigation menu
    nav_items = [
        ("Dashboard", "📊", "Dashboard"),
        ("Heart", "❤️", "Heart"),
        ("Medications", "💊", "Medications"),
        ("Reports", "📋", "Reports")
    ]
    
    for item, icon, key in nav_items:
        if st.button(f"{icon} {item}", key=f"nav_{key}", use_container_width=True):
            st.session_state.dashboard_page = key
            st.rerun()
    
    st.markdown("---")
    
    # Logout button
    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        # Clear session state for logout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Logged out successfully!")
        st.rerun()

def dashboard_main():
    """Main dashboard content"""
    # Ensure user is logged in
    if 'user_id' not in st.session_state or 'username' not in st.session_state:
        st.error("Please log in to access the dashboard")
        return
    
    # Generate sample data for demo
    generate_sample_data(st.session_state.user_id)
    
    # Get latest vital signs
    vital_signs = get_latest_vital_signs(st.session_state.user_id)
    
    # Default values if no data
    if vital_signs:
        systolic, diastolic, heart_rate, temperature, glucose, water_balance, general_health = vital_signs
    else:
        systolic, diastolic, heart_rate, temperature, glucose, water_balance, general_health = 120, 80, 75, 36.8, 95, 42, 61
    
    # Header section
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="welcome-section">
            <div class="welcome-text">
                <h1>Hello, <span class="username">{st.session_state.username}</span></h1>
                <p>Have a nice day and don't forget to take care of your health!</p>
                <a href="#" class="read-more">Read more →</a>
            </div>
            <button class="time-selector">THIS WEEK</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card heart-rate">
            <div class="metric-header">
                <div class="metric-icon">❤️</div>
                <h3 class="metric-title">Heart rate</h3>
            </div>
            <div class="metric-value">{heart_rate} <small>BPM</small></div>
            <p class="metric-subtitle">Pulse is the most important parameter for good health</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card temperature">
            <div class="metric-header">
                <div class="metric-icon">🌡️</div>
                <h3 class="metric-title">Temperature</h3>
            </div>
            <div class="metric-value">{temperature}°C</div>
            <p class="metric-subtitle">Temperature shows the body's ability to generate heat</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card blood-pressure">
            <div class="metric-header">
                <div class="metric-icon">🩺</div>
                <h3 class="metric-title">Blood pressure</h3>
            </div>
            <div class="metric-value">{systolic}/{diastolic}</div>
            <p class="metric-subtitle">Blood pressure can rise and fall throughout the day</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card glucose">
            <div class="metric-header">
                <div class="metric-icon">🍯</div>
                <h3 class="metric-title">Glucose</h3>
            </div>
            <div class="metric-value">{glucose} <small>mg/dl</small></div>
            <p class="metric-subtitle">The normal concentration of glucose in the blood</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Bottom section
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        # Water balance circular progress
        st.markdown(f"""
        <div class="circular-metric water-balance">
            <div class="circular-progress">
                {create_circular_progress(water_balance, "#06b6d4")}
                <div class="circular-value">{water_balance}%</div>
            </div>
            <h3 class="circular-title">Water balance</h3>
            <p class="circular-subtitle">The body's water balance</p>
        </div>
        """, unsafe_allow_html=True)
        
        # General health circular progress
        st.markdown(f"""
        <div class="circular-metric general-health">
            <div class="circular-progress">
                {create_circular_progress(general_health, "#eab308")}
                <div class="circular-value">{general_health}%</div>
            </div>
            <h3 class="circular-title">General Health</h3>
            <p class="circular-subtitle">Comprehensive health</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        # Blood pressure chart
        st.markdown("""
        <div class="chart-section">
            <div class="chart-header">
                <h3 class="chart-title">Activity Analytics</h3>
                <select class="chart-period">
                    <option>Week</option>
                </select>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Get BP history and create chart
        bp_history = get_bp_history(st.session_state.user_id, 7)
        
        if bp_history:
            # Convert to DataFrame
            df = pd.DataFrame(bp_history, columns=['Date', 'Systolic', 'Diastolic'])
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Create the blood pressure line chart
            fig = go.Figure()
            
            # Add systolic line
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Systolic'],
                mode='lines+markers',
                name='Systolic',
                line=dict(color='#ef4444', width=3),
                marker=dict(size=8)
            ))
            
            # Add diastolic line
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Diastolic'],
                mode='lines+markers',
                name='Diastolic',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                height=300,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#e2e8f0',
                    showline=False,
                    tickformat='%a'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#e2e8f0',
                    showline=False,
                    title='BP (mmHg)'
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No blood pressure data available. Start recording your vitals!")

def heart_page():
    """Heart monitoring page"""
    st.title("❤️ Heart Monitor")
    st.info("Heart monitoring page - Coming soon!")

def medications_page():
    """Medications page"""
    st.title("💊 Medications")
    st.info("Medications page - Coming soon!")

def reports_page():
    """Reports page"""
    st.title("📋 Reports")
    st.info("Reports page - Coming soon!")

def run_dashboard():
    """Main function to run the dashboard"""
    st.set_page_config(
        page_title="HealthCare Dashboard",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("Please log in to access the dashboard")
        st.stop()
    
    # Create vital signs table
    
    
    # Load custom CSS
    load_dashboard_css()
    
    # Sidebar
    with st.sidebar:
        dashboard_sidebar()
    
    # Main content based on selected page
    if 'dashboard_page' not in st.session_state:
        st.session_state.dashboard_page = 'Dashboard'
    
    if st.session_state.dashboard_page == "Dashboard":
        dashboard_main()
    elif st.session_state.dashboard_page == "Heart":
        heart_page()
    elif st.session_state.dashboard_page == "Medications":
        medications_page()
    elif st.session_state.dashboard_page == "Reports":
        reports_page()

# If running this file directly
if __name__ == "__main__":
    run_dashboard()