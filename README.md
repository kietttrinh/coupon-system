<div align="center">

# 🏷️ CouponStore

**A full-stack e-commerce coupon management system**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://mysql.com)
[![aiogram](https://img.shields.io/badge/aiogram-3.28-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://aiogram.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [API Docs](#-api-reference) · [Bot Commands](#-telegram-bot-commands)

---

> **Transparency note:** This project was built with significant assistance from AI tools. The architecture, algorithms, and implementation were developed collaboratively — the AI helped write code, debug issues, structure the codebase, and generate documentation. All logic has been reviewed, tested, and understood; all algorithms wrote by the project author.

</div>

---

## 📋 Table of Contents

- [🏷️ CouponStore](#️-couponstore)
  - [📋 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🏗️ Architecture](#️-architecture)
  - [🛠️ Tech Stack](#️-tech-stack)
  - [📁 Project Structure](#-project-structure)
  - [🚀 Quick Start](#-quick-start)
    - [Prerequisites](#prerequisites)
    - [1 — Clone \& Install](#1--clone--install)
    - [2 — Configure Environment](#2--configure-environment)
    - [3 — Set Up Database](#3--set-up-database)
    - [4 — Run the Backend](#4--run-the-backend)
    - [5 — Run the Frontend](#5--run-the-frontend)
    - [6 — Run the Telegram Bot](#6--run-the-telegram-bot)
  - [🔧 Environment Variables](#-environment-variables)
    - [Variable Reference](#variable-reference)
  - [📡 API Reference](#-api-reference)
    - [Authentication](#authentication)
    - [Products](#products)
    - [Coupons](#coupons)
    - [Validate Coupon — Request \& Response](#validate-coupon--request--response)
  - [🤖 Telegram Bot Commands](#-telegram-bot-commands)
    - [Coupon Management](#coupon-management)
    - [Product Management](#product-management)
    - [Utility](#utility)
  - [🧮 Core Algorithms](#-core-algorithms)
    - [1. Pricing Engine — `algorithms/pricing_engine/discount_calculator.py`](#1-pricing-engine--algorithmspricing_enginediscount_calculatorpy)
    - [2. Greedy Dynamic Sorting — `algorithms/greedy_sorting/recommend_coupons.py`](#2-greedy-dynamic-sorting--algorithmsgreedy_sortingrecommend_couponspy)
    - [3. Merge Intervals — `algorithms/merge_intervals/overlap_processing.py`](#3-merge-intervals--algorithmsmerge_intervalsoverlap_processingpy)
  - [🧪 Running Tests](#-running-tests)
  - [🤝 AI Collaboration](#-ai-collaboration)
  - [📄 License](#-license)

---

## ✨ Features

| Area | Feature |
|------|---------|
| 🛍️ **Products** | Browse, paginate, sort, and view stock in real-time |
| 🏷️ **Coupons** | Fixed-amount and percentage discounts with constraints |
| 🔐 **Auth** | JWT-based register/login; role-based access (USER / ADMIN) |
| 🤖 **Admin Bot** | Full CRUD for coupons and products via Telegram |
| 💡 **Smart Recommendations** | Greedy algorithm surfaces best coupons for your cart value |
| ⏱️ **Time Scheduling** | Activate coupons on a time window; overlap detection prevents conflicts |
| 🔒 **Private Codes** | Hidden coupon codes for targeted promotions |
| 🧮 **Pricing Engine** | Server-side discount calculation — clients never control pricing |
| 📋 **Audit Log** | Every coupon redemption is tracked in `usage_logs` |
| 🧪 **E2E Tests** | Full test suite using in-memory SQLite — no external DB needed |

---

## 🏗️ Architecture

```
┌──────────────────────────────────┐     ┌──────────────────────────┐
│   Web Browser (Customer)         │     │  Telegram (Admin)        │
│   HTML + CSS + Vanilla JS        │     │  aiogram 3 Bot           │
│   • Browse products              │     │  • Create/edit coupons   │
│   • Apply coupon codes           │     │  • Manage products       │
│   • Smart recommendations        │     │  • FSM multi-step UX     │
└──────────────┬───────────────────┘     └────────────┬─────────────┘
               │  JWT Bearer token                     │  JWT Bearer token
               │  Fetch API (CORS)                     │  httpx (async)
               └──────────────────┬────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │      FastAPI Backend        │
                    │   /api/v1/auth/*            │
                    │   /api/v1/products/*        │
                    │   /api/v1/coupons/*         │
                    │                             │
                    │   ┌─────────────────────┐   │
                    │   │  3 Core Algorithms  │   │
                    │   │  • Pricing Engine   │   │
                    │   │  • Greedy Sort      │   │
                    │   │  • Merge Intervals  │   │
                    │   └─────────────────────┘   │
                    └─────────────┬───────────────┘
                                  │  SQLAlchemy ORM
                    ┌─────────────▼───────────────┐
                    │       MySQL Database         │
                    │  users · products · coupons  │
                    │  coupon_schedules · usage_logs│
                    └─────────────────────────────┘
```

Both the web frontend and the Telegram bot authenticate against the **same** FastAPI backend using standard JWT tokens. The bot logs in as the admin account configured in `.env`.

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — API framework with automatic validation and Swagger docs
- [SQLAlchemy 2.0](https://sqlalchemy.org/) — ORM for database operations
- [Pydantic v2](https://docs.pydantic.dev/) — request/response schema validation
- [PyMySQL](https://pymysql.readthedocs.io/) — MySQL driver
- [python-jose](https://python-jose.readthedocs.io/) — JWT token creation and verification
- [passlib + bcrypt](https://passlib.readthedocs.io/) — secure password hashing
- [uvicorn](https://www.uvicorn.org/) — ASGI server

**Frontend**
- Vanilla HTML5 / CSS3 / JavaScript — zero frameworks, zero build step
- Fetch API — all HTTP calls to the backend
- Google Fonts — Bebas Neue + DM Sans + DM Mono
- CSS custom properties — full dark-theme design system

**Telegram Bot**
- [aiogram 3](https://aiogram.dev/) — async Telegram bot framework
- [httpx](https://www.python-httpx.org/) — async HTTP client for backend calls
- FSM (Finite State Machine) — guided multi-step command flows

**Database**
- MySQL 8.0+ with InnoDB engine
- Proper indexes, foreign keys, and cascade rules

**Testing**
- [pytest](https://pytest.org/) — test runner
- SQLite in-memory — fast isolated test database (no MySQL required)
- FastAPI `TestClient` — full HTTP-level integration tests

---

## 📁 Project Structure

```
coupon-system/
│
├── 📂 backend/
│   └── app/
│       ├── main.py                    # FastAPI app — CORS, router mounting
│       ├── core/
│       │   ├── config.py              # Typed settings from .env (pydantic-settings)
│       │   ├── database.py            # SQLAlchemy engine + session factory
│       │   └── security.py            # bcrypt hashing + JWT sign/verify
│       ├── api/
│       │   ├── deps.py                # Shared dependencies: get_db, get_current_user, get_current_admin
│       │   └── v1/
│       │       ├── router.py          # Combines all endpoint routers under /api/v1
│       │       └── endpoints/
│       │           ├── auth.py        # POST /register, /login, /logout, /refresh · GET /me
│       │           ├── products.py    # CRUD /products + /products/{id}/stock
│       │           └── coupons.py     # CRUD /coupons + /validate + /recommend
│       ├── models/                    # SQLAlchemy ORM table definitions
│       │   ├── user.py
│       │   ├── product.py
│       │   ├── coupon.py              # Enums: VisibilityEnum, DiscountTypeEnum
│       │   ├── coupon_schedule.py
│       │   └── usage_log.py           # UniqueConstraint(user_id, coupon_id)
│       ├── schemas/                   # Pydantic request / response models
│       │   ├── user.py                # UserCreate, UserResponse, Token, TokenPayload
│       │   ├── product.py             # ProductCreate, ProductUpdate, ProductResponse, ProductList
│       │   ├── coupon.py              # CouponCreate, CouponUpdate, CouponResponse, CouponValidate, CouponValidationResult
│       │   └── coupon_schedule.py
│       ├── crud/                      # Pure DB read/write functions (no business logic)
│       │   ├── coupon.py
│       │   ├── product.py
│       │   ├── user.py
│       │   ├── coupon_schedule.py
│       │   └── usage_log.py
│       └── algorithms/                # Isolated, testable business algorithms
│           ├── pricing_engine/
│           │   └── discount_calculator.py   # Validate + calculate any coupon
│           ├── greedy_sorting/
│           │   └── recommend_coupons.py     # Sort coupons by real discount value
│           └── merge_intervals/
│               └── overlap_processing.py    # Detect + merge schedule overlaps
│
├── 📂 backend/tests/
│   ├── conftest.py                    # SQLite override + pytest fixtures
│   └── test_api.py                    # Full E2E: auth → products → coupons → pricing → deactivation
│
├── 📂 database/
│   └── schema/
│       └── mysql_schema.sql           # Full DDL: all 5 tables, indexes, foreign keys
│
├── 📂 frontend/
│   ├── index.html                     # Single-page app — all sections, modals, drawers
│   ├── css/
│   │   └── styles.css                 # 1,100+ lines: design tokens, grid, animations
│   └── js/
│       └── app.js                     # State management, API calls, cart, coupon flow
│
├── 📂 telegram_bot/
│   ├── main.py                        # Bot startup: Dispatcher, middleware, routers, polling
│   ├── config.py                      # Reads shared .env from project root via pathlib
│   ├── middlewares/
│   │   └── auth.py                    # AdminCheckMiddleware — rejects non-admin chat IDs
│   ├── states/
│   │   └── forms.py                   # FSM state groups: CreateCouponState, CreateProductState
│   ├── api/
│   │   └── client.py                  # BackendAPIClient — httpx wrapper with auto token refresh
│   ├── handlers/
│   │   ├── start.py                   # /start — welcome + displays Chat ID
│   │   ├── create_coupon.py           # /add_coupon — dual mode: quick one-liner or FSM interview
│   │   ├── manage.py                  # /me /list_coupons /view_coupon /edit_coupon /del_coupon
│   │   └── product.py                 # /add_product /list_products /view_product /edit_product /del_product
│   ├── keyboards/
│   │   ├── reply.py                   # Reply keyboards: discount type, skip, visibility buttons
│   │   └── inline.py                  # Inline keyboards
│   └── utils/
│       └── formatters.py              # Message formatting helpers
│
├── EXPLAIN.md                         # Deep-dive code explanation for reviewers
├── requirements.txt                   # All Python dependencies (pinned versions)
├── .env.example                       # Template — copy to .env and fill in secrets
└── README.md                          # This file
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Backend + Bot runtime |
| MySQL | 8.0+ | Primary database |
| pip | latest | Dependency management |
| A Telegram account | — | To create and use the admin bot |

---

### 1 — Clone & Install

```bash
# Clone the repository
git clone https://github.com/your-username/coupon-system.git
cd coupon-system

# Create and activate a virtual environment (strongly recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

---

### 2 — Configure Environment

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env` — see the [Environment Variables](#-environment-variables) section below for a description of every key.

**The minimum you must fill in before starting:**
- `MYSQL_PASSWORD` — your MySQL root password
- `BOT_TOKEN` — from [@BotFather](https://t.me/BotFather) on Telegram
- `ADMIN_CHAT_ID` — your personal Telegram Chat ID (send `/start` to the bot first to find it)
- `SECRET_KEY` — any long random string (used to sign JWT tokens)

---

### 3 — Set Up Database

**Create the database in MySQL:**

```bash
mysql -u root -p
```

```sql
CREATE DATABASE coupon_system
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE coupon_system;

-- Run the schema (adjust path separator for your OS)
SOURCE /path/to/coupon-system/database/schema/mysql_schema.sql;

EXIT;
```

> **Windows example:**
> ```sql
> SOURCE C:/projects/coupon-system/database/schema/mysql_schema.sql;
> ```

> **Note:** The FastAPI backend also calls `Base.metadata.create_all()` on startup, which creates any missing tables automatically via SQLAlchemy. Running the SQL schema manually is recommended for production to ensure indexes and constraints are applied correctly.

---

### 4 — Run the Backend

```bash
cd backend

# Development (auto-reload on file changes)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Verify it's running:**
- API root: [http://localhost:8000](http://localhost:8000)
- Interactive Swagger docs: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- ReDoc: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

---

### 5 — Run the Frontend

The frontend is plain HTML/CSS/JS — **no build step required**.

**Option A — Python simple server:**
```bash
cd frontend
python -m http.server 5500
# Open http://localhost:5500
```

**Option B — VS Code Live Server extension:**
Right-click `frontend/index.html` → *Open with Live Server*

**Option C — Open directly:**
Double-click `frontend/index.html` in your file explorer.

> ⚠️ If you open via `file://` directly, some browsers block `fetch()` to `localhost` due to CORS. Using a local server (Option A or B) is recommended.

---

### 6 — Run the Telegram Bot

```bash
# From the project root (so pathlib can find .env)
cd telegram_bot
python main.py
```

**First-time setup — finding your Chat ID:**

1. Create a bot via [@BotFather](https://t.me/BotFather) → get `BOT_TOKEN`
2. Set `ADMIN_CHAT_ID=0` temporarily in `.env`
3. Start the bot: `python main.py`
4. Send `/start` to your bot in Telegram
5. The bot replies with your Chat ID — copy it into `.env` as `ADMIN_CHAT_ID`
6. Restart the bot

---

## 🔧 Environment Variables

Create a `.env` file in the project root. All variables below are required unless marked optional.

```env
# ─────────────────────────────────────────
# APPLICATION
# ─────────────────────────────────────────
APP_NAME=Coupon System
ENVIRONMENT=development       # development | production
DEBUG=true                    # Set false in production

# ─────────────────────────────────────────
# SERVER
# ─────────────────────────────────────────
HOST=0.0.0.0
PORT=8000
API_V1_STR=/api/v1

# ─────────────────────────────────────────
# DATABASE (MySQL)
# ─────────────────────────────────────────
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DB=coupon_system

# ─────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────
# Generate a strong key: python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=change-me-to-a-long-random-secret-string

# ─────────────────────────────────────────
# CORS — origins allowed to call the API
# ─────────────────────────────────────────
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://localhost:5500

# ─────────────────────────────────────────
# TELEGRAM BOT
# ─────────────────────────────────────────
BOT_TOKEN=your_telegram_bot_token_from_botfather

# Your personal Telegram numeric Chat ID
# Send /start to your bot to get it
ADMIN_CHAT_ID=123456789

# ─────────────────────────────────────────
# ADMIN ACCOUNT (used by the bot to log into the API)
# Must match a user registered with role=ADMIN in the database
# ─────────────────────────────────────────
ADMIN_USERNAME=
ADMIN_PASSWORD=
```

### Variable Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_NAME` | Application display name | `Coupon System` |
| `ENVIRONMENT` | Runtime environment | `development` |
| `DEBUG` | Enable SQLAlchemy query logging | `true` |
| `HOST` | Uvicorn bind address | `0.0.0.0` |
| `PORT` | Uvicorn bind port | `8000` |
| `API_V1_STR` | API version prefix | `/api/v1` |
| `MYSQL_HOST` | MySQL server hostname | `localhost` |
| `MYSQL_PORT` | MySQL server port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | `secret` |
| `MYSQL_DB` | Database name | `coupon_system` |
| `SECRET_KEY` | JWT signing secret — keep private | 64-char random string |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5500` |
| `BOT_TOKEN` | Telegram bot token from @BotFather | `123:ABC...` |
| `ADMIN_CHAT_ID` | Your Telegram numeric user ID | `987654321` |
| `ADMIN_USERNAME` | Admin account username in the DB | `admin` |
| `ADMIN_PASSWORD` | Admin account password in the DB | `admin@123` |

> **Security:** Never commit `.env` to version control. The `.gitignore` should include `.env`.

---

## 📡 API Reference

Base URL: `http://localhost:8000/api/v1`

All endpoints except `/auth/register` and `/auth/login` require:
```
Authorization: Bearer <access_token>
```

### Authentication

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | `{username, email, password}` | Create new user account |
| `POST` | `/auth/login` | Form: `username`, `password` | Login; returns JWT token |
| `GET` | `/auth/me` | — | Get current user profile |
| `POST` | `/auth/refresh` | — | Issue a fresh token |
| `POST` | `/auth/logout` | — | Client-side logout hint |

### Products

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/products/` | User | List products `?skip=0&limit=12` |
| `GET` | `/products/{id}` | User | Get product by ID |
| `GET` | `/products/{id}/stock` | User | Check stock availability |
| `POST` | `/products/` | **Admin** | Create product |
| `PUT` | `/products/{id}` | **Admin** | Update product (partial) |
| `DELETE` | `/products/{id}` | **Admin** | Delete product |

### Coupons

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/coupons/` | User | List all coupons `?limit=50` |
| `GET` | `/coupons/recommend` | User | Best coupons for cart `?order_value=99.99&limit=5` |
| `GET` | `/coupons/{id}` | User | Get coupon by ID |
| `POST` | `/coupons/validate` | User | Validate code + calculate discount |
| `POST` | `/coupons/` | **Admin** | Create coupon |
| `PUT` | `/coupons/{id}` | **Admin** | Update coupon (partial) |
| `DELETE` | `/coupons/{id}` | **Admin** | Delete coupon |

### Validate Coupon — Request & Response

```jsonc
// POST /api/v1/coupons/validate
// Request
{
  "code": "SAVE20",
  "order_value": 150.00
}

// Response (valid)
{
  "is_valid": true,
  "coupon_id": 3,
  "code": "SAVE20",
  "discount_type": "PERCENT",
  "discount_value": 20,
  "discount_amount": 25.00,     // capped at max_discount_amount if set
  "final_price": 125.00,
  "error_message": null
}

// Response (invalid)
{
  "is_valid": false,
  "discount_amount": 0,
  "final_price": 0,
  "error_message": "Minimum order value of 200.00 required."
}
```

> 📖 Full interactive docs available at `/api/v1/docs` when the server is running.

---

## 🤖 Telegram Bot Commands

All commands are restricted to the `ADMIN_CHAT_ID` configured in `.env`.

### Coupon Management

| Command | Description |
|---------|-------------|
| `/add_coupon` | Create a coupon via guided step-by-step interview (FSM) |
| `/add_coupon CODE TYPE VALUE MIN_ORDER MAX_DISC VISIBILITY` | Create a coupon instantly in one line |
| `/list_coupons` | Show all coupons with status indicators |
| `/view_coupon CODE` | Show full details of a specific coupon |
| `/edit_coupon CODE FIELD VALUE` | Update any field of a coupon |
| `/del_coupon CODE` | Permanently delete a coupon |

**Quick create example:**
```
/add_coupon FLASH50 FIXED 50000 200000 0 PUBLIC
#           ↑code   ↑type ↑val  ↑min   ↑max ↑visibility
#  (0 = no limit for max_discount)
```

**Edit examples:**
```
/edit_coupon SALE20 is_active false
/edit_coupon SALE20 discount_value 30
/edit_coupon SALE20 visibility PUBLIC
```

### Product Management

| Command | Description |
|---------|-------------|
| `/add_product` | Create a product via guided FSM interview |
| `/add_product Name_With_Underscores Price Stock Description here` | Create instantly |
| `/list_products` | Show all products with ID, price, stock |
| `/view_product ID` | Show full product details |
| `/edit_product ID FIELD VALUE` | Update any product field |
| `/del_product ID` | Delete a product |

### Utility

| Command | Description |
|---------|-------------|
| `/start` | Welcome message + displays your Chat ID |
| `/me` | Show current admin account info from the API |

---

## 🧮 Core Algorithms

### 1. Pricing Engine — `algorithms/pricing_engine/discount_calculator.py`

Centralised discount calculation used by both the validate endpoint and the recommendation system.

```
Inputs:  coupon, order_value, schedules[]
Rules:
  1. Coupon must be is_active = True
  2. If schedules exist: current time must fall within at least one window
  3. order_value must meet min_order_value (if set)
  4. FIXED:   discount = coupon.discount_value (flat amount)
     PERCENT: discount = order_value × (discount_value / 100)
              capped at max_discount_amount (if set)
  5. Clamp: discount = min(discount, order_value)  → price never negative
Output:  {is_valid, discount_amount, final_price, error_message}
```

### 2. Greedy Dynamic Sorting — `algorithms/greedy_sorting/recommend_coupons.py`

Recommends the best coupons for a given cart total, sorted by actual savings.

```
Inputs:  valid_coupons[], order_value
Steps:
  1. Filter: skip coupons where order_value < min_order_value
  2. Score:  run Pricing Engine on each remaining coupon → get actual_discount
  3. Sort:   by actual_discount descending (highest savings first)
Output:  sorted list of CouponResponse schemas
```

> Why not sort by face value? A 30% coupon saves less than a $50 flat coupon on a $100 order. The algorithm scores each coupon against the *actual* cart value to find the true best deal.

### 3. Merge Intervals — `algorithms/merge_intervals/overlap_processing.py`

Detects and merges overlapping coupon time schedules.

```
Inputs:  schedules[]
Steps:
  1. Sort by start_time
  2. Iterate; if current.start ≤ last_merged.end → merge (extend end)
              else → new independent interval
  3. Sum merged durations → total active time
Output:  timedelta (total non-overlapping active duration)
```

Time complexity: **O(N log N)** for sorting + O(N) linear scan.

---

## 🧪 Running Tests

```bash
cd backend

# Run all tests
pytest

# With verbose output
pytest -v

# Run a specific test
pytest tests/test_api.py::test_comprehensive_system_flow -v

# With output (print statements visible)
pytest -s -v
```

**What the test suite covers:**

```
Phase 1 — Auth         Register admin + user · Login both · Verify /me
Phase 2 — Products     Admin creates products · User lists + checks stock
                       User attempts admin action → expects 403
Phase 3 — Coupons      Admin creates FIXED + PERCENT coupons
Phase 4 — Pricing      Below-minimum rejection · FIXED discount · PERCENT cap
Phase 5 — Recommend    Greedy sort returns correct order for given cart value
Phase 6 — Deactivation Admin disables coupon · User attempt fails
```

> Tests use an **in-memory SQLite database** — no MySQL connection needed. The test DB is created fresh before each test and destroyed after, ensuring full isolation.

---

## 🤝 AI Collaboration

This project was built with meaningful assistance from [Claude](https://claude.ai) (Anthropic). Here's an honest breakdown of what that collaboration looked like:

**What AI helped with:**
- Designing the overall system architecture and component boundaries
- Writing the FastAPI endpoints, SQLAlchemy models, and Pydantic schemas
- Implementing the three core algorithms (Pricing Engine, Greedy Sort, Merge Intervals)
- Building the Telegram bot structure, FSM state machine, and API client
- Developing the frontend HTML/CSS/JS from scratch
- Generating this README and `EXPLAIN.md`
- Debugging integration bugs (Markdown parsing errors, type-casting issues, token expiry handling)
- Writing the end-to-end test suite

**What the author contributed:**
- Project requirements and feature definitions
- All architectural decisions were reviewed and approved
- Testing and validating the system actually runs correctly
- Understanding every part of the codebase (see `EXPLAIN.md`)
- Iterating on feedback and directing the AI toward the right solutions

**Why disclose this?**
Because honesty matters in software development. AI tools are becoming a standard part of the development workflow — similar to using Stack Overflow, libraries, or code editors. What matters is whether the developer understands what was built and can maintain, extend, and explain it. This project meets that bar.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ and a lot of ☕ — with help from AI

**[⬆ Back to top](#️-couponstore)**

</div>
