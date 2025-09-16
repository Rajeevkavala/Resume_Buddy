import streamlit as st


def clear_all_data():
    """Clear all session data including uploads, inputs, analysis, and flags.

    This resets the file uploader, job description, analysis/Q&A/interview/improvement
    results, background flags, and cached data. Returns True on success.
    """
    keys_to_clear = [
        # Core data
        'parsed_resume', 'vector_store', 'analysis_results', 'ats_results', 'skill_analysis',
        'improvement_suggestions', 'interview_questions', 'qa_results',
        'improved_resume_content', 'improved_resume',
        # Inputs and widgets
        'job_description', 'job_description_input', 'resume_file_uploader',
        'gemini_api_key_input',
        # Hashes / memo
        'last_analysis_hash', 'last_qa_key', 'last_interview_key', 'last_improvement_key',
        'last_jd_hash', 'last_qa_topic',
        # Background processing states
        'analysis_in_progress', 'qa_in_progress', 'interview_in_progress', 'improvement_in_progress',
        # Completion flags
        'analysis_completed', 'qa_completed', 'interview_completed', 'improvement_completed',
        # Services and persistence
        'gemini_service', 'session_id', 'data_hash',
        # UI helpers
        'improved_resume_display_container', 'confirm_clear'
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            # Reset string inputs to empty string, others to None for cleanliness
            if key in {'job_description', 'job_description_input', 'gemini_api_key_input'}:
                st.session_state[key] = ""
            elif key == 'resume_file_uploader':
                st.session_state[key] = None
            else:
                st.session_state[key] = None

    # Reset defaults for sidebar controls and navigation
    st.session_state.selected_role = "Mid-level"
    st.session_state.use_ocr = False
    st.session_state.use_gemini_ai = True
    st.session_state.current_section = "Dashboard"

    # Bump nonce to reset widgets that depend on it (e.g., file_uploader key)
    try:
        st.session_state['resume_uploader_nonce'] = (
            st.session_state.get('resume_uploader_nonce', 0) + 1
        )
    except Exception:
        st.session_state['resume_uploader_nonce'] = 1

    # Clear any cached data
    try:
        st.cache_data.clear()
    except Exception:
        pass

    return True
