"""
Indeed Job Scraper using JobSpy library.
Much more reliable than custom Selenium scraping.
"""
import csv
from typing import List, Dict
from jobspy import scrape_jobs
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def scrape_indeed_jobs(
    search_term: str,
    location: str = "",
    results_wanted: int = 50,
    hours_old: int = 72
) -> List[Dict]:
    """
    Scrape jobs from Indeed using JobSpy.
    
    Args:
        search_term: Job search query
        location: Location filter
        results_wanted: Number of results to fetch
        hours_old: Only get jobs posted within this many hours
        
    Returns:
        List of job dictionaries
    """
    console.print(f"[dim]Searching Indeed for: {search_term}[/dim]")
    
    try:
        # Use JobSpy to scrape
        jobs_df = scrape_jobs(
            site_name=["indeed"],
            search_term=search_term,
            location=location if location else None,
            results_wanted=results_wanted,
            hours_old=hours_old,
            country_indeed="USA",
        )
        
        if jobs_df.empty:
            console.print(f"[yellow]No jobs found for: {search_term}[/yellow]")
            return []
        
        # Convert DataFrame to list of dicts
        jobs = []
        for _, row in jobs_df.iterrows():
            job = {
                "title": row.get("title", ""),
                "company": row.get("company", ""),
                "location": f"{row.get('city', '')} {row.get('state', '')}".strip(),
                "url": row.get("job_url", ""),
                "description": row.get("description", ""),
                "salary_min": row.get("min_amount"),
                "salary_max": row.get("max_amount"),
                "job_type": row.get("job_type", ""),
            }
            if job["title"]:
                jobs.append(job)
        
        console.print(f"[green]Found {len(jobs)} jobs[/green]")
        return jobs
        
    except Exception as e:
        console.print(f"[red]Error scraping jobs: {e}[/red]")
        return []


def scrape_multiple_keywords(
    keywords: List[str],
    location: str = "",
    results_per_keyword: int = 30,
    hours_old: int = 72
) -> List[Dict]:
    """
    Scrape jobs for multiple search keywords.
    
    Args:
        keywords: List of search terms
        location: Location filter
        results_per_keyword: Results to fetch per keyword
        hours_old: Job age filter in hours
        
    Returns:
        Combined list of jobs from all keywords
    """
    all_jobs = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Scraping jobs...", total=len(keywords))
        
        for keyword in keywords:
            jobs = scrape_indeed_jobs(
                search_term=keyword,
                location=location,
                results_wanted=results_per_keyword,
                hours_old=hours_old
            )
            all_jobs.extend(jobs)
            progress.advance(task)
    
    # Log stats
    with_desc = sum(1 for j in all_jobs if j.get("description") and len(j["description"]) > 100)
    console.print(f"[green]Total jobs: {len(all_jobs)}, with descriptions: {with_desc}[/green]")
    
    return all_jobs


def save_jobs_to_csv(jobs: List[Dict], filename: str = "jobs.csv"):
    """Save jobs to CSV file."""
    if not jobs:
        console.print("[yellow]No jobs to save[/yellow]")
        return
    
    fieldnames = ["title", "company", "location", "url", "description", "salary_min", "salary_max", "job_type"]
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(jobs)
    
    console.print(f"[green]Saved {len(jobs)} jobs to {filename}[/green]")


if __name__ == "__main__":
    # Test the scraper
    console.print("[bold]Testing JobSpy-based scraper[/bold]")
    
    jobs = scrape_indeed_jobs("AI Engineer", results_wanted=10)
    
    for job in jobs[:3]:
        console.print(f"\n[bold]{job.get('title', 'N/A')}[/bold]")
        console.print(f"  Company: {job.get('company', 'N/A')}")
        console.print(f"  Location: {job.get('location', 'N/A')}")
        desc = job.get("description", "")[:200]
        console.print(f"  Description: {desc}...")
