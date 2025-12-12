"""
Main entry point for the Indeed AI Jobs Skill Analyzer.

Usage:
    python main.py [--results N] [--keywords N] [--discover-new]
    
Environment Variables:
    GROQ_API_KEY: Your Groq API key (required for keyword generation and skill discovery)
"""
import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from groq_helper import generate_search_keywords, discover_new_skills
from indeed_scraper import scrape_multiple_keywords, save_jobs_to_csv
from skill_analyzer import analyze_skills, get_predefined_skills
from visualize import create_skills_bar_chart, create_category_pie_chart

console = Console()


def main():
    """Main execution function."""
    load_dotenv()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Scrape Indeed for AI jobs and analyze required skills")
    parser.add_argument("--results", type=int, default=30, help="Results per search keyword (default: 30)")
    parser.add_argument("--keywords", type=int, default=5, help="Number of search keywords to generate (default: 5)")
    parser.add_argument("--location", type=str, default="", help="Location filter (e.g., 'Remote', 'New York')")
    parser.add_argument("--hours", type=int, default=72, help="Only get jobs posted within this many hours (default: 72)")
    parser.add_argument("--discover-new", action="store_true", help="Use Groq to discover new skills not in predefined list")
    args = parser.parse_args()
    
    # Check for API key
    if not os.environ.get("GROQ_API_KEY"):
        console.print("[red bold]Error: GROQ_API_KEY environment variable not set![/red bold]")
        console.print("Set it with: export GROQ_API_KEY=your_key_here")
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold cyan]Indeed AI Jobs Skill Analyzer[/bold cyan]\n"
        "Scrape AI/ML job postings and discover in-demand skills",
        border_style="cyan"
    ))
    
    # Step 1: Generate search keywords using Groq
    console.print("\n[bold]Step 1:[/bold] Generating search keywords with AI...")
    try:
        keywords = generate_search_keywords(args.keywords)
        console.print(f"[green]Generated {len(keywords)} search terms:[/green]")
        for kw in keywords:
            console.print(f"  • {kw}")
    except Exception as e:
        console.print(f"[red]Error generating keywords: {e}[/red]")
        console.print("[yellow]Using default keywords...[/yellow]")
        keywords = ["AI Engineer", "AI Developer", "AI Research Scientist"]
    
    # Step 2: Scrape jobs using JobSpy
    console.print(f"\n[bold]Step 2:[/bold] Scraping Indeed ({args.results} results per keyword)...")
    
    all_jobs = scrape_multiple_keywords(
        keywords=keywords,
        location=args.location,
        results_per_keyword=args.results,
        hours_old=args.hours
    )
    
    if not all_jobs:
        console.print("[red]No jobs found![/red]")
        sys.exit(1)
    
    console.print(f"\n[green]Total jobs collected: {len(all_jobs)}[/green]")
    
    # Step 3: Extract skills using REGEX (fast, no API calls)
    console.print(f"\n[bold]Step 3:[/bold] Extracting skills using regex matching...")
    console.print(f"[dim]Using {len(get_predefined_skills())} predefined skills[/dim]")
    
    ranked_skills = analyze_skills(all_jobs)
    
    if not ranked_skills:
        console.print("[yellow]No skills to analyze[/yellow]")
        sys.exit(1)
    
    jobs_with_skills = [j for j in all_jobs if j.get("skills")]
    console.print(f"[green]Found skills in {len(jobs_with_skills)} jobs[/green]")
    
    # Step 4 (Optional): Discover NEW skills with Groq
    new_skills = []
    if args.discover_new:
        console.print(f"\n[bold]Step 4:[/bold] Discovering new skills with AI...")
        sample_descriptions = [
            j.get("description", "") for j in all_jobs[:20] 
            if j.get("description")
        ]
        known = get_predefined_skills()
        
        try:
            new_skills = discover_new_skills(sample_descriptions, known)
            if new_skills:
                console.print(f"[green]Discovered {len(new_skills)} new skills:[/green]")
                for skill in new_skills[:10]:
                    console.print(f"  • {skill}")
                if len(new_skills) > 10:
                    console.print(f"  ... and {len(new_skills) - 10} more")
            else:
                console.print("[dim]No new skills discovered[/dim]")
        except Exception as e:
            console.print(f"[yellow]Could not discover new skills: {e}[/yellow]")
    
    # Step 5: Create visualizations
    console.print(f"\n[bold]Step 5:[/bold] Creating visualizations...")
    os.makedirs("output", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    create_skills_bar_chart(
        ranked_skills,
        output_path=f"output/skills_ranking_{timestamp}.png",
        top_n=30
    )
    
    create_category_pie_chart(
        ranked_skills,
        output_path=f"output/skills_categories_{timestamp}.png"
    )
    
    # Save raw data
    output_data = {
        "timestamp": timestamp,
        "total_jobs": len(all_jobs),
        "jobs_with_skills": len(jobs_with_skills),
        "search_keywords": keywords,
        "ranked_skills": [
            {"skill": s, "count": c, "percentage": p}
            for s, c, p in ranked_skills
        ],
        "new_skills_discovered": new_skills
    }
    
    with open(f"output/results_{timestamp}.json", "w") as f:
        json.dump(output_data, f, indent=2)
    
    save_jobs_to_csv(all_jobs, f"output/jobs_{timestamp}.csv")
    
    console.print(Panel.fit(
        f"[bold green]Analysis Complete![/bold green]\n\n"
        f"Jobs analyzed: {len(all_jobs)}\n"
        f"Unique skills found: {len(ranked_skills)}\n"
        f"New skills discovered: {len(new_skills)}\n\n"
        f"Output files saved to [cyan]output/[/cyan] directory",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
