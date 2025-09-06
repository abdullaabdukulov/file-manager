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