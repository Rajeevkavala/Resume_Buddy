import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from resume_parser import parse_resume
from embedding_utils import create_vector_store, load_embedding_model, embed_query
from analysis import analyze_skills, compute_ats_score, improvement_suggestions
from interview_agent import generate_interview_questions, generate_sample_answers
from export_utils import build_improved_resume_text, generate_docx, generate_pdf
from gemini_integration import (
    get_gemini_service, analyze_resume_with_gemini, 
    generate_interview_questions_gemini, improve_resume_with_gemini, 
    generate_qa_with_gemini
)
import tempfile
import os

# Import modular components
from modules.dashboard import render_dashboard
from modules.resume_analysis import render_analysis_section
from modules.resume_qa import render_qa_section
from modules.interview_questions import render_interview_section
from modules.resume_improvement import render_improvement_section
from modules.resume_summary import render_summary_section

st.set_page_config(page_title="Resume Buddy", layout="wide")

# Load external CSS file
def load_css(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the external CSS file
load_css('static/styles.css')

# Enhanced header - Single header for the application
st.markdown("""
<div class="header-section">
    <h1 class="header-title">🧠 Resume Buddy</h1>
    <p class="header-subtitle">AI-Powered Resume Analyzer & Career Enhancement Platform</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for data persistence and UI state - consolidated navigation
def initialize_session_state():
    """Initialize all session state variables."""
    session_vars = {
        'parsed_resume': None,
        'vector_store': None,
        'analysis_results': None,
        'gemini_service': None,
        'current_section': "Dashboard",
        'ats_results': None,
        'skill_analysis': None,
        'improvement_suggestions': None,
        'interview_questions': None,
        'qa_results': None,
        'improved_resume_content': None,
        'improved_resume': None,
        'job_description': "",
        'selected_role': "Mid-level",
        'use_ocr': False,
        'use_gemini_ai': True,
        'gemini_api_key_input': "",
        'last_analysis_hash': None,
        'last_qa_key': None,
        'last_interview_key': None,
        'last_improvement_key': None,
        'last_jd_hash': None,
        'last_qa_topic': None
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

# Initialize session state
initialize_session_state()

# Enhanced navigation with better button management
def render_enhanced_navbar():
    """Render the enhanced navigation bar with modern styling."""
    current_section = st.session_state.get('current_section', 'Dashboard')
    
    # Calculate progress based on actual completed tasks - only count meaningful completions
    progress_items = [
        ('parsed_resume', 'Resume Upload'),
        ('ats_results', 'Analysis Complete'),
        ('qa_results', 'Q&A Generated'),
        ('interview_questions', 'Interview Questions'),
        ('improved_resume', 'Resume Improved')
    ]
    
    # More strict checking to ensure actual completion, not just initialization
    completed = 0
    if st.session_state.get('parsed_resume') is not None:
        completed += 1
    if st.session_state.get('ats_results') is not None and st.session_state.get('ats_results') != {}:
        completed += 1
    if st.session_state.get('qa_results') is not None and st.session_state.get('qa_results') != []:
        completed += 1
    if st.session_state.get('interview_questions') is not None and st.session_state.get('interview_questions') != []:
        completed += 1
    if st.session_state.get('improved_resume') is not None and str(st.session_state.get('improved_resume')).strip() != '':
        completed += 1
    
    progress_pct = (completed / len(progress_items)) * 100
    
    # Enhanced navigation container
    st.markdown(f"""
    <div class="nav-container">
        <div class="nav-buttons">
            {generate_nav_button("Dashboard", "📋", current_section)}
            {generate_nav_button("Resume Analysis", "📊", current_section)}
            {generate_nav_button("Resume Q&A", "❓", current_section)}
            {generate_nav_button("Interview Questions", "🎤", current_section)}
            {generate_nav_button("Resume Improvement", "✨", current_section)}
            {generate_nav_button("Improved Resume", "📋", current_section)}
        </div>
        <div class="progress-container">
            <div class="progress-title">Overall Progress</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_pct}%;"></div>
            </div>
            <div class="progress-text">{completed}/{len(progress_items)} features completed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Handle navigation button clicks
    handle_navigation_clicks()

def generate_nav_button(section_name, icon, current_section):
    """Generate HTML for navigation button."""
    is_active = section_name == current_section
    section_class = section_name.lower().replace(" ", "_")
    active_class = "active" if is_active else ""
    
    return f"""
    <button class="nav-button {active_class} {section_class}" 
            onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: '{section_name}'}}, '*')">
        {icon} {section_name}
    </button>
    """

def handle_navigation_clicks():
    """Handle navigation button clicks using session state."""
    sections = ["Dashboard", "Resume Analysis", "Resume Q&A", "Interview Questions", "Resume Improvement", "Improved Resume"]
    
    nav_cols = st.columns(len(sections))
    
    for i, section in enumerate(sections):
        with nav_cols[i]:
            if st.button(f"Go to {section}", key=f"nav_btn_{section.replace(' ', '_').lower()}", 
                        type="primary" if section == st.session_state.current_section else "secondary"):
                st.session_state.current_section = section
                st.rerun()

# Sidebar for persistent inputs
def render_sidebar():
    """Render the sidebar with persistent inputs."""
    with st.sidebar:
        st.markdown("### 📄 Resume Upload")
        uploaded_file = st.file_uploader(
            "Choose your resume file", 
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume in PDF, DOCX, or TXT format"
        )
        
        if uploaded_file and not st.session_state.parsed_resume:
            process_uploaded_resume(uploaded_file)
        
        # Job Description
        st.markdown("---")
        st.markdown("### 🎯 Job Description")
        st.session_state.job_description = st.text_area(
            "Paste the job description here",
            value=st.session_state.job_description,
            height=200,
            help="Paste the target job description for better analysis"
        )
        
        # Configuration options
        st.markdown("---")
        st.markdown("### ⚙️ Configuration")
        
        st.session_state.selected_role = st.selectbox(
            "Experience Level",
            ["Entry-level", "Mid-level", "Senior-level", "Executive"],
            index=["Entry-level", "Mid-level", "Senior-level", "Executive"].index(st.session_state.selected_role)
        )
        
        st.session_state.use_ocr = st.checkbox(
            "Use OCR for PDF parsing", 
            value=st.session_state.use_ocr,
            help="Enable for better text extraction from image-based PDFs"
        )
        
        # Gemini AI Configuration
        st.markdown("---")
        st.markdown("### 🤖 AI Configuration")
        
        st.session_state.use_gemini_ai = st.checkbox(
            "Enable Gemini AI", 
            value=st.session_state.use_gemini_ai,
            help="Enable for advanced AI-powered analysis and improvements"
        )
        
        if st.session_state.use_gemini_ai:
            st.session_state.gemini_api_key_input = st.text_input(
                "Gemini API Key",
                value=st.session_state.gemini_api_key_input,
                type="password",
                help="Enter your Google Gemini API key"
            )
            
            if st.session_state.gemini_api_key_input and not st.session_state.gemini_service:
                try:
                    st.session_state.gemini_service = get_gemini_service(st.session_state.gemini_api_key_input)
                    st.success("✅ Gemini AI connected!")
                except Exception as e:
                    st.error(f"❌ Gemini connection failed: {str(e)}")
        
        # Current status
        if st.session_state.parsed_resume:
            st.markdown("---")
            st.markdown("### 📊 Current Status")
            st.success("✅ Resume loaded")
            
            if st.session_state.job_description and st.session_state.job_description.strip():
                st.success("✅ Job description provided")
            else:
                st.warning("⚠️ Job description needed")
            
            if st.session_state.gemini_service:
                st.success("✅ AI enhancement ready")

def process_uploaded_resume(uploaded_file):
    """Process the uploaded resume file."""
    tmp_file_path = None
    with st.spinner("📄 Processing resume..."):
        try:
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Parse resume
            parsed_resume = parse_resume(tmp_file_path)
            st.session_state.parsed_resume = parsed_resume
            
            # Create vector store
            vector_store = create_vector_store(parsed_resume.text)
            st.session_state.vector_store = vector_store
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            st.success("✅ Resume processed successfully!")
            
        except Exception as e:
            st.error(f"❌ Failed to process resume: {str(e)}")
            # Clean up temp file if it exists
            if tmp_file_path:
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass

# Main application logic
def main():
    """Main application function."""
    # Render sidebar
    render_sidebar()
    
    # Render navigation
    render_enhanced_navbar()
    
    # Get current section
    current_section = st.session_state.current_section
    
    # Route to appropriate section
    if current_section == "Dashboard":
        render_dashboard()
    elif current_section == "Resume Analysis":
        render_analysis_section()
    elif current_section == "Resume Q&A":
        render_qa_section()
    elif current_section == "Interview Questions":
        render_interview_section()
    elif current_section == "Resume Improvement":
        render_improvement_section()
    elif current_section == "Improved Resume":
        render_summary_section()
    else:
        # Fallback to dashboard
        render_dashboard()

if __name__ == "__main__":
    main()
