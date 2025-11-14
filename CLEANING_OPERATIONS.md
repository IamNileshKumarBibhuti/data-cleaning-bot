# Cleaning Operations Reference

## Complete Pipeline Walkthrough

### Step 1: Load CSV
**Function:** `DataCleaningPipeline.load_csv(file_path)`

Reads CSV into pandas DataFrame and creates backup.
```python
self.original_df = df.copy()  # Backup for comparison
self.cleaned_df = df.copy()   # Working copy
```

**Tracked:**
- `original_rows`
- `columns`

---

### Step 2: Trim & Normalize Strings
**Function:** `DataCleaningPipeline.trim_and_normalize_strings()`

Uses `clean_string()` from `utils.py`:
- Strip leading/trailing spaces
- Convert to lowercase
- Remove special characters via regex

**Applied to:** All `object` dtype columns

**Example:**
```
"  John DOE!!  " → "john doe"
```

**Tracked:** Count of values changed

---

### Step 3: Fix Dates
**Function:** `DataCleaningPipeline.fix_dates()`

For each column:
1. Call `detect_column_type()` → check if 'date'
2. Try `pd.to_datetime(errors='coerce')`
3. If >70% values convert successfully → use it
4. Format as `'%Y-%m-%d'` string

**Detects:** Multiple date formats automatically

**Example:**
```
"15/01/2023" → "2023-01-15"
"1-15-2023" → "2023-01-15"
"2023-01-15" → "2023-01-15" (unchanged)
```

**Tracked:** Count of date columns fixed

---

### Step 4: Handle Missing Values
**Function:** `DataCleaningPipeline.handle_missing_values()`

For each column with NaN:
- **Numeric** → Fill with median
- **Categorical** → Fill with mode (most frequent)
- **Date** → Forward fill, then backward fill
- **Other** → Leave as NaN

**Heuristic:** Uses `detect_column_type()` to classify

**Example:**
```
Numeric: [1, 2, NaN, 4, 5] → [1, 2, 3, 4, 5]  (median=3)
Categorical: ["A", "B", NaN, "B"] → ["A", "B", "B", "B"]  (mode="B")
```

**Tracked:** Total missing values filled

---

### Step 5: Remove Duplicates
**Function:** `DataCleaningPipeline.remove_duplicates()`

Uses `df.drop_duplicates(keep='first')`:
- Keeps first occurrence of each duplicate row
- Removes subsequent identical rows

**Example:**
```
Before: [row1, row1, row2, row1]
After:  [row1, row2]
```

**Tracked:** Number of duplicate rows removed

---

### Step 6: Detect & Replace Outliers
**Function:** `DataCleaningPipeline.detect_and_replace_outliers()`

For each numeric column:
1. Calculate Q1 (25th percentile), Q3 (75th percentile)
2. IQR = Q3 - Q1
3. Lower bound = Q1 - 1.5×IQR
4. Upper bound = Q3 + 1.5×IQR
5. Replace outliers with median

**Formula:**
```
outlier = value < (Q1 - 1.5×IQR) OR value > (Q3 + 1.5×IQR)
```

**Example:**
```
Data: [10, 20, 30, 40, 1000]
Q1=20, Q3=40, IQR=20
Bounds: [10-30, 40+30] = [-20, 70]
1000 is outlier → replace with median (30)
Result: [10, 20, 30, 40, 30]
```

**Tracked:** Total outliers replaced

---

### Step 7: Generate Python Script
**Function:** `generate_python_script(cleaning_steps, original_columns)`

Creates standalone `.py` file with all functions embedded:
- Can be run on new CSV files independently
- Includes all helper functions
- Same pipeline steps replicated
- Command-line interface

**Usage:**
```bash
python clean_data.py input.csv output.csv
```

---

### Step 8: AI Report Generation
**Function:** `generate_ai_report(original_df, cleaned_df, cleaning_steps, summary, ai_provider)`

Builds prompt with:
- Original data stats (rows, columns, types)
- Cleaning operations performed
- Final data stats
- Summary metrics

