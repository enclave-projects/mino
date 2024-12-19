from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, current_user
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import os
from models.user import User
from config.database import db
from auth.routes import auth
from mino.routes import mino

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Set session lifetime to 1 hour

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')

# Set up file handler
file_handler = RotatingFileHandler('logs/mino.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

# Set up console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)

# Add handlers to app logger
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Mino Password Manager startup')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user_by_id(user_id)
    return User(user_data) if user_data else None

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(mino, url_prefix='/mino')

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('mino.dashboard'))
    return render_template('index.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms-of-service.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Template filters
@app.template_filter('format_date')
def format_date(value):
    if isinstance(value, datetime):
        return value.strftime('%B %d, %Y')
    return value

#if __name__ == '__main__':
#    app.run(debug=True)
