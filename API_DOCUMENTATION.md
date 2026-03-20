# Teach Edison API Documentation

Welcome to the Teach Edison API documentation. This API is built using Django REST Framework and provides endpoints for user authentication, AI-powered quiz generation, attempt tracking, and performance analytics.

## 🚀 Interactive Documentation (Swagger / ReDoc)

Because this project uses `drf-spectacular`, **interactive documentation is auto-generated** and available out-of-the-box when the backend server is running!

With the local server running (`python manage.py runserver`), visit:

- **Swagger UI (Interactive):** [http://localhost:8000/api/v1/docs/](http://localhost:8000/api/v1/docs/)
- **ReDoc (Static Layout):** [http://localhost:8000/api/v1/redoc/](http://localhost:8000/api/v1/redoc/)
- **Raw OpenAPI 3.0 Schema:** [http://localhost:8000/api/v1/schema/](http://localhost:8000/api/v1/schema/)

You can use the Swagger UI to authenticate, input parameters, and make live API calls directly from your browser.

---

## 🔒 Authentication

This API uses **JSON Web Tokens (JWT)** for authentication.
All endpoints (except `auth/register` and `auth/login`) require a valid Access Token in the `Authorization` header.

**Format:**
```http
Authorization: Bearer <your_access_token>
```

### Auth Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register/` | Register a new user |
| `POST` | `/api/v1/auth/login/` | Obtain JWT access/refresh token pair |
| `POST` | `/api/v1/auth/refresh/` | Get a new access token using a refresh token |
| `GET` | `/api/v1/auth/me/` | Fetch current user profile |

---

## 🧠 Quizzes

Endpoints for viewing and generating quizzes via AI.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/quizzes/` | List all available quizzes (Paginated) |
| `GET` | `/api/v1/quizzes/my/` | List quizzes created by the current user |
| `POST` | `/api/v1/quizzes/` | Trigger AI generation for a new quiz (Admin only) |
| `GET` | `/api/v1/quizzes/{id}/` | Get full quiz details (Questions & Choices) |
| `GET` | `/api/v1/quizzes/{id}/status/` | Poll for async generation status (`generating`, `ready`, `failed`) |
| `DELETE` | `/api/v1/quizzes/{id}/` | Delete a quiz and all associated data |

### Example: Generate a Quiz (POST `/quizzes/`)
*Triggers a background Celery task. Returns `status: 'generating'` immediately.*

**Request Body:**
```json
{
  "topic": "Python Generators",
  "difficulty": "medium",
  "question_count": 5
}
```

---

## ✍️ Quiz Attempts

Endpoints for starting a quiz, answering questions, and submitting the final result.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/attempts/` | Get user's personal attempt history |
| `POST` | `/api/v1/attempts/` | Start a new attempt (`quiz_id` required in body) |
| `GET` | `/api/v1/attempts/{id}/` | Get current state of an attempt |
| `POST` | `/api/v1/attempts/{id}/answer/` | Submit a single choice response |
| `POST` | `/api/v1/attempts/{id}/complete/` | Finish attempt, calculate score, and update global analytics |

### Example: Submit Answer (POST `/attempts/{id}/answer/`)
**Request Body:**
```json
{
  "question_id": "uuid-here",
  "choice_id": "uuid-here",
  "time_taken_seconds": 12
}
```

---

## 📊 Analytics

Endpoints for fetching individual and global performance metrics. Note that statistics update asynchronously when an Attempt is completed.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/analytics/me/` | Current user's stats (Total taken, Avg score, Hot streaks) |
| `GET` | `/api/v1/analytics/history/` | Time-series data of user's past quiz scores |
| `GET` | `/api/v1/analytics/topics/` | Breakdown of performance grouped by quiz topic |
| `GET` | `/api/v1/analytics/leaderboard/` | Global top performers |

---

## 🛡️ Admin Dashboard

Endpoints reserved for users with the `admin` role to monitor overall system health.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/admin/stats/` | Total platform metrics (system-wide usage, active users) |
| `GET` | `/api/v1/admin/users/` | List of all registered users (Paginated) |

---

## ⚠️ Error Handling & Rate Limiting

The API uses standard HTTP status codes:
- `200 OK` / `201 Created` - Success
- `400 Bad Request` - Validation error (check response body)
- `401 Unauthorized` - Token missing or expired
- `403 Forbidden` - You lack permission (e.g. you're a standard user trying to hit an admin route)
- `404 Not Found` - Resource does not exist
- `429 Too Many Requests` - You've hit the rate limit

### Rate Limits
- **Anonymous Users:** 10 requests / minute
- **Authenticated Users:** 60 requests / minute
