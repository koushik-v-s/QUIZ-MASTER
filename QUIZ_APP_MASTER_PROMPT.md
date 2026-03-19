# 🧠 MASTER AI BUILD PROMPT — AI-Powered Quiz App
# Backend Developer Assignment | Django + React + Supabase + Railway

---

> **HOW TO USE THIS PROMPT:**
> Paste this entire document into your AI assistant (Claude, Cursor, GPT-4o, etc.).
> The AI will build phase by phase and ASK YOU for credentials at the right time.
> You just respond with the requested info and it continues building.

---

## 🎯 PROJECT OVERVIEW

You are building a **full-stack AI-Powered Quiz Application** for a backend developer job interview assignment. This must be production-grade, well-architected, and impressive.

**Interviewer's focus**: Database design, API architecture, auth, external AI integration, performance, scalability.

**Stack Decision (already chosen — do not deviate):**
- **Backend**: Django 4.2 + Django REST Framework + SimpleJWT
- **Database**: PostgreSQL via Supabase (connection pooling via pgbouncer)
- **AI Integration**: Google Gemini API (gemini-1.5-flash model)
- **Deployment**: Railway (backend) + Vercel (frontend)
- **Frontend**: React 18 + Vite + TailwindCSS + Framer Motion + React Bits components
- **Cache**: Redis (Railway add-on) via django-redis
- **Task Queue**: Celery + Redis (for async AI generation)
- **API Docs**: drf-spectacular (OpenAPI/Swagger)
- **Auth**: JWT (access + refresh tokens) + strict role-based permissions (Admin creates, User attempts)

---

## 🔑 ROLE DEFINITIONS — READ THIS BEFORE BUILDING ANYTHING

This is the **core business rule** of the entire application. Every model, every view, every permission class, every frontend page, every route guard must respect this without exception.

| Capability | `admin` role | `user` role |
|---|---|---|
| Register / Login | ✅ | ✅ |
| View own profile | ✅ | ✅ |
| Browse published quizzes | ✅ (own quizzes only) | ✅ (all published quizzes) |
| **Create a quiz** | ✅ **ONLY ADMINS** | ❌ Returns 403 |
| **Trigger AI generation** | ✅ **ONLY ADMINS** | ❌ Returns 403 |
| Edit / Delete own quiz | ✅ | ❌ Returns 403 |
| **Attempt a quiz** | ❌ Returns 403 | ✅ **ONLY USERS** |
| **Submit answers** | ❌ Returns 403 | ✅ **ONLY USERS** |
| View own attempt results | ❌ | ✅ |
| View own score analytics | ❌ | ✅ |
| View quiz attempt stats (who attempted, avg score) | ✅ (own quizzes) | ❌ |
| Manage all platform users | ✅ | ❌ |
| View platform-wide stats | ✅ | ❌ |
| Promote user to admin | ✅ | ❌ |

**Critical enforcement rules — implement at permission class level, not in view logic:**
- On registration, `role` is always hardcoded to `'user'`. Even if client sends `{"role": "admin"}` in the body, it is silently ignored. Log a warning if attempted.
- `role` field is `read_only=True` in the profile serializer — cannot be changed via `/auth/me/`.
- Only endpoint that changes role: `PATCH /api/v1/admin/users/{id}/` — protected by `IsAdminRole`.
- If an `admin` calls any attempt endpoint → `403 {"error": "Admins cannot attempt quizzes. Use a user account."}`.
- If a `user` calls any quiz creation/edit endpoint → `403 {"error": "Only admins can create and manage quizzes."}`.
- First superuser created via `python manage.py seed_data` gets `role='admin'`.

---

## 📁 FINAL PROJECT STRUCTURE

```
quiz-app/
├── backend/                    # Django project root
│   ├── config/                 # Django settings package
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── users/              # Auth, profiles, roles
│   │   ├── quizzes/            # Quiz CRUD, AI generation (admin only)
│   │   ├── attempts/           # Attempt tracking, scoring (user only)
│   │   └── analytics/          # User performance analytics
│   ├── core/                   # Shared utilities
│   │   ├── permissions.py      # IsAdminRole, IsUserRole, IsQuizOwner
│   │   ├── pagination.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   ├── requirements.txt
│   ├── Procfile                # For Railway
│   ├── railway.json
│   └── manage.py
│
└── frontend/                   # React + Vite app
    ├── src/
    │   ├── api/                # Axios instances + endpoints
    │   ├── components/         # Shared UI components
    │   │   ├── ui/             # Base components (Button, Card, Input)
    │   │   ├── layout/         # AdminNavbar, UserNavbar, Sidebar
    │   │   └── animations/     # All React Bits components from UI.md
    │   ├── pages/
    │   │   ├── Auth/           # Login, Register (shared)
    │   │   ├── AdminDashboard/ # Admin home, quiz management, user mgmt
    │   │   ├── UserDashboard/  # User home, browse, take quiz, analytics
    │   │   └── Shared/         # 404, unauthorized pages
    │   ├── hooks/              # Custom React hooks
    │   ├── store/              # Zustand (auth store with role)
    │   ├── routes/             # AdminRoute, UserRoute guards
    │   ├── utils/
    │   └── App.jsx
    ├── package.json
    └── vite.config.js
```

---

## 🗄️ DATABASE SCHEMA (Build this exactly)

