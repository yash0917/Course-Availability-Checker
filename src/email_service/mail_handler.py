import smtplib
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.sender_email = os.getenv('NOTIFICATION_EMAIL')

        if not self.smtp_host or not self.smtp_port or not self.smtp_username or not self.smtp_password or not self.sender_email:
            logging.error("Email service credentials (SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, or NOTIFICATION_EMAIL) are not set.")
            raise ValueError("Email service credentials are not configured.")

    def send_email(self, receiver_email, subject, body):
        message = f"""\
Subject: {subject}
To: {receiver_email}
From: {self.sender_email}

{body}"""

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_email, receiver_email, message)
            logging.info(f"Email sent successfully to {receiver_email} with subject: {subject}")
            return True
        except smtplib.SMTPException as e:
            logging.error(f"SMTP error occurred when sending email to {receiver_email}: {e}")
            return False
        except Exception as e:
            logging.error(f"An unexpected error occurred when sending email to {receiver_email}: {e}")
            return False