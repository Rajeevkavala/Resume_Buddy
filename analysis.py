"""Resume analysis utilities: skills extraction, ATS scoring, strengths/weaknesses.

This module uses lightweight heuristics plus optional spaCy NER.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Set, Dict, Tuple

try:
    import spacy  # type: ignore
except Exception:  # pragma: no cover
    spacy = None  # type: ignore

# Comprehensive skill lexicon (extendable)
BASE_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell',
    
    # Web Frameworks & Libraries
    'react', 'angular', 'vue', 'svelte', 'django', 'flask', 'fastapi', 'express', 'node', 'nodejs', 'spring', 'laravel', 'rails', 'asp.net', 'blazor',
    
    # Databases
    'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'cassandra', 'elasticsearch', 'sqlite', 'oracle', 'mssql', 'dynamodb', 'firebase',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'gitlab', 'github', 'ci/cd', 'nginx', 'apache', 'linux', 'unix', 'windows',
    
    # Data Science & ML
    'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'matplotlib', 'seaborn', 'jupyter', 'anaconda', 'ml', 'machine learning', 'deep learning', 'nlp', 'opencv', 'spark', 'hadoop', 'kafka', 'airflow',
    
    # Tools & Technologies
    'git', 'svn', 'jira', 'confluence', 'slack', 'teams', 'figma', 'adobe', 'photoshop', 'excel', 'powerbi', 'tableau', 'looker', 'grafana',
    
    # API & Web Technologies
    'rest', 'restful', 'graphql', 'soap', 'json', 'xml', 'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind', 'webpack', 'vite', 'npm', 'yarn',
    
    # Methodologies & Practices
    'agile', 'scrum', 'kanban', 'devops', 'tdd', 'bdd', 'microservices', 'api', 'mvp', 'lean', 'waterfall',
    
    # Mobile Development
    'ios', 'android', 'react native', 'flutter', 'xamarin', 'cordova', 'ionic',
    
    # Testing
    'junit', 'pytest', 'jest', 'selenium', 'cypress', 'postman', 'unit testing', 'integration testing', 'automation testing'
}

SKILL_REGEX = re.compile(r"\b([A-Za-z][A-Za-z+#.]{1,31}(?:\s+[A-Za-z][A-Za-z+#.]{1,31})?)\b")

STOPWORDS = {
    'and','or','the','a','an','for','to','in','on','with','of','by','at','is','are','this','that','from','as','it','be','using','used','use'
}

@dataclass
class SkillAnalysis:
    strengths: Set[str]
    gaps: Set[str]
    matched_ratio: float

@dataclass
class ATSScore:
    score: float
    matched_skills: Set[str]
    missing_skills: Set[str]
    detail: Dict[str, float]


def normalize_token(tok: str) -> str:
    return tok.lower().strip()


def extract_candidate_skills(text: str) -> Set[str]:
    # Convert text to lowercase for matching
    text_lower = text.lower()
    tokens = set()
    
    # First, try to match multi-word skills directly
    multi_word_skills = {
        'machine learning', 'deep learning', 'data analysis', 'web development',
        'software development', 'unit testing', 'integration testing', 'automation testing',
        'rest api', 'react native', 'node.js', 'asp.net', 'ci/cd'
    }
    
    for skill in multi_word_skills:
        if skill in text_lower:
            tokens.add(skill)
    
    # Then extract single words and match against base skills
    for match in SKILL_REGEX.finditer(text):
        token = normalize_token(match.group(1))
        if token in STOPWORDS or len(token) <= 1:
            continue
        
        # Check if token is in our base skills
        if token in BASE_SKILLS:
            tokens.add(token)
        
        # Handle some special cases
        if 'postgres' in token.lower():
            tokens.add('postgresql')
        if 'js' in token and len(token) <= 3:
            tokens.add('javascript')
        if 'node' in token:
            tokens.add('nodejs')
    
    # Additional direct text matching for common variations
    skill_variations = {
        'python': ['python', 'py'],
        'javascript': ['javascript', 'js', 'ecmascript'],
        'postgresql': ['postgresql', 'postgres', 'psql'],
        'mysql': ['mysql', 'my sql'],
        'aws': ['aws', 'amazon web services'],
        'docker': ['docker', 'containerization'],
        'kubernetes': ['kubernetes', 'k8s'],
        'react': ['react', 'reactjs', 'react.js'],
        'django': ['django'],
        'flask': ['flask'],
        'git': ['git', 'version control'],
        'agile': ['agile', 'scrum'],
        'rest': ['rest', 'restful', 'rest api'],
        'ci/cd': ['ci/cd', 'continuous integration', 'continuous deployment']
    }
    
    for skill, variations in skill_variations.items():
        for variation in variations:
            if variation in text_lower:
                tokens.add(skill)
                break
    
    return tokens


def enrich_with_spacy(text: str, skills: Set[str]) -> Set[str]:
    if not spacy:
        return skills
    try:
        nlp = spacy.load('en_core_web_sm')  # type: ignore
    except Exception:
        return skills
    doc = nlp(text)
    ents = {normalize_token(ent.text) for ent in doc.ents if ent.label_ in {'ORG','PRODUCT','LANGUAGE','SKILL'} }
    return skills.union(ents.intersection(BASE_SKILLS))


def analyze_skills(resume_text: str, jd_text: str) -> SkillAnalysis:
    resume_skills = extract_candidate_skills(resume_text)
    jd_skills = extract_candidate_skills(jd_text)
    resume_skills = enrich_with_spacy(resume_text, resume_skills)
    jd_skills = enrich_with_spacy(jd_text, jd_skills)
    strengths = resume_skills.intersection(jd_skills)
    gaps = jd_skills - resume_skills
    matched_ratio = (len(strengths) / len(jd_skills)) if jd_skills else 0.0
    return SkillAnalysis(strengths=strengths, gaps=gaps, matched_ratio=matched_ratio)


def compute_ats_score(resume_text: str, jd_text: str) -> ATSScore:
    analysis = analyze_skills(resume_text, jd_text)
    # naive weighting
    coverage = analysis.matched_ratio
    # keyword density
    total_tokens = len(resume_text.split()) or 1
    matched_tokens = sum(resume_text.lower().count(skill) for skill in analysis.strengths)
    density = matched_tokens / total_tokens
    score = (0.7 * coverage) + (0.3 * min(density * 5, 1.0))
    detail = {
        'coverage': coverage,
        'density': density
    }
    return ATSScore(score=round(score * 100, 2), matched_skills=analysis.strengths, missing_skills=analysis.gaps, detail=detail)


def improvement_suggestions(resume_text: str, analysis: SkillAnalysis) -> List[str]:
    suggestions: List[str] = []
    if analysis.gaps:
        suggestions.append(f"Consider adding or demonstrating experience with: {', '.join(sorted(analysis.gaps))} (if applicable).")
    if len(resume_text.split()) < 200:
        suggestions.append("Resume seems short; consider expanding achievements with quantified impact.")
    if 'achieved' not in resume_text.lower():
        suggestions.append("Include action verbs (achieved, led, improved, optimized) to emphasize impact.")
    if resume_text.count('\n\n') < 2:
        suggestions.append("Add clear section breaks (Experience, Skills, Education).")
    if not any(w in resume_text.lower() for w in ['%','increased','reduced','improved']):
        suggestions.append("Quantify results with metrics or percentages.")
    if not suggestions:
        suggestions.append("Resume structure and keywords look solid. Fine-tune bullet specificity for further impact.")
    return suggestions
