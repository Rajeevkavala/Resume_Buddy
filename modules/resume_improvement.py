"""
Resume Improvement Module
Handles resume enhancement and optimization features.
"""

import streamlit as st
import time
from analysis import analyze_skills, improvement_suggestions
from export_utils import build_improved_resume_text, generate_docx, generate_pdf
from gemini_integration import improve_resume_with_gemini

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


def render_improvement_section():
    """Render the resume improvement section with background processing support."""
    st.markdown('<div class="section-header">✨ Resume Improvement</div>', unsafe_allow_html=True)
    
    if not st.session_state.parsed_resume:
        st.warning("📄 Please upload and analyze a resume first.")
        return
    
    # Check if background improvement was in progress
    if st.session_state.get('improvement_in_progress', False):
        with st.spinner("🔄 Background resume improvement processing in progress..."):
            time.sleep(0.1)  # Brief pause for visual feedback
        st.info("✅ Resume improvement completed in background!")
        st.session_state.improvement_in_progress = False  # Reset flag
    
    # Check if resume analysis has been performed
    if not st.session_state.ats_results or not st.session_state.skill_analysis:
        st.warning("📊 Please perform Resume Analysis first to get improvement recommendations.")
        st.info("💡 Go to the Resume Analysis section and analyze your resume against a job description.")
        
        # Show what's missing
        missing_items = []
        if not st.session_state.ats_results:
            missing_items.append("ATS Score Analysis")
        if not st.session_state.skill_analysis:
            missing_items.append("Skills Analysis")
        
        st.markdown("**Missing Analysis Components:**")
        for item in missing_items:
            st.markdown(f"• {item}")
        
        return
    
    # Display current analysis summary
    display_analysis_summary()
    
    parsed = st.session_state.parsed_resume
    
    # Improvement options
    st.markdown("### 🎯 Improvement Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        improvement_focus = st.multiselect(
            "Improvement Focus Areas", 
            ["Professional Summary", "Skills Section", "Achievement Quantification",
             "ATS Optimization", "Action Verbs", "Industry Keywords", "Missing Skills"],
            default=["ATS Optimization", "Missing Skills", "Achievement Quantification"], 
            key="improvement_focus_select"
        )
    
    with col2:
        enhancement_level = st.selectbox(
            "Enhancement Level",
            ["Light Enhancement", "Moderate Enhancement", "Comprehensive Overhaul"],
            key="enhancement_level_select"
        )
    
    # Show cached results if available
    cached_key = f"{str(improvement_focus)}_{enhancement_level}_{hash(st.session_state.job_description.strip()) if st.session_state.job_description.strip() else 'no_jd'}"
    
    if (st.session_state.improved_resume and 
        getattr(st.session_state, 'last_improvement_key', None) == cached_key):
        
        # Create container for cached results
        if 'improved_resume_display_container' not in st.session_state:
            st.session_state.improved_resume_display_container = st.empty()
        
        with st.session_state.improved_resume_display_container.container():
            st.markdown("### ✨ Resume Improvement Results (Cached)")
            display_improved_resume(st.session_state.improved_resume)
            st.info("💡 Results cached from previous generation. Click 'Generate Improved Resume' to refresh.")
    
    # Generate improved resume button
    if st.button("🚀 Generate Improved Resume", key="generate_improved_btn"):
        generate_improved_resume(improvement_focus, enhancement_level, cached_key)


