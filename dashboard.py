import streamlit as st #type: ignore
import mysql.connector #type: ignore
from mysql.connector import Error #type: ignore

from datetime import datetime, date, timedelta #type: ignore

import random #type: ignore
import numpy as np #type: ignore
import hashlib

import heart
import medications




DB_CONFIG = {
    'host': 'localhost',
    'database': 'vital_signs_db',
    'user': 'root',
    'password': '1234'
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
        

        # Create vital_results table
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

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def update_user(user_id, username, email, password, age, weight, height, blood_type, allergies, diseases):
    """Update user profile information"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
            
        # Update user with specific id
        cursor.execute("""
        UPDATE users SET username=%s, email=%s, password=%s, age=%s, weight=%s, height=%s, 
        blood_type=%s, allergies=%s, diseases=%s WHERE id = %s
        """, (username, email, hashed_password, age, weight, height, blood_type, allergies, diseases, user_id))
            
        connection.commit()
        cursor.close()
        connection.close()
        return True
    return False

def delete_user(user_id):
    """Delete user account and all associated data"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            
        connection.commit()
        cursor.close()
        connection.close()
        return True
        
    return False

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
            # Checks if data already exists
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
    /* Main dashboard background */
    .stApp {
        background: #f8fafc !important;
    }
                
    /* Global heading colors - make all black */
    h1, h2, h3, h4, h5, h6,
    .stSubheader,
    [data-testid="stSubheader"] {
        color: black !important;
    }
    
    /* Make input labels black */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    label {
        color: black !important;
        font-weight: 500 !important;
    }

    /* Also target the label text specifically */
    .stTextInput > label > div,
    .stNumberInput > label > div,
    .stSelectbox > label > div {
        color: black !important;
    }

    /* Target Streamlit's label spans */
    [data-testid="stWidgetLabel"] {
        color: black !important;
    }

    /* Make sure placeholder text is visible but lighter */
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {
        color: #64748b !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #07635b 0%, #0a4d47 100%) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 50px !important;
        padding: 12px 20px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        margin: 5px 0 !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        transform: translateX(5px) !important;
    }
    
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1F5675, #44A08D) !important;
        color: white !important;
        border: none !important;
        padding: 12px 32px !important;
        border-radius: 25px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(76, 205, 196, 0.4) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 205, 196, 0.6) !important;
    }
    
    /* Deploy Bar Color */
    .est0q592 {
        background: #17a2b8 !important;
    }
    
    /* Header section */
    .dashboard-header {
        background: white !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        margin-bottom: 2rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .welcome-section {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    
    .welcome-text h1 {
        color: #1e293b !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin: 0 0 0.5rem 0 !important;
    }
    
    .welcome-text .username {
        color: #3b82f6 !important;
        font-weight: 600 !important;
    }
    
    .welcome-text p {
        color: #64748b !important;
        font-size: 1rem !important;
        margin: 0 0 1rem 0 !important;
    }
    
    /* Metrics cards */
    .metric-card {
        background: white !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e2e8f0 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        margin-bottom: 20px !important;
        min-height: 250px !important;
        max-height: 250px !important;
    }
    
    .metric-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    .metric-card.heart-rate {
        border-left: 4px solid #ef4444 !important;
    }
    
    .metric-card.temperature {
        border-left: 4px solid #06b6d4 !important;
    }
    
    .metric-card.blood-pressure {
        border-left: 4px solid #8C1007 !important;
    }
    
    .metric-card.glucose {
        border-left: 4px solid #eab308 !important;
    }
    
    .metric-card.water {
        min-height: 460px !important;
        border-left: 4px solid #262657 !important;
    }
    
    .metric-card.blood-status {
        border-left: 4px solid #eab308 !important;
    }
    
    .metric-card.glucose-level {
        border-left: 4px solid #eab308 !important;
    }
    
    .metric-card.waterbalance {
        min-height: 100px !important;
        border-left: 4px solid #06b6d4 !important;
    }
    
    .metric-card.medication-card {
        border-left: 4px solid #3b82f6 !important;
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
        color: black !important;
        font-size: 1.5rem !important;
        margin: 0 !important;
    }
    
    .metric-value {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        margin: 0.25rem 0 !important;
    }

    .metric-subtitle {
        color: #64748b !important;
        font-size: 0.8rem !important;
        margin: 0 !important;
    }
    
    .metric-subtitle.water {
        color: #64748b !important;
        font-size: 1.25rem !important;
        margin: 0 !important;
    }
    
    .metric-detail {
        color: #64748b !important;
        font-size: 0.875rem !important;
        margin: 0.25rem 0 !important;
    }
    
    .divider-line {
        height: 1px;   
        background: #64748b;  
        margin: 0.5rem 0;        
    }
    
    /* Profile section */
    .profile-section {
        background: white !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid #e2e8f0 !important;
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
        color: #1e293b !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    
    .profile-value {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        margin: 0.25rem 0 !important;
    }
    
    .profile-subtitle {
        color: #64748b !important;
        font-size: 0.8rem !important;
        margin: 0 !important;
    }
    
    .profile-details p {
        margin: 6px 0 !important;
        font-size: 20px !important;
        color: #444 !important;
    }
                
    /* Form sections */
    .form-section {
        margin-bottom: 1.5rem;
    }
    
    .form-section h4 {
        color: #2c3e50 !important;
        font-size: 1.1rem !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid #4ECDC4 !important;
        font-weight: 600 !important;
    }
    

    /* Input fields styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
        padding: 10px 12px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #17a2b8 !important;
        box-shadow: 0 0 0 3px rgba(23, 162, 184, 0.1) !important;
    }
    
    
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-content {
            padding: 0 1rem;
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
    
    
    if st.button("Logout", key="logout_btn", use_container_width=True):
        # Clear session state for logout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Logged out successfully!")
        st.rerun()

def show_edit_profile_form(user_data):
    """Show edit profile form with current user data"""
    username, email, age, weight, height, blood_type, allergies, diseases, created_at = user_data
    
    st.markdown('<div class="form-section"><h3>Edit Profile</h3></div>', unsafe_allow_html=True)
    
    col_form1, col_form2 = st.columns(2)
    with col_form1:
        new_username = st.text_input("Name", value=username, placeholder="Full name", key="edit_username")
        new_password = st.text_input("New Password", type="password", placeholder="Enter new password", key="edit_password")
    
    with col_form2:
        new_email = st.text_input("Email", value=email, placeholder="Email address", key="edit_email")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password", key="edit_confirm_password")
    
    
    st.markdown('<div class="form-section"><h4>🏥 Medical Information</h4></div>', unsafe_allow_html=True)
    
    col_med1, col_med2 = st.columns(2)
    with col_med1:
        new_age = st.number_input("Age", min_value=1, max_value=120, value=int(age) if age else 25, key="edit_age")
        new_height = st.number_input("Height (cm)", min_value=50, max_value=250, value=int(height) if height else 170, key="edit_height")
        
        
        blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        blood_type_index = blood_types.index(blood_type) if blood_type in blood_types else 0
        new_blood_type = st.selectbox("Blood Type", blood_types, index=blood_type_index, key="edit_blood")
    
    with col_med2:
        new_weight = st.number_input("Weight (kg)", min_value=20, max_value=300, value=int(weight) if weight else 70, key="edit_weight")
        new_allergies = st.text_input("Allergies", value=allergies if allergies else "", placeholder="Any allergies (optional)", key="edit_allergies")
        new_diseases = st.text_input("Medical Conditions", value=diseases if diseases else "", placeholder="Any conditions (optional)", key="edit_diseases")
    
    col_save, col_cancel = st.columns(2)
    
    with col_save:
        save_button = st.button("Save Changes", key="save_profile_details_button", type="primary")
    
    with col_cancel:
        cancel_button = st.button("Cancel", key="cancel_edit_button")
    
    if save_button:
        if not new_username or not new_email or not new_password:
            st.error("Please fill in all required fields (Name, Email, Password)")
            return False
        
        if new_password != confirm_password:
            st.error("Passwords do not match!")
            return False
        
        if len(new_password) < 6:
            st.error("Password must be at least 6 characters long!")
            return False
        
        # Update user
        if update_user(st.session_state.user_id, new_username, new_email, new_password, 
                      new_age, new_weight, new_height, new_blood_type, new_allergies, new_diseases):
            st.success("Profile updated successfully!")
            st.session_state.username = new_username
            st.session_state.edit_mode = False #clears edit mode
            st.rerun()
        else:
            st.error("Failed to update profile. Please try again.")
        return True
    
    if cancel_button:
        st.session_state.edit_mode = False
        st.rerun()
        return False
    
    return False

def show_delete_confirmation():
    confirm_delete = st.checkbox("I understand that this action is irreversible", key="delete_confirmation")
    
    col_delete, col_cancel_delete = st.columns(2)
    
    with col_delete:
        delete_confirmed = st.button("Delete My Account", key="confirm_delete_button", disabled=not confirm_delete, type="primary")
    
    with col_cancel_delete:
        cancel_delete = st.button("Cancel", key="cancel_delete_button")
    
    if delete_confirmed and confirm_delete:
        if delete_user(st.session_state.user_id):
            st.success("Account deleted successfully!")
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        else:
            st.error("Failed to delete account. Please try again.")
    
    if cancel_delete:
        st.session_state.delete_mode = False
        st.rerun()

def dashboard_main():
    """Main dashboard content"""
    # ensures user is logged in (have to log in to access dashboard)
    if 'user_id' not in st.session_state or 'username' not in st.session_state:
        st.error("Please log in to access the dashboard")
        return
    
    # initialize edit and delete modes
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'delete_mode' not in st.session_state:
        st.session_state.delete_mode = False
    
    # sample data 
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
            <div class="metric-value"><small> You have had</small> {water_balance} <small>glasses of water today!</small></div>
            <div class="divider-line"></div>
            <p class="metric-subtitle water">Drinking enough water boosts your energy, keeps your brain sharp, helps your heart stay healthy, and makes your body feel fresh all day!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        #get user details
        user=get_user_profile(st.session_state.user_id)

        if user:
            # Check if we're in edit or delete mode
            if st.session_state.edit_mode:
                show_edit_profile_form(user)
            elif st.session_state.delete_mode:
                show_delete_confirmation()
            else:
                username, email, age, weight, height, blood_type, allergies, diseases, created_at = user
                
                # Normal profile display
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
                            <p><b>Allergies:</b> {allergies if allergies else 'None'}</p>
                            <p><b>Diseases:</b> {diseases if diseases else 'None'}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Edit Profile", key="edit_profile_button", type="primary"):
                        st.session_state.edit_mode = True
                        st.rerun()
                
                with col2:
                    if st.button("Delete Account", key="delete_account_button", type="secondary"):
                        st.session_state.delete_mode = True
                        st.rerun()
        
        
def run_dashboard():
    """Main function to run the dashboard"""
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
