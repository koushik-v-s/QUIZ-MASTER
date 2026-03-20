# Teach Edison: AI-Powered Quiz Platform

A production-grade, full-stack application that leverages Google's Gemini AI to dynamically generate complex multiple-choice quizzes, evaluate performance, and track analytics over time.

## 🚀 Key Features

*   **Intelligent Quiz Generation:** Input a topic and difficulty, and Gemini AI generates 5-20 specific, high-quality questions with incorrect distractors and detailed explanations.
*   **Asynchronous Processing:** Long-running AI generation is handled safely via Celery and Redis to prevent timeouts and ensure reliability.
*   **Real-time Polling:** The React frontend polls the backend for quiz generation status, transitioning smoothly using Framer Motion animations.
*   **Advanced Analytics:** Tracks total quizzes, average score, daily streaks, global leaderboards, and topic-specific mastery over time.
*   **Role-Based Access Control:** Secure JWT authentication with `admin` and `user` roles to restrict access to the Admin Panel.
*   **Premium UI/UX:** Built with React, Tailwind CSS v4, Framer Motion, and Recharts, offering a seamless, dark-mode native experience.

## 🛠 Tech Stack

**Backend:**
*   **Framework:** Django 4.2.9, Django REST Framework
*   **Database:** PostgreSQL (via `psycopg2-binary`)
*   **AI Integration:** Google Gemini API (`google-generativeai`)
*   **Task Queue & Caching:** Celery, Redis
*   **Authentication:** JWT (SimpleJWT)

**Frontend:**
*   **Framework:** React 19, Vite
*   **Styling:** Tailwind CSS v4
*   **State Management:** Zustand
*   **Animations:** Framer Motion
*   **Charts & Icons:** Recharts, Lucide React

## 📦 Local Development Setup

### 1. Backend Setup
1.  Navigate to the `backend` directory.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate it: `venv\Scripts\activate.bat` (Windows) or `source venv/bin/activate` (Mac/Linux).
4.  Install dependencies: `pip install -r requirements.txt`
5.  Create a `.env` file in `backend/` using the format in `.env.example`. Make sure to add your `GEMINI_API_KEY`.
6.  Run migrations: `python manage.py migrate`
7.  Seed database: `python manage.py seed_data`
8.  Start Django: `python manage.py runserver`
9.  *(In a separate terminal)* Start Redis (requires WSL or Docker on Windows).
10. *(In a separate terminal)* Start Celery: `celery -A config worker -l info --pool=solo` (Windows)

### 2. Frontend Setup
1.  Navigate to the `frontend` directory.
2.  Install dependencies: `npm install`
3.  Create a `.env` file with: `VITE_API_URL=http://localhost:8000/api`
4.  Start Vite dev server: `npm run dev`

## 🗄️ Database Schema and Model Relationships

The database is built on PostgreSQL and structured logically to handle users, quizzes, user attempts, and performance analytics.

- **User Model:** Custom user model extending AbstractUser, storing email, role (admin/user) and basic details.
- **Quiz:** Stores `topic`, `difficulty`, `status` (generating, ready, failed), `question_count`. Linked to the User who created it.
- **Question:** Linked to a Quiz (`ForeignKey`). Stores the prompt, correct answer, and explanation.
- **Choice:** Linked to a Question (`ForeignKey`). Stores the distractor text and whether it is correct.
- **Attempt:** Tracks a User's attempt on a Quiz (`ForeignKey` to both). Stores start/end time, score, and status (in_progress, completed).
- **UserResponse:** Linked to an Attempt and a Question. Stores the selected Choice and whether it was correct.
- **Analytics Models (UserStat, TopicPerformance, QuizStat):** Denormalized statistics linked via OneToOne or ForeignKey to Users/Quizzes for fast read-heavy analytical queries (e.g., streak, strongest/weakest topics, leaderboards).

## 📡 API Endpoint Overview

The REST API is organized logically around core resources. All endpoints (except Auth) require JWT authentication.

**Auth Endpoints:**
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Obtain JWT pairs
- `POST /api/auth/refresh/` - Refresh JWT
- `GET /api/auth/me/` - Get current user profile

**Quiz Endpoints:**
- `GET /api/quizzes/` - List available quizzes (paginated)
- `POST /api/quizzes/` - Create a new quiz (Triggers async Celery task)
- `GET /api/quizzes/:id/` - Get quiz details
- `GET /api/quizzes/:id/status/` - Poll for quiz generation status

