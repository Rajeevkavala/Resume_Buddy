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

st.set_page_config(page_title="Resume Buddy", layout="wide")

# Custom CSS for improved UI
st.markdown("""
<style>
    /* Global Styles */
    .main {
        padding-top: 1rem;
    }
    
    /* Enhanced Button Styling with better hover effects */
    .stButton > button {
        background: linear-gradient(145deg, #34495e, #2c3e50);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 24px;
        font-size: 14px;
        font-weight: 600;
        width: 100%;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        margin: 4px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #3498db, #2980b9);
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
        color: white;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
        transition: all 0.1s;
    }
    
    .stButton > button[data-baseweb="button"][kind="primary"] {
        background: linear-gradient(145deg, #e74c3c, #c0392b);
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.3);
    }
    
    .stButton > button[data-baseweb="button"][kind="primary"]:hover {
        background: linear-gradient(145deg, #e74c3c, #c0392b);
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 30px rgba(231, 76, 60, 0.5);
        filter: brightness(1.1);
    }
    
    /* Header Styling */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 32px;
        font-weight: 700;
        margin: -1rem -1rem 2rem -1rem;
        padding: 2rem 1rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Navigation Section */
    .nav-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        border: 1px solid #e1e8ed;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    /* Section Headers */
    .section-header {
        color: white;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e74c3c;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Enhanced Metrics with better hover effects */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e9ecef;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    div[data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3498db, #9b59b6, #e74c3c);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }
    
    div[data-testid="metric-container"]:hover::before {
        transform: scaleX(1);
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        border-color: #3498db;
        background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
    }
    
    /* Enhanced metric values */
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #2c3e50 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    div[data-testid="metric-container"] [data-testid="metric-label"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #7f8c8d !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Enhanced Cards and Containers */
    .content-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border-left: 5px solid #3498db;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .content-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.02) 0%, rgba(155, 89, 182, 0.02) 100%);
        opacity: 0;
        transition: opacity 0.4s ease;
        pointer-events: none;
    }
    
    .content-card:hover::before {
        opacity: 1;
    }
    
    .content-card:hover {
        box-shadow: 0 16px 48px rgba(52, 152, 219, 0.15);
        transform: translateY(-5px);
        border-left-color: #e74c3c;
    }
    
    /* Enhanced Analysis Cards */
    .analysis-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
        border: 2px solid #e3f2fd;
        border-radius: 16px;
        padding: 25px;
        margin: 15px 0;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .analysis-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(33, 150, 243, 0.15);
        border-color: #2196f3;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 20px 0;
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    /* Summary cards with enhanced styling */
    .summary-card {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .summary-card:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15) !important;
    }
    
    /* Sidebar Enhancement */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Current Section Indicator */
    .current-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        font-weight: 600;
        font-size: 18px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Loading Spinner Enhancement */
    .stSpinner > div {
        border-top-color: #e74c3c !important;
    }
    
    /* Info/Warning/Error Messages */
    .stInfo, .stWarning, .stError, .stSuccess {
        border-radius: 10px;
        border-left-width: 5px;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #f8f9fa, #e9ecef);
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Progress Indicators */
    .progress-indicator {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        padding: 15px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    
    .progress-step {
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        flex: 1;
        margin: 0 5px;
        transition: all 0.3s ease;
    }
    
    .progress-step.completed {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        color: white;
    }
    
    .progress-step.active {
        background: linear-gradient(135deg, #e74c3c, #c0392b);
        color: white;
        transform: scale(1.05);
    }
    
    .progress-step.pending {
        background: #ecf0f1;
        color: #7f8c8d;
    }
    
    /* Enhanced CSS with modern navbar styling */
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 0;
    }

    /* Header section */
    .header-section {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px 0;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }

    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: 1px;
    }

    .header-subtitle {
        color: #e0e6ff;
        font-size: 1.1rem;
        text-align: center;
        margin: 10px 0 0 0;
        font-weight: 300;
    }

    /* Enhanced Navigation Bar */
    .nav-container {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        border-radius: 15px;
        padding: 8px;
        margin: 20px 0 30px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .nav-buttons {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        flex-wrap: wrap;
    }

    /* Base button styling */
    .nav-button {
        flex: 1;
        min-width: 180px;
        padding: 16px 20px;
        border: none;
        border-radius: 12px;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Inactive button styling */
    .nav-button:not(.active) {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        color: #ecf0f1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    .nav-button:not(.active):hover {
        background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        color: white;
    }

    /* Active button styling with unique colors */
    .nav-button.active.analysis {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
    }

    .nav-button.active.qa {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
    }

    .nav-button.active.interview {
        background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
        color: white;
        box-shadow: 0 6px 20px rgba(155, 89, 182, 0.4);
    }

    .nav-button.active.improvement {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        box-shadow: 0 6px 20px rgba(243, 156, 18, 0.4);
    }

    .nav-button.active.summary {
        background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        color: white;
        box-shadow: 0 6px 20px rgba(39, 174, 96, 0.4);
    }

    /* Active button hover effects */
    .nav-button.active:hover {
        transform: translateY(-3px) scale(1.02);
        filter: brightness(1.1);
    }

    /* Button text with icons */
    .nav-button::before {
        margin-right: 8px;
        font-size: 1.1rem;
    }

    .nav-button.analysis::before { content: "📊"; }
    .nav-button.qa::before { content: "❓"; }
    .nav-button.interview::before { content: "🎤"; }
    .nav-button.improvement::before { content: "✨"; }
    .nav-button.summary::before { content: "📋"; }

    /* Ripple effect */
    .nav-button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .nav-button:active::after {
        width: 300px;
        height: 300px;
    }

    /* Progress indicator */
    .progress-container {
        margin: 20px 0;
        padding: 20px;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .progress-title {
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 15px;
        text-align: center;
    }

    .progress-bar {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        overflow: hidden;
        height: 8px;
        margin: 10px 0;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #27ae60 0%, #2ecc71 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
    }

    .progress-text {
        color: #ecf0f1;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 8px;
    }

    /* Enhanced cards */
    .summary-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }

    .summary-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }

    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }

    .card-icon {
        font-size: 2rem;
        margin-right: 15px;
    }

    .card-title {
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0;
    }

    .card-content {
        color: #ecf0f1;
        line-height: 1.6;
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 5px 5px 5px 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-complete {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
    }

    .status-pending {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
    }

    .status-error {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .nav-buttons {
            flex-direction: column;
        }
        
        .nav-button {
            min-width: 100%;
            margin: 4px 0;
        }
        
        .header-title {
            font-size: 2rem;
        }
    }

    /* Loading animations */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    .loading {
        animation: pulse 2s infinite;
    }

    /* Subtle animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }

    /* Welcome hero section (clean, class-based; no inline event handlers) */
    .welcome-hero {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #ffffff;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        text-align: center;
    }
    .welcome-hero h1 {
        color: #ffffff;
        font-size: 2.6rem;
        font-weight: 700;
        margin: 0 0 0.75rem 0;
        letter-spacing: -0.5px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .welcome-hero p.lead {
        color: rgba(255,255,255,0.92);
        font-size: 1.15rem;
        margin: 0 0 2rem 0;
        font-weight: 400;
        max-width: 720px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.65;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .welcome-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        max-width: 1000px;
        margin: 0 auto;
    }
    .welcome-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 16px;
        padding: 2rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        text-align: left;
    }
    .welcome-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.18);
        border-color: rgba(255,255,255,0.35);
    }
    .welcome-icon {
        width: 70px;
        height: 70px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 0 1.25rem 0;
        font-size: 2rem;
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .icon-blue { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); }
    .icon-red { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); }
    .icon-purple { background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); }
    .welcome-card h3 {
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    .welcome-card p {
        color: rgba(255,255,255,0.88);
        font-size: 0.98rem;
        margin: 0;
        line-height: 1.6;
    }
    .welcome-cta {
        margin-top: 2.5rem;
        padding-top: 2rem;
        border-top: 1px solid rgba(255,255,255,0.2);
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        font-style: italic;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Enhanced header - Single header for the application
st.markdown("""
<div class="header-section">
    <h1 class="header-title">🧠 Resume Buddy</h1>
    <p class="header-subtitle">AI-Powered Resume Analyzer & Career Enhancement Platform</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for data persistence and UI state - consolidated navigation
if 'parsed_resume' not in st.session_state:
    st.session_state.parsed_resume = None
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'gemini_service' not in st.session_state:
    st.session_state.gemini_service = None
if 'current_section' not in st.session_state:  # Using single navigation state
    st.session_state.current_section = "Resume Analysis"
if 'ats_results' not in st.session_state:
    st.session_state.ats_results = None
if 'skill_analysis' not in st.session_state:
    st.session_state.skill_analysis = None
if 'improvement_suggestions' not in st.session_state:
    st.session_state.improvement_suggestions = None
if 'interview_questions' not in st.session_state:
    st.session_state.interview_questions = None
if 'qa_results' not in st.session_state:
    st.session_state.qa_results = None
if 'improved_resume_content' not in st.session_state:
    st.session_state.improved_resume_content = None
if 'improved_resume' not in st.session_state:
    st.session_state.improved_resume = None

# Initialize persistent sidebar inputs
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = "Mid-level"
if 'use_ocr' not in st.session_state:
    st.session_state.use_ocr = False
if 'use_gemini_ai' not in st.session_state:
    st.session_state.use_gemini_ai = True
if 'gemini_api_key_input' not in st.session_state:
    st.session_state.gemini_api_key_input = ""

# Cache tracking for preventing re-computation
if 'last_analysis_hash' not in st.session_state:
    st.session_state.last_analysis_hash = None
if 'last_qa_key' not in st.session_state:
    st.session_state.last_qa_key = None
if 'last_interview_key' not in st.session_state:
    st.session_state.last_interview_key = None
if 'last_improvement_key' not in st.session_state:
    st.session_state.last_improvement_key = None
if 'last_jd_hash' not in st.session_state:
    st.session_state.last_jd_hash = None
if 'last_qa_topic' not in st.session_state:
    st.session_state.last_qa_topic = None

# Enhanced navigation with better button management
def render_enhanced_navbar():
    """Render the enhanced navigation bar with modern styling."""
    current_section = st.session_state.get('current_section', 'Resume Analysis')
    
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
    
    progress_percentage = (completed / len(progress_items)) * 100
    
    # Progress indicator
    st.markdown(f"""
    <div class="progress-container fade-in">
        <div class="progress-title">Overall Progress</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress_percentage}%"></div>
        </div>
        <div class="progress-text">{completed}/{len(progress_items)} sections completed ({progress_percentage:.0f}%)</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for buttons directly without extra container
    cols = st.columns(5)
    
    sections = [
        ('Resume Analysis', 'analysis', '📊 Resume Analysis'),
        ('Resume Q&A', 'qa', '❓ Resume Q&A'),
        ('Interview Questions', 'interview', '🎤 Interview Questions'),
        ('Resume Improvement', 'improvement', '✨ Resume Improvement'),
        ('Improved Resume', 'summary', '📋 Improved Resume')
    ]
    
    for i, (section_key, css_class, display_name) in enumerate(sections):
        with cols[i]:
            # Display button and handle clicks
            if st.button(display_name, key=f"nav_{section_key}", use_container_width=True):
                st.session_state.current_section = section_key
                st.rerun()

# Render the enhanced navbar
render_enhanced_navbar()

with st.sidebar:
    st.header("📁 Upload & Config")
    uploaded = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf","docx"])
    
    # Persistent job description input
    st.text_area(
        "Paste Job Description", 
        value=st.session_state.job_description,
        height=200,
        key="jd_input",
        on_change=lambda: setattr(st.session_state, 'job_description', st.session_state.jd_input)
    )
    
    # Persistent role selection
    st.selectbox(
        "Role Level", 
        ["Fresher","Mid-level","Senior"], 
        index=["Fresher","Mid-level","Senior"].index(st.session_state.selected_role),
        key="role_input",
        on_change=lambda: setattr(st.session_state, 'selected_role', st.session_state.role_input)
    )
    
    # Persistent OCR checkbox
    st.checkbox(
        "Force OCR (scanned PDF)", 
        value=st.session_state.use_ocr,
        key="ocr_input",
        on_change=lambda: setattr(st.session_state, 'use_ocr', st.session_state.ocr_input)
    )
    
    st.divider()
    st.header("🤖 AI Configuration")
    
    # Persistent Gemini checkbox
    use_gemini = st.checkbox(
        "Use Google Gemini AI", 
        value=st.session_state.use_gemini_ai,
        key="gemini_enabled_input",
        on_change=lambda: setattr(st.session_state, 'use_gemini_ai', st.session_state.gemini_enabled_input)
    )
    
    gemini_api_key = None
    if use_gemini:
        # Persistent API key input
        gemini_api_key = st.text_input(
            "Gemini API Key", 
            type="password",
            value=st.session_state.gemini_api_key_input,
            help="Get your API key from Google AI Studio",
            key="gemini_key_input",
            on_change=lambda: setattr(st.session_state, 'gemini_api_key_input', st.session_state.gemini_key_input)
        )
        if gemini_api_key:
            st.success("✅ Gemini API key provided")
    
    st.divider()
    run_btn = st.button("🚀 Analyze Resume", type="primary")

# Main processing
if run_btn and uploaded:
    with st.spinner("🔍 Parsing resume..."):
        tmpdir = tempfile.mkdtemp()
        path = os.path.join(tmpdir, uploaded.name)
        with open(path, 'wb') as f:
            f.write(uploaded.read())
        parsed = parse_resume(path, force_ocr=st.session_state.use_ocr)
        st.session_state.parsed_resume = parsed

    # Initialize Gemini service if configured
    if use_gemini and gemini_api_key:
        gemini_service = get_gemini_service(gemini_api_key)
        if gemini_service:
            st.sidebar.success("🤖 Gemini AI activated")
            st.session_state.gemini_service = gemini_service
        else:
            st.sidebar.error("❌ Failed to initialize Gemini")
            st.session_state.gemini_service = None
    else:
        st.session_state.gemini_service = None

    st.subheader("📄 Extracted Text (Preview)")
    st.caption(f"OCR Used: {parsed.ocr_used} | Characters: {parsed.meta['char_len']}")
    with st.expander("View Full Text", expanded=False):
        st.text_area("Resume Text", parsed.text, height=300)

    # Embeddings + Vector store
    with st.spinner("🔗 Creating embeddings & vector store..."):
        store = create_vector_store(parsed.text)
        st.session_state.vector_store = store

# Display sections with data persistence
current_section = st.session_state.current_section

# Show welcome message if no resume is uploaded
if not st.session_state.parsed_resume:
    # Force CSS reapplication with inline styles as fallback
    st.markdown("""
    <style>
    /* Ensure welcome styles are applied */
    .welcome-hero {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
        color: #ffffff !important;
        padding: 3rem 2rem !important;
        margin-bottom: 2rem !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15) !important;
        text-align: center !important;
    }
    .welcome-hero h1 {
        color: #ffffff !important;
        font-size: 2.6rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.75rem 0 !important;
        letter-spacing: -0.5px !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
    }
    .welcome-hero p.lead {
        color: rgba(255,255,255,0.92) !important;
        font-size: 1.15rem !important;
        margin: 0 0 2rem 0 !important;
        font-weight: 400 !important;
        max-width: 720px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        line-height: 1.65 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2) !important;
    }
    .welcome-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)) !important;
        gap: 1.5rem !important;
        max-width: 1000px !important;
        margin: 0 auto !important;
    }
    .welcome-card {
        background: rgba(255,255,255,0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
        text-align: left !important;
    }
    .welcome-card:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 30px rgba(0,0,0,0.18) !important;
        border-color: rgba(255,255,255,0.35) !important;
    }
    .welcome-icon {
        width: 70px !important;
        height: 70px !important;
        border-radius: 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 0 1.25rem 0 !important;
        font-size: 2rem !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    .icon-blue { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%) !important; }
    .icon-red { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important; }
    .icon-purple { background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%) !important; }
    .welcome-card h3 {
        color: #ffffff !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        margin: 0 0 0.5rem 0 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2) !important;
    }
    .welcome-card p {
        color: rgba(255,255,255,0.88) !important;
        font-size: 0.98rem !important;
        margin: 0 !important;
        line-height: 1.6 !important;
    }
    .welcome-cta {
        margin-top: 2.5rem !important;
        padding-top: 2rem !important;
        border-top: 1px solid rgba(255,255,255,0.2) !important;
        color: rgba(255,255,255,0.85) !important;
        font-size: 1rem !important;
        font-style: italic !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Enhanced Dashboard Header with improved UI
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
        padding: 3rem 2rem; 
        border-radius: 20px; 
        margin-bottom: 2.5rem; 
        color: white; 
        text-align: center;
        box-shadow: 0 15px 35px rgba(30, 60, 114, 0.3);
        position: relative;
        overflow: hidden;
    ">
        <div style="position: absolute; top: -50%; right: -10%; width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%; opacity: 0.6;"></div>
        <div style="position: absolute; bottom: -30%; left: -5%; width: 80px; height: 80px; background: rgba(255,255,255,0.08); border-radius: 50%;"></div>
        <h1 style="margin: 0; font-size: 3rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); letter-spacing: 1px;">
            🚀 Resume Optimization Hub
        </h1>
        <p style="margin: 1.5rem 0 0 0; font-size: 1.3rem; opacity: 0.95; font-weight: 400; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
            Transform your career with AI-powered resume enhancement
        </p>
        <div style="margin-top: 1.5rem; width: 100px; height: 3px; background: rgba(255,255,255,0.4); margin-left: auto; margin-right: auto; border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Stats Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f0f0f 0%, #1e3c72 100%); padding: 1.5rem; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 0 12px rgba(52, 152, 219, 0.3); 
                    border-left: 4px solid #3498db;">
            <h3 style="color: #3498db; margin: 0; font-size: 2rem;">🎯</h3>
            <p style="margin: 0.5rem 0 0 0; color: #ecf0f1; font-weight: 600;">ATS Optimization</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f0f0f 0%, #1e3c72 100%); padding: 1.5rem; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 0 12px rgba(231, 76, 60, 0.3); 
                    border-left: 4px solid #e74c3c;">
            <h3 style="color: #e74c3c; margin: 0; font-size: 2rem;">⚡</h3>
            <p style="margin: 0.5rem 0 0 0; color: #ecf0f1; font-weight: 600;">Skills Analysis</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f0f0f 0%, #1e3c72 100%); padding: 1.5rem; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 0 12px rgba(243, 156, 18, 0.3); 
                    border-left: 4px solid #f39c12;">
            <h3 style="color: #f39c12; margin: 0; font-size: 2rem;">💡</h3>
            <p style="margin: 0.5rem 0 0 0; color: #ecf0f1; font-weight: 600;">AI Enhancement</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f0f0f 0%, #1e3c72 100%); padding: 1.5rem; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 0 12px rgba(39, 174, 96, 0.3); 
                    border-left: 4px solid #27ae60;">
            <h3 style="color: #27ae60; margin: 0; font-size: 2rem;">🤝</h3>
            <p style="margin: 0.5rem 0 0 0; color: #ecf0f1; font-weight: 600;">Interview Prep</p>
        </div>
        """, unsafe_allow_html=True)

    
    # Getting Started Section
    st.markdown("---")
    st.markdown("### 🚀 Getting Started")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f0f0f 0%, #1e1e2f 100%); 
                    padding: 1.5rem; border-radius: 12px; 
                    border-left: 4px solid #667eea; 
                    box-shadow: 0 0 12px rgba(102,126,234,0.3);">
            <h4 style="color: #ecf0f1; margin-top: 0;">📋 Quick Start Guide</h4>
            <ol style="color: #bdc3c7; line-height: 1.8; text-align: left; padding-left: 1.2rem;">
                <li><strong style="color:#ffffff;">Upload your resume</strong> - Use the sidebar to upload your current resume (PDF or Word format)</li>
                <li><strong style="color:#ffffff;">Add job description</strong> - Paste the target job description for analysis</li>
                <li><strong style="color:#ffffff;">Get instant analysis</strong> - View ATS score, skill matching, and improvement suggestions</li>
                <li><strong style="color:#ffffff;">Enhance your resume</strong> - Use AI-powered tools to optimize content and keywords</li>
                <li><strong style="color:#ffffff;">Practice interviews</strong> - Generate personalized interview questions and answers</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                    padding: 1.5rem; border-radius: 12px; 
                    text-align: center; color: white; 
                    box-shadow: 0 0 12px rgba(118,75,162,0.3);">
            <h4 style="margin-top: 0;">📊 Your Progress</h4>
            <div style="margin: 1rem 0;">
                <div style="background: rgba(255,255,255,0.1); 
                            padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
                    <span style="font-weight: 600;">Resume Uploaded:</span><br>
                    <span style="color: #ffed4e;">{"✅ Complete" if st.session_state.get('parsed_resume') is not None else "⏳ Pending"}</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); 
                            padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
                    <span style="font-weight: 600;">Job Description:</span><br>
                    <span style="color: #ffed4e;">{"✅ Added" if st.session_state.get('job_description', '').strip() else "⏳ Pending"}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# Display analysis if data is available
elif current_section == "Resume Analysis":
    parsed = st.session_state.parsed_resume
    
    # Single container for the entire analysis section
    with st.container():
        st.markdown('<div class="section-header">📊 Resume Analysis Dashboard</div>', unsafe_allow_html=True)
    
    if st.session_state.job_description.strip():
        # Check if we need to recompute analysis (only if JD changed or not cached)
        current_jd_hash = hash(st.session_state.job_description.strip())
        analysis = None
        ats = None
        suggs = None
        
        if (not st.session_state.ats_results or 
            getattr(st.session_state, 'last_jd_hash', None) != current_jd_hash):
            
            with st.spinner("🔍 Analyzing resume against job description..."):
                try:
                    # Traditional analysis
                    analysis = analyze_skills(parsed.text, st.session_state.job_description)
                    ats = compute_ats_score(parsed.text, st.session_state.job_description)
                    suggs = improvement_suggestions(parsed.text, analysis)
                    
                    # Cache results
                    st.session_state.skill_analysis = analysis
                    st.session_state.ats_results = ats
                    st.session_state.improvement_suggestions = suggs
                    st.session_state.last_jd_hash = current_jd_hash
                    
                    st.success("✅ Analysis completed successfully!")
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.info("💡 Please check your inputs and try again")
        else:
            # Use cached results
            analysis = st.session_state.skill_analysis
            ats = st.session_state.ats_results
            suggs = st.session_state.improvement_suggestions
        
        if ats and analysis:
            # Enhanced metrics display with better layout
            st.markdown("### 📈 Performance Dashboard")
            
            # Main metrics row with improved styling
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                ats_color = "normal" if ats.score >= 70 else "inverse"
                st.metric("🎯 ATS Score", f"{ats.score}/100", 
                         delta=f"{ats.score-70:.1f} vs baseline", 
                         delta_color=ats_color)
            with col2:
                total_skills = len(ats.matched_skills) + len(ats.missing_skills)
                if total_skills > 0:
                    match_ratio = len(ats.matched_skills) / total_skills
                    st.metric("🔗 Skills Match", f"{len(ats.matched_skills)}/{total_skills}",
                             delta=f"{match_ratio:.1%} match rate")
                else:
                    st.metric("🔗 Skills Match", "0/0", delta="No skills detected")
            with col3:
                coverage_pct = analysis.matched_ratio * 100 if analysis and hasattr(analysis, 'matched_ratio') else 0
                st.metric("📈 Coverage", f"{coverage_pct:.1f}%",
                         delta=f"{coverage_pct-50:.1f}% vs average")
            with col4:
                resume_length = len(parsed.text.split())
                length_status = "Good" if 300 <= resume_length <= 800 else ("Too short" if resume_length < 300 else "Too long")
                st.metric("📝 Resume Length", f"{resume_length} words", delta=length_status)
            
            # Create visual charts if plotly is available
            try:
                # Skills comparison chart
                st.markdown("### 🔍 Skills Analysis")
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    # ATS Score Gauge
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = ats.score,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "ATS Score", 'font': {'size': 20}},
                        delta = {'reference': 70, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                        gauge = {
                            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                            'bar': {'color': "#3498db"},
                            'bgcolor': "white",
                            'borderwidth': 2,
                            'bordercolor': "#e9ecef",
                            'steps': [
                                {'range': [0, 50], 'color': '#ffebee'},
                                {'range': [50, 70], 'color': '#fff3e0'},
                                {'range': [70, 85], 'color': '#e8f5e8'},
                                {'range': [85, 100], 'color': '#e3f2fd'}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_gauge, use_container_width=True)
                
                with col_chart2:
                    # Skills pie chart
                    total_skills = len(ats.matched_skills) + len(ats.missing_skills)
                    if total_skills > 0:
                        skills_data = pd.DataFrame({
                            'Category': ['Matched Skills', 'Missing Skills'],
                            'Count': [len(ats.matched_skills), len(ats.missing_skills)]
                        })
                        
                        fig_skills = px.pie(
                            skills_data,
                            values='Count',
                            names='Category',
                            title="Skills Distribution",
                            color_discrete_sequence=['#2ecc71', '#e74c3c']
                        )
                        fig_skills.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                        fig_skills.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig_skills, use_container_width=True)
                    else:
                        st.info("No skills data available for visualization")
                
            except Exception as chart_error:
                st.warning(f"Charts not available: {chart_error}")
        else:
            st.error("❌ Failed to generate analysis results. Please ensure both resume and job description are provided.")
        
        # Enhanced analysis with Gemini (only if not already cached)
        if st.session_state.gemini_service and ats and analysis:
            if not st.session_state.analysis_results or getattr(st.session_state, 'last_ai_jd_hash', None) != current_jd_hash:
                with st.spinner("🤖 Generating AI-powered analysis..."):
                    try:
                        gemini_analysis = analyze_resume_with_gemini(st.session_state.gemini_service, parsed.text, st.session_state.job_description, st.session_state.selected_role)
                        st.session_state.analysis_results = gemini_analysis
                        st.session_state.last_ai_jd_hash = current_jd_hash
                    except Exception as e:
                        st.error(f"❌ AI Analysis failed: {str(e)}")
            
            if st.session_state.analysis_results:
                st.markdown("### 🤖 AI-Enhanced Analysis")
                st.markdown(st.session_state.analysis_results['analysis'])
        
        # Traditional analysis results
        if ats and analysis:
            with st.expander("📈 Detailed Analysis Results", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**✅ Matched Skills:**")
                    if ats.matched_skills:
                        for skill in sorted(ats.matched_skills):
                            st.markdown(f"• {skill}")
                    else:
                        st.write("None detected")
                
                with col_b:
                    st.write("**❌ Missing Skills:**")
                    if ats.missing_skills:
                        for skill in sorted(ats.missing_skills):
                            st.markdown(f"• {skill}")
                    else:
                        st.write("None detected")
                
                st.subheader("💡 Improvement Suggestions")
                if suggs:
                    for i, sug in enumerate(suggs, 1):
                        st.markdown(f"{i}. {sug}")
                else:
                    st.write("No specific suggestions available.")
    else:
        st.info("📝 Paste a Job Description in the sidebar to run comprehensive analysis.")
        
        # Show basic resume info even without JD
        if parsed:
            st.subheader("📄 Resume Information")
            info_cols = st.columns(3)
            with info_cols[0]:
                st.metric("📝 Characters", parsed.meta['char_len'])
            with info_cols[1]:
                st.metric("� OCR Used", "Yes" if parsed.ocr_used else "No")
            with info_cols[2]:
                st.metric("📁 File Type", parsed.meta['extension'].upper())
    


elif current_section == "Resume Q&A":
    if not st.session_state.parsed_resume:
        st.markdown('<div class="section-header">❓ Resume Q&A</div>', unsafe_allow_html=True)
        st.warning("📄 Please upload and analyze a resume first to access Q&A generation.")
    else:
        parsed = st.session_state.parsed_resume
        
        st.markdown('<div class="section-header">❓ Resume Q&A</div>', unsafe_allow_html=True)
        
        qa_topic = st.selectbox("Select Q&A Topic", [
            "Technical Skills", "Leadership Experience", "Project Management", 
            "Problem Solving", "Career Goals", "Custom Topic"
        ], key="qa_topic_select")
        
        if qa_topic == "Custom Topic":
            qa_topic = st.text_input("Enter custom topic:", key="custom_qa_topic")
        
        # Show cached results if available
        if st.session_state.qa_results and getattr(st.session_state, 'last_qa_topic', None) == qa_topic:
            st.markdown("### 🗣️ Generated Q&A (Cached)")
            st.markdown(st.session_state.qa_results['qa_content'])
            st.info("💡 Results cached from previous generation. Click 'Generate Q&A' to refresh.")
        
        if st.button("🎯 Generate Q&A", key="generate_qa_btn") and qa_topic:
            if st.session_state.gemini_service:
                with st.spinner("🤖 Generating Q&A with Gemini..."):
                    try:
                        qa_results = generate_qa_with_gemini(st.session_state.gemini_service, parsed.text, qa_topic)
                        st.session_state.qa_results = qa_results
                        st.session_state.last_qa_topic = qa_topic
                        st.markdown("### 🗣️ Generated Q&A")
                        st.markdown(qa_results['qa_content'])
                    except Exception as e:
                        st.error(f"❌ Failed to generate Q&A: {str(e)}")
                        st.info("💡 Check your Gemini API key and try again")
            else:
                st.info("💡 Enable Gemini AI for enhanced Q&A generation")
                st.markdown("**Available with Gemini AI:**")
                st.markdown("- Topic-specific questions and answers")
                st.markdown("- Contextual content based on your resume")
                st.markdown("- Professional interview preparation")
                st.markdown("- Custom topic exploration")
        
        

elif current_section == "Interview Questions":
    if not st.session_state.parsed_resume:
        st.markdown('<div class="section-header">🎤 Interview Questions</div>', unsafe_allow_html=True)
        st.warning("📄 Please upload and analyze a resume first to access interview question generation.")
    else:
        parsed = st.session_state.parsed_resume
        
        st.markdown('<div class="section-header">🎤 Interview Questions</div>', unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            num_questions = st.slider("Number of Questions", 3, 10, 5, key="num_questions_slider")
        with col_b:
            question_type = st.selectbox("Question Focus", [
                "Behavioral", "Technical", "Mixed", "Role-Specific"
            ], key="question_type_select")
        
        # Show cached results if available
        cached_key = f"{num_questions}_{question_type}_{hash(st.session_state.job_description.strip()) if st.session_state.job_description.strip() else 'no_jd'}"
        if (st.session_state.interview_questions and 
            getattr(st.session_state, 'last_interview_key', None) == cached_key):
            
            st.markdown("### 🎯 Generated Interview Questions (Cached)")
            questions = st.session_state.interview_questions
            for i, q_data in enumerate(questions, 1):
                with st.expander(f"Question {i}: {q_data.get('question', 'Question')[:80]}...", expanded=i<=2):
                    st.markdown(f"**❓ Question:** {q_data.get('question', 'N/A')}")
                    st.markdown(f"**💡 Sample Answer:** {q_data.get('sample_answer', 'N/A')}")
                    st.markdown(f"**🔍 What they're looking for:** {q_data.get('looking_for', 'N/A')}")
            st.info("💡 Results cached from previous generation. Click 'Generate Questions' to refresh.")
        
        if st.button("🎯 Generate Interview Questions", key="generate_interview_btn"):
            if st.session_state.gemini_service:
                if not st.session_state.job_description.strip():
                    st.warning("📝 Please provide a Job Description for better interview questions")
                else:
                    with st.spinner("🤖 Generating interview questions with Gemini..."):
                        try:
                            questions = generate_interview_questions_gemini(
                                st.session_state.gemini_service, parsed.text, st.session_state.job_description, st.session_state.selected_role, num_questions
                            )
                            st.session_state.interview_questions = questions
                            st.session_state.last_interview_key = cached_key
                            
                            st.markdown("### 🎯 AI-Generated Interview Questions")
                            for i, q_data in enumerate(questions, 1):
                                with st.expander(f"Question {i}: {q_data['question'][:80]}...", expanded=i<=2):
                                    st.markdown(f"**❓ Question:** {q_data['question']}")
                                    st.markdown(f"**💡 Sample Answer:** {q_data['sample_answer']}")
                                    st.markdown(f"**🔍 What they're looking for:** {q_data['looking_for']}")
                        except Exception as e:
                            st.error(f"❌ Failed to generate interview questions: {str(e)}")
                            st.info("💡 Try again or check your Gemini API key")
            else:
                # Show message about enabling Gemini for better functionality
                st.info("🤖 Enable Gemini AI for advanced interview question generation")
                st.markdown("""
                **With Gemini AI enabled, you'll get:**
                - Personalized interview questions based on your resume
                - Context-aware sample answers
                - Insights into what interviewers are looking for
                - Role-specific question types (Behavioral, Technical, etc.)
                
                **To enable:** Add your Gemini API key in the sidebar configuration.
                """)
                
                # Fallback to simpler traditional method only if vector store exists
                if st.session_state.vector_store:
                    st.markdown("---")
                    st.markdown("**🔄 Basic Interview Questions (Traditional Method)**")
                    if st.button("Generate Basic Questions", key="basic_interview_btn"):
                        with st.spinner("🔄 Generating basic questions..."):
                            try:
                                questions = generate_interview_questions(st.session_state.vector_store, num_questions)
                                answers = generate_sample_answers(st.session_state.vector_store, questions)
                                
                                # Convert to standard format
                                formatted_questions = []
                                for q, a in zip(questions, answers):
                                    formatted_questions.append({
                                        'question': q,
                                        'sample_answer': a,
                                        'looking_for': 'General interview skills and experience-based responses'
                                    })
                                
                                st.session_state.interview_questions = formatted_questions
                                st.session_state.last_interview_key = cached_key
                                
                                st.subheader("📝 Generated Interview Questions")
                                for i, q_data in enumerate(formatted_questions, 1):
                                    with st.expander(f"Question {i}", expanded=i<=2):
                                        st.markdown(f"**❓ {q_data['question']}**")
                                        st.markdown(f"**💡 Sample Answer:** {q_data['sample_answer']}")
                            except Exception as e:
                                st.error(f"❌ Traditional generation failed: {str(e)}")
                                st.info("💡 This might be due to missing dependencies. Try enabling Gemini AI for better results.")
                else:
                    st.warning("📄 Please upload and analyze a resume first to generate questions.")


elif current_section == "Resume Improvement":
    if not st.session_state.parsed_resume:
        st.markdown('<div class="section-header">✨ Resume Improvement</div>', unsafe_allow_html=True)
        st.warning("📄 Please upload and analyze a resume first to access resume improvement.")
    else:
        parsed = st.session_state.parsed_resume
        
        st.markdown('<div class="section-header">✨ Resume Improvement</div>', unsafe_allow_html=True)
        
        improvement_focus = st.multiselect("Improvement Focus Areas", [
            "Professional Summary", "Skills Section", "Achievement Quantification",
            "ATS Optimization", "Action Verbs", "Industry Keywords"
        ], default=["Professional Summary", "ATS Optimization"], key="improvement_focus_select")
        
        # Show cached results if available
        cached_key = f"{str(improvement_focus)}_{hash(st.session_state.job_description.strip()) if st.session_state.job_description.strip() else 'no_jd'}"
        if (st.session_state.improved_resume and 
            getattr(st.session_state, 'last_improvement_key', None) == cached_key):
            
            st.markdown("### ✨ Resume Improvement Results (Cached)")
            improved_content = st.session_state.improved_resume
            
            tab1, tab2 = st.tabs(["📄 Improved Resume", "📥 Download Options"])
            
            with tab1:
                with st.expander("📄 Preview Improved Resume", expanded=True):
                    st.markdown(improved_content)
            
            with tab2:
                st.markdown("#### 📥 Download Improved Resume")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📄 Generate DOCX", key="cached_docx_btn"):
                        try:
                            docx_buf = generate_docx(improved_content)
                            st.download_button(
                                "⬇️ Download DOCX",
                                data=docx_buf,
                                file_name="resume_improved_ai.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="cached_download_docx"
                            )
                        except Exception as e:
                            st.error(f"❌ DOCX export failed: {e}")
                
                with col2:
                    if st.button("📑 Generate PDF", key="cached_pdf_btn"):
                        try:
                            pdf_buf = generate_pdf(improved_content)
                            st.download_button(
                                "⬇️ Download PDF",
                                data=pdf_buf,
                                file_name="resume_improved_ai.pdf",
                                mime="application/pdf",
                                key="cached_download_pdf"
                            )
                        except Exception as e:
                            st.error(f"❌ PDF export failed: {e}")
            
            st.info("💡 Results cached from previous generation. Click 'Generate Improved Resume' to refresh.")
        
        if st.button("🚀 Generate Improved Resume", key="generate_improved_btn"):
            if st.session_state.gemini_service:
                with st.spinner("🤖 Creating improved resume with Gemini..."):
                    try:
                        analysis_data = st.session_state.analysis_results or {}
                        improved_content = improve_resume_with_gemini(
                            st.session_state.gemini_service, parsed.text, analysis_data, st.session_state.selected_role
                        )
                        st.session_state.improved_resume = improved_content
                        st.session_state.last_improvement_key = cached_key
                        
                        st.markdown("### ✨ AI-Improved Resume")
                        tab1, tab2 = st.tabs(["📄 Improved Resume", "📥 Download Options"])
                        
                        with tab1:
                            with st.expander("📄 Preview Improved Resume", expanded=True):
                                st.markdown(improved_content)
                        
                        with tab2:
                            st.markdown("#### 📥 Download Improved Resume")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("📄 Generate DOCX", key="generate_docx_btn"):
                                    try:
                                        docx_buf = generate_docx(improved_content)
                                        st.download_button(
                                            "⬇️ Download DOCX",
                                            data=docx_buf,
                                            file_name="resume_improved_ai.docx",
                                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                            key="download_docx"
                                        )
                                    except Exception as e:
                                        st.error(f"❌ DOCX export failed: {e}")
                            
                            with col2:
                                if st.button("📑 Generate PDF", key="generate_pdf_btn"):
                                    try:
                                        pdf_buf = generate_pdf(improved_content)
                                        st.download_button(
                                            "⬇️ Download PDF",
                                            data=pdf_buf,
                                            file_name="resume_improved_ai.pdf",
                                            mime="application/pdf",
                                            key="download_pdf"
                                        )
                                    except Exception as e:
                                        st.error(f"❌ PDF export failed: {e}")
                    except Exception as e:
                        st.error(f"❌ Failed to improve resume: {str(e)}")
                        st.info("💡 Check your Gemini API key and try again")
            else:
                st.info("🤖 Enable Gemini AI for advanced resume improvement")
                st.markdown("""
                **With Gemini AI enabled, you'll get:**
                - Professional summary enhancement
                - Stronger action verbs and quantified achievements
                - ATS optimization with relevant keywords
                - Better content organization and flow
                - Industry-specific improvements
                
                **To enable:** Add your Gemini API key in the sidebar configuration.
                """)
                
                # Fallback to traditional improvement
                if st.session_state.job_description.strip():
                    st.markdown("---")
                    st.markdown("**🔄 Basic Resume Improvement (Traditional Method)**")
                    if st.button("Generate Basic Improvement", key="basic_improve_btn"):
                        with st.spinner("🔄 Creating improved resume (traditional method)..."):
                            try:
                                analysis = analyze_skills(parsed.text, st.session_state.job_description)
                                suggs = improvement_suggestions(parsed.text, analysis)
                                improved_text = build_improved_resume_text(
                                    resume_text=parsed.text,
                                    suggestions=suggs,
                                    strengths=analysis.strengths,
                                    gaps=analysis.gaps,
                                    role=st.session_state.selected_role
                                )
                                st.session_state.improved_resume = improved_text
                                st.session_state.last_improvement_key = cached_key
                                
                                st.markdown("### 📝 Traditional Improvement")
                                with st.expander("Preview Basic Improved Resume", expanded=True):
                                    st.text_area("Improved Resume", improved_text, height=400, key="traditional_improved_resume")
                            except Exception as e:
                                st.error(f"❌ Traditional improvement failed: {str(e)}")
                                st.info("💡 Try enabling Gemini AI for better results.")
                else:
                    st.warning("📝 Provide a Job Description for resume improvement")
        

elif current_section == "Improved Resume":
    if not st.session_state.parsed_resume:
        st.markdown('<div class="section-header">📋 Improved Resume Summary</div>', unsafe_allow_html=True)
        st.warning("📄 Please upload and analyze a resume first to view the summary.")
    else:
        st.markdown('<div class="section-header">📋 Improved Resume Summary</div>', unsafe_allow_html=True)
    
    if st.session_state.analysis_results:
        st.success("✅ Analysis completed with AI enhancement")
    
    # Status overview with enhanced styling
    st.markdown("### 📊 Processing Status")
    summary_cols = st.columns(4)
    with summary_cols[0]:
        status = "✅ Ready" if st.session_state.parsed_resume else "❌ Missing"
        st.metric("📄 Resume", status)
    with summary_cols[1]:
        status = "✅ Complete" if st.session_state.analysis_results else "❌ Pending"
        st.metric("🤖 AI Analysis", status)
    with summary_cols[2]:
        status = "✅ Provided" if st.session_state.job_description.strip() else "❌ Missing"
        st.metric("🎯 Job Description", status)
    with summary_cols[3]:
        status = "✅ Ready" if st.session_state.vector_store else "❌ Missing"
        st.metric("🔗 Vector Store", status)
    
    # Progress indicator
    completed_features = sum([
        bool(st.session_state.parsed_resume),
        bool(st.session_state.analysis_results),
        bool(st.session_state.qa_results),
        bool(st.session_state.interview_questions),
        bool(st.session_state.improved_resume)
    ])
    total_features = 5
    progress = completed_features / total_features
    
    st.markdown("### 🎯 Feature Completion")
    st.progress(progress)
    st.caption(f"Completed: {completed_features}/{total_features} features")
    
    # Quick actions with enhanced styling
    st.markdown("### 🚀 Quick Actions")
    action_cols = st.columns(3)
    with action_cols[0]:
        if st.button("🔄 Re-analyze with Different JD", key="reanalyze_btn", use_container_width=True):
            st.session_state.current_section = "Resume Analysis"
            st.rerun()
    with action_cols[1]:
        if st.button("📊 View Detailed Analytics", key="analytics_btn", use_container_width=True):
            if st.session_state.analysis_results:
                with st.expander("📈 Analysis Results", expanded=True):
                    st.json(st.session_state.analysis_results)
            else:
                st.warning("No analysis results available")
    with action_cols[2]:
        if st.button("💾 Clear All Data", key="clear_data_btn", use_container_width=True, type="secondary"):
            for key in ['parsed_resume', 'vector_store', 'analysis_results', 'qa_results', 
                       'interview_questions', 'improved_resume']:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("All data cleared successfully!")
            st.rerun()
    
    # Feature summary cards
    if st.session_state.analysis_results or st.session_state.qa_results or st.session_state.interview_questions:
        st.markdown("### 📋 Generated Content Summary")
        
        summary_cards = st.columns(3)
        
        with summary_cards[0]:
            if st.session_state.analysis_results:
                st.markdown("""
                <div class='summary-card' style='
                    padding: 1.5rem; 
                    border: 2px solid #4CAF50; 
                    border-radius: 12px; 
                    background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 50%, #A5D6A7 100%);
                    box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
                    margin-bottom: 1rem;
                '>
                    <h4 style='color: #2E7D32; margin-bottom: 1rem; font-weight: bold;'>📊 Analysis Results</h4>
                    <p style='color: #1B5E20; margin: 0.5rem 0; font-weight: 500;'>✅ ATS Score Available</p>
                    <p style='color: #1B5E20; margin: 0.5rem 0; font-weight: 500;'>✅ Skills Analysis Complete</p>
                    <p style='color: #1B5E20; margin: 0.5rem 0; font-weight: 500;'>✅ Improvement Suggestions Ready</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='summary-card' style='
                    padding: 1.5rem; 
                    border: 2px solid #FF9800; 
                    border-radius: 12px; 
                    background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 50%, #FFCC80 100%);
                    box-shadow: 0 4px 8px rgba(255, 152, 0, 0.2);
                    margin-bottom: 1rem;
                '>
                    <h4 style='color: #E65100; margin-bottom: 1rem; font-weight: bold;'>📊 Analysis Pending</h4>
                    <p style='color: #BF360C; margin: 0.5rem 0; font-weight: 500;'>⏳ Analysis not yet performed</p>
                </div>
                """, unsafe_allow_html=True)
        
        with summary_cards[1]:
            if st.session_state.qa_results:
                qa_count = len(st.session_state.qa_results)
                st.markdown(f"""
                <div class='summary-card' style='
                    padding: 1.5rem; 
                    border: 2px solid #2196F3; 
                    border-radius: 12px; 
                    background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 50%, #90CAF9 100%);
                    box-shadow: 0 4px 8px rgba(33, 150, 243, 0.2);
                    margin-bottom: 1rem;
                '>
                    <h4 style='color: #0D47A1; margin-bottom: 1rem; font-weight: bold;'>❓ Q&A Generated</h4>
                    <p style='color: #1565C0; margin: 0.5rem 0; font-weight: 500;'>✅ {qa_count} Questions Available</p>
                    <p style='color: #1565C0; margin: 0.5rem 0; font-weight: 500;'>✅ Context-aware Answers</p>
                    <p style='color: #1565C0; margin: 0.5rem 0; font-weight: 500;'>✅ Interview Ready</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='summary-card' style='
                    padding: 1.5rem; 
                    border: 2px solid #FF9800; 
                    border-radius: 12px; 
                    background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 50%, #FFCC80 100%);
                    box-shadow: 0 4px 8px rgba(255, 152, 0, 0.2);
                    margin-bottom: 1rem;
                '>
                    <h4 style='color: #E65100; margin-bottom: 1rem; font-weight: bold;'>❓ Q&A Pending</h4>
                    <p style='color: #BF360C; margin: 0.5rem 0; font-weight: 500;'>⏳ Q&A not yet generated</p>
                </div>
                """, unsafe_allow_html=True)
        
        with summary_cards[2]:
            if st.session_state.interview_questions:
                q_count = len(st.session_state.interview_questions)
                st.markdown(f"""
                <div class='summary-card' style='
                    padding: 1.5rem; 
                    border: 2px solid #9C27B0; 
                    border-radius: 12px; 
                    background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 50%, #CE93D8 100%);
                    box-shadow: 0 4px 8px rgba(156, 39, 176, 0.2);
                    margin-bottom: 1rem;
                '>
                    <h4 style='color: #4A148C; margin-bottom: 1rem; font-weight: bold;'>🎤 Interview Questions</h4>
                    <p style='color: #6A1B9A; margin: 0.5rem 0; font-weight: 500;'>✅ {q_count} Questions Ready</p>
                    <p style='color: #6A1B9A; margin: 0.5rem 0; font-weight: 500;'>✅ Sample Answers Provided</p>
                    <p style='color: #6A1B9A; margin: 0.5rem 0; font-weight: 500;'>✅ Interview Tips Included</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                    st.markdown("""
                    <div class='summary-card' style='
                        padding: 1.5rem; 
                        border: 2px solid #FF9800; 
                        border-radius: 12px; 
                        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 50%, #FFCC80 100%);
                        box-shadow: 0 4px 8px rgba(255, 152, 0, 0.2);
                        margin-bottom: 1rem;
                    '>
                        <h4 style='color: #E65100; margin-bottom: 1rem; font-weight: bold;'>🎤 Questions Pending</h4>
                        <p style='color: #BF360C; margin: 0.5rem 0; font-weight: 500;'>⏳ Interview questions not yet generated</p>
                    </div>
                    """, unsafe_allow_html=True)
        
