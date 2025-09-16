"""
Interview Questions Module
Handles interview question generation and preparation.
"""

import streamlit as st
import time
from interview_agent import generate_interview_questions, generate_sample_answers
from gemini_integration import generate_interview_questions_gemini

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


def render_interview_section():
    """Render the interview questions section with background processing support."""
    st.markdown('<div class="section-header">🎤 Interview Questions Generator</div>', unsafe_allow_html=True)
    
    if not st.session_state.parsed_resume:
        st.warning("📄 Please upload and analyze a resume first.")
        return
    
    # Check if background interview generation was in progress
    if st.session_state.get('interview_in_progress', False):
        with st.spinner("🔄 Background interview questions processing in progress..."):
            time.sleep(0.1)  # Brief pause for visual feedback
        st.info("✅ Interview questions generation completed in background!")
        st.session_state.interview_in_progress = False  # Reset flag
    
    # Interview configuration
    col1, col2 = st.columns(2)
    
    with col1:
        interview_type = st.selectbox(
            "🎯 Interview Type",
            ["Technical Interview", "Behavioral Interview", "Leadership Interview", 
             "General Interview", "Industry-Specific"],
            key="interview_type_select"
        )
    
    with col2:
        difficulty_level = st.selectbox(
            "📈 Difficulty Level",
            ["Entry Level", "Mid Level", "Senior Level", "Executive Level"],
            key="difficulty_level_select"
        )
    
    # Number of questions
    num_questions = st.slider("🔢 Number of Questions", 5, 20, 10, key="num_questions_slider")
    
    # Check for cached results
    cached_key = f"{interview_type}_{difficulty_level}_{num_questions}_{hash(st.session_state.job_description.strip()) if st.session_state.job_description.strip() else 'no_jd'}"
    
    if (st.session_state.interview_questions and 
        getattr(st.session_state, 'last_interview_key', None) == cached_key):
        
        st.markdown("### 🎤 Interview Questions (Cached)")
        display_interview_questions(st.session_state.interview_questions)
        st.info("💡 Results cached from previous generation. Click 'Generate Questions' to refresh.")
    
    # Generate questions button
    if st.button("🚀 Generate Interview Questions", key="generate_interview_btn"):
        generate_interview_content(interview_type, difficulty_level, num_questions, cached_key)


def generate_interview_content(interview_type, difficulty_level, num_questions, cached_key):
    """Generate interview questions based on parameters."""
    parsed = st.session_state.parsed_resume
    
    if st.session_state.gemini_service:
        with st.spinner("🤖 Generating AI-powered interview questions..."):
            try:
                show_toast("🎯 Creating personalized interview questions...", "info")
                
                questions = generate_interview_questions_gemini(
                    st.session_state.gemini_service,
                    parsed.text,
                    st.session_state.job_description,
                    st.session_state.selected_role
                )
                st.session_state.interview_questions = questions
                st.session_state.last_interview_key = cached_key
                st.session_state.interview_completed = True  # Mark as completed
                
                show_toast("🎉 Interview questions generated successfully!", "success")
                
                st.markdown("### 🎤 AI-Generated Interview Questions")
                display_interview_questions(questions)
                
            except Exception as e:
                show_toast(f"❌ Failed to generate interview questions: {str(e)}", "error")
                st.info("💡 Check your Gemini API key and try again")
    else:
        # Fallback to traditional interview questions
        generate_traditional_interview(interview_type, difficulty_level, num_questions, cached_key)


