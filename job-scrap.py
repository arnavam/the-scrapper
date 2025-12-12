# Source - https://stackoverflow.com/a
# Posted by Andrej Kesely
# Retrieved 2025-12-12, License - CC BY-SA 4.0

import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
}


url = "https://www.indeed.com/jobs?q=data+engineer&l=United+States"
api_url = "https://www.indeed.com/viewjob?viewtype=embedded&jk={job_id}"

soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")

for job in soup.select('a[id^="job_"]'):
    job_id = job["id"].split("_")[-1]
    s = BeautifulSoup(
        requests.get(api_url.format(job_id=job_id), headers=headers).content,
        "html.parser",
    )

    print(s.title.get_text(strip=True))
    print()
    print(
        s.select_one("#jobDescriptionText").get_text(strip=True, separator="\n")
    )
    print("#" * 80)
