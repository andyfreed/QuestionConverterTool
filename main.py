import streamlit as st
import pandas as pd
from utils import validate_raw_csv, transform_csv, get_csv_preview, convert_df_to_csv
import io
import zipfile

def main():
    st.set_page_config(
        page_title="CSV Format Converter",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("CSV Format Converter")
    st.write("Convert raw questions CSV to structured goal format")

    # Add helper information
    with st.expander("ℹ️ Input Format Requirements"):
        st.write("""
        Your CSV files should contain the following columns:
        - Question
        - answer choice A
        - answer choice B
        - answer choice C
        - answer choice D
        - Correct Answer
        """)

    # File uploader with multiple files support
    uploaded_files = st.file_uploader(
        "Upload raw questions CSV files",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload one or more CSV files containing questions and answers in the raw format"
    )

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded")

        # Process files button
        if st.button("🔄 Process All Files", help="Click to convert all uploaded files"):
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
                            converted_df = transform_csv(df)
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

                    # Offer ZIP download
                    st.download_button(
                        label="📥 Download All Converted Files (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="converted_files.zip",
                        mime="application/zip",
                        help="Download a ZIP file containing all successfully converted files"
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