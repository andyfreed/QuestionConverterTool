import pandas as pd
import io
import random

def validate_raw_csv(df):
    """Validate the raw CSV format"""
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

    # Check if there are any empty rows (excluding trailing commas)
    if df[required_columns].isna().any().any():
        return False, "CSV contains empty cells in required columns"

    return True, "Validation successful"

def transform_csv(df):
    """Transform raw CSV to goal format"""
    # Clean column names
    df.columns = df.columns.str.strip()

    # Initialize empty lists for new data
    records = []

    # Starting ID (can be randomized or sequential)
    current_id = random.randint(100000, 999999)

    for _, row in df.iterrows():
        # Skip empty rows
        if pd.isna(row['Question']):
            continue

        # Combine all answer choices into pipe-separated string
        options = "|".join([
            str(row['answer choice A']).strip(),
            str(row['answer choice B']).strip(),
            str(row['answer choice C']).strip(),
            str(row['answer choice D']).strip()
        ])

        # Create new record in goal format
        record = {
            'ID': current_id,
            'Title': row['Question'],
            'Category': '366524 Exam Questions',  # Default category
            'Type': 'single-choice',
            'Post Content': row['Question'],
            'Status': 'publish',
            'Menu Order': len(records) + 1,
            'Options': options,
            'Answer': str(row['Correct Answer']).strip()
        }

        records.append(record)
        current_id += 1

    # Create new dataframe in goal format
    goal_df = pd.DataFrame(records)

    return goal_df

def get_csv_preview(df, num_rows=5):
    """Get a preview of the dataframe as HTML"""
    return df.head(num_rows).to_html(index=False)

def convert_df_to_csv(df):
    """Convert dataframe to CSV string"""
    return df.to_csv(index=False)