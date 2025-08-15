# 👤 UserHub: The Identity Layer of NeuraCity

> The Central Identity, Authentication, and Authorization Service for the NeuraCity Platform.
> Co-created by Swayam and his wife.

---

## 🏛️ Architectural Purpose

`UserHub` is the **single source of truth for identity** in the NeuraCity ecosystem. It transforms the platform from a system that merely monitors spaces into one that understands and securely interacts with the *people* within them—students, staff, and administrators.

Its core responsibility is to answer three critical questions for the entire platform:
1.  **Who are you?** (Authentication)
2.  **What are you allowed to do?** (Authorization & Role-Based Access Control)
3.  **What is your status and history?** (User Profiles & Attendance)

## ✨ Core Features

*   **🔐 Enterprise-Grade Security**: Implements a robust authentication system using **JSON Web Tokens (JWT)** and secure **bcrypt** password hashing.
*   **🛂 Role-Based Access Control (RBAC)**: A sophisticated, hierarchical permission system with predefined roles (`student`, `staff`, `security`, `admin`, `superadmin`) to ensure users and system modules can only access the data and actions they are authorized for.
*   **🗄️ Production-Ready Database**: Built on a powerful **PostgreSQL** database with a clean schema managed by **SQLAlchemy ORM** and **Alembic** for safe, repeatable database migrations.
*   **👤 Centralized User Profiles**: Manages all user data, including personal details, roles, and status, providing a central point for user management.
*   **🕒 Attendance Tracking**: Includes a full-featured attendance system with API endpoints to log user `check-in` and `check-out` events, enabling powerful conversational queries like *"Who is on campus?"*
*   **🔌 Seamless Integration**: Designed as a standalone microservice that all other NeuraCity modules securely connect to for user data and authorization checks.

---

## 🛠️ Technology Stack

*   **Backend Framework**: `FastAPI`
*   **Database**: `PostgreSQL`
*   **ORM & Migrations**: `SQLAlchemy` & `Alembic`
*   **Authentication**: `python-jose` for JWT & `passlib[bcrypt]` for password hashing
*   **Data Validation**: `Pydantic`

---

## 🔗 Architectural Integration & Schema

`UserHub` is a foundational service that is queried by nearly every other module.

![System Architecture](diagram.svg)

## Database Schema (ERD)

The system uses two core tables: one for users and one for their attendance history, linked by a one-to-many relationship.

![Schema](schema.svg)

---


## ⚙️ Setup and Installation

### 1. **Prerequisites**

Docker Desktop must be installed and running.
The project's virtual environment (venv) must be active.

### 2. **Start the Database**
Run the PostgreSQL container. You only need to do this once.
```bash
docker run --name neuracity-postgres -e POSTGRES_PASSWORD=your_super_secret_password -e POSTGRES_USER=neuracity -e POSTGRES_DB=neuracity_db -p 5432:5432 -d postgres
```

### 3. **Configure Environment Variables**
   
Ensure your root .env file contains the following variables, matching your Docker command:
```bash
# in your root .env file
DATABASE_URL="postgresql://neuracity:your_super_secret_password@localhost/neuracity_db"
JWT_SECRET_KEY="a_very_long_and_random_secret_string_please_change_me"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
SYSTEM_ADMIN_EMAIL="alerts-system@neuracity.dev"
SYSTEM_ADMIN_PASSWORD="a_strong_and_secret_password"```
```

### 4. Run Database Migrations
This is a **critical one-time setup** step to create your database tables.

```bash
# In the NeuraCity project root with (venv) active

# 1. Initialize Alembic (only if the 'alembic/' folder doesn't exist)
# alembic init alembic

# 2. Configure alembic.ini and alembic/env.py as per the project guide

# 3. Generate the migration script from your models
alembic revision --autogenerate -m "Create initial user and attendance tables"

# 4. Apply the migration to the database
alembic upgrade head
```

---

## ▶️ How to Run
```bash
# In the NeuraCity project root with (venv) active
python3 -m uvicorn modules.userhub.app:app --host 0.0.0.0 --port 8005 --reload
```
The service is now live. View the interactive API documentation at http://localhost:8005/docs.

---

## 📖 API Usage Example
UserHub is a secure service. Most endpoints require a JWT Bearer Token.

Flow: Create User -> Log In to Get Token -> Use Token for Other Requests.

### 1. **Create a User (e.g., your superadmin)**

```bash
curl -X 'POST' \
  'http://localhost:8005/users/' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@neuracity.dev",
    "full_name": "username",
    "password": "a-secure-password",
    "role": "superadmin"
  }'
```

### 2. **Log In to Get a Token**

```bash
curl -X 'POST' \
  'http://localhost:8005/auth/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user%40neuracity.dev&password=a-secure-password'
```
This will return an access_token. Copy it.

### 3. **Access a Protected Endpoint**
To get a list of all security staff, you must provide the token in an Authorization header.
```bash
curl -X 'GET' \
  'http://localhost:8005/users/by-role/security' \
  -H 'Authorization: Bearer <YOUR_COPIED_TOKEN_HERE>'
```
This secure flow is the foundation for all user interactions within the NeuraCity platform.