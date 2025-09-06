# File Manager

This is a FastAPI-based file management application that supports uploading, downloading, and metadata extraction for files (PDF, DOCX) stored in an S3-compatible storage (MinIO). It uses Celery for asynchronous metadata extraction, PostgreSQL for data persistence, Redis for task queuing, and includes production-ready configurations.

## Features
- **File Upload/Download**: Upload files to MinIO and download with access control.
- **Metadata Extraction**: Asynchronous extraction of PDF (page count, title, author, creator, creation date) and DOCX (paragraph count, table count, title, author, creation date) metadata using Celery.
- **Authentication**: JWT-based authentication for user access control.
- **Database**: Async SQLAlchemy with PostgreSQL for storing file metadata and user data.
- **S3 Storage**: MinIO integration for file storage.
- **Production Ready**:
  - Optimized `Dockerfile.prod` with non-root user and Poetry for dependency management.
  - Gunicorn with dynamic workers for scalability.
  - JSON logging and Sentry for error tracking.
- **Development**:
  - Easy local setup with `just` scripts.
  - Linting with `ruff` and `ruff format`.
  - Alembic migrations with custom naming (`YYYY-MM-DD_slug`).

## Local Development

### Prerequisites
- **Python**: 3.11 or 3.12
- **Docker**: For running PostgreSQL, Redis, and MinIO
- **Just**: Command runner for simplified scripts
- **Poetry**: Dependency management

### Setup Just
MacOS:
```shell
brew install just
```

Debian/Ubuntu:
```shell
apt install just
```

Others: [Just Installation](https://github.com/casey/just?tab=readme-ov-file#packages)

### Setup Poetry
```shell
pip install poetry
```

Other ways: [Poetry Installation](https://python-poetry.org/docs/#installation)

### Setup Environment
1. Copy the environment file:
   ```shell
   cp .env.example .env
   ```
2. Update `.env` with your settings:
   ```env
   DATABASE_URL=postgresql://app:app@localhost:5432/app
   DATABASE_ASYNC_URL=postgresql+asyncpg://app:app@localhost:5432/app
   ENVIRONMENT=LOCAL
   CORS_HEADERS=["*"]
   CORS_ORIGINS=["http://localhost:3000"]
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   AWS_ACCESS_KEY_ID=minioadmin
   AWS_SECRET_ACCESS_KEY=minioadmin
   AWS_S3_ENDPOINT_URL=http://localhost:9000
   AWS_S3_BUCKET_NAME=file-manager
   REDIS_URL=redis://localhost:6379/0
   ```
3. Install dependencies:
   ```shell
   poetry install
   ```

### Setup Services
Start PostgreSQL, Redis, and MinIO using Docker:
```shell
docker-compose -f docker-compose.yml up -d
```

Create the MinIO bucket:
```shell
curl -X PUT "http://localhost:9000/file-manager" -u minioadmin:minioadmin
```

### Run the Uvicorn Server
With default settings:
```shell
just run
```

With custom logging:
```shell
just run --log-config logging.ini
```

### Run Celery Worker
For asynchronous metadata extraction:
```shell
just celery
```

### Linters
Format code with `ruff --fix` and `ruff format`:
```shell
just lint
```

### Migrations
- Create a migration:
  ```shell
  just mm migration_name
  ```
- Run migrations:
  ```shell
  just migrate
  ```
- Downgrade migrations:
  ```shell
  just downgrade -1  # or -2, base, or migration hash
  ```

### Testing Locally
1. Seed the database:
   ```shell
   docker-compose -f docker-compose.yml exec app_db psql -U app -d app
   ```
   ```sql
   INSERT INTO departments (id, name) VALUES ('aee38173-1a79-4277-9f77-735a79083117', 'Test Department');
   INSERT INTO users (id, username, email, hashed_password, role, department_id, is_active)
   VALUES ('a0585613-1051-4b59-ba7e-1167d756a00f', 'testuser', 'test@example.com', '$2b$12$your_bcrypt_hash', 'USER', 'aee38173-1a79-4277-9f77-735a79083117', true);
   ```
   Generate bcrypt hash:
   ```shell
   poetry run python -c "from passlib.hash import bcrypt; print(bcrypt.hash('testpass123'))"
   ```

2. Login:
   ```shell
   curl -X POST "http://localhost:8000/api/v1/auth/login" -d "username=testuser&password=testpass123"
   ```

3. Upload a file:
   ```shell
   curl -X POST "http://localhost:8000/api/v1/files/upload?visibility=PRIVATE" -H "Authorization: Bearer <token>" -F "file=@1_Анкета_кандидата_2024.docx"
   ```

4. Download a file:
   ```shell
   curl -X GET "http://localhost:8000/api/v1/files/<file_id>/download" -H "Authorization: Bearer <token>" -o downloaded_file.docx
   ```

5. Check metadata:
   ```shell
   docker-compose -f docker-compose.yml exec app_db psql -U app -d app -c "SELECT * FROM file_metadata WHERE file_id = '<file_id>';"
   ```

## Deployment
The application is deployed using Docker and Gunicorn for production. The `Dockerfile.prod` is optimized for small size, fast builds, and runs as a non-root user (`app`). Gunicorn is configured with dynamic workers based on CPU cores.

### Steps
1. Update `.env` for production:
   ```env
   DATABASE_URL=postgresql+asyncpg://app:app@app_db:5432/app
   DATABASE_ASYNC_URL=postgresql+asyncpg://app:app@app_db:5432/app
   ENVIRONMENT=PROD
   AWS_S3_ENDPOINT_URL=http://minio:9000
   AWS_S3_BUCKET_NAME=file-manager
   REDIS_URL=redis://redis:6379/0
   ```

2. Build and run:
   ```shell
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

3. Apply migrations:
   ```shell
   docker-compose -f docker-compose.prod.yml exec app poetry run alembic upgrade head
   ```

4. Create MinIO bucket:
   ```shell
   curl -X PUT "http://localhost:9000/file-manager" -u minioadmin:minioadmin
   ```

5. Test endpoints (same as local testing, using production URL).

### Notes
- **Metadata Extraction**:
  - PDF: Extracts `page_count`, `title`, `author`, `creator`, `creation_date`.
  - DOCX: Extracts `paragraph_count`, `table_count`, `title`, `author`, `creation_date` (`page_count` and `creator` are `null`).
  - If `title` is empty, consider modifying `src/tasks.py` to extract from content:
    ```python
    title = next((p.text for p in doc.paragraphs if p.style.name.startswith("Heading")), "") or ""
    ```
- **Non-ASCII Filenames**: Handled in `src/files/router.py` using URL-encoded `Content-Disposition`.
- **Sentry**: Configured for error tracking in production.
- **Logging**: JSON logs for production, configurable via `logging.ini`.

## Troubleshooting
- **Docker Permissions**:
  ```shell
  sudo usermod -aG docker $USER
  newgrp docker
  ```
- **Metadata Issues**:
  - Check Celery logs:
    ```shell
    docker-compose -f docker-compose.prod.yml logs celery
    ```
  - Verify `src/tasks.py` uses synchronous `run_async`.
- **Download Errors**:
  - Ensure `src/files/router.py` uses `filename*=UTF-8''` for non-ASCII filenames.
- **Database**:
  - Verify connectivity:
    ```shell
    docker-compose -f docker-compose.prod.yml exec app_db psql -U app -d app -c "SELECT 1;"
    ```