def get_basic_interview_questions_by_type(interview_type, num_questions):
    """Get basic interview questions by type."""
    question_templates = {
        "Technical Interview": [
            "Describe your technical expertise and key technologies you've worked with.",
            "How do you approach problem-solving in technical challenges?",
            "Can you walk me through a challenging technical project you've completed?",
            "How do you stay updated with new technologies and industry trends?",
            "Describe a time when you had to learn a new technology quickly."
        ],
        "Behavioral Interview": [
            "Tell me about a time when you faced a significant challenge at work.",
            "Describe a situation where you had to work with a difficult team member.",
            "How do you handle stress and pressure in the workplace?",
            "Tell me about a time when you made a mistake and how you handled it.",
            "Describe a situation where you had to meet a tight deadline."
        ],
        "Leadership Interview": [
            "Describe your leadership style and how you motivate team members.",
            "Tell me about a time when you had to make a difficult decision as a leader.",
            "How do you handle conflict within your team?",
            "Describe a situation where you had to implement change in your organization.",
            "How do you develop and mentor team members?"
        ],
        "General Interview": [
            "Tell me about yourself.",
            "Why are you interested in this position?",
            "What are your greatest strengths?",
            "What are your areas for improvement?",
            "Where do you see yourself in 5 years?"
        ],
        "Industry-Specific": [
            "What industry trends do you think will impact our business?",
            "How do you stay current with industry developments?",
            "What do you think sets our company apart in the industry?",
            "How would you contribute to our company's goals?",
            "What challenges do you see facing our industry?"
        ]
    }
    
    questions = question_templates.get(interview_type, question_templates["General Interview"])
    # Repeat questions if needed to reach num_questions
    while len(questions) < num_questions:
        questions.extend(question_templates.get(interview_type, question_templates["General Interview"]))
    
    return questions[:num_questions]


def generate_traditional_interview(interview_type, difficulty_level, num_questions, cached_key):
    """Generate traditional interview questions without AI."""
    st.info("🤖 Enable Gemini AI for advanced interview question generation")
    
    parsed = st.session_state.parsed_resume
    
    with st.spinner("📋 Generating traditional interview questions..."):
        try:
            # Use existing interview_agent functions
            if st.session_state.vector_store:
                questions = generate_interview_questions(
                    st.session_state.vector_store, 
                    num_questions
                )
                
                # Generate sample answers
                sample_answers = generate_sample_answers(
                    st.session_state.vector_store,
                    questions
                )
                
                questions_with_answers = []
                for i, question in enumerate(questions):
                    answer = sample_answers[i] if i < len(sample_answers) else "Please provide specific examples from your experience."
                    questions_with_answers.append({
                        "question": question,
                        "sample_answer": answer,
                        "type": interview_type,
                        "difficulty": difficulty_level
                    })
            else:
                # Fallback to basic questions without vector store
                basic_questions = get_basic_interview_questions_by_type(interview_type, num_questions)
                questions_with_answers = []
                for question in basic_questions:
                    questions_with_answers.append({
                        "question": question,
                        "sample_answer": "Please provide specific examples from your experience that demonstrate your skills and achievements.",
                        "type": interview_type,
                        "difficulty": difficulty_level
                    })
            
            st.session_state.interview_questions = questions_with_answers
            st.session_state.last_interview_key = cached_key
            st.session_state.interview_completed = True  # Mark as completed
            
            st.markdown("### 🎤 Traditional Interview Questions")
            display_interview_questions(questions_with_answers)
            
        except Exception as e:
            st.error(f"❌ Failed to generate traditional interview questions: {str(e)}")


