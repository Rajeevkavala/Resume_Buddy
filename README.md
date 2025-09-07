# 🧠 Resume Buddy – AI-Powered Resume Analyzer

Advanced AI-powered resume analysis & improvement assistant with Google Gemini integration. Upload a PDF/DOCX resume and optionally a Job Description to get comprehensive analysis, interview prep, and improvement suggestions.

## ✨ Features

### 📊 Resume Analysis
- **Traditional Analysis**: ATS scoring, skills gap identification, coverage metrics
- **AI-Enhanced Analysis**: Google Gemini-powered deep insights and recommendations
- **Visual Metrics**: Score displays, coverage percentages, skill matching

### ❓ Resume Q&A  
- **Topic-Based Q&A**: Generate Q&A for Technical Skills, Leadership, Projects, etc.
- **Custom Topics**: Create Q&A for any specific area
- **AI-Powered**: Uses Gemini for contextual, relevant questions and answers

### 🎤 Interview Questions
- **Role-Specific Questions**: Behavioral, technical, and mixed question types
- **Sample Answers**: AI-generated answers based on your resume content
- **Interview Insights**: What interviewers are looking for in each response
- **Customizable**: Choose number of questions and focus areas

### ✨ Resume Improvement
- **AI-Enhanced Rewriting**: Gemini-powered resume improvement with focus areas
- **Professional Formatting**: Structured output with clear sections
- **Export Options**: Download improved resumes as DOCX or PDF
- **Multiple Focus Areas**: Target specific improvement areas

### 🔧 Technical Features
- **Multi-format Support**: PDF, DOCX, scanned documents (OCR)
- **Local Vector Store**: FAISS-based semantic search
- **Session Management**: Persistent data across app interactions
- **Export Capabilities**: Professional DOCX and PDF generation

## 🏗️ Architecture

```
app.py                     Main Streamlit interface with 5 sections
resume_parser.py           File extraction & OCR (PDF, DOCX, scanned)
embedding_utils.py         Chunking + embeddings + FAISS vector store
analysis.py                Traditional skills analysis & ATS scoring
interview_agent.py         Local LLM-based question generation (fallback)
export_utils.py            Resume export (DOCX & PDF generation)
gemini_integration.py      Google Gemini AI integration for enhanced features
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Google Gemini API Key (for AI features)
- Tesseract OCR (for scanned PDF support)

### Setup
1. **Clone and create virtual environment:**
```powershell
git clone <repo-url>
cd Resume_Buddy
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. **Install dependencies:**
```powershell
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. **Install OCR dependencies (Windows):**
   - Download Tesseract: https://github.com/tesseract-ocr/tesseract
   - Add Tesseract to PATH
   - Install poppler: https://github.com/oschwartz10612/poppler-windows
   - Add poppler `bin` to PATH

4. **Get Google Gemini API Key:**
   - Visit Google AI Studio: https://makersuite.google.com/app/apikey
   - Create and copy your API key

## 🎯 Usage

### Running the App
```powershell
streamlit run app.py
```

### Using the Application

1. **Upload & Configure**
   - Upload your resume (PDF/DOCX)
   - Paste job description (optional but recommended)
   - Select your role level (Fresher/Mid-level/Senior)
   - Enable Google Gemini AI and enter your API key

2. **Resume Analysis**
   - Get traditional ATS scoring and skills analysis
   - View AI-enhanced insights and recommendations
   - See detailed skill matching and gaps

3. **Resume Q&A**
   - Select a topic or enter custom topic
   - Generate relevant Q&A for interview preparation
   - Use for understanding how to articulate your experience

4. **Interview Questions**
   - Choose question type and quantity
   - Get role-specific interview questions
   - Review sample answers and interviewer expectations

5. **Resume Improvement**
   - Select focus areas for improvement
   - Generate AI-enhanced resume content
   - Download improved versions in DOCX/PDF

## ⚙️ Configuration

### AI Features
- **Default Mode**: Traditional analysis without API requirements
- **Enhanced Mode**: Requires Google Gemini API key for advanced features
- **Fallback Support**: Graceful degradation when API is unavailable

### Model Selection
- **Primary**: Google Gemini 1.5 Flash (fast, cost-effective)
- **Fallback**: Local sentence transformers for embeddings
- **OCR**: Tesseract for scanned document processing

## 🔒 Privacy & Security
- **Local-First**: Core analysis runs locally
- **Optional AI**: Gemini integration is opt-in
- **Data Privacy**: Resume content sent to Gemini only when explicitly enabled
- **No Storage**: No permanent storage of personal data

## 🎨 UI Sections

1. **📊 Resume Analysis**: Metrics, traditional + AI analysis
2. **❓ Resume Q&A**: Topic-based question generation  
3. **🎤 Interview Questions**: Interview preparation with sample answers
4. **✨ Resume Improvement**: AI-powered content enhancement
5. **📋 Improved Resume Summary**: Dashboard and quick actions

## 🔧 Advanced Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_api_key_here  # Optional, can be entered in UI
```

### Model Customization
Edit `gemini_integration.py` to:
- Change model (gemini-1.5-flash, gemini-1.5-pro)
- Adjust temperature and token limits
- Modify prompt templates

## 🚨 Limitations
- **Skill extraction**: Heuristic-based; accuracy varies by resume format
- **ATS scoring**: Approximate algorithm, not official ATS
- **AI dependencies**: Gemini features require API key and internet
- **Large files**: Processing time varies with document size

## 🔄 Fallback Behavior
- **No API key**: Traditional analysis still available
- **API errors**: Graceful fallback to local processing  
- **Network issues**: Local features continue to work
- **Large documents**: Automatic text truncation for API limits

## 🛠️ Troubleshooting

### Common Issues
1. **OCR not working**: Install Tesseract and add to PATH
2. **Gemini API errors**: Check API key validity and quota
3. **Import errors**: Ensure all dependencies installed in virtual environment
4. **Large file processing**: Try with smaller documents or OCR disabled

### Performance Tips
- Use Gemini for best AI features
- Enable OCR only for scanned documents
- Provide detailed job descriptions for better analysis

## 📈 Future Enhancements
- Multi-language support
- Industry-specific templates
- Advanced ATS simulation
- Cover letter generation
- Batch processing capabilities

## 📄 License
MIT License - See LICENSE file for details.
