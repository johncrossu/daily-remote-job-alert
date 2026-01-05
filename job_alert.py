import requests
import json
import pandas as pd
import yagmail
import os

# ---- ENVIRONMENT ---- #
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
SENT_FILE = "sent_jobs.json"

# ---- LOAD SENT JOBS ---- #
try:
    with open(SENT_FILE) as f:
        sent_jobs = json.load(f)
except FileNotFoundError:
    sent_jobs = []

new_jobs = []

# ---- FUNCTION: REMOTIVE API ---- #
def get_remotive():
    url = "https://remotive.com/api/remote-jobs?search=customer"
    res = requests.get(url).json()
    for job in res.get("jobs", []):
        link = job["url"]
        if link not in sent_jobs:
            new_jobs.append({
                "source": "Remotive",
                "title": job["title"],
                "company": job["company_name"],
                "link": f'<a href="{link}">Open</a>'
            })
            sent_jobs.append(link)

# ---- FUNCTION: SERPAPI JOBS (Dynamic Sites) ---- #
def get_serpapi(query, location=""):
    endpoint = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "location": location,
        "engine": "google_jobs",
        "api_key": SERPAPI_KEY
    }
    res = requests.get(endpoint, params=params).json()
    for job in res.get("jobs_results", []):
        link = job.get("link")
        title = job.get("title")
        company = job.get("organization")
        if link and link not in sent_jobs:
            new_jobs.append({
                "source": "SerpAPI",
                "title": title,
                "company": company,
                "link": f'<a href="{link}">Open</a>'
            })
            sent_jobs.append(link)

# ---- RUN API FETCHES ---- #
get_remotive()
locations = ["USA", "Canada", "UK", "Nigeria"]
for loc in locations:
    get_serpapi("Remote Customer Support Representative", loc)

# ---- EXIT IF NO NEW JOBS ---- #
if not new_jobs:
    print("No new jobs to send.")
    exit()

# ---- SEND EMAIL ---- #
df = pd.DataFrame(new_jobs)
html_table = df.to_html(index=False, escape=False)
yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)
yag.send(
    to=GMAIL_USER,
    subject="Global Remote Customer Care Jobs Alert",
    contents=[html_table]
)

# ---- UPDATE SENT JOBS ---- #
with open(SENT_FILE, "w") as f:
    json.dump(sent_jobs, f)

print(f"Sent {len(new_jobs)} new jobs to your email!")