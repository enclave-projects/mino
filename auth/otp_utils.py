from datetime import datetime, timedelta
import random
import string
from config.database import db

def generate_otp(length=6):
    """Generate a numeric OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def store_otp(email, otp):
    """Store OTP with expiration time (10 minutes from now)"""
    expiry = datetime.utcnow() + timedelta(minutes=10)
    db.db.otps.insert_one({
        'email': email,
        'otp': otp,
        'expiry': expiry
    })

def verify_otp(email, otp):
    """Verify OTP and check if it's still valid"""
    otp_record = db.db.otps.find_one({
        'email': email,
        'otp': otp,
        'expiry': {'$gt': datetime.utcnow()}
    })
    
    if otp_record:
        # Delete the OTP after successful verification
        db.db.otps.delete_one({'_id': otp_record['_id']})
        return True
    
    # Clean up expired OTPs
    db.db.otps.delete_many({'expiry': {'$lte': datetime.utcnow()}})
    return False
