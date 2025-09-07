"""Google Gemini AI integration for enhanced resume analysis and generation.

This module provides wrappers around Google Gemini API for:
- Enhanced skill analysis
- Interview question generation
- Resume improvement suggestions
- Q&A generation
"""
from __future__ import annotations
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    genai = None

@dataclass
class GeminiConfig:
    api_key: str
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_output_tokens: int = 1024

class GeminiService:
    def __init__(self, config: GeminiConfig):
        if not genai:
            raise RuntimeError("google-generativeai not installed. Run: pip install google-generativeai")
        
        self.config = config
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model_name)
    
    def generate_content(self, prompt: str) -> str:
        """Generate content using Gemini API."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                )
            )
            return response.text
        except Exception as e:
            return f"Error generating content: {str(e)}"

def analyze_resume_with_gemini(gemini_service: GeminiService, resume_text: str, jd_text: str, role: str) -> Dict[str, str]:
    """Enhanced resume analysis using Gemini."""
    prompt = f"""
    As an expert HR consultant, analyze this resume against the job description:

    ROLE LEVEL: {role}
    
    RESUME:
    {resume_text[:3000]}
    
    JOB DESCRIPTION:
    {jd_text[:2000]}
    
    Provide analysis in this format:
    
    STRENGTHS:
    - [List 3-5 key strengths]
    
    SKILL GAPS:
    - [List missing skills/requirements]
    
    ATS OPTIMIZATION:
    - [Specific keyword recommendations]
    
    EXPERIENCE ALIGNMENT:
    - [How well experience matches role requirements]
    
    Keep each section concise and actionable.
    """
    
    return {
        "analysis": gemini_service.generate_content(prompt)
    }

def generate_interview_questions_gemini(gemini_service: GeminiService, resume_text: str, jd_text: str, role: str, num_questions: int = 5) -> List[Dict[str, str]]:
    """Generate interview questions using Gemini."""
    prompt = f"""
    As an experienced interviewer, create {num_questions} interview questions for a {role} candidate based on their resume and the job description.

    RESUME SUMMARY:
    {resume_text[:2000]}
    
    JOB DESCRIPTION:
    {jd_text[:1500]}
    
    For each question, provide:
    1. The question
    2. A sample answer based on the resume
    3. What the interviewer is looking for
    
    Format:
    Q1: [Question]
    Sample Answer: [Answer based on resume]
    Looking for: [Key points interviewer wants to hear]
    
    Q2: [Question]
    Sample Answer: [Answer based on resume]
    Looking for: [Key points interviewer wants to hear]
    
    Continue for all {num_questions} questions.
    Focus on behavioral, technical, and role-specific questions.
    """
    
    response = gemini_service.generate_content(prompt)
    
    # Parse response into structured format
    questions = []
    sections = response.split('Q')[1:]  # Split by question markers
    
    for i, section in enumerate(sections[:num_questions], 1):
        lines = section.strip().split('\n')
        question = lines[0].split(':', 1)[-1].strip() if lines else f"Question {i}"
        
        sample_answer = ""
        looking_for = ""
        
        for line in lines:
            if line.startswith('Sample Answer:'):
                sample_answer = line.split(':', 1)[-1].strip()
            elif line.startswith('Looking for:'):
                looking_for = line.split(':', 1)[-1].strip()
        
        questions.append({
            "question": question,
            "sample_answer": sample_answer,
            "looking_for": looking_for
        })
    
    return questions

def improve_resume_with_gemini(gemini_service: GeminiService, resume_text: str, analysis_results: Dict, role: str) -> str:
    """Generate improved resume content using Gemini."""
    prompt = f"""
    As a professional resume writer, improve this resume for a {role} position.

    CURRENT RESUME:
    {resume_text[:3000]}
    
    ANALYSIS INSIGHTS:
    {analysis_results.get('analysis', '')[:1000]}
    
    Create an improved version that:
    1. Adds a compelling professional summary
    2. Reorganizes content for better flow
    3. Uses stronger action verbs and quantified achievements
    4. Optimizes for ATS keywords
    5. Maintains all original information while enhancing presentation
    
    Structure the improved resume as:
    
    PROFESSIONAL SUMMARY
    [2-3 sentences highlighting key value proposition]
    
    CORE COMPETENCIES
    [Bullet points of key skills]
    
    PROFESSIONAL EXPERIENCE
    [Improved job descriptions with quantified achievements]
    
    [Include other sections as appropriate]
    
    Make it compelling and professional while keeping all factual information from the original.
    """
    
    return gemini_service.generate_content(prompt)

def generate_qa_with_gemini(gemini_service: GeminiService, resume_text: str, topic: str) -> Dict[str, str]:
    """Generate Q&A based on resume content using Gemini."""
    prompt = f"""
    Based on this resume, generate a comprehensive Q&A about {topic}:

    RESUME:
    {resume_text[:2500]}
    
    Create 5 detailed Q&A pairs that help the candidate understand and articulate their experience in {topic}.
    
    Format:
    Q: [Question]
    A: [Detailed answer based on resume content]
    
    Focus on practical, interview-relevant questions.
    """
    
    response = gemini_service.generate_content(prompt)
    return {"qa_content": response}

def get_gemini_service(api_key: Optional[str] = None) -> Optional[GeminiService]:
    """Initialize Gemini service with API key."""
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return None
    
    config = GeminiConfig(api_key=api_key)
    try:
        return GeminiService(config)
    except Exception:
        return None
