import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime
import pytz
from dotenv import load_dotenv
import logging

from src.database.db_handler import DatabaseHandler
from src.email_service.mail_handler import EmailService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Initialize database and email handlers
db = DatabaseHandler()
email_service = EmailService()

# Get configurable parameters from environment variables
PST_TIMEZONE = os.getenv('TIMEZONE', 'US/Pacific')
SCRAPER_START_TIME = os.getenv('SCRAPER_START_TIME', '04:35')
SCRAPER_END_TIME = os.getenv('SCRAPER_END_TIME', '19:35')
SCRAPER_INTERVAL_MINUTES = int(os.getenv('SCRAPER_INTERVAL_MINUTES', 60))

# Set timezone
pst = pytz.timezone(PST_TIMEZONE)

def check_course_availability():
    current_time = datetime.now(pst).time()
    start_time = datetime.strptime(SCRAPER_START_TIME, "%H:%M").time()
    end_time = datetime.strptime(SCRAPER_END_TIME, "%H:%M").time()

    if start_time <= current_time <= end_time:
        logging.info("Scraper active within the defined time window.")
        # Get all active users and their preferences
        active_users = db.get_active_users()
        
        for user in active_users:
            course_id = user['course_id']
            preferred_instructors = user['preferred_instructors']
            user_email = user['email']
            
            url = f"https://app.testudo.umd.edu/soc/search?courseId={course_id}&sectionId=&termId=202408&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"
            
            try:
                response = requests.get(url, timeout=10) # Added timeout
                response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
                
                soup = BeautifulSoup(response.content, 'html.parser')
                sections = soup.find_all('div', class_='section')
                
                for section in sections:
                    instructor_tag = section.find('span', class_='section-instructor')
                    instructor = instructor_tag.text.strip() if instructor_tag else "N/A"

                    if preferred_instructors and instructor not in preferred_instructors:
                        continue # Skip if instructor not preferred

                    seats_available_tag = section.find('span', class_='open-seats-count')
                    if seats_available_tag:
                        try:
                            seats_available = int(seats_available_tag.text)
                            section_id = section.get('id', '').replace('section-', '')
                            
                            # Update course status in database
                            db.update_course_status(course_id, section_id, instructor, seats_available)
                            
                            if seats_available > 0:
                                notify_user(user_email, instructor, seats_available, course_id, section_id)
                        except ValueError:
                            logging.error(f"Could not parse seats available for {course_id}-{section.get('id')}")
                    else:
                        logging.info(f"No seats availability information found for {course_id}-{section.get('id')}")

            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to retrieve webpage for course {course_id}: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred while scraping {course_id}: {e}")
    else:
        logging.info("Scraper is outside the defined time window.")

def notify_user(email, instructor, seats_available, course_id, section_id):
    subject = f"Course Seat Available: {course_id} Section {section_id}"
    body = f"Seats are available for {course_id} with {instructor}!\nOpen seats: {seats_available}"
    email_service.send_email(email, subject, body)

# Schedule the scraper
schedule.every(SCRAPER_INTERVAL_MINUTES).minutes.do(check_course_availability)

if __name__ == "__main__":
    logging.info("Starting Testudo Course Scraper...")
    while True:
        schedule.run_pending()
        time.sleep(1)