def display_interview_questions(questions):
    """Display interview questions in an organized format."""
    if not questions:
        st.warning("No interview questions to display.")
        return
    
    # Question statistics
    st.markdown("### 📊 Questions Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📝 Total Questions", len(questions))
    with col2:
        question_types = set(q.get('type', 'General') for q in questions)
        st.metric("🎯 Question Types", len(question_types))
    with col3:
        avg_length = sum(len(q.get('question', '').split()) for q in questions) / len(questions) if questions else 0
        st.metric("📏 Avg Question Length", f"{avg_length:.0f} words")
    
    # Display questions
    st.markdown("### ❓ Interview Questions")
    
    for i, question_data in enumerate(questions, 1):
        question = question_data.get('question', 'N/A')
        
        with st.expander(f"🎤 Question {i}: {question[:80]}{'...' if len(question) > 80 else ''}", expanded=False):
            st.markdown("**Question:**")
            st.write(question)
            
            # Question metadata
            if 'type' in question_data:
                st.markdown(f"**Type:** {question_data['type']}")
            if 'difficulty' in question_data:
                st.markdown(f"**Difficulty:** {question_data['difficulty']}")
            
            # Sample answer
            if 'sample_answer' in question_data:
                st.markdown("**Sample Answer:**")
                st.write(question_data['sample_answer'])
            elif 'answer' in question_data:
                st.markdown("**Sample Answer:**")
                st.write(question_data['answer'])
            
            # Tips if available
            if 'tips' in question_data:
                st.markdown("**💡 Tips:**")
                for tip in question_data['tips']:
                    st.markdown(f"• {tip}")
    
    # Practice mode
    st.markdown("---")
    st.markdown("### 🎯 Practice Mode")
    
    if st.button("🎮 Start Practice Session", key="practice_mode_btn"):
        start_practice_session(questions)
    
    # Download questions
    if st.button("📥 Download Questions", key="download_questions_btn"):
        questions_text = format_questions_for_download(questions)
        st.download_button(
            "⬇️ Download Interview Questions",
            data=questions_text,
            file_name="interview_questions.txt",
            mime="text/plain",
            key="questions_download"
        )


def start_practice_session(questions):
    """Start an interactive practice session."""
    if 'practice_mode' not in st.session_state:
        st.session_state.practice_mode = True
        st.session_state.current_question_index = 0
        st.session_state.practice_responses = []
    
    if st.session_state.practice_mode and questions:
        current_idx = st.session_state.current_question_index
        
        if current_idx < len(questions):
            question = questions[current_idx]
            
            st.markdown(f"### Question {current_idx + 1} of {len(questions)}")
            st.write(question.get('question', 'N/A'))
            
            # Response area
            response = st.text_area(
                "Your Answer:",
                key=f"practice_response_{current_idx}",
                height=150
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("⏭️ Next Question", key=f"next_{current_idx}"):
                    st.session_state.practice_responses.append(response)
                    st.session_state.current_question_index += 1
                    st.rerun()
            
            with col2:
                if st.button("💡 Show Sample Answer", key=f"show_answer_{current_idx}"):
                    if 'sample_answer' in question:
                        st.info(f"Sample Answer: {question['sample_answer']}")
                    elif 'answer' in question:
                        st.info(f"Sample Answer: {question['answer']}")
            
            with col3:
                if st.button("🛑 End Practice", key=f"end_practice_{current_idx}"):
                    st.session_state.practice_mode = False
                    st.success("Practice session completed!")
                    st.rerun()
        else:
            st.success("🎉 Practice session completed!")
            st.markdown("### 📊 Practice Summary")
            st.write(f"You answered {len(st.session_state.practice_responses)} questions.")
            
            if st.button("🔄 Start New Session", key="new_practice_session"):
                st.session_state.practice_mode = False
                st.session_state.current_question_index = 0
                st.session_state.practice_responses = []
                st.rerun()


def format_questions_for_download(questions):
    """Format interview questions for download."""
    formatted_text = "INTERVIEW QUESTIONS PREPARATION\n"
    formatted_text += "=" * 50 + "\n\n"
    
    for i, question_data in enumerate(questions, 1):
        formatted_text += f"QUESTION {i}:\n"
        formatted_text += f"{question_data.get('question', 'N/A')}\n\n"
        
        if 'type' in question_data:
            formatted_text += f"TYPE: {question_data['type']}\n"
        if 'difficulty' in question_data:
            formatted_text += f"DIFFICULTY: {question_data['difficulty']}\n"
        
        if 'sample_answer' in question_data:
            formatted_text += f"\nSAMPLE ANSWER:\n"
            formatted_text += f"{question_data['sample_answer']}\n"
        elif 'answer' in question_data:
            formatted_text += f"\nSAMPLE ANSWER:\n"
            formatted_text += f"{question_data['answer']}\n"
        
        if 'tips' in question_data:
            formatted_text += "\nTIPS:\n"
            for tip in question_data['tips']:
                formatted_text += f"• {tip}\n"
        
        formatted_text += "\n" + "-" * 50 + "\n\n"
    
    return formatted_text
