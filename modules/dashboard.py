"""
Dashboard Module
Handles the main dashboard and welcome screen.
"""

import streamlit as st


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


def render_dashboard():
    """Render the main dashboard/welcome screen."""
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
    display_feature_stats()
    
    # Getting Started Section
    display_getting_started()


def display_feature_stats():
    """Display feature statistics cards."""
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


def display_getting_started():
    """Display getting started section."""
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
        display_progress_widget()


def display_progress_widget():
    """Display progress widget showing current status."""
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
            <div style="background: rgba(255,255,255,0.1); 
                        padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
                <span style="font-weight: 600;">Analysis:</span><br>
                <span style="color: #ffed4e;">{"✅ Complete" if st.session_state.get('analysis_completed', False) else "⏳ Pending"}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_tips_and_features():
    """Display tips and features section."""
    st.markdown("---")
    st.markdown("### 💡 Features & Tips")
    
    # Feature highlights
    feature_cols = st.columns(3)
    
    with feature_cols[0]:
        st.markdown("""
        #### 📊 Smart Analysis
        • **ATS Score** - Check compatibility with Applicant Tracking Systems
        • **Skills Matching** - Compare your skills with job requirements
        • **Keyword Optimization** - Identify missing industry keywords
        • **Content Analysis** - Get detailed feedback on resume content
        """)
    
    with feature_cols[1]:
        st.markdown("""
        #### 🤖 AI Enhancement
        • **Gemini AI Integration** - Advanced resume analysis and improvement
        • **Smart Suggestions** - AI-powered improvement recommendations
        • **Content Generation** - Create compelling resume sections
        • **Interview Prep** - AI-generated questions and answers
        """)
    
    with feature_cols[2]:
        st.markdown("""
        #### 🎯 Career Tools
        • **Multiple Formats** - Export in PDF, DOCX, and TXT
        • **Practice Mode** - Interactive interview preparation
        • **Progress Tracking** - Monitor your improvement journey
        • **Comprehensive Reports** - Download complete analysis
        """)


def display_recent_activity():
    """Display recent activity if any."""
    if any([
        st.session_state.get('parsed_resume'),
        st.session_state.get('analysis_completed', False),
        st.session_state.get('qa_completed', False),
        st.session_state.get('interview_completed', False)
    ]):
        st.markdown("---")
        st.markdown("### 📈 Recent Activity")
        
        activities = []
        
        if st.session_state.get('parsed_resume'):
            activities.append("✅ Resume uploaded and parsed")
        
        if st.session_state.get('analysis_completed', False):
            activities.append("✅ AI analysis completed")
        
        if st.session_state.get('qa_completed', False):
            activities.append(f"✅ Q&A pairs generated")
        
        if st.session_state.get('interview_completed', False):
            activities.append(f"✅ Interview questions created")
        
        if st.session_state.get('improvement_completed', False):
            activities.append("✅ Resume improvement completed")
        
        for activity in activities:
            st.markdown(f"• {activity}")
        
        # Quick navigation buttons
        st.markdown("### 🔄 Quick Actions")
        nav_cols = st.columns(len(activities) if len(activities) <= 4 else 4)
        
        sections = ["Resume Analysis", "Resume Q&A", "Interview Questions", "Resume Improvement"]
        
        for i, section in enumerate(sections[:len(nav_cols)]):
            with nav_cols[i]:
                if st.button(f"Go to {section}", key=f"nav_{section.replace(' ', '_').lower()}", use_container_width=True):
                    st.session_state.current_section = section
                    st.rerun()
