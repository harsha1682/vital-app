import streamlit as st #type: ignore
import mysql.connector #type: ignore
from mysql.connector import Error #type: ignore
import pandas as pd #type: ignore
from datetime import datetime, date, timedelta #type: ignore
import plotly.graph_objects as go #type: ignore
import plotly.express as px #type: ignore
import random #type: ignore
import numpy as np #type: ignore

import heart
import medications
import reports


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

def create_tables():
    """Create necessary database tables if they don't exist"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            age INT,
            weight FLOAT,
            height FLOAT,
            blood_type VARCHAR(5),
            allergies TEXT,
            diseases TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Drop old tables if they exist
        cursor.execute("DROP TABLE IF EXISTS vital_signs")
        cursor.execute("DROP TABLE IF EXISTS heart_results")
        
        # Create new unified vital_results table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vital_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            date_recorded DATE NOT NULL,
            systolic_bp INT,
            diastolic_bp INT,
            heart_rate INT,
            temperature DECIMAL(4,1),
            glucose_level INT,
            blood_status VARCHAR(20),
            water_balance INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
    return False

def get_user_profile(user_id):
    """Get user profile information"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            SELECT username, email, age, weight, height, blood_type, allergies, diseases, created_at 
            FROM users WHERE id = %s
            """, (user_id,))
            profile = cursor.fetchone()
            cursor.close()
            connection.close()
            return profile
        except Error as e:
            st.error(f"Error fetching user profile: {e}")
            cursor.close()
            connection.close()
    return None

def get_latest_vital_results(user_id):
    """Get latest vital results for dashboard"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            SELECT systolic_bp, diastolic_bp, heart_rate, temperature, glucose_level, blood_status, water_balance
            FROM vital_results WHERE user_id = %s ORDER BY date_recorded DESC LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result
        except Error as e:
            st.error(f"Error fetching vital results: {e}")
            cursor.close()
            connection.close()
    return None

def get_bp_history(user_id, days=7):
    """Get blood pressure history for the last N days"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            SELECT date_recorded, systolic_bp, diastolic_bp
            FROM vital_results 
            WHERE user_id = %s AND date_recorded >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            ORDER BY date_recorded ASC
            """, (user_id, days))
            
            records = cursor.fetchall()
            cursor.close()
            connection.close()
            return records
        except Error as e:
            st.error(f"Error fetching BP history: {e}")
            cursor.close()
            connection.close()
    return []

def generate_sample_data(user_id):
    """Generate sample vital results data for demo purposes"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        try:
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM vital_results WHERE user_id = %s", (user_id,))
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
                    blood_status = f"{systolic}/{diastolic}"
                    water_balance = random.randint(1, 10)
                    
                    cursor.execute("""
                    INSERT INTO vital_results (user_id, date_recorded, systolic_bp, diastolic_bp, 
                    heart_rate, temperature, glucose_level, blood_status, water_balance)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, date_record, systolic, diastolic, heart_rate, temperature, 
                         glucose, blood_status, water_balance))
                
                connection.commit()
        except Error as e:
            st.error(f"Error generating sample data: {e}")
        finally:
            cursor.close()
            connection.close()

