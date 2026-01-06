# Meeting Room Booking System - Python Backend

A FastAPI-based backend for managing meeting room bookings with AWS DynamoDB integration, JWT authentication, and bcrypt password hashing.

## Features

- **JWT-based authentication** with role-based access control (admin/user)
- **AWS DynamoDB** integration using the same schema as the Go backend
- **Clean architecture** with repository, service, and controller layers
- **Password hashing** using bcrypt
- **CORS support** for frontend integration
- **RESTful API** with comprehensive endpoints

## Tech Stack

- **FastAPI** - Modern Python web framework
- **AWS DynamoDB** - NoSQL database (same table schema as Go backend)
- **boto3** - AWS SDK for Python
- **PyJWT** - JSON Web Token implementation
- **bcrypt** - Password hashing
- **Pydantic** - Data validation

## Installation (Linux OS)

1. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

## Running the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`


## API Endpoints

### Authentication

- `POST /login` - User login
- `GET /health` - Health check

### Users

- `POST /api/register` - Register user (admin)
- `GET /api/users` - Get all users (admin)
- `GET /api/users/{id}` - Get user by ID
- `DELETE /api/users/{id}` - Delete user (admin)

### Rooms

- `POST /api/rooms` - Add room (admin)
- `GET /api/rooms` - Get all rooms
- `GET /api/rooms/{id}` - Get room by ID
- `DELETE /api/rooms/{id}` - Delete room (admin)
- `GET /api/rooms/search` - Search rooms

### Bookings

- `POST /api/bookings` - Create booking
- `GET /api/bookings/{id}` - Get booking
- `DELETE /api/bookings/{id}` - Cancel booking
- `GET /api/bookings` - Get all bookings (admin)
- `GET /api/bookings/my` - Get user's bookings
- `GET /api/rooms/{id}/schedule` - Get room schedule
