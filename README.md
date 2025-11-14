# Data Cleaning Bot 🤖

An intelligent, full-stack CSV data cleaning application powered by AI. Upload your messy CSV files and get automatically cleaned data with Python scripts and AI-generated reports.

## 🎯 Features

✅ **Automatic Data Cleaning**
- Trim leading/trailing whitespace from string columns
- Normalize strings (lowercase, remove special characters)
- Fix date formats to YYYY-MM-DD
- Handle missing values (mean/median for numeric, mode for categorical)
- Remove duplicate rows
- Detect and replace outliers using IQR method

✅ **Generated Outputs**
- Download cleaned CSV file
- Download reusable Python cleaning script
- Get AI-powered analysis report explaining what was cleaned

✅ **User-Friendly Interface**
- Simple drag-and-drop file upload
- Real-time cleaning progress indicator
- Beautiful display of cleaning statistics
- Error boundaries and graceful error handling

## 🧰 Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **OpenAI / Groq** - AI-powered report generation

### Frontend
- **Next.js 14** - React framework with server-side rendering
- **React 18** - UI components
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API communication

### Deployment
- **Vercel** - Serverless backend and frontend hosting

## 📁 Project Structure

```
data-cleaning-bot/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── cleaning_logic.py       # Core cleaning pipeline
│   ├── ai_report.py           # AI report generation
│   ├── utils.py               # Utility functions
│   ├── requirements.txt        # Python dependencies
│   └── .env.example           # Environment variables template
├── frontend/
│   ├── app/
│   │   ├── page.jsx           # Main page component
│   │   └── layout.jsx         # Root layout
│   ├── components/
│   │   ├── FileUploader.jsx   # File upload with drag-drop
│   │   ├── DownloadButtons.jsx # Download buttons
│   │   ├── CleaningSummary.jsx # Statistics display
│   │   ├── AIReport.jsx       # AI report display
│   │   ├── LoadingSpinner.jsx # Loading indicator
│   │   └── ErrorBoundary.jsx  # Error handling
│   ├── utils/
│   │   └── api.js             # API client
│   ├── styles/
│   │   └── globals.css        # Global CSS
│   ├── package.json           # Node dependencies
│   ├── next.config.js         # Next.js config
│   ├── tailwind.config.js     # Tailwind config
│   ├── tsconfig.json          # TypeScript config
│   └── .env.local             # Environment variables
├── README.md                   # This file
├── .gitignore                 # Git ignore rules
└── vercel.json                # Vercel deployment config
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- pip and npm

### Installation

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd frontend
npm install
```

### Configuration

#### Backend Environment
Copy `.env.example` to `.env` and add your API keys:
```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

Set these variables:
```env
OPENAI_API_KEY=sk-your-openai-key-here
GROQ_API_KEY=gsk-your-groq-key-here
AI_PROVIDER=openai  # or 'groq'
PORT=8000
```

#### Frontend Environment
The frontend uses `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🎮 Running Locally

### Start Backend
```bash
cd backend
python main.py
```
Backend runs on `http://localhost:8000`

### Start Frontend
In a new terminal:
```bash
cd frontend
npm run dev
```
Frontend runs on `http://localhost:3000`

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

## 📚 API Documentation

### POST /clean
Upload a CSV file for cleaning.

**Request:**
- `Content-Type: multipart/form-data`
- `file`: CSV file (required)

**Response:**
```json
{
  "success": true,
  "message": "Data cleaned successfully",
  "cleaned_csv_base64": "base64_encoded_csv",
  "cleaning_script_base64": "base64_encoded_python_script",
  "ai_report": "human_readable_report",
  "summary": {
    "original_rows": 1000,
    "cleaned_rows": 950,
    "rows_removed": 50,
    "columns": 10,
    "missing_values_handled": 25,
    "outliers_replaced": 8,
    "date_columns_fixed": 2,
    "duplicates_removed": 17
  }
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## 🧠 Cleaning Pipeline

The cleaning pipeline processes data in this order:

1. **Load CSV** - Parse CSV file into DataFrame
2. **Trim & Normalize Strings** - Remove extra spaces, lowercase, normalize special characters
3. **Fix Dates** - Convert to YYYY-MM-DD format
4. **Handle Missing Values** - Use median for numeric, mode for categorical
5. **Remove Duplicates** - Keep first occurrence, remove subsequent
6. **Detect & Replace Outliers** - IQR method, replace with median
7. **Generate Script** - Create reusable Python script
8. **AI Report** - Generate human-readable insights

## 💻 Generated Python Script

The system generates a standalone Python script that can be reused:

```bash
python clean_data.py input.csv output.csv
```

The script includes:
- All cleaning functions
- Same pipeline steps applied
- Column detection logic
- Error handling

## 🤖 AI Report Generation

Reports are powered by:
- **OpenAI GPT-4o** (default, requires API key)
- **Groq Mixtral** (alternative, faster)

Reports include:
- Data quality before/after
- Issues found and fixed
- Improvements achieved
- Recommendations

## 🌐 Deployment to Vercel

### Backend (Serverless Functions)

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Update `backend/main.py` for serverless:
```python
from mangum import Mangum
handler = Mangum(app)
```

3. Create `vercel.json`:
```json
{
  "buildCommand": "cd backend && pip install -r requirements.txt",
  "outputDirectory": "backend"
}
```

4. Deploy:
```bash
vercel --prod
```

### Frontend
```bash
cd frontend
vercel --prod
```

## 📋 Example Workflow

1. Open `http://localhost:3000`
2. Click or drag-drop a CSV file
3. System processes the file (progress indicator shows)
4. View cleaning summary and statistics
5. Download cleaned CSV
6. Download Python script for future use
7. Read AI analysis report

## 🧪 Testing

### Backend Unit Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 Code Comments

All code includes detailed inline comments explaining:
- Purpose of each function
- Parameter descriptions
- Return values
- Complex logic steps

This makes the code ideal for educational purposes and team understanding.

## 🐛 Troubleshooting

### "Connection refused" error
- Ensure backend is running: `python backend/main.py`
- Check port 8000 is not in use
- Verify `NEXT_PUBLIC_API_URL` in frontend `.env.local`

### API key errors
- Verify `OPENAI_API_KEY` or `GROQ_API_KEY` is set in backend `.env`
- Check keys are valid (no typos)
- Ensure account has credits/quota

### CSV Upload fails
- Check file is valid CSV format
- File size under 50MB
- No special characters in filename
- Try with sample data first

### Dates not converting
- Ensure date column has consistent format
- Common formats are auto-detected
- 70%+ of values must be parseable as dates

## 📖 Learning Resources

This project demonstrates:
- FastAPI framework usage
- Data cleaning best practices
- Error handling and validation
- AI API integration
- Frontend-backend communication
- Docker deployment
- Environment configuration

Perfect for students learning:
- Full-stack development
- Data engineering
- API design
- React patterns

## 📄 License

MIT License - Feel free to use for learning and projects!

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional data cleaning operations
- Support for other file formats (Excel, JSON)
- Advanced outlier detection methods
- Custom cleaning rules UI
- Batch processing
- Data profiling visualizations

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review code comments and documentation
3. Check API response error messages
4. Review browser console for frontend errors

---

**Made with ❤️ for students and data enthusiasts**
