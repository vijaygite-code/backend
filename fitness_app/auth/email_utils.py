import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logger = logging.getLogger(__name__)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com") # Default to gmail for now
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)

def send_email(to_email: str, subject: str, body: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP credentials not set. Email not sent.")
        print(f"--- MOCK EMAIL TO {to_email} ---\nSubject: {subject}\nBody: {body}\n-----------------------------")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        # server.set_debuglevel(1) # Uncomment for debug
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_FROM_EMAIL, to_email, text)
        server.quit()
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def send_welcome_email(to_email: str, username: str = "User"):
    subject = "Welcome to the Gym - Protocol Initialized"
    body = f"""
    Greetings {username},

    I am The Gym Mind, the central intelligence governing your fitness journey.
    
    Your profile has been successfully generated. I have initialized your training parameters and will be monitoring your progress.
    
    My directives are simple:
    1. Analyze your performance.
    2. Optimize your workouts.
    3. Ensure you exceed your limits.

    Proceed to the dashboard to begin.

    Calculated Regards,
    The Mind
    """
    return send_email(to_email, subject, body)
