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
        /* Base styles */
        .stApp {
            background-color: transparent;
        }

        /* Remove default Streamlit margins */
        .block-container {
            padding: 1rem !important;
        }

        /* Custom content wrapper */
        .content-wrapper {
            background-color: #f8f9fa;
            border-radius: 4px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        /* Remove expander margins */
        div[data-testid="stExpander"] {
            margin-bottom: 0 !important;
            border: none !important;
        }

        /* Target the category input container */
        .stTextInput {
            margin-top: 0 !important;
        }

        /* Style only the file uploader dropzone */
        div[data-testid="stFileUploader"] div[data-testid="stFileUploadDropzone"] {
            border: 2px dashed #1f77b4;
            border-radius: 4px;
            padding: 1rem;
            margin-top: 1rem;
        }

        /* Hide unnecessary elements */
        div[data-testid="stToolbar"] {
            display: none;
        }

        footer {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("CSV Format Converter")
    st.write("Convert raw questions CSV to structured goal format")

    # Wrap content in a custom container
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

    # Format requirements
    st.markdown("""
        <h4>Required CSV Columns:</h4>
        <ul>
        <li>Question</li>
        <li>answer choice A</li>
        <li>answer choice B</li>
        <li>answer choice C</li>
        <li>answer choice D</li>
        <li>Correct Answer</li>
        </ul>

        <h4>Important Notes:</h4>
        <ul>
        <li>Make sure your CSV file contains all required columns</li>
        <li>Column names should match exactly (case-sensitive)</li>
        <li>All fields should be filled out</li>
        <li>The correct answer must match one of the choices exactly</li>
        </ul>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Category input (immediately after requirements)
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

    # File uploader (without extra wrapper)
    uploaded_files = st.file_uploader(
        "Upload raw questions CSV files",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload one or more CSV files containing questions and answers in the raw format"
    )

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded")

        if not category:
            st.error("⚠️ Please enter a category before processing files")
        elif st.button("🔄 Process All Files", help="Click to convert all uploaded files", use_container_width=True):
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

                st.subheader("Processing Results")
                cols = st.columns(2)

                with cols[0]:
                    st.markdown("#### ✅ Successful Conversions")
                    successful_files = [f for f in processed_files if f['status'] == 'success']
                    for file in successful_files:
                        st.success(f"{file['name']}: {file['message']}")

                with cols[1]:
                    st.markdown("#### ❌ Failed Conversions")
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
                        label="📥 Download All Converted Files (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="converted_files.zip",
                        mime="application/zip",
                        help="Download a ZIP file containing all successfully converted files",
                        use_container_width=True
                    )

                    st.info(f"""
                    📊 Batch Processing Statistics:
                    - Total files processed: {len(processed_files)}
                    - Successfully converted: {len(successful_files)}
                    - Failed conversions: {len(failed_files)}
                    """)

            except Exception as e:
                st.error(f"❌ Batch processing error: {str(e)}")

if __name__ == "__main__":
    main()