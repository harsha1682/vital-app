import streamlit as st #type: ignore
import mysql.connector #type: ignore
from mysql.connector import Error #type: ignore
import pandas as pd #type: ignore
from datetime import datetime, date, timedelta
import plotly.graph_objects as go #type: ignore
import plotly.express as px #type: ignore
import random
import numpy as np #type: ignore


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
    
    .metric-card.medication-one {
        border-left: 4px solid #eab308;
    }
    
    .metric-card.medication-two {
        border-left: 4px solid #06b6d4;
    }
    
    .metric-card.medication-three {
        border-left: 4px solid #8C1007;
    }
    
    .metric-card.medications-four {
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
    
    .med-text h3 {
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
    </style>
    """, unsafe_allow_html=True)

def run_med_page():
    st.title("Your Medications")
    col1, col2, col3=st.columns([1,1,2], gap="small", border=True)
        # Metrics grid
    with col1:
        st.markdown(f"""
        <div class="metric-card medication-one">
            <div class="metric-header">
                <div class="metric-icon">🩸</div>
                <h3 class="metric-title">Medication 1</h3>
            </div>
        </div>
        <div class="metric-card medication-two">
                <div class="metric-header">
                    <div class="metric-icon">🫀</div>
                    <h3 class="metric-title">Medication 2</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)
    

    with col2:
        st.markdown(f"""
            <div class="metric-card medication-three">
                <div class="metric-header">
                    <div class="metric-icon">🩸</div>
                    <h3 class="metric-title">Medication 3</h3>
                </div>
            </div>
            <div class="metric-card medication-four">
                    <div class="metric-header">
                        <div class="metric-icon">🫀</div>
                        <h3 class="metric-title">Medication 4</h3>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
    with col3:
        medication1, = st.columns(1, border=True)
    
        with medication1:
            medication_name = st.text_input("Medication Name", placeholder="Enter medication name")
            med1, med2= st.columns(2)
            with med1:
                time1 = st.number_input("Time", min_value=1, max_value=24)
            with med2:
                dose = st.number_input("Dose", min_value=1, max_value=20)
        
        medication2, = st.columns(1, border=True)
        with medication2:
            type_med = st.text_input("Type: ", placeholder="pills, liquid, injection etc")
            day, end = st.columns(2, border=True, gap='small')
            with day:
                start_day = st.text_input("Start Day", placeholder="e.g., 79-92", key="diag_blood_count")
            with end:
                end_day = st.text_input("End Day")
            
        medication3, =st.columns(1, border=True)
        with medication3:
            duration = st.text_input("Duration", placeholder="everyday, 1 week, 2 weeks etc")


    
if __name__ == "__main__":
    run_med_page()