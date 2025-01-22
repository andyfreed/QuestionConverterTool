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
        .uploadedFile {
            border: 2px dashed #1f77b4;
            border-radius: 4px;
            padding: 20px;
            margin: 0;
            background-color: #f8f9fa;
        }
        .stApp {
            background-color: transparent;
        }
        .usage-info {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 10px;
            color: #333333;
        }
        .usage-info h4 {
            color: #1f77b4;
            margin-top: 10px;
            margin-bottom: 8px;
        }
        .usage-info ul {
            margin-left: 20px;
        }
        /* Aggressive spacing removal */
        .stExpander, .element-container, div[data-testid="stExpander"], div[data-testid="stMarkdown"] {
            margin: 0 !important;
            padding: 0 !important;
        }
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 0 !important;
        }
        div[data-testid="stFileUploader"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        /* Remove all gaps */
        .css-1544g2n {
            padding: 0 !important;
            margin: 0 !important;
        }
        .css-1kyxreq {
            margin-top: -1rem !important;
        }
        /* Hide default expander spacing */
        .streamlit-expanderHeader {
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Target Streamlit's internal structure */
        div[data-testid="stVerticalBlock"] > div {
            margin-top: -1em !important;
            padding-top: 0 !important;
        }
        div[data-baseweb="input"] {
            margin-top: 0 !important;
        }
        div[data-testid="stExpander"] + div {
            margin-top: -1em !important;
        }
        /* Additional aggressive spacing fixes */
        div[class*="stMarkdown"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        .main > div {
            padding: 0 !important;
        }
        div[data-testid="InputInstructions"] {
            display: none;
        }
        /* Force compact layout */
        .element-container:not(:last-child) {
            margin-bottom: -1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("CSV Format Converter")
    st.write("Convert raw questions CSV to structured goal format")

    # Container to group related elements
    with st.container():
        # Format requirements expander
        with st.expander("ℹ️ Input Format Requirements", expanded=True):
            st.markdown("""
            <div class="usage-info">
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
            </div>
            """, unsafe_allow_html=True)

        # Category input
        category = st.text_input(
            "Category",
            help="Enter the category to be used in the converted files",
            placeholder="Enter category (required)",
        )

        # Blank IDs checkbox
        blank_ids = st.checkbox(
            "Export with blank IDs",
            help="Check this to export files with blank ID column values (header will be kept)",
            value=False
        )

        # File uploader
        st.markdown('<div class="uploadedFile">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload raw questions CSV files",
            type=['csv'],
            accept_multiple_files=True,
            help="Upload one or more CSV files containing questions and answers in the raw format"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded")

        # Process files button with enhanced visibility
        if not category:
            st.error("⚠️ Please enter a category before processing files")
        elif st.button("🔄 Process All Files", help="Click to convert all uploaded files", use_container_width=True):
            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Process each file
                processed_files = []
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing file {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")

                    try:
                        # Read and process the file
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

                    # Update progress
                    progress_bar.progress((idx + 1) / len(uploaded_files))

                # Show processing results
                st.subheader("Processing Results")

                # Display results in columns
                cols = st.columns(2)

                # Success column
                with cols[0]:
                    st.markdown("#### ✅ Successful Conversions")
                    successful_files = [f for f in processed_files if f['status'] == 'success']
                    for file in successful_files:
                        st.success(f"{file['name']}: {file['message']}")

                # Error column
                with cols[1]:
                    st.markdown("#### ❌ Failed Conversions")
                    failed_files = [f for f in processed_files if f['status'] == 'error']
                    for file in failed_files:
                        st.error(f"{file['name']}: {file['message']}")

                # Prepare download if there are successful conversions
                if successful_files:
                    # Create a ZIP file containing all converted CSVs
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for file in successful_files:
                            csv_data = convert_df_to_csv(file['df'])
                            output_filename = f"converted_{file['name']}"
                            zf.writestr(output_filename, csv_data)

                    # Offer ZIP download with enhanced visibility
                    st.download_button(
                        label="📥 Download All Converted Files (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="converted_files.zip",
                        mime="application/zip",
                        help="Download a ZIP file containing all successfully converted files",
                        use_container_width=True
                    )

                    # Show conversion statistics
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