```sql
-- Users (extends Django AbstractUser)
users_user:
  id (UUID, PK)
  email (unique)
  username (unique)
  role (enum: 'admin', 'user')  -- 'user' is always the default on registration
  avatar_url
  is_active
  date_joined
  last_login

-- Quiz (created ONLY by admins)
quizzes_quiz:
  id (UUID, PK)
  created_by (FK → users_user, must be role='admin')
  title
  topic
  difficulty (enum: 'easy', 'medium', 'hard')
  question_count (int, 1-50)
  time_limit_minutes (nullable)
  is_public (bool)
  status (enum: 'generating', 'ready', 'failed')
  generation_prompt (text)
  ai_model_used
  created_at
  updated_at

-- Question
quizzes_question:
  id (UUID, PK)
  quiz (FK → quizzes_quiz)
  order (int)
  question_text (text)
  question_type (enum: 'mcq', 'true_false')
  explanation (text, shown ONLY after user completes attempt)
  points (default 1)
  created_at

-- Choice
quizzes_choice:
  id (UUID, PK)
  question (FK → quizzes_question)
  choice_text
  is_correct (bool)  -- NEVER exposed to users during quiz-taking
  order (int)

-- Attempt (created ONLY by users)
attempts_attempt:
  id (UUID, PK)
  user (FK → users_user, must be role='user')
  quiz (FK → quizzes_quiz)
  status (enum: 'in_progress', 'completed', 'abandoned')
  score (float, 0-100)
  total_points_earned (int)
  total_points_possible (int)
  started_at
  completed_at
  time_taken_seconds (int)

-- AttemptAnswer
attempts_attemptanswer:
  id (UUID, PK)
  attempt (FK → attempts_attempt)
  question (FK → quizzes_question)
  selected_choice (FK → quizzes_choice, nullable)
  is_correct (bool)
  time_taken_seconds (int)
  answered_at

-- Analytics (for users only — admins have quiz-level stats instead)
analytics_userstat:
  id (UUID, PK)
  user (OneToOne → users_user, role='user' only)
  total_quizzes_taken (int)
  average_score (float)
  best_score (float)
  total_time_spent_seconds (int)
  strongest_topic (text)
  weakest_topic (text)
  streak_days (int)
  last_activity_date
  updated_at

analytics_topicperformance:
  id (UUID, PK)
  user (FK → users_user)
  topic (text)
  attempts_count (int)
  average_score (float)
  best_score (float)
  updated_at

-- Quiz-level stats for admins (denormalized for performance)
analytics_quizstat:
  id (UUID, PK)
  quiz (OneToOne → quizzes_quiz)
  total_attempts (int)
  average_score (float)
  highest_score (float)
  lowest_score (float)
  completion_rate (float)  -- % who completed vs abandoned
  updated_at
```

---

## 🔌 API ENDPOINTS (Build all of these — role access marked on every endpoint)

### Auth (`/api/v1/auth/`)
```
POST   /register/         → Register [Public — role always set to 'user', never trust client]
POST   /login/            → Login, returns {access, refresh, user: {id, email, username, role}}
POST   /token/refresh/    → Refresh access token [Public]
POST   /logout/           → Blacklist refresh token [IsAuthenticated]
GET    /me/               → Get current user profile [IsAuthenticated]
PATCH  /me/               → Update profile — role field is read_only [IsAuthenticated]
POST   /change-password/  → Change password [IsAuthenticated]
```

### Quizzes (`/api/v1/quizzes/`)
```
GET    /                      → List published+ready quizzes [IsAuthenticated — both roles can browse]
POST   /                      → Create quiz + trigger AI generation [IsAdminRole ONLY → 403 for users]
GET    /{id}/                 → Quiz detail WITH questions (no correct answers for users) [IsAuthenticated]
PATCH  /{id}/                 → Update quiz [IsAdminRole + IsQuizOwner]
DELETE /{id}/                 → Delete quiz [IsAdminRole + IsQuizOwner]
GET    /my/                   → Quizzes created by this admin [IsAdminRole ONLY]
POST   /{id}/regenerate/      → Re-trigger AI generation [IsAdminRole + IsQuizOwner]
GET    /{id}/status/          → Poll generation status [IsAdminRole ONLY]
GET    /{id}/attempt-stats/   → Attempt count, avg score, top scorers [IsAdminRole + IsQuizOwner]
```

### Attempts (`/api/v1/attempts/`)
```
⚠️ ALL endpoints below → IsUserRole ONLY. 
   Admin calling any of these gets: 403 {"error": "Admins cannot attempt quizzes."}

POST   /                  → Start attempt for a quiz [IsUserRole]
GET    /{id}/             → Get attempt detail [IsUserRole, must own attempt]
POST   /{id}/answer/      → Submit answer for one question [IsUserRole, must own attempt]
POST   /{id}/complete/    → Complete attempt + calculate score [IsUserRole, must own attempt]
GET    /{id}/results/     → Full results with correct answers + explanations [IsUserRole, must own]
GET    /history/          → Paginated past attempts list [IsUserRole]
```

### Analytics (`/api/v1/analytics/`)
```
GET    /me/               → User's overall stats [IsUserRole ONLY]
GET    /me/topics/        → Topic-by-topic breakdown [IsUserRole ONLY]
GET    /me/history/       → Score history over time for chart [IsUserRole ONLY]
GET    /leaderboard/      → Top scoring users [IsAuthenticated — both roles can view]
GET    /quiz/{id}/stats/  → Stats for a specific quiz [IsAdminRole + IsQuizOwner]
```

### Admin Panel (`/api/v1/admin/`)
```
⚠️ ALL endpoints below → IsAdminRole ONLY. 403 for users.

GET    /users/            → List all users with role badges [IsAdminRole]
GET    /users/{id}/       → User detail + their attempt history [IsAdminRole]
PATCH  /users/{id}/       → Promote to admin OR deactivate [IsAdminRole]
GET    /quizzes/          → All quizzes including drafts/failed [IsAdminRole]
DELETE /quizzes/{id}/     → Force delete any quiz [IsAdminRole]
GET    /stats/            → Platform stats: users, quizzes, attempts, avg score [IsAdminRole]
```

---

## 🤖 AI INTEGRATION DESIGN

**Provider**: Google Gemini (gemini-1.5-flash) — already have API key

**Flow**:
1. Admin POSTs to `/api/v1/quizzes/` with `{topic, question_count, difficulty}`
2. Quiz record created with `status: "generating"`
3. Celery task dispatched: `generate_quiz_questions.delay(quiz_id)`
4. Celery worker calls Gemini with structured prompt
5. Parse JSON response → create Question + Choice records
6. Quiz status updated to `"ready"` or `"failed"`
7. Admin frontend polls `/api/v1/quizzes/{id}/status/` every 2 seconds

