# FastAPI Authentication Service

A backend authentication service built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, and **JWT**. The application provides user registration, login, logout, token refresh, and protected profile endpoints.

The application is containerized using **Docker** and can be deployed as a **Docker Swarm stack**.

## Features

* User registration
* User login
* Password hashing using Argon2
* JWT access tokens
* JWT refresh tokens
* Refresh token revocation
* Protected API endpoints
* User profile endpoint
* PostgreSQL database
* SQLAlchemy database integration
* Alembic database migrations
* Dockerized application
* Docker Swarm deployment
* Persistent PostgreSQL storage using Docker volumes
* Swagger/OpenAPI API documentation

## Tech Stack

* **Python 3.12**
* **FastAPI**
* **Uvicorn**
* **PostgreSQL**
* **SQLAlchemy**
* **Alembic**
* **Pydantic**
* **JWT**
* **Argon2**
* **Docker**
* **Docker Swarm**

## Project Structure

```text
FastAPI/
│
├── alembic/
│   ├── versions/
│   │   └── <migration_files>.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── db/
│   └── database.py
│
├── models/
│   └── ...
│
├── router/
│   ├── auth.py
│   └── sample.py
│
├── services/
│   └── auth.py
│
├── utils/
│   └── auth.py
│
├── main.py
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

## API Endpoints

### Authentication

| Method | Endpoint         | Description                    | Authentication |
| ------ | ---------------- | ------------------------------ | -------------- |
| POST   | `/auth/register` | Register a new user            | No             |
| POST   | `/auth/login`    | Login and generate tokens      | No             |
| POST   | `/auth/logout`   | Revoke refresh token           | No             |
| POST   | `/auth/refresh`  | Generate a new access token    | No             |
| GET    | `/auth/profile`  | Get authenticated user profile | Bearer Token   |

### Sample

| Method | Endpoint         | Description               | Authentication |
| ------ | ---------------- | ------------------------- | -------------- |
| GET    | `/sample/sample` | Protected sample endpoint | Bearer Token   |

## API Documentation

FastAPI automatically provides Swagger UI.

After starting the application, open:

```text
http://localhost:8000/docs
```

OpenAPI specification:

```text
http://localhost:8000/openapi.json
```

## Environment Variables

The application requires PostgreSQL and authentication configuration.

Example:

```env
POSTGRES_DB=authDB
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=Selva
POSTGRES_PASSWORD=your_password

SECRET_KEY=your_secret_key
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=3
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> Do not commit real passwords, secret keys, or other sensitive credentials to GitHub.

For production deployments, use environment variables or Docker Secrets.

## Running Locally

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd FastAPI
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the database

Make sure PostgreSQL is running and update your database configuration.

For example:

```text
postgresql://Selva:your_password@localhost:5432/authDB
```

### 5. Run Alembic migrations

Apply existing migrations:

```bash
alembic upgrade head
```

To create a new migration after changing your SQLAlchemy models:

```bash
alembic revision --autogenerate -m "your migration message"
```

Then apply it:

```bash
alembic upgrade head
```

### 6. Start FastAPI

```bash
uvicorn main:app --reload
```

The application will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

## Running with Docker

Build the application image:

```bash
docker build -t auth-service:latest .
```

Run the application using Docker Compose:

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

View application logs:

```bash
docker logs <container_name>
```

## Docker Swarm Deployment

This project can also be deployed as a Docker Swarm stack.

### 1. Initialize Docker Swarm

If Swarm is not already initialized:

```bash
docker swarm init
```

Check the Swarm node:

```bash
docker node ls
```

### 2. Build the application image

```bash
docker build -t auth-service:latest .
```

The Dockerfile runs the Alembic migrations before starting Uvicorn:

```dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

### 3. Deploy the stack

```bash
docker stack deploy -c docker-compose.yml auth_service
```

Check the stack:

```bash
docker stack ls
```

Check services:

```bash
docker service ls
```

Expected services:

```text
auth_service_auth-service
auth_service_postgres
```

### 4. Check application logs

```bash
docker service logs -f auth_service_auth-service
```

PostgreSQL logs:

```bash
docker service logs -f auth_service_postgres
```

### 5. Access the API

The API is exposed on port `8000`.

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

If running Docker Swarm inside WSL or another virtualized environment, you may need to access the service using the host IP address:

```text
http://<host-ip>:8000
```

For example:

```text
http://172.22.229.227:8000
```

## Database Persistence

PostgreSQL uses a named Docker volume to persist database data.

```yaml
volumes:
  - postgres_data:/var/lib/postgresql
```

The named volume is declared as:

```yaml
volumes:
  postgres_data:
```

This allows PostgreSQL data to survive when the Docker Swarm stack is removed and redeployed.

To check Docker volumes:

```bash
docker volume ls
```

To inspect the PostgreSQL volume:

```bash
docker volume inspect auth_service_postgres_data
```

> Avoid deleting the PostgreSQL volume unless you intentionally want to remove the database data.

## Database Migrations

Alembic is used to manage database schema changes.

Create a migration:

```bash
alembic revision --autogenerate -m "create users and refresh tokens"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback the latest migration:

```bash
alembic downgrade -1
```

When the Docker container starts, migrations are automatically applied before the FastAPI server starts:

```text
alembic upgrade head
        ↓
Database schema updated
        ↓
Uvicorn starts
        ↓
FastAPI application starts
```

## Authentication Flow

### Registration

```text
Client
  │
  │ POST /auth/register
  ▼
FastAPI
  │
  ├── Validate request
  ├── Check existing user
  ├── Hash password
  └── Save user
       │
       ▼
   PostgreSQL
```

### Login

```text
Client
  │
  │ POST /auth/login
  ▼
FastAPI
  │
  ├── Find user
  ├── Verify password
  ├── Generate access token
  └── Generate refresh token
       │
       ▼
   PostgreSQL
```

### Protected Endpoint

```text
Client
  │
  │ Authorization: Bearer <access_token>
  ▼
FastAPI
  │
  ├── Validate JWT
  ├── Extract user information
  └── Process request
       │
       ▼
 Protected Resource
```

## Docker Architecture

```text
                    Docker Swarm
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
      Auth Service              PostgreSQL
      Port: 8000                Port: 5432
             │                       │
             │                       │
             └───────────┬───────────┘
                         │
                    Docker Network
                         │
                         ▼
                  Persistent Volume
                   postgres_data
```

## Useful Docker Commands

List stacks:

```bash
docker stack ls
```

List services:

```bash
docker service ls
```

List containers:

```bash
docker ps
```

Inspect a service:

```bash
docker service inspect auth_service_auth-service
```

View service logs:

```bash
docker service logs -f auth_service_auth-service
```

Scale the authentication service:

```bash
docker service scale auth_service_auth-service=3
```

Remove the stack:

```bash
docker stack rm auth_service
```

Redeploy the stack:

```bash
docker stack deploy -c docker-compose.yml auth_service
```

## Important Notes

* The PostgreSQL database uses a persistent Docker volume.
* Alembic migrations are applied when the authentication service starts.
* `depends_on` controls service startup ordering but does not guarantee that PostgreSQL is fully ready to accept connections.
* For production, a database health-check or retry mechanism should be implemented before running migrations.
* Secrets should not be hardcoded in `docker-compose.yml`.
* Docker Secrets or a dedicated secret manager should be used for production deployments.
* The default PostgreSQL password in the example should be replaced with a secure password.

## Future Improvements

* Add PostgreSQL health checks
* Add database connection retry logic
* Use Docker Secrets for sensitive credentials
* Add Redis for token/session management
* Add rate limiting for authentication endpoints
* Add email verification
* Add password reset functionality
* Add role-based access control
* Add automated tests with Pytest
* Add CI/CD using GitHub Actions
* Add production logging and monitoring
* Deploy to AWS ECS or Kubernetes

## License

This project is for learning and demonstration purposes.
