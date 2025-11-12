import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@healthcare.local")

def send_email(to_email: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_appointment_confirmation(to_email: str, appointment_details: dict):
    subject = "Appointment Confirmation"
    body = f"""
    <html>
    <body>
        <h2>Appointment Confirmed</h2>
        <p>Your appointment has been scheduled:</p>
        <ul>
            <li><strong>Doctor:</strong> {appointment_details.get('doctor_name')}</li>
            <li><strong>Date:</strong> {appointment_details.get('appointment_date')}</li>
            <li><strong>Reason:</strong> {appointment_details.get('reason')}</li>
        </ul>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)
