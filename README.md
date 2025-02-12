# Blog API

## Overview
The Blog API is a web-based application that allows users to sign up, log in, create, read, update, and delete blog posts. This project leverages Flask for the web framework, SQLAlchemy for database interactions, JWT for authentication, and various other tools for caching, rate limiting, and testing.

## Features
- User signup and login with JWT authentication
- Create, read, update, and delete blog posts
- Rate limiting to prevent abuse
- Caching of frequently accessed data to improve performance
- Pagination for efficient data retrieval
- Unit tests to ensure application correctness

## Technologies Used
- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Flask-Caching
- Flask-Limiter
- Flask-Testing

## Setup Instructions

### Prerequisites
- Python 3.6+
- PostgreSQL

### Installation
1. **Clone the repository:**
    ```bash
    git clone https://github.com/shashank0008/blog_api.git
    cd blog_api
    ```

2. **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up PostgreSQL:**
    - Make sure PostgreSQL is installed and running.
    - Create a PostgreSQL database and user:
      ```sql
      CREATE DATABASE blog_db;
      CREATE USER yourusername WITH PASSWORD 'yourpassword';
      GRANT ALL PRIVILEGES ON DATABASE blog_db TO yourusername;
      ```

5. **Set up your environment variables:**
    You can create a `.env` file in the project root and add the following variables. Replace `your_secret_key`, `yourusername`, `yourpassword`, and `your_jwt_secret_key` with your actual values.
    ```bash
    SECRET_KEY=your_secret_key
    DATABASE_URL=postgresql://yourusername:yourpassword@localhost:5432/blog_db
    JWT_SECRET_KEY=your_jwt_secret_key
    ```

6. **Initialize the database:**
    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

7. **Run the application:**
    ```bash
    python3 run.py
    ```

### Running Tests
To run the unit tests, use the following command:
```bash
python3 -m unittest discover -s app
```
### Manual API Hit Samples
1. **Signup:**
curl -X POST -H "Content-Type: application/json" -d '{"email":"test@gmail.com","password":"test1234"}' http://127.0.0.1:5000/signup

2. **Login:**
curl -X POST -H "Content-Type: application/json" -d '{"email":"test@gmail.com","password":"test1234"}' http://127.0.0.1:5000/login

3. **Create a Blog Post:**
curl -X POST \
-H "Content-Type: application/json" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMTI2ODIzMCwianRpIjoiZDVhN2NiNTItYjZiNS00ZWY5LTgyYmEtZDIzMWFkM2IwYjdkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzIxMjY4MjMwLCJjc3JmIjoiZDYzMjc3ZTEtZTBiYi00OGQzLWE5YjctYjEwOTdhOGYyNDQ2IiwiZXhwIjoxNzIxMjY5MTMwfQ.U1RTgiUkPT8oFep9X6SfOiKiKh97xH2SHzZf3ceuQgU" \
-d '{"title":"My New Blog Post","body":"This is the content of my new blog post. It contains interesting information about a topic I care about."}' \
http://127.0.0.1:5000/posts

4. **Get All Blog Posts:**
curl -X GET \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyMTI2ODIzMCwianRpIjoiZDVhN2NiNTItYjZiNS00ZWY5LTgyYmEtZDIzMWFkM2IwYjdkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzIxMjY4MjMwLCJjc3JmIjoiZDYzMjc3ZTEtZTBiYi00OGQzLWE5YjctYjEwOTdhOGYyNDQ2IiwiZXhwIjoxNzIxMjY5MTMwfQ.U1RTgiUkPT8oFep9X6SfOiKiKh97xH2SHzZf3ceuQgU" \
http://127.0.0.1:5000/posts