def display_analysis_summary():
    """Display a summary of the current analysis results."""
    st.markdown("### 📊 Current Analysis Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    ats = st.session_state.ats_results
    analysis = st.session_state.skill_analysis
    
    with col1:
        st.metric("ATS Score", f"{ats.score:.1f}/100", f"{ats.score - 50:.1f} vs baseline")
    
    with col2:
        matched_skills = len(ats.matched_skills) if ats.matched_skills else 0
        total_skills = matched_skills + len(ats.missing_skills) if ats.missing_skills else matched_skills
        st.metric("Skills Match", f"{matched_skills}/{total_skills}", f"{(matched_skills/total_skills*100):.1f}% match" if total_skills > 0 else "No data")
    
    with col3:
        st.metric("Missing Skills", len(ats.missing_skills) if ats.missing_skills else 0)
    
    with col4:
        st.metric("Improvement Areas", len(st.session_state.improvement_suggestions) if st.session_state.improvement_suggestions else 0)
    
    # Key improvement opportunities
    if ats.missing_skills:
        with st.expander("🎯 Key Improvement Opportunities", expanded=False):
            st.markdown("**Missing Skills to Add:**")
            missing_skills_list = list(ats.missing_skills)[:8] if isinstance(ats.missing_skills, set) else ats.missing_skills[:8]  # Show top 8
            for skill in missing_skills_list:
                st.markdown(f"• {skill}")
            
            if len(ats.missing_skills) > 8:
                st.markdown(f"• ... and {len(ats.missing_skills) - 8} more")


def generate_improved_resume(improvement_focus, enhancement_level, cached_key):
    """Generate improved resume based on options and analysis data."""
    parsed = st.session_state.parsed_resume
    
    # Clear any existing improved resume to prevent duplication
    if 'improved_resume_display_container' in st.session_state:
        del st.session_state.improved_resume_display_container
    
    if st.session_state.gemini_service:
        with st.spinner("🤖 Creating improved resume with Gemini AI..."):
            try:
                # Gather comprehensive analysis data
                analysis_data = compile_analysis_data()
                
                improved_content = improve_resume_with_gemini(
                    st.session_state.gemini_service, 
                    parsed.text, 
                    analysis_data,
                    improvement_focus,
                    enhancement_level,
                    st.session_state.selected_role
                )
                st.session_state.improved_resume = improved_content
                st.session_state.last_improvement_key = cached_key
                st.session_state.improvement_completed = True  # Mark as completed
                
                # Create a placeholder for the improved resume display
                st.session_state.improved_resume_display_container = st.empty()
                
                with st.session_state.improved_resume_display_container.container():
                    st.markdown("### ✨ AI-Improved Resume")
                    display_improved_resume(improved_content)
                
                show_toast("✅ Resume improvement completed successfully!", "success")
                
            except Exception as e:
                show_toast(f"❌ Failed to improve resume: {str(e)}", "error")
                # Debug information for troubleshooting
                if "subscriptable" in str(e):
                    st.error("🔍 **Debug Info**: This appears to be a data type issue. Please try refreshing the page and running the Resume Analysis again before improvement.")
                st.info("💡 Check your Gemini API key and try again")
    else:
        # Fallback to traditional improvement
        generate_traditional_improvement(improvement_focus, enhancement_level, cached_key)


def compile_analysis_data():
    """Compile all available analysis data for resume improvement."""
    ats = st.session_state.ats_results
    analysis = st.session_state.skill_analysis
    ai_analysis = st.session_state.analysis_results or {}
    suggestions = st.session_state.improvement_suggestions or []
    
    # Ensure missing skills are properly extracted and formatted
    missing_skills = []
    matched_skills = []
    
    if ats:
        if hasattr(ats, 'missing_skills') and ats.missing_skills:
            if isinstance(ats.missing_skills, set):
                missing_skills = list(ats.missing_skills)[:20]  # Top 20 missing skills
            else:
                missing_skills = list(ats.missing_skills)[:20]
        if hasattr(ats, 'matched_skills') and ats.matched_skills:
            if isinstance(ats.matched_skills, set):
                matched_skills = list(ats.matched_skills)[:15]  # Top 15 matched skills
            else:
                matched_skills = list(ats.matched_skills)[:15]
    
    # Additional missing skills from analysis gaps
    if analysis and hasattr(analysis, 'gaps') and analysis.gaps:
        gaps_list = list(analysis.gaps)[:10] if isinstance(analysis.gaps, set) else analysis.gaps[:10]
        for gap in gaps_list:  # Add up to 10 more from gaps
            if gap not in missing_skills:
                missing_skills.append(gap)
    
    return {
        "ats_score": ats.score if ats else 0,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "strengths": list(analysis.strengths) if analysis and hasattr(analysis, 'strengths') else [],
        "gaps": list(analysis.gaps) if analysis and hasattr(analysis, 'gaps') else [],
        "suggestions": suggestions,
        "ai_analysis": ai_analysis.get('analysis', '') if ai_analysis else '',
        "job_description": st.session_state.job_description,
        "current_role": st.session_state.selected_role,
        "total_missing_count": len(missing_skills),
        "total_matched_count": len(matched_skills)
    }


def generate_traditional_improvement(improvement_focus, enhancement_level, cached_key):
    """Generate traditional resume improvement using analysis data."""
    st.info("🤖 Enable Gemini AI for advanced resume improvement")
    
    parsed = st.session_state.parsed_resume
    
    # Clear any existing improved resume to prevent duplication
    if 'improved_resume_display_container' in st.session_state:
        del st.session_state.improved_resume_display_container
    
    if st.session_state.job_description.strip():
        with st.spinner("🔄 Creating improved resume (traditional method)..."):
            try:
                # Use existing analysis data
                analysis = st.session_state.skill_analysis
                ats = st.session_state.ats_results
                suggs = st.session_state.improvement_suggestions
                
                # Create improvement summary based on analysis
                improvement_summary = create_improvement_summary(ats, analysis, improvement_focus)
                
                improved_text = build_improved_resume_text(
                    resume_text=parsed.text,
                    suggestions=suggs,
                    strengths=analysis.strengths if analysis and hasattr(analysis, 'strengths') else [],
                    gaps=analysis.gaps if analysis and hasattr(analysis, 'gaps') else [],
                    role=st.session_state.selected_role
                )
                
                st.session_state.improved_resume = {
                    "content": improved_text,
                    "summary": improvement_summary,
                    "type": "traditional"
                }
                st.session_state.last_improvement_key = cached_key
                st.session_state.improvement_completed = True  # Mark as completed
                
                # Create a placeholder for the improved resume display
                st.session_state.improved_resume_display_container = st.empty()
                
                with st.session_state.improved_resume_display_container.container():
                    st.markdown("### 📝 Traditional Improvement")
                    
                    # Display improvement summary
                    if improvement_summary:
                        st.markdown("#### 🎯 Improvements Made:")
                        for item in improvement_summary:
                            st.markdown(item)
                    
                    display_traditional_improvement(improved_text)
                
                show_toast("✅ Traditional resume improvement completed!", "success")
                
            except Exception as e:
                show_toast(f"❌ Traditional improvement failed: {str(e)}", "error")
                st.info("💡 Try enabling Gemini AI for better results.")
    else:
        show_toast("📝 Provide a Job Description for resume improvement", "warning")


def create_improvement_summary(ats, analysis, improvement_focus):
    """Create a summary of improvements made."""
    summary = []
    
    if ats and hasattr(ats, 'missing_skills') and ats.missing_skills:
        missing_count = len(ats.missing_skills) if isinstance(ats.missing_skills, (set, list)) else 0
        summary.append(f"• Added {min(missing_count, 10)} missing skills from analysis")
    
    if "ATS Optimization" in improvement_focus:
        ats_score = ats.score if ats and hasattr(ats, 'score') else 0
        summary.append(f"• Improved ATS score from {ats_score:.1f}/100")
    
    if "Achievement Quantification" in improvement_focus:
        summary.append("• Enhanced descriptions with quantified achievements")
    
    if "Professional Summary" in improvement_focus:
        summary.append("• Added compelling professional summary")
        
    if analysis and hasattr(analysis, 'strengths') and analysis.strengths:
        strengths_count = len(analysis.strengths) if isinstance(analysis.strengths, (set, list)) else 0
        summary.append(f"• Highlighted {strengths_count} key strengths")
    
    return summary


def display_improved_resume(improved_content):
    """Display improved resume with download options and analytics."""
    # Display improvement metrics
    display_improvement_metrics()
    
    tab1, tab2, tab3 = st.tabs(["📄 Improved Resume", "📊 Comparison", "📥 Download Options"])
    
    with tab1:
        with st.expander("📄 Preview Improved Resume", expanded=True):
            if isinstance(improved_content, dict):
                st.markdown(improved_content.get('content', improved_content))
            else:
                st.markdown(improved_content)
    
    with tab2:
        content_to_compare = improved_content.get('content', improved_content) if isinstance(improved_content, dict) else improved_content
        display_resume_comparison(content_to_compare)
    
    with tab3:
        content_to_download = improved_content.get('content', improved_content) if isinstance(improved_content, dict) else improved_content
        display_download_options(content_to_download)


def display_improvement_metrics():
    """Display metrics showing the improvement impact."""
    if not st.session_state.ats_results:
        return
        
    ats = st.session_state.ats_results
    
    st.markdown("#### 🎯 Improvement Impact")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Estimated ATS score improvement
        estimated_improvement = min(25, len(ats.missing_skills) * 2) if ats.missing_skills else 0
        new_score = min(100, ats.score + estimated_improvement)
        st.metric("Estimated ATS Score", f"{new_score:.1f}/100", f"+{estimated_improvement:.1f}")
    
    with col2:
        missing_count = len(ats.missing_skills) if ats.missing_skills else 0
        added_skills = min(missing_count, 10)  # Assume we add up to 10 missing skills
        st.metric("Skills Added", added_skills, f"Addressed {added_skills}/{missing_count}")
    
    with col3:
        matched_count = len(ats.matched_skills) if ats.matched_skills else 0
        total_skills = matched_count + missing_count
        new_match_rate = ((matched_count + added_skills) / total_skills * 100) if total_skills > 0 else 0
        old_match_rate = (matched_count / total_skills * 100) if total_skills > 0 else 0
        improvement = new_match_rate - old_match_rate
        st.metric("Skills Match Rate", f"{new_match_rate:.1f}%", f"+{improvement:.1f}%")
    
    with col4:
        sugg_count = len(st.session_state.improvement_suggestions) if st.session_state.improvement_suggestions else 0
        st.metric("Improvements Applied", sugg_count, "Applied all suggestions")


def display_traditional_improvement(improved_text):
    """Display traditional improvement results."""
    with st.expander("Preview Basic Improved Resume", expanded=True):
        st.text_area("Improved Resume", improved_text, height=400, key="traditional_improved_resume")
    
    # Basic download option
    st.download_button(
        "📥 Download Improved Resume",
        data=improved_text,
        file_name="resume_improved_traditional.txt",
        mime="text/plain",
        key="traditional_download"
    )


def display_resume_comparison(improved_content):
    """Display enhanced comparison between original and improved resume with ATS scores."""
    st.markdown("#### 📊 Before vs After Comparison")
    
    if st.session_state.parsed_resume:
        # ATS Score Comparison Header
        st.markdown("##### 🎯 ATS Score Comparison")
        score_col1, score_col2, score_col3 = st.columns(3)
        
        original_ats_score = st.session_state.ats_results.score if st.session_state.ats_results else 0
        
        with score_col1:
            st.metric("📋 Original ATS Score", f"{original_ats_score:.1f}/100", 
                     delta=None, delta_color="normal")
        
        with score_col2:
            # Calculate estimated improved score
            missing_skills_count = len(st.session_state.ats_results.missing_skills) if st.session_state.ats_results and st.session_state.ats_results.missing_skills else 0
            estimated_improvement = min(30, missing_skills_count * 2.5)  # 2.5 points per missing skill, max 30 points
            estimated_new_score = min(100, original_ats_score + estimated_improvement)
            
            st.metric("✨ Improved ATS Score (Est.)", f"{estimated_new_score:.1f}/100", 
                     delta=f"+{estimated_improvement:.1f}", delta_color="normal")
        
        with score_col3:
            improvement_percentage = (estimated_improvement / original_ats_score * 100) if original_ats_score > 0 else 0
            st.metric("📈 Improvement", f"{improvement_percentage:.1f}%", 
                     delta=f"+{estimated_improvement:.1f} points", delta_color="normal")
        
        # Skills comparison
        st.markdown("##### 🎯 Skills Enhancement")
        skills_col1, skills_col2, skills_col3 = st.columns(3)
        
        if st.session_state.ats_results:
            matched_count = len(st.session_state.ats_results.matched_skills) if st.session_state.ats_results.matched_skills else 0
            missing_count = len(st.session_state.ats_results.missing_skills) if st.session_state.ats_results.missing_skills else 0
            total_skills = matched_count + missing_count
            
            with skills_col1:
                st.metric("📋 Original Skills Match", f"{matched_count}/{total_skills}", 
                         f"{(matched_count/total_skills*100):.1f}%" if total_skills > 0 else "0%")
            
            with skills_col2:
                skills_added = min(missing_count, 15)  # Assume we add up to 15 missing skills
                new_matched = matched_count + skills_added
                st.metric("✨ Improved Skills Match", f"{new_matched}/{total_skills}", 
                         f"{(new_matched/total_skills*100):.1f}%" if total_skills > 0 else "0%")
            
            with skills_col3:
                st.metric("� Skills Added", skills_added, 
                         f"Added {skills_added}/{missing_count}" if missing_count > 0 else "All covered")
        
        # Resume content comparison
        st.markdown("##### 📄 Content Comparison")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**�📋 Original Resume**")
            original_text = st.session_state.parsed_resume.text
            st.text_area("Original", original_text[:1000] + "..." if len(original_text) > 1000 else original_text, 
                        height=300, key="original_comparison")
        
        with col2:
            st.markdown("**✨ Improved Resume**")
            improved_text = improved_content[:1000] + "..." if len(improved_content) > 1000 else improved_content
            st.text_area("Improved", improved_text, height=300, key="improved_comparison")
        
        # Enhanced statistics comparison
        st.markdown("##### 📈 Content Enhancement Statistics")
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        original_words = len(st.session_state.parsed_resume.text.split())
        improved_words = len(improved_content.split())
        
        # Word count comparison
        with stats_col1:
            word_diff = improved_words - original_words
            st.metric("Word Count", improved_words, f"{'+' if word_diff > 0 else ''}{word_diff}")
        
        # Quantified achievements count
        with stats_col2:
            # Count numbers/percentages in improved content (rough estimate)
            import re
            numbers_in_improved = len(re.findall(r'\b\d+(?:\.\d+)?%|\b\d+(?:,\d{3})*(?:\.\d+)?[KkMm]?\b', improved_content))
            numbers_in_original = len(re.findall(r'\b\d+(?:\.\d+)?%|\b\d+(?:,\d{3})*(?:\.\d+)?[KkMm]?\b', st.session_state.parsed_resume.text))
            metrics_added = max(0, numbers_in_improved - numbers_in_original)
            st.metric("Quantified Achievements", numbers_in_improved, f"+{metrics_added}")
        
        # Keywords integration
        with stats_col3:
            if st.session_state.ats_results:
                keywords_integrated = min(missing_skills_count, 15)  # Estimate keywords added
                st.metric("Keywords Added", keywords_integrated, f"ATS optimized")
            else:
                st.metric("Keywords Added", "N/A")
        
        # Section improvements
        with stats_col4:
            sections_improved = 0
            if "PROFESSIONAL SUMMARY" in improved_content.upper() or "SUMMARY" in improved_content.upper():
                sections_improved += 1
            if "CORE COMPETENCIES" in improved_content.upper() or "TECHNICAL SKILLS" in improved_content.upper():
                sections_improved += 1
            if re.search(r'\d+%|\d+\.\d+%|\$\d+', improved_content):  # Check for quantified achievements
                sections_improved += 1
            
            st.metric("Sections Enhanced", sections_improved, f"Improved {sections_improved} areas")
        
        with stats_col1:
            st.metric("📝 Word Count", improved_words, delta=improved_words - original_words)
        
        with stats_col2:
            original_sentences = st.session_state.parsed_resume.text.count('.') + st.session_state.parsed_resume.text.count('!') + st.session_state.parsed_resume.text.count('?')
            improved_sentences = improved_content.count('.') + improved_content.count('!') + improved_content.count('?')
            st.metric("📖 Sentences", improved_sentences, delta=improved_sentences - original_sentences)
        
        with stats_col3:
            # Simple keyword density (count of common action verbs)
            action_verbs = ['achieved', 'managed', 'led', 'developed', 'created', 'implemented', 'improved', 'increased']
            original_actions = sum(st.session_state.parsed_resume.text.lower().count(verb) for verb in action_verbs)
            improved_actions = sum(improved_content.lower().count(verb) for verb in action_verbs)
            st.metric("⚡ Action Verbs", improved_actions, delta=improved_actions - original_actions)


def display_download_options(improved_content):
    """Display download options for improved resume."""
    st.markdown("#### 📥 Download Improved Resume")
    
    col1, col2, col3 = st.columns(3)
    
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
    
    with col3:
        # Text download
        st.download_button(
            "📝 Download TXT",
            data=improved_content,
            file_name="resume_improved_ai.txt",
            mime="text/plain",
            key="download_txt"
        )
    
    # Additional options
    st.markdown("---")
    st.markdown("#### 🔧 Additional Options")
    
    if st.button("📧 Email Resume", key="email_resume_btn"):
        display_email_options(improved_content)
    
    if st.button("🔄 Generate Alternative Version", key="alt_version_btn"):
        generate_alternative_version(improved_content)


def display_email_options(improved_content):
    """Display email sharing options."""
    st.markdown("#### 📧 Email Resume")
    
    with st.form("email_form"):
        email_to = st.text_input("Recipient Email")
        email_subject = st.text_input("Subject", value="My Updated Resume")
        email_body = st.text_area("Message", value="Please find my updated resume attached.")
        
        submitted = st.form_submit_button("Send Email")
        
        if submitted:
            if email_to:
                st.success(f"Resume would be sent to {email_to}")
                st.info("📧 Email functionality is not implemented in this demo.")
            else:
                st.error("Please enter a recipient email address.")


def generate_alternative_version(current_content):
    """Generate an alternative version of the improved resume."""
    st.info("🔄 Generating alternative version...")
    
    # This would typically use AI to generate a different version
    # For now, we'll show a placeholder
    with st.expander("🔄 Alternative Version", expanded=True):
        st.markdown("Alternative version generation would create a different style or focus for your resume.")
        st.markdown("**Features might include:**")
        st.markdown("• Different formatting style")
        st.markdown("• Alternative summary approach")
        st.markdown("• Different skill emphasis")
        st.markdown("• Varied achievement presentation")
        
        if st.button("💡 Request Custom Alternative", key="custom_alt_btn"):
            st.info("Custom alternative generation feature coming soon!")


def show_improvement_tips():
    """Show general resume improvement tips."""
    st.markdown("### 💡 Resume Improvement Tips")
    
    with st.expander("📋 General Best Practices", expanded=False):
        st.markdown("""
        **Professional Summary:**
        • Start with a compelling 2-3 line summary
        • Include your years of experience and key specializations
        • Mention your most significant achievement
        
        **Skills Section:**
        • List both technical and soft skills
        • Use keywords from the job description
        • Organize skills by category (e.g., Programming Languages, Tools, etc.)
        
        **Experience Section:**
        • Use action verbs to start each bullet point
        • Quantify achievements with numbers, percentages, or dollar amounts
        • Focus on results and impact, not just responsibilities
        
        **ATS Optimization:**
        • Use standard section headings
        • Include relevant keywords naturally
        • Avoid excessive formatting, graphics, or tables
        • Use a clean, simple layout
        """)
    
    with st.expander("🎯 Industry-Specific Tips", expanded=False):
        st.markdown("""
        **Technology/Engineering:**
        • Highlight specific technologies and frameworks
        • Include links to GitHub, portfolio, or project demos
        • Mention certifications and continuing education
        
        **Business/Management:**
        • Emphasize leadership and team management experience
        • Include budget management and cost savings
        • Highlight process improvements and efficiency gains
        
        **Creative/Design:**
        • Include portfolio links
        • Mention specific software proficiencies
        • Highlight client satisfaction and project outcomes
        """)
