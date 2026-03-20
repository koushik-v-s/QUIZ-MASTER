<div align="center">
  <img src="https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/cpu.svg" width="100" alt="Teach Edison Logo"/>
  <h1 align="center">Teach Edison: AI-Powered Quiz Platform</h1>
  <p align="center">
    <strong>A production-grade, full-stack application that leverages Grok AI (via Groq) to dynamically generate complex multiple-choice quizzes, evaluate performance, and track analytics over time.</strong>
  </p>
  
  <p align="center">
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
    <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
    <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
    <img src="https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white" alt="Celery" />
  </p>
</div>

<hr />

## 🚀 Key Features

<table>
  <tr>
    <td>🧠 <b>Intelligent Generation</b></td>
    <td>Input a topic and difficulty, and <b>Grok AI</b> generates 5-20 specific, high-quality questions with incorrect distractors and detailed explanations.</td>
  </tr>
  <tr>
    <td>⚡ <b>Asynchronous Processing</b></td>
    <td>Long-running AI generation is handled safely via <b>Celery</b> and <b>Redis</b> to prevent timeouts and ensure reliability.</td>
  </tr>
  <tr>
    <td>🔄 <b>Real-time Polling</b></td>
    <td>The React frontend polls the backend for quiz generation status, transitioning smoothly using Framer Motion animations.</td>
  </tr>
  <tr>
    <td>📊 <b>Advanced Analytics</b></td>
    <td>Tracks total quizzes, average score, daily streaks, global leaderboards, and topic-specific mastery over time.</td>
  </tr>
  <tr>
    <td>🔒 <b>Role-Based Access</b></td>
    <td>Secure JWT authentication with <code>admin</code> and <code>user</code> roles to restrict access to the Admin Panel.</td>
  </tr>
  <tr>
    <td>✨ <b>Premium UI/UX</b></td>
    <td>Built with React, Tailwind CSS v4, Framer Motion, and Recharts, offering a seamless, dark-mode native experience.</td>
  </tr>
</table>

## 🛠 Tech Stack

| Domain | Technologies |
|---|---|
| **Backend Framework** | Django 4.2.9, Django REST Framework |
| **Database** | PostgreSQL (via `psycopg2-binary`) |
| **AI Integration** | Grok AI (`groq` SDK, `llama-3.3-70b-versatile` model) |
| **Task Queue & Cache** | Celery, Redis |
| **Authentication** | JWT (SimpleJWT) |
| **Frontend Framework**| React 19, Vite |
| **Styling & Animation** | Tailwind CSS v4, Framer Motion |
| **State & Charts** | Zustand, Recharts |

## 📦 Local Development Setup

### 1. Backend Setup
```bash
# Navigate to the backend directory
cd backend

# Create & activate a virtual environment
python -m venv venv
# Windows: venv\Scripts\activate.bat
# Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and seed database
python manage.py migrate
python manage.py seed_data

# Start Django
python manage.py runserver
```

> **Note:** Make sure to create a `.env` file in `backend/` using the format in `.env.example` and add your `GROQ_API_KEY`.

### 2. Async Workers
In separate terminals, start your Redis server and Celery worker:
```bash
# Windows
celery -A config worker -l info --pool=solo
```

### 3. Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies & start Vite
npm install
npm run dev
```

> **Note:** Create a `.env` file in `frontend/` with: `VITE_API_URL=http://localhost:8000/api`

## 👨‍💻 Default Authentication
The system comes pre-configured with default accounts via `seed_data`. Test the platform using:

<div align="center">
  
| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@quiz.com` | `admin123` |
| **Student** | `user@quiz.com` | `User@123` |

</div>

<br/>

*To create your own quizzes, you must log in using the Admin account.*

## 🗄️ Database Architecture

The database is built on PostgreSQL and structured logically for analytics:
- **Core Entities:** `User`, `Quiz`, `Question`, `Choice`
- **Attempt Tracking:** `Attempt` and `UserResponse` capture start/end times, selections, and correctness.
- **Analytics Denormalization:** `UserStat`, `TopicPerformance`, and `QuizStat` update synchronously at the end of every attempt via signals/method calls for blazing-fast dashboard loads.

## 🧠 System Design & Trade-offs

*   **Asynchronous AI Generation:** 
    Instead of blocking the HTTP request while Grok generates questions (which can easily timeout after 30+ seconds), Celery + Redis queues the task and immediately returns `status: 'generating'`. The frontend then polls a lightweight `/status/` endpoint.
*   **Pydantic-like Structured Validation:**
    The Grok API can sometimes return malformed JSON. A custom `GroqQuizGenerator` intercepts responses, validates structure (exactly 4 choices, 1 correct answer), and triggers automatic retries with prompt corrections if validation fails.
*   **Zustand State Locks:**
    Managing the timer, selected answers, and submission states simultaneously led to edge-case bugs. Transitioning to Zustand with explicit action locks guarantees single-submissions during quiz-taking.

<div align="center">
  <p>Crafted with ❤️ by KOUSHIK V S.</p>
</div>
