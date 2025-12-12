"""
Groq AI Helper for search keyword generation and discovering NEW skills.
"""
import os
from groq import Groq
from typing import List, Set
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
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            keywords = json.loads(match.group())
            return keywords[:num_keywords]
    except json.JSONDecodeError:
        pass
    
    # Fallback keywords
    return [
        "AI Engineer",
        "AI Developer", 
        "AI Research Scientist",
        "AI Solutions Architect",
        "AI Product Manager",
        "Senior AI Engineer",
        "AI/ML Engineer",
        "AI Specialist",
        "AI Consultant",
        "AI Team Lead"
    ][:num_keywords]


def discover_new_skills(job_descriptions: List[str], known_skills: Set[str]) -> List[str]:
    """
    Use Groq AI to discover NEW skills/tools from job descriptions
    that are NOT in the known skills list.
    
    This is called once with a SAMPLE of job descriptions to find
    new skills to add to the predefined list.
    
    Args:
        job_descriptions: List of job description texts (sample of ~10-20)
        known_skills: Set of skills we already know about
        
    Returns:
        List of newly discovered skills not in known_skills
    """
    if not job_descriptions:
        return []
    
    # Combine sample descriptions (limit to avoid token limits)
    combined = "\n---\n".join(job_descriptions[:15])[:8000]
    known_list = ", ".join(sorted(known_skills)[:100])
    
    prompt = f"""Analyze these job descriptions and extract technical skills, tools, frameworks, and technologies.

IMPORTANT: Only return skills that are NOT in this list of already-known skills:
{known_list}

Job Descriptions:
{combined}

Find NEW skills/tools/frameworks/technologies that are:
1. Specific and technical (not generic terms like "programming" or "software")
2. NOT already in the known skills list above
3. Mentioned in these job postings

Return ONLY a JSON array of new skill names. If no new skills found, return empty array [].
Example: ["New Tool 1", "New Framework 2"]"""

    try:
        response = get_client().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip()
        
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            new_skills = json.loads(match.group())
            # Filter out any that somehow match known skills
            known_lower = {s.lower() for s in known_skills}
            filtered = [
                s for s in new_skills 
                if isinstance(s, str) and s.strip() 
                and s.lower() not in known_lower
                and len(s) > 1
            ]
            return filtered
    except Exception as e:
        print(f"Error discovering new skills: {e}")
    
    return []


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("Testing keyword generation...")
    keywords = generate_search_keywords(5)
    print(f"Generated keywords: {keywords}")
    
    print("\nTesting new skill discovery...")
    sample_descs = [
        "Looking for experience with LangGraph and Crew AI for multi-agent systems.",
        "Must know Streamlit, Gradio for ML demos. Experience with Modal or Replicate a plus.",
    ]
    known = {"Python", "TensorFlow", "PyTorch", "LangChain"}
    new_skills = discover_new_skills(sample_descs, known)
    print(f"Discovered new skills: {new_skills}")
