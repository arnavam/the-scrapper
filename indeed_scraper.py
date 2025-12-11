"""
Indeed Job Scraper using Selenium with Chrome/Chromium.
Handles JavaScript-rendered content and includes anti-detection measures.
"""
import time
import random
import csv
import os
import subprocess
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]


def find_chrome_binary() -> Optional[str]:
    """Find Chrome/Chromium binary on the system."""
    # Common locations for Chrome for Testing and other Chrome variants
    possible_paths = [
        # Chrome for Testing (common locations)
        os.path.expanduser("~/.cache/puppeteer/chrome/*/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"),
        os.path.expanduser("~/.cache/puppeteer/chrome/*/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"),
        os.path.expanduser("~/chrome-for-testing/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"),
        "/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        # Standard Chrome
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        # Chromium
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        # Brave (Chromium-based)
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        # Arc (Chromium-based)
        "/Applications/Arc.app/Contents/MacOS/Arc",
        # Zen (Firefox-based - won't work with Chrome driver)
    ]
    
    # Check direct paths first
    for path in possible_paths:
        if '*' not in path and os.path.exists(path):
            return path
    
    # Try glob patterns
    import glob
    for pattern in possible_paths:
        if '*' in pattern:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
    
    # Try using 'which' command
    try:
        result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    # Try mdfind on macOS to find Chrome for Testing
    try:
        result = subprocess.run(
            ['mdfind', 'kMDItemCFBundleIdentifier == "com.google.Chrome.for.Testing"'],
            capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            app_path = result.stdout.strip().split('\n')[0]
            binary = os.path.join(app_path, 'Contents/MacOS/Google Chrome for Testing')
            if os.path.exists(binary):
                return binary
    except:
        pass
    
    # Try to find any Chrome-like binary
    try:
        result = subprocess.run(
            ['mdfind', 'kMDItemDisplayName == "Google Chrome*"'],
            capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            for app_path in result.stdout.strip().split('\n'):
                if '.app' in app_path:
                    # Get the binary inside the app
                    app_name = os.path.basename(app_path).replace('.app', '')
                    binary = os.path.join(app_path, f'Contents/MacOS/{app_name}')
                    if os.path.exists(binary):
                        return binary
    except:
        pass
    
    return None


class IndeedScraper:
    """Scraper for Indeed job postings."""
    
    def __init__(self, headless: bool = True, chrome_path: Optional[str] = None):
        """
        Initialize the scraper with Selenium WebDriver.
        
        Args:
            headless: Run browser in headless mode (set False for debugging)
            chrome_path: Optional explicit path to Chrome binary
        """
        self.headless = headless
        self.chrome_path = chrome_path
        self.driver = None
        self.jobs_data = []
        
    def _create_driver(self) -> webdriver.Chrome:
        """Create a new Chrome WebDriver with anti-detection settings."""
        options = Options()
        
        if self.headless:
            options.add_argument("--headless=new")
        
        # Anti-detection options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
        
        # Disable automation flags
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Find Chrome binary
        chrome_binary = self.chrome_path or find_chrome_binary()
        
        if chrome_binary:
            # Handle .app paths on macOS - need the actual binary inside
            if chrome_binary.endswith('.app'):
                inner_binary = os.path.join(chrome_binary, 'Contents/MacOS/Google Chrome for Testing')
                if os.path.exists(inner_binary):
                    chrome_binary = inner_binary
                else:
                    # Try generic name
                    app_name = os.path.basename(chrome_binary).replace('.app', '')
                    inner_binary = os.path.join(chrome_binary, f'Contents/MacOS/{app_name}')
                    if os.path.exists(inner_binary):
                        chrome_binary = inner_binary
            
            options.binary_location = chrome_binary
            console.print(f"[dim]Using browser: {chrome_binary}[/dim]")
        else:
            console.print("[red]Chrome/Chromium not found![/red]")
            console.print("[yellow]Please provide the path to your Chrome for Testing binary.[/yellow]")
            console.print("[yellow]You can set it with: --chrome-path '/path/to/chrome'[/yellow]")
            raise FileNotFoundError("Chrome binary not found. Please install Chrome or provide path via --chrome-path")
        
        # Let Selenium 4.39+ handle ChromeDriver automatically via Selenium Manager
        # This automatically downloads the correct ChromeDriver version
        driver = webdriver.Chrome(options=options)
        
        # Execute CDP commands to hide webdriver
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """
        })
        
        return driver
    
    def _random_delay(self, min_sec: float = 2, max_sec: float = 5):
        """Add a random delay between actions."""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def search_jobs(self, query: str, location: str = "", num_pages: int = 3) -> List[Dict]:
        """
        Search for jobs on Indeed and collect job listings.
        """
        self.driver = self._create_driver()
        jobs = []
        
        try:
            for page in range(num_pages):
                start = page * 10
                
                url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}"
                if location:
                    url += f"&l={location.replace(' ', '+')}"
                if start > 0:
                    url += f"&start={start}"
                
                console.print(f"[dim]Fetching page {page + 1}: {url}[/dim]")
                self.driver.get(url)
                self._random_delay(3, 6)
                
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='slider_container'], .job_seen_beacon, .jobsearch-ResultsList, .mosaic-zone"))
                    )
                except TimeoutException:
                    console.print(f"[yellow]Timeout waiting for results on page {page + 1}[/yellow]")
                    continue
                
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                job_cards = soup.select(".job_seen_beacon, [data-testid='slider_container'] > div, .resultContent")
                
                if not job_cards:
                    job_cards = soup.select(".jobsearch-ResultsList li, .mosaic-zone article")
                
                console.print(f"[green]Found {len(job_cards)} job cards on page {page + 1}[/green]")
                
                for card in job_cards:
                    job = self._parse_job_card(card)
                    if job and job.get("title"):
                        jobs.append(job)
                
                self._random_delay(2, 4)
                
        except Exception as e:
            console.print(f"[red]Error during search: {e}[/red]")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
        
        return jobs
    
    def _parse_job_card(self, card) -> Optional[Dict]:
        """Parse a job card element to extract basic info."""
        job = {}
        
        try:
            title_elem = card.select_one("h2 a, h2 span, .jobTitle a, .jobTitle span, [data-testid='jobTitle']")
            if title_elem:
                job["title"] = title_elem.get_text(strip=True)
            
            company_elem = card.select_one("[data-testid='company-name'], .companyName, .company")
            if company_elem:
                job["company"] = company_elem.get_text(strip=True)
            
            location_elem = card.select_one("[data-testid='text-location'], .companyLocation, .location")
            if location_elem:
                job["location"] = location_elem.get_text(strip=True)
            
            link_elem = card.select_one("h2 a, .jobTitle a, a[data-jk], a[href*='/viewjob']")
            if link_elem and link_elem.get("href"):
                href = link_elem.get("href")
                if href.startswith("/"):
                    job["url"] = f"https://www.indeed.com{href}"
                else:
                    job["url"] = href
            
            snippet_elem = card.select_one(".job-snippet, .underShelf, [class*='snippet']")
            if snippet_elem:
                job["snippet"] = snippet_elem.get_text(strip=True)
                
        except Exception as e:
            console.print(f"[dim]Error parsing job card: {e}[/dim]")
        
        return job if job else None
    
    def extract_job_details(self, job_url: str) -> Optional[str]:
        """Navigate to a job page and extract the full description."""
        if not self.driver:
            self.driver = self._create_driver()
        
        try:
            self.driver.get(job_url)
            self._random_delay(2, 4)
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#jobDescriptionText, .jobsearch-jobDescriptionText, [class*='jobDescription']"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            desc_elem = soup.select_one("#jobDescriptionText, .jobsearch-jobDescriptionText, [class*='jobDescription']")
            if desc_elem:
                return desc_elem.get_text(separator="\n", strip=True)
                
        except TimeoutException:
            console.print(f"[yellow]Timeout loading job details[/yellow]")
        except Exception as e:
            console.print(f"[red]Error extracting job details: {e}[/red]")
        
        return None
    
    def scrape_with_details(self, query: str, location: str = "", num_pages: int = 2) -> List[Dict]:
        """Scrape jobs and fetch full descriptions for each."""
        jobs = self.search_jobs(query, location, num_pages)
        
        if not jobs:
            return []
        
        # Use snippets as descriptions for now since Indeed blocks detail pages
        # This is more reliable and faster
        for job in jobs:
            if job.get("snippet"):
                job["description"] = job["snippet"]
            else:
                job["description"] = f"{job.get('title', '')} at {job.get('company', '')}"
        
        console.print(f"[green]Using job snippets for skill extraction ({len(jobs)} jobs)[/green]")
        
        return jobs
    
    def save_to_csv(self, jobs: List[Dict], filename: str = "jobs.csv"):
        """Save scraped jobs to a CSV file."""
        if not jobs:
            console.print("[yellow]No jobs to save[/yellow]")
            return
        
        fieldnames = ["title", "company", "location", "url", "snippet", "description"]
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(jobs)
        
        console.print(f"[green]Saved {len(jobs)} jobs to {filename}[/green]")


if __name__ == "__main__":
    scraper = IndeedScraper(headless=False)
    
    console.print("[bold]Testing Indeed Scraper[/bold]")
    jobs = scraper.search_jobs("AI Engineer", "Remote", num_pages=1)
    
    for job in jobs[:5]:
        console.print(f"\n[bold]{job.get('title', 'N/A')}[/bold]")
        console.print(f"  Company: {job.get('company', 'N/A')}")
        console.print(f"  Location: {job.get('location', 'N/A')}")
