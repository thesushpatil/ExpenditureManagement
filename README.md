<div align="center">

# ExpManage - Smart Personal Finance Manager

![Django](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![DRF](https://img.shields.io/badge/DRF-3.15-red?style=for-the-badge&logo=django&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

A full-stack expense management application with a decoupled architecture featuring a Django REST API backend and a plain HTML/CSS/JavaScript frontend. Track expenses, manage budgets, monitor income, and grow savings with beautiful data visualizations.

[Features](#features) | [Architecture](#architecture) | [Tech Stack](#tech-stack) | [Getting Started](#getting-started) | [API Reference](#api-reference) | [Database Design](#database-design)

</div>

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [System Design](#system-design)
- [Tech Stack & Why](#tech-stack--why)
- [Database Design](#database-design)
- [API Design](#api-design)
- [Security](#security)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Project Flow](#project-flow)
- [Benefits](#benefits)
- [Future Scope](#future-scope)

---

## Features

### Backend (Django REST API)
- **JWT Authentication** - Secure token-based auth (register, login, refresh, logout)
- **RESTful API** - Full CRUD for Income, Expenses, Savings, Budgets with proper HTTP methods
- **Consistent Error Handling** - Every error returns a structured JSON response with error codes
- **Budget Validation** - Automatically warns when expenses exceed budget limits
- **Dashboard Endpoint** - Single API call returns all summary data (totals, charts, recent activity)
- **API Documentation** - Auto-generated Swagger UI at `/api/docs/`
- **Rate Limiting** - Built-in throttling to prevent abuse
- **Pagination, Filtering, Search** - All list endpoints support query params
- **Seeded Categories** - 12 default expense categories with colors and icons

### Frontend (Plain HTML/CSS/JavaScript)
- **Modern UI** - Glass-morphism cards, gradient accents, smooth animations
- **Responsive** - Works on mobile, tablet, and desktop
- **Dashboard** - Bar charts, budget progress bars, recent transactions
- **Protected Routes** - Auto-redirects to login if not authenticated
- **Token Refresh** - Fetch interceptor automatically refreshes expired tokens
- **Toast Notifications** - User-friendly success/error messages
- **Dark Gradient Landing Page** - Stunning first impression
- **Zero Build Step** - Just open index.html or serve with any static server

---

## Architecture

```
+--------------------------------------------------+
|                   CLIENT (Browser)                |
+--------------------------------------------------+
                        |
                        | HTTP/HTTPS
                        v
+--------------------------------------------------+
|       FRONTEND (Plain HTML + CSS + JavaScript)   |
|                                                  |
|  +----------+  +----------+  +--------------+   |
|  |  Pages   |  |  app.js  |  |   api.js     |   |
|  | (HTML)   |  |  (Logic) |  | (Fetch+JWT)  |   |
|  +----------+  +----------+  +--------------+   |
|                                                  |
|  Served by: Live Server / Nginx / Any host       |
+--------------------------------------------------+
                        |
                        | REST API Calls (JSON)
                        | Authorization: Bearer <token>
                        v
+--------------------------------------------------+
|           BACKEND (Django REST Framework)         |
|                                                  |
|  +------------+  +-------------+  +----------+  |
|  |   Auth     |  |  Expenses   |  |   Core   |  |
|  | (SimpleJWT)|  | (ViewSets)  |  | (Errors) |  |
|  +------------+  +-------------+  +----------+  |
|                                                  |
|  +------------+  +-------------+  +----------+  |
|  |   CORS     |  |  Filtering  |  | Throttle |  |
|  | (Headers)  |  | (DjangoFilt)|  | (Rate)   |  |
|  +------------+  +-------------+  +----------+  |
|                                                  |
|  Port: 8000                                      |
+--------------------------------------------------+
                        |
                        | ORM Queries
                        v
+--------------------------------------------------+
|              DATABASE (SQLite / PostgreSQL)       |
|                                                  |
|  Users | Income | Expenses | Savings | Budgets   |
|  ExpenseCategories | Token Blacklist             |
+--------------------------------------------------+
```

### Request Flow

```
User Action (Click/Submit)
    |
    v
app.js (Event Handler) --> api.js (API Function)
    |
    v
fetch() with JWT token from localStorage
    |-- Attaches Authorization: Bearer <token>
    |-- Handles 401 with automatic token refresh
    |
    v
Django REST Framework
    |-- CORS Middleware (validates origin)
    |-- JWT Authentication (validates token)
    |-- Permission Check (IsAuthenticated + IsOwner)
    |-- Throttle Check (rate limiting)
    |-- View Logic (business rules)
    |-- Serializer (validation + transformation)
    |
    v
Database Query (Django ORM)
    |
    v
JSON Response --> fetch() --> app.js --> DOM Update
```

---

## System Design

### Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Separation of Concerns** | Frontend and Backend are completely independent projects |
| **Stateless API** | JWT tokens - no server-side sessions needed |
| **Single Responsibility** | Each app handles one domain (accounts, expenses) |
| **DRY (Don't Repeat Yourself)** | Shared permissions, exception handler, base serializers |
| **Fail Fast** | Validation at serializer level before hitting the database |
| **Consistent Responses** | All endpoints return `{success, data/error}` format |

### Data Flow Diagram

```
[User Registration]
    |
    v
[Login] --> [JWT Access + Refresh Tokens]
    |
    v
[Dashboard] <-- GET /api/v1/dashboard/
    |           Returns: income, expenses, savings, balance,
    |                    budget progress, category breakdown
    |
    +---> [Add Income] --> POST /api/v1/incomes/
    |
    +---> [Add Expense] --> POST /api/v1/expenses/
    |         |-- Validates against budget limits
    |         |-- Returns warning if over budget
    |
    +---> [Set Budget] --> POST /api/v1/budgets/
    |         |-- Unique per user + category + month
    |         |-- Returns spent/remaining/percentage
    |
    +---> [Add Saving] --> POST /api/v1/savings/
    |
    +---> [Logout] --> POST /api/v1/auth/logout/
              |-- Blacklists refresh token
```

---

## Tech Stack & Why

### Backend

| Technology | Version | Why |
|-----------|---------|-----|
| **Python** | 3.11+ | Mature ecosystem, excellent for rapid API development |
| **Django** | 5.1 | Battle-tested web framework with built-in ORM, admin, auth |
| **Django REST Framework** | 3.15 | Industry standard for building REST APIs in Django |
| **SimpleJWT** | 5.4 | Stateless JWT auth - perfect for SPA frontends, no sessions |
| **django-cors-headers** | 4.6 | Handles CORS for cross-origin requests from React |
| **django-filter** | 24.3 | Declarative filtering on querysets via URL params |
| **drf-spectacular** | 0.28 | Auto-generates OpenAPI 3.0 schema + Swagger UI docs |
| **python-decouple** | 3.8 | Environment variable management (12-factor app) |
| **WhiteNoise** | 6.8 | Serves static files efficiently without nginx in production |
| **SQLite** | (built-in) | Zero-config for development; swap to PostgreSQL for production |

### Frontend

| Technology | Version | Why |
|-----------|---------|-----|
| **HTML5** | - | Semantic markup, accessible, works everywhere |
| **CSS3** | - | Custom properties, flexbox, grid - no framework needed |
| **JavaScript (ES6+)** | - | Async/await, fetch API, no build step required |
| **Font Awesome** | 6.5 | Beautiful icon set via CDN |
| **Google Fonts (Inter)** | - | Clean, modern typography |

---

## Database Design

### Entity Relationship Diagram

```
+------------------+       +--------------------+
|      User        |       | ExpenseCategory    |
|------------------|       |--------------------|
| id (PK)         |       | id (PK)            |
| username         |       | name (unique)      |
| email            |       | icon               |
| first_name       |       | color              |
| last_name        |       | created_at         |
| password (hash)  |       +--------------------+
| date_joined      |              |
+------------------+              |
    |   |   |   |                 |
    |   |   |   |                 |
    v   v   v   v                 v
+--------+ +--------+ +--------+ +--------+
| Income | |Expense | | Saving | | Budget |
|--------| |--------| |--------| |--------|
| id(PK) | | id(PK) | | id(PK) | | id(PK) |
| user(FK)| | user(FK)| | user(FK)| | user(FK)|
| amount  | | amount  | | amount  | | cat(FK) |
| source  | | cat(FK) | | goal    | | limit   |
| date    | | date    | | date    | | month   |
| desc    | | desc    | | desc    | | year    |
| created | | created | | created | | created |
| updated | | updated | | updated | | updated |
+--------+ +--------+ +--------+ +--------+
```

### Model Details

| Model | Key Fields | Constraints |
|-------|-----------|-------------|
| **User** | username, email, password | Built-in Django User model |
| **ExpenseCategory** | name, icon, color | `name` is unique |
| **Income** | user, amount, source, date | `amount > 0` (MinValueValidator) |
| **Expense** | user, amount, category, date | `amount > 0`, FK to Category (PROTECT) |
| **Saving** | user, amount, goal, date | `amount > 0` |
| **Budget** | user, category, limit, month, year | `unique_together(user, category, month, year)` |

### Design Decisions

- **`on_delete=PROTECT`** on Expense.category prevents accidental deletion of categories with existing expenses
- **`MinValueValidator(0.01)`** ensures no zero or negative amounts at the database level
- **`unique_together`** on Budget prevents duplicate budgets for the same category/month
- **Separate `date` field** (not auto_now_add) allows users to backdate entries
- **`created_at` / `updated_at`** timestamps for audit trail

---

## API Design

### Design Principles

1. **RESTful conventions** - Resources as nouns, HTTP verbs for actions
2. **Versioned** - All endpoints under `/api/v1/` for future compatibility
3. **Consistent response format** - Every response follows the same structure
4. **Pagination by default** - 20 items per page, prevents large payloads
5. **Filterable & Searchable** - Query params for all list endpoints

### Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": {
      "field_name": ["Specific error for this field"]
    }
  }
}
```

**Paginated Response:**
```json
{
  "count": 45,
  "next": "http://api/v1/expenses/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

### Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `BAD_REQUEST` | 400 | Invalid input data |
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Not allowed to access this resource |
| `NOT_FOUND` | 404 | Resource does not exist |
| `CONFLICT` | 409 | Duplicate resource |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_SERVER_ERROR` | 500 | Server error |

---

## Security

| Layer | Implementation |
|-------|---------------|
| **Authentication** | JWT (JSON Web Tokens) with access + refresh token pattern |
| **Token Expiry** | Access: 60 min, Refresh: 7 days with rotation |
| **Token Blacklisting** | Refresh tokens are blacklisted on logout |
| **Password Hashing** | Django's PBKDF2 with SHA256 (industry standard) |
| **Password Validation** | Min length, common password check, numeric-only check |
| **CORS** | Only whitelisted origins can make API requests |
| **Rate Limiting** | 30 req/min (anonymous), 100 req/min (authenticated) |
| **Object-Level Permissions** | Users can only access their own data (IsOwner) |
| **Input Validation** | Serializer-level validation before database operations |
| **CSRF Protection** | Enabled by default (not needed for JWT but active) |
| **SQL Injection** | Prevented by Django ORM (parameterized queries) |
| **XSS Protection** | React escapes output by default; Django middleware headers |
| **Clickjacking** | X-Frame-Options middleware enabled |
| **Environment Variables** | Secrets stored in `.env`, never committed to git |
| **HTTPS Ready** | WhiteNoise + security middleware for production |

### Authentication Flow

```
1. Register/Login
   POST /auth/login/ {username, password}
   Response: {access: "eyJ...", refresh: "eyJ..."}

2. Authenticated Request
   GET /expenses/
   Header: Authorization: Bearer eyJ...(access_token)

3. Token Expired (401)
   POST /auth/login/refresh/ {refresh: "eyJ..."}
   Response: {access: "new_eyJ..."}
   (Axios interceptor handles this automatically)

4. Logout
   POST /auth/logout/ {refresh: "eyJ..."}
   (Blacklists the refresh token)
```

---

## Project Structure

```
ExpManage/
|
+-- backend/                          # Django REST API Server
|   +-- config/                       # Project configuration
|   |   +-- settings.py               # Django settings (DB, JWT, CORS, DRF)
|   |   +-- urls.py                   # Root URL routing
|   |   +-- wsgi.py                   # WSGI entry point (production)
|   |   +-- asgi.py                   # ASGI entry point (async)
|   |
|   +-- apps/
|   |   +-- core/                     # Shared utilities
|   |   |   +-- exceptions.py         # Custom exception handler
|   |   |   +-- permissions.py        # IsOwner permission class
|   |   |
|   |   +-- accounts/                 # Authentication & user management
|   |   |   +-- views.py              # Register, Profile, ChangePassword, Logout
|   |   |   +-- serializers.py        # User serializers with validation
|   |   |   +-- urls.py               # Auth URL patterns
|   |   |
|   |   +-- expenses/                 # Core business logic
|   |       +-- models.py             # Income, Expense, Saving, Budget, Category
|   |       +-- serializers.py        # Data validation + budget checking
|   |       +-- views.py              # ViewSets + Dashboard
|   |       +-- urls.py               # Router-based URL patterns
|   |       +-- admin.py              # Django admin configuration
|   |       +-- management/commands/  # seed_categories command
|   |
|   +-- manage.py                     # Django CLI
|   +-- requirements.txt              # Python dependencies
|   +-- .env                          # Environment variables (not in git)
|   +-- .env.example                  # Template for environment setup
|
+-- frontend/                         # Plain HTML/CSS/JS Client
|   +-- index.html                    # Single-page app (all pages in one file)
|   +-- css/
|   |   +-- style.css                 # All styles (responsive, animations)
|   +-- js/
|   |   +-- api.js                    # API layer (fetch + JWT token management)
|   |   +-- app.js                    # App logic (UI, events, rendering)
|
+-- README.md                         # This file
```

---

## Getting Started

### Prerequisites

- **Python 3.11+** installed
- **Node.js 18+** and npm installed
- **Git** installed

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/expense-management.git
cd expense-management
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
# Edit .env file with your settings (or use defaults for development)

# Run database migrations
python manage.py makemigrations accounts expenses
python manage.py migrate

# Seed default expense categories (12 categories)
python manage.py seed_categories

# Create admin user (optional - for Django admin panel)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The API is now running at `http://127.0.0.1:8000`

### 3. Frontend Setup

```bash
# No build step needed! Just serve the files.

# Option 1: VS Code Live Server extension (recommended for development)
# Right-click index.html -> "Open with Live Server"

# Option 2: Python simple server
cd frontend
python -m http.server 5500

# Option 3: Node.js serve
npx serve frontend
```

The frontend is now running at `http://localhost:5500` (or whichever port your server uses)

### 4. Access the Application

| URL | Description |
|-----|-------------|
| `http://localhost:5500` | Frontend application |
| `http://127.0.0.1:8000/api/docs/` | Swagger API documentation |
| `http://127.0.0.1:8000/admin/` | Django admin panel |

### 5. First Use

1. Open `http://localhost:5500` (or open `frontend/index.html` directly)
2. Click "Get Started" or "Create Account"
3. Register with username, email, and password
4. You'll be automatically logged in and redirected to the Dashboard
5. Start adding income, expenses, savings, and budgets

---

## API Reference

### Base URL
```
http://127.0.0.1:8000/api/v1
```

### Authentication Endpoints

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register/` | `{username, email, first_name, password, password_confirm}` | Register new user, returns JWT tokens |
| `POST` | `/auth/login/` | `{username, password}` | Login, returns access + refresh tokens |
| `POST` | `/auth/login/refresh/` | `{refresh}` | Get new access token |
| `GET` | `/auth/profile/` | - | Get current user profile |
| `PATCH` | `/auth/profile/` | `{first_name?, last_name?, email?}` | Update profile |
| `POST` | `/auth/change-password/` | `{old_password, new_password}` | Change password |
| `POST` | `/auth/logout/` | `{refresh}` | Blacklist refresh token |

### Dashboard

| Method | Endpoint | Query Params | Description |
|--------|----------|--------------|-------------|
| `GET` | `/dashboard/` | `?month=5&year=2025` | Monthly financial summary with charts data |

### Income Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/incomes/` | List incomes (paginated, filterable) |
| `POST` | `/incomes/` | Create income `{amount, source, date, description}` |
| `GET` | `/incomes/{id}/` | Get single income |
| `PUT` | `/incomes/{id}/` | Update income |
| `DELETE` | `/incomes/{id}/` | Delete income |
| `GET` | `/incomes/summary/` | Current month total income |

### Expense Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/expenses/` | List expenses (paginated, filterable) |
| `POST` | `/expenses/` | Create expense `{amount, category, date, description}` |
| `GET` | `/expenses/{id}/` | Get single expense |
| `PUT` | `/expenses/{id}/` | Update expense |
| `DELETE` | `/expenses/{id}/` | Delete expense |
| `GET` | `/expenses/summary/` | Current month total expenses |
| `GET` | `/expenses/by-category/` | Expenses grouped by category |

**Query Parameters:** `?month=5&year=2025&category=1&start_date=2025-05-01&end_date=2025-05-31&search=food&ordering=-amount`

### Savings Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/savings/` | List savings (paginated) |
| `POST` | `/savings/` | Create saving `{amount, goal, date, description}` |
| `GET` | `/savings/{id}/` | Get single saving |
| `PUT` | `/savings/{id}/` | Update saving |
| `DELETE` | `/savings/{id}/` | Delete saving |
| `GET` | `/savings/summary/` | Total + monthly savings |

### Budget Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/budgets/` | List budgets (filterable by month/year) |
| `POST` | `/budgets/` | Create budget `{category, limit, month, year}` |
| `GET` | `/budgets/{id}/` | Get budget with spent/remaining/percentage |
| `PUT` | `/budgets/{id}/` | Update budget |
| `DELETE` | `/budgets/{id}/` | Delete budget |

### Category Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/categories/` | List all expense categories |
| `POST` | `/categories/` | Create category (admin only) |

---

## Project Flow

### User Journey

```
1. LANDING PAGE
   User visits the app --> Sees features & CTA

2. REGISTRATION
   User creates account --> Backend validates & creates user
   --> Returns JWT tokens --> Frontend stores in localStorage

3. DASHBOARD (Home)
   Frontend calls GET /dashboard/ --> Backend aggregates:
   - Total income this month
   - Total expenses this month
   - Total savings this month
   - Balance (income - expenses - savings)
   - Expenses by category (for pie chart)
   - Budget progress (for progress bars)
   - Recent 5 expenses

4. EXPENSE TRACKING
   User adds expense --> POST /expenses/
   Backend checks:
   - Amount > 0? (validator)
   - Category exists? (FK check)
   - Exceeds budget? (business logic warning)
   --> Saves to DB --> Returns created expense

5. BUDGET MANAGEMENT
   User sets budget --> POST /budgets/
   Backend checks:
   - No duplicate for same category/month? (unique_together)
   - Limit > 0? (validator)
   --> On GET, calculates spent/remaining/percentage dynamically

6. INCOME & SAVINGS
   Similar CRUD flow with validation

7. LOGOUT
   Frontend sends refresh token --> Backend blacklists it
   --> Frontend clears localStorage --> Redirects to login
```

### Frontend Component Flow

```
index.html (Single Page - all views in one file)
  |
  |-- Landing Page (visible by default)
  |-- Login Page (shown via showPage())
  |-- Register Page (shown via showPage())
  |-- App Page (shown after login)
        |-- Sidebar Navigation
        |-- Dashboard Section (default)
        |-- Expenses Section
        |-- Income Section
        |-- Savings Section
        |-- Budgets Section

js/api.js
  |-- Token management (localStorage)
  |-- apiRequest() - core fetch wrapper with JWT
  |-- refreshAccessToken() - auto refresh on 401
  |-- All API functions (apiLogin, apiGetExpenses, etc.)

js/app.js
  |-- Page navigation (showPage, switchSection)
  |-- Event handlers (handleLogin, handleAddExpense, etc.)
  |-- Data rendering (loadDashboard, loadExpenses, etc.)
  |-- UI utilities (showToast, toggleForm, formatCurrency)
```

---

## Benefits

### For Users
- **Complete financial picture** in one dashboard
- **Budget alerts** prevent overspending before it happens
- **Category-based tracking** shows exactly where money goes
- **Historical data** with filtering by date, month, category
- **Fast and responsive** - no page reloads, instant feedback
- **No installation** - works in any browser, no npm/node needed

### For Developers
- **Clean separation** - Frontend and backend can be developed/deployed independently
- **Type-safe API** - Serializers validate all input/output
- **Auto-generated docs** - Swagger UI always in sync with code
- **Easy to extend** - Add new models/endpoints following existing patterns
- **Production-ready** - Rate limiting, CORS, error handling, security headers
- **Simple frontend** - Plain HTML/CSS/JS, easy to understand and modify

### Technical Benefits
- **Stateless backend** - Horizontally scalable (add more servers)
- **Token-based auth** - Works with mobile apps, other clients
- **Optimized queries** - `select_related` prevents N+1 queries
- **Zero build step** - Frontend deploys as-is to any static host
- **No node_modules** - Frontend has zero dependencies to install

---

## Future Scope

| Feature | Description |
|---------|-------------|
| **Recurring Transactions** | Auto-create monthly expenses (rent, subscriptions) |
| **Export to PDF/CSV** | Download expense reports for any date range |
| **Multi-Currency** | Support for different currencies with conversion |
| **Notifications** | Email/push alerts when approaching budget limits |
| **Analytics** | Monthly/yearly trends, spending predictions |
| **Dark Mode** | Full dark theme toggle in the frontend |
| **Mobile App** | React Native app using the same API |
| **Shared Budgets** | Family/group expense tracking |
| **Receipt Upload** | OCR to auto-extract expense data from photos |
| **PostgreSQL** | Production database with better performance |
| **Docker** | Containerized deployment with docker-compose |
| **CI/CD** | GitHub Actions for automated testing and deployment |
| **WebSocket** | Real-time budget alerts when limits are reached |
| **2FA** | Two-factor authentication for enhanced security |

---

## Deployment Guide

### Backend Deployment (Railway / Render / VPS)

```bash
# 1. Set production environment variables
DEBUG=False
SECRET_KEY=your-strong-random-secret-key
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Run with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Frontend Deployment (Vercel / Netlify / GitHub Pages / Any Static Host)

```bash
# 1. Update API_BASE in js/api.js to your production backend URL:
#    const API_BASE = 'https://your-api-domain.com/api/v1';

# 2. Deploy the entire frontend/ folder as-is
#    - Vercel: vercel deploy ./frontend
#    - Netlify: drag & drop the frontend/ folder
#    - GitHub Pages: push frontend/ contents to gh-pages branch
#    - Any web server: just copy the files (index.html, css/, js/)
```

> **Note:** Since the frontend is plain HTML/CSS/JS with no build step, you can deploy it literally anywhere that serves static files.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with passion for better financial management**

</div>
