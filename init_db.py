from pymongo import MongoClient, ASCENDING
from datetime import datetime

def init_database():
    # Connect to MongoDB
    client = MongoClient("mongodb+srv://pasx:xsap@pasx.c0fab.mongodb.net/?retryWrites=true&w=majority&appName=PasX")
    db = client.mino_passwords

    # Create collections if they don't exist
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
    if 'passwords' not in db.list_collection_names():
        db.create_collection('passwords')

    # Create indexes
    # Users collection indexes
    db.users.create_index([('email', ASCENDING)], unique=True)
    db.users.create_index([('created_at', ASCENDING)])

    # Passwords collection indexes
    db.passwords.create_index([('user_id', ASCENDING)])
    db.passwords.create_index([('service_name', ASCENDING)])
    db.passwords.create_index([('created_at', ASCENDING)])

    print("Database initialization completed successfully!")
    
    # Create test user if it doesn't exist
    test_user = db.users.find_one({'email': 'test@example.com'})
    if not test_user:
        db.users.insert_one({
            'email': 'test@example.com',
            'password': 'pbkdf2:sha256:260000$TEST_HASH',  # This is just a placeholder, not a real hash
            'name': 'Test User',
            'created_at': datetime.utcnow()
        })
        print("Test user created!")

if __name__ == '__main__':
    init_database()
