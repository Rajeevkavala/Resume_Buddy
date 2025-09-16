"""
Resume Summary Module
Handles the summary dashboard and overview functionality.
"""

import streamlit as st
from modules.session_utils import clear_all_data as _clear_all_data


def show_toast(message, toast_type="info"):
    """Display a toast message with different types."""
    if toast_type == "success":
        icon = "✅"
        color = "#28a745"
    elif toast_type == "error":
        icon = "❌"
        color = "#dc3545"
    elif toast_type == "warning":
        icon = "⚠️"
        color = "#ffc107"
    else:  # info
        icon = "ℹ️"
        color = "#17a2b8"
    
    st.markdown(
        f"""
        <div class="toast" style="background-color: {color};">
            <span class="toast-icon">{icon}</span>
            <span class="toast-message">{message}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_summary_section():
    """Render the improved resume summary section."""
    if not st.session_state.parsed_resume:
        st.markdown('<div class="section-header">📋 Improved Resume Summary</div>', unsafe_allow_html=True)
        st.warning("📄 Please upload and analyze a resume first to view the summary.")
        return
        
    st.markdown('<div class="section-header">📋 Improved Resume Summary</div>', unsafe_allow_html=True)
    
    if st.session_state.analysis_results:
        st.success("✅ Analysis completed with AI enhancement")
    
    # Status overview with enhanced styling
    display_processing_status()
    
    # Progress indicator
    display_progress_indicator()
    
    # Quick actions
    display_quick_actions()
    
    # Feature summary cards
    display_feature_summary()


def display_processing_status():
    """Display processing status overview."""
    st.markdown("### 📊 Processing Status")
    summary_cols = st.columns(4)
    
    with summary_cols[0]:
        status = "✅ Ready" if st.session_state.parsed_resume else "❌ Missing"
        st.metric("📄 Resume", status)
    
    with summary_cols[1]:
        status = "✅ Complete" if st.session_state.get('analysis_completed', False) else "❌ Pending"
        st.metric("🤖 AI Analysis", status)
    
    with summary_cols[2]:
        status = "✅ Provided" if st.session_state.job_description.strip() else "❌ Missing"
        st.metric("🎯 Job Description", status)
    
    with summary_cols[3]:
        status = "✅ Ready" if st.session_state.vector_store else "❌ Missing"
        st.metric("🔗 Vector Store", status)


def display_progress_indicator():
    """Display feature completion progress."""
    completed_features = sum([
        bool(st.session_state.parsed_resume),
        bool(st.session_state.get('analysis_completed', False)),
        bool(st.session_state.get('qa_completed', False)),
        bool(st.session_state.get('interview_completed', False)),
        bool(st.session_state.get('improvement_completed', False))
    ])
    total_features = 5
    progress = completed_features / total_features
    
    st.markdown("### 🎯 Feature Completion")
    st.progress(progress)
    st.caption(f"Completed: {completed_features}/{total_features} features")


def display_quick_actions():
    """Display quick action buttons."""
    st.markdown("### 🚀 Quick Actions")
    action_cols = st.columns(3)
    
    with action_cols[0]:
        if st.button("🔄 Re-analyze with Different JD", key="reanalyze_btn", use_container_width=True):
            st.session_state.current_section = "Resume Analysis"
            show_toast("📊 Redirecting to Resume Analysis...", "info")
            st.rerun()
    
    with action_cols[1]:
        if st.button("📊 View Detailed Analytics", key="analytics_btn", use_container_width=True):
            display_detailed_analytics()
            show_toast("📈 Loading detailed analytics...", "info")
    
    with action_cols[2]:
        if st.button("💾 Clear All Data", key="clear_data_btn", use_container_width=True, type="secondary"):
            _clear_all_data()
            show_toast("✅ All data cleared successfully!", "success")
            st.rerun()


def display_detailed_analytics():
    """Display detailed analytics if available."""
    if st.session_state.analysis_results:
        with st.expander("📈 Analysis Results", expanded=True):
            st.json(st.session_state.analysis_results)
    else:
        st.warning("No analysis results available")


def display_feature_summary():
    """Display feature summary cards."""
    if st.session_state.analysis_results or st.session_state.qa_results or st.session_state.interview_questions:
        st.markdown("### 📋 Generated Content Summary")
        
        summary_cards = st.columns(3)
        
        with summary_cards[0]:
            display_analysis_summary_card()
        
        with summary_cards[1]:
            display_qa_summary_card()
        
        with summary_cards[2]:
            display_interview_summary_card()


def display_analysis_summary_card():
    """Display analysis summary card."""
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


def display_qa_summary_card():
    """Display Q&A summary card."""
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


def display_interview_summary_card():
    """Display interview questions summary card."""
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


def display_export_options():
    """Display export options for all generated content."""
    st.markdown("### 📤 Export All Content")
    
    if st.button("📋 Generate Complete Report", key="complete_report_btn"):
        generate_complete_report()


def generate_complete_report():
    """Generate a complete report with all analysis and results."""
    report_content = "RESUME BUDDY - COMPLETE ANALYSIS REPORT\n"
    report_content += "=" * 60 + "\n\n"
    
    # Resume information
    if st.session_state.parsed_resume:
        report_content += "ORIGINAL RESUME:\n"
        report_content += "-" * 20 + "\n"
        report_content += st.session_state.parsed_resume.text[:500] + "...\n\n"
    
    # Analysis results
    if st.session_state.analysis_results:
        report_content += "ANALYSIS RESULTS:\n"
        report_content += "-" * 20 + "\n"
        report_content += str(st.session_state.analysis_results) + "\n\n"
    
    # Q&A results
    if st.session_state.qa_results:
        report_content += "QUESTION & ANSWERS:\n"
        report_content += "-" * 20 + "\n"
        for i, qa in enumerate(st.session_state.qa_results, 1):
            report_content += f"Q{i}: {qa.get('question', 'N/A')}\n"
            report_content += f"A{i}: {qa.get('answer', 'N/A')}\n\n"
    
    # Interview questions
    if st.session_state.interview_questions:
        report_content += "INTERVIEW QUESTIONS:\n"
        report_content += "-" * 20 + "\n"
        for i, q in enumerate(st.session_state.interview_questions, 1):
            report_content += f"{i}. {q.get('question', 'N/A')}\n"
    
    # Improved resume
    if st.session_state.improved_resume:
        report_content += "\n\nIMPROVED RESUME:\n"
        report_content += "-" * 20 + "\n"
        report_content += st.session_state.improved_resume + "\n"
    
    st.download_button(
        "📥 Download Complete Report",
        data=report_content,
        file_name="resume_buddy_complete_report.txt",
        mime="text/plain",
        key="download_complete_report"
    )
    
    st.success("Complete report generated successfully!")