def load_dashboard_css():
    """Load custom CSS for dashboard"""
    st.markdown("""
    <style>
    
    
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
    .e1v5e29v2 {
        background: #07635b;
        border-right: 1px solid #e2e8f0;
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
        border-left: 4px solid #8C1007;
    }
    
    .metric-card.glucose {
        border-left: 4px solid #eab308;
    }
    
    .metric-card.water {
        border-left: 4px solid #262657;
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
        font-size: 0.5rem;
        font-weight: 500;
        margin: 0;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0.25rem 0;
    }

    
    .metric-subtitle {
        color: #64748b;
        font-size: 0.8rem;
        margin: 0;
    }
    
    /* Profile section */
    .profile-section {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    .profile-icon {
        font-size: 1.5rem;
        margin-right: 8px;
    }      
    .profile-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
                
    .profile-title {
        color: #1e293b;
        font-size; 1.25rem;
        font-weight: 600;
        margin: 0;    
    }
    
    .profile-value {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0.25rem 0;
    }
    
    .profile-subtitle {
        color: #64748b;
        font-size: 0.8rem;
        margin: 0;
    }
    
    .profile-details p {
        margin: 6px 0;
        font-size: 20px;
        color: #444;
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


def dashboard_sidebar():
    """Create dashboard sidebar"""
    st.image("Logo.png",  use_container_width=True)
    
    # Initialize dashboard page in session state if not exists
    if 'dashboard_page' not in st.session_state:
        st.session_state.dashboard_page = 'Dashboard'
    
    # Navigation menu
    nav_items = [
        ("Dashboard",  "Dashboard"),
        ("Heart", "Heart"),
        ("Medications", "Medications")
    ]
    
    for item, key in nav_items:
        if st.button(f"{item}", key=f"nav_{key}", use_container_width=True):
            st.session_state.dashboard_page = key
            st.rerun()
    
    st.markdown("---")
    
    # Logout button
    if st.button("Logout", key="logout_btn", use_container_width=True):
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
    
    # Get latest vital results
    vital_results = get_latest_vital_results(st.session_state.user_id)
    
    # Default values if no data
    if vital_results:
        systolic_bp, diastolic_bp, heart_rate, temperature, glucose_level, blood_status, water_balance = vital_results
    else:
        systolic_bp, diastolic_bp, heart_rate, temperature, glucose_level, blood_status, water_balance = 120, 80, 75, 36.8, 95, "120/80", 3
    
    # Header section
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="welcome-section">
            <div class="welcome-text">
                <h1>Hello, <span class="username">{st.session_state.username}</span></h1>
                <p>Have a nice day and don't forget to take care of your health!</p>
            </div>
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
            <p class="metric-subtitle">Pulse is the most important parameter to maintain good health </p>
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
            <p class="metric-subtitle">Temperature is the body's ability to generate heat</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card blood-pressure">
            <div class="metric-header">
                <div class="metric-icon">🩺</div>
                <h3 class="metric-title">Blood pressure</h3>
            </div>
            <div class="metric-value">{systolic_bp}/{diastolic_bp}</div>
            <p class="metric-subtitle">Blood pressure can rise and fall throughout the day</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card glucose">
            <div class="metric-header">
                <div class="metric-icon">💉</div>
                <h3 class="metric-title">Glucose</h3>
            </div>
            <div class="metric-value">{glucose_level} <small>mg/dl</small></div>
            <p class="metric-subtitle">Glucose is body's main source of energy to function properly</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Bottom section
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown(f"""
        <div class="metric-card water">
            <div class="metric-header">
                <div class="metric-icon">🥛</div>
                <h3 class="metric-title">Water Balance</h3>
            </div>
            <div class="metric-value"><small> you have had</small> {water_balance} <small>glasses of water today!</small></div>
            <p class="metric-subtitle">Drinking enough water boosts your energy and helps your heart stay healthy!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        #get user details
        user=get_user_profile(st.session_state.user_id)

        if user:
            username, email, age, weight, height, blood_type, allergies, diseases, created_at= user
            # Blood pressure chart
            st.markdown(f"""
            <div class="profile-section">
                <div class="profile-header">
                    <h3 class="profile-title">👤 Profile</h3>
                </div>
                <div class="profile-details">
                        <p><b>Patient Name:</b> {username}</p>
                        <p><b>Email:</b> {email}</p>
                        <p><b>Age:</b> {age}</p>  
                        <p><b>Weight:</b> {weight}</p>
                        <p><b>Height:</b> {height}</p>
                        <p><b>Blood type:</b> {blood_type}</p>
                        <p><b>Allergies:</b> {allergies}</p>
                        <p><b>Diseases:</b> {diseases}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        
        
        



def run_dashboard():
    """Main function to run the dashboard"""
    st.set_page_config(
        page_title="Dashboard",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("Please log in to access the dashboard")
        st.stop()
    
    # Create necessary tables
    if not create_tables():
        st.error("Failed to create database tables. Please check your database connection.")
        st.stop()
    
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
        import heart as heart 
        heart.run_heart_page()
    elif st.session_state.dashboard_page == "Medications":
        import medications as med
        med.run_med_page()

# If running this file directly
if __name__ == "__main__":
    run_dashboard()