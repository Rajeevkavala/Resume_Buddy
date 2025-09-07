#!/usr/bin/env python3
"""Test script to verify the analysis functions are working properly."""

from analysis import analyze_skills, compute_ats_score, improvement_suggestions

# Sample resume text
sample_resume = """
John Doe
Senior Software Engineer

EXPERIENCE:
Software Engineer at TechCorp (2020-2023)
- Developed web applications using Python and Django
- Worked with PostgreSQL databases and implemented REST APIs
- Used Git for version control and Docker for containerization
- Collaborated in Agile development environment

SKILLS:
- Programming: Python, JavaScript, Java
- Frameworks: Django, React, Node.js
- Databases: PostgreSQL, MySQL
- Tools: Git, Docker, AWS
- Methodologies: Agile, CI/CD

EDUCATION:
Bachelor of Science in Computer Science
"""

# Sample job description
sample_jd = """
We are looking for a Senior Python Developer with the following skills:
- Strong experience in Python programming
- Experience with Django or Flask frameworks
- Knowledge of PostgreSQL and database design
- Experience with AWS cloud services
- Understanding of Docker and containerization
- Knowledge of Git version control
- Experience with REST API development
- Agile development experience
- Knowledge of CI/CD pipelines
- Experience with React for frontend development
"""

def test_analysis():
    print("Testing Resume Analysis Functions...")
    print("=" * 50)
    
    # Import the extraction function for debugging
    from analysis import extract_candidate_skills
    
    # Test skill extraction first
    print("0. Testing Skill Extraction...")
    resume_skills = extract_candidate_skills(sample_resume)
    jd_skills = extract_candidate_skills(sample_jd)
    print(f"   Resume Skills Detected: {resume_skills}")
    print(f"   JD Skills Detected: {jd_skills}")
    print()
    
    # Test skills analysis
    print("1. Testing Skills Analysis...")
    analysis = analyze_skills(sample_resume, sample_jd)
    print(f"   Strengths: {analysis.strengths}")
    print(f"   Gaps: {analysis.gaps}")
    print(f"   Match Ratio: {analysis.matched_ratio:.2%}")
    print()
    
    # Test ATS scoring
    print("2. Testing ATS Scoring...")
    ats = compute_ats_score(sample_resume, sample_jd)
    print(f"   ATS Score: {ats.score}/100")
    print(f"   Matched Skills: {ats.matched_skills}")
    print(f"   Missing Skills: {ats.missing_skills}")
    print(f"   Details: {ats.detail}")
    print()
    
    # Test improvement suggestions
    print("3. Testing Improvement Suggestions...")
    suggestions = improvement_suggestions(sample_resume, analysis)
    for i, sug in enumerate(suggestions, 1):
        print(f"   {i}. {sug}")
    print()
    
    print("Analysis test completed successfully!")
    return analysis, ats, suggestions

if __name__ == "__main__":
    test_analysis()
