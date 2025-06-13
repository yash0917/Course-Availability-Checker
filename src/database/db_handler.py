import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Global MongoClient instance
_mongo_client = None

class DatabaseHandler:
    def __init__(self):
        global _mongo_client
        if _mongo_client is None:
            try:
                # Get MongoDB connection string from environment variables
                mongo_uri = os.getenv('MONGODB_URI')
                if not mongo_uri:
                    raise ValueError("MONGODB_URI environment variable not set.")
                _mongo_client = MongoClient(mongo_uri)
                # The ismaster command is cheap and does not require auth.
                _mongo_client.admin.command('ismaster')
                logging.info("Successfully connected to MongoDB.")
            except ConnectionFailure as e:
                logging.error(f"MongoDB connection failed: {e}")
                _mongo_client = None
                raise ConnectionFailure("Could not connect to MongoDB. Please check MONGODB_URI and network access.") from e
            except Exception as e:
                logging.error(f"An unexpected error occurred during MongoDB connection: {e}")
                _mongo_client = None
                raise

        if _mongo_client:
            self.client = _mongo_client
            # Consider making these configurable via environment variables if needed for open source flexibility
            self.db = self.client.get_database(os.getenv('MONGODB_DB_NAME', 'testudo_scraper'))
            self.users = self.db.get_collection(os.getenv('MONGODB_USERS_COLLECTION', 'users'))
            self.courses = self.db.get_collection(os.getenv('MONGODB_COURSES_COLLECTION', 'courses'))
        else:
            raise ConnectionFailure("MongoDB client is not initialized.")

    def add_user(self, email, preferred_instructors, course_id, section_id=None):
        """Add or update a user's course preferences"""
        try:
            user_data = {
                'email': email,
                'preferred_instructors': preferred_instructors,
                'course_id': course_id,
                'section_id': section_id,
                'active': True
            }
            self.users.update_one(
                {'email': email, 'course_id': course_id},
                {'$set': user_data},
                upsert=True
            )
            logging.info(f"User {email} tracking course {course_id} added/updated successfully.")
        except PyMongoError as e:
            logging.error(f"Error adding/updating user {email} for course {course_id}: {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred in add_user: {e}")
            raise

    def get_active_users(self):
        """Get all active users and their preferences"""
        try:
            return list(self.users.find({'active': True}))
        except PyMongoError as e:
            logging.error(f"Error getting active users: {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred in get_active_users: {e}")
            raise

    def update_course_status(self, course_id, section_id, instructor, seats_available):
        """Update course availability information"""
        try:
            course_data = {
                'course_id': course_id,
                'section_id': section_id,
                'instructor': instructor,
                'seats_available': seats_available,
                'last_updated': datetime.utcnow()
            }
            self.courses.update_one(
                {'course_id': course_id, 'section_id': section_id},
                {'$set': course_data},
                upsert=True
            )
            logging.info(f"Course {course_id} section {section_id} status updated successfully.")
        except PyMongoError as e:
            logging.error(f"Error updating course status for {course_id}-{section_id}: {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred in update_course_status: {e}")
            raise

    def get_course_status(self, course_id, section_id=None):
        """Get current status of a course"""
        try:
            query = {'course_id': course_id}
            if section_id:
                query['section_id'] = section_id
            return list(self.courses.find(query))
        except PyMongoError as e:
            logging.error(f"Error getting course status for {course_id}-{section_id}: {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred in get_course_status: {e}")
            raise

    def deactivate_user(self, email, course_id):
        """Deactivate a user's course tracking"""
        try:
            self.users.update_one(
                {'email': email, 'course_id': course_id},
                {'$set': {'active': False}}
            )
            logging.info(f"User {email} tracking course {course_id} deactivated successfully.")
        except PyMongoError as e:
            logging.error(f"Error deactivating user {email} for course {course_id}: {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred in deactivate_user: {e}")
            raise 