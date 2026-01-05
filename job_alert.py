import requests
from bs4 import BeautifulSoup
import pandas as pd
import yagmail
import os

# ---- CONFIGURATION ---- #
# Email credentials
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
TO_EMAIL = GMAIL_USER  # send to yourself

# ---- JOB BOARDS TO SCRAPE ---- #
JOB_BOARDS = [
    {"name": "RemoteOK", "url": "https://remoteok.com/remote-customer-support-jobs"},
    {"name": "WeWorkRemotely", "url": "https://weworkremotely.com/categories/remote-customer-support-jobs"},
    {"name": "StartupJobs", "url": "https://startup.jobs/remote-jobs/customer-support"},
    {"name": "Indeed Canada", "url": "https://ca.indeed.com/jobs?q=Customer+Service+Representative&l=Remote"},
    {"name": "Indeed USA", "url": "https://www.indeed.com/jobs?q=Customer+Service+Representative&l=Remote"},
    {"name": "Glassdoor UK", "url": "https://www.glassdoor.co.uk/Job/remote-customer-service-jobs-SRCH_IL.0,2_IS11047_KO3,20.htm"}
]

# Helper to extract sample keywords and skills
def extract_keywords_skills(title, description):
    words = title.split() + description.split()
    keywords = words[:5]
    skills = words[5:10]
    return keywords, skills

# ---- SCRAPING JOBS ---- #
all_jobs = []

for board in JOB_BOARDS:
    try:
        response = requests.get(board["url"], headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"Failed to fetch {board['name']}")
            continue
        soup = BeautifulSoup(response.text, "lxml")

        # Simplified scraping logic: adapt for each site if needed
        jobs = soup.find_all("a", href=True)
        for job in jobs[:10]:  # first 10 jobs per board
            title = job.get_text(strip=True)
            link = job["href"]
            if not link.startswith("http"):
                link = f"https://{board['name'].lower().replace(' ', '')}.com{link}"

            # Filter for Customer Care / Customer Support
            if any(keyword.lower() in title.lower() for keyword in ["customer", "support", "care", "representative"]):
                keywords, skills = extract_keywords_skills(title, title)
                all_jobs.append({
                    "Company": board["name"],
                    "Role": title,
                    "Direct Link": link,
                    "Keywords": ", ".join(keywords),
                    "Skills": ", ".join(skills)
                })
    except Exception as e:
        print(f"Error fetching {board['name']}: {e}")

# ---- CREATE DATAFRAME AND CSV ---- #
df = pd.DataFrame(all_jobs)
csv_filename = "daily_jobs.csv"
df.to_csv(csv_filename, index=False)

# ---- CREATE HTML TABLE ---- #
html_table = df.to_html(index=False)

# ---- SEND EMAIL ---- #
try:
    yag = yagmail.SMTP(user=GMAIL_USER, password=GMAIL_APP_PASSWORD)
    subject = "Daily Remote Customer Care Job Alert"
    contents = [
        "<h2>Here are the latest Customer Care job listings (Global / Remote):</h2>",
        html_table,
        f"\nCSV attached: {csv_filename}"
    ]
    yag.send(to=TO_EMAIL, subject=subject, contents=contents, attachments=csv_filename)
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")

