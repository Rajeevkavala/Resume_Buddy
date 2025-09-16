import streamlit as st

# Page configuration MUST be the first Streamlit command
st.set_page_config(page_title="Resume Buddy", layout="wide")

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time
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
from modules.session_utils import clear_all_data

# Toast message utilities
def show_toast(message, type="info", duration=3):
    """Show a toast message with auto-dismiss."""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)
    
    # Auto-dismiss after duration (for better UX)
    time.sleep(0.1)  # Brief pause for visibility

def show_loading_spinner(message="Processing..."):
    """Show a loading spinner with custom message."""
    return st.spinner(message)

def show_progress_bar(progress, message=""):
    """Show a progress bar with optional message."""
    if message:
        st.text(message)
    progress_bar = st.progress(progress)
    return progress_bar

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
    """Initialize all session state variables with persistence support."""
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
        'last_qa_topic': None,
        # Background processing states
        'analysis_in_progress': False,
        'qa_in_progress': False,
        'interview_in_progress': False,
        'improvement_in_progress': False,
        # Processing completion flags
        'analysis_completed': False,
        'qa_completed': False,
        'interview_completed': False,
        'improvement_completed': False,
        # Data persistence key for browser refresh recovery
        'session_id': None,
    'data_hash': None,
    # Widget reset nonces
    'resume_uploader_nonce': 0
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

"""Use clear_all_data from modules.session_utils"""

# Initialize session state
initialize_session_state()

# Data persistence and recovery system using Streamlit cache
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_session_data(session_key):
    """Get cached session data."""
    return None

@st.cache_data(ttl=3600)
def set_cached_session_data(session_key, data):
    """Set cached session data."""
    return data

def save_session_data():
    """Save critical session data using Streamlit's caching."""
    if st.session_state.parsed_resume:
        import hashlib
        
        # Create a unique session identifier based on resume content
        if not st.session_state.session_id:
            content_hash = hashlib.md5(
                f"{st.session_state.parsed_resume.text[:100]}{st.session_state.job_description[:50]}".encode()
            ).hexdigest()[:16]
            st.session_state.session_id = content_hash
        
        # Prepare data for persistence
        persistent_data = {
            'parsed_resume_text': st.session_state.parsed_resume.text if st.session_state.parsed_resume else None,
            'job_description': st.session_state.job_description,
            'selected_role': st.session_state.selected_role,
            'current_section': st.session_state.current_section,
            'use_gemini_ai': st.session_state.use_gemini_ai,
            'gemini_api_key_input': st.session_state.gemini_api_key_input,
            'analysis_completed': st.session_state.get('analysis_completed', False),
            'qa_completed': st.session_state.get('qa_completed', False),
            'interview_completed': st.session_state.get('interview_completed', False),
            'improvement_completed': st.session_state.get('improvement_completed', False),
        }
        
        # Save using Streamlit cache
        set_cached_session_data(st.session_state.session_id, persistent_data)

def load_session_data():
    """Load session data from cache if available."""
    if st.session_state.session_id:
        cached_data = get_cached_session_data(st.session_state.session_id)
        if cached_data:
            # Normalize to dict for safe iteration
            data_dict = cached_data if isinstance(cached_data, dict) else {}
            # Restore data to session state
            for key, value in data_dict.items():
                if key != 'parsed_resume_text':
                    st.session_state[key] = value
            
            # Restore parsed resume if available
            if data_dict.get('parsed_resume_text') and not st.session_state.parsed_resume:
                from resume_parser import ParseResult
                st.session_state.parsed_resume = ParseResult(
                    text=data_dict['parsed_resume_text'],
                    meta={"restored": "true"},
                    ocr_used=False
                )

# Enhanced background processing system
def start_background_analysis():
    """Start analysis in background."""
    if (st.session_state.parsed_resume and st.session_state.job_description.strip() 
        and not st.session_state.analysis_in_progress and not st.session_state.analysis_completed):
        
        st.session_state.analysis_in_progress = True
        # The actual analysis will be triggered when switching back to analysis section

