import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()


def send_email_to_boss(email_subject: str, email_content: str, pdf_path: str):
    """
    Send email to boss with PDF attachment.

    Args:
        email_subject: Subject line from LLM output
        email_content: Email body content from LLM output
        pdf_path: Path to the PDF file to attach
    """
    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    boss_email = os.getenv("BOSS_EMAIL")

    if not all([email, password, boss_email]):
        print("Error: Missing email configuration in .env file")
        print("Required: EMAIL_ADDRESS, EMAIL_PASSWORD, BOSS_EMAIL")
        return False

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return False

    msg = EmailMessage()
    msg['From'] = email
    msg['To'] = boss_email
    msg['Subject'] = email_subject
    msg.set_content(email_content)

    # Attach PDF
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
        pdf_name = os.path.basename(pdf_path)
        msg.add_attachment(
            pdf_data,
            maintype='application',
            subtype='pdf',
            filename=pdf_name
        )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email, password)
            server.send_message(msg)
        print(f"Email sent successfully to {boss_email}!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_test_email(email_subject: str, email_content: str, pdf_path: str = None, tracking_id: str = None):
    """
    Send a test email to yourself (EMAIL_ADDRESS) with optional PDF attachment and tracking.

    Args:
        email_subject: Subject line from LLM output
        email_content: Email body content from LLM output
        pdf_path: Optional path to the PDF file to attach
        tracking_id: Optional tracking ID for analytics
    """
    email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    if not all([email, password]):
        print("Error: Missing email configuration in .env file")
        print("Required: EMAIL_ADDRESS, EMAIL_PASSWORD")
        return False

    # Plain text version
    plain_content = email_content

    # HTML version with tracking
    html_content = email_content.replace('\n', '<br>')

    # Add tracking pixel if tracking_id provided
    if tracking_id:
        tracking_pixel = f'<img src="http://localhost:8000/track/open/{tracking_id}" width="1" height="1" style="display:none;" />'
        html_content += tracking_pixel

        # Replace Calendly link with tracked version
        if "calendly.com" in email_content:
            import urllib.parse
            original_url = "https://calendly.com/kasper-fermaniq"
            tracked_url = f"http://localhost:8000/track/click/{tracking_id}?url={urllib.parse.quote(original_url)}"
            html_content = html_content.replace(original_url, tracked_url)
            plain_content = plain_content.replace(original_url, tracked_url)

    msg = EmailMessage()
    msg['From'] = email
    msg['To'] = email  # Send to yourself for testing
    msg['Subject'] = f"[TEST] {email_subject}"
    msg.set_content(plain_content)  # Plain text version
    msg.add_alternative(html_content, subtype='html')  # HTML version with tracking

    # Attach PDF if provided and exists
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
            pdf_name = os.path.basename(pdf_path)
            msg.add_attachment(
                pdf_data,
                maintype='application',
                subtype='pdf',
                filename=pdf_name
            )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email, password)
            server.send_message(msg)
        print(f"Test email sent successfully to {email}!")
        return True
    except Exception as e:
        print(f"Failed to send test email: {e}")
        return False