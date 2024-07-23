import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz

# Mailtrap credentials
mailtrap_user = "api"
mailtrap_pass = "0c51efc1b8ee06372e37b2b4085cca8e"
mailtrap_host = "live.smtp.mailtrap.io"
mailtrap_port = 587
sender = "Private Person <mailtrap@demomailtrap.com>"
receiver = "A Test User <yash.aggy@gmail.com>"

# List of preferred instructors
preferred_instructors = ["Christopher Kauffman", "Nelson Padua-Perez"]

# Set timezone to PST
pst = pytz.timezone('US/Pacific')

def check_course_availability():
    current_time = datetime.now(pst).time()
    start_time = datetime.strptime("04:35", "%H:%M").time()
    end_time = datetime.strptime("19:35", "%H:%M").time()

    if start_time <= current_time <= end_time:
        print("Checking course availability...")
        url = "https://app.testudo.umd.edu/soc/search?courseId=cmsc216&sectionId=&termId=202408&_openSectionsOnly=on&creditCompare=%3E%3D&credits=0.0&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Successfully retrieved the webpage.")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the relevant information about seat availability
            sections = soup.find_all('div', class_='section')
            
            for section in sections:
                instructor_tag = section.find('span', class_='section-instructor')
                if instructor_tag:
                    instructor = instructor_tag.text.strip()
                    if instructor in preferred_instructors:
                        seats_available_tag = section.find('span', class_='open-seats-count')
                        if seats_available_tag:
                            seats_available = int(seats_available_tag.text)
                            print(f"Instructor: {instructor}, Open seats: {seats_available}")
                            if seats_available > 0:
                                notify_user(instructor, seats_available)
                                return  # Exit after first notification
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    else:
        print("Outside of checking hours.")

def notify_user(instructor, seats_available):
    subject = "Course Seat Availability Notification"
    message = f"Seats are available for the course with {instructor}! Open seats: {seats_available}"

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

# Schedule the scraper to run every 30 minutes
schedule.every(60).minutes.do(check_course_availability)

while True:
    schedule.run_pending()
    time.sleep(1)
