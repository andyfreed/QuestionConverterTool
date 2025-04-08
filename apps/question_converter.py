import streamlit as st
import pandas as pd
from utils import validate_raw_csv, transform_csv, get_csv_preview, convert_df_to_csv
import io
import zipfile
import base64

def main():
    st.set_page_config(
        page_title="Convert Exam to Import File",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Base styling
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to bottom right, #1a1a2e, #16213e);
            color: white;
        }

        .stButton > button {
            background: linear-gradient(45deg, #e94560, #ff6b6b);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
        }

        .stTextInput > div > div {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: white;
        }

        .uploadedFile {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 1.5rem;
        }

        @keyframes slide {
            from {
                transform: translateX(-100%);
            }
            to {
                transform: translateX(100vw);
            }
        }

        .success-animation {
            position: fixed;
            top: 50%;
            transform: translateY(-50%);
            z-index: 1000;
            animation: slide 5s linear;
        }

        .success-animation img {
            height: 100px;
            width: auto;
        }

        #MainMenu, footer {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("Convert Exam to Import File")
    st.write("Transform exam questions into importable format")

    # Load and encode the Pepe GIF
    with open("attached_assets/pepe-pepe-wink.gif", "rb") as f:
        pepe_gif = base64.b64encode(f.read()).decode()

    # Requirements section
    with st.container():
        st.subheader("📋 Required CSV Columns")
        cols = st.columns([1, 2])

        with cols[0]:
            st.markdown("""
                - Question
                - answer choice A
                - answer choice B
                - answer choice C
                - answer choice D
                - Correct Answer
            """)

        with cols[1]:
            st.subheader("⚠️ Important Notes")
            st.markdown("""
                - CSV file must contain all required columns
                - Column names are case-sensitive
                - All fields must be filled out
                - Correct answer must match one of the choices exactly
            """)

    # Input section
    st.divider()

    category = st.text_input(
        "Category",
        help="Enter the category to be used in the converted files",
        placeholder="Enter category (required)"
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

    # Success animation container
    success_container = st.empty()

    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded")

        if not category:
            st.error("⚠️ Please enter a category before processing files")
        elif st.button("🔄 Process Files", help="Click to convert all uploaded files"):
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

                    # Results section
                    st.divider()
                    cols = st.columns(2)

                    with cols[0]:
                        st.subheader("✅ Successful")
                        successful_files = [f for f in processed_files if f['status'] == 'success']
                        for file in successful_files:
                            st.success(f"{file['name']}: {file['message']}")

                    with cols[1]:
                        st.subheader("❌ Failed")
                        failed_files = [f for f in processed_files if f['status'] == 'error']
                        for file in failed_files:
                            st.error(f"{file['name']}: {file['message']}")

                    if successful_files:
                        # Show success animation
                        success_container.markdown(
                            f"""
                            <div class="success-animation">
                                <img src="data:image/gif;base64,{pepe_gif}" alt="Success!">
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # Prepare download
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
                            help="Download a ZIP file containing all successfully converted files"
                        )

                        st.info(f"""
                        📊 Conversion Summary:
                        - Total files: {len(processed_files)}
                        - Successful: {len(successful_files)}
                        - Failed: {len(failed_files)}
                        """)

                except Exception as e:
                    st.error(f"❌ Batch processing error: {str(e)}")

if __name__ == "__main__":
    main()