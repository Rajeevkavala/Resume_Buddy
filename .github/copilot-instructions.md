# Resume Buddy - AI Coding Instructions

## 🎯 Project Overview
Resume Buddy is a Streamlit-based AI-powered resume analyzer that combines traditional ATS scoring with Google Gemini AI enhancement. The application uses a modular architecture with session-based state management and optional OCR capabilities.

## 🏗️ Architecture Patterns

### Modular Design
- **Core App**: `app.py` handles navigation, session state, and routing
- **Modules**: Feature-specific modules in `modules/` directory (dashboard, analysis, Q&A, interview questions, improvement, summary)
- **Utils**: Specialized utilities (`gemini_integration.py`, `embedding_utils.py`, `analysis.py`, `export_utils.py`)
- **Each module exports a `render_[feature]_section()` function called by the main app router**

### Session State Management
**Critical Pattern**: All data persists in `st.session_state` for browser refresh recovery
```python
# Always check session state before processing
if not st.session_state.parsed_resume:
    st.warning("📄 Please upload and analyze a resume first.")
    return

# Cache computation results with hash keys
cached_key = f"{params}_{hash(job_description)}"
if st.session_state.last_key == cached_key:
    # Use cached results
```

### Error Handling & Fallbacks
- **Graceful degradation**: Features work without Gemini API (traditional analysis still available)
- **Optional dependencies**: All AI/ML imports wrapped in try/except blocks
- **User feedback**: Always show progress spinners and success/error messages

## 🔧 Key Development Workflows

### Running the Application
```powershell
# Setup (first time)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run app
streamlit run app.py
```

### Adding New Features
1. Create module in `modules/[feature].py` with `render_[feature]_section()` function
2. Add to navigation in `app.py` sections list around line 825
3. Add routing case in main section around line 1140
4. Initialize any session state variables in `initialize_session_state()`

### Debugging Session Issues
- Check `modules/session_utils.py` for session variable names
- Use `st.rerun()` after session state changes for immediate UI updates
- Session state persists across page refreshes - useful for development

## 🤖 AI Integration Patterns

### Gemini Integration
```python
# Always check if service is available
if st.session_state.gemini_service:
    # Gemini-powered features
else:
    # Fallback to traditional analysis
```

### Vector Store Usage
- Text chunked and embedded using sentence-transformers
- FAISS index for semantic search
- Created once per resume upload, cached in session state

## 📁 File Processing Pipeline

### Resume Parsing Flow
1. **Upload** → `resume_parser.py` (PDF/DOCX extraction, optional OCR)
2. **Embedding** → `embedding_utils.py` (chunk, embed, FAISS index)
3. **Analysis** → `analysis.py` (skill extraction, ATS scoring) + optional Gemini enhancement
4. **Export** → `export_utils.py` (DOCX/PDF generation)

### OCR Configuration
- Requires Tesseract installation and PATH configuration
- Toggle-based: users can force OCR for scanned documents
- Fallback to direct text extraction when OCR unavailable

## 🎨 UI/UX Conventions

### Styling
- External CSS in `static/styles.css` loaded via `load_css()` function
- Gradient backgrounds and modern card layouts
- Progress indicators for multi-step workflows
- Consistent emoji usage for visual hierarchy

### User Experience
- **Single-page app** with section-based navigation
- **Progress tracking** shows completion status across features  
- **Caching notifications** inform users when using previous results
- **Sidebar persistence** for configuration (job description, API keys, settings)

## 🔍 Testing & Validation

### Manual Testing Workflow
1. Upload sample resume (PDF/DOCX)
2. Add job description for enhanced analysis
3. Test each module section independently
4. Verify export functionality (DOCX/PDF downloads)
5. Test with/without Gemini API to verify fallbacks

### Common Issues
- **Large files**: API token limits require text truncation in `gemini_integration.py`
- **OCR dependencies**: Graceful fallback when Tesseract unavailable
- **Session persistence**: Use `st.rerun()` after session state mutations

## 📦 Dependencies & Configuration

### Core Stack
- **Streamlit**: UI framework
- **Google Gemini**: AI enhancement (optional)
- **FAISS**: Vector similarity search
- **spaCy/sentence-transformers**: NLP processing
- **Plotly**: Interactive visualizations

### Environment Setup
- Optional `.env` for `GEMINI_API_KEY`
- API key can be entered in UI sidebar
- All AI features degrade gracefully without API access

## 🚀 Performance Considerations

- **Lazy loading**: Heavy ML models loaded only when needed
- **Caching**: Results cached with hash-based keys to prevent recomputation
- **Text limits**: Gemini requests truncated for token limits
- **Session optimization**: Clear unused session data with `clear_all_data()`

When working on this codebase, prioritize maintaining the modular structure, session state consistency, and graceful fallback patterns that allow the app to function across various user configurations.