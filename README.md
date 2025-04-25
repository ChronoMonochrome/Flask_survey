# Flask Survey Project

Welcome to the Flask Survey project! This project is a web application built using Flask that allows users to create and manage surveys for different roles (students, parents, teachers). It integrates a customizable form system and includes user authentication features.

## Features

- **User Authentication**: Supports login, signup, and user roles management.
- **Survey Management**: Create and manage surveys for schools, parents, and teachers.
- **File Uploads**: Users can upload files securely.
- **Data Export**: Export survey results in CSV and Excel formats.
- **Localization**: Supports multilingual content through Flask-Babel.

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- SQLAlchemy
- Flask-Login
- Flask-Mail
- Flask-Babel
- Other dependencies listed in `requirements.txt`

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Chronomonochrome/flask_survey.git
   cd flask-survey
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database and create necessary tables (using Flask-Migrate or similar).

4. Configure the application settings in `intro_to_flask/__init__.py`.

5. Run the application:

   ```bash
   python runserver.py
   ```

### Usage

- Visit `http://127.0.0.1:8001` in your web browser to access the application.
- Sign up or log in to start creating and managing surveys.

## Contribution

If you want to contribute to the project, feel free to fork the repository, make changes, and submit a pull request.