**Gemini Prompt Template**:
```python
QUIZ_GENERATION_PROMPT = """
You are a quiz generation expert. Generate exactly {question_count} multiple choice questions about "{topic}" at {difficulty} difficulty level.

Rules:
- Each question must have exactly 4 choices
- Exactly 1 choice must be correct
- Include a brief explanation for the correct answer
- Questions should be clear, unambiguous, and educational
- Vary question styles (definition, application, analysis)

Respond ONLY with valid JSON in this exact format:
{{
  "questions": [
    {{
      "question_text": "...",
      "explanation": "...",
      "points": 1,
      "choices": [
        {{"choice_text": "...", "is_correct": true}},
        {{"choice_text": "...", "is_correct": false}},
        {{"choice_text": "...", "is_correct": false}},
        {{"choice_text": "...", "is_correct": false}}
      ]
    }}
  ]
}}
"""
```

**Error Handling**:
- Retry failed AI calls up to 3 times with exponential backoff
- If all retries fail → mark quiz `status: "failed"`, store error message
- Validate JSON structure before saving to DB
- Rate limit: max 10 AI generations per admin per day (Redis counter)
- Log token usage per generation for cost tracking

---

## 🔐 AUTHENTICATION & PERMISSIONS

**JWT Setup**:
- Access token: 15 minutes
- Refresh token: 7 days
- Token blacklisting on logout

**Permission Classes** — build ALL four in `core/permissions.py`:
```python
class IsAdminRole(BasePermission):
    """Allows access ONLY to role='admin'. Users get 403."""
    message = "Only admins can perform this action."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsUserRole(BasePermission):
    """Allows access ONLY to role='user'. Admins get 403."""
    message = "Admins cannot attempt quizzes. Use a user account."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'user'

class IsQuizOwner(BasePermission):
    """Object-level: only the admin who created this quiz can edit/delete."""
    message = "You do not own this quiz."
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class IsQuizOwnerOrSuperAdmin(BasePermission):
    """Quiz owner OR superuser (initial seed admin) can modify."""
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or request.user.is_superuser
```

**Applying permissions to views — strict mapping:**
```
Quiz CREATE, /my/, /regenerate/, /status/  → [IsAdminRole]
Quiz UPDATE, DELETE                         → [IsAdminRole, IsQuizOwner]
Quiz GET (detail + list)                    → [IsAuthenticated]
Attempt ALL endpoints                       → [IsUserRole]
Analytics /me/, /me/topics/, /me/history/  → [IsUserRole]
Analytics /leaderboard/                    → [IsAuthenticated]
Analytics /quiz/{id}/stats/                → [IsAdminRole, IsQuizOwner]
Admin panel ALL endpoints                  → [IsAdminRole]
```

**Role System (strict separation):**
- `admin`: Content creator. Creates AI-powered quizzes, monitors who attempted them, manages platform users, views platform-wide stats. **Cannot attempt quizzes.**
- `user`: Learner. Browses published quizzes created by admins, attempts and completes them, tracks own score history. **Cannot create quizzes.**
- Registration always produces `role='user'`. Only an existing admin can promote via admin panel.

---

## ⚡ PERFORMANCE REQUIREMENTS

**Caching** (Redis):
```python
# Cache quiz list: 5 minutes
# Cache quiz detail (ready status): 10 minutes
# Cache leaderboard: 1 minute (Redis sorted set for O(log n) ranking)
# Cache user stats: 2 minutes
# Cache quiz attempt stats: 3 minutes
# Invalidate on write operations
```

**Database**:
- Add indexes: `quiz.status`, `quiz.is_public`, `attempt.user+quiz`, `topicperformance.user+topic`
- Use `select_related` and `prefetch_related` everywhere
- Paginate all list endpoints (default 20, max 100)

**Query Optimization**:
- Analytics computed via DB aggregation not Python loops
- Use `annotate()` for score calculations
- Bulk create questions/choices after AI generation
- Leaderboard uses Redis sorted sets (ZADD/ZREVRANK) for O(log n) ranking

**Idempotency**:
- Prevent duplicate quiz generation: check if same admin already has a quiz with same topic+difficulty in `generating` status → return existing quiz, do not dispatch new Celery task
- Prevent duplicate attempts: if user already has `in_progress` attempt for same quiz → return existing attempt, do not create new one

---

## 🎨 FRONTEND DESIGN

### ⚠️ CRITICAL UI INSTRUCTION — READ BEFORE WRITING ANY FRONTEND CODE

**STEP 1 — MANDATORY: Before writing a single line of frontend code, read the file at:**
```
TEACH-EDISON/UI.md
```
This file contains React Bits components and animated backgrounds as `npx` CLI install commands. **Every single component listed in that file MUST be used in this project.** They are not optional. Install all of them first, then build the UI around them.

**STEP 2 — Install everything from UI.md first:**
```bash
# Read UI.md and run every npx jsrepo command listed in it
# These are the COMPULSORY components — use all of them
```

**STEP 3 — You may ADDITIONALLY use these if needed beyond what UI.md provides:**
```bash
npx jsrepo add github/DavidHDev/react-bits/src/Backgrounds/Particles
npx jsrepo add github/DavidHDev/react-bits/src/TextAnimations/GradientText
npx jsrepo add github/DavidHDev/react-bits/src/TextAnimations/BlurText
npx jsrepo add github/DavidHDev/react-bits/src/TextAnimations/CountUp
npx jsrepo add github/DavidHDev/react-bits/src/Components/SpotlightCard
npx jsrepo add github/DavidHDev/react-bits/src/Backgrounds/Aurora
```
These above are supplementary — add them only where the UI.md components do not already cover the need.

---

**Aesthetic Direction**: Dark, futuristic, tech-noir with electric blue/violet accents. Think "neural network meets terminal". Glassmorphism cards on deep dark backgrounds. Every background and animation must come from UI.md first.

**Color Palette**:
```css
--bg-primary: #030712        /* near black */
--bg-secondary: #0f172a      /* dark slate */
--bg-card: rgba(15,23,42,0.8) /* glass */
--accent-primary: #6366f1    /* electric indigo */
--accent-secondary: #8b5cf6  /* violet */
--accent-glow: #4f46e5       /* deep blue glow */
--text-primary: #f1f5f9
--text-secondary: #94a3b8
--success: #10b981
--error: #ef4444
--warning: #f59e0b
```

