"""
Core data cleaning logic for the Data Cleaning Bot.
Implements all cleaning operations: trimming, normalization, date fixing,
missing value handling, duplicate removal, and outlier detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Any
import re
from datetime import datetime
from backend.utils import clean_string, normalize_special_characters, detect_column_type


class DataCleaningPipeline:
    """
    Main pipeline for cleaning CSV data.
    Tracks all operations for script generation and reporting.
    """
    
    def __init__(self):
        self.cleaning_steps: List[Dict[str, Any]] = []
        self.original_df = None
        self.cleaned_df = None
        self.summary = {
            'original_rows': 0,
            'cleaned_rows': 0,
            'rows_removed': 0,
            'columns': 0,
            'missing_values_handled': 0,
            'outliers_replaced': 0,
            'date_columns_fixed': 0,
            'duplicates_removed': 0
        }
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load CSV file into DataFrame.
        """
        try:
            df = pd.read_csv(file_path)
            self.original_df = df.copy()
            self.cleaned_df = df.copy()
            
            self.summary['original_rows'] = len(df)
            self.summary['columns'] = len(df.columns)
            
            self.cleaning_steps.append({
                'step': 'load_csv',
                'description': f'Loaded CSV with {len(df)} rows and {len(df.columns)} columns'
            })
            
            return df
        except Exception as e:
            raise Exception(f"Error loading CSV: {str(e)}")
    
    def trim_and_normalize_strings(self) -> pd.DataFrame:
        """
        Step 1: Trim leading/trailing spaces from all string columns.
        Also normalize to lowercase and remove special characters.
        """
        df = self.cleaned_df.copy()
        string_columns = df.select_dtypes(include=['object']).columns
        
        trimmed_count = 0
        
        for col in string_columns:
            # Skip if column is entirely numeric
            if df[col].dtype == 'object':
                original = df[col].copy()
                
                # Apply cleaning to string values
                df[col] = df[col].apply(
                    lambda x: clean_string(x) if isinstance(x, str) else x
                )
                
                # Track changes
                changes = (original != df[col]).sum()
                if changes > 0:
                    trimmed_count += changes
        
        self.cleaned_df = df
        self.cleaning_steps.append({
            'step': 'trim_and_normalize',
            'description': f'Trimmed and normalized {trimmed_count} string values'
        })
        
        return df
    
    def fix_dates(self) -> pd.DataFrame:
        """
        Step 2: Detect and fix date columns.
        Convert to YYYY-MM-DD format.
        """
        df = self.cleaned_df.copy()
        date_columns_fixed = 0
        
        for col in df.columns:
            # Try to detect if column might be a date
            if detect_column_type(df[col]) == 'date':
                try:
                    # Attempt conversion with common date formats
                    converted = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                    
                    # Only convert if most values are successfully converted
                    success_rate = converted.notna().sum() / len(df)
                    if success_rate > 0.7:
                        df[col] = converted.dt.strftime('%Y-%m-%d')
                        date_columns_fixed += 1
                except Exception as e:
                    pass  # Column stays as is
        
        self.cleaned_df = df
        self.summary['date_columns_fixed'] = date_columns_fixed
        self.cleaning_steps.append({
            'step': 'fix_dates',
            'description': f'Fixed {date_columns_fixed} date columns to YYYY-MM-DD format'
        })
        
        return df
    
    def handle_missing_values(self) -> pd.DataFrame:
        """
        Step 3: Handle missing values safely.
        - Numeric columns: median
        - Categorical/string columns: mode
        - Mixed columns: treat as categorical
        - Date columns: forward/backward fill
        """

        df = self.cleaned_df.copy()
        missing_handled = 0

        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count == 0:
                continue

            # --- SAFEST NUMERIC CHECK ---
            if pd.api.types.is_numeric_dtype(df[col]):
                # Clean numeric column even if mixed types
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                median_val = numeric_series.median()

                if not pd.isna(median_val):
                    df[col] = numeric_series.fillna(median_val)
                    missing_handled += missing_count
                else:
                    # fallback: use mode if numeric conversion fails
                    mode_val = df[col].mode()
                    if len(mode_val) > 0:
                        df[col].fillna(mode_val[0], inplace=True)
                        missing_handled += missing_count

            else:
                # Check if it's a date column
                col_type = detect_column_type(df[col])

                if col_type == "date":
                    df[col] = df[col].fillna(method="ffill").fillna(method="bfill")
                    missing_handled += missing_count

                else:
                    # Treat everything else (string, mixed, categorical) as categorical
                    mode_val = df[col].mode()
                    if len(mode_val) > 0:
                        df[col].fillna(mode_val[0], inplace=True)
                        missing_handled += missing_count
                    else:
                        df[col].fillna("", inplace=True)
                        missing_handled += missing_count

        self.cleaned_df = df
        self.summary["missing_values_handled"] = missing_handled

        self.cleaning_steps.append({
            'step': 'handle_missing',
            'description': f'Handled {missing_handled} missing values'
        })

        return df

    def remove_duplicates(self) -> pd.DataFrame:
        """
        Step 4: Remove duplicate rows.
        Keeps first occurrence, removes subsequent duplicates.
        """
        df = self.cleaned_df.copy()
        initial_rows = len(df)
        
        df = df.drop_duplicates(keep='first')
        
        duplicates_removed = initial_rows - len(df)
        self.cleaned_df = df
        self.summary['duplicates_removed'] = duplicates_removed
        self.cleaning_steps.append({
            'step': 'remove_duplicates',
            'description': f'Removed {duplicates_removed} duplicate rows'
        })
        
        return df
    
    def detect_and_replace_outliers(self) -> pd.DataFrame:
        """
        Step 5: Detect and replace outliers using IQR method.
        Outliers are replaced with median value.
        """
        df = self.cleaned_df.copy()
        outliers_replaced = 0
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Find outliers
            outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_count = outlier_mask.sum()
            
            if outlier_count > 0:
                # Replace with median
                median_val = df[col].median()
                df.loc[outlier_mask, col] = median_val
                outliers_replaced += outlier_count
        
        self.cleaned_df = df
        self.summary['outliers_replaced'] = outliers_replaced
        self.cleaning_steps.append({
            'step': 'detect_outliers',
            'description': f'Detected and replaced {outliers_replaced} outliers using IQR method'
        })
        
        return df
    
    def finalize(self) -> pd.DataFrame:
        """
        Final step: update summary statistics.
        """
        self.summary['cleaned_rows'] = len(self.cleaned_df)
        self.summary['rows_removed'] = (
            self.summary['original_rows'] - self.summary['cleaned_rows']
        )
        
        return self.cleaned_df
    
    def run_pipeline(self, file_path: str) -> Tuple[pd.DataFrame, List[Dict], Dict]:
        """
        Run the complete cleaning pipeline.
        Returns: (cleaned_df, cleaning_steps, summary)
        """
        self.load_csv(file_path)
        self.trim_and_normalize_strings()
        self.fix_dates()
        self.handle_missing_values()
        self.remove_duplicates()
        self.detect_and_replace_outliers()
        self.finalize()
        
        return self.cleaned_df, self.cleaning_steps, self.summary


