"""
Main entry point for the Indeed AI Jobs Skill Analyzer.

Usage:
    python main.py [--pages N] [--headless]
    
Environment Variables:
    GROQ_API_KEY: Your Groq API key (required)
"""
import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from groq_helper import generate_search_keywords, extract_skills
from indeed_scraper import IndeedScraper
from skill_analyzer import analyze_skills, aggregate_skills, rank_skills
from visualize import create_skills_bar_chart, create_category_pie_chart

console = Console()


def main():
    """Main execution function."""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Scrape Indeed for AI jobs and analyze required skills")
    parser.add_argument("--pages", type=int, default=2, help="Number of pages to scrape per search term (default: 2)")
    parser.add_argument("--keywords", type=int, default=5, help="Number of search keywords to generate (default: 5)")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Show browser window")
    parser.add_argument("--location", type=str, default="", help="Location filter (e.g., 'Remote', 'New York')")
    parser.add_argument("--chrome-path", type=str, default=None, help="Path to Chrome/Chromium binary")
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
        keywords = ["AI Engineer", "Machine Learning Engineer", "Data Scientist AI"]
    
    # Step 2: Scrape jobs for each keyword
    console.print(f"\n[bold]Step 2:[/bold] Scraping Indeed ({args.pages} pages per keyword)...")
    scraper = IndeedScraper(headless=args.headless, chrome_path=args.chrome_path)
    all_jobs = []
    
    for keyword in keywords:
        console.print(f"\n[cyan]Searching: {keyword}[/cyan]")
        jobs = scraper.scrape_with_details(
            query=keyword,
            location=args.location,
            num_pages=args.pages
        )
        console.print(f"  Found {len(jobs)} jobs with descriptions")
        all_jobs.extend(jobs)
    
    if not all_jobs:
        console.print("[red]No jobs found! Indeed may be blocking requests.[/red]")
        console.print("[yellow]Try running with --no-headless or reducing --pages[/yellow]")
        sys.exit(1)
    
    console.print(f"\n[green]Total jobs collected: {len(all_jobs)}[/green]")
    
    # Step 3: Extract skills using Groq
    console.print(f"\n[bold]Step 3:[/bold] Extracting skills from job descriptions with AI...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing job descriptions...", total=len(all_jobs))
        
        for job in all_jobs:
            if job.get("description"):
                skills = extract_skills(job["description"])
                job["skills"] = skills
            else:
                job["skills"] = []
            progress.advance(task)
    
    # Count jobs with skills
    jobs_with_skills = [j for j in all_jobs if j.get("skills")]
    console.print(f"[green]Extracted skills from {len(jobs_with_skills)} jobs[/green]")
    
    # Step 4: Analyze and rank skills
    console.print(f"\n[bold]Step 4:[/bold] Ranking skills by frequency...\n")
    ranked_skills = analyze_skills(all_jobs)
    
    if not ranked_skills:
        console.print("[yellow]No skills to analyze[/yellow]")
        sys.exit(1)
    
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
        ]
    }
    
    with open(f"output/results_{timestamp}.json", "w") as f:
        json.dump(output_data, f, indent=2)
    
    # Save jobs data
    scraper.save_to_csv(all_jobs, f"output/jobs_{timestamp}.csv")
    
    console.print(Panel.fit(
        f"[bold green]Analysis Complete![/bold green]\n\n"
        f"Jobs analyzed: {len(all_jobs)}\n"
        f"Unique skills found: {len(ranked_skills)}\n\n"
        f"Output files saved to [cyan]output/[/cyan] directory",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
