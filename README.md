# Mino - Password Manager

Mino is a secure password manager application developed by Enclave Projects. It provides a user-friendly interface for storing and managing passwords with strong encryption.

## Features

- User authentication and authorization
- Secure password storage
- Password generation
- Password strength checking
- Mobile-responsive design
- Search and filter passwords
- Edit and delete passwords
- View password history

## Prerequisites

- Python 3.8 or higher
- MongoDB
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/enclave-projects/mino.git
cd mino
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- On Windows:
```bash
venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Initialize the database:
```bash
python init_db.py
```

## Configuration

The application uses MongoDB for data storage. The connection string is already configured in `config/database.py`.

## Running the Application

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
mino/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── init_db.py             # Database initialization script
├── config/
│   └── database.py        # Database configuration
├── models/
│   └── user.py           # User model
├── auth/
│   └── routes.py         # Authentication routes
├── mino/
│   └── routes.py         # Password management routes
├── static/
│   └── css/
│       └── custom.css    # Custom styles
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Landing page
    └── mino/
        ├── base.html     # Mino app base template
        ├── dashboard.html # Password dashboard
        ├── add_password.html
        ├── edit_password.html
        └── auth/
            ├── login.html
            ├── register.html
            └── complete_profile.html
```

## Security Features

- Password hashing using bcrypt
- Session management with Flask-Login
- CSRF protection
- Secure password generation
- Password strength validation
- Input validation and sanitization

## Development

To run the application in development mode with debug enabled:

```bash
python app.py
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, don't hesitate to get in touch with pranjal.ai.arena@hotmail.com

## Credits

Developed by Enclave Projects