def generate_python_script(cleaning_steps: List[Dict], original_columns: List[str]) -> str:
    """
    Generate a reusable Python script that replicates all cleaning steps.
    This script can be downloaded and used on new CSVs.
    """
    
    script = '''"""
Auto-generated Data Cleaning Script
Generated by Data Cleaning Bot
This script replicates all the cleaning operations performed.
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime


def clean_string(value):
    """Trim and normalize string values."""
    if not isinstance(value, str):
        return value
    value = value.strip().lower()
    return value


def detect_column_type(series):
    """Detect if a column is numeric, categorical, or date."""
    non_null = series.dropna()
    if len(non_null) == 0:
        return 'unknown'
    
    try:
        pd.to_numeric(series, errors='coerce')
        if pd.to_numeric(series, errors='coerce').notna().sum() > len(non_null) * 0.8:
            return 'numeric'
    except:
        pass
    
    try:
        pd.to_datetime(series, errors='coerce')
        if pd.to_datetime(series, errors='coerce').notna().sum() > len(non_null) * 0.8:
            return 'date'
    except:
        pass
    
    unique_ratio = len(non_null.unique()) / len(non_null)
    if unique_ratio < 0.5:
        return 'categorical'
    return 'string'


def clean_data(input_csv, output_csv='cleaned_data.csv'):
    """
    Main cleaning function that applies all operations.
    """
    print("Loading CSV...")
    df = pd.read_csv(input_csv)
    original_rows = len(df)
    
    # Step 1: Trim and normalize strings
    print("Step 1: Trimming and normalizing strings...")
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].apply(
            lambda x: clean_string(x) if isinstance(x, str) else x
        )
    
    # Step 2: Fix dates
    print("Step 2: Fixing date formats...")
    for col in df.columns:
        if detect_column_type(df[col]) == 'date':
            try:
                converted = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                success_rate = converted.notna().sum() / len(df)
                if success_rate > 0.7:
                    df[col] = converted.dt.strftime('%Y-%m-%d')
            except:
                pass
    
    # Step 3: Handle missing values
    print("Step 3: Handling missing values...")
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            col_type = detect_column_type(df[col])
            if col_type == 'numeric':
                median_val = df[col].median()
                if not pd.isna(median_val):
                    df[col].fillna(median_val, inplace=True)
            elif col_type == 'categorical':
                mode_val = df[col].mode()
                if len(mode_val) > 0:
                    df[col].fillna(mode_val[0], inplace=True)
    
    # Step 4: Remove duplicates
    print("Step 4: Removing duplicates...")
    duplicates_before = len(df)
    df = df.drop_duplicates(keep='first')
    print(f"Removed {duplicates_before - len(df)} duplicates")
    
    # Step 5: Detect and replace outliers
    print("Step 5: Handling outliers (IQR method)...")
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        if outlier_mask.sum() > 0:
            median_val = df[col].median()
            df.loc[outlier_mask, col] = median_val
    
    # Save cleaned CSV
    print(f"Saving cleaned data to {output_csv}...")
    df.to_csv(output_csv, index=False)
    
    print(f"\\nCleaning Summary:")
    print(f"  Original rows: {original_rows}")
    print(f"  Cleaned rows: {len(df)}")
    print(f"  Rows removed: {original_rows - len(df)}")
    print(f"  Columns: {len(df.columns)}")


if __name__ == "__main__":
    # Usage: python clean_data.py <input_csv> [output_csv]
    import sys
    if len(sys.argv) < 2:
        print("Usage: python clean_data.py <input_csv> [output_csv]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'cleaned_data.csv'
    
    clean_data(input_file, output_file)
'''
    
    return script
