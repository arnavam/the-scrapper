"""
Skill Analyzer - Uses predefined skills with regex matching (fast)
and Groq AI only to discover new skills.
"""
import re
from collections import Counter
from typing import List, Dict, Tuple, Set
from rich.console import Console
from rich.table import Table

console = Console()

# Comprehensive predefined skills list - regex patterns
# Format: (display_name, [regex_patterns])
PREDEFINED_SKILLS = {
    # Programming Languages
    "Python": [r"\bpython\b"],
    "Java": [r"\bjava\b(?!\s*script)"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "C++": [r"\bc\+\+\b", r"\bcpp\b"],
    "C#": [r"\bc#\b", r"\bcsharp\b"],
    "Go": [r"\bgolang\b", r"\bgo\s+(?:programming|language)\b"],
    "Rust": [r"\brust\b"],
    "R": [r"\br\s+(?:programming|language|studio)\b", r"\br-lang\b"],
    "Scala": [r"\bscala\b"],
    "Julia": [r"\bjulia\b"],
    "MATLAB": [r"\bmatlab\b"],
    "Bash": [r"\bbash\b", r"\bshell\s*script"],
    "SQL": [r"\bsql\b"],
    
    # ML/AI Frameworks
    "TensorFlow": [r"\btensorflow\b", r"\btf\b"],
    "PyTorch": [r"\bpytorch\b", r"\btorch\b"],
    "Keras": [r"\bkeras\b"],
    "scikit-learn": [r"\bscikit-learn\b", r"\bsklearn\b", r"\bscikit\b"],
    "Hugging Face": [r"\bhugging\s*face\b", r"\bhf\b", r"\btransformers\b"],
    "OpenCV": [r"\bopencv\b"],
    "NLTK": [r"\bnltk\b"],
    "spaCy": [r"\bspacy\b"],
    "JAX": [r"\bjax\b"],
    "XGBoost": [r"\bxgboost\b"],
    "LightGBM": [r"\blightgbm\b"],
    "CatBoost": [r"\bcatboost\b"],
    "FastAI": [r"\bfastai\b"],
    "MXNet": [r"\bmxnet\b"],
    "Theano": [r"\btheano\b"],
    "Caffe": [r"\bcaffe\b"],
    "ONNX": [r"\bonnx\b"],
    
    # LLM & GenAI
    "LangChain": [r"\blangchain\b"],
    "LlamaIndex": [r"\bllamaindex\b", r"\bllama\s*index\b"],
    "OpenAI API": [r"\bopenai\b"],
    "Anthropic": [r"\banthropic\b", r"\bclaude\b"],
    "GPT": [r"\bgpt-?\d?\b", r"\bchatgpt\b"],
    "LLaMA": [r"\bllama\b"],
    "BERT": [r"\bbert\b"],
    "RAG": [r"\brag\b", r"\bretrieval.augmented\b"],
    "Vector DB": [r"\bvector\s*(?:db|database)\b", r"\bpinecone\b", r"\bweaviate\b", r"\bchroma\b", r"\bmilvus\b", r"\bqdrant\b"],
    
    # Cloud Platforms  
    "AWS": [r"\baws\b", r"\bamazon\s*web\s*services\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle\s*cloud\b"],
    "Azure": [r"\bazure\b", r"\bmicrosoft\s*cloud\b"],
    "AWS SageMaker": [r"\bsagemaker\b"],
    "Vertex AI": [r"\bvertex\s*ai\b"],
    "AWS Bedrock": [r"\bbedrock\b"],
    "Databricks": [r"\bdatabricks\b"],
    
    # Data & Databases
    "PostgreSQL": [r"\bpostgres(?:ql)?\b"],
    "MySQL": [r"\bmysql\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
    "Redis": [r"\bredis\b"],
    "Elasticsearch": [r"\belasticsearch\b", r"\belastic\b"],
    "Snowflake": [r"\bsnowflake\b"],
    "BigQuery": [r"\bbigquery\b"],
    "Redshift": [r"\bredshift\b"],
    "Cassandra": [r"\bcassandra\b"],
    "DynamoDB": [r"\bdynamodb\b"],
    
    # Data Processing
    "Apache Spark": [r"\bspark\b", r"\bpyspark\b"],
    "Hadoop": [r"\bhadoop\b"],
    "Kafka": [r"\bkafka\b"],
    "Airflow": [r"\bairflow\b"],
    "dbt": [r"\bdbt\b"],
    "Flink": [r"\bflink\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "SciPy": [r"\bscipy\b"],
    "Polars": [r"\bpolars\b"],
    "Dask": [r"\bdask\b"],
    
    # DevOps & MLOps
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "Git": [r"\bgit\b(?!hub|lab)"],
    "GitHub": [r"\bgithub\b"],
    "GitLab": [r"\bgitlab\b"],
    "CI/CD": [r"\bci/?cd\b", r"\bcontinuous\s*integration\b"],
    "Jenkins": [r"\bjenkins\b"],
    "Terraform": [r"\bterraform\b"],
    "Ansible": [r"\bansible\b"],
    "MLflow": [r"\bmlflow\b"],
    "Kubeflow": [r"\bkubeflow\b"],
    "Weights & Biases": [r"\bwandb\b", r"\bweights\s*(?:&|and)\s*biases\b"],
    "DVC": [r"\bdvc\b"],
    "BentoML": [r"\bbentoml\b"],
    
    # Visualization
    "Matplotlib": [r"\bmatplotlib\b"],
    "Seaborn": [r"\bseaborn\b"],
    "Plotly": [r"\bplotly\b"],
    "Tableau": [r"\btableau\b"],
    "Power BI": [r"\bpower\s*bi\b"],
    "Grafana": [r"\bgrafana\b"],
    "D3.js": [r"\bd3\.?js\b", r"\bd3\b"],
    
    # Deep Learning Concepts
    "CNN": [r"\bcnn\b", r"\bconvolutional\b"],
    "RNN": [r"\brnn\b", r"\brecurrent\b"],
    "LSTM": [r"\blstm\b"],
    "GAN": [r"\bgan\b", r"\bgenerative\s*adversarial\b"],
    "Transformer": [r"\btransformer(?:s)?\b"],
    "Attention": [r"\battention\s*mechanism\b", r"\bself-attention\b"],
    "Diffusion": [r"\bdiffusion\s*model\b"],
    
    # ML Concepts
    "NLP": [r"\bnlp\b", r"\bnatural\s*language\s*processing\b"],
    "Computer Vision": [r"\bcomputer\s*vision\b", r"\bcv\b"],
    "Deep Learning": [r"\bdeep\s*learning\b", r"\bdl\b"],
    "Reinforcement Learning": [r"\breinforcement\s*learning\b", r"\brl\b"],
    "Time Series": [r"\btime\s*series\b"],
    "Recommendation Systems": [r"\brecommend(?:ation|er)\s*(?:system|engine)?\b"],
    
    # Other Tools
    "Linux": [r"\blinux\b", r"\bunix\b"],
    "Jupyter": [r"\bjupyter\b", r"\bnotebook\b"],
    "VS Code": [r"\bvs\s*code\b", r"\bvscode\b"],
    "CUDA": [r"\bcuda\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "REST API": [r"\brest\s*api\b", r"\brestful\b"],
    "GraphQL": [r"\bgraphql\b"],
    "gRPC": [r"\bgrpc\b"],
}

# Compile regex patterns for efficiency
COMPILED_PATTERNS = {}
for skill, patterns in PREDEFINED_SKILLS.items():
    COMPILED_PATTERNS[skill] = [re.compile(p, re.IGNORECASE) for p in patterns]


def extract_skills_regex(text: str) -> Set[str]:
    """
    Extract skills from text using regex matching against predefined skills.
    Fast and doesn't require API calls.
    
    Args:
        text: Job description text
        
    Returns:
        Set of matched skill names
    """
    if not text:
        return set()
    
    found_skills = set()
    text_lower = text.lower()
    
    for skill, patterns in COMPILED_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text_lower):
                found_skills.add(skill)
                break  # Found this skill, move to next
    
    return found_skills


def aggregate_skills(all_skills: List[Set[str]]) -> Counter:
    """
    Aggregate skills from multiple job descriptions.
    
    Args:
        all_skills: List of skill sets (one per job)
        
    Returns:
        Counter with skill counts
    """
    counter = Counter()
    for skills in all_skills:
        counter.update(skills)
    return counter


def rank_skills(skill_counts: Counter, total_jobs: int, top_n: int = 50) -> List[Tuple[str, int, float]]:
    """
    Rank skills by frequency and calculate percentages.
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


def analyze_skills(jobs: List[Dict]) -> List[Tuple[str, int, float]]:
    """
    Full analysis pipeline using regex-based skill extraction.
    
    Args:
        jobs: List of job dicts with 'description' key
        
    Returns:
        Ranked skills list
    """
    all_skills = []
    
    for job in jobs:
        desc = job.get("description", "")
        skills = extract_skills_regex(desc)
        job["skills"] = list(skills)  # Store for reference
        if skills:
            all_skills.append(skills)
    
    if not all_skills:
        console.print("[yellow]No skills found to analyze[/yellow]")
        return []
    
    skill_counts = aggregate_skills(all_skills)
    total_jobs = len(all_skills)
    ranked = rank_skills(skill_counts, total_jobs)
    
    display_skills_table(ranked, total_jobs)
    
    return ranked


def get_predefined_skills() -> Set[str]:
    """Return the set of all predefined skill names."""
    return set(PREDEFINED_SKILLS.keys())


if __name__ == "__main__":
    # Test with sample data
    sample_jobs = [
        {"description": "Looking for Python developer with TensorFlow and PyTorch experience. AWS and Docker required."},
        {"description": "ML Engineer needed with scikit-learn, pandas, numpy. Experience with Kubernetes is a plus."},
        {"description": "AI Research Scientist - Deep learning, NLP, transformers, BERT, GPT models."},
    ]
    
    ranked = analyze_skills(sample_jobs)
    print(f"\nFound {len(ranked)} skills")
