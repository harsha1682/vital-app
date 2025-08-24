import streamlit as st #type: ignore
import mysql.connector #type: ignore
from mysql.connector import Error #type: ignore
import pandas as pd #type: ignore
from datetime import datetime, date, timedelta
import plotly.graph_objects as go #type: ignore
import plotly.express as px #type: ignore
import random
import numpy as np #type: ignore


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
    

def create_medications_table():
    """Create medications table if it doesn't exist"""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS medications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                medication_name VARCHAR(255) NOT NULL,
                time_hour INT NOT NULL,
                dose DECIMAL(10,2) NOT NULL,
                medication_type VARCHAR(100),
                start_day VARCHAR(50),
                end_day VARCHAR(50),
                duration VARCHAR(100),
                comments VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            cursor.close()
            connection.close()
        except Error as e:
            st.error(f"Error creating medications table: {e}")


def add_medication(medication_name, time_hour, dose, medication_type, start_day, end_day, duration, comments):
    """Add a new medication to the database"""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
            INSERT INTO medications (medication_name, time_hour, dose, medication_type, start_day, end_day, duration, comments)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (medication_name, time_hour, dose, medication_type, start_day, end_day, duration, comments))

            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f"Error adding medication: {e}")
            return False
    return False


def get_all_medications():
    """Retrieve all medications from the database"""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            select_query = "SELECT * FROM medications ORDER BY created_at DESC"
            cursor.execute(select_query)
            medications = cursor.fetchall()
            cursor.close()
            connection.close()
            return medications
        except Error as e:
            st.error(f"Error retrieving medications: {e}")
            return []
    return []


def delete_medication(medication_id):
    """Delete a medication from the database"""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            delete_query = "DELETE FROM medications WHERE id = %s"
            cursor.execute(delete_query, (medication_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f"Error deleting medication: {e}")
            return False
    return False


def load_med_css():
    """Load custom CSS for medications page"""
    st.markdown("""
    <style>
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
    
    .metric-card.medication-card {
        border-left: 4px solid #3b82f6;
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
        color: #1e293b;
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
    }
    
    .metric-value {
        font-size: 1.2rem;
        font-weight: 500;
        color: #64748b;
        margin: 0.25rem 0;
    }
    
    .metric-detail {
        color: #64748b;
        font-size: 0.875rem;
        margin: 0.25rem 0;
    }
    
    /* medications box */
    .med-header {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    .med-section {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    
    .med-text h1 {
        color: #1e293b;
        font-size: 2rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .med-text p {
        color: #64748b;
        font-size: 1rem;
        margin: 0 0 1rem 0;
    }
    
    .success-message {
        background-color: #d1fae5;
        color: #065f46;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
    }
    
    .delete-btn {
        background-color: #ef4444;
        color: white;
        border: none;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        cursor: pointer;
    }
    
    .emjbblw1 {
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)


def display_medication_cards(medications):
    """Display medication cards in the sidebar"""
    if not medications:
        st.markdown("""
        <div class="metric-card medication-card">
            <div class="metric-header">
                <div class="metric-icon">💊</div>
                <h3 class="metric-title">No Medications</h3>
            </div>
            <p class="metric-detail">Add your first medication using the form</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    for med in medications:
        # Get appropriate icon based on medication type
        icon = "💊"
        if med.get('medication_type'):
            med_type = med['medication_type'].lower()
            if 'liquid' in med_type:
                icon = "🧪"
            elif 'injection' in med_type:
                icon = "💉"
            elif 'inhaler' in med_type:
                icon = "🌬️"
        
        st.markdown(f"""
        <div class="metric-card medication-card">
            <div class="metric-header">
                <div class="metric-icon">{icon}</div>
                <h3 class="metric-title">{med['medication_name']}</h3>
            </div>
            <p class="metric-value">Time: {med['time_hour']}:00</p>
            <p class="metric-detail">Dose: {med['dose']}</p>
            <p class="metric-detail">Type: {med.get('medication_type', 'Not specified')}</p>
            <p class="metric-detail">Duration: {med.get('duration', 'Not specified')}</p>
            {f"<p class='metric-detail'>Period: {med.get('start_day', '')} - {med.get('end_day', '')}</p>" if med.get('start_day') else ""}
            <p class="metric-detail"> {med.get('comments')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Add delete button
        if st.button(f"🗑️ Delete", key=f"delete_{med['id']}", help="Delete this medication"):
            if delete_medication(med['id']):
                st.success("Medication deleted successfully!")
                st.rerun()


def run_med_page():
    # Load CSS
    load_med_css()
    
    # Create table if it doesn't exist
    create_medications_table()
    
    st.markdown(f"""
    <div class="med-header">
        <div class="med-section">
            <div class="med-text">
                <h1>👩🏻‍⚕️ Medication Reminder</h1>
                <p>Stay consistent with your medicines — each dose is a step towards better health!</p> 
                <p>You've got this 🙌</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns layout
    col1, col2 = st.columns([1, 2], gap="small")
    
    
    with col1:
        st.subheader("Current Medications")
        medications = get_all_medications()
        display_medication_cards(medications)
        
        # Show total count
        st.info(f"Total Medications: {len(medications)}")
    
    
    with col2:
        st.subheader("Add New Medication")
        
        # Create form
        with st.form("medication_form", clear_on_submit=True):
            medication1 = st.container(border=True)
            
            with medication1:
                medication_name = st.text_input("Medication Name")
                med1, med2 = st.columns(2)
                with med1:
                    time_hour = st.number_input("Time (Hour)", min_value=0, max_value=23, value=8, help="24-hour format")
                with med2:
                    dose = st.number_input("Dose", min_value=0.1, max_value=1000.0, value=1.0, step=0.1)
            
            medication2 = st.container(border=True)
            with medication2:
                medication_type = st.text_input("Type")
                day, end = st.columns(2)
                with day:
                    start_day = st.text_input("Start Day")
                with end:
                    end_day = st.text_input("End Day")
                
            medication3 = st.container(border=True)
            with medication3:
                duration = st.text_input("Duration")
                comments= st.text_input("Comments (if not any, please type 'None')")
            
            # Form submit button
            submitted = st.form_submit_button("Add Medication", type="primary")
            
            if submitted:
                # Validate required fields
                if not medication_name:
                    st.error("Please enter a medication name")
                elif not medication_type:
                    st.error("Please enter the medication type")
                else:
                    # Add medication to database
                    success = add_medication(
                        medication_name=medication_name,
                        time_hour=time_hour,
                        dose=dose,
                        medication_type=medication_type,
                        start_day=start_day,
                        end_day=end_day,
                        duration=duration,
                        comments=comments,
                    )
                    
                    if success:
                        st.success("Medication added successfully!")
                        st.rerun()  # Refresh the page to show the new medication
                    else:
                        st.error("Failed to add medication. Please try again.")
        


if __name__ == "__main__":
    run_med_page()