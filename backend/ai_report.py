"""
AI Report Generation Module
Uses OpenAI GPT-4o or Groq LLM to generate human-readable cleaning reports.
"""

import os
from typing import Dict, Any
import pandas as pd


def generate_ai_report(
    original_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    cleaning_steps: list,
    summary: dict,
    ai_provider: str = "openai"
) -> str:
    """
    Generate a human-readable AI report explaining the cleaning operations.
    
    Args:
        original_df: DataFrame before cleaning
        cleaned_df: DataFrame after cleaning
        cleaning_steps: List of cleaning operations performed
        summary: Summary statistics
        ai_provider: 'openai' or 'groq'
    
    Returns:
        Formatted AI report as string
    """
    
    # Build the cleaning steps summary
    steps_description = "\n".join([
        f"- {step['description']}" for step in cleaning_steps
    ])
    
    # Build data quality metrics
    original_stats = _get_dataframe_stats(original_df)
    cleaned_stats = _get_dataframe_stats(cleaned_df)
    
    prompt = f"""
Analyze this data cleaning operation and provide a concise, professional report.

ORIGINAL DATA:
- Rows: {len(original_df)}
- Columns: {len(original_df.columns)}
- Column names: {list(original_df.columns)[:10]}
- Data types: {dict(original_df.dtypes.astype(str).head(10))}
- Missing values: {original_df.isnull().sum().sum()}

CLEANING OPERATIONS PERFORMED:
{steps_description}

CLEANED DATA:
- Rows: {len(cleaned_df)}
- Columns: {len(cleaned_df.columns)}
- Missing values: {cleaned_df.isnull().sum().sum()}

SUMMARY:
- Rows removed: {summary.get('rows_removed', 0)}
- Duplicates removed: {summary.get('duplicates_removed', 0)}
- Missing values fixed: {summary.get('missing_values_handled', 0)}
- Outliers replaced: {summary.get('outliers_replaced', 0)}
- Date columns fixed: {summary.get('date_columns_fixed', 0)}

Please provide:
1. A brief overview of the data quality before cleaning
2. What issues were found and fixed
3. Data quality improvements achieved
4. Recommendations for further improvements (if any)

Keep the report concise (2-3 paragraphs) and actionable.
"""
    
    try:
        if ai_provider.lower() == "openai":
            return _call_openai(prompt)
        elif ai_provider.lower() == "groq":
            return _call_groq(prompt)
        else:
            return _fallback_report(summary)
    except Exception as e:
        # Fallback if API fails
        print(f"AI report generation failed: {str(e)}, using fallback")
        return _fallback_report(summary)


def _call_openai(prompt: str) -> str:
    """Call OpenAI API for report generation."""
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a data quality expert. Provide clear, actionable insights about data cleaning operations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content


def _call_groq(prompt: str) -> str:
    """Call Groq API for report generation."""
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    
    client = Groq(api_key=api_key)
    
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {
                "role": "system",
                "content": "You are a data quality expert. Provide clear, actionable insights about data cleaning operations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content


def _fallback_report(summary: dict) -> str:
    """Generate a fallback report if AI APIs fail."""
    
    report = f"""
## Data Cleaning Report

### Summary of Operations
- **Original Records:** {summary.get('original_rows', 0)}
- **Cleaned Records:** {summary.get('cleaned_rows', 0)}
- **Records Removed:** {summary.get('rows_removed', 0)} ({(summary.get('rows_removed', 0) / max(summary.get('original_rows', 1), 1) * 100):.1f}%)

### Data Quality Improvements
- **Duplicate Rows Removed:** {summary.get('duplicates_removed', 0)}
- **Missing Values Fixed:** {summary.get('missing_values_handled', 0)}
- **Outliers Replaced:** {summary.get('outliers_replaced', 0)}
- **Date Formats Fixed:** {summary.get('date_columns_fixed', 0)}

### Recommendations
1. **Review the cleaned data** to ensure quality meets your requirements
2. **Validate date conversions** to confirm accuracy
3. **Check categorical values** for consistency
4. **Consider domain-specific rules** that may need additional cleaning
"""
    
    return report.strip()


def _get_dataframe_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Extract statistics from a DataFrame."""
    stats = {
        'rows': len(df),
        'columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=['number']).columns),
        'missing_total': df.isnull().sum().sum(),
        'memory_usage': df.memory_usage(deep=True).sum() / 1024 ** 2  # MB
    }
    return stats


def format_ai_report_html(report: str) -> str:
    """Convert markdown report to HTML for frontend display."""
    
    # Simple markdown to HTML conversion
    html = report
    
    # Convert headers
    html = html.replace("## ", "<h2>").replace("### ", "<h3>")
    
    # Convert bold
    html = html.replace("**", "<strong>").replace("**", "</strong>")
    
    # Convert line breaks to paragraphs
    paragraphs = html.split('\n\n')
    html = ''.join([f"<p>{p}</p>" for p in paragraphs if p.strip()])
    
    return html
