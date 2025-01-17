import streamlit as st
import pandas as pd
from utils import validate_raw_csv, transform_csv, get_csv_preview, convert_df_to_csv

def main():
    st.set_page_config(page_title="CSV Format Converter", layout="wide")
    
    st.title("CSV Format Converter")
    st.write("Convert raw questions CSV to structured goal format")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload raw questions CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Validate input format
            is_valid, message = validate_raw_csv(df)
            
            if is_valid:
                st.success("File uploaded and validated successfully!")
                
                # Show input preview
                st.subheader("Input Preview")
                st.write(get_csv_preview(df))
                
                # Transform data
                with st.spinner("Converting data..."):
                    converted_df = transform_csv(df)
                
                # Show output preview
                st.subheader("Output Preview")
                st.write(get_csv_preview(converted_df))
                
                # Download button
                csv = convert_df_to_csv(converted_df)
                st.download_button(
                    label="Download Converted CSV",
                    data=csv,
                    file_name="converted_questions.csv",
                    mime="text/csv"
                )
            else:
                st.error(f"Validation Error: {message}")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.write("Please ensure your CSV file matches the expected format:")
            st.code("""
Expected columns:
- Question
- answer choice A
- answer choice B
- answer choice C
- answer choice D
- Correct Answer
            """)

if __name__ == "__main__":
    main()
