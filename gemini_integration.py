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

def improve_resume_with_gemini(gemini_service: GeminiService, resume_text: str, analysis_data: Dict, 
                               improvement_focus: List[str], enhancement_level: str, role: str) -> str:
    """Generate improved resume content using Gemini with comprehensive analysis data."""
    
    try:
        # Prepare focus areas description
        focus_description = ", ".join(improvement_focus) if improvement_focus else "general improvement"
        
        # Prepare missing skills list with safe handling
        missing_skills = analysis_data.get('missing_skills', [])
        if isinstance(missing_skills, set):
            missing_skills = list(missing_skills)
        elif missing_skills is None:
            missing_skills = []
        missing_skills_text = ", ".join(missing_skills[:15]) if missing_skills else "None identified"
        
        # Prepare matched skills with safe handling
        matched_skills = analysis_data.get('matched_skills', [])
        if isinstance(matched_skills, set):
            matched_skills = list(matched_skills)
        elif matched_skills is None:
            matched_skills = []
        matched_skills_text = ", ".join(matched_skills[:10]) if matched_skills else "None identified"
        
        # Prepare strengths and gaps with safe handling
        strengths = analysis_data.get('strengths', [])
        if isinstance(strengths, set):
            strengths = list(strengths)
        elif strengths is None:
            strengths = []
        
        gaps = analysis_data.get('gaps', [])
        if isinstance(gaps, set):
            gaps = list(gaps)
        elif gaps is None:
            gaps = []
        
        prompt = f"""As an expert resume writer and career coach, improve this resume for a {role} position with {enhancement_level.lower()}.

CURRENT RESUME:
{resume_text[:3000]}

CRITICAL ANALYSIS DATA:
- Current ATS Score: {analysis_data.get('ats_score', 0):.1f}/100 (MUST IMPROVE TO 75+)
- Matched Skills: {matched_skills_text}
- MISSING CRITICAL SKILLS (MUST ADD): {missing_skills_text}
- Key Strengths to Highlight: {', '.join(strengths[:5])[:300] if strengths else 'None identified'}
- Skill Gaps to Address: {', '.join(gaps[:5])[:300] if gaps else 'None identified'}

AI ANALYSIS INSIGHTS:
{analysis_data.get('ai_analysis', '')[:800]}

IMPROVEMENT FOCUS: {focus_description}

TARGET JOB KEYWORDS (MUST INCLUDE):
{analysis_data.get('job_description', '')[:500]}

MANDATORY REQUIREMENTS:
1. **INTEGRATE ALL MISSING SKILLS**: Every missing skill must be naturally woven into existing experience sections
2. **ADD QUANTIFIED ACHIEVEMENTS**: Include specific metrics like "increased efficiency by 25%", "managed budget of $500K", "reduced processing time by 40%", "achieved 95% customer satisfaction"
3. **USE POWER METRICS**: Revenue generated, cost savings, time reductions, percentage improvements, team size managed, projects completed
4. **ATS OPTIMIZATION**: Include exact keywords from job description naturally throughout the resume
5. **PROFESSIONAL IMPACT**: Every bullet point should demonstrate measurable business value

QUANTIFICATION EXAMPLES TO INCLUDE:
- Performance improvements: "Enhanced system performance by 30%"
- Time savings: "Reduced processing time from 4 hours to 1.5 hours (62.5% improvement)"
- Revenue/Cost: "Generated $2.3M in revenue" or "Saved company $150K annually"
- Quality metrics: "Achieved 99.2% accuracy rate" or "Maintained 4.8/5 customer rating"
- Scale metrics: "Managed team of 12 developers" or "Processed 10,000+ transactions daily"
- Project success: "Delivered 15 projects on time and under budget"

MISSING SKILLS INTEGRATION STRATEGY:
For each missing skill in [{missing_skills_text}]:
- Add to Technical Skills/Core Competencies section
- Integrate naturally into 2-3 job descriptions where relevant
- Include in professional summary if it's a core skill
- Mention in context of specific achievements or projects

ENHANCEMENT LEVEL INSTRUCTIONS:
{"- Add 3-5 quantified achievements per role, integrate 100% of missing skills, create compelling professional summary" if enhancement_level == "Light Enhancement" else
 "- Add 5-7 quantified achievements per role, restructure for impact, enhance all sections with metrics" if enhancement_level == "Moderate Enhancement" else
 "- Complete overhaul with 7-10 quantified achievements per role, new sections, strategic repositioning of all content"}

REQUIRED STRUCTURE:

**PROFESSIONAL SUMMARY**
[Compelling 3-4 lines incorporating missing skills and quantified value proposition]

**CORE COMPETENCIES / TECHNICAL SKILLS**
[All missing skills + existing skills, organized by category]

**PROFESSIONAL EXPERIENCE**
[Each role with 5-8 quantified bullet points showing measurable impact]

**[ADDITIONAL SECTIONS AS APPROPRIATE]**
[Projects, Education, Certifications - all with quantified achievements where possible]

CRITICAL SUCCESS CRITERIA:
- ATS Score potential: 75+ (by including all missing skills and job keywords)
- Every bullet point has a number, percentage, or measurable outcome
- All missing skills are naturally integrated
- Professional summary mentions 3-5 key missing skills
- Each job role shows 5-8 quantified achievements
- Uses strong action verbs: achieved, delivered, optimized, generated, reduced, improved, managed, led

QUALITY CHECKLIST:
✓ All {len(missing_skills) if missing_skills else 0} missing skills integrated
✓ Minimum 20+ quantified achievements across all roles
✓ Professional summary includes top 3-5 missing skills
✓ Every job description has measurable outcomes
✓ ATS keywords naturally distributed throughout
✓ Strong action verbs in every bullet point
✓ Business impact clearly demonstrated

Return the complete improved resume in markdown format with clear section headers."""
        
        return gemini_service.generate_content(prompt)
    
    except Exception as e:
        # If there's any error in data processing, return a safe error message
        raise Exception(f"Data processing error in resume improvement: {str(e)}")