def start_background_qa():
    """Start Q&A generation in background."""
    if (st.session_state.parsed_resume and not st.session_state.qa_in_progress 
        and not st.session_state.qa_completed):
        
        st.session_state.qa_in_progress = True

def start_background_interview():
    """Start interview questions generation in background."""
    if (st.session_state.parsed_resume and st.session_state.job_description.strip()
        and not st.session_state.interview_in_progress and not st.session_state.interview_completed):
        
        st.session_state.interview_in_progress = True

def start_background_improvement():
    """Start resume improvement in background."""
    if (st.session_state.ats_results and st.session_state.skill_analysis
        and not st.session_state.improvement_in_progress and not st.session_state.improvement_completed):
        
        st.session_state.improvement_in_progress = True

# Enhanced navigation with better button management
def render_enhanced_navbar():
    """Render the enhanced navigation bar with modern styling and background processing."""
    current_section = st.session_state.get('current_section', 'Dashboard')
    
    # Auto-save session data on navigation
    save_session_data()
    
    # Calculate progress based on actual completed tasks - only count meaningful completions
    progress_items = [
        ('parsed_resume', 'Resume Upload'),
        ('analysis_completed', 'Analysis Complete'),
        ('qa_completed', 'Q&A Generated'),
        ('interview_completed', 'Interview Questions'),
        ('improvement_completed', 'Resume Improved')
    ]
    
    # More strict checking to ensure actual completion, not just initialization
    completed = 0
    if st.session_state.get('parsed_resume') is not None:
        completed += 1
    if st.session_state.get('analysis_completed', False):
        completed += 1
    if st.session_state.get('qa_completed', False):
        completed += 1
    if st.session_state.get('interview_completed', False):
        completed += 1
    if st.session_state.get('improvement_completed', False):
        completed += 1
    
    progress_pct = (completed / len(progress_items)) * 100
    
    # Show background processing status
    show_background_status()
    
    # Enhanced navigation with beautiful container - CSS-only responsive approach
    st.markdown("""
    <div class="nav-container">
        <div class="navigation-title">🧭 Navigation</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation sections with icons - optimized for responsive design
    sections = ["Dashboard", "Resume Analysis", "Resume Q&A", "Interview Questions", "Resume Improvement", "Improved Resume"]
    icons = ["📋", "📊", "❓", "🎤", "✨", "📄"]
    
    # Adaptive short names for smaller screens
    short_names = ["Dashboard", "Analysis", "Q&A", "Interview", "Improve", "Summary"]
    
    # Create columns with responsive spacing
    nav_cols = st.columns(len(sections), gap="small")
    
    for i, (section, icon, short_name) in enumerate(zip(sections, icons, short_names)):
        with nav_cols[i]:
            button_type = "primary" if section == current_section else "secondary"
            
            # Create responsive button text with proper formatting
            # Use shorter names for better mobile display
            display_name = short_name if len(short_name) <= 8 else section
            button_text = f"{icon}\n{display_name.replace(' ', '\n')}"
            
            if st.button(button_text, key=f"nav_btn_{section.replace(' ', '_').lower()}", 
                        type=button_type, use_container_width=True,
                        help=f"Navigate to {section}"):  # Add tooltip for clarity
                
                # Handle section switching with background processing
                handle_section_switch(current_section, section)
                st.session_state.current_section = section
                st.rerun()

def show_background_status():
    """Show background processing status."""
    status_items = []
    
    if st.session_state.get('analysis_in_progress', False):
        status_items.append("🔄 Analysis Running")
    if st.session_state.get('qa_in_progress', False):
        status_items.append("🔄 Q&A Generation")
    if st.session_state.get('interview_in_progress', False):
        status_items.append("🔄 Interview Questions")
    if st.session_state.get('improvement_in_progress', False):
        status_items.append("🔄 Resume Improvement")
    
    if status_items:
        st.info(f"Background Processing: {' | '.join(status_items)}")

def handle_section_switch(from_section, to_section):
    """Handle section switching and background processing triggers."""
    # Start background processing for other sections when conditions are met
    if st.session_state.parsed_resume and st.session_state.job_description.strip():
        
        # Trigger background analysis if not completed
        if to_section != "Resume Analysis" and not st.session_state.get('analysis_completed', False):
            start_background_analysis()
        
        # Trigger background Q&A if not completed
        if to_section != "Resume Q&A" and not st.session_state.get('qa_completed', False):
            start_background_qa()
        
        # Trigger background interview questions if not completed
        if to_section != "Interview Questions" and not st.session_state.get('interview_completed', False):
            start_background_interview()
        
        # Trigger background improvement if analysis is complete
        if (to_section != "Resume Improvement" and 
            st.session_state.get('analysis_completed', False) and 
            not st.session_state.get('improvement_completed', False)):
            start_background_improvement()

def render_progress_indicator():
    """Render the progress indicator."""
    # Calculate progress based on actual completed tasks
    progress_items = [
        ('parsed_resume', 'Resume Upload'),
        ('ats_results', 'Analysis Complete'),
        ('qa_results', 'Q&A Generated'),
        ('interview_questions', 'Interview Questions'),
        ('improved_resume', 'Resume Improved')
    ]
    
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
    
    # Progress indicator
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-title">Overall Progress</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_pct}%;"></div>
        </div>
        <div class="progress-text">{completed}/{len(progress_items)} features completed</div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar for persistent inputs
def render_sidebar():
    """Render the sidebar with persistent inputs."""
    with st.sidebar:
        st.markdown("### 📄 Resume Upload")
        uploaded_file = st.file_uploader(
            "Choose your resume file", 
            type=['pdf', 'docx', 'txt'],
            help="Upload your resume in PDF, DOCX, or TXT format",
            key=f"resume_file_uploader_{st.session_state.resume_uploader_nonce}"
        )
        
        if uploaded_file and not st.session_state.parsed_resume:
            process_uploaded_resume(uploaded_file)
        
        # Job Description
        st.markdown("---")
        st.markdown("### 🎯 Job Description")
        jd_val = st.text_area(
            "Paste the job description here",
            value=st.session_state.job_description,
            height=200,
            help="Paste the target job description for better analysis",
            key=f"job_description_input"
        )
        st.session_state.job_description = jd_val or ""
        
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
        
        # Clear All Data Button
        st.markdown("---")
        st.markdown("### 🗑️ Data Management")
        
        # Check if there's any data to clear
        has_data = (st.session_state.parsed_resume or 
                   (st.session_state.job_description and st.session_state.job_description.strip()) or
                   st.session_state.ats_results or 
                   st.session_state.qa_results or 
                   st.session_state.interview_questions or 
                   st.session_state.improved_resume)
        
        if has_data:
            # Show what data will be cleared
            st.markdown("**Data to clear:**")
            if st.session_state.parsed_resume:
                st.markdown("• 📄 Uploaded resume")
            if st.session_state.job_description and st.session_state.job_description.strip():
                st.markdown("• 🎯 Job description")
            if st.session_state.ats_results:
                st.markdown("• 📊 Analysis results")
            if st.session_state.qa_results:
                st.markdown("• ❓ Q&A results")
            if st.session_state.interview_questions:
                st.markdown("• 🎤 Interview questions")
            if st.session_state.improved_resume:
                st.markdown("• ✨ Improved resume")
            
            button_type = "primary"
        else:
            st.info("💡 No data to clear")
            button_type = "secondary"
        
        if st.button("🗑️ Clear All Data", 
                    type=button_type, 
                    help="Clear all uploaded resume data, job description, and analysis results",
                    use_container_width=True,
                    disabled=not has_data):
            # Add confirmation
            if 'confirm_clear' not in st.session_state:
                st.session_state.confirm_clear = False
            
            if not st.session_state.confirm_clear:
                st.warning("⚠️ This will clear ALL data including resume, job description, and analysis results.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirm", type="primary", use_container_width=True):
                        st.session_state.confirm_clear = True
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.confirm_clear = False
            else:
                with show_loading_spinner("🧹 Clearing all data..."):
                    time.sleep(0.5)  # Brief pause for user feedback
                    clear_all_data()
                    st.session_state.confirm_clear = False  # Reset confirmation
                    
                show_toast("🗑️ All data cleared successfully!", "success")
                st.rerun()  # Refresh the page to show cleared state

def process_uploaded_resume(uploaded_file):
    """Process the uploaded resume file with enhanced loading and feedback."""
    tmp_file_path = None
    
    # Create progress stages
    progress_stages = [
        ("📁 Preparing file...", 0.2),
        ("� Extracting text...", 0.4),
        ("🤖 Initializing AI...", 0.6),
        ("🧠 Creating search index...", 0.8),
        ("✅ Finalizing...", 1.0)
    ]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Stage 1: Prepare file
        status_text.text(progress_stages[0][0])
        progress_bar.progress(progress_stages[0][1])
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        time.sleep(0.3)
        
        # Stage 2: Parse resume
        status_text.text(progress_stages[1][0])
        progress_bar.progress(progress_stages[1][1])
        
        parsed_resume = parse_resume(tmp_file_path)
        st.session_state.parsed_resume = parsed_resume
        time.sleep(0.3)
        
        # Stage 3: Initialize AI if enabled
        status_text.text(progress_stages[2][0])
        progress_bar.progress(progress_stages[2][1])
        
        if st.session_state.use_gemini_ai and st.session_state.gemini_api_key_input:
            try:
                gemini_service = get_gemini_service(st.session_state.gemini_api_key_input)
                st.session_state.gemini_service = gemini_service
                show_toast("🤖 AI service activated successfully!", "success")
            except Exception as e:
                show_toast(f"⚠️ AI service failed: {str(e)}", "warning")
                st.session_state.gemini_service = None
        time.sleep(0.3)
        
        # Stage 4: Create vector store
        status_text.text(progress_stages[3][0])
        progress_bar.progress(progress_stages[3][1])
        
        vector_store = create_vector_store(parsed_resume.text)
        st.session_state.vector_store = vector_store
        time.sleep(0.3)
        
        # Stage 5: Finalize
        status_text.text(progress_stages[4][0])
        progress_bar.progress(progress_stages[4][1])
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        time.sleep(0.2)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        show_toast("🎉 Resume processed successfully! Ready for analysis.", "success")
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        show_toast(f"❌ Failed to process resume: {str(e)}", "error")
        
        # Clean up temp file if it exists
        if tmp_file_path:
            try:
                os.unlink(tmp_file_path)
            except:
                pass

# Main application logic
def main():
    """Main application function with data persistence and background processing."""
    # Load cached session data if available
    load_session_data()
    
    # Render sidebar
    render_sidebar()
    
    # Render navigation
    render_enhanced_navbar()
    
    # Render progress indicator
    render_progress_indicator()
    
    # Get current section
    current_section = st.session_state.current_section
    
    # Route to appropriate section
    if current_section == "Dashboard":
        render_dashboard()
    elif current_section == "Resume Analysis":
        render_analysis_section()
        # Mark analysis as completed when results exist
        if st.session_state.ats_results and st.session_state.skill_analysis:
            st.session_state.analysis_completed = True
            st.session_state.analysis_in_progress = False
    elif current_section == "Resume Q&A":
        render_qa_section()
        # Mark Q&A as completed when results exist
        if st.session_state.qa_results:
            st.session_state.qa_completed = True
            st.session_state.qa_in_progress = False
    elif current_section == "Interview Questions":
        render_interview_section()
        # Mark interview as completed when results exist
        if st.session_state.interview_questions:
            st.session_state.interview_completed = True
            st.session_state.interview_in_progress = False
    elif current_section == "Resume Improvement":
        render_improvement_section()
        # Mark improvement as completed when results exist
        if st.session_state.improved_resume:
            st.session_state.improvement_completed = True
            st.session_state.improvement_in_progress = False
    elif current_section == "Improved Resume":
        render_summary_section()
    else:
        # Fallback to dashboard
        render_dashboard()
    
    # Auto-save session data after rendering
    save_session_data()

if __name__ == "__main__":
    main()
