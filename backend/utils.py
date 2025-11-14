"""
Utility functions for data cleaning bot.
Handles common operations like string manipulation, date parsing, etc.
"""

import re
from typing import Any


def clean_string(value: str) -> str:
    """
    Trim leading/trailing spaces and normalize string.
    Removes special characters but keeps spaces for readability.
    """
    if not isinstance(value, str):
        return value
    
    # Trim leading/trailing spaces
    value = value.strip()
    
    # Lowercase
    value = value.lower()
    
    return value


def normalize_special_characters(value: str) -> str:
    """
    Remove special characters from string, keeping alphanumeric and spaces.
    """
    if not isinstance(value, str):
        return value
    
    # Keep only alphanumeric, spaces, and common punctuation
    value = re.sub(r'[^a-z0-9\s\-._]', '', value)
    value = re.sub(r'\s+', ' ', value).strip()
    
    return value


def safe_numeric_conversion(value: Any) -> Any:
    """
    Safely convert value to numeric if possible.
    """
    if value is None or (isinstance(value, float) and value != value):  # NaN check
        return None
    
    if isinstance(value, (int, float)):
        return value
    
    if isinstance(value, str):
        value = value.strip()
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return None
    
    return None


def detect_column_type(series) -> str:
    """
    Detect if a column is numeric, categorical, or date.
    Returns: 'numeric', 'categorical', 'date', or 'string'
    """
    import pandas as pd
    import numpy as np
    
    # Remove null values for analysis
    non_null = series.dropna()
    
    if len(non_null) == 0:
        return 'unknown'
    
    # Check if numeric
    try:
        pd.to_numeric(series, errors='coerce')
        if pd.to_numeric(series, errors='coerce').notna().sum() > len(non_null) * 0.8:
            return 'numeric'
    except:
        pass
    
    # Check if date
    try:
        pd.to_datetime(series, errors='coerce')
        if pd.to_datetime(series, errors='coerce').notna().sum() > len(non_null) * 0.8:
            return 'date'
    except:
        pass
    
    # Check cardinality for categorical vs string
    unique_ratio = len(non_null.unique()) / len(non_null)
    if unique_ratio < 0.5:  # Less than 50% unique values
        return 'categorical'
    
    return 'string'


def format_report_summary(summary: dict) -> str:
    """
    Format cleaning summary for display.
    """
    lines = []
    lines.append(f"**Original Rows:** {summary.get('original_rows', 0)}")
    lines.append(f"**Cleaned Rows:** {summary.get('cleaned_rows', 0)}")
    lines.append(f"**Rows Removed:** {summary.get('rows_removed', 0)}")
    lines.append(f"**Columns:** {summary.get('columns', 0)}")
    
    if 'missing_values_handled' in summary:
        lines.append(f"**Missing Values Fixed:** {summary['missing_values_handled']}")
    
    if 'outliers_replaced' in summary:
        lines.append(f"**Outliers Replaced:** {summary['outliers_replaced']}")
    
    if 'date_columns_fixed' in summary:
        lines.append(f"**Date Columns Fixed:** {summary['date_columns_fixed']}")
    
    return "\n".join(lines)
