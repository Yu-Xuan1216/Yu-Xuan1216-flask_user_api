# User Management API
A simple Flask API for creating, deleting, and managing users. Includes CSV upload and Swagger documentation.

## Features
- Create new user (POST /users)
- Delete user (DELETE /users/<name>)
- List all users (GET /users)
- Upload users from CSV (POST /users/upload)
- Get average age grouped by first letter of username (GET /users/average-age)
- Swagger UI documentation (GET /apidocs/)

## Code structure
```
project/
│
├─ app.py                # Main Flask application
├─ test_app.py           # Unittest for User API
├─ requirements.txt      # Python dependencies
├─ Dockerfile            # Docker image build instructions
└─ README.md             # Project documentation
```

## Environment Requirements
### Option 1: Run with Docker
This project runs inside a Docker container.  
Please make sure Docker is installed before building the image.
- Docker Desktop (Windows / macOS)
- Docker Engine 20.10+ (Linux)

### Option 2: Run locally
```bash
pip install -r requirements.txt
python app.py
```

## Build Docker image
```bash
docker build -t user-api .
```

## Run container
```bash
docker run -d -p 5000:5000 --name userapi_container user-api
```

## Test API
Swagger UI is available at: http://localhost:5000/apidocs/