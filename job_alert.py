import os
import requests
import pandas as pd
import json
import feedparser
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To

# ------------------ ENV ------------------
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
EMAIL_TO = os.environ.get("EMAIL_TO")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
SENT_FILE = "sent_jobs.json"

# ------------------ LOAD SENT JOBS ------------------
if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r") as f:
        sent_jobs = json.load(f)
else:
    sent_jobs = []

new_jobs = []

# ------------------ HELPER ------------------
def add_job(title, company, link):
    if link not in sent_jobs:
        new_jobs.append({
            "Job Title": title,
            "Company": company,
            "Apply": f'<a href="{link}">Apply</a>'
        })
        sent_jobs.append(link)

# ------------------ FETCH SERPAPI ------------------
def fetch_jobs_serpapi():
    if not SERPAPI_KEY:
        return
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

    allowed_titles = ["customer care", "customer support", "customer service", "customer representative", "call center"]

    for job in data.get("jobs_results", []):
        title = (job.get("title") or "").lower()
        company = job.get("organization")
        link = job.get("link")
        if any(t in title for t in allowed_titles):
            add_job(job.get("title"), company, link)

# ------------------ FETCH REMOTIVE ------------------
def fetch_jobs_remotive():
    try:
        res = requests.get("https://remotive.io/api/remote-jobs", timeout=15)
        data = res.json()
    except Exception as e:
        print(f"Remotive fetch failed: {e}")
        return

    allowed_titles = ["customer care", "customer support", "customer service", "customer representative", "call center"]
    for job in data.get("jobs", []):
        title = job.get("title").lower()
        company = job.get("company_name")
        link = job.get("url")
        if any(t in title for t in allowed_titles):
            add_job(job.get("title"), company, link)

# ------------------ FETCH WWR ------------------
def fetch_jobs_wwr():
    feed_url = "https://weworkremotely.com/categories/remote-customer-support-jobs.rss"
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        print(f"WWR fetch failed: {e}")
        return

    for entry in feed.entries:
        add_job(entry.title, entry.get("author", "Unknown"), entry.link)

# ------------------ RUN ALL ------------------
fetch_jobs_serpapi()
fetch_jobs_remotive()
fetch_jobs_wwr()

# ------------------ SEND EMAIL ------------------
try:
    if not new_jobs:
        content_html = "<p>No new customer care jobs found at this time. Will keep checking.</p>"
    else:
        df = pd.DataFrame(new_jobs)
        content_html = "<h3>Remote Customer Care / Support Jobs</h3>" + df.to_html(index=False, escape=False)

    message = Mail(
        from_email=Email("alerts@sendgrid.net"),
        to_emails=To(EMAIL_TO),
        subject=f"🔥 Remote Customer Care Jobs ({len(new_jobs)} new)",
        html_content=content_html
    )

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print(f"✅ Email sent: status {response.status_code}")
except Exception as e:
    print(f"❌ Email failed: {e}")

# ------------------ SAVE SENT ------------------
with open(SENT_FILE, "w") as f:
    json.dump(sent_jobs, f)