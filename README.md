# GitHub Code Analyzer API

## 1. Project Overview

GitHub Code Analyzer is a backend application developed using Python and FastAPI. It connects with GitHub accounts, fetches repositories and branches, analyzes source code using Groq AI, and generates detailed code analysis reports.

The application identifies:

- Bugs and potential errors
- Code quality issues
- Security vulnerabilities
- Performance issues
- Code improvement recommendations

Analysis reports are stored in PostgreSQL and can be accessed later through the API.

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| PostgreSQL | Database |
| SQLAlchemy | Database ORM |
| Alembic | Database migrations |
| Pydantic | Data validation and settings |
| JWT | User authentication |
| GitHub OAuth | GitHub account connection |
| GitHub REST API | Repository and branch fetching |
| Groq AI | AI-based code analysis |
| Fernet | GitHub token encryption |
| pwdlib | Password hashing |
| HTTPX | External HTTP requests |
| Postman | API testing |
| Swagger UI | API documentation |

## 3. Main Features

1. User registration and login.
2. JWT-based authentication.
3. Get logged-in user information.
4. GitHub account integration using OAuth.
5. Secure GitHub access token encryption.
6. Fetch GitHub repositories.
7. Repository pagination.
8. Fetch repository branches.
9. Analyze repository source code using Groq AI.
10. Generate detailed code analysis reports.
11. Store analysis reports in PostgreSQL.
12. View analysis history.
13. Retrieve individual analysis reports.

## 4. Project Environment Configuration

Create a `.env` file in the project root directory.

Example configuration:

```env
APP_NAME=GitHub Code Analyzer API
DEBUG=false

DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/github_analyzer

JWT_SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Generate using Fernet
FERNET_KEY=REPLACE_WITH_FERNET_KEY

GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
GITHUB_REDIRECT_URI=http://127.0.0.1:8000/api/v1/github/callback
GITHUB_OAUTH_STATE_SECRET=REPLACE_WITH_ANOTHER_LONG_RANDOM_SECRET

GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b

MAX_REPOSITORY_FILES=40
MAX_FILE_BYTES=40000
MAX_TOTAL_CODE_BYTES=250000
MAX_ANALYSIS_CHARS_PER_CHUNK=12000
```

### Environment Variable Explanation

| Variable | Description |
|---|---|
| APP_NAME | Application name |
| DEBUG | Debug mode |
| DATABASE_URL | PostgreSQL connection URL |
| JWT_SECRET_KEY | Secret used to sign JWT tokens |
| JWT_ALGORITHM | JWT signing algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT expiration time |
| FERNET_KEY | Encryption key for GitHub access tokens |
| GITHUB_CLIENT_ID | GitHub OAuth application ID |
| GITHUB_CLIENT_SECRET | GitHub OAuth application secret |
| GITHUB_REDIRECT_URI | GitHub OAuth callback URL |
| GITHUB_OAUTH_STATE_SECRET | Secret used to sign OAuth state |
| GROQ_API_KEY | Groq API key |
| GROQ_MODEL | Groq model name |
| MAX_REPOSITORY_FILES | Maximum source files to analyze |
| MAX_FILE_BYTES | Maximum size of an individual file |
| MAX_TOTAL_CODE_BYTES | Maximum total source code size |
| MAX_ANALYSIS_CHARS_PER_CHUNK | Maximum characters per AI analysis chunk |

**Generate Fernet key:**

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Use a strong, randomly generated JWT secret and OAuth state secret. Never commit your real `.env` file to GitHub.

## 5. Installation and Setup

### Step 1: Clone the Project

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd github-code-analyzer
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create and configure the `.env` file.

### Step 5: Run Database Migrations

```bash
alembic upgrade head
```

### Step 6: Start FastAPI Server

```bash
uvicorn app.main:app --reload
```

### Step 7: Open API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# 6. API Documentation

**Base URL**

```text
http://127.0.0.1:8000/api/v1
```

## 6.1 Authentication APIs

### 1. User Registration

**Method:** POST

**Endpoint:**

```http
/api/v1/auth/register
```

**Full URL:**

```text
http://127.0.0.1:8000/api/v1/auth/register
```

**Request Body — JSON:**

```json
{
  "username": "divya123",
  "email": "divya@example.com",
  "password": "YOUR_PASSWORD"
}
```

**Description:**

- Registers a new user.
- Validates user information.
- Hashes the password before storing it.
- Saves user details in PostgreSQL.

### 2. User Login

**Method:** POST

**Endpoint:**

```http
/api/v1/auth/login
```

**Full URL:**

```text
http://127.0.0.1:8000/api/v1/auth/login
```

**Postman Configuration:**

1. Select Body.
2. Select `x-www-form-urlencoded`.
3. Enter the following values.

| Key | Value |
|---|---|
| username | Your registered username |
| password | Your registered password |