**Typography**:
```
Display/Headings: "Space Mono" or "JetBrains Mono" (monospace, techy)
Body: "DM Sans" (clean, readable)
Code/Stats: "Fira Code" (monospaced numbers)
```

---

## 🚀 BUILD PHASES — EXECUTE IN ORDER

---

### ═══════════════════════════════════════
### PHASE 1: PROJECT SETUP & CONFIGURATION
### ═══════════════════════════════════════

**WHAT TO BUILD:**

1. Create Django project with the folder structure above
2. Install all dependencies into `requirements.txt`:
```
Django==4.2.9
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
django-environ==0.11.2
drf-spectacular==0.27.0
psycopg2-binary==2.9.9
redis==5.0.1
django-redis==5.4.0
celery==5.3.6
google-generativeai==0.8.3
Pillow==10.2.0
gunicorn==21.2.0
whitenoise==6.6.0
django-filter==23.5
```

3. Create `config/settings/base.py` with:
   - All installed apps
   - REST_FRAMEWORK config (JWT auth, pagination, filtering, exception handler)
   - SIMPLE_JWT config (15min access, 7day refresh, blacklist)
   - CORS config
   - Celery config (broker = Redis)
   - Cache config (Redis backend)
   - drf-spectacular config

4. Create `config/settings/production.py`:
   - Read all secrets from environment variables via `django-environ`
   - Static files via WhiteNoise
   - Database from `DATABASE_URL` env var

5. Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/api/v1/health/",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

6. Create `Procfile`:
```
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2
worker: celery -A config worker -l info
```

**❓ STOP AND ASK THE USER:**
> "Phase 1 setup is ready. Before I connect to Supabase, I need your Supabase PostgreSQL connection details. Please go to your Supabase dashboard → Project Settings → Database → Connection string (URI mode, port 6543 for pgbouncer). It looks like: `postgresql://postgres.xxxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres`
> Also, please provide your Railway project's Redis URL if you've added a Redis service, OR tell me if you want me to show you how to add Redis on Railway first."

*(Wait for user to provide DATABASE_URL and REDIS_URL before proceeding to Phase 2)*

---

### ═══════════════════════════════════════
### PHASE 2: DATA MODELS
### ═══════════════════════════════════════

**WHAT TO BUILD** (after receiving DB credentials):

Create all 4 Django apps: `users`, `quizzes`, `attempts`, `analytics`

**`apps/users/models.py`**:
```python
# Custom User extending AbstractBaseUser + PermissionsMixin
# Fields: id(UUID), email, username, role(choices: 'admin'/'user'), avatar_url
# role default = 'user' at the model level
# Custom UserManager with create_user (role='user') and create_superuser (role='admin')
# __str__, full_name property
```

**`apps/quizzes/models.py`**:
```python
# Quiz model — created_by must be role='admin' (validated in serializer)
# Question model with order, points
# Choice model — is_correct never serialized to users during quiz-taking
# Custom QuerySet: QuizQuerySet with .public(), .ready(), .by_admin(user)
# Manager using QuerySet
# Quiz.get_questions_with_choices() using prefetch (hides is_correct by default)
```

**`apps/attempts/models.py`**:
```python
# Attempt model — user must be role='user' (enforced by IsUserRole permission)
# AttemptAnswer model
# Attempt.calculate_score() — DB aggregation, not Python loops
# Attempt.complete() — calculates score, saves, triggers analytics refresh
```

**`apps/analytics/models.py`**:
```python
# UserStat model (OneToOne with User, role='user' only)
# TopicPerformance model
# QuizStat model (OneToOne with Quiz, for admin quiz-level analytics)
# UserStat.refresh_for_user(user) classmethod — recalculates all stats via aggregation
# QuizStat.refresh_for_quiz(quiz) classmethod — recalculates quiz-level stats
```

**Also build**:
- All `admin.py` files with proper list_display, search_fields, filters
- All database migrations
- Seed management command: `python manage.py seed_data` — creates 1 admin user + 3 sample users + 2 sample ready quizzes
- Add all DB indexes as `Meta.indexes`

**❓ STOP AND ASK THE USER:**
> "Models are done. I'm about to run migrations. Please confirm you want me to run:
> `python manage.py makemigrations && python manage.py migrate`
> Also confirm: what should the default admin email/password be for the seed data? (e.g., admin@quiz.com / Admin@123)"

---

### ═══════════════════════════════════════
### PHASE 3: AUTHENTICATION SYSTEM
### ═══════════════════════════════════════

**WHAT TO BUILD:**

**`apps/users/serializers.py`**:
- `UserRegistrationSerializer`: validate email uniqueness, password strength (min 8 chars, 1 uppercase, 1 number), hash password. `role` field NOT in writable fields — always set to `'user'` in `create()`. Warn in logs if `role` was present in request data.
- `UserLoginSerializer`: validate credentials, return user
- `UserProfileSerializer`: read/write profile fields. `role` is `read_only=True` — never writable here.
- `ChangePasswordSerializer`: validate old password, confirm new password match

**`apps/users/views.py`**:
- `RegisterView(CreateAPIView)`: create user with `role='user'` hardcoded, create UserStat record (only for users), return JWT pair + full user object including `role`
- `LoginView(GenericAPIView)`: validate credentials, return `{access, refresh, user: {id, email, username, role}}` — frontend uses `role` to decide which dashboard to render
- `LogoutView`: blacklist refresh token
- `MeView(RetrieveUpdateAPIView)`: get/update profile — `role` is read-only
- `ChangePasswordView`: update password

**`apps/users/urls.py`**: all auth endpoints

**`core/permissions.py`**: Build all 4 permission classes as defined in the Role Definitions section above.

**`core/exceptions.py`**: Custom exception handler that always returns:
```json
{"success": false, "error": {"code": "VALIDATION_ERROR", "message": "...", "details": {}}}
```

