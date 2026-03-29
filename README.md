# Indeed AI Jobs Skill Analyzer

Scrapes AI/ML job postings from Indeed and uses **Groq AI** to dynamically extract and rank the most in-demand skills and tools.

## Features

- 🤖 **AI-Powered Keyword Generation** - Groq generates relevant job search terms
- 🔍 **AI-Powered Skill Extraction** - No predefined skill lists, discovers skills organically
- 📊 **Visual Analytics** - Bar charts and pie charts of top skills
- 🛡️ **Anti-Detection** - Selenium with random delays and user-agent rotation

## Setup

Choose your preferred method:

**Method 1: Using `uv` (Recommended)**

1.  **Install `uv` (if you haven't already):**
    ```bash
    pip install uv
    ```

2.  **Create a virtual environment and sync dependencies:**
    ```bash
    uv venv
    uv sync
    ```

**Method 2: Using `pip` and `venv`**

1.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

### Configuration

1.  **Set your Groq API key:**
    ```bash
    export GROQ_API_KEY=your_key_here
    ```
    Or create a `.env` file:
    ```
    GROQ_API_KEY=your_key_here
    ```

2.  **Run the analyzer:**
    ```bash
    python main.py
    ```

## Usage Options

```bash
# Basic usage (2 pages per search, 5 keywords)
python main.py

# More thorough scraping
python main.py --pages 5 --keywords 10

# Show browser window (helps bypass detection)
python main.py --no-headless

# Filter by location
python main.py --location "Remote"
python main.py --location "San Francisco"
```

## Output

Results are saved to `output/` directory:
- `skills_ranking_[timestamp].png` - Bar chart of top skills
- `skills_categories_[timestamp].png` - Pie chart by category
- `results_[timestamp].json` - Raw skill data
- `jobs_[timestamp].csv` - All scraped job data

## Project Structure

```
the-scrapper/
├── main.py           # Entry point
├── groq_helper.py    # AI keyword & skill extraction
├── indeed_scraper.py # Selenium-based scraper
├── skill_analyzer.py # Skill aggregation & ranking
├── visualize.py      # Chart generation
├── pyproject.toml    # Project configuration and dependencies
├── requirements.txt  # Pip dependencies
├── uv.lock           # uv lock file
└── output/           # Results directory
```

## Notes

⚠️ **Rate Limiting**: Indeed has anti-bot protections. The scraper includes delays, but if blocked, try `--no-headless` mode.

⚠️ **Ethical Use**: Respect Indeed's servers by not scraping excessively.