**Description:**

- Validates user credentials.
- Verifies the password hash.
- Generates a JWT access token.
- Returns the access token to the user.

Use the returned `access_token` for protected APIs.

### 3. Get Current User

**Method:** GET

**Endpoint:**

```http
/api/v1/auth/me
```

**Full URL:**

```text
http://127.0.0.1:8000/api/v1/auth/me
```

**Postman Authorization:**

- Select Authorization.
- Select Bearer Token.
- Paste your JWT access token.

**Description:**

Returns the currently authenticated user's information.

---

## 6.2 GitHub Integration APIs

### 4. Connect GitHub Account

**Method:** GET

**Endpoint:**

```http
/api/v1/github/connect
```

**Full URL:**

```text
http://127.0.0.1:8000/api/v1/github/connect
```

**Authorization:**

Bearer Token — JWT access token.

**Description:**

- Verifies the logged-in user.
- Generates a secure OAuth state.
- Creates the GitHub authorization URL.
- Returns the URL to authorize the application.

**Example Response:**

```json
{
  "authorization_url": "https://github.com/login/oauth/authorize?...",
  "message": "Open authorization_url in a browser"
}
```

Open the returned `authorization_url` in your browser and authorize the GitHub application.

### 5. GitHub OAuth Callback

**Method:** GET

**Endpoint:**

```http
/api/v1/github/callback
```

**Callback URL:**

```text
http://127.0.0.1:8000/api/v1/github/callback
```

**Query Parameters:**

| Parameter | Description |
|---|---|
| code | Authorization code returned by GitHub |
| state | OAuth state generated by the application |

**Description:**

- Receives the authorization code and state from GitHub.
- Validates the OAuth state.
- Exchanges the authorization code for a GitHub access token.
- Fetches the GitHub user profile.
- Encrypts the GitHub access token using Fernet.
- Stores GitHub account information in PostgreSQL.

**Example Response:**

```json
{
  "message": "GitHub account connected",
  "github_username": "your-github-username",
  "next": "Return to Postman and call GET /api/v1/github/repositories"
}
```

The callback is called by GitHub after the user approves authorization. Normally, you do not need to call it manually in Postman.

### 6. Get GitHub Repositories

**Method:** GET

**Endpoint:**

```http
/api/v1/github/repositories
```

**Full URL:**

```text
http://127.0.0.1:8000/api/v1/github/repositories
```

**Pagination Example:**

```http
http://127.0.0.1:8000/api/v1/github/repositories?page=1
```

```http
http://127.0.0.1:8000/api/v1/github/repositories?page=2
```

**Authorization:**

Bearer Token — JWT access token.

**Description:**

- Gets the logged-in user's GitHub account from PostgreSQL.
- Decrypts the stored GitHub access token.
- Calls the GitHub REST API.
- Fetches repositories belonging to the user or accessible to them.
- Returns repository details.

**Example Response:**

```json
[
  {
    "id": 123456,
    "name": "repo-intel",
    "full_name": "divya/repo-intel",
    "private": false,
    "default_branch": "main"
  }
]
```

**Pagination Parameters:**

| Parameter | Description |
|---|---|
| page | Page number |
| per_page | Number of repositories fetched per page |

Note: In the currently shared endpoint code, `per_page` is fixed at 100. Only `page` is accepted as a query parameter. To make `per_page=30` configurable through the URL, add a FastAPI `Query` parameter for it.

### 7. Get Repository Branches

**Method:** GET

**Endpoint:**

```http
/api/v1/github/repositories/{repo_id}/branches
```

**Example Full URL:**

```text
http://127.0.0.1:8000/api/v1/github/repositories/1169139992/branches
```

**Authorization:**

Bearer Token — JWT access token.

**Path Parameter:**

| Parameter | Description |
|---|---|
| repo_id | GitHub repository ID |

**Description:**

- Validates the repository ID.
- Retrieves the connected GitHub account.
- Decrypts the GitHub access token.
- Finds the selected repository.
- Fetches available branches from GitHub.

**Example Response:**

```json
[
  {
    "name": "main",
    "commit": {
      "sha": "example-commit-sha",
      "url": "https://api.github.com/repos/owner/repo/commits/example"
    },
    "protected": false
  }
]
```

The exact response depends on the branches returned by GitHub.

---

## 6.3 Repository Analysis APIs

### 8. Start Repository Analysis

**Method:** POST

**Endpoint:**

```http
/api/v1/analysis/start
```

**Full URL:**

```text
http://127.0.0.1:8000/api/v1/analysis/start
```

**Authorization:**

Bearer Token — JWT access token.

**Request Body — JSON:**

```json
{
  "github_repo_id": 1169139992,
  "branch": "main"
}
```

**Description:**

