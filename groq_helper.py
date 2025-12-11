"""
Groq AI Helper for skill extraction and search keyword generation.
"""
import os
from groq import Groq
from typing import List
import json
import re

# Initialize Groq client
client = None

def get_client():
    """Get or create Groq client."""
    global client
    if client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        client = Groq(api_key=api_key)
    return client


def generate_search_keywords(num_keywords: int = 10) -> List[str]:
    """
    Use Groq AI to generate relevant job search keywords for AI/ML positions.
    
    Returns:
        List of search keywords/job titles
    """
    prompt = f"""Generate exactly {num_keywords} job search keywords/titles for AI and Machine Learning positions.

IMPORTANT: Every keyword MUST contain the word "AI" explicitly.

Include a mix of:
- Entry to senior level positions (e.g., "AI Engineer", "Senior AI Developer")
- Different AI specializations (e.g., "AI Research Scientist", "AI Solutions Architect")
- Both technical and research roles

Return ONLY a JSON array of strings, no other text. Example format:
["AI Engineer", "Senior AI Developer", "AI Research Scientist"]"""

    response = get_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    
    content = response.choices[0].message.content.strip()
    
    # Parse JSON response
    try:
        # Try to extract JSON array from response
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            keywords = json.loads(match.group())
            return keywords[:num_keywords]
    except json.JSONDecodeError:
        pass
    
    # Fallback keywords if parsing fails
    return [
        "AI Engineer",
        "Machine Learning Engineer", 
        "Data Scientist AI",
        "NLP Engineer",
        "Computer Vision Engineer",
        "Deep Learning Engineer",
        "LLM Developer",
        "AI Research Scientist",
        "MLOps Engineer",
        "Generative AI Developer"
    ][:num_keywords]


def extract_skills(job_description: str) -> List[str]:
    """
    Use Groq AI to dynamically extract skills and tools from a job description.
    
    Args:
        job_description: The full job description text
        
    Returns:
        List of extracted skills/tools
    """
    if not job_description or len(job_description.strip()) < 50:
        return []
    
    # Truncate very long descriptions
    truncated = job_description[:4000] if len(job_description) > 4000 else job_description
    
    prompt = f"""Extract all technical skills, tools, frameworks, programming languages, and technologies mentioned in this job description.

Job Description:
{truncated}

Return ONLY a JSON array of skill/tool names, no other text. Be specific (e.g., "PyTorch" not "deep learning framework").
Include: programming languages, ML frameworks, cloud platforms, databases, tools, libraries, methodologies.
Exclude: soft skills, generic terms like "AI" or "machine learning", job requirements like "5 years experience".

Example format: ["Python", "TensorFlow", "AWS", "Docker", "SQL"]"""

    try:
        response = get_client().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse JSON response
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            skills = json.loads(match.group())
            # Clean and deduplicate
            cleaned = []
            seen = set()
            for skill in skills:
                if isinstance(skill, str):
                    skill_clean = skill.strip()
                    skill_lower = skill_clean.lower()
                    if skill_clean and skill_lower not in seen and len(skill_clean) > 1:
                        cleaned.append(skill_clean)
                        seen.add(skill_lower)
            return cleaned
    except Exception as e:
        print(f"Error extracting skills: {e}")
    
    return []


if __name__ == "__main__":
    # Test the functions
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing keyword generation...")
    keywords = generate_search_keywords(5)
    print(f"Generated keywords: {keywords}")
    
    print("\nTesting skill extraction...")
    sample_desc = """
    We are looking for a Machine Learning Engineer with experience in Python, TensorFlow, 
    and PyTorch. Must have knowledge of AWS, Docker, and Kubernetes. Experience with 
    NLP, transformers, and LLMs is a plus. Familiarity with SQL, PostgreSQL, and 
    data pipelines using Apache Spark is required.
    """
    skills = extract_skills(sample_desc)
    print(f"Extracted skills: {skills}")
