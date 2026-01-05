import requests
import json
import os
import yagmail
import pandas as pd
import feedparser

# ------------------ ENV ------------------
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

SENT_FILE = "sent_jobs.json"

# ------------------ LOAD SENT JOBS ------------------
if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r") as f:
        sent_jobs = json.load(f)
else:
    sent_jobs = []

new_jobs = []

# ------------------ HELPER FUNCTION ------------------
def add_job(title, company, link):
    if link not in sent_jobs:
        new_jobs.append({
            "Job Title": title,
            "Company": company,
            "Apply": f'<a href="{link}">Apply</a>'
        })
        sent_jobs.append(link)

# ------------------ SERPAPI / GOOGLE JOBS ------------------
def fetch_jobs_serpapi():
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_jobs",
        "q": "Remote Customer Care Representative",
        "api_key": SERPAPI_KEY
    }

    try:
        data = requests.get(url, params=params, timeout=15).json()
    except Exception as e:
        print(f"SerpAPI fetch failed: {e}")
        return

    allowed_titles = [
        "customer care",
        "customer support",
        "customer service",
        "customer representative",
        "support representative",
        "call center"
    ]
    blocked = [
        "us only",
        "canada only",
        "uk only",
        "europe only",
        "united states only"
    ]

    for job in data.get("jobs_results", []):
        title = (job.get("title") or "").lower()
        company = job.get("organization")
        link = job.get("link")
        text = ((job.get("location") or "") + (job.get("description") or "")).lower()

        if not any(t in title for t in allowed_titles):
            continue
        if any(b in text for b in blocked):
            continue

        add_job(job.get("title"), company, link)

# ------------------ REMOTIVE API ------------------
def fetch_jobs_remotive():
    url = "https://remotive.io/api/remote-jobs"
    try:
        res = requests.get(url, timeout=15)
        data = res.json()
    except Exception as e:
        print(f"Remotive fetch failed: {e}")
        return

    allowed_titles = [
        "customer care",
        "customer support",
        "customer service",
        "customer representative",
        "support representative",
        "call center"
    ]

    for job in data.get("jobs", []):
        title = job.get("title").lower()
        company = job.get("company_name")
        link = job.get("url")
        if any(t in title for t in allowed_titles):
            add_job(job.get("title"), company, link)

# ------------------ WE WORK REMOTELY RSS ------------------
def fetch_jobs_wwr():
    feed_url = "https://weworkremotely.com/categories/remote-customer-support-jobs.rss"
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        print(f"WWR fetch failed: {e}")
        return

    for entry in feed.entries:
        add_job(entry.title, entry.get("author", "Unknown"), entry.link)

# ------------------ RUN ALL SOURCES ------------------
fetch_jobs_serpapi()
fetch_jobs_remotive()
fetch_jobs_wwr()

# ------------------ EMAIL ------------------
try:
    yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)

    if not new_jobs:
        yag.send(
            to=GMAIL_USER,
            subject="Customer Care Job Alert",
            contents="No new customer care jobs found at this time. Will keep checking."
        )
    else:
        df = pd.DataFrame(new_jobs)
        html = df.to_html(index=False, escape=False)
        yag.send(
            to=GMAIL_USER,
            subject="🔥 Remote Customer Care Jobs",
            contents=[
                "<h3>Remote Customer Care / Support Jobs</h3>",
                html
            ]
        )
except Exception as e:
    print(f"Email failed: {e}")

# ------------------ SAVE SENT JOBS ------------------
with open(SENT_FILE, "w") as f:
    json.dump(sent_jobs, f)