**Test auth manually**:
- Register → verify role is 'user' → Login → check role in response → use access token → refresh → logout

---

### ═══════════════════════════════════════
### PHASE 4: AI INTEGRATION (GEMINI)
### ═══════════════════════════════════════

**WHAT TO BUILD:**

**`apps/quizzes/ai_service.py`**:
```python
import google.generativeai as genai
import json
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class GeminiQuizGenerator:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate(self, topic: str, question_count: int, difficulty: str) -> dict:
        prompt = self._build_prompt(topic, question_count, difficulty)

        for attempt in range(3):  # retry with exponential backoff
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=4096,
                    )
                )
                # Log token usage for cost tracking
                logger.info(f"Gemini tokens used: {response.usage_metadata}")
                return self._parse_response(response.text)
            except Exception as e:
                logger.warning(f"Gemini attempt {attempt+1} failed: {e}")
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)  # 1s, 2s, 4s

    def _build_prompt(self, topic, count, difficulty) -> str:
        # Full prompt from the template above
        pass

    def _parse_response(self, text: str) -> dict:
        # Strip markdown code fences if present
        # Parse JSON
        # Validate structure: must have 'questions' array
        # Validate each question: exactly 4 choices, exactly 1 is_correct=true
        # Raise ValueError with clear message if validation fails
        pass
```

**`apps/quizzes/tasks.py`** (Celery):
```python
from celery import shared_task
from .models import Quiz, Question, Choice
from .ai_service import GeminiQuizGenerator
from apps.analytics.models import QuizStat

@shared_task(bind=True, max_retries=3)
def generate_quiz_questions(self, quiz_id: str):
    quiz = Quiz.objects.get(id=quiz_id)

    try:
        generator = GeminiQuizGenerator()
        data = generator.generate(quiz.topic, quiz.question_count, quiz.difficulty)

        # Bulk create questions then choices
        questions_to_create = [
            Question(quiz=quiz, order=i, **{k: v for k, v in q.items() if k != 'choices'})
            for i, q in enumerate(data['questions'], 1)
        ]
        created_questions = Question.objects.bulk_create(questions_to_create)

        choices_to_create = []
        for question, q_data in zip(created_questions, data['questions']):
            for j, c in enumerate(q_data['choices']):
                choices_to_create.append(Choice(question=question, order=j, **c))
        Choice.objects.bulk_create(choices_to_create)

        quiz.status = 'ready'
        quiz.save(update_fields=['status', 'updated_at'])

        # Initialize quiz stats
        QuizStat.objects.get_or_create(quiz=quiz)

    except Exception as exc:
        quiz.status = 'failed'
        quiz.save(update_fields=['status'])
        raise self.retry(exc=exc, countdown=60)
```

**Idempotency + Rate limiting in `apps/quizzes/views.py`**:
```python
from django.core.cache import cache
from datetime import date

def check_ai_rate_limit(user):
    """Max 10 AI generations per admin per day"""
    key = f"ai_gen_count:{user.id}:{date.today()}"
    count = cache.get(key, 0)
    if count >= 10:
        raise ValidationError("Daily AI generation limit (10) reached. Try again tomorrow.")
    cache.set(key, count + 1, timeout=86400)

def check_duplicate_generation(user, topic, difficulty):
    """Prevent duplicate in-flight generations"""
    exists = Quiz.objects.filter(
        created_by=user, topic=topic, difficulty=difficulty, status='generating'
    ).exists()
    if exists:
        raise ValidationError("A quiz with this topic and difficulty is already being generated.")
```

**❓ STOP AND ASK THE USER:**
> "AI integration is built. The Gemini API key will be stored as an environment variable `GEMINI_API_KEY`. Before setting that on Railway, do you want to test the AI generation locally first? If yes, create a `.env` file in `/backend/` with:
> ```
> GEMINI_API_KEY=AIzaSyDLuZ2_XGS0XJjEMDhWYlnQZJdUe7bnGrMl
> ```
> Type 'yes, test locally' or 'skip to Railway deployment'."

---

### ═══════════════════════════════════════
### PHASE 5: ALL API VIEWS & SERIALIZERS
### ═══════════════════════════════════════

**WHAT TO BUILD:**

**`apps/quizzes/serializers.py`**:
- `ChoiceSerializer`: id, choice_text, order — **never include is_correct** (used during quiz-taking)
- `ChoiceWithAnswerSerializer`: includes is_correct — **only used in results after attempt completion**
- `QuestionSerializer`: question_text, question_type, points, choices (using ChoiceSerializer)
- `QuestionWithAnswerSerializer`: includes explanation + ChoiceWithAnswerSerializer (results only)
- `QuizListSerializer`: id, title, topic, difficulty, question_count, status, created_by_username, created_at
- `QuizDetailSerializer`: all fields + nested questions WITHOUT answers (admin sees all; user sees no correct answers)
- `QuizAdminDetailSerializer`: all fields + questions WITH correct answers (admin preview only)
- `QuizCreateSerializer`: validate inputs, call `check_ai_rate_limit` + `check_duplicate_generation`, trigger Celery task on save

**`apps/attempts/serializers.py`**:
- `AttemptStartSerializer`: quiz_id → validate quiz is ready + is_public + user has no active attempt for this quiz
- `SubmitAnswerSerializer`: question_id, choice_id → validate both belong to attempt's quiz
- `AttemptResultSerializer`: full results including score, per-question breakdown with correct answer + explanation (QuestionWithAnswerSerializer)

**`apps/analytics/serializers.py`**:
- `UserStatSerializer` (user-facing)
- `TopicPerformanceSerializer`
- `ScoreHistorySerializer` (for chart: date + score per attempt)
- `LeaderboardSerializer` (username, avg_score, total_attempts)
- `QuizStatSerializer` (admin-facing: attempts, avg_score, completion_rate)

**ALL VIEWS** — implement with:
- Correct permission class from the mapping table above — no exceptions
- `@action` decorators for custom endpoints
- `get_queryset()` with role-aware filtering
- Cache decorators on read-heavy views
- `drf-spectacular` `@extend_schema` decorators for all endpoints
- All responses wrapped in `{"success": true, "data": ..., "message": "..."}` format

