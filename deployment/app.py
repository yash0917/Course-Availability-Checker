import streamlit as st
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
import threading

# Mailtrap credentials
mailtrap_user = "api"
mailtrap_pass = "0c51efc1b8ee06372e37b2b4085cca8e"
mailtrap_host = "live.smtp.mailtrap.io"
mailtrap_port = 587
sender = "Private Person <mailtrap@demomailtrap.com>"

# Set timezone to PST
pst = pytz.timezone('US/Pacific')

def send_email(receiver, subject, message):
    msg = f"""\
Subject: {subject}
To: {receiver}
From: {sender}

{message}"""

    try:
        with smtplib.SMTP(mailtrap_host, mailtrap_port) as server:
            server.starttls()
            server.login(mailtrap_user, mailtrap_pass)
            server.sendmail(sender, receiver, msg)
        print("Notification email sent successfully.")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def check_course_availability(url, receiver):
    while True:
        current_time = datetime.now(pst).time()
        start_time = datetime.strptime("04:35", "%H:%M").time()
        end_time = datetime.strptime("19:35", "%H:%M").time()

        if start_time <= current_time <= end_time:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                sections = soup.find_all('div', class_='section')
                for section in sections:
                    instructor_tag = section.find('span', class_='section-instructor')
                    if instructor_tag:
                        instructor = instructor_tag.text.strip()
                        seats_available_tag = section.find('span', class_='open-seats-count')
                        if seats_available_tag:
                            seats_available = int(seats_available_tag.text)
                            if seats_available > 0:
                                subject = "Course Seat Availability Notification"
                                message = f"Seats are available for the course with {instructor}! Open seats: {seats_available}"
                                send_email(receiver, subject, message)
                                return
            else:
                print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        else:
            print("Outside of checking hours.")
        time.sleep(1800)  # Check every 30 minutes

def main():
    st.title("Course Availability Notifier")

    name = st.text_input("Name")
    email = st.text_input("Email")
    url = st.text_input("URL to Scrape")

    if st.button("Submit"):
        if name and email and url:
            st.success(f"Thank you, {name}! You will be notified at {email} when a seat becomes available.")
            thread = threading.Thread(target=check_course_availability, args=(url, email))
            thread.start()
        else:
            st.error("Please fill out all fields.")

if __name__ == "__main__":
    main()
