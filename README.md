# Healthcare Backend API

A RESTful backend system for managing patients and doctors, built with Django, Django REST Framework, and PostgreSQL.

## Tech Stack
- Python / Django
- Django REST Framework
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt)

## Setup Instructions

### 1. Clone the repo
git clone <your-repo-url>
cd <project-folder>

### 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure environment variables
cp .env.example .env
# Fill in your values in .env

### 5. Set up PostgreSQL
sudo service postgresql start
sudo -u postgres psql < create your DB and user as in .env >

### 6. Run migrations
python manage.py migrate

### 7. Start the server
python manage.py runserver
## Architecture

```mermaid
flowchart TD
    Client([Client / Postman])
    Client -->|HTTP + Bearer token| JWT

    JWT[JWT Middleware\nValidates every request]
    JWT --> Router

    Router[Django URL Router]
    Router --> Auth
    Router --> Patients
    Router --> Doctors
    Router --> Mappings

    Auth[accounts app\nAPIView\nregister, login]
    Patients[patients app\nModelViewSet\nowner-scoped CRUD]
    Doctors[doctors app\nModelViewSet\nshared CRUD]
    Mappings[mappings app\nModelViewSet\nassign doctors]

    Auth --> Serializers
    Patients --> Serializers
    Doctors --> Serializers
    Mappings --> Serializers

    Serializers[Serializers\nValidation + ORM bridge]
    Serializers --> DB[(PostgreSQL)]
```

## Database Schema

```mermaid
erDiagram
    USER {
        int id PK
        string name
        string email
        string password
        datetime created_at
    }

    PATIENT {
        int id PK
        int created_by FK
        string name
        int age
        char gender
        text medical_history
        datetime created_at
        datetime updated_at
    }

    DOCTOR {
        int id PK
        string name
        string specialization
        int experience_years
        string phone
        string email
        datetime created_at
        datetime updated_at
    }

    PATIENTDOCTORMAPPING {
        int id PK
        int patient_id FK
        int doctor_id FK
        datetime assigned_at
    }

    USER ||--o{ PATIENT : "creates"
    PATIENT ||--o{ PATIENTDOCTORMAPPING : "has"
    DOCTOR ||--o{ PATIENTDOCTORMAPPING : "assigned via"
```

## API Flow

```mermaid
sequenceDiagram
    actor User
    participant API
    participant JWT
    participant DB

    User->>API: POST /api/auth/register/
    API->>DB: Create user (hashed password)
    DB-->>API: User created
    API-->>User: 201 + access & refresh tokens

    User->>API: POST /api/auth/login/
    API->>DB: Authenticate email + password
    DB-->>API: User valid
    API-->>User: 200 + access & refresh tokens

    User->>API: POST /api/patients/ + Bearer token
    API->>JWT: Validate token
    JWT-->>API: Token valid, user = X
    API->>DB: Create patient (created_by = X)
    DB-->>API: Patient created
    API-->>User: 201 + patient data

    User->>API: POST /api/mappings/ + Bearer token
    API->>JWT: Validate token
    JWT-->>API: Token valid
    API->>DB: Check patient ownership + assign doctor
    DB-->>API: Mapping created
    API-->>User: 201 + mapping data
```
## API Endpoints

### Auth
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Login and get JWT | No |

### Patients
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/patients/` | Create patient | Yes |
| GET | `/api/patients/` | List own patients | Yes |
| GET | `/api/patients/<id>/` | Get patient detail | Yes |
| PUT | `/api/patients/<id>/` | Update patient | Yes |
| DELETE | `/api/patients/<id>/` | Delete patient | Yes |

### Doctors
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/doctors/` | Create doctor | Yes |
| GET | `/api/doctors/` | List all doctors | Yes |
| GET | `/api/doctors/<id>/` | Get doctor detail | Yes |
| PUT | `/api/doctors/<id>/` | Update doctor | Yes |
| DELETE | `/api/doctors/<id>/` | Delete doctor | Yes |

### Mappings
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/mappings/` | Assign doctor to patient | Yes |
| GET | `/api/mappings/` | List all mappings | Yes |
| GET | `/api/mappings/patient/<patient_id>/` | Get doctors for a patient | Yes |
| DELETE | `/api/mappings/<id>/` | Remove mapping | Yes |
## Authentication
All protected endpoints require a Bearer token in the header:
Authorization: Bearer <access_token>