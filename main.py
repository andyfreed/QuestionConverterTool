import streamlit as st
import sys
import os
import traceback

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Multi-App Dashboard",
    page_icon="🎯",
    layout="wide"
)

# Add the apps directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "apps"))

debug_container = st.empty()
debug_container.write("Debug: Starting app import")

try:
    # Import your apps
    from question_converter import main as question_converter_app

    # Create a dictionary of apps
    APPS = {
        "Question Converter": question_converter_app,
        # Add more apps here as you create them
        # "App 2": app2_main,
        # "App 3": app3_main,
    }
    debug_container.write("Debug: Successfully imported apps")
except Exception as e:
    st.error(f"Error importing apps: {str(e)}")
    st.code(traceback.format_exc())

def main():
    try:
        # Sidebar for app selection
        st.sidebar.title("Navigation")
        selection = st.sidebar.radio("Go to", list(APPS.keys()))
        
        # Run the selected app
        debug_container.write(f"Debug: About to run app '{selection}'")
        app = APPS[selection]
        # Clear the debug messages before running the app
        debug_container.empty()
        app()
    except Exception as e:
        st.error(f"Error in main function: {str(e)}")
        st.code(traceback.format_exc())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Top-level error: {str(e)}")
        st.code(traceback.format_exc()) 