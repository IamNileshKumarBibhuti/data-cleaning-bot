# Copilot Instructions for Data Cleaning Bot

## Project Overview

**Data Cleaning Bot** is a full-stack AI-powered CSV data cleaning application. Users upload messy CSVs → system cleans them automatically → generates cleaned CSV, Python script, and AI analysis report.

**Core Architecture:**
- **Backend:** FastAPI (Python) processes data via pipeline at `POST /clean`
- **Frontend:** Next.js 14 + React + Tailwind CSS for upload UI and results display
- **AI Integration:** OpenAI GPT-4o or Groq for generating cleaning reports
- **Data Pipeline:** 7-step cleaning sequence tracked for script generation

## Key Files & Responsibilities

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app with `/clean` and `/health` endpoints |
| `backend/cleaning_logic.py` | DataCleaningPipeline class - orchestrates 7 cleaning steps |
| `backend/ai_report.py` | Generates human-readable reports via OpenAI/Groq APIs |
| `backend/utils.py` | Helpers: string cleaning, column type detection, formatting |
| `frontend/app/page.jsx` | Main page - file upload, results display, state management |
| `frontend/components/FileUploader.jsx` | Drag-drop file input with validation |
| `frontend/utils/api.js` | Axios client for `/clean` endpoint (base64 decode/encode) |

## Cleaning Pipeline (Must Understand)

The `DataCleaningPipeline.run_pipeline()` executes these steps sequentially:

1. **Load CSV** → Creates backup copy in `self.original_df`
2. **Trim & Normalize** → Apply `clean_string()` to object columns (strip, lowercase)
3. **Fix Dates** → Detect via `detect_column_type()`, convert to `YYYY-MM-DD`
4. **Handle Missing** → Median (numeric), mode (categorical), ffill (dates)
5. **Remove Duplicates** → Keep first occurrence
6. **Detect Outliers** → IQR method (Q1/Q3 ± 1.5×IQR), replace with median
7. **Finalize** → Update summary statistics

Each step appends to `self.cleaning_steps` list (for script generation).

## Critical Patterns

### Column Type Detection
```python
# Used everywhere to determine treatment
detect_column_type(series) → returns 'numeric' | 'categorical' | 'date' | 'string'
```
Heuristic: tries pd.to_numeric, pd.to_datetime, checks cardinality ratio. **Fallback:** return 'string'.

### Base64 Encoding/Decoding
Results flow as base64 (CSV → string → base64 → frontend → atob() → blob → download). See `DownloadButtons.jsx` line with `atob()`.

### API Response Shape
All endpoints return `CleaningResponse` pydantic model:
```python
{
  "success": bool,
  "message": str,
  "cleaned_csv_base64": str,
  "cleaning_script_base64": str,
  "ai_report": str,
  "summary": dict
}
```

### Environment Configuration
- Backend: `OPENAI_API_KEY` or `GROQ_API_KEY` in `.env`
- Frontend: `NEXT_PUBLIC_API_URL` in `.env.local` (must prefix with `NEXT_PUBLIC_`)
- Fallback if AI fails: use `_fallback_report()` in `ai_report.py`

## Developer Workflows

### Run Backend Locally
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
python main.py
# Runs on http://localhost:8000
```

### Run Frontend Locally
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### Test Cleaning Pipeline
```bash
# From backend directory
python -c "from cleaning_logic import DataCleaningPipeline; p = DataCleaningPipeline(); df, steps, summary = p.run_pipeline('test.csv'); print(summary)"
```

### Generate Python Script
Inspect `generate_python_script()` in `cleaning_logic.py` — it's a template string that creates a standalone executable script with all functions embedded.

## Common Modifications & Their Impact

| Change | Files Affected | Notes |
|--------|---|---|
| Add new cleaning step | `cleaning_logic.py` (add to pipeline), `ai_report.py` (document in prompt) | Update summary dict, append to `cleaning_steps` |
| Change column detection | `utils.py` (`detect_column_type`) | Used by all cleaning steps — test thoroughly |
| Add output format | `backend/main.py` (`/clean` response) | Update `CleaningSummary`, `DownloadButtons` components |
| Modify AI prompt | `ai_report.py` (prompt string) | Change prompt content, not API structure |
| Update UI layout | `frontend/app/page.jsx` and components | All styled with Tailwind, check mobile responsiveness |

## Edge Cases & Error Handling

1. **File Upload Errors:** Validated in `FileUploader.jsx` (`.endswith('.csv')`); backend checks again with `file.filename.endswith('.csv')`
2. **AI API Failures:** Caught in `generate_ai_report()` → fallback to `_fallback_report()`
3. **Column Type Ambiguity:** `detect_column_type()` uses 70% success threshold; undetected → 'string'
4. **Missing Values (all-null column):** Not explicitly filled, remains null (safe fallback)
5. **Temp File Cleanup:** Always in `try/finally` in `backend/main.py`

## Integration Points

- **Frontend → Backend:** POST `/clean` with FormData file → receive JSON
- **Backend → AI API:** Build prompt from df stats → call OpenAI/Groq → extract text response
- **Result Flow:** DataFrame → CSV string → base64 → JSON → frontend → decode → download

## Testing & Validation

- Health check: `curl http://localhost:8000/health`
- Sample CSV: Create with mixed data types, missing values, dates, duplicates, outliers
- Manual test: Upload in UI, verify all outputs (CSV, script, report)

## Deployment Checklist

- [ ] Set `AI_PROVIDER` env var (openai or groq)
- [ ] Verify API key is set and has quota
- [ ] Set `NEXT_PUBLIC_API_URL` to backend URL in production
- [ ] Test `/clean` endpoint with sample file
- [ ] Verify generated script runs standalone
- [ ] Check all downloads work (blob creation, file names)
- [ ] Monitor API costs (OpenAI charges per request)

## Useful Debugging

- **Backend logs:** Print to stdout in `uvicorn` (auto-reloads)
- **Frontend console:** Browser DevTools → Network tab to see `/clean` request/response
- **Base64 decode:** Copy base64 string, decode at `https://www.base64decode.org/`
- **DataFrame issues:** Use `df.dtypes`, `df.isnull().sum()`, `df.head()` in terminal
