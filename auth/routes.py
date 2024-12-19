from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from config.database import db
import re
from datetime import datetime
from .email_utils import (
    email_sender,  # For direct access to EmailSender instance
    send_email,    # For backward compatibility
    send_otp_email,
    send_password_reset_email,
    send_login_alert,
    send_welcome_email
)
from .otp_utils import generate_otp, store_otp, verify_otp

auth = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not email or not password or not confirm_password:
            flash('All fields are required', 'error')
            return redirect(url_for('auth.register'))

        if not is_valid_email(email):
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('auth.register'))

        if not is_valid_password(password):
            flash('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers', 'error')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.register'))

        existing_user = db.get_user_by_email(email)
        if existing_user:
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        user_result = db.create_user(email, hashed_password)
        
        # Send welcome email
        dashboard_link = url_for('mino.dashboard', _external=True)
        try:
            send_welcome_email(email, email.split('@')[0], dashboard_link)
        except Exception as e:
            current_app.logger.error(f"Failed to send welcome email: {e}")
            
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('mino/auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please enter both email and password', 'error')
            return redirect(url_for('auth.login'))

        user_data = db.get_user_by_email(email)
        # Check if admin credentials
        if email == "mino-enclave" and password == "6307232833@mino-enclave":
            return redirect(url_for('admin.login', username=email, password=password, next='/admin/dashboard'))
            
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)
            # Update last login time
            db.update_last_login(user.get_id())
            
            # Send login alert email
            try:
                login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ip_address = request.remote_addr
                device = request.headers.get('User-Agent', 'Unknown Device')
                location = "Unknown Location"  # You could use a geolocation service here
                account_security_link = url_for('auth.complete_profile', _external=True)
                
                send_login_alert(email, login_time, ip_address, device, location, account_security_link)
            except Exception as e:
                current_app.logger.error(f"Failed to send login alert email: {e}")
            
            if not user_data.get('name'):
                return redirect(url_for('auth.complete_profile'))
            return redirect(url_for('mino.dashboard'))
        
        flash('Invalid email or password', 'error')
        return redirect(url_for('auth.login'))

    return render_template('mino/auth/login.html')

@auth.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    email = request.form.get('email')
    if not email:
        flash('Email is required', 'error')
        return redirect(url_for('auth.login'))

    if not is_valid_email(email):
        flash('Please enter a valid email address', 'error')
        return redirect(url_for('auth.login'))

    # Check if user exists
    user = db.get_user_by_email(email)
    if not user:
        # Don't reveal if email exists, just show generic message
        flash('If the email exists, an OTP will be sent.', 'info')
        return render_template('mino/auth/login.html', show_otp_form=True)

    try:
        # Generate and store OTP
        otp = generate_otp()
        current_app.logger.info(f"Generated OTP for {email}")
        
        # Store OTP first
        try:
            store_otp(email, otp)
            current_app.logger.info(f"Stored OTP for {email}")
        except Exception as e:
            current_app.logger.error(f"Failed to store OTP: {e}")
            flash('Failed to generate OTP. Please try again.', 'error')
            return render_template('mino/auth/login.html')
        
        # Store email in session before sending
        session['reset_email'] = email
        current_app.logger.info(f"Stored email in session for {email}")
        
        # Generate reset link
        reset_link = url_for('auth.reset_password', email=email, _external=True)
        
        # Send password reset email with OTP
        if send_password_reset_email(email, reset_link):
            current_app.logger.info(f"Successfully sent OTP email to {email}")
            flash('An OTP has been sent to your email. Please check your inbox and spam folder.', 'success')
            return render_template('mino/auth/login.html', show_otp_form=True)
        else:
            current_app.logger.error(f"Failed to send email to {email}")
            flash('Failed to send OTP email. Please try again.', 'error')
            return render_template('mino/auth/login.html')
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in password reset: {e}")
        flash('An unexpected error occurred. Please try again later.', 'error')
        return render_template('mino/auth/login.html')

@auth.route('/verify-otp', methods=['POST'])
def verify_otp():
    email = request.form.get('email')
    otp = request.form.get('otp')
    
    if not email or not otp:
        flash('Email and OTP are required', 'error')
        return render_template('mino/auth/login.html', show_otp_form=True)
    
    # Verify email matches the one in session
    if email != session.get('reset_email'):
        flash('Invalid request', 'error')
        return redirect(url_for('auth.login'))

    if verify_otp(email, otp):
        # Clear the session
        session.pop('reset_email', None)
        return redirect(url_for('auth.reset_password', email=email))
    else:
        flash('Invalid OTP. Please try again.', 'error')
        return render_template('mino/auth/login.html', show_otp_form=True)

@auth.route('/reset-password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    # Verify user exists
    user = db.get_user_by_email(email)
    if not user:
        flash('Invalid reset link', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or not confirm_password:
            flash('Both password fields are required', 'error')
            return redirect(url_for('auth.reset_password', email=email))

        if not is_valid_password(new_password):
            flash('Password must be at least 8 characters long and contain uppercase, lowercase, and numbers', 'error')
            return redirect(url_for('auth.reset_password', email=email))

        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth.reset_password', email=email))

        hashed_password = generate_password_hash(new_password)
        db.update_user_password(email, hashed_password)
        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('mino/auth/reset_password.html', email=email)

@auth.route('/complete-profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        mobile = request.form.get('mobile')

        if not name:
            flash('Name is required', 'error')
            return redirect(url_for('auth.complete_profile'))

        db.update_user_profile(current_user.get_id(), name, mobile)
        flash('Profile completed successfully!', 'success')
        return redirect(url_for('mino.dashboard'))

    return render_template('mino/auth/complete_profile.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('mino.dashboard'))
