# Lemmatica
### Moore's Template Statement

#### 1. FOR:
Social service employees and casual language learners
#### 2. WHO 
Need a simple way to capture and practice real-world phrases.
#### 3. LEMMATICA 
Is a minimalist application
#### 4. THAT 
Allows users to build a personalized knowledge base with built-in recall practice.
##### 5. UNLIKE 
Duolingo or Google Translate,
##### 6. LEMMATICA 
is simple, user-focused, and built to facilitate conversations. Language learners can
log and review words from their daily encounters, while also having access to essential vocabulary terms
in areas like social services and emergency assistance. Inputted words and phrases become a card with
the equivalent translation pulled via API. Users can then study using a recall flashcard technique, and
optionally study with curated “essential vocab” packs designed for immigrant and refugee support.


## Project Structure

```text
cen-project/
├── app.py                 # Flask entry point (debug runner)
├── config.py              # App configuration (secret key, DB URI)
├── requirements.txt       # Python dependencies
├── wsgi.py                # Gunicorn entry point for production
├── docker/
│   └── nginx/default.conf # Reverse proxy configuration
└── app/
    ├── __init__.py        # Application factory & blueprint registration
    ├── extensions.py      # SQLAlchemy setup
    ├── models/orm_objects.py
    ├── scripts/setup_db.py
    ├── main/, auth/, cards/, sets/, practice/  # Feature blueprints
    └── templates/         # Jinja templates

docker-compose.yml         # Container stack (root directory)
.env                       # Environment variables (root directory)
```
Important: "docker-compose.yml" and ".env" go in an outer directory. So create a folder called something like "cen" and then move the "cen-project" github repository inside of it. Then add your docker-compose.yml and .env files. Will be attached in Slack.

## Docker Deployment

### Prerequisites

- Install **Docker Desktop** (includes Docker Engine & Docker Compose) from https://www.docker.com/products/docker-desktop/
- Docker desktop must be installed and the application must be open on your computer in order to run the flask app

### Environment Configuration

1. Copy `.env` in the repository root (or create it) and adjust values:
   - `SECRET_KEY`: Flask secret for session signing.
   - `APP_PORT`: External port for nginx (default `8025`).
   - `DB_PORT`: Internal MariaDB port (default `3306`).
   - `DB_NAME`: Database schema name.
   - `DB_USER` / `DB_PASSWORD`: Application DB credentials.
   - `MARIADB_ROOT_PASSWORD`: MariaDB root password.
   - `RAPIDAPI_KEY`: Rapid API key.

### Commands

Run these from the root directory (where `docker-compose.yml` resides):

```bash
# Build or rebuild images
docker-compose build

# Start the stack in detached mode
docker-compose up -d

# Follow logs (cen-app | cen-nginx | cen-db)
docker-compose logs -f --tail 200 <container_name>

# Stop and remove the stack
docker-compose down
```

Once running, access the app at `http://localhost:${APP_PORT}` (default `http://localhost:8025`).

> **Note:** If you change environment variables or dependencies, rebuild with `docker-compose build` to capture the updates.

## Additional Notes

- Blueprint modules (`app/auth`, `app/cards`, etc.) keep routes organized by feature.
- Database models live in `app/models/orm_objects.py` and use SQLAlchemy.
- Static and template assets reside under `app/templates` and blueprint-specific template directories.
- For production deployments, the Docker stack uses Gunicorn (`cen-project/wsgi.py`) behind nginx with MariaDB for persistence.

## Current docker-compose.yml
```docker-compose
services:
  db:
    image: mariadb:11.4
    container_name: cen-db
    restart: unless-stopped
    environment:
      MARIADB_ROOT_PASSWORD: ${MARIADB_ROOT_PASSWORD}
      MARIADB_DATABASE: ${DB_NAME}
      MARIADB_USER: ${DB_USER}
      MARIADB_PASSWORD: ${DB_PASSWORD}
      RAPIDAPI_KEY: ${RAPIDAPI_KEY}
    volumes:
      - db_data:/var/lib/mysql
    ports:
      - "${DB_PORT}:3306"
    healthcheck:
      test: ["CMD-SHELL", "mariadb-admin ping -h localhost -P 3306 -u $$MARIADB_USER --password=$$MARIADB_PASSWORD --silent"]
      interval: 10s
      timeout: 5s
      retries: 5

  web:
    build:
      context: ./cen-project
      dockerfile: Dockerfile
    container_name: cen-app
    depends_on:
      db:
        condition: service_healthy
    environment:
      SECRET_KEY: ${SECRET_KEY}
      SQLALCHEMY_DATABASE_URI: mysql+pymysql://${DB_USER}:${DB_PASSWORD}@db:3306/${DB_NAME}
      RAPIDAPI_KEY: ${RAPIDAPI_KEY}
    expose:
      - "8000"
    restart: unless-stopped

  nginx:
    image: nginx:1.27-alpine
    container_name: cen-nginx
    depends_on:
      - web
    ports:
      - "${APP_PORT}:80"
    volumes:
      - ./cen-project/docker/nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    restart: unless-stopped

volumes:
  db_data:

```