def generate_qa_with_gemini(gemini_service: GeminiService, resume_text: str, topic: str) -> List[Dict[str, str]]:
    """Generate Q&A based on resume content using Gemini."""
    prompt = f"""
    Based on this resume, generate exactly 5 Q&A pairs about {topic}.

    RESUME:
    {resume_text[:2500]}
    
    Create 5 detailed Q&A pairs that help the candidate understand and articulate their experience in {topic}.
    
    IMPORTANT: Return ONLY a JSON array with this exact format:
    [
        {{
            "question": "Question text here",
            "answer": "Detailed answer based on resume content"
        }},
        {{
            "question": "Next question",
            "answer": "Next answer"
        }}
    ]
    
    Focus on practical, interview-relevant questions. Make sure the JSON is valid and properly formatted.
    """
    
    try:
        response = gemini_service.generate_content(prompt)
        # Try to parse the JSON response
        import json
        import re
        
        # Extract JSON from response if it contains other text
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            qa_list = json.loads(json_str)
            return qa_list
        else:
            # Fallback: parse Q: A: format
            return parse_qa_text_format(response)
            
    except Exception as e:
        print(f"Error parsing Gemini Q&A response: {e}")
        # Return fallback Q&A
        return generate_fallback_qa(topic)


def parse_qa_text_format(text: str) -> List[Dict[str, str]]:
    """Parse Q&A from text format."""
    qa_pairs = []
    lines = text.split('\n')
    current_question = ""
    current_answer = ""
    
    for line in lines:
        line = line.strip()
        if line.startswith('Q:') or line.startswith('Question'):
            if current_question and current_answer:
                qa_pairs.append({
                    "question": current_question.strip(),
                    "answer": current_answer.strip()
                })
            current_question = line.replace('Q:', '').replace('Question:', '').strip()
            current_answer = ""
        elif line.startswith('A:') or line.startswith('Answer'):
            current_answer = line.replace('A:', '').replace('Answer:', '').strip()
        elif current_answer and line:
            current_answer += " " + line
    
    # Add the last Q&A pair
    if current_question and current_answer:
        qa_pairs.append({
            "question": current_question.strip(),
            "answer": current_answer.strip()
        })
    
    return qa_pairs[:5]  # Return max 5 pairs


def generate_fallback_qa(topic: str) -> List[Dict[str, str]]:
    """Generate fallback Q&A when Gemini fails."""
    fallback_qa = {
        "General Resume Questions": [
            {
                "question": "Tell me about yourself and your background.",
                "answer": "Based on your resume, highlight your key experiences, skills, and achievements that make you a strong candidate for this role."
            },
            {
                "question": "What are your key strengths?",
                "answer": "Focus on the technical and soft skills prominently featured in your resume and provide specific examples."
            }
        ],
        "Technical Skills": [
            {
                "question": "Describe your technical expertise and experience.",
                "answer": "Reference the programming languages, tools, and technologies listed in your resume with specific project examples."
            },
            {
                "question": "How do you approach learning new technologies?",
                "answer": "Discuss your continuous learning approach and how you've applied new skills in your projects."
            }
        ]
    }
    
    return fallback_qa.get(topic, [
        {
            "question": f"Tell me about your experience with {topic}.",
            "answer": "Based on your resume, provide specific examples and achievements related to this topic."
        }
    ])

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
