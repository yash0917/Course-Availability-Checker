from flask import Flask, render_template, request, jsonify
import os
from database.db_handler import DBHandler
import logging

app = Flask(__name__, root_path=os.path.join(os.path.dirname(os.path.abspath(__file__))), template_folder='templates')

# Initialize DBHandler
db_handler = DBHandler(os.getenv("MONGODB_URI"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == 'POST':
        try:
            course_id = request.form['course_id']
            email = request.form['email']
            section_id = request.form.get('section_id') # Optional
            preferred_instructors = request.form.get('preferred_instructors', '').split(',') # Optional, split by comma

            # Call add_user instead of add_tracker
            db_handler.add_user(email, preferred_instructors, course_id, section_id)
            return jsonify({"message": "Tracking added successfully!"}), 200
        except Exception as e:
            logging.error(f"Error processing track form: {e}")
            return jsonify({"error": "Failed to add tracking. Please try again later."}), 500
    return render_template('track.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0') 