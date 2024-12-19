from flask_login import UserMixin
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data
        
    def get_id(self):
        return str(self.user_data.get('_id'))
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    @staticmethod
    def get_by_id(db, user_id):
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        return User(user_data) if user_data else None
    
    @staticmethod
    def get_by_email(db, email):
        user_data = db.users.find_one({'email': email})
        return User(user_data) if user_data else None
