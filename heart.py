import streamlit as st #type: ignore
import mysql.connector #type: ignore
from mysql.connector import Error #type: ignore
import pandas as pd #type: ignore
from datetime import datetime, date, timedelta
import plotly.graph_objects as go #type: ignore
import plotly.express as px #type: ignore
import random
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

def create_vital_results_table():
    """Create vital_results table if it doesn't exist"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create unified vital_results table
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

def get_latest_heart_results(user_id):
    """Get latest heart results from vital_results table"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            SELECT blood_status, heart_rate, systolic_bp, diastolic_bp, glucose_level, date_recorded
            FROM vital_results WHERE user_id = %s ORDER BY date_recorded DESC LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result
        except Error as e:
            st.error(f"Error fetching heart results: {e}")
            cursor.close()
            connection.close()
    return None

def get_heart_history(user_id, days=30):
    """Get heart history from vital_results table"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            SELECT blood_status, heart_rate, systolic_bp, diastolic_bp, glucose_level, date_recorded
            FROM vital_results 
            WHERE user_id = %s AND date_recorded >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            ORDER BY date_recorded DESC
            """, (user_id, days))
            
            records = cursor.fetchall()
            cursor.close()
            connection.close()
            return records
        except Error as e:
            st.error(f"Error fetching heart history: {e}")
            cursor.close()
            connection.close()
    return []

def get_complete_vital_record(user_id, date_recorded):
    """Get temperature and water_balance for a specific date"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            SELECT temperature, water_balance
            FROM vital_results 
            WHERE user_id = %s AND date_recorded = %s
            LIMIT 1
            """, (user_id, date_recorded))
            
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result
        except Error as e:
            st.error(f"Error fetching complete vital record: {e}")
            cursor.close()
            connection.close()
    return None

