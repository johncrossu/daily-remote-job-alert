import requests
import json
import os
import yagmail
import pandas as pd

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

# ------------------ SERPAPI (GOOGLE JOBS) ------------------
def fetch_customer_care_jobs():
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_jobs",
        "q": "Remote Customer Care Representative Nigeria Global",
        "api_key": SERPAPI_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    allowed_titles = [
        "customer care",
        "customer support",
        "customer service",
        "customer representative",
        "support representative",
        "call center"
    ]

    allowed_locations = [
        "nigeria",
        "global",
        "worldwide",
        "anywhere",
        "remote",
        "africa"
    ]

    blocked_locations = [
        "us only",
        "canada only",
        "uk only",
        "europe only",
        "united states only"
    ]

    for job in data.get("jobs_results", []):
        title = (job.get("title") or "").lower()
        link = job.get("link")
        company = job.get("organization")

        text = (
            (job.get("location") or "") + " " +
            (job.get("description") or "")
        ).lower()

        if not any(t in title for t in allowed_titles):
            continue

        if any(b in text for b in blocked_locations):
            continue

        if not any(a in text for a in allowed_locations):
            continue

        if link and link not in sent_jobs:
            new_jobs.append({
                "Job Title": job.get("title"),
                "Company": company,
                "Apply": f'<a href="{link}">Apply</a>'
            })
            sent_jobs.append(link)

# ------------------ RUN ------------------
fetch_customer_care_jobs()

if not new_jobs:
    yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)
    yag.send(
        to=GMAIL_USER,
        subject="Customer Care Job Alert",
        contents="No new Nigeria-eligible customer care jobs found at this time."
    )
    exit()

# ------------------ EMAIL ------------------
df = pd.DataFrame(new_jobs)
html = df.to_html(index=False, escape=False)

yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)
yag.send(
    to=GMAIL_USER,
    subject="🔥 Remote Customer Care Jobs (Nigeria / Global)",
    contents=[
        "<h3>Customer Care / Support Jobs (Nigeria & Global)</h3>",
        html
    ]
)

with open(SENT_FILE, "w") as f:
    json.dump(sent_jobs, f)