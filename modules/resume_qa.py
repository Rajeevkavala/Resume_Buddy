"""
Resume Q&A Module
Handles question and answer generation based on resume content.
"""

import streamlit as st
import time
from embedding_utils import embed_query
from gemini_integration import generate_qa_with_gemini

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


def render_qa_section():
    """Render the resume Q&A section with background processing support."""
    st.markdown('<div class="section-header">❓ Resume Q&A Generator</div>', unsafe_allow_html=True)
    
    if not st.session_state.parsed_resume:
        st.warning("📄 Please upload and analyze a resume first.")
        return
    
    # Check if background Q&A generation was in progress
    if st.session_state.get('qa_in_progress', False):
        with st.spinner("🔄 Background Q&A processing in progress..."):
            time.sleep(0.1)  # Brief pause for visual feedback
        st.info("✅ Q&A generation completed in background!")
        st.session_state.qa_in_progress = False  # Reset flag
        
    # Topic selection
    qa_topic = st.selectbox(
        "🎯 Select Q&A Topic", 
        ["General Resume Questions", "Technical Skills", "Work Experience", 
         "Career Goals", "Project Experience", "Education Background"],
        key="qa_topic_select"
    )
    
    # Check for cached results
    cached_key = f"{qa_topic}_{hash(st.session_state.job_description.strip()) if st.session_state.job_description.strip() else 'no_jd'}"
    
    if (st.session_state.qa_results and 
        getattr(st.session_state, 'last_qa_key', None) == cached_key):
        
        st.markdown("### ❓ Q&A Results (Cached)")
        display_qa_results(st.session_state.qa_results)
        st.info("💡 Results cached from previous generation. Click 'Generate Q&A' to refresh.")
    
    # Generate Q&A button
    if st.button("🚀 Generate Q&A", key="generate_qa_btn"):
        generate_qa_content(qa_topic, cached_key)


def generate_qa_content(qa_topic, cached_key):
    """Generate Q&A content based on topic and resume."""
    parsed = st.session_state.parsed_resume
    
    if st.session_state.gemini_service:
        with st.spinner("🤖 Generating AI-powered Q&A..."):
            try:
                show_toast("🧠 AI is creating personalized Q&A...", "info")
                
                qa_results = generate_qa_with_gemini(
                    st.session_state.gemini_service,
                    parsed.text,
                    qa_topic
                )
                st.session_state.qa_results = qa_results
                st.session_state.last_qa_key = cached_key
                st.session_state.last_qa_topic = qa_topic
                st.session_state.qa_completed = True  # Mark as completed
                
                show_toast("🎉 Q&A generated successfully!", "success")
                
                st.markdown("### ❓ AI-Generated Q&A")
                display_qa_results(qa_results)
                
            except Exception as e:
                show_toast(f"❌ Failed to generate Q&A: {str(e)}", "error")
                st.info("💡 Check your Gemini API key and try again")
    else:
        # Fallback to traditional Q&A generation
        generate_traditional_qa(qa_topic, cached_key)


def generate_traditional_qa(qa_topic, cached_key):
    """Generate traditional Q&A without AI."""
    st.info("🤖 Enable Gemini AI for advanced Q&A generation")
    
    # Traditional Q&A templates based on topic
    traditional_qa = get_traditional_qa_templates(qa_topic)
    
    if traditional_qa:
        st.session_state.qa_results = traditional_qa
        st.session_state.last_qa_key = cached_key
        st.session_state.last_qa_topic = qa_topic
        st.session_state.qa_completed = True  # Mark as completed
        
        st.markdown("### ❓ Template-Based Q&A")
        display_qa_results(traditional_qa)
    else:
        st.warning("No traditional templates available for this topic.")


def get_traditional_qa_templates(topic):
    """Get traditional Q&A templates based on topic."""
    templates = {
        "General Resume Questions": [
            {
                "question": "Tell me about yourself.",
                "answer": "Based on your resume, highlight your key experiences and skills that align with the target role."
            },
            {
                "question": "What are your greatest strengths?",
                "answer": "Focus on the skills and achievements prominently featured in your resume."
            },
            {
                "question": "Where do you see yourself in 5 years?",
                "answer": "Align your career trajectory with the progression shown in your resume."
            }
        ],
        "Technical Skills": [
            {
                "question": "Describe your technical expertise.",
                "answer": "Reference the technical skills and technologies listed in your resume."
            },
            {
                "question": "How do you stay updated with new technologies?",
                "answer": "Mention continuous learning approaches that complement your resume."
            }
        ],
        "Work Experience": [
            {
                "question": "Describe your most significant professional achievement.",
                "answer": "Choose an achievement from your resume and elaborate on the impact."
            },
            {
                "question": "Why are you leaving your current position?",
                "answer": "Focus on growth opportunities that align with your career progression."
            }
        ]
    }
    
    return templates.get(topic, [])


def display_qa_results(qa_results):
    """Display Q&A results in an organized format."""
    if not qa_results:
        st.warning("No Q&A results to display.")
        return
        
    for i, qa in enumerate(qa_results, 1):
        with st.expander(f"❓ Question {i}: {qa.get('question', 'N/A')}", expanded=False):
            st.markdown("**Question:**")
            st.write(qa.get('question', 'N/A'))
            
            st.markdown("**Suggested Answer:**")
            st.write(qa.get('answer', 'N/A'))
            
            if 'tips' in qa:
                st.markdown("**💡 Tips:**")
                for tip in qa['tips']:
                    st.markdown(f"• {tip}")
    
    # Download Q&A option
    st.markdown("---")
    if st.button("📥 Download Q&A as Text", key="download_qa_btn"):
        qa_text = format_qa_for_download(qa_results)
        st.download_button(
            "⬇️ Download Q&A",
            data=qa_text,
            file_name="resume_qa.txt",
            mime="text/plain",
            key="qa_download"
        )


def format_qa_for_download(qa_results):
    """Format Q&A results for download."""
    formatted_text = "RESUME Q&A PREPARATION\n"
    formatted_text += "=" * 50 + "\n\n"
    
    for i, qa in enumerate(qa_results, 1):
        formatted_text += f"QUESTION {i}:\n"
        formatted_text += f"{qa.get('question', 'N/A')}\n\n"
        formatted_text += f"ANSWER:\n"
        formatted_text += f"{qa.get('answer', 'N/A')}\n\n"
        
        if 'tips' in qa:
            formatted_text += "TIPS:\n"
            for tip in qa['tips']:
                formatted_text += f"• {tip}\n"
        
        formatted_text += "-" * 30 + "\n\n"
    
    return formatted_text
