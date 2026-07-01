# Healthcare Backend API

A RESTful backend system for managing patients and doctors, built with Django, Django REST Framework, and PostgreSQL.

## Tech Stack
- Python / Django
- Django REST Framework
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt)

---

## Setup Instructions

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd healthcare_api
```

### 2. Create and activate virtual environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Then open `.env` and fill in your values.

### 5. Set up PostgreSQL
```bash
sudo service postgresql start
sudo -u postgres psql
```
Inside psql, run:
```sql
CREATE DATABASE healthcare_db;
CREATE USER healthcare_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO healthcare_user;

-- Required for PostgreSQL 15+
GRANT ALL ON SCHEMA public TO healthcare_user;
ALTER DATABASE healthcare_db OWNER TO healthcare_user;
\q
```
### 6. Run migrations
```bash
python manage.py migrate
```

### 7. Start the server
```bash
python manage.py runserver
```
> Visit `http://localhost:8000/api/health/` to confirm the API is running.
---

## Testing

Import the Postman collection to test all endpoints:

1. Download `healthcare_api.postman_collection.json` from the repo
2. Open Postman → `Ctrl + O` → select the file
3. In Postman, create a new environment with two variables:
   - `base_url` → `http://localhost:8000`
   - `token` → (leave blank)
4. Hit **Register** first → then **Login** — token saves automatically for all requests
---
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

> **Note:** `GET /api/mappings/patient/<patient_id>/` uses an explicit `patient/` 
> prefix to avoid URL conflicts with `DELETE /api/mappings/<id>/`.

## Authentication
All protected endpoints require a Bearer token in the header:
Authorization: Bearer <access_token>