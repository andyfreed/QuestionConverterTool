import pandas as pd
import io
import random
import re

def clean_question_text(text):
    """
    Remove question numbers from the beginning of the text while preserving text content

    Args:
        text (str): Input text that may start with a question number

    Returns:
        str: Cleaned text without leading question number
    """
    # Convert to string and handle encoding
    text = str(text).strip()

    # Only remove numbers at the start of the text that are followed by a period and space
    # This preserves periods in abbreviations like "Inc." or other mid-text numbers
    cleaned_text = re.sub(r'^(\d+)\.\s+', '', text)

    return cleaned_text

def validate_raw_csv(df):
    """
    Validate the raw CSV format and structure

    Args:
        df (pandas.DataFrame): Input dataframe to validate

    Returns:
        tuple: (bool, str) indicating validation status and message
    """
    # Read CSV with proper encoding
    df = df.copy()

    # Clean up column names - strip whitespace and convert to lowercase
    df.columns = df.columns.str.strip()

    required_columns = [
        'Question',
        'answer choice A',
        'answer choice B', 
        'answer choice C',
        'answer choice D',
        'Correct Answer'
    ]

    # Check if all required columns exist (case-insensitive)
    df_cols_lower = [col.lower() for col in df.columns]
    missing_cols = [col for col in required_columns if col.lower() not in df_cols_lower]

    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}"

    # Check if there are any empty rows
    empty_cells = df[required_columns].isna().any(axis=1)
    if empty_cells.any():
        first_empty_row = empty_cells[empty_cells].index[0] + 1
        return False, f"Empty cells found in required columns (first occurrence at row {first_empty_row})"

    # Validate that correct answers match one of the choices
    for idx, row in df.iterrows():
        correct_answer = str(row['Correct Answer']).strip()
        choices = [
            str(row['answer choice A']).strip(),
            str(row['answer choice B']).strip(),
            str(row['answer choice C']).strip(),
            str(row['answer choice D']).strip()
        ]
        if correct_answer not in choices:
            return False, f"Correct answer doesn't match any choice in row {idx + 1}"

    return True, "Validation successful"

def transform_csv(df):
    """
    Transform raw CSV to goal format

    Args:
        df (pandas.DataFrame): Input dataframe to transform

    Returns:
        pandas.DataFrame: Transformed dataframe in goal format
    """
    # Clean column names
    df.columns = df.columns.str.strip()

    # Initialize empty lists for new data
    records = []

    # Starting ID (random but consistent within batch)
    current_id = random.randint(100000, 999999)

    for idx, row in df.iterrows():
        # Skip empty rows
        if pd.isna(row['Question']):
            continue

        # Clean the question text to remove leading numbers
        cleaned_question = clean_question_text(row['Question'])

        # Combine all answer choices into pipe-separated string
        options = "|".join([
            str(row['answer choice A']).strip(),
            str(row['answer choice B']).strip(),
            str(row['answer choice C']).strip(),
            str(row['answer choice D']).strip()
        ])

        # Create new record in goal format
        record = {
            'ID': current_id + idx,
            'Title': cleaned_question,
            'Category': '366524 Exam Questions',
            'Type': 'single-choice',
            'Post Content': cleaned_question,
            'Status': 'publish',
            'Menu Order': idx + 1,
            'Options': options,
            'Answer': str(row['Correct Answer']).strip()
        }

        records.append(record)

    # Create new dataframe in goal format
    goal_df = pd.DataFrame(records)

    # Ensure proper encoding in the output
    for col in goal_df.columns:
        if goal_df[col].dtype == 'object':
            goal_df[col] = goal_df[col].str.encode('utf-8').str.decode('utf-8')

    return goal_df

def get_csv_preview(df, num_rows=5):
    """
    Get a preview of the dataframe as HTML

    Args:
        df (pandas.DataFrame): Dataframe to preview
        num_rows (int): Number of rows to show in preview

    Returns:
        str: HTML representation of the dataframe preview
    """
    return df.head(num_rows).to_html(index=False)

def convert_df_to_csv(df):
    """
    Convert dataframe to CSV string

    Args:
        df (pandas.DataFrame): Dataframe to convert

    Returns:
        str: CSV string representation of the dataframe
    """
    return df.to_csv(index=False, encoding='utf-8')