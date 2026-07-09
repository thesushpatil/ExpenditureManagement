# ExpManage - Smart Personal Finance Manager

## Interview Preparation Guide (STAR Approach)

> This document covers **every feature and technical decision** in the ExpManage project using the **STAR method** (Situation, Task, Action, Result) so you can confidently explain this project in interviews.

---

## Table of Contents

1. [Project Overview (STAR)](#1-project-overview-star)
2. [Architecture & System Design](#2-architecture--system-design)
3. [Tech Stack & Justification](#3-tech-stack--justification)
4. [Feature Breakdown (STAR for Each)](#4-feature-breakdown-star-for-each)
5. [Database Design](#5-database-design)
6. [API Design](#6-api-design)
7. [Security Implementation](#7-security-implementation)
8. [Frontend Architecture](#8-frontend-architecture)
9. [KhataBook Module (STAR)](#9-khatabook-module-star)
10. [AI Chatbot (STAR)](#10-ai-chatbot-star)
11. [PDF Export (STAR)](#11-pdf-export-star)
12. [Error Handling (STAR)](#12-error-handling-star)
13. [Deployment](#13-deployment)
14. [Project Structure](#14-project-structure)
15. [API Reference (Complete)](#15-api-reference-complete)
16. [Interview Questions & Answers](#16-interview-questions--answers)
17. [Future Scope](#17-future-scope)

---

## 1. Project Overview (STAR)

### Situation
Managing personal finances is a challenge for individuals who lack a centralized tool to track income, expenses, savings, and budgets. Existing apps are either too complex, paid, or don't offer features like lending/borrowing tracking (KhataBook) in one place.

### Task
Build a **full-stack personal finance management application** with:
- Expense tracking with category-wise analysis
- Income management
- Savings goal tracking
- Monthly budget limits with overspend alerts
- KhataBook-style lending/borrowing ledger with SMS/WhatsApp reminders
- AI-powered financial assistant chatbot
- PDF report export
- Beautiful, responsive UI with zero build step

### Action
- Designed a **decoupled architecture** (separate frontend + backend)
- Built a **Django REST Framework** backend with JWT authentication
- Created a **plain HTML/CSS/JavaScript** frontend (no React/Vue/Angular dependency)
- Implemented **Gemini AI** integration for the chatbot
- Added **KhataBook module** with contact management, ledger, and payment reminders
- Used **STAR principles**: Separation of Concerns, Token-based auth, API-first design, RESTful conventions

### Result
- A production-ready, scalable expense management system
- 7 modules: Dashboard, Income, Expenses, Savings, Budgets, KhataBook, AI Chatbot
- 25+ REST API endpoints with Swagger documentation
- Fully responsive UI that works on mobile, tablet, and desktop
- Zero npm dependencies on frontend (deploys as static files anywhere)

---

## 2. Architecture & System Design

### High-Level Architecture

```
+--------------------------------------------------+
|                   CLIENT (Browser)                |
+--------------------------------------------------+
                        |
                        | HTTP/HTTPS (REST)
                        v
+--------------------------------------------------+
|       FRONTEND (Plain HTML + CSS + JavaScript)   |
|                                                  |
|  +----------+  +----------+  +--------------+   |
|  |  Pages   |  |  app.js  |  |   api.js     |   |
|  | (HTML)   |  |  (Logic) |  | (Fetch+JWT)  |   |
|  +----------+  +----------+  +--------------+   |
|                                                  |
|  +----------+                                    |
|  |chatbot.js|  (Gemini AI Integration)           |
|  +----------+                                    |
|                                                  |
|  Served by: Any static host (Netlify/Vercel)     |
+--------------------------------------------------+
                        |
                        | REST API Calls (JSON)
                        | Authorization: Bearer <JWT>
                        v
+--------------------------------------------------+
|           BACKEND (Django REST Framework)         |
|                                                  |
|  +------------+  +-------------+  +----------+  |
|  |  Accounts  |  |  Expenses   |  |   Core   |  |
|  | (Auth/JWT) |  | (ViewSets)  |  | (Errors) |  |
|  +------------+  +-------------+  +----------+  |
|                                                  |
|  +------------+  +-------------+  +----------+  |
|  | KhataBook  |  |  Dashboard  |  | Budgets  |  |
|  | (Contacts/ |  | (Aggregate) |  | (Limits) |  |
|  |  Ledger)   |  |             |  |          |  |
|  +------------+  +-------------+  +----------+  |
|                                                  |
|  Middleware: CORS | WhiteNoise | Rate Limiting   |
|  Port: 8000                                      |
+--------------------------------------------------+
                        |
                        | Django ORM
                        v
+--------------------------------------------------+
|              DATABASE (SQLite / PostgreSQL)       |
|                                                  |
|  Users | Income | Expenses | Savings | Budgets   |
|  Categories | Contacts | LedgerEntries           |
|  Token Blacklist                                 |
+--------------------------------------------------+
```

### Request-Response Flow

```
User Action (Click/Submit)
    |
    v
app.js (Event Handler) --> api.js (apiRequest function)
    |
    v
fetch() with JWT from localStorage
    |-- Header: Authorization: Bearer <access_token>
    |-- Auto-handles 401 via refreshAccessToken()
    |
    v
Django REST Framework Pipeline:
    1. CORS Middleware (validates origin)
    2. JWT Authentication (validates/decodes token)
    3. Permission Check (IsAuthenticated + IsOwner)
    4. Throttle Check (30/min anon, 100/min auth)
    5. View Logic (ViewSet action)
    6. Serializer (input validation + transformation)
    7. Django ORM (database query)
    |
    v
JSON Response --> fetch() --> app.js --> DOM Update --> User sees result
```

### Design Principles

| Principle | How We Applied It |
|-----------|------------------|
| **Separation of Concerns** | Frontend and Backend are completely independent deployable units |
| **Stateless API** | JWT tokens; no server-side sessions; horizontally scalable |
| **Single Responsibility** | Each Django app handles one domain (accounts, expenses, core) |
| **DRY** | Shared IsOwner permission, custom_exception_handler, base patterns |
| **Fail Fast** | Serializer-level validation rejects bad data before DB layer |
| **Consistent Responses** | Every endpoint returns `{success: true/false, data/error}` |
| **API Versioning** | All endpoints under `/api/v1/` for backward compatibility |
| **Object-Level Security** | Users can ONLY access their own records (IsOwner permission) |

---

## 3. Tech Stack & Justification

### Backend

| Technology | Version | Why We Chose It |
|-----------|---------|-----------------|
| **Python** | 3.11+ | Mature ecosystem, rapid API development, readable syntax |
| **Django** | 5.1 | Battle-tested framework with built-in ORM, admin, auth, migrations |
| **Django REST Framework** | 3.15 | Industry standard for REST APIs in Django; ViewSets, Serializers, Routers |
| **SimpleJWT** | 5.4 | Stateless JWT auth, perfect for SPA frontends, supports token rotation & blacklisting |
| **django-cors-headers** | 4.6 | Handles cross-origin requests from frontend on different port/domain |
| **django-filter** | 24.3 | Declarative filtering on querysets via URL query parameters |
| **drf-spectacular** | 0.28 | Auto-generates OpenAPI 3.0 schema + Swagger UI documentation |
| **python-decouple** | 3.8 | Environment variable management following 12-factor app methodology |
| **WhiteNoise** | 6.8 | Serves static files efficiently in production without nginx |
| **SQLite** | built-in | Zero-config for development; easily swap to PostgreSQL for production |
| **Gunicorn** | 23.0 | Production-grade WSGI server for deploying Django |

### Frontend

| Technology | Why We Chose It |
|-----------|-----------------|
| **HTML5** | Semantic markup, accessible, universal browser support |
| **CSS3** (Custom Properties, Flexbox, Grid) | Modern layouts without CSS framework overhead |
| **JavaScript ES6+** | async/await, fetch API, modules; no build step required |
| **Font Awesome 6.5** | Beautiful icon set via CDN, no installation needed |
| **Google Fonts (Inter)** | Clean, modern typography for professional appearance |
| **Gemini AI API** | Google's latest AI model for intelligent financial assistant |
| **Marked.js** | Markdown rendering in chatbot responses |
| **Highlight.js** | Code syntax highlighting in AI responses |

### Why No React/Vue/Angular?
- **Zero build step** = instant deployment to any static host
- **No node_modules** = no dependency management headaches
- **Simpler debugging** = no virtual DOM, no state management libraries
- **Faster initial load** = no 200KB+ JS bundle to parse
- **Educational value** = demonstrates raw JavaScript skills in interviews

---

## 4. Feature Breakdown (STAR for Each)

### 4.1 JWT Authentication System

**Situation:** Need secure, stateless authentication for a decoupled SPA frontend calling a REST API.

**Task:** Implement token-based auth with register, login, refresh, logout, profile management, and password change.

**Action:**
- Used `djangorestframework-simplejwt` for JWT token generation
- Access token (60 min lifetime) + Refresh token (7 day lifetime) pattern
- Token rotation: every refresh generates new access AND refresh tokens
- Token blacklisting on logout (prevents replay attacks)
- Frontend stores tokens in `localStorage` and attaches `Authorization: Bearer` header
- Auto-refresh: `api.js` intercepts 401 responses, calls `/auth/login/refresh/`, retries original request
- Password validation: minimum length, common password check, numeric-only check

**Result:**
- Secure, stateless auth that works without server-side sessions
- Seamless UX: user never sees token expiry (auto-refresh handles it)
- Logout properly invalidates tokens (not just clearing localStorage)

---

### 4.2 Dashboard (Aggregated Financial Summary)

**Situation:** Users need a quick overview of their financial health at a glance.

**Task:** Create a single API endpoint that returns all summary data for the current month.

**Action:**
- `GET /api/v1/dashboard/?month=&year=` endpoint
- Aggregates using Django ORM `Sum()`:
  - Total income, total expenses, total savings, balance (income - expenses - savings)
- Category-wise expense breakdown (for bar chart visualization)
- Budget progress with spent/remaining/percentage (for progress bars)
- Recent 5 expenses (for quick activity feed)
- Used `select_related('category')` to prevent N+1 query problem

**Result:**
- Single API call returns everything the dashboard needs
- Frontend renders: stat cards, category bar chart, budget progress bars, recent expenses table
- Optimized DB queries (aggregates + select_related)

---

### 4.3 Expense Management

**Situation:** Core feature - users need to track every expense with categorization.

**Task:** Full CRUD with category filtering, date range filtering, search, budget validation.

**Action:**
- `ExpenseViewSet` with ModelViewSet (auto-generates list/create/retrieve/update/destroy)
- 12 seeded categories (Food, Transport, Shopping, Entertainment, Bills, Healthcare, etc.)
- Query parameters: `?category=1&month=5&year=2025&start_date=&end_date=&search=&ordering=-amount`
- **Budget validation in serializer**: when creating an expense, checks if it would exceed the budget limit for that category/month and raises `ValidationError`
- Custom actions: `/expenses/summary/` (monthly total), `/expenses/by-category/` (grouped aggregation)
- `on_delete=PROTECT` on category FK prevents deleting a category that has expenses

**Result:**
- Complete expense tracking with smart budget warnings
- Filterable, searchable, sortable list with pagination (20/page)
- Category-wise analytics for spending insights

---

### 4.4 Income Management

**Situation:** Users need to record income from various sources to calculate balance.

**Task:** CRUD for income with source tracking and monthly summaries.

**Action:**
- `IncomeViewSet` with fields: amount, source (Salary, Freelance, etc.), date, description
- Filter by date, source; order by date/amount
- Summary endpoint: `GET /incomes/summary/` returns current month total
- `MinValueValidator(0.01)` prevents zero/negative amounts

**Result:**
- Tracks multiple income streams per user
- Feeds into dashboard balance calculation (income - expenses - savings)

---

### 4.5 Savings Management

**Situation:** Users want to track savings towards specific goals.

**Task:** CRUD for savings with goal-based tracking and summary stats.

**Action:**
- `SavingViewSet` with fields: amount, goal (Emergency Fund, Vacation, etc.), date, description
- Summary endpoint: total lifetime savings + current month savings
- Filter by goal, date; order by date/amount

**Result:**
- Goal-based savings tracking
- Contributes to dashboard balance (income - expenses - savings = available)

---

### 4.6 Budget Management

**Situation:** Users overspend because they lack category-wise spending limits.

**Task:** Allow users to set monthly budgets per category and warn when approaching/exceeding limits.

**Action:**
- `BudgetViewSet` with fields: category (FK), limit amount, month, year
- `unique_together('user', 'category', 'month', 'year')` prevents duplicate budgets
- **Computed fields in serializer:**
  - `spent`: real-time query of expenses for that category/month
  - `remaining`: limit - spent
  - `percentage_used`: (spent / limit) * 100
- Dashboard shows progress bars with color coding:
  - Green: < 70% used
  - Yellow/Orange: 70-90% used
  - Red: > 90% used (overspent)
- Expense creation validates against budget limits

**Result:**
- Proactive overspend prevention
- Visual progress bars show budget health at a glance
- Business logic enforced at API level (not just frontend display)

---

## 5. Database Design

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
+------------------+              | (FK: PROTECT)
    |   |   |   |   |            |
    |   |   |   |   |            v
    v   v   v   v   v     +--------+
+--------+ +--------+ +--------+ +--------+ +----------+ +-------------+
| Income | |Expense | | Saving | | Budget | | Contact  | | LedgerEntry |
|--------| |--------| |--------| |--------| |----------| |-------------|
| id(PK) | | id(PK) | | id(PK) | | id(PK) | | id(PK)  | | id(PK)      |
| user(FK)| | user(FK)| | user(FK)| | user(FK)| | user(FK) | | user(FK)    |
| amount  | | amount  | | amount  | | cat(FK) | | name     | | contact(FK) |
| source  | | cat(FK) | | goal    | | limit   | | phone    | | amount      |
| date    | | date    | | date    | | month   | | notes    | | type(gave/  |
| desc    | | desc    | | desc    | | year    | | created  | |   got)      |
| created | | created | | created | | created | | updated  | | date        |
| updated | | updated | | updated | | updated | +----------+ | desc        |
+--------+ +--------+ +--------+ +--------+               | notify_sent |
                                                           | created     |
                                                           +-------------+
```

### Key Constraints & Design Decisions

| Decision | Reasoning |
|----------|-----------|
| `on_delete=PROTECT` on Expense.category | Prevents accidental deletion of categories that have associated expenses |
| `on_delete=CASCADE` on Contact.user | When user is deleted, all their contacts and entries are cleaned up |
| `on_delete=CASCADE` on LedgerEntry.contact | Deleting a contact removes all their transaction history |
| `MinValueValidator(0.01)` on all amounts | Enforces positive amounts at database level (not just frontend) |
| `unique_together('user', 'category', 'month', 'year')` on Budget | Prevents duplicate budgets, enforced at DB level |
| `unique_together('user', 'phone')` on Contact | Same user can't add duplicate contacts with same phone |
| Separate `date` field (not `auto_now_add`) | Allows users to backdate entries (e.g., logging yesterday's expense) |
| `created_at` (auto_now_add) + `updated_at` (auto_now) | Audit trail without manual management |
| `RegexValidator` on phone field | Validates phone format (7-15 digits, optional + prefix) |
| `transaction_type` as CharField with choices | Limits to 'gave'/'got' only; better than boolean for readability |
| `notify_sent` boolean on LedgerEntry | Tracks which entries have had reminders sent (avoid spam) |

### 12 Seeded Categories

| Category | Icon | Color |
|----------|------|-------|
| Food & Dining | utensils | #ef4444 (red) |
| Transportation | car | #f97316 (orange) |
| Shopping | shopping-bag | #eab308 (yellow) |
| Entertainment | film | #22c55e (green) |
| Bills & Utilities | file-text | #06b6d4 (cyan) |
| Healthcare | heart | #8b5cf6 (purple) |
| Education | book-open | #6366f1 (indigo) |
| Rent & Housing | home | #ec4899 (pink) |
| Groceries | shopping-cart | #14b8a6 (teal) |
| Personal Care | user | #f43f5e (rose) |
| Travel | plane | #0ea5e9 (sky) |
| Other | more-horizontal | #64748b (slate) |

---

## 6. API Design

### Design Principles
1. **RESTful conventions** - Resources as nouns (`/expenses/`, `/incomes/`), HTTP verbs for actions
2. **Versioned** - All under `/api/v1/` for future backward compatibility
3. **Consistent response envelope** - Every response follows `{success, data/error}`
4. **Paginated by default** - 20 items/page prevents large payloads
5. **Filterable & Searchable** - Query params on all list endpoints
6. **Router-based URLs** - DRF DefaultRouter auto-generates URL patterns from ViewSets

### Response Formats

**Success:**
```json
{
  "success": true,
  "data": { "id": 1, "amount": "500.00", ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": { "field_name": ["Specific error"] }
  }
}
```

**Paginated List:**
```json
{
  "count": 45,
  "next": "http://api/v1/expenses/?page=2",
  "previous": null,
  "results": [ { ... }, { ... } ]
}
```

### Error Code Mapping

| Code | HTTP Status | When It Happens |
|------|-------------|-----------------|
| `BAD_REQUEST` | 400 | Invalid input, validation errors |
| `UNAUTHORIZED` | 401 | Missing/expired/invalid JWT token |
| `FORBIDDEN` | 403 | Accessing another user's data (IsOwner fails) |
| `NOT_FOUND` | 404 | Resource doesn't exist or wrong ID |
| `METHOD_NOT_ALLOWED` | 405 | Wrong HTTP verb for endpoint |
| `CONFLICT` | 409 | Duplicate resource (e.g., budget already exists) |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests (30/min anon, 100/min auth) |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error |

---

## 7. Security Implementation

### STAR for Security

**Situation:** Financial data is highly sensitive; API must be protected from unauthorized access, data leaks, and abuse.

**Task:** Implement multi-layered security covering authentication, authorization, data isolation, and abuse prevention.

**Action & Results:**

| Layer | Implementation | How It Works |
|-------|---------------|--------------|
| **Authentication** | JWT (Access + Refresh token pattern) | Stateless; no server sessions; scalable |
| **Token Expiry** | Access: 60 min, Refresh: 7 days | Short-lived access limits damage window |
| **Token Rotation** | New refresh token on each refresh call | Old tokens auto-invalidated |
| **Token Blacklisting** | SimpleJWT token_blacklist app | Logout actually invalidates tokens |
| **Password Hashing** | Django PBKDF2 + SHA256 (260,000 iterations) | Industry standard; resistant to brute force |
| **Password Validation** | 4 validators (length, common, numeric, similarity) | Prevents weak passwords at registration |
| **CORS** | django-cors-headers with allowed origins | Only whitelisted frontends can call API |
| **Rate Limiting** | DRF throttling: 30/min anon, 100/min authenticated | Prevents brute force & abuse |
| **Object-Level Permissions** | Custom `IsOwner` permission class | User A cannot see/edit User B's data |
| **Data Isolation** | `get_queryset()` filters by `user=request.user` | Queryset-level isolation (no data leaks) |
| **Input Validation** | Serializer validators (amount > 0, required fields, etc.) | Bad data never reaches database |
| **SQL Injection** | Django ORM (parameterized queries) | All queries are parameterized by default |
| **XSS Prevention** | Proper Content-Type headers, textContent in JS | No raw HTML injection |
| **Clickjacking** | X-Frame-Options: DENY (via middleware + Netlify header) | Cannot be embedded in iframes |
| **Secret Management** | python-decouple reads from .env file | Keys never hardcoded or committed to git |
| **HTTPS Ready** | WhiteNoise + SecurityMiddleware | Production serves over HTTPS only |

### Authentication Flow (Detailed)

```
1. REGISTER
   POST /api/v1/auth/register/
   Body: {username, email, first_name, password, password_confirm}
   --> Validates all fields (email unique, passwords match, password strong)
   --> Creates user with hashed password
   --> Returns: {access_token, refresh_token, user_profile}
   --> Frontend saves both tokens to localStorage

2. LOGIN
   POST /api/v1/auth/login/
   Body: {username, password}
   --> SimpleJWT verifies credentials
   --> Returns: {access, refresh}
   --> Frontend saves tokens

3. AUTHENTICATED REQUEST
   GET /api/v1/expenses/
   Header: Authorization: Bearer <access_token>
   --> JWTAuthentication middleware decodes token
   --> Sets request.user from token payload
   --> IsOwner checks obj.user == request.user

4. TOKEN EXPIRED (401 Response)
   --> Frontend api.js intercepts 401
   --> Calls POST /api/v1/auth/login/refresh/ {refresh: <refresh_token>}
   --> Gets new access_token (+ new refresh due to rotation)
   --> Retries original failed request with new token
   --> User never notices the refresh happened

5. LOGOUT
   POST /api/v1/auth/logout/ {refresh: <refresh_token>}
   --> Blacklists the refresh token (can never be used again)
   --> Frontend clears localStorage
   --> Redirects to login page
```

---

## 8. Frontend Architecture

### STAR for Frontend

**Situation:** Need a responsive, modern UI for a financial app without heavy frameworks that would add complexity.

**Task:** Build a multi-page SPA-like experience with protected routes, auto-refresh tokens, and rich visualizations using only HTML/CSS/JS.

**Action:**
- **Multi-page approach**: Each feature is its own HTML file (dashboard.html, expenses.html, khatabook.html, etc.)
- **Shared JS files**: `api.js` (HTTP layer + JWT) and `app.js` (shared logic) loaded on every page
- **Auth guard**: `requireAuth()` called on page load; redirects to login if no token
- **CSS Glass-morphism**: Modern card design with backdrop filters, gradients, shadows
- **Responsive sidebar**: Collapsible on mobile with hamburger menu toggle
- **Toast notifications**: Non-blocking success/error messages
- **Currency formatting**: `Intl.NumberFormat` with Indian Rupee locale

**Result:**
- Zero build step, zero npm dependencies
- Pages load instantly (no JS framework parsing)
- Works on all screen sizes (mobile-first responsive)
- Professional UI with animations and smooth transitions

### File Responsibilities

| File | Responsibility |
|------|---------------|
| `api.js` | Token management (localStorage), `apiRequest()` wrapper with auto-refresh, all API functions |
| `app.js` | Auth guard, logout, toast notifications, currency formatting, dashboard/expense/income/savings/budget rendering, PDF export |
| `chatbot.js` | Gemini AI integration, chat UI management, markdown rendering |
| `style.css` | Global styles, layout (sidebar + main), responsive breakpoints, cards, forms, tables, animations |
| `chatbot.css` | Chat-specific styles (bubbles, input area, typing indicator) |

### Page Structure

```
frontend/
|-- index.html          (Landing page - public, with CTA to register/login)
|-- pages/
|   |-- login.html      (Login form)
|   |-- register.html   (Registration form)
|   |-- dashboard.html  (Financial summary with charts)
|   |-- income.html     (Income CRUD)
|   |-- expenses.html   (Expense CRUD with filters)
|   |-- savings.html    (Savings CRUD with summary)
|   |-- budgets.html    (Budget CRUD with progress bars)
|   |-- khatabook.html  (Contact + Ledger management)
|   |-- chatbot.html    (Gemini AI assistant)
|   |-- about.html      (Team + tech stack info)
```

### Key Frontend Patterns

1. **Token Auto-Refresh Pattern (api.js):**
```javascript
async function apiRequest(endpoint, options = {}) {
    // Attach JWT token
    headers['Authorization'] = `Bearer ${getAccessToken()}`;
    let response = await fetch(url, { ...options, headers });

    // If 401, try refresh
    if (response.status === 401 && getRefreshToken()) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            // Retry with new token
            headers['Authorization'] = `Bearer ${getAccessToken()}`;
            response = await fetch(url, { ...options, headers });
        } else {
            clearTokens();
            redirect to login;
        }
    }
    return response;
}
```

2. **Auth Guard Pattern:**
```javascript
function requireAuth() {
    if (!getAccessToken()) {
        window.location.href = 'login.html';
    }
}
// Called on every protected page load
```

3. **API Base URL Auto-Detection:**
```javascript
const API_BASE = window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:8000/api/v1'
    : 'https://expmanage-api.onrender.com/api/v1';
```

---

## 9. KhataBook Module (STAR)

### Situation
In India, people frequently lend and borrow money from friends, family, and colleagues. Tracking who owes whom is usually done on paper or in memory, leading to disputes. Apps like KhataBook solve this but are standalone. We wanted this integrated into our finance app.

### Task
Build a digital ledger system where users can:
- Add contacts (with phone numbers)
- Record "You Gave" and "You Got" transactions
- View balance per contact (who owes whom and how much)
- Send SMS/WhatsApp payment reminders
- View complete transaction history per contact

### Action

**Backend (Models):**
- `Contact` model: name, phone (validated with regex), notes, `unique_together(user, phone)`
- `LedgerEntry` model: contact (FK), amount, transaction_type (gave/got), date, description, notify_sent
- `ContactSerializer`: computed fields `balance`, `total_gave`, `total_got` via `SerializerMethodField`
- `LedgerEntrySerializer`: validates that contact belongs to current user

**Backend (Views):**
- `ContactViewSet`: Full CRUD with search by name/phone
- `LedgerEntryViewSet`: CRUD + two custom actions:
  - `GET /ledger/by-contact/?contact_id=X` - filter entries by contact
  - `POST /ledger/send-reminder/` - calculates balance, generates SMS/WhatsApp deep links

**Reminder System:**
```python
# Calculate balance
gave_total = entries.filter(type='gave').aggregate(Sum)
got_total = entries.filter(type='got').aggregate(Sum)
balance = gave - got  # positive = they owe you

# Generate message
message = f"Hi {contact.name}, you have a pending payment of Rs.{balance}..."

# Create deep links
sms_link = f"sms:{phone}?body={encoded_message}"
whatsapp_link = f"https://wa.me/{phone}?text={encoded_message}"

# Mark entries as notified
entries.filter(notify_sent=False).update(notify_sent=True)
```

**Frontend:**
- Contact cards with avatar (initials), balance display (color-coded: green=they owe you, red=you owe them)
- "You Gave" / "You Got" buttons on each contact card
- SMS and WhatsApp buttons appear only when contact owes money (balance > 0)
- Modal forms for adding contacts and transactions
- Expandable ledger detail panel showing full transaction history

### Result
- Complete KhataBook feature integrated within the expense management app
- Real-time balance calculation per contact
- One-click SMS/WhatsApp reminders (opens native messaging apps)
- Prevents duplicate contacts per user (phone uniqueness)
- Visual color coding: green (they owe), red (you owe), gray (settled)

### API Endpoints for KhataBook

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/contacts/` | List all contacts with computed balances |
| `POST` | `/contacts/` | Add contact `{name, phone, notes}` |
| `GET` | `/contacts/{id}/` | Contact detail |
| `PUT` | `/contacts/{id}/` | Update contact |
| `DELETE` | `/contacts/{id}/` | Delete contact + all entries (CASCADE) |
| `GET` | `/ledger/` | All ledger entries |
| `POST` | `/ledger/` | Create entry `{contact, amount, transaction_type, date, description}` |
| `DELETE` | `/ledger/{id}/` | Delete entry |
| `GET` | `/ledger/by-contact/?contact_id=X` | Entries for specific contact |
| `POST` | `/ledger/send-reminder/` | Generate SMS/WhatsApp reminder links |

---

## 10. AI Chatbot (STAR)

### Situation
Users often need guidance on financial management, budgeting strategies, or help navigating the app. Instead of a static FAQ page, we wanted an intelligent assistant.

### Task
Integrate an AI-powered chatbot that can:
- Answer financial management questions
- Guide users on how to use the app
- Provide budgeting and savings tips
- Maintain conversation context across messages

### Action

**AI Integration:**
- Used **Google Gemini 1.5 Flash** (latest model) via REST API
- System instruction defines the AI's persona: "intelligent, friendly financial assistant for ExpManage"
- Conversation history maintained in `chatMessages[]` array (sent with each request for context)
- Markdown rendering with `marked.js` for formatted AI responses
- Code highlighting with `highlight.js` for any code snippets in responses

**Frontend Implementation:**
- Dedicated chat page (`chatbot.html`) with full-screen chat UI
- Typing indicator (animated dots) while waiting for AI response
- Suggestion chips for common questions (quick start for new users)
- "New Chat" button to clear conversation history
- Auto-resize textarea input (grows with content)
- Enter to send, Shift+Enter for new line

**System Prompt:**
```
You are an intelligent, friendly financial assistant for ExpManage app. Help users with:
1. Quick expense/income logging guidance
2. Budget setting tips
3. Financial management strategies
4. App navigation help
Be concise, use emojis sparingly, and format responses with markdown.
```

### Result
- Intelligent AI assistant that understands financial context
- Maintains conversation memory (multi-turn dialogue)
- Beautiful chat UI with user/AI message bubbles
- Suggestion chips reduce friction for first-time users
- Markdown + syntax highlighting for rich, formatted responses

---

## 11. PDF Export (STAR)

### Situation
Users need expense reports for tax filing, reimbursement, or personal record keeping.

### Task
Allow users to export monthly expense reports as printable PDF documents.

### Action
- Frontend-only implementation (no server-side PDF generation needed)
- User selects a month from date picker
- Fetches all expenses for that month via API
- Generates a styled HTML document with:
  - Title: "Expense Report"
  - Subtitle: Month/Year
  - Table: Category, Description, Date, Amount
  - Total sum at bottom
  - Footer with generation date
- Opens in new browser tab with `window.print()` auto-triggered
- Print dialog allows saving as PDF (browser-native)

### Result
- No additional library needed (uses browser's built-in print-to-PDF)
- Professional-looking reports with proper formatting
- Works on all browsers without server-side PDF generation overhead
- Instant generation (no server round-trip for PDF creation)

---

## 12. Error Handling (STAR)

### Situation
APIs need consistent, predictable error responses for frontend to handle gracefully.

### Task
Create a centralized error handling system that converts all exceptions into a uniform response format.

### Action
- **Custom Exception Handler** (`apps/core/exceptions.py`):
  - Intercepts all DRF exceptions
  - Maps HTTP status codes to readable error codes
  - Wraps every error in: `{success: false, error: {code, message, details}}`
  - Handles Django `ValidationError` (not just DRF ones)
- **Serializer-level validation**: Field-specific errors with meaningful messages
- **Frontend handling**: `api.js` checks `response.ok`, displays error message via toast
- **Budget validation**: Custom validation in `ExpenseSerializer.validate()` checks budget limits

**Example error flow:**
```
User submits expense of ₹5000 for Food (budget limit: ₹3000, already spent: ₹2500)
  --> ExpenseSerializer.validate() catches it
  --> Raises ValidationError with specific message
  --> custom_exception_handler wraps it
  --> Response: {success: false, error: {code: "BAD_REQUEST", message: "...", details: {amount: ["This expense would exceed your budget..."]}}}
  --> Frontend shows toast with the error message
```

### Result
- Every API error is predictable and structured
- Frontend can display field-specific errors (e.g., show error under "amount" input)
- No raw 500 errors leak stack traces to users
- Easy debugging: error codes map directly to causes

---

## 13. Deployment

### Backend Deployment (Render)

The project includes `render.yaml`, `Procfile`, `build.sh`, and `runtime.txt` for Render deployment:

```bash
# Procfile
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT

# build.sh
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed_categories

# Production Environment Variables
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=expmanage-api.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend.netlify.app
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Frontend Deployment (Netlify)

```toml
# netlify.toml
[build]
  publish = "."

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
```

- Zero build step: Netlify serves static files directly
- Security headers configured via `netlify.toml`
- `api.js` auto-detects production URL via `window.location.hostname`

### Local Development Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd Exp_Management

# 2. Backend setup
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
# Create .env file (copy from .env.example)
python manage.py migrate
python manage.py seed_categories
python manage.py runserver     # Runs on http://127.0.0.1:8000

# 3. Frontend setup (separate terminal)
cd frontend
python -m http.server 5173     # Or use VS Code Live Server
# Opens on http://127.0.0.1:5173

# 4. Access
# Frontend: http://127.0.0.1:5173
# API Docs: http://127.0.0.1:8000/api/docs/
# Admin: http://127.0.0.1:8000/admin/
```

---

## 14. Project Structure

```
ExpManage/
|
+-- backend/                          # Django REST API Server
|   +-- config/                       # Project configuration
|   |   +-- settings.py               # Django settings (DB, JWT, CORS, DRF, Throttling)
|   |   +-- urls.py                   # Root URL routing (/api/v1/, /admin/, /api/docs/)
|   |   +-- wsgi.py                   # WSGI entry point (Gunicorn in production)
|   |   +-- asgi.py                   # ASGI entry point (async support)
|   |
|   +-- apps/
|   |   +-- core/                     # Shared utilities
|   |   |   +-- exceptions.py         # Custom exception handler (consistent error format)
|   |   |   +-- permissions.py        # IsOwner permission (object-level access control)
|   |   |
|   |   +-- accounts/                 # Authentication & user management
|   |   |   +-- views.py              # Register, Profile, ChangePassword, Logout
|   |   |   +-- serializers.py        # User validation (unique email, password strength)
|   |   |   +-- urls.py               # Auth URL patterns (/auth/register, /auth/login, etc.)
|   |   |
|   |   +-- expenses/                 # Core business logic
|   |       +-- models.py             # Income, Expense, Saving, Budget, Category, Contact, LedgerEntry
|   |       +-- serializers.py        # Data validation + computed fields + budget checking
|   |       +-- views.py              # ViewSets + Dashboard + KhataBook + Reminder
|   |       +-- urls.py               # Router-based URL patterns
|   |       +-- admin.py              # Django admin panel configuration
|   |       +-- management/
|   |           +-- commands/
|   |               +-- seed_categories.py  # Management command to seed 12 default categories
|   |
|   +-- manage.py                     # Django CLI entry point
|   +-- requirements.txt              # Python dependencies (pinned versions)
|   +-- .env                          # Environment variables (SECRET_KEY, DEBUG, etc.)
|   +-- .env.example                  # Template for team members
|   +-- Procfile                      # Render deployment command
|   +-- build.sh                      # Render build script
|   +-- render.yaml                   # Render service configuration
|   +-- runtime.txt                   # Python version for deployment
|   +-- db.sqlite3                    # SQLite database (development)
|
+-- frontend/                         # Plain HTML/CSS/JS Client
|   +-- index.html                    # Landing page (public)
|   +-- pages/
|   |   +-- login.html                # Login form
|   |   +-- register.html             # Registration form
|   |   +-- dashboard.html            # Dashboard with charts and stats
|   |   +-- income.html               # Income management
|   |   +-- expenses.html             # Expense management with filters + PDF export
|   |   +-- savings.html              # Savings management
|   |   +-- budgets.html              # Budget management with progress bars
|   |   +-- khatabook.html            # KhataBook (contacts + ledger + reminders)
|   |   +-- chatbot.html              # AI Assistant (Gemini integration)
|   |   +-- about.html                # About team page
|   +-- css/
|   |   +-- style.css                 # Global styles (layout, components, responsive)
|   |   +-- chatbot.css               # Chat-specific styles
|   +-- js/
|   |   +-- api.js                    # HTTP layer (fetch + JWT token management)
|   |   +-- app.js                    # Shared app logic (auth guard, rendering, utilities)
|   |   +-- chatbot.js                # Gemini AI chatbot logic
|   +-- images/
|   |   +-- sushant.jpg               # Team member photo
|   +-- netlify.toml                  # Netlify deployment config
|
+-- README.md                         # This file
```

---

## 15. API Reference (Complete)

### Base URL
```
Development: http://127.0.0.1:8000/api/v1
Production:  https://expmanage-api.onrender.com/api/v1
```

### Authentication Endpoints

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register/` | `{username, email, first_name, password, password_confirm}` | Register + auto-login (returns tokens) |
| `POST` | `/auth/login/` | `{username, password}` | Login, returns access + refresh tokens |
| `POST` | `/auth/login/refresh/` | `{refresh}` | Get new access token using refresh token |
| `GET` | `/auth/profile/` | - | Get current user profile |
| `PATCH` | `/auth/profile/` | `{first_name?, last_name?, email?}` | Update profile fields |
| `POST` | `/auth/change-password/` | `{old_password, new_password}` | Change password |
| `POST` | `/auth/logout/` | `{refresh}` | Blacklist refresh token (invalidate) |

### Dashboard

| Method | Endpoint | Query Params | Returns |
|--------|----------|--------------|---------|
| `GET` | `/dashboard/` | `?month=5&year=2025` | total_income, total_expenses, total_savings, balance, recent_expenses, budget_overview, expenses_by_category |

### Categories

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `GET` | `/categories/` | Authenticated | List all 12 categories |
| `POST` | `/categories/` | Admin only | Create new category |

### Income

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/incomes/` | List incomes (paginated, `?month=&year=&source=&ordering=`) |
| `POST` | `/incomes/` | Create `{amount, source, date, description}` |
| `GET` | `/incomes/{id}/` | Get single income |
| `PUT` | `/incomes/{id}/` | Update income |
| `DELETE` | `/incomes/{id}/` | Delete income |
| `GET` | `/incomes/summary/` | Current month total |

### Expenses

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/expenses/` | List expenses (`?category=&month=&year=&start_date=&end_date=&search=&ordering=`) |
| `POST` | `/expenses/` | Create `{amount, category, date, description}` (validates vs budget) |
| `GET` | `/expenses/{id}/` | Get single expense |
| `PUT` | `/expenses/{id}/` | Update expense |
| `DELETE` | `/expenses/{id}/` | Delete expense |
| `GET` | `/expenses/summary/` | Current month total |
| `GET` | `/expenses/by-category/` | Grouped by category with totals (`?month=&year=`) |

### Savings

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/savings/` | List savings (`?goal=&date=&ordering=`) |
| `POST` | `/savings/` | Create `{amount, goal, date, description}` |
| `GET` | `/savings/{id}/` | Get single saving |
| `PUT` | `/savings/{id}/` | Update saving |
| `DELETE` | `/savings/{id}/` | Delete saving |
| `GET` | `/savings/summary/` | Total + monthly savings |

### Budgets

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/budgets/` | List budgets (`?category=&month=&year=`) with spent/remaining/percentage |
| `POST` | `/budgets/` | Create `{category, limit, month, year}` (unique per category/month) |
| `GET` | `/budgets/{id}/` | Budget detail with computed fields |
| `PUT` | `/budgets/{id}/` | Update budget limit |
| `DELETE` | `/budgets/{id}/` | Delete budget |

### Contacts (KhataBook)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/contacts/` | List contacts with balance/total_gave/total_got |
| `POST` | `/contacts/` | Create `{name, phone, notes}` (phone unique per user) |
| `GET` | `/contacts/{id}/` | Contact detail |
| `PUT` | `/contacts/{id}/` | Update contact |
| `DELETE` | `/contacts/{id}/` | Delete contact + all entries |

### Ledger (KhataBook)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ledger/` | All ledger entries (`?contact=&transaction_type=&date=`) |
| `POST` | `/ledger/` | Create `{contact, amount, transaction_type, date, description}` |
| `DELETE` | `/ledger/{id}/` | Delete entry |
| `GET` | `/ledger/by-contact/?contact_id=X` | Entries for specific contact |
| `POST` | `/ledger/send-reminder/` | Generate SMS/WhatsApp links `{contact_id}` |

### Documentation

| URL | Description |
|-----|-------------|
| `/api/docs/` | Interactive Swagger UI |
| `/api/schema/` | Raw OpenAPI 3.0 JSON schema |
| `/admin/` | Django Admin Panel |

---

## 16. Interview Questions & Answers

### Q1: "Tell me about your project." (STAR)

**S:** People struggle to manage personal finances across income, expenses, savings, and lending.
**T:** Build a full-stack web app to track all financial activities in one place with AI assistance.
**A:** Designed a decoupled architecture with Django REST API backend (JWT auth, ViewSets, 25+ endpoints) and a plain HTML/CSS/JS frontend with Gemini AI chatbot, KhataBook ledger, and PDF export.
**R:** 7-module application handling complete personal finance lifecycle with real-time budget validation, SMS/WhatsApp reminders, and AI-powered guidance.

---

### Q2: "Why did you choose this tech stack?"

**Backend (Django + DRF):** Rapid development, built-in ORM/admin/auth, industry-standard REST patterns. SimpleJWT gives stateless auth suitable for any client (web, mobile, etc.).

**Frontend (Plain JS):** Zero build step means instant deployability. Demonstrates raw JavaScript proficiency (no framework crutch). No dependency vulnerabilities to manage.

**SQLite for dev, PostgreSQL for prod:** Zero config in development, swap one line for production-grade database.

---

### Q3: "How do you handle authentication?"

JWT with access + refresh token pattern:
- Access token (60 min) for API calls
- Refresh token (7 days) to get new access tokens without re-login
- Token rotation (new refresh on each refresh call)
- Token blacklisting on logout (prevents reuse)
- Frontend auto-refresh: intercepts 401, refreshes, retries request seamlessly
- Object-level permission (IsOwner) ensures data isolation between users

---

### Q4: "How do you prevent one user from accessing another user's data?"

Three layers:
1. **Queryset filtering:** `get_queryset()` returns `Model.objects.filter(user=request.user)` - even if you guess an ID, the queryset won't include it
2. **IsOwner permission:** On object-level access (retrieve/update/delete), checks `obj.user == request.user`
3. **Serializer validation (KhataBook):** `validate_contact()` ensures the contact FK belongs to the requesting user

---

### Q5: "How does budget validation work?"

When creating an expense:
1. Serializer's `validate()` method fires
2. Looks up Budget for that user + category + month/year
3. If budget exists, queries current spending for that category/month
4. If `current_spending + new_expense > budget_limit`, raises `ValidationError`
5. Error response includes: current spending, budget limit, and the category name
6. Frontend displays this as a toast notification

This is **server-side validation** - even if someone bypasses the frontend, the API rejects overspending.

---

### Q6: "Explain your KhataBook feature."

**What it is:** Digital ledger for tracking money lent to or borrowed from people (like the KhataBook app).

**How it works:**
- Add contacts with phone numbers (validated, unique per user)
- Record "You Gave" (they owe you) or "You Got" (they paid back)
- Balance auto-calculated: `sum(gave) - sum(got)` per contact
- Positive balance = they owe you, Negative = you owe them
- Send SMS/WhatsApp reminders via deep links (opens native messaging app)
- `notify_sent` flag tracks which entries have been reminded about

---

### Q7: "How does the AI chatbot work?"

- Frontend directly calls Google Gemini 1.5 Flash API (no backend proxy)
- System instruction defines the AI as a "financial assistant for ExpManage"
- Conversation history array maintains context across messages
- Responses rendered with Markdown (via marked.js) and code highlighting (via highlight.js)
- Suggestion chips provide quick-start prompts for new users

---

### Q8: "How do you handle errors consistently?"

Custom exception handler (`apps/core/exceptions.py`):
- Intercepts ALL DRF exceptions via `EXCEPTION_HANDLER` setting
- Maps status codes to error codes (400->BAD_REQUEST, 401->UNAUTHORIZED, etc.)
- Returns uniform structure: `{success: false, error: {code, message, details}}`
- Frontend knows exactly how to parse every error response
- Also catches Django's `ValidationError` (not just DRF's)

---

### Q9: "What would you improve with more time?"

- **PostgreSQL** for production (better performance, concurrent writes)
- **Docker + docker-compose** for one-command setup
- **CI/CD** with GitHub Actions (automated tests on PR)
- **WebSocket** for real-time budget alerts
- **Recurring expenses** (auto-create monthly rent, subscriptions)
- **React Native mobile app** using the same API
- **Two-factor authentication** (2FA)
- **Multi-currency support** with conversion rates

---

### Q10: "How is this project production-ready?"

| Aspect | Implementation |
|--------|---------------|
| Deployment | Render (backend) + Netlify (frontend) configs included |
| Security | JWT, CORS, rate limiting, data isolation, password validation |
| Performance | Pagination, select_related (no N+1), WhiteNoise for static |
| Monitoring | Consistent error responses, Django admin for data review |
| Scalability | Stateless JWT = add more servers behind load balancer |
| Documentation | Auto-generated Swagger UI always in sync with code |

---

## 17. Future Scope

| Feature | Description | Complexity |
|---------|-------------|------------|
| **Recurring Transactions** | Auto-create monthly expenses (rent, subscriptions) | Medium |
| **CSV/Excel Export** | Download expense data in spreadsheet format | Easy |
| **Multi-Currency** | Support different currencies with live conversion rates | Medium |
| **Email Notifications** | Weekly spending summaries via email | Medium |
| **Push Notifications** | Browser push alerts when approaching budget limits | Medium |
| **Analytics & Trends** | Monthly/yearly spending trends, predictions | Hard |
| **Dark Mode** | Full dark theme toggle | Easy |
| **React Native App** | Mobile app using the same REST API | Hard |
| **Shared Budgets** | Family/group expense tracking and splitting | Hard |
| **Receipt Upload (OCR)** | Photo of receipt -> auto-extract amount & category | Hard |
| **PostgreSQL** | Production database for concurrent access | Easy |
| **Docker** | Containerized deployment with docker-compose | Medium |
| **CI/CD** | GitHub Actions for automated testing & deployment | Medium |
| **WebSocket Alerts** | Real-time notifications when budget exceeded | Medium |
| **2FA** | Two-factor authentication (TOTP/SMS) | Medium |
| **Audit Logs** | Track all user actions for compliance | Medium |

---

## Quick Summary Card (For Interview Opening)

```
Project: ExpManage - Smart Personal Finance Manager
Type:    Full-Stack Web Application
Stack:   Django 5.1 + DRF + SimpleJWT | HTML5 + CSS3 + JavaScript (ES6+) | Gemini AI
DB:      SQLite (dev) / PostgreSQL (prod)
Auth:    JWT (Access + Refresh tokens with rotation & blacklisting)
Deploy:  Render (API) + Netlify (Frontend)

Modules:
  1. Dashboard      - Aggregated financial summary with charts
  2. Income         - CRUD with source tracking
  3. Expenses       - CRUD with category filtering, budget validation
  4. Savings        - CRUD with goal-based tracking
  5. Budgets        - Category-wise monthly limits with overspend alerts
  6. KhataBook      - Contact ledger (gave/got) + SMS/WhatsApp reminders
  7. AI Chatbot     - Gemini AI financial assistant

Key Technical Highlights:
  - 25+ REST API endpoints with Swagger documentation
  - Custom exception handler for consistent error responses
  - Object-level permissions (IsOwner) for data isolation
  - Auto token refresh (seamless UX on expiry)
  - Server-side budget validation (not just frontend)
  - Zero frontend dependencies (no npm, no build step)
  - Production deployment configs included (Render + Netlify)
```

---

## Team

| Name | Role |
|------|------|
| Sushant Patil | Lead Developer |
| Vilas Rathod | Front-End Developer |
| Devraj Powar | Back-End Developer |
| Sanghpal Pawar | Front-End Developer |

---

*Built for better financial management. Good luck in your interview!*