**Attempts Endpoints:**
- `GET /api/attempts/` - Get user's quiz attempts history
- `POST /api/quizzes/:id/attempt/` - Start a new quiz attempt
- `POST /api/attempts/:id/submit/` - Submit a specific response
- `POST /api/attempts/:id/complete/` - Finish quiz, calculate score, and update analytics

**Analytics Endpoints:**
- `GET /api/analytics/me/` - Current User's performance summary (Streaks, Best Score, Topics)
- `GET /api/analytics/history/` - Historical trend data for scoring
- `GET /api/analytics/leaderboard/` - Global top performers

**Admin Endpoints:**
- `GET /api/admin/dashboard/` - High-level system statistics
- `GET /api/admin/users/` - System user management

## 🧠 Design Decisions & Trade-offs

*   **Asynchronous AI Generation:** 
    *   *Decision:* Instead of blocking the HTTP request while Gemini generates questions (which can easily timeout after 30+ seconds), I utilized Celery + Redis to queue the task and immediate return a `status: 'generating'` response. The frontend polls a lightweight `/status/` endpoint.
    *   *Trade-off:* Introduces slightly higher infrastructure complexity (needs Redis and Celery worker), but drastically improves UX.
*   **Analytics Denormalization:**
    *   *Decision:* Calculating overall average scores, streaks, and topic mastered on-the-fly via `GROUP BY` aggregations across the entire Attempts table during a Dashboard load would lead to N+1 querying and massive slowdowns at scale. Instead, I introduced a denormalized `UserStat` model that updates synchronously at the end of every attempt via Django Signals/Method calls.
    *   *Trade-off:* Higher write-time cost and potential for state de-sync, but guarantees lightning-fast user dashboard loads.
*   **JWT Authentication:**
    *   *Decision:* Decoupled the React frontend fully from the Django backend using statless JWTs instead of Session-based Auth.

## 🚧 Challenges Faced and Solutions

*   **Handling Unpredictable AI Outputs:**
    *   *Challenge:* The Gemini API would sometimes return malformed JSON, markdown-wrapped JSON, or miss required fields (like explanations or the exact correct answer text).
    *   *Solution:* Implemented robust Pydantic-like structural validation in the Celery task. If validation fails, the generator auto-retries the API call (up to 3 times) with an explicit prompt correction appended.
*   **React State Desync During Quiz:**
    *   *Challenge:* Managing the timer, selected answers, and submission states simultaneously led to edge-case bugs (e.g. submitting twice if the timer hits 0 while the user clicks "Next").
    *   *Solution:* Transitioned state management to Zustand with explicit action locks and `useEffect` unmount cleanup to guarantee single-submissions.

## 🤖 How AI Integration was Handled

1.  **Prompt Engineering:** I crafted a strict, rigid system prompt forcing the `gemini-1.5-flash` model to output a continuous, standard string of JSON without backticks or meta-narrative.
2.  **Service Layer:** Created a dedicated `GeminiService` class within the backend to abstract all AI initialization, token handling, and network calls via the `google-generativeai` SDK.
3.  **Task Offloading:** The `create_quiz` API view simply saves a Quiz record with `status='generating'` and passes the ID to a Celery delayed task. The task invokes `GeminiService`, parses the JSON, atomically saves Questions and Choices into Postgres, and flips `status='ready'`.

## 🧪 Testing Approach

I adopted a Postman-style API testing methodology throughout development because rapid iteration was necessary.

1.  **Endpoint Verification (Postman/ThunderClient):** 
    *   Used standard collections to hit Auth, Quizzes, Attempts, and Analytics endpoints individually. Validated payload constraints (e.g. attempting to submit an answer after an Attempt was marked "Completed" returns a `400 Bad Request`).
2.  **Celery/Queue Local Testing:** 
    *   Verified the async task by monitoring the Celery worker logs. Simulated Gemini failures (e.g., using a bad API key or forcing invalid JSON mocking) to ensure the Model's status correctly set to `failed` and updated the frontend.
3.  **Manual E2E Flow:**
    *   Full path traces: User Registration -> Token fetch -> Admin generating Quiz -> Frontend Polling -> User answers Questions -> User Views Analytics -> Validate Topic Strength calculations.

## 🌍 Deployment

*   **Backend:** Configured for Railway deployment via `railway.json` and `Procfile`. Set the required environment variables in your Railway project settings.
*   **Frontend:** Configured for Vercel deployment via `vercel.json` (resolves SPA routing issues). Set `VITE_API_URL` to your production backend URL.

## 👨‍💻 Authentication
To test the platform, you can register a new account or use the seeded admin credentials:
*   Email: `admin@quiz.com`
*   Password: `Admin@123`
