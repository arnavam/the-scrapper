"""
Visualization module for skill analysis results.
"""
import os
import matplotlib.pyplot as plt
from typing import List, Tuple


def create_skills_bar_chart(
    ranked_skills: List[Tuple[str, int, float]],
    output_path: str = "output/skills_ranking.png",
    top_n: int = 30
):
    """
    Create a horizontal bar chart of top skills.
    
    Args:
        ranked_skills: List of (skill, count, percentage) tuples
        output_path: Where to save the chart
        top_n: Number of skills to show
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    # Take top N skills
    skills_to_plot = ranked_skills[:top_n]
    
    if not skills_to_plot:
        print("No skills to visualize")
        return
    
    # Prepare data (reverse for horizontal bar chart so top is at top)
    skills = [s[0] for s in reversed(skills_to_plot)]
    counts = [s[1] for s in reversed(skills_to_plot)]
    percentages = [s[2] for s in reversed(skills_to_plot)]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, max(8, len(skills) * 0.35)))
    
    # Color gradient based on percentage
    colors = plt.cm.viridis([p / 100 for p in percentages])
    
    # Create horizontal bar chart
    bars = ax.barh(skills, counts, color=colors)
    
    # Add percentage labels on bars
    for bar, pct in zip(bars, percentages):
        width = bar.get_width()
        ax.text(
            width + 0.5, 
            bar.get_y() + bar.get_height() / 2,
            f'{pct:.1f}%',
            ha='left', 
            va='center',
            fontsize=9,
            color='gray'
        )
    
    # Styling
    ax.set_xlabel('Number of Job Postings Mentioning Skill', fontsize=11)
    ax.set_title('Most In-Demand AI/ML Skills & Tools', fontsize=14, fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add grid
    ax.xaxis.grid(True, linestyle='--', alpha=0.6)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Chart saved to: {output_path}")


def create_category_pie_chart(
    ranked_skills: List[Tuple[str, int, float]],
    output_path: str = "output/skills_categories.png"
):
    """
    Create a pie chart grouping skills by category.
    
    Args:
        ranked_skills: List of (skill, count, percentage) tuples
        output_path: Where to save the chart
    """
    # Define skill categories
    categories = {
        "Programming Languages": {"Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "R", "Scala", "Julia", "MATLAB", "Bash"},
        "ML/AI Frameworks": {"TensorFlow", "PyTorch", "Keras", "scikit-learn", "Hugging Face", "Transformers", "OpenCV", "NLTK", "spaCy", "LangChain"},
        "Cloud Platforms": {"AWS", "GCP", "Azure", "AWS SageMaker", "Vertex AI", "Databricks"},
        "Data & Databases": {"SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Snowflake", "Apache Spark", "Hadoop", "Kafka"},
        "DevOps & Tools": {"Docker", "Kubernetes", "Git", "GitHub", "GitLab", "Jenkins", "CI/CD", "Terraform", "MLflow", "Apache Airflow", "dbt"},
        "Visualization": {"Tableau", "Power BI", "Matplotlib", "Seaborn", "Plotly"},
        "AI/ML Concepts": {"LLM", "NLP", "Computer Vision", "Deep Learning", "Reinforcement Learning", "RAG", "GANs", "CNN", "RNN", "LSTM", "BERT", "GPT"},
    }
    
    # Count skills per category
    category_counts = {cat: 0 for cat in categories}
    other_count = 0
    
    for skill, count, _ in ranked_skills:
        found = False
        for cat, cat_skills in categories.items():
            if skill in cat_skills:
                category_counts[cat] += count
                found = True
                break
        if not found:
            other_count += count
    
    # Prepare data
    labels = []
    sizes = []
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        if count > 0:
            labels.append(cat)
            sizes.append(count)
    
    if other_count > 0:
        labels.append("Other")
        sizes.append(other_count)
    
    if not sizes:
        print("No data for pie chart")
        return
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = plt.cm.Set3(range(len(labels)))
    
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        pctdistance=0.75
    )
    
    # Style labels
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title('Skill Categories Distribution', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"Pie chart saved to: {output_path}")


if __name__ == "__main__":
    # Test visualization
    sample_data = [
        ("Python", 45, 90.0),
        ("TensorFlow", 30, 60.0),
        ("PyTorch", 28, 56.0),
        ("AWS", 25, 50.0),
        ("SQL", 22, 44.0),
        ("Docker", 20, 40.0),
        ("Kubernetes", 15, 30.0),
        ("scikit-learn", 14, 28.0),
        ("GCP", 12, 24.0),
        ("Java", 10, 20.0),
    ]
    
    create_skills_bar_chart(sample_data, "output/test_skills.png", top_n=10)
    create_category_pie_chart(sample_data, "output/test_categories.png")