def save_heart_results(user_id, blood_status, heart_rate, systolic_bp, diastolic_bp, glucose_level, water_balance, temperature):
    """Save heart results to vital_results table"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
            INSERT INTO vital_results (user_id, blood_status, heart_rate, systolic_bp, diastolic_bp, 
            glucose_level, water_balance, temperature, date_recorded)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, blood_status, heart_rate, systolic_bp, diastolic_bp, glucose_level, 
                 water_balance, temperature, date.today()))
            
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f"Error saving heart results: {e}")
            cursor.close()
            connection.close()
    return False

def generate_heart_sample_data(user_id):
    """Generate sample heart data for demo"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        try:
            # Check if vital results data exists
            cursor.execute("SELECT COUNT(*) FROM vital_results WHERE user_id = %s", (user_id,))
            results_count = cursor.fetchone()[0]
            
            if results_count == 0:
                # Generate sample results data
                for i in range(4):
                    date_record = date.today() - timedelta(days=3-i)
                    systolic = random.randint(110, 130)
                    diastolic = random.randint(70, 85)
                    blood_status = f"{systolic}/{diastolic}"
                    heart_rate = random.randint(110, 130)
                    glucose_level = random.randint(155, 170)
                    water_balance = random.randint(3, 8)
                    temperature = round(random.uniform(36.0, 37.5), 1)
                    
                    cursor.execute("""
                    INSERT INTO vital_results (user_id, blood_status, heart_rate, systolic_bp, diastolic_bp,
                    glucose_level, water_balance, temperature, date_recorded)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, blood_status, heart_rate, systolic, diastolic, glucose_level, 
                         water_balance, temperature, date_record))
                         
            connection.commit()

        except Error as e:
            st.error(f"Error generating heart sample data: {e}")
        finally:
            cursor.close()
            connection.close()

def load_heart_css():
    """Load custom CSS for heart page"""
    st.markdown("""
    <style>
    
    
    .heart-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .heart-icon {
        font-size: 2rem;
        margin-right: 1rem;
        color: #ef4444;
    }
    
    .heart-title {
        color: #1e293b;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
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
        margin-bottom: 20px;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card.blood-status {
        border-left: 4px solid #eab308;
    }
    
    .metric-card.heart-rate {
        border-left: 4px solid #06b6d4;
    }
    
    .metric-card.blood-pressure {
        border-left: 4px solid #8C1007;
    }
    
    .metric-card.glucose-level {
        border-left: 4px solid #eab308;
    }
    
    .metric-card.temperature {
        border-left: 4px solid #06b6d4;
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
    
    
    /* medications box in history page */
    .medications-header {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    .medications-section {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    
    .medications-text h3 {
        color: #1e293b;
        font-size: 2rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .medications-text p {
        color: #64748b;
        font-size: 1rem;
        margin: 0 0 1rem 0;
    }
    
    
    /* Form section */
    .form-header {background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
                
    .form-section {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    
    .form-text h3 {
        color: #1e293b;
        font-size: 2rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }

                

    .body-image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        border-radius: 16px;
        margin-bottom: 2rem;
    }
    
    .body-image {
        max-width: 250px;
        width: 100%;
        height: auto;
    }
    
    
    
    .heart-metric-card {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease;
    }
    
    .heart-metric-card:hover {
        transform: translateY(-2px);
    }
    
    
    
    .history-card {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    .history-date {
        color: #6b7280;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    .diagnosis-form {
        background: #f8fafc;
        border-radius: 12px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    .form-section-title {
        color: #1e293b;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4ECDC4;
    }
    
    /* Style the input fields directly */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }
    
    .submit-button {
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
        margin-top: 2rem !important;
    }
    
    .submit-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 205, 196, 0.6) !important;
    }
    
    /* Heart tab navigation buttons */
    .stButton > button {
        background: #f8fafc !important;           
        color: #64748b !important;                
        border: 1px solid #e2e8f0 !important;   
        padding: 12px 20px !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stButton > button:hover {
        background: #e2e8f0 !important;          
        color: #475569 !important;                
        border-color: #cbd5e1 !important;        
        transform: none !important;
        box-shadow: none !important;
    }
    
    .stButton > button:focus {
        background: linear-gradient(135deg, #2196f3 , #44A08D) !important; 
        color: white !important;                  
        border-color: #1F5675 !important;         
        box-shadow: 0 2px 8px rgba(31, 86, 117, 0.3) !important;
    }
    
    /* Override for submit button to maintain original styling */
    .stButton[data-testid="submit_diagnosis"] > button {
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
        margin-top: 2rem !important;
    }
    
    .stButton[data-testid="submit_diagnosis"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 205, 196, 0.6) !important;
    }
    
    @media (max-width: 768px) {
        .metric-grid, .symptoms-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def heart_results_tab():
    """Heart Results Tab Content"""
    # Generate sample data
    generate_heart_sample_data(st.session_state.user_id)
    
    # Get latest results
    results = get_latest_heart_results(st.session_state.user_id)
    
    if results:
        blood_status, heart_rate, systolic_bp, diastolic_bp, glucose_level, date_recorded = results
        # Calculate blood count range for display
        blood_count = f"{diastolic_bp}-{systolic_bp}"
    else:
        blood_status, heart_rate, systolic_bp, diastolic_bp, glucose_level = "120/80", 120, 120, 80, 162
        blood_count = f"{diastolic_bp}-{systolic_bp}"
    
    

    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Heart image placeholder
        st.image("heartimage.png", width=450)
    
    with col2:
        st.title("Heart Health Monitor")
        heart1, heart2=st.columns(2, gap="small")
        # Metrics grid

        with heart1:
            st.markdown(f"""
            <div class="metric-card blood_status">
                <div class="metric-header">
                    <div class="metric-icon">🩸</div>
                    <h3 class="metric-title">Blood status</h3>
                </div>
                <div class="metric-value">{blood_status} ml</div>
            </div>

            <div class="metric-card heart-rate">
                <div class="metric-header">
                    <div class="metric-icon">🫀</div>
                    <h3 class="metric-title">Heart Rate</h3>
                </div>
                <div class="metric-value">{heart_rate} BPM</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with heart2:
            st.markdown(f"""
            <div class="metric-card blood-pressure">
                <div class="metric-header">
                    <div class="metric-icon">🩺</div>
                    <h3 class="metric-title">Blood Pressure</h3>
                </div>
                <div class="metric-value">{blood_count} BPM</div>
            </div>

            <div class="metric-card glucose-level">
                <div class="metric-header">
                    <div class="metric-icon">💉</div>
                    <h3 class="metric-title">Glucose Level</h3>
                </div>
                <div class="metric-value">{glucose_level} mg/dL </div>
            </div>

            """, unsafe_allow_html=True)



def heart_diagnosis_tab():
    
    
    col1, col2 = st.columns(2, border=True)
    
    with col1:
        blood_status = st.text_input("Blood Status (e.g., 120/80)", placeholder="Enter blood pressure", key="diag_blood_status")
        heart_rate = st.number_input("Heart Rate (BPM)", min_value=40, max_value=200, value=75, key="diag_heart_rate")
        water_balance = st.number_input("How many glasses of water have you drank today?", min_value=1, max_value=50)
    
    with col2:
        systolic_bp = st.number_input("Systolic BP", min_value=80, max_value=200, value=120, key="diag_systolic")
        diastolic_bp = st.number_input("Diastolic BP", min_value=40, max_value=120, value=80, key="diag_diastolic")
        glucose_level = st.number_input("Glucose Level (/ml)", min_value=50, max_value=300, value=100, key="diag_glucose")
        temperature = st.number_input("Temperature (°C)", min_value=30.0, max_value=45.0, value=36.8, step=0.1)

    
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        if st.button("Save", key="submit_diagnosis", use_container_width=True):
            if blood_status and heart_rate and water_balance and systolic_bp and diastolic_bp and glucose_level and temperature:
                # Save results
                if save_heart_results(st.session_state.user_id, blood_status, heart_rate, systolic_bp, diastolic_bp, glucose_level, water_balance, temperature):
                    st.success("✅ Results saved successfully!")
                    st.balloons()
                    # Refresh to show new data
                    st.rerun()
                else:
                    st.error("❌ Failed to save results")
            else:
                st.error("⚠️ Please fill in all required fields")
    
    st.markdown('</div>', unsafe_allow_html=True)

def heart_history_tab():
    # Get results history
    results_history = get_heart_history(st.session_state.user_id, 30)
    
    if results_history:
        date_options = [r[5] for r in results_history]  # date_recorded is at index 5
        
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            selected_date = st.selectbox("Choose date", date_options, index=0)

        # Filter results for selected date
        filtered_results = [r for r in results_history if r[5] == selected_date]  # date_recorded is at index 5

        for result in filtered_results:
            # Unpack all 6 values from the query result
            blood_status, heart_rate, systolic_bp, diastolic_bp, glucose_level, date_recorded = result
            
            # Calculate blood count range for display
            blood_count = f"{diastolic_bp}-{systolic_bp}"
            st.markdown("---")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card blood-status">
                    <div class="metric-header">
                        <div class="metric-icon">🩸</div>
                        <h3 class="metric-title">Blood Status</h3>
                    </div>
                    <div class="metric-value">{blood_status}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card heart-rate">
                    <div class="metric-header">
                        <div class="metric-icon">🫀</div>
                        <h3 class="metric-title">Heart Rate</h3>
                    </div>
                    <div class="metric-value">{heart_rate} BPM</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col3:
                st.markdown(f"""
                <div class="metric-card blood-pressure">
                    <div class="metric-header">
                        <div class="metric-icon">🩺</div>
                        <h3 class="metric-title">Blood Pressure</h3>
                    </div>
                    <div class="metric-value">{blood_count} BPM</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col4:
                st.markdown(f"""
                <div class="metric-card glucose-level">
                    <div class="metric-header">
                        <div class="metric-icon">💉</div>
                        <h3 class="metric-title">Glucose Level</h3>
                    </div>
                    <div class="metric-value">{glucose_level} mg/dL</div>
                </div>
                """, unsafe_allow_html=True)
        
            st.markdown("---")
            
            # Now we need to get temperature and water_balance from the database
            # Get the complete record for this date
            temp_water_result = get_complete_vital_record(st.session_state.user_id, date_recorded)
            
            if temp_water_result:
                temperature, water_balance = temp_water_result
            else:
                # Default values if not found
                temperature, water_balance = 36.8, 3
            
            temp, water = st.columns(2)
            with temp:
                st.markdown(f"""
                <div class="metric-card temperature">
                    <div class="metric-header">
                        <div class="metric-icon">🌡️</div>
                        <h3 class="metric-title">Temperature</h3>
                    </div>
                    <div class="metric-value">{temperature}°C</div>
                </div>
                """, unsafe_allow_html=True)
            
            with water:
                st.markdown(f"""
                <div class="metric-card water">
                    <div class="metric-header">
                        <div class="metric-icon">🥛</div>
                        <h3 class="metric-title">Water Balance</h3>
                    </div>
                    <div class="metric-value"><small>you have had</small> {water_balance} <small>glasses of water today!</small></div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.info("No results history found.")
    
    st.markdown("---") 


def run_heart_page():
    """Main function to run the heart page"""
    # Create vital_results table
    create_vital_results_table()
    
    # Load CSS
    load_heart_css()
    
    # Initialize heart tab in session state if not exists
    if 'heart_tab' not in st.session_state:
        st.session_state.heart_tab = 'Results'
    
    
    
    # Tab navigation buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Results", key="heart_results_btn", use_container_width=True):
            st.session_state.heart_tab = 'Results'
            st.rerun()
    
    with col2:
        if st.button("History", key="heart_history_btn", use_container_width=True):
            st.session_state.heart_tab = 'History'
            st.rerun()
    
    with col3:
        if st.button("Diagnosis", key="heart_diagnosis_btn", use_container_width=True):
            st.session_state.heart_tab = 'Diagnosis'
            st.rerun()
    
    
    
    st.markdown("---")
    
    # Display content based on selected tab
    if st.session_state.heart_tab == 'Results':
        heart_results_tab()
    elif st.session_state.heart_tab == 'History':
        heart_history_tab()
    elif st.session_state.heart_tab == 'Diagnosis':
        heart_diagnosis_tab()
    
    st.markdown('</div>', unsafe_allow_html=True)

# If running this file directly
if __name__ == "__main__":
    run_heart_page()