import pandas as pd
import io
import random

def validate_raw_csv(df):
    """Validate the raw CSV format"""
    required_columns = [
        'Question', 
        'answer choice A',
        'answer choice B', 
        'answer choice C',
        'answer choice D',
        'Correct Answer'
    ]
    
    # Check if all required columns exist
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}"
    
    # Check if there are any empty rows
    if df.isna().any().any():
        return False, "CSV contains empty cells"
        
    return True, "Validation successful"

def transform_csv(df):
    """Transform raw CSV to goal format"""
    # Initialize empty lists for new data
    records = []
    
    # Starting ID (can be randomized or sequential)
    current_id = random.randint(100000, 999999)
    
    for _, row in df.iterrows():
        # Combine all answer choices into pipe-separated string
        options = "|".join([
            row['answer choice A'].strip(),
            row['answer choice B'].strip(),
            row['answer choice C'].strip(),
            row['answer choice D'].strip()
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
            'Answer': row['Correct Answer'].strip()
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
