from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

class Database:
    def __init__(self, mongo_uri):
        try:
            # Connect with proper options
            self.client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                retryWrites=True
            )
            # Get the database
            self.db = self.client.mino_passwords
            # Test the connection
            self.db.command('ping')
            print("Successfully connected to MongoDB Atlas")
        except ServerSelectionTimeoutError:
            print("Could not connect to MongoDB Atlas. Please check your internet connection and MongoDB Atlas status.")
            raise
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB Atlas: {str(e)}")
            raise
        except Exception as e:
            print(f"An error occurred while connecting to MongoDB Atlas: {str(e)}")
            raise

    def get_user_passwords(self, user_id):
        return list(self.db.passwords.find({'user_id': ObjectId(user_id)}))

    def add_password(self, user_id, service_name, username, password):
        return self.db.passwords.insert_one({
            'user_id': ObjectId(user_id),
            'service_name': service_name,
            'username': username,
            'password': password,
            'created_at': datetime.utcnow()
        })

    def update_password(self, password_id, service_name, username, password):
        return self.db.passwords.update_one(
            {'_id': ObjectId(password_id)},
            {
                '$set': {
                    'service_name': service_name,
                    'username': username,
                    'password': password,
                    'updated_at': datetime.utcnow()
                }
            }
        )

    def delete_password(self, password_id):
        return self.db.passwords.delete_one({'_id': ObjectId(password_id)})

    def get_password_by_id(self, password_id):
        return self.db.passwords.find_one({'_id': ObjectId(password_id)})

    def create_user(self, email, password_hash):
        return self.db.users.insert_one({
            'email': email,
            'password': password_hash,
            'created_at': datetime.utcnow(),
            'last_login': None
        })

    def update_last_login(self, user_id):
        return self.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'last_login': datetime.utcnow()}}
        )

    def update_user_profile(self, user_id, name, mobile=None):
        update_data = {
            'name': name,
            'updated_at': datetime.utcnow()
        }
        if mobile:
            update_data['mobile'] = mobile

        return self.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )

    def get_user_by_email(self, email):
        return self.db.users.find_one({'email': email})

    def get_user_by_id(self, user_id):
        return self.db.users.find_one({'_id': ObjectId(user_id)})
        
    def update_user_password(self, email, new_password_hash):
        return self.db.users.update_one(
            {'email': email},
            {'$set': {
                'password': new_password_hash,
                'updated_at': datetime.utcnow()
            }}
        )

# Initialize database with MongoDB Atlas URI
MONGO_URI = "mongodb+srv://pasx:xsap@pasx.c0fab.mongodb.net/?retryWrites=true&w=majority&appName=PasX"
db = Database(MONGO_URI)
