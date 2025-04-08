import streamlit as st
import sys
import os

# Add the apps directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "apps"))

# Import your apps
from question_converter import main as question_converter_app

# Create a dictionary of apps
APPS = {
    "Question Converter": question_converter_app,
    # Add more apps here as you create them
    # "App 2": app2_main,
    # "App 3": app3_main,
}

def main():
    st.set_page_config(
        page_title="Multi-App Dashboard",
        page_icon="🎯",
        layout="wide"
    )
    
    # Sidebar for app selection
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(APPS.keys()))
    
    # Run the selected app
    app = APPS[selection]
    app() 