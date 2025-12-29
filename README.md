# Translation Platform

A comprehensive translation booking and video conferencing platform connecting companies with professional translators. Built with Next.js, FastAPI, PostgreSQL, and Jitsi Meet.

## Features

- **🌍 Multi-language Support**: Spanish, French, and German translators
- **📅 Calendar-Based Booking**: Interactive calendar for scheduling translation sessions
- **👥 Role-Based Access**: Translators, Employees, Company Admins, and System Admins
- **🎥 Integrated Video Conferencing**: Self-hosted Jitsi Meet for secure video calls
- **⏱️ Flexible Durations**: 30-minute or 1-hour translation sessions
- **🔒 Secure Authentication**: JWT-based auth with role management
- **📊 Booking Management**: Create, view, update, and cancel bookings
- **🚫 Conflict Prevention**: Automatic double-booking detection

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Zustand, Tailwind CSS
- **Backend**: FastAPI, Python, SQLAlchemy
- **Database**: PostgreSQL
- **Real-time**: Jitsi Meet API, WebSockets

## Documentation

For detailed documentation, see the [/docs](/docs) directory:
- **[Local Setup Guide](/docs/LOCAL_SETUP.md)** - Complete guide for running locally (portfolio/demo)
- [Translation Platform Guide](/docs/TRANSLATION_PLATFORM.md) - Complete platform overview
- [Jitsi Setup](/docs/JITSI_SETUP.md) - Video conferencing configuration

## Getting Started

You can run this application in two ways:
1. **Using Docker (Recommended)** - Easiest way to get started
2. **Manual Setup** - For development

### Option 1: Docker Setup (Recommended)

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

#### Quick Start

```bash
# Make the stack script executable (already done)
chmod +x stack.sh

# Start the entire stack
./stack.sh start
```

That's it! The application will be available at:
- Frontend: http://localhost:3000
- Translator Registration: http://localhost:3000/register/translator
- Calendar: http://localhost:3000/calendar
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Jitsi Meet: http://localhost:8443

#### Stack Management Commands

```bash
./stack.sh start              # Start all services
./stack.sh stop               # Stop all services
./stack.sh restart            # Restart all services
./stack.sh status             # Show status of all services
./stack.sh logs               # Show logs for all services
./stack.sh logs backend       # Show logs for specific service
./stack.sh build              # Rebuild Docker images
./stack.sh clean              # Remove all containers and volumes
./stack.sh backup             # Backup database
./stack.sh restore <file>     # Restore database from backup
./stack.sh exec backend bash  # Execute command in service
```

### Option 2: Manual Setup

#### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+

#### Database Setup

Using Docker:

```bash
cd database
docker-compose up -d
```

Or install PostgreSQL manually and create the database:

```bash
createdb callcenter
psql callcenter < database/init.sql
```

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Update .env with your database credentials
# DATABASE_URL=postgresql://callcenter:callcenter123@localhost:5432/callcenter

# Run the server
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Run the development server
npm run dev
```

The frontend will be available at http://localhost:3000

## Usage

### For Translators
1. Register at http://localhost:3000/register/translator
2. Select your languages (Spanish, French, German)
3. Set your hourly rate (optional)
4. Wait for booking confirmations from companies

### For Companies & Employees
1. Contact admin to set up your company account
2. Register employees under your company
3. Book translation sessions via the calendar interface
4. Choose duration (30 minutes or 1 hour)
5. Join video meetings when the session starts

## Default Credentials

For testing, use these credentials:

- **Translator**: translator1@example.com / password123
- **Employee**: employee@example.com / password123
- **Admin**: admin@example.com / password123

Or register a new translator account at http://localhost:3000/register/translator

## Project Structure

```
interpretation_platform/
├── frontend/           # Next.js frontend application
│   ├── src/
│   │   ├── app/       # Next.js app router pages
│   │   ├── components/# React components
│   │   ├── lib/       # Utilities (API, WebSocket)
│   │   ├── store/     # Zustand state management
│   │   └── types/     # TypeScript type definitions
│   └── package.json
│
├── backend/           # FastAPI backend application
│   ├── app/
│   │   ├── api/       # API endpoints
│   │   ├── core/      # Core functionality (auth, config)
│   │   ├── db/        # Database session
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   └── services/  # Business logic
│   └── requirements.txt
│
└── database/          # Database setup
    ├── docker-compose.yml
    └── init.sql
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Translators
- `POST /translators/register` - Register new translator
- `GET /translators/` - List available translators
- `PUT /translators/{id}/availability` - Update translator availability

### Bookings
- `GET /bookings/` - Get all bookings (filtered by user role)
- `POST /bookings/` - Create new booking
- `GET /bookings/{id}` - Get booking details
- `PUT /bookings/{id}` - Update booking
- `DELETE /bookings/{id}` - Cancel booking

### Companies
- `POST /companies/` - Create new company
- `POST /companies/employees/register` - Register employee

For complete API documentation, visit http://localhost:8000/docs after starting the stack.

## Development

### Running Tests

Backend:
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm test
```

### Building for Production

Backend:
```bash
cd backend
# The FastAPI app is production-ready
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd frontend
npm run build
npm start
```

## License

Apache License 2.0

Copyright 2025 Translation Platform Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
