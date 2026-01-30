# Docs Automation API

A FastAPI-based service designed to automate content management on GitHub repositories. It acts as a bridge for external systems (like a Headless CMS) to create branches, write files, and open Pull Requests programmatically without direct Git access.

## Features

- **GitHub App Authentication**: Securely interacts with GitHub using App ID and Private Key (JWT).
- **Automatic Branch Management**: Automatically checks out existing branches or creates new ones from `main`.
- **File Upsert**: Create or update files with automatic commit generation.
- **Pull Request Automation**: Open Pull Requests programmatically via API.

## API Endpoints

The API exposes endpoints under the `/docs` prefix.

### 1. Write File
`POST /docs/files`

Writes content to a specific path in the repository. If the branch doesn't exist, it is created automatically.

**Request Body:**
```json
{
  "branch": "update-post-123",
  "path": "docs/intro.md",
  "content": "# Hello World",
  "overwrite": true
}
```

**Response:**
```json
{
  "status": "written",
  "commit": "sha_of_the_commit"
}
```

### 2. Create Pull Request
`POST /docs/pull-requests`

Opens a Pull Request from the specified branch to `main`.

**Request Body:**
```json
{
  "branch": "update-post-123",
  "title": "Docs Update",
  "description": "Automated update from CMS",
  "base": "main"
}
```

**Response:**
```json
{
  "status": "created",
  "pull_request": "https://github.com/owner/repo/pull/1"
}
```

## Setup & Configuration

### Prerequisites
- Python 3.10+
- A GitHub App installed on the target repository.

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file in the root directory (based on `.env.example`):
   ```env
   GITHUB_APP_ID=your_app_id
   GITHUB_INSTALLATION_ID=your_installation_id
   GITHUB_PRIVATE_KEY=your_private_key_content
   GITHUB_REPO=owner/repo_name
   ```

### Quick Start (Recommended)

For convenience, you can use the `run.sh` script. It automatically handles environment setup (copying `.env`), dependency installation (using `uv` or `pip`), and starting the server.

```bash
chmod +x run.sh
./run.sh
```

### Manual Setup


Run the server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

### Running with Docker

You can also run the application using Docker. This ensures a consistent environment and easy deployment.

**Using Docker Compose (Recommended):**

```bash
docker compose up -d --build
```

**Using Docker manually:**

1. Build the image:
   ```bash
   docker build -t dosaurus-hoster-bot .
   ```

2. Run the container:
   ```bash
   # Make sure your .env file is present
   docker run -d -p 8000:8000 --env-file .env dosaurus-hoster-bot
   ```