1. Validates the authenticated user.
2. Retrieves the connected GitHub account.
3. Decrypts the GitHub access token.
4. Finds the selected repository.
5. Validates the selected branch.
6. Fetches repository source files.
7. Prepares and divides source code into chunks.
8. Sends source code to Groq AI for analysis.
9. Processes AI-generated findings.
10. Generates the final analysis report.
11. Saves the report in PostgreSQL.
12. Returns the report ID and analysis status.

**Analysis Categories:**

- Bugs
- Code Quality
- Security
- Performance
- Recommendations

**Example Request:**

```json
{
  "github_repo_id": 1169139992,
  "branch": "main"
}
```

### 9. Get Analysis Report

**Method:** GET

**Endpoint:**

```http
/api/v1/analysis/{report_id}
```

**Example Full URL:**

```text
http://127.0.0.1:8000/api/v1/analysis/1
```

**Authorization:**

Bearer Token — JWT access token.

**Path Parameter:**

| Parameter | Description |
|---|---|
| report_id | Analysis report ID |

**Description:**

- Retrieves the requested report from PostgreSQL.
- Checks that the report belongs to the authenticated user.
- Returns the saved analysis report.
- Does not run Groq analysis again.

### 10. Get Analysis History

**Method:** GET

**Endpoint:**

```http
/api/v1/analysis/history/list
```

**Full URL:**

```text
http://127.0.0.1:8000/api/v1/analysis/history/list
```

**Authorization:**

Bearer Token — JWT access token.

**Description:**

- Retrieves previous analysis reports.
- Filters reports by the logged-in user's ID.
- Returns reports in newest-first order.
- Supports pagination using limit and offset.

**Pagination Example:**

```http
http://127.0.0.1:8000/api/v1/analysis/history/list?limit=10&offset=0
```

| Parameter | Description |
|---|---|
| limit | Maximum number of reports to return |
| offset | Number of reports to skip |

---

# 7. Complete API Endpoint Summary

| No. | Method | Endpoint | Purpose |
|---:|---|---|---|
| 1 | POST | `/auth/register` | Register user |
| 2 | POST | `/auth/login` | User login and JWT generation |
| 3 | GET | `/auth/me` | Get current user |
| 4 | GET | `/github/connect` | Start GitHub OAuth |
| 5 | GET | `/github/callback` | GitHub OAuth callback |
| 6 | GET | `/github/repositories` | Fetch repositories |
| 7 | GET | `/github/repositories/{repo_id}/branches` | Fetch branches |
| 8 | POST | `/analysis/start` | Start repository analysis |
| 9 | GET | `/analysis/{report_id}` | Get specific report |
| 10 | GET | `/analysis/history/list` | Get analysis history |

---

# 8. Complete Application Workflow

```text
                 USER
                   |
                   v
             User Registration
                   |
                   v
                User Login
                   |
                   v
             Generate JWT Token
                   |
                   v
             Connect GitHub
                   |
                   v
              GitHub OAuth
                   |
                   v
           Receive Authorization Code
                   |
                   v
           Exchange Code for Token
                   |
                   v
          Encrypt GitHub Access Token
                   |
                   v
             PostgreSQL Database
                   |
                   v
            Fetch Repositories
                   |
                   v
             Select Repository
                   |
                   v
              Select Branch
                   |
                   v
           Fetch Repository Files
                   |
                   v
          Prepare and Chunk Code
                   |
                   v
                Groq AI
                   |
                   v
             Analyze Source Code
                   |
                   v
           Generate Analysis Report
                   |
                   v
             Save Report in DB
                   |
                   v
          View Report / History
```

## 9. Security Implementation

| Security Feature | Implementation |
|---|---|
| Password Security | pwdlib password hashing |
| Authentication | JWT access token |
| Token Validation | JWT signature and expiration verification |
| GitHub Authorization | GitHub OAuth |
| OAuth Protection | Signed and time-limited OAuth state |
| Token Encryption | Fernet encryption |
| Database Access | SQLAlchemy ORM |
| Request Validation | FastAPI and Pydantic |

## 10. Database

PostgreSQL is used to store application data.

Main data includes:

- User accounts
- GitHub account details
- Encrypted GitHub access tokens
- Repository analysis reports

SQLAlchemy handles database operations, while Alembic manages database schema migrations.

## 11. Testing

The APIs can be tested using:

**Postman**

- Register and login.
- Copy the JWT access token.
- Connect the GitHub account.
- Fetch repositories and branches.
- Start repository analysis.
- Retrieve analysis reports and history.

**Swagger UI**

```text
http://127.0.0.1:8000/docs
```

## 12. Future Improvements

- React frontend dashboard.
- Redis caching.
- Celery background task processing.
- Automated retry handling for AI rate limits.
- Scheduled repository analysis.
- Export reports as PDF.
- Improved support for large repositories.

## 13. Author

Developed using Python, FastAPI, PostgreSQL, GitHub OAuth, and Groq AI.