Sends to:
- **OpenAI GPT-4o** (default)
- **Groq Mixtral** (alternative)

**Fallback:** If API fails, generates basic markdown report

---

## Column Type Detection Logic

**Function:** `detect_column_type(series)`

Order of checks:
1. **Numeric?** Try `pd.to_numeric()` → if >80% convert, return 'numeric'
2. **Date?** Try `pd.to_datetime()` → if >80% convert, return 'date'
3. **Categorical?** If unique_ratio < 50%, return 'categorical'
4. **Default:** return 'string'

**Used by:**
- Missing value handling (numeric vs categorical)
- Outlier detection (only numeric)
- String normalization (only object types)

---

## Summary Dictionary

Tracked throughout pipeline:

```python
summary = {
    'original_rows': int,          # Before cleaning
    'cleaned_rows': int,           # After cleaning
    'rows_removed': int,           # Calculated: original - cleaned
    'columns': int,                # Number of columns
    'missing_values_handled': int, # Total nulls filled
    'outliers_replaced': int,      # IQR replacements
    'date_columns_fixed': int,     # Converted to YYYY-MM-DD
    'duplicates_removed': int      # Dropped rows
}
```

---

## Error Handling

### CSV Load Errors
```python
try:
    df = pd.read_csv(file_path)
except Exception as e:
    raise Exception(f"Error loading CSV: {str(e)}")
```

### API Errors
```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    print(f"AI report generation failed: {str(e)}")
    return _fallback_report(summary)
```

### File Upload Validation
```python
if not file.filename.endswith('.csv'):
    raise HTTPException(status_code=400, detail="Only CSV files supported")
```

### Type Detection Edge Cases
```python
if len(non_null) == 0:
    return 'unknown'  # All null column
```

---

## Performance Notes

- **Large files (>50MB):** May timeout (60s limit)
- **Many columns:** Outlier detection iterates each numeric column
- **Unique values:** Cardinality check may be slow for very large datasets
- **AI API:** Slowest step (1-5 seconds depending on provider)

**Optimization opportunities:**
- Chunking for very large files
- Parallel processing for columns
- Caching column type detection

---

## Examples & Test Cases

### Test Case 1: Mixed Data Types
```csv
Name, Age, Salary, JoinDate, Active
john,28,50000, 2023-01-15, yes
Jane,35,60000,15/01/2023,true
  Bob  ,45, $75000  , 1-15-2023 , 1
```

Expected results:
- Names trimmed/normalized
- Salary as numeric ($ removed? NO - stays as string)
- Dates converted to YYYY-MM-DD
- Active as categorical (yes/true/1 → not normalized)

### Test Case 2: Missing Values
```csv
Value, Category
10, A
20,
, B
40, A
```

Expected:
- Missing numeric → filled with median (20)
- Missing categorical → filled with mode (A)

### Test Case 3: Outliers
```csv
Score
100
102
98
99
101
1000
```

Q1=99, Q3=101, IQR=2, bounds=[96, 104]
1000 → replaced with median (100)

### Test Case 4: Duplicates
```csv
ID, Name
1, Alice
2, Bob
1, Alice
```

After duplicate removal:
```csv
ID, Name
1, Alice
2, Bob
```

---

## Extension Points

### Add New Cleaning Step
1. Add method to `DataCleaningPipeline`:
   ```python
   def my_cleaning_step(self):
       # Logic here
       self.cleaning_steps.append({
           'step': 'my_step',
           'description': 'What was done'
       })
   ```

2. Call from `run_pipeline()`:
   ```python
   self.my_cleaning_step()
   ```

3. Update AI report prompt in `ai_report.py`

### Add New Column Type
1. Modify `detect_column_type()` checks
2. Update all cleaning functions that use types
3. Test thoroughly with sample data

### Change Outlier Method
1. Replace IQR logic in `detect_and_replace_outliers()`
2. Test with known outlier datasets
3. Update documentation

---

Last updated: November 14, 2025
