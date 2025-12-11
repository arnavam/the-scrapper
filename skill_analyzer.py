"""
Skill Analyzer - Aggregates and ranks skills extracted from job descriptions.
"""
from collections import Counter
from typing import List, Dict, Tuple
from rich.console import Console
from rich.table import Table

console = Console()


def normalize_skill(skill: str) -> str:
    """
    Normalize skill names to reduce duplicates.
    E.g., "python" and "Python" become "Python"
    """
    skill = skill.strip()
    
    # Common normalizations
    normalizations = {
        "python": "Python",
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "keras": "Keras",
        "scikit-learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "aws": "AWS",
        "gcp": "GCP",
        "azure": "Azure",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "k8s": "Kubernetes",
        "sql": "SQL",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "mongodb": "MongoDB",
        "spark": "Apache Spark",
        "apache spark": "Apache Spark",
        "hadoop": "Hadoop",
        "kafka": "Kafka",
        "redis": "Redis",
        "git": "Git",
        "github": "GitHub",
        "gitlab": "GitLab",
        "linux": "Linux",
        "bash": "Bash",
        "java": "Java",
        "javascript": "JavaScript",
        "js": "JavaScript",
        "typescript": "TypeScript",
        "ts": "TypeScript",
        "c++": "C++",
        "cpp": "C++",
        "c#": "C#",
        "csharp": "C#",
        "go": "Go",
        "golang": "Go",
        "rust": "Rust",
        "r": "R",
        "scala": "Scala",
        "julia": "Julia",
        "matlab": "MATLAB",
        "numpy": "NumPy",
        "pandas": "Pandas",
        "scipy": "SciPy",
        "matplotlib": "Matplotlib",
        "seaborn": "Seaborn",
        "plotly": "Plotly",
        "opencv": "OpenCV",
        "nltk": "NLTK",
        "spacy": "spaCy",
        "huggingface": "Hugging Face",
        "hugging face": "Hugging Face",
        "transformers": "Transformers",
        "langchain": "LangChain",
        "llama": "LLaMA",
        "gpt": "GPT",
        "openai": "OpenAI",
        "bert": "BERT",
        "fastapi": "FastAPI",
        "flask": "Flask",
        "django": "Django",
        "react": "React",
        "vue": "Vue.js",
        "angular": "Angular",
        "node.js": "Node.js",
        "nodejs": "Node.js",
        "airflow": "Apache Airflow",
        "apache airflow": "Apache Airflow",
        "mlflow": "MLflow",
        "dvc": "DVC",
        "wandb": "Weights & Biases",
        "weights & biases": "Weights & Biases",
        "tableau": "Tableau",
        "power bi": "Power BI",
        "powerbi": "Power BI",
        "excel": "Excel",
        "jupyter": "Jupyter",
        "colab": "Google Colab",
        "google colab": "Google Colab",
        "sagemaker": "AWS SageMaker",
        "aws sagemaker": "AWS SageMaker",
        "vertex ai": "Vertex AI",
        "databricks": "Databricks",
        "snowflake": "Snowflake",
        "dbt": "dbt",
        "terraform": "Terraform",
        "ansible": "Ansible",
        "jenkins": "Jenkins",
        "ci/cd": "CI/CD",
        "cicd": "CI/CD",
        "agile": "Agile",
        "scrum": "Scrum",
        "jira": "Jira",
        "rag": "RAG",
        "llm": "LLM",
        "llms": "LLM",
        "nlp": "NLP",
        "cv": "Computer Vision",
        "computer vision": "Computer Vision",
        "deep learning": "Deep Learning",
        "reinforcement learning": "Reinforcement Learning",
        "rl": "Reinforcement Learning",
        "gan": "GANs",
        "gans": "GANs",
        "cnn": "CNN",
        "rnn": "RNN",
        "lstm": "LSTM",
        "attention": "Attention Mechanism",
    }
    
    skill_lower = skill.lower()
    return normalizations.get(skill_lower, skill)


def aggregate_skills(all_skills: List[List[str]]) -> Counter:
    """
    Aggregate skills from multiple job descriptions.
    
    Args:
        all_skills: List of skill lists (one per job)
        
    Returns:
        Counter with skill counts
    """
    counter = Counter()
    
    for skills in all_skills:
        # Normalize and count unique skills per job (not duplicates within same job)
        normalized = set(normalize_skill(s) for s in skills)
        counter.update(normalized)
    
    return counter


def rank_skills(skill_counts: Counter, total_jobs: int, top_n: int = 50) -> List[Tuple[str, int, float]]:
    """
    Rank skills by frequency and calculate percentages.
    
    Args:
        skill_counts: Counter with skill counts
        total_jobs: Total number of jobs analyzed
        top_n: Number of top skills to return
        
    Returns:
        List of (skill, count, percentage) tuples
    """
    ranked = []
    
    for skill, count in skill_counts.most_common(top_n):
        percentage = (count / total_jobs * 100) if total_jobs > 0 else 0
        ranked.append((skill, count, percentage))
    
    return ranked


def display_skills_table(ranked_skills: List[Tuple[str, int, float]], total_jobs: int):
    """Display skills as a rich table in the console."""
    table = Table(
        title=f"[bold]Top Skills from {total_jobs} AI Job Postings[/bold]",
        show_header=True,
        header_style="bold cyan"
    )
    
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Skill/Tool", style="bold")
    table.add_column("Mentions", justify="right")
    table.add_column("% of Jobs", justify="right")
    
    for i, (skill, count, pct) in enumerate(ranked_skills, 1):
        # Color code by frequency
        if pct >= 50:
            style = "green bold"
        elif pct >= 25:
            style = "green"
        elif pct >= 10:
            style = "yellow"
        else:
            style = "white"
        
        table.add_row(
            str(i),
            f"[{style}]{skill}[/{style}]",
            str(count),
            f"{pct:.1f}%"
        )
    
    console.print(table)


def analyze_skills(jobs_with_skills: List[Dict]) -> List[Tuple[str, int, float]]:
    """
    Full analysis pipeline: aggregate, rank, and display skills.
    
    Args:
        jobs_with_skills: List of job dicts with 'skills' key containing skill lists
        
    Returns:
        Ranked skills list
    """
    # Extract all skill lists
    all_skills = [job.get("skills", []) for job in jobs_with_skills if job.get("skills")]
    
    if not all_skills:
        console.print("[yellow]No skills found to analyze[/yellow]")
        return []
    
    # Aggregate and rank
    skill_counts = aggregate_skills(all_skills)
    total_jobs = len(all_skills)
    ranked = rank_skills(skill_counts, total_jobs)
    
    # Display
    display_skills_table(ranked, total_jobs)
    
    return ranked


if __name__ == "__main__":
    # Test with sample data
    sample_jobs = [
        {"skills": ["Python", "TensorFlow", "AWS", "Docker", "SQL"]},
        {"skills": ["Python", "PyTorch", "GCP", "Kubernetes", "SQL"]},
        {"skills": ["Python", "scikit-learn", "AWS", "Docker", "PostgreSQL"]},
        {"skills": ["Java", "TensorFlow", "Azure", "Docker", "MongoDB"]},
        {"skills": ["Python", "PyTorch", "AWS", "Docker", "SQL", "Spark"]},
    ]
    
    ranked = analyze_skills(sample_jobs)
