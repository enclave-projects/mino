from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from config.database import db
import secrets
import string

mino = Blueprint('mino', __name__)

def generate_secure_password(length=16):
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*"
    
    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]
    
    # Fill the rest with random characters from all sets
    all_characters = lowercase + uppercase + digits + special
    for _ in range(length - 4):
        password.append(secrets.choice(all_characters))
    
    # Shuffle the password
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

@mino.route('/dashboard')
@login_required
def dashboard():
    passwords = db.get_user_passwords(current_user.get_id())
    return render_template('mino/dashboard.html', passwords=passwords)

@mino.route('/add-password', methods=['GET', 'POST'])
@login_required
def add_password():
    if request.method == 'POST':
        service_name = request.form.get('service_name')
        username = request.form.get('username')
        password = request.form.get('password')
        use_generated = request.form.get('use_generated') == 'true'

        if not service_name or not username:
            flash('Service name and username are required', 'error')
            return redirect(url_for('mino.add_password'))

        if use_generated:
            password = generate_secure_password()
        elif not password:
            flash('Password is required', 'error')
            return redirect(url_for('mino.add_password'))

        db.add_password(current_user.get_id(), service_name, username, password)
        flash('Password saved successfully!', 'success')
        return redirect(url_for('mino.dashboard'))

    return render_template('mino/add_password.html')

@mino.route('/edit-password/<password_id>', methods=['GET', 'POST'])
@login_required
def edit_password(password_id):
    password_entry = db.get_password_by_id(password_id)
    if not password_entry or str(password_entry['user_id']) != current_user.get_id():
        flash('Password not found or access denied', 'error')
        return redirect(url_for('mino.dashboard'))

    if request.method == 'POST':
        service_name = request.form.get('service_name')
        username = request.form.get('username')
        password = request.form.get('password')
        use_generated = request.form.get('use_generated') == 'true'

        if not service_name or not username:
            flash('Service name and username are required', 'error')
            return redirect(url_for('mino.edit_password', password_id=password_id))

        if use_generated:
            password = generate_secure_password()
        elif not password:
            flash('Password is required', 'error')
            return redirect(url_for('mino.edit_password', password_id=password_id))

        db.update_password(password_id, service_name, username, password)
        flash('Password updated successfully!', 'success')
        return redirect(url_for('mino.dashboard'))

    return render_template('mino/edit_password.html', password=password_entry)

@mino.route('/delete-password/<password_id>', methods=['POST'])
@login_required
def delete_password(password_id):
    password_entry = db.get_password_by_id(password_id)
    if not password_entry or str(password_entry['user_id']) != current_user.get_id():
        flash('Password not found or access denied', 'error')
        return redirect(url_for('mino.dashboard'))
    
    db.delete_password(password_id)
    flash('Password deleted successfully!', 'success')
    return redirect(url_for('mino.dashboard'))

@mino.route('/password/<password_id>/view')
@login_required
def view_password(password_id):
    password_entry = db.get_password_by_id(password_id)
    if not password_entry or str(password_entry['user_id']) != current_user.get_id():
        return jsonify({'error': 'Password not found or access denied'}), 403
    return jsonify({'password': password_entry['password']})

@mino.route('/password/generate')
@login_required
def generate_password():
    password = generate_secure_password()
    return jsonify({'password': password})
