import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
EMAIL_TO = os.environ.get("EMAIL_TO")

try:
    message = Mail(
        from_email=Email("johncrossugwuegede@gmail.com"),  # verified sender
        to_emails=To(EMAIL_TO),
        subject="✅ SendGrid Test Email",
        html_content="<p>This is a test email from GitHub Actions via SendGrid.</p>"
    )
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print(f"Email sent successfully! Status code: {response.status_code}")
except Exception as e:
    print(f"❌ Email failed: {e}")