**`config/urls.py`**:
```python
urlpatterns = [
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/quizzes/', include('apps.quizzes.urls')),
    path('api/v1/attempts/', include('apps.attempts.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/admin/', include('apps.admin_panel.urls')),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('api/v1/health/', HealthCheckView.as_view()),
]
```

---

### ═══════════════════════════════════════
### PHASE 6: FRONTEND — REACT APP
### ═══════════════════════════════════════

## ⚠️ MANDATORY FIRST STEP — DO THIS BEFORE WRITING ANY COMPONENT:

**1. Open and read the file: `TEACH-EDISON/UI.md`**
**2. Install EVERY component listed in that file using its exact `npx` command**
**3. Map each installed component to where it will be used (listed below)**
**4. Only then start writing page code**

If you skip reading UI.md, you are violating the build instructions. Every animation, background, and interactive component available in UI.md must appear somewhere in this app.

---

**Setup**:
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install tailwindcss @tailwindcss/vite framer-motion axios zustand recharts react-router-dom react-hot-toast lucide-react

# STEP 1: Install EVERYTHING from UI.md (read the file and run all npx commands)

# STEP 2: Install supplementary React Bits components only if not already covered by UI.md:
npx jsrepo add github/DavidHDev/react-bits/src/Backgrounds/Particles
npx jsrepo add github/DavidHDev/react-bits/src/TextAnimations/GradientText
npx jsrepo add github/DavidHDev/react-bits/src/TextAnimations/BlurText
npx jsrepo add github/DavidHDev/react-bits/src/TextAnimations/CountUp
npx jsrepo add github/DavidHDev/react-bits/src/Components/SpotlightCard
npx jsrepo add github/DavidHDev/react-bits/src/Backgrounds/Aurora
```

**`src/api/axios.js`**:
```javascript
// Axios instance with baseURL from env
// Request interceptor: add Authorization: Bearer {access_token} from zustand
// Response interceptor: on 401, attempt token refresh, retry original request
// On refresh fail: clear store + redirect to /login
```

**`src/store/authStore.js`** (Zustand):
```javascript
// State: user, accessToken, refreshToken, isAuthenticated
// user object includes: { id, email, username, role }
// Actions: login(tokens, user), logout(), updateUser(user), refreshToken()
// Persist to localStorage
```

**`src/routes/index.jsx`** — Role-based routing:
```javascript
// AdminRoute: if user.role !== 'admin' → redirect to /dashboard
// UserRoute: if user.role !== 'user' → redirect to /dashboard
// App.jsx: after login, role decides which dashboard component renders at /dashboard
const AdminRoute = ({ children }) => {
  const { user } = useAuthStore();
  if (!user) return <Navigate to="/login" />;
  if (user.role !== 'admin') return <Navigate to="/dashboard" replace />;
  return children;
};
const UserRoute = ({ children }) => {
  const { user } = useAuthStore();
  if (!user) return <Navigate to="/login" />;
  if (user.role !== 'user') return <Navigate to="/dashboard" replace />;
  return children;
};
```

---

### LOGIN / REGISTER PAGE (shared — both roles use this)
**Route**: `/login`, `/register`

- **Background**: Use the animated background from UI.md (Aurora or equivalent)
- Frosted glass card centered on screen with `backdrop-blur-xl border border-white/10`
- Input fields with animated bottom-border glow on focus (from UI.md or Framer Motion)
- Password strength meter on register page (colored bar: red → yellow → green)
- Submit button with loading spinner state
- After login: read `role` from API response → if `admin` render AdminDashboard, if `user` render UserDashboard at `/dashboard`
- Smooth animated transition between login ↔ register forms

---

### 🖥️ ADMIN DASHBOARD (role='admin' — wrapped in AdminRoute)
**Route**: `/dashboard` when role === 'admin'

**Layout**: Dark left sidebar (fixed) + scrollable main content

**Sidebar navigation** (admin sees only these):
```
📊  Overview          → /dashboard
✨  Create Quiz       → /quiz/create
📚  My Quizzes        → /quizzes/my
👥  Users             → /admin/users
📈  Platform Stats    → /admin/stats
👤  Profile           → /profile
```
No "Browse Quizzes to attempt", no "My Progress", no attempt-related links anywhere.

**Main Overview content**:
- Use the animated background/particles from UI.md (subtle, low opacity)
- Header: `"Welcome back, [username]"` with `[ADMIN]` role badge in electric indigo — use GradientText or BlurText from UI.md
- 4 SpotlightCards (from UI.md or supplementary) with CountUp animations:
  - **Total Quizzes Created** (by this admin)
  - **Total Platform Users**
  - **Total Attempts** (across all this admin's quizzes)
  - **Platform Avg Score** (across all attempts on this admin's quizzes)
- **Recent Attempts Feed**: last 10 attempts on this admin's quizzes — "User X scored 85% on Python Basics — 2h ago"
- **Big glowing CTA**: `"+ Create New Quiz with AI"` button in hero section (admin's primary action)
- **Quiz Status Table**: recent quizzes with status badges (generating/ready/failed) and action buttons

**Admin — Create Quiz** (`/quiz/create`, AdminRoute):
- 3-step animated wizard using UI.md components for transitions:
  - Step 1: Title + Topic input with animated placeholder suggestions
  - Step 2: Difficulty selector (Easy / Medium / Hard) — 3 animated selection cards
  - Step 3: Question count slider (5–50) + time limit toggle + is_public toggle + review summary
- Submit → full-screen "🤖 AI is generating your quiz..." with pulsing animated SVG (neural network / brain icon from UI.md)
- Polls `/api/v1/quizzes/{id}/status/` every 2 seconds
- On `status: 'ready'` → animate transition to quiz detail page
- On `status: 'failed'` → show error state with "Retry Generation" button

**Admin — My Quizzes** (`/quizzes/my`, AdminRoute):
- Paginated card grid of own quizzes
- Each card: title, topic chip, difficulty badge, question count, status badge, attempt count, avg score
- Actions: Preview | Edit | Delete | View Attempt Stats
- Filter by status (generating / ready / failed) and difficulty

**Admin — Quiz Detail / Preview** (`/quiz/:id`, AdminRoute):
- Admin CAN see all correct answers in preview mode (toggle "Show Answers" button)
- Quiz attempt stats panel: total attempts, avg score, score distribution bar chart
- Table: users who attempted — username, score, time taken, date

**Admin — Users** (`/admin/users`, AdminRoute):
- Searchable, sortable data table
- Columns: Username, Email, Role badge, Quizzes Attempted, Avg Score, Join date, Status
- Row actions: Promote to Admin | Deactivate (with confirmation modal)

**Admin — Platform Stats** (`/admin/stats`, AdminRoute):
- CountUp stat cards: total users, total quizzes, total attempts, platform avg score
- Line chart (Recharts): new users per day last 30 days
- Bar chart (Recharts): top 10 quizzes by attempt count
- Pie chart (Recharts): difficulty distribution

---

### 📱 USER DASHBOARD (role='user' — wrapped in UserRoute)
**Route**: `/dashboard` when role === 'user'

**Layout**: Top navbar only — no sidebar. Full-width content. Cleaner, learner-focused.

**Top navbar** (user sees only these):
```
🏠 Home    🔍 Browse Quizzes    📊 My Progress    👤 Profile
```
No "Create Quiz", no admin links, no platform stats anywhere.

**Main Home content**:
- Use animated background from UI.md (particles or equivalent)
- Personalized greeting: `"Good morning, [username] 👋"` using BlurText or equivalent from UI.md
- 🔥 Streak counter top-right: flame icon + `"5 day streak"` with CountUp
- 4 SpotlightCards with CountUp on mount:
  - **Quizzes Completed**
  - **Average Score** (%)
  - **Best Score** (%)
  - **Total Time Spent** (formatted "2h 34m")
- **Continue where you left off**: card for last in-progress attempt with "Resume" button (if exists)
- **Recommended Quizzes**: 3 quiz cards from published library
- **Recent Performance**: mini sparkline chart of last 5 attempt scores (Recharts)
- **No "Create Quiz" button anywhere** — not even hidden

**User — Browse Quizzes** (`/quizzes`, UserRoute):
- Responsive grid of quiz cards (filter by topic, difficulty)
- Each card: title, topic chip, difficulty badge, question count, admin creator name, community avg score
- Click card → Quiz intro page (no correct answers shown)
- "Start Quiz" CTA → POST `/api/v1/attempts/` → navigate to take quiz

**User — Take Quiz** (`/quiz/:id/take`, UserRoute):
- Full-screen focus mode — hide top navbar
- Question card slides in from right (Framer Motion)
- 4 choice buttons with hover glow using UI.md components
- Progress bar at top + "Question X of Y" counter + timer (if time_limit set, color turns red < 1 min)
- After selecting → brief flash (neutral, no green/red yet — revealed only in results)
- No going back (linear progression enforced on backend too)

**User — Results** (`/quiz/:id/results/:attemptId`, UserRoute):
- Score animates up with CountUp (0 → final %)
- Grade badge: "Excellent 🏆" / "Good 👍" / "Needs Practice 📚" by score range
- Animated circular progress ring (SVG or from UI.md)
- Q&A breakdown: ✅ green / ❌ red per question with explanation text revealed
- CTAs: "Retake Quiz" | "Browse More Quizzes" — NOT "Create Quiz"

**User — My Progress / Analytics** (`/analytics`, UserRoute):
- Line chart: score over last 20 attempts (Recharts)
- Radar chart: per-topic performance (Recharts)
- 🔥 Streak calendar heatmap (active days)
- Topic cards: strongest glows green, weakest glows amber (from UI.md or custom)
- Leaderboard tab: user's rank + top 10 users

---

**❓ STOP AND ASK THE USER:**
> "Frontend structure is done. I need two things:
> 1. What will your backend URL be on Railway? It will look like `https://your-app-name.up.railway.app` — if you haven't deployed yet, type 'not deployed yet' and I'll set it as an env variable placeholder.
> 2. Do you want the frontend deployed on Vercel? If yes, do you have a Vercel account connected to GitHub?"

---

### ═══════════════════════════════════════
### PHASE 7: RAILWAY DEPLOYMENT
### ═══════════════════════════════════════

**INSTRUCTIONS TO GIVE THE USER:**

"Here is exactly how to deploy to Railway:

**Step 1 — Create Railway Project**
1. Go to railway.app → New Project → Deploy from GitHub repo
2. Select your repository
3. Railway will auto-detect Python/Django

**Step 2 — Add Redis Service**
1. In your Railway project dashboard, click '+ New'
2. Select 'Redis' from the database options
3. Click on the Redis service → Variables tab
4. Copy the `REDIS_URL` value

**Step 3 — Add PostgreSQL (Supabase)**
You're using Supabase for Postgres, so no Railway Postgres needed.

**Step 4 — Set Environment Variables on Railway**
Click your Django service → Variables tab → Add all these:

```
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=[generate a random 50-char string]
DATABASE_URL=[your Supabase pgbouncer URL]
REDIS_URL=[from Railway Redis service]
GEMINI_API_KEY=AIzaSyDLuZ2_XGS0XJjEMDhWYlnQZJdUe7bnGrMl
ALLOWED_HOSTS=.railway.app,.up.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
DEBUG=False
```

**Step 5 — Add Celery Worker Service**
1. In Railway, click '+ New' → 'Empty Service'
2. Connect to same GitHub repo
3. Set start command: `cd backend && celery -A config worker -l info`
4. Set same environment variables as main service

**Step 6 — Run Migrations**
In Railway, click your Django service → 'New Deployment' → open shell:
```bash
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --no-input
```

**Step 7 — Get your Railway URL**
Click your Django service → Settings → copy the generated domain
It will look like: `https://quiz-app-production.up.railway.app`

Please share this URL so I can update the frontend `.env` and finalize deployment."

---

### ═══════════════════════════════════════
### PHASE 8: FINAL POLISH & README
### ═══════════════════════════════════════

**WHAT TO BUILD:**

**Final Polish**:
1. **Leaderboard**: Use Redis sorted sets (ZADD on attempt complete, ZREVRANK for user rank) — O(log n) reads
2. **Partial Quiz Loading**: Serve questions one at a time via `/api/v1/attempts/{id}/next-question/` instead of full payload upfront
3. **Idempotency**: Already handled in Phase 4 — verify duplicate generation check and duplicate attempt check are both working
4. **AI Cost Control**: Token usage logged per generation. Daily limit = 10 per admin. Add cost estimate to quiz creation response: `{"estimated_tokens": 1200, "generations_remaining_today": 8}`
5. **Analytics denormalization**: After every attempt completion, run both `UserStat.refresh_for_user(user)` AND `QuizStat.refresh_for_quiz(quiz)` in a Celery task (not blocking the HTTP response)

**API Documentation**:
- All views decorated with `@extend_schema` (drf-spectacular)
- Swagger UI accessible at `/api/v1/docs/`
- ReDoc at `/api/v1/redoc/`

**README.md** (professional, interview-ready):
```markdown
# AI-Powered Quiz API

## Tech Stack
## Role Architecture
  - Admin: quiz creator, cannot attempt
  - User: learner, cannot create
  - How roles are enforced (permission class level, not view logic)
## Architecture Decisions
  - Why UUID PKs (distributed-safe, no enumeration attacks)
  - Why Celery for AI generation (non-blocking UX)
  - Why Redis for both cache and task queue
  - Why Supabase pgbouncer (connection pooling for serverless)
  - Why denormalized analytics tables (read performance)
  - Why Redis sorted sets for leaderboard
## Database Schema (with diagram link)
## API Endpoint Reference (full table with role access column)
## Local Setup Instructions
## Environment Variables Reference
## Design Trade-offs
  - Polling vs WebSockets for generation status
  - Celery vs Django Background Tasks
  - SimpleJWT vs Djoser
  - Partial question loading vs full payload
## How AI Integration Works
## Performance Considerations
## Scaling Strategy
```

**Final checklist before interview**:
- [ ] All endpoints return consistent JSON format `{success, data, message}`
- [ ] Error responses all return `{success: false, error: {code, message, details}}`
- [ ] All list endpoints paginated
- [ ] `POST /api/v1/quizzes/` returns 403 with clear message when a `user` role calls it
- [ ] ALL attempt endpoints return 403 with clear message when an `admin` role calls them
- [ ] Registration always assigns `role='user'` — even if client sends `role=admin` in body
- [ ] `role` field cannot be changed via `/auth/me/` — only via `/api/v1/admin/users/{id}/`
- [ ] Admin dashboard has ZERO attempt/progress UI
- [ ] User dashboard has ZERO quiz-creation UI
- [ ] `AdminRoute` and `UserRoute` guards prevent wrong-role access on frontend
- [ ] After login, `role` stored in Zustand + persisted to localStorage
- [ ] All UI.md components are installed and used across the app
- [ ] Gemini API key in env var (NOT hardcoded)
- [ ] Supabase URL in env var (NOT hardcoded)
- [ ] Redis caching on quiz list, leaderboard (sorted set), user stats
- [ ] Celery worker running separately on Railway
- [ ] Swagger docs accessible at /api/v1/docs/
- [ ] Health check endpoint returns 200
- [ ] Frontend deployed on Vercel with correct API URL
- [ ] JWT refresh flow working in frontend

---

## 🎤 INTERVIEW PREP ANSWERS

Be ready to explain these:

**Q: Why are admin and user roles completely separated — why can't admins attempt quizzes?**
A: Clean separation of concerns. Admins are content creators, users are learners. Mixing roles would pollute analytics (admin test attempts skewing community scores), complicate the permission model, and blur the product's purpose. Every `Attempt` record in the DB is guaranteed to belong to a `role='user'` — making all analytics and leaderboard data pure and meaningful.

**Q: How do you prevent a user from self-promoting to admin?**
A: Three layers of defense: (1) `UserRegistrationSerializer` does not include `role` as a writable field — it's hardcoded to `'user'` in `create()` and logs a warning if `role` was in the request. (2) `MeView` serializer has `role` as `read_only=True`. (3) The only role-change endpoint is `PATCH /api/v1/admin/users/{id}/` protected by `IsAdminRole` — so only an existing admin can promote.

**Q: Why UUID instead of integer PKs?**
A: UUIDs are globally unique, safe to expose in URLs (no sequential enumeration attacks), and work well in distributed systems if we ever shard the database.

**Q: Why Celery for AI generation?**
A: AI API calls take 3-10 seconds. Blocking the HTTP request would timeout and ruin UX. Celery lets us return immediately with `status: "generating"` and let the admin frontend poll asynchronously. It also enables retries with backoff without holding server threads.

**Q: How do you handle AI failures?**
A: Three-layer strategy: (1) Celery task retries with exponential backoff (3 attempts, 1s/2s/4s). (2) JSON structure validation before any DB writes. (3) Quiz marked `status: "failed"` with error stored — admin can trigger regeneration via `/regenerate/` endpoint.

**Q: How does scoring work?**
A: When `attempt.complete()` is called, we aggregate all `AttemptAnswer` records for that attempt, sum `points` for `is_correct=True` answers, divide by total possible points, multiply by 100. Done entirely via Django ORM `annotate()` + `aggregate()` — no Python loops. Then `UserStat.refresh_for_user()` and `QuizStat.refresh_for_quiz()` run in a background Celery task to update denormalized analytics.

**Q: How would you scale this?**
A: (1) Read replicas for analytics queries, (2) CDN for static assets, (3) Increase Celery workers for AI generation bursts, (4) Redis cluster for cache + leaderboard sorted sets, (5) Rate limit per admin tier, (6) Extract AI generation into a dedicated microservice if volume grows, (7) WebSockets to replace polling for quiz generation status.

---

*End of Master Build Prompt*
*Estimated build time: 6-10 hours of focused AI-assisted coding*
*Result: Production-grade, interview-winning full-stack quiz application*