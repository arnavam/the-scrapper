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

    """
    prompt = f"""Generate exactly {num_keywords} job search keywords/titles related to AI and Machine Learning engineering.

Include a variety of:
- AI/ML engineering roles (e.g., "Machine Learning Engineer", "AI Engineer")
- Data science and research roles (e.g., "Data Scientist", "Research Scientist")  
- Specialized roles (e.g., "NLP Engineer", "Computer Vision Engineer", "LLM Developer")
- MLOps and infrastructure roles (e.g., "MLOps Engineer", "ML Platform Engineer")

Return ONLY a JSON array of strings, no other text.
Example: ["Machine Learning Engineer", "Data Scientist", "NLP Engineer"]"""

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
    console.print("[yellow]Using fallback keywords...[/yellow]")
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
    
    Processes ALL descriptions in chunks of 15 to stay within token limits.
    
    Args:
        job_descriptions: List of job description texts
        known_skills: Set of skills we already know about
        
    Returns:
        List of newly discovered skills not in known_skills
    """
    if not job_descriptions:
        return []
    
    all_new_skills = set()
    known_list = ", ".join(sorted(known_skills)[:100])
    known_lower = {s.lower() for s in known_skills}
    
    # Process in chunks of 15
    chunk_size = 15
    total_chunks = (len(job_descriptions) + chunk_size - 1) // chunk_size
    
    for i in range(0, len(job_descriptions), chunk_size):
        chunk = job_descriptions[i:i + chunk_size]
        combined = "\n---\n".join(chunk)[:8000]
        
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
                # Filter and add to set
                for s in new_skills:
                    if isinstance(s, str) and s.strip() and s.lower() not in known_lower and len(s) > 1:
                        all_new_skills.add(s.strip())
                        known_lower.add(s.lower())  # Prevent duplicates across chunks
        except Exception as e:
            print(f"Error in chunk {i//chunk_size + 1}: {e}")
            continue
    
    return list(all_new_skills)


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
