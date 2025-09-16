"""
Resume Analysis Module
Handles all resume analysis functionality including ATS scoring and skill matching.
Enhanced with advanced analysis logic and improved UI.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time
from analysis import analyze_skills, compute_ats_score, improvement_suggestions
from gemini_integration import analyze_resume_with_gemini

def show_toast(message, type="info"):
    """Show a toast message."""
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)


def calculate_resume_quality_score(parsed_resume, ats_results, analysis):
    """Calculate comprehensive resume quality score."""
    quality_factors = {
        'length': 0,
        'structure': 0,
        'skills_match': 0,
        'keywords': 0,
        'readability': 0
    }
    
    # Length scoring (300-800 words optimal)
    word_count = len(parsed_resume.text.split())
    if 300 <= word_count <= 800:
        quality_factors['length'] = 20
    elif 200 <= word_count < 300 or 800 < word_count <= 1000:
        quality_factors['length'] = 15
    elif 100 <= word_count < 200 or 1000 < word_count <= 1200:
        quality_factors['length'] = 10
    else:
        quality_factors['length'] = 5
    
    # Structure scoring (sections detection)
    text_lower = parsed_resume.text.lower()
    sections = ['experience', 'education', 'skills', 'summary', 'objective']
    section_count = sum(1 for section in sections if section in text_lower)
    quality_factors['structure'] = min(section_count * 4, 20)
    
    # Skills match scoring
    if ats_results:
        total_skills = len(ats_results.matched_skills) + len(ats_results.missing_skills)
        if total_skills > 0:
            match_ratio = len(ats_results.matched_skills) / total_skills
            quality_factors['skills_match'] = int(min(match_ratio * 30, 30))
    
    # Keywords density scoring
    if hasattr(ats_results, 'keywords') and ats_results.keywords:
        keyword_density = len(ats_results.keywords) / word_count * 100
        if 2 <= keyword_density <= 8:  # Optimal keyword density
            quality_factors['keywords'] = 20
        elif 1 <= keyword_density < 2 or 8 < keyword_density <= 12:
            quality_factors['keywords'] = 15
        else:
            quality_factors['keywords'] = 10
    
    # Readability scoring (sentence length and complexity)
    sentences = parsed_resume.text.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    if 10 <= avg_sentence_length <= 20:
        quality_factors['readability'] = 10
    elif 8 <= avg_sentence_length < 10 or 20 < avg_sentence_length <= 25:
        quality_factors['readability'] = 8
    else:
        quality_factors['readability'] = 5
    
    return quality_factors, sum(quality_factors.values())


def get_industry_insights(job_description, matched_skills, missing_skills):
    """Generate industry-specific insights based on job description."""
    jd_lower = job_description.lower()
    
    # Detect industry/role type
    industry_keywords = {
        'data_science': ['data scientist', 'machine learning', 'analytics', 'python', 'r', 'sql'],
        'web_development': ['frontend', 'backend', 'react', 'javascript', 'html', 'css'],
        'mobile_development': ['ios', 'android', 'mobile', 'react native', 'flutter'],
        'devops': ['devops', 'kubernetes', 'docker', 'aws', 'ci/cd', 'terraform'],
        'ai_ml': ['artificial intelligence', 'machine learning', 'deep learning', 'nlp', 'computer vision']
    }
    
    detected_industry = 'general'
    for industry, keywords in industry_keywords.items():
        if sum(1 for keyword in keywords if keyword in jd_lower) >= 2:
            detected_industry = industry
            break
    
    # Industry-specific recommendations
    industry_insights = {
        'data_science': {
            'critical_skills': ['python', 'sql', 'pandas', 'numpy', 'scikit-learn'],
            'nice_to_have': ['tensorflow', 'pytorch', 'tableau', 'spark'],
            'tips': 'Focus on showcasing data projects and quantifiable business impact'
        },
        'web_development': {
            'critical_skills': ['javascript', 'html', 'css', 'react', 'node'],
            'nice_to_have': ['typescript', 'webpack', 'sass', 'mongodb'],
            'tips': 'Highlight responsive design skills and modern framework experience'
        },
        'mobile_development': {
            'critical_skills': ['ios', 'android', 'swift', 'kotlin'],
            'nice_to_have': ['react native', 'flutter', 'firebase'],
            'tips': 'Emphasize app store publications and cross-platform experience'
        },
        'devops': {
            'critical_skills': ['docker', 'kubernetes', 'aws', 'linux', 'jenkins'],
            'nice_to_have': ['terraform', 'ansible', 'prometheus', 'grafana'],
            'tips': 'Quantify infrastructure improvements and automation achievements'
        },
        'general': {
            'critical_skills': [],
            'nice_to_have': [],
            'tips': 'Focus on transferable skills and measurable achievements'
        }
    }
    
    return detected_industry, industry_insights.get(detected_industry, industry_insights['general'])


def display_smart_recommendations(ats, analysis, quality_factors, industry_insights, detected_industry):
    """Display smart recommendations panel with enhanced styling and actionable insights."""
    st.markdown("""
    <div class="recommendations-panel">
        <h3 style="text-align: center; margin-bottom: 1.5rem; color: white;">🎯 Smart Recommendations</h3>
    """, unsafe_allow_html=True)
    
    # Priority recommendations based on lowest quality factors
    recommendations = []
    
    # Analyze quality factors for recommendations
    if quality_factors['length'] < 15:
        word_count = len(st.session_state.parsed_resume.text.split()) if st.session_state.parsed_resume else 0
        if word_count < 300:
            recommendations.append({
                'priority': 'high',
                'category': 'Content Length',
                'issue': 'Resume is too short',
                'action': 'Add more details about your experience, achievements, and skills',
                'icon': '📝'
            })
        else:
            recommendations.append({
                'priority': 'medium',
                'category': 'Content Length',
                'issue': 'Resume is too long',
                'action': 'Condense content and focus on most relevant experiences',
                'icon': '✂️'
            })
    
    if quality_factors['structure'] < 15:
        recommendations.append({
            'priority': 'high',
            'category': 'Structure',
            'issue': 'Missing key resume sections',
            'action': 'Add clear sections: Summary, Experience, Education, Skills',
            'icon': '🏗️'
        })
    
    if quality_factors['skills_match'] < 20:
        recommendations.append({
            'priority': 'high',
            'category': 'Skills Alignment',
            'issue': 'Low skills match with job requirements',
            'action': 'Incorporate more relevant skills from the job description',
            'icon': '🎯'
        })
    
    # Industry-specific recommendations
    if detected_industry != 'general':
        critical_missing = set(industry_insights['critical_skills']) - ats.matched_skills
        if critical_missing:
            recommendations.append({
                'priority': 'critical',
                'category': f'{detected_industry.replace("_", " ").title()} Skills',
                'issue': f'Missing critical skills: {", ".join(list(critical_missing)[:3])}',
                'action': 'Highlight experience with these technologies or acquire these skills',
                'icon': '⚡'
            })
    
    # Display recommendations in priority order
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
    
    if recommendations:
        for i, rec in enumerate(recommendations[:5]):  # Show top 5 recommendations
            priority_colors = {
                'critical': '#e74c3c',
                'high': '#f39c12', 
                'medium': '#f1c40f',
                'low': '#95a5a6'
            }
            
            st.markdown(f"""
            <div class="recommendation-item {rec['priority']}">
                <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.8rem;">{rec['icon']}</span>
                    <div class="priority-badge" style="background: {priority_colors[rec['priority']]};">
                        {rec['priority']} Priority
                    </div>
                    <span style="margin-left: auto; font-weight: bold; color: white; font-size: 1.1rem;">{rec['category']}</span>
                </div>
                <div style="margin-bottom: 0.8rem; color: rgba(255,255,255,0.9); font-size: 1rem;">
                    <strong>Issue:</strong> {rec['issue']}
                </div>
                <div style="color: rgba(255,255,255,0.8); font-size: 0.95rem;">
                    <strong>Action:</strong> {rec['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: rgba(46, 204, 113, 0.2); border-radius: 12px; border: 1px solid rgba(46, 204, 113, 0.3);">
            <h4 style="color: #2ecc71; margin: 0;">🎉 Excellent Work!</h4>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Your resume meets most quality criteria.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)  # Close recommendations-panel


def render_analysis_section():
    """Render the enhanced resume analysis section with new gradient theme."""
    parsed = st.session_state.parsed_resume
    
    # Modern dashboard header with gradient background
    st.markdown("""
    <div class="analysis-dashboard">
        <div class="dashboard-header">
            📊 Resume Analysis Dashboard
        </div>
        <p style="text-align: center; font-size: 1.1rem; opacity: 0.9; margin-top: -1rem;">
            Comprehensive AI-powered analysis with industry insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if background analysis was in progress
    if st.session_state.get('analysis_in_progress', False):
        st.info("🔄 Analysis is being processed in the background...")
        st.session_state.analysis_in_progress = False  # Reset flag
    
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
                    show_toast("🔄 Starting comprehensive analysis...", "info")
                    
                    # Traditional analysis
                    analysis = analyze_skills(parsed.text, st.session_state.job_description)
                    ats = compute_ats_score(parsed.text, st.session_state.job_description)
                    suggs = improvement_suggestions(parsed.text, analysis)
                    
                    # Cache results
                    st.session_state.skill_analysis = analysis
                    st.session_state.ats_results = ats
                    st.session_state.improvement_suggestions = suggs
                    st.session_state.last_jd_hash = current_jd_hash
                    st.session_state.analysis_completed = True
                    
                    show_toast("🎉 Analysis completed successfully!", "success")
                    time.sleep(0.1)  # Brief pause for visibility
                    
                except Exception as e:
                    show_toast(f"❌ Analysis failed: {str(e)}", "error")
                    st.info("💡 Please check your inputs and try again")
        else:
            # Use cached results
            analysis = st.session_state.skill_analysis
            ats = st.session_state.ats_results
            suggs = st.session_state.improvement_suggestions
            # Ensure completion flag is set when using cached results
            st.session_state.analysis_completed = True
        
        if ats and analysis:
            # Enhanced metrics display with modern dashboard style
            st.markdown("""
            <div class="analysis-dashboard">
                <h3 style="text-align: center; margin-bottom: 1.5rem; color: white;">📈 Performance Dashboard</h3>
            """, unsafe_allow_html=True)
            
            # Calculate enhanced quality score
            quality_factors, overall_quality = calculate_resume_quality_score(parsed, ats, analysis)
            
            # Get industry insights
            detected_industry, industry_insights = get_industry_insights(
                st.session_state.job_description, ats.matched_skills, ats.missing_skills
            )
            
            # Enhanced metrics grid with glassmorphism cards
            col1, col2, col3, col4, col5 = st.columns(5)
            
            metrics_data = [
                {
                    "col": col1,
                    "icon": "🎯",
                    "label": "ATS Score",
                    "value": f"{ats.score}",
                    "unit": "/100",
                    "delta": f"{ats.score-70:.1f} vs baseline",
                    "color": "#2ecc71" if ats.score >= 70 else "#e74c3c"
                },
                {
                    "col": col2,
                    "icon": "🔗",
                    "label": "Skills Match",
                    "value": f"{len(ats.matched_skills)}",
                    "unit": f"/{len(ats.matched_skills) + len(ats.missing_skills)}",
                    "delta": f"{len(ats.matched_skills)/(len(ats.matched_skills) + len(ats.missing_skills))*100:.1f}%" if (len(ats.matched_skills) + len(ats.missing_skills)) > 0 else "0%",
                    "color": "#3498db"
                },
                {
                    "col": col3,
                    "icon": "📈",
                    "label": "Coverage",
                    "value": f"{analysis.matched_ratio * 100:.1f}" if analysis and hasattr(analysis, 'matched_ratio') else "0",
                    "unit": "%",
                    "delta": f"{(analysis.matched_ratio * 100)-50:.1f}% vs avg" if analysis and hasattr(analysis, 'matched_ratio') else "0% vs avg",
                    "color": "#9b59b6"
                },
                {
                    "col": col4,
                    "icon": "📝",
                    "label": "Word Count",
                    "value": f"{len(parsed.text.split())}",
                    "unit": " words",
                    "delta": "Good" if 300 <= len(parsed.text.split()) <= 800 else ("Too short" if len(parsed.text.split()) < 300 else "Too long"),
                    "color": "#2ecc71" if 300 <= len(parsed.text.split()) <= 800 else "#e74c3c"
                },
                {
                    "col": col5,
                    "icon": "⭐",
                    "label": "Quality Score",
                    "value": f"{overall_quality}",
                    "unit": "/100",
                    "delta": "Excellent" if overall_quality >= 85 else "Good" if overall_quality >= 70 else "Needs Work",
                    "color": "#2ecc71" if overall_quality >= 70 else "#e74c3c"
                }
            ]
            
            for metric in metrics_data:
                with metric["col"]:
                    st.markdown(f"""
                    <div class="metric-card-enhanced">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{metric["icon"]}</div>
                        <div class="metric-value">{metric["value"]}<span style="font-size: 1rem; opacity: 0.7;">{metric["unit"]}</span></div>
                        <div class="metric-label">{metric["label"]}</div>
                        <div class="metric-delta" style="color: {metric["color"]};">
                            {metric["delta"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close analysis-dashboard
            
            # Industry Detection Banner with enhanced styling
            if detected_industry != 'general':
                st.markdown(f"""
                <div class="industry-banner">
                    <h4 style="color: white; margin: 0; font-size: 1.3rem;">🎯 Detected Industry: {detected_industry.replace('_', ' ').title()}</h4>
                    <p style="color: rgba(255,255,255,0.9); margin: 0.8rem 0 0 0; font-size: 1rem;">{industry_insights['tips']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced visual charts with modern styling
            try:
                st.markdown("""
                <div class="skills-analysis-container">
                    <h3 style="text-align: center; margin-bottom: 1.5rem; color: white;">🔍 Advanced Skills Analysis</h3>
                """, unsafe_allow_html=True)
                
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    st.markdown('<div class="chart-container-enhanced">', unsafe_allow_html=True)
                    # Enhanced ATS Score Gauge with Quality Indicators
                    fig_gauge = go.Figure()
                    
                    # Main ATS gauge with custom styling
                    fig_gauge.add_trace(go.Indicator(
                        mode = "gauge+number+delta",
                        value = ats.score,
                        domain = {'x': [0, 1], 'y': [0.5, 1]},
                        title = {'text': "ATS Score", 'font': {'size': 18, 'color': 'white'}},
                        delta = {'reference': 70, 'increasing': {'color': "#2ecc71"}, 'decreasing': {'color': "#e74c3c"}},
                        gauge = {
                            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                            'bar': {'color': "#2ecc71" if ats.score >= 70 else "#e74c3c"},
                            'steps': [
                                {'range': [0, 50], 'color': "rgba(231, 76, 60, 0.3)"},
                                {'range': [50, 70], 'color': "rgba(243, 156, 18, 0.3)"},
                                {'range': [70, 85], 'color': "rgba(46, 204, 113, 0.3)"},
                                {'range': [85, 100], 'color': "rgba(46, 204, 113, 0.5)"}
                            ],
                            'threshold': {
                                'line': {'color': "white", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    
                    fig_gauge.update_layout(
                        height=250,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font={'color': 'white'}
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_chart2:
                    st.markdown('<div class="chart-container-enhanced">', unsafe_allow_html=True)
                    # Skills distribution with modern styling
                    if ats.matched_skills or ats.missing_skills:
                        fig_skills = make_subplots(
                            rows=2, cols=1,
                            subplot_titles=('Skills Distribution', 'Quality Factors'),
                            specs=[[{"type": "pie"}], [{"type": "bar"}]],
                            vertical_spacing=0.15
                        )
                        
                        # Skills pie chart with custom colors
                        fig_skills.add_trace(go.Pie(
                            labels=['Matched Skills', 'Missing Skills'],
                            values=[len(ats.matched_skills), len(ats.missing_skills)],
                            marker_colors=['#2ecc71', '#e74c3c'],
                            hole=0.4,
                            textfont={'color': 'white'}
                        ), row=1, col=1)
                        
                        # Quality factors bar chart with gradient colors
                        fig_skills.add_trace(go.Bar(
                            x=list(quality_factors.keys()),
                            y=list(quality_factors.values()),
                            marker_color=['#1e3c72', '#2a5298', '#3498db', '#2ecc71', '#f39c12'],
                            text=list(quality_factors.values()),
                            textposition='auto',
                            textfont={'color': 'white'}
                        ), row=2, col=1)
                        
                        fig_skills.update_layout(
                            height=400, 
                            showlegend=True,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font={'color': 'white'}
                        )
                        st.plotly_chart(fig_skills, use_container_width=True)
                    else:
                        st.info("No skills data available for visualization")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)  # Close skills-analysis-container
                
            except Exception as chart_error:
                st.warning(f"Charts not available: {chart_error}")
            
            # Enhanced Smart Recommendations Panel
            display_smart_recommendations(ats, analysis, quality_factors, industry_insights, detected_industry)
                
            # Enhanced analysis with Gemini (only if not already cached)
            if st.session_state.gemini_service and ats and analysis:
                if not st.session_state.analysis_results or getattr(st.session_state, 'last_ai_jd_hash', None) != current_jd_hash:
                    with st.spinner("🤖 Generating AI-powered analysis..."):
                        try:
                            show_toast("🧠 AI is analyzing your resume...", "info")
                            
                            gemini_analysis = analyze_resume_with_gemini(
                                st.session_state.gemini_service, 
                                parsed.text, 
                                st.session_state.job_description, 
                                st.session_state.selected_role
                            )
                            st.session_state.analysis_results = gemini_analysis
                            st.session_state.last_ai_jd_hash = current_jd_hash
                            st.session_state.analysis_completed = True  # Mark as completed for AI analysis too
                            
                            show_toast("✨ AI analysis completed!", "success")
                            
                        except Exception as e:
                            show_toast(f"⚠️ AI Analysis failed: {str(e)}", "error")
                            
            # Display Gemini analysis results if available
            if st.session_state.analysis_results:
                st.markdown("""
                <div class="ai-analysis-panel">
                    <h3 style="text-align: center; margin-bottom: 1.5rem; color: white;">🤖 AI-Powered Analysis</h3>
                """, unsafe_allow_html=True)
                with st.expander("📋 Detailed AI Analysis", expanded=True):
                    # Extract and display the analysis content properly
                    if isinstance(st.session_state.analysis_results, dict) and 'analysis' in st.session_state.analysis_results:
                        analysis_content = st.session_state.analysis_results['analysis']
                        st.markdown(analysis_content)
                    else:
                        st.markdown(str(st.session_state.analysis_results))
                st.markdown("</div>", unsafe_allow_html=True)
                    
            # Display traditional analysis results
            display_traditional_analysis(ats, analysis, suggs)
            
        else:
            st.error("❌ Failed to generate analysis results. Please ensure both resume and job description are provided.")
    else:
        st.warning("📝 Please provide a job description in the sidebar to enable resume analysis.")


def display_traditional_analysis(ats, analysis, suggs):
    """Display enhanced traditional analysis results with improved UI and modern styling."""
    st.markdown("""
    <div class="skills-analysis-container">
        <h3 style="text-align: center; margin-bottom: 1.5rem; color: white;">🎯 Detailed Skills Analysis</h3>
        <div class="skills-grid">
    """, unsafe_allow_html=True)
    
    # Enhanced skills breakdown with modern styling
    col1, col2 = st.columns(2)
    
    with col1:
        if ats.matched_skills:
            st.markdown("""
            <div class="skills-section matched">
                <h4 style="color: #2ecc71; margin-bottom: 1rem; display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">✅</span>
                    Matched Skills
                </h4>
            """, unsafe_allow_html=True)
            
            matched_skills_list = list(ats.matched_skills)[:10]
            for i, skill in enumerate(matched_skills_list):
                st.markdown(f"""
                <div class="skill-item matched">
                    <strong style="color: white;">{skill.title()}</strong>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7); margin-top: 0.2rem;">
                        Match Score: {min(100, 80 + (10-i)*2)}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(ats.matched_skills) > 10:
                st.markdown(f"""
                <div style="text-align: center; margin-top: 1rem; color: rgba(255,255,255,0.8);">
                    <em>+ {len(ats.matched_skills) - 10} more skills matched</em>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="skills-section">
                <div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.7);">
                    <span style="font-size: 3rem; display: block; margin-bottom: 1rem;">🔍</span>
                    <p style="margin: 0;">No matched skills found</p>
                    <small>Try updating your resume with relevant keywords</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with col2:
        if ats.missing_skills:
            st.markdown("""
            <div class="skills-section missing">
                <h4 style="color: #e74c3c; margin-bottom: 1rem; display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">❌</span>
                    Missing Key Skills
                </h4>
            """, unsafe_allow_html=True)
            
            missing_skills_list = list(ats.missing_skills)[:10]
            for i, skill in enumerate(missing_skills_list):
                importance = "High" if i < 3 else "Medium" if i < 7 else "Low"
                importance_color = "#e74c3c" if importance == "High" else "#f39c12" if importance == "Medium" else "#95a5a6"
                
                st.markdown(f"""
                <div class="skill-item missing">
                    <strong style="color: white;">{skill.title()}</strong>
                    <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7); margin-top: 0.2rem; display: flex; justify-content: space-between;">
                        <span>Consider adding this skill</span>
                        <span style="color: {importance_color}; font-weight: bold;">{importance}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(ats.missing_skills) > 10:
                st.markdown(f"""
                <div style="text-align: center; margin-top: 1rem; color: rgba(255,255,255,0.8);">
                    <em>+ {len(ats.missing_skills) - 10} more skills to consider</em>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="skills-section">
                <div style="text-align: center; padding: 2rem; background: rgba(46, 204, 113, 0.2); border-radius: 12px;">
                    <span style="font-size: 3rem; display: block; margin-bottom: 1rem;">🎉</span>
                    <p style="color: #2ecc71; margin: 0; font-weight: bold;">Great! No critical skills missing</p>
                    <small style="color: rgba(255,255,255,0.8);">Your skill set aligns well with the job requirements</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)  # Close skills-grid and skills-analysis-container
    
    # Enhanced improvement suggestions with categories
    if suggs:
        st.markdown("""
        <div class="recommendations-panel">
            <h3 style="text-align: center; margin-bottom: 1.5rem; color: white;">💡 Actionable Improvement Suggestions</h3>
        """, unsafe_allow_html=True)
        
        # Categorize suggestions (simple heuristic)
        categorized_suggestions = {
            'Content': [],
            'Skills': [],
            'Format': [],
            'Keywords': [],
            'General': []
        }
        
        for suggestion in suggs:
            suggestion_lower = suggestion.lower()
            if any(word in suggestion_lower for word in ['skill', 'technology', 'tool']):
                categorized_suggestions['Skills'].append(suggestion)
            elif any(word in suggestion_lower for word in ['keyword', 'term', 'phrase']):
                categorized_suggestions['Keywords'].append(suggestion)
            elif any(word in suggestion_lower for word in ['format', 'structure', 'section']):
                categorized_suggestions['Format'].append(suggestion)
            elif any(word in suggestion_lower for word in ['experience', 'achievement', 'accomplishment']):
                categorized_suggestions['Content'].append(suggestion)
            else:
                categorized_suggestions['General'].append(suggestion)
        
        # Display categorized suggestions in a grid
        suggestion_cols = st.columns(2)
        col_index = 0
        
        category_icons = {
            'Content': '📝', 'Skills': '🛠️', 'Format': '📐', 
            'Keywords': '🔍', 'General': '💭'
        }
        
        category_colors = {
            'Content': '#3498db', 'Skills': '#e67e22', 'Format': '#9b59b6',
            'Keywords': '#1abc9c', 'General': '#95a5a6'
        }
        
        for category, category_suggestions in categorized_suggestions.items():
            if category_suggestions:
                with suggestion_cols[col_index % 2]:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 1.5rem; margin: 0.5rem 0; border-left: 4px solid {category_colors[category]};">
                        <h5 style="color: {category_colors[category]}; margin-bottom: 1rem; display: flex; align-items: center;">
                            <span style="font-size: 1.3rem; margin-right: 0.5rem;">{category_icons[category]}</span>
                            {category} ({len(category_suggestions)})
                        </h5>
                    """, unsafe_allow_html=True)
                    
                    for suggestion in category_suggestions:
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.05); padding: 0.8rem; margin: 0.5rem 0; border-radius: 8px; border-left: 2px solid {category_colors[category]};">
                            <span style="color: rgba(255,255,255,0.9);">• {suggestion}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                col_index += 1
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close recommendations-panel
    
    # Keywords analysis with enhanced visualization
    if hasattr(ats, 'keywords') and ats.keywords:
        st.markdown("""
        <div class="chart-container-enhanced">
            <h3 style="text-align: center; margin-bottom: 1.5rem; color: white;">🔍 Keywords & Relevance Analysis</h3>
        """, unsafe_allow_html=True)
        
        col_kw1, col_kw2 = st.columns([2, 1])
        
        with col_kw1:
            st.markdown('<h4 style="color: white; margin-bottom: 1rem;">📊 Top Keywords Found</h4>', unsafe_allow_html=True)
            keywords_display = ats.keywords[:15]  # Show top 15
            
            # Create enhanced keyword cloud with gradient effects
            keyword_html = "<div style='display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0;'>"
            for i, keyword in enumerate(keywords_display):
                size = max(0.8, 1.3 - (i * 0.03))  # Decreasing size
                opacity = max(0.6, 1 - (i * 0.03))  # Decreasing opacity
                gradient_stop = min(100, 30 + (15-i)*5)  # Color variation
                
                keyword_html += f"""
                <span style="background: linear-gradient(135deg, rgba(30, 60, 114, {opacity}) 0%, rgba(42, 82, 152, {opacity}) 100%); 
                           padding: 0.4rem 1rem; border-radius: 20px; 
                           font-size: {size}rem; color: white; font-weight: 600;
                           box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                           border: 1px solid rgba(255,255,255,0.2);
                           transition: transform 0.2s ease;">
                    {keyword}
                </span>
                """
            keyword_html += "</div>"
            st.markdown(keyword_html, unsafe_allow_html=True)
        
        with col_kw2:
            st.markdown('<h4 style="color: white; margin-bottom: 1rem;">📈 Keyword Stats</h4>', unsafe_allow_html=True)
            total_keywords = len(ats.keywords) if hasattr(ats, 'keywords') else 0
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                <div style="color: white; font-size: 1.5rem; font-weight: bold; text-align: center;">{total_keywords}</div>
                <div style="color: rgba(255,255,255,0.8); text-align: center; font-size: 0.9rem;">Total Keywords</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                <div style="color: white; font-size: 1.5rem; font-weight: bold; text-align: center;">{min(15, total_keywords)}</div>
                <div style="color: rgba(255,255,255,0.8); text-align: center; font-size: 0.9rem;">Displayed</div>
            </div>
            """, unsafe_allow_html=True)
            
            if total_keywords > 15:
                st.markdown(f"""
                <div style="text-align: center; color: rgba(255,255,255,0.7); font-size: 0.85rem; margin-top: 1rem;">
                    <em>+{total_keywords - 15} more keywords found</em>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close chart-container-enhanced
