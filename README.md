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
5.  Create a `.env` file in `backend/` using the format in `.env.example`.
6.  Run migrations: `python manage.py migrate`
7.  Seed database: `python manage.py seed_data`
8.  Start Django: `python manage.py runserver`
9.  *(In a separate terminal)* Start Celery: `celery -A config worker -l info --pool=solo` (Windows)

### 2. Frontend Setup
1.  Navigate to the `frontend` directory.
2.  Install dependencies: `npm install`
3.  Create a `.env` file with: `VITE_API_URL=http://localhost:8000/api`
4.  Start Vite dev server: `npm run dev`

## 🌍 Deployment

*   **Backend:** Configured for Railway deployment via `railway.json` and `Procfile`. Set the required environment variables in your Railway project settings.
*   **Frontend:** Configured for Vercel deployment via `vercel.json` (resolves SPA routing issues). Set `VITE_API_URL` to your production backend URL.

## 👨‍💻 Authentication
To test the platform, you can register a new account or use the seeded admin credentials:
*   Email: `admin@quiz.com`
*   Password: `Admin@123`
