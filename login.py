import streamlit as st #type: ignore
import mysql.connector #type: ignore
from mysql.connector import Error #type: ignore
import hashlib
import base64
import time

from pathlib import Path

DB_CONFIG = {
    'host': 'localhost',
    'database': 'vital_signs_db',
    'user': 'root',
    'password': 'H0ney123'
}


# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'


def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None
    
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user():
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

        connection.commit()
        cursor.close()
        connection.close()
        return True
    return False

def register_user(username, password, email, age, weight, height, blood_type, allergies, diseases):
    """Register a new user"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        
        try:
            cursor.execute("""
            INSERT INTO users (username, password, email, age, weight, height, blood_type, allergies, diseases)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, hashed_password, email, age, weight, height, blood_type, allergies, diseases))
            
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f"Registration failed: {e}")
            return False
    return False

def login_user(email, password):
    """Authenticate user login"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        
        cursor.execute("SELECT id, username FROM users WHERE email = %s AND password = %s", 
                      (email, hashed_password))
        user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.username = user[1]
            return True
    return False



def get_base64_of_bin_file(background):
    with open(background, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = get_base64_of_bin_file("bg.png")


st.markdown(f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{bg_image}") no-repeat center center fixed;
        background-size: 100% auto;
    }}
    </style>
""", unsafe_allow_html=True)



def load_medical_css():
    """Load custom CSS for medical theme"""
    st.markdown("""
    <style>

                
    /* Main container */
    .login-main-container {
        display: flex;
        min-height: 100vh;
        width: 100%;
        position: relative;
        overflow: hidden;
    }
    

    /* Right side with form */
    .form-side {
        flex: 1;
        background: #f8f9fa;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        position: relative;
    }
    
    .form-side::before {
        content: '';
        position: absolute;
        top: 0;
        left: -50px;
        width: 100px;
        height: 100%;
        background: linear-gradient(90deg, #1f5675, transparent);
        transform: skewX(-10deg);
        z-index: 1;
    }
    
    /* Form container */
    .form-container {
        background: #ffffff;
        padding: 3rem 2.5rem;
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        width: 100%;
        max-width: 400px;
        position: relative;
        z-index: 2;
        border: 1px solid rgba(76, 205, 196, 0.1);
    }
    
    .form-title {
        color: #2c3e50;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        background: #f1f3f4 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
        color: #2c3e50 !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        background: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(76, 205, 196, 0.2) !important;
        outline: none !important;
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
    
    
    
    /* Form sections for signup */
    .form-section {
        margin-bottom: 1.5rem;
    }
    
    .form-section h4 {
        color: #2c3e50;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4ECDC4;
        font-weight: 600;
    }
    
    .e1hznt4w0 {
        color: black;
    }
                
    /* Mobile responsive */
    @media (max-width: 768px) {
        
        .form-side {
            min-height: 60vh;
            padding: 1rem;
        }
        
        .form-container {
            padding: 2rem 1.5rem;
        }
        
    }
    </style>
    """, unsafe_allow_html=True)


def login_page():
    """Login page UI"""
    col1, col2, col3 = st.columns([0.5, 0.2, 1], gap="large")

    
    with col3:
        first, second, third= st.columns([1,2,1])
        with second: 
            st.title("Log in")
            # Login form
            email = st.text_input("Email", placeholder="Enter your email address", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
        
            col_btn1, col_btn2, col_btn3 = st.columns([0.5, 2, 0.5], gap="small")
            with col_btn2:
                login_clicked = st.button("LOG IN", key="login_btn", use_container_width=True)
        
            if login_clicked:
                if email and password:
                    if login_user(email, password):
                        st.success("Login successful! Redirecting...")
                        st.balloons()
                        time.sleep(1)
                        #rerun app
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
                else:
                    st.warning("⚠️ Please enter both email and password")
        
            # switch to signup link
            st.markdown("---")
            col_link1, col_link2, col_link3 = st.columns([0.2, 6, 0.2])
            with col_link2:
                if st.button("Don't have an account? Sign up", key="switch_signup", use_container_width=True):
                    st.session_state.current_page = 'signup'
                    st.rerun()
        
            st.markdown("</div></div>", unsafe_allow_html=True)

def signup_page():
    """Signup page UI"""
    col1, col2 = st.columns([1, 1], gap="large")

    with col2:
        

        st.markdown('<div class="form-section"><h4>👤 Basic Information</h4></div>', unsafe_allow_html=True)
        
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            username = st.text_input("Name", placeholder="Full name", key="signup_username")
            password = st.text_input("Password", type="password", placeholder="Create password", key="signup_password")
        
        with col_form2:
            email = st.text_input("Email", placeholder="Email address", key="signup_email")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="confirm_password")
        
        
        st.markdown('<div class="form-section"><h4>🏥 Medical Information</h4></div>', unsafe_allow_html=True)
        
        col_med1, col_med2 = st.columns(2)
        with col_med1:
            age = st.number_input("Age", min_value=1, max_value=120, value=25, key="signup_age")
            height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170, key="signup_height")
            blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], key="signup_blood")
        
        with col_med2:
            weight = st.number_input("Weight (kg)", min_value=20, max_value=300, value=70, key="signup_weight")
            allergies = st.text_input("Allergies", placeholder="Any allergies (optional)", key="signup_allergies")
            diseases = st.text_input("Medical Conditions", placeholder="Any conditions (optional)", key="signup_diseases")
        
        # Register button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            register_clicked = st.button("REGISTER", key="signup_btn", use_container_width=True)
        
        if register_clicked:
            if password != confirm_password:
                st.error("❌ Passwords don't match!")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters long!")
            elif not all([username, password, email, age, weight, height]):
                st.error("❌ Please fill in all required fields!")
            else:
                if register_user(username, password, email, age, weight, height, blood_type, allergies, diseases):
                    st.success("✅ Account created successfully!")
                    st.balloons()
                    st.info("Please switch to Login to access your account.")
                else:
                    st.error("❌ Registration failed. Email may already exist.")
        
        # switch to login link
        st.markdown("---")
        col_link1, col_link2, col_link3 = st.columns([1, 2, 1])
        with col_link2:
            if st.button("Already have an account? Log in", key="switch_login", use_container_width=True):
                st.session_state.current_page = 'login'
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)


def show_dashboard_placeholder():
    """Show dashboard placeholder if dashboard module is not available"""
    st.success("🎉 Welcome to your HealthCare Dashboard!")
    st.info("Dashboard is loading... Please make sure dashboard.py is in the same directory.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Heart Rate", "75 BPM", "2 BPM")
    
    with col2:
        st.metric("Blood Pressure", "120/80", "-5 mmHg")
    
    with col3:
        st.metric("Temperature", "36.8°C", "0.2°C")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        # clear session state for logout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()



def main():
    """Main application"""
    st.set_page_config(
        page_title="HomeCare",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    
    create_user()
    # Load custom CSS
    load_medical_css()

    
if st.session_state.logged_in:
    try: 
        import dashboard as dash
        dash.run_dashboard()
    except ImportError:
        show_dashboard_placeholder()
else:

    st.markdown('<div class="login-main-container">', unsafe_allow_html=True)
    

    if st.session_state.current_page == 'login':
        login_page()
    else:
        signup_page()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()