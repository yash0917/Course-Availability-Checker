from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from src.database.db_handler import DatabaseHandler
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='src/templates')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-please-change')
Bootstrap(app)

db = DatabaseHandler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track', methods=['GET', 'POST'])
def track_course():
    if request.method == 'POST':
        email = request.form.get('email')
        course_id = request.form.get('course_id')
        preferred_instructors = request.form.get('preferred_instructors').split(',')
        section_id = request.form.get('section_id') or None

        # Add user preferences to database
        db.add_user(email, preferred_instructors, course_id, section_id)
        flash('Course tracking has been set up! You will receive email notifications when seats become available.', 'success')
        return redirect(url_for('index'))

    return render_template('track.html')

@app.route('/manage')
def manage_preferences():
    email = request.args.get('email')
    if not email:
        return redirect(url_for('index'))
    
    # Get user's active trackings
    user_preferences = db.get_active_users()
    return render_template('manage.html', preferences=user_preferences)

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    email = request.form.get('email')
    course_id = request.form.get('course_id')
    db.deactivate_user(email, course_id)
    flash('You have been unsubscribed from course notifications.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 