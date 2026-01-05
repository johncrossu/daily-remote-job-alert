# ------------------ TEST EMAIL ------------------
try:
    yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASSWORD)
    print("✅ Connected to Gmail SMTP")

    test_jobs = [{
        "Job Title": "Test Customer Care Job",
        "Company": "Test Company",
        "Apply": '<a href="https://example.com">Apply</a>'
    }]
    df = pd.DataFrame(test_jobs)
    html = df.to_html(index=False, escape=False)

    yag.send(
        to=GMAIL_USER,
        subject="🔥 TEST Remote Customer Care Jobs",
        contents=[
            "<h3>Remote Customer Care / Support Jobs - Test</h3>",
            html
        ]
    )
    print("✅ Test email sent")
except Exception as e:
    print(f"❌ Email failed: {e}")