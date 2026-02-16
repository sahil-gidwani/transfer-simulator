import streamlit as st

st.set_page_config(
    page_title="Football Transfer Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Football Transfer Analytics Platform")

st.divider()

st.markdown(
    """
    ### Welcome to the Transfer Analytics Platform
    
    This application provides two complementary approaches to understanding and predicting 
    player performance across different leagues and teams:
    
    **1. ML-Based Performance Prediction**
    - Uses historical transfer data to predict player performance metrics
    - Employs gradient boosting regression on aggregated player statistics
    - Ideal for understanding general trends and patterns in player transfers
    
    **2. Rule-Based Transfer Simulation**
    - Simulates specific player transfers using team and league ratings
    - Applies scaling factors based on competitive differences
    - Useful for scenario analysis and comparative transfers
    
    ---
    
    **Getting Started:**
    - Navigate using the sidebar to explore each approach
    - Each method provides unique insights into transfer performance prediction
    - Compare results across both approaches for comprehensive analysis
    
    ---
    
    **Data Sources:**
    - Historical player statistics from multiple leagues
    - Team competitive ratings and rankings
    - League difficulty and quality metrics
    """
)
