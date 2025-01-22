import streamlit as st
import pandas as pd
from utils import validate_raw_csv, transform_csv, get_csv_preview, convert_df_to_csv
import io
import zipfile

def main():
    st.set_page_config(
        page_title="CSV Format Converter",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items=None
    )

    st.markdown("""
        <style>
        /* Modern dark theme */
        .stApp {
            background: linear-gradient(to bottom right, #1a1a2e, #16213e);
        }

        /* Custom typography */
        h1, h2, h3 {
            color: #e94560 !important;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        /* Section styling */
        .content-section {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
        }

        /* Input fields styling */
        .stTextInput > div > div {
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
            color: #fff !important;
            transition: all 0.3s ease;
        }

        .stTextInput > div > div:hover {
            border-color: #e94560 !important;
        }

        /* Checkbox styling */
        .stCheckbox > label {
            color: #fff !important;
        }

        .stCheckbox > label > div[role="checkbox"] {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
        }

        .stCheckbox > label > div[role="checkbox"][aria-checked="true"] {
            background-color: #e94560 !important;
            border-color: #e94560 !important;
        }

        /* File uploader styling */
        [data-testid="stFileUploader"] {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 1rem;
        }

        [data-testid="stFileUploadDropzone"] {
            background: rgba(255, 255, 255, 0.02);
            border: 2px dashed rgba(233, 69, 96, 0.5) !important;
            border-radius: 8px;
            color: #fff !important;
            transition: all 0.3s ease;
        }

        [data-testid="stFileUploadDropzone"]:hover {
            border-color: #e94560 !important;
            background: rgba(233, 69, 96, 0.1);
        }

        /* Button styling */
        .stButton > button {
            background: linear-gradient(45deg, #e94560, #ff6b6b) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
        }

        /* Info/Error message styling */
        .stAlert {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
        }

        /* Requirements list styling */
        .requirements-list {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
        }

        .requirements-list h4 {
            color: #e94560;
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }

        .requirements-list ul {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }

        .requirements-list li {
            color: #fff;
            margin-bottom: 0.5rem;
            padding-left: 1.5rem;
            position: relative;
        }

        .requirements-list li:before {
            content: "→";
            position: absolute;
            left: 0;
            color: #e94560;
        }

        /* Hide default elements */
        #MainMenu, footer, .stDeployButton {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 2.5rem; margin-bottom: 0.5rem;'>CSV Format Converter</h1>
            <p style='color: #fff; opacity: 0.8; font-size: 1.1rem;'>Transform raw questions into structured formats with ease</p>
        </div>
    """, unsafe_allow_html=True)

    # Requirements section
    st.markdown("""
        <div class='requirements-list'>
            <h4>📋 Required CSV Columns</h4>
            <ul>
                <li>Question</li>
                <li>answer choice A</li>
                <li>answer choice B</li>
                <li>answer choice C</li>
                <li>answer choice D</li>
                <li>Correct Answer</li>
            </ul>

            <h4 style='margin-top: 1.5rem;'>⚠️ Important Notes</h4>
            <ul>
                <li>CSV file must contain all required columns</li>
                <li>Column names are case-sensitive</li>
                <li>All fields must be filled out</li>
                <li>Correct answer must match one of the choices exactly</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Input section
    st.markdown("<div class='content-section'>", unsafe_allow_html=True)
    category = st.text_input(
        "Category",
        help="Enter the category to be used in the converted files",
        placeholder="Enter category (required)",
    )

    blank_ids = st.checkbox(
        "Export with blank IDs",
        help="Check this to export files with blank ID column values (header will be kept)",
        value=False
    )

    uploaded_files = st.file_uploader(
        "Upload raw questions CSV files",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload one or more CSV files containing questions and answers in the raw format"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded")

        if not category:
            st.error("⚠️ Please enter a category before processing files")
        elif st.button("🔄 Process Files", help="Click to convert all uploaded files", use_container_width=True):
            with st.spinner("Processing files..."):
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    processed_files = []
                    for idx, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Processing file {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")

                        try:
                            df = pd.read_csv(uploaded_file)
                            is_valid, message = validate_raw_csv(df)

                            if is_valid:
                                converted_df = transform_csv(df, category=category, include_ids=not blank_ids)
                                processed_files.append({
                                    'name': uploaded_file.name,
                                    'df': converted_df,
                                    'status': 'success',
                                    'message': 'Successfully converted'
                                })
                            else:
                                processed_files.append({
                                    'name': uploaded_file.name,
                                    'df': None,
                                    'status': 'error',
                                    'message': message
                                })

                        except Exception as e:
                            processed_files.append({
                                'name': uploaded_file.name,
                                'df': None,
                                'status': 'error',
                                'message': str(e)
                            })

                        progress_bar.progress((idx + 1) / len(uploaded_files))

                    st.markdown("<div class='content-section'>", unsafe_allow_html=True)
                    st.subheader("Processing Results")
                    cols = st.columns(2)

                    with cols[0]:
                        st.markdown("#### ✅ Successful")
                        successful_files = [f for f in processed_files if f['status'] == 'success']
                        for file in successful_files:
                            st.success(f"{file['name']}: {file['message']}")

                    with cols[1]:
                        st.markdown("#### ❌ Failed")
                        failed_files = [f for f in processed_files if f['status'] == 'error']
                        for file in failed_files:
                            st.error(f"{file['name']}: {file['message']}")

                    if successful_files:
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                            for file in successful_files:
                                csv_data = convert_df_to_csv(file['df'])
                                output_filename = f"converted_{file['name']}"
                                zf.writestr(output_filename, csv_data)

                        st.download_button(
                            label="📥 Download Converted Files (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name="converted_files.zip",
                            mime="application/zip",
                            help="Download a ZIP file containing all successfully converted files",
                            use_container_width=True
                        )

                        st.info(f"""
                        📊 Conversion Summary:
                        - Total files: {len(processed_files)}
                        - Successful: {len(successful_files)}
                        - Failed: {len(failed_files)}
                        """)
                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Batch processing error: {str(e)}")

if __name__ == "__main__":
    main()