# 🧠 Project Match — Backend

RRebuilt using **FastAPI**, **SQLAlchemy**, and **MySQL**, providing user authentication and role-based access control for students and supervisors.

---

## 🔧 Tech Stack

- **FastAPI** — High performance, async-ready API framework
- **SQLAlchemy** — ORM for database interaction
- **MySQL** — Relational database
- **Pydantic v2** — Data validation and parsing
- **Postman** — API testing

---

## 📁 Project Structure Overview

```bash
backend/
├── assets/              # Screenshots for testing
├── config.py            # App-level configuration
├── database.py          # DB connection and session management
├── main.py              # FastAPI app entrypoint
│
├── crud/                # Low-level DB operations
│   ├── user.py
│   ├── student.py
│   └── supervisor.py
│
├── models/              # SQLAlchemy models
│   ├── user_base.py     # Abstract user class
│   ├── student.py
│   ├── supervisor.py
│   └── project.py
│
├── routers/             # API route handlers
│   ├── user.py          # /register, /login, /me, /refresh
│   ├── student.py       # Student-only routes
│   └── supervisor.py    # Supervisor-only routes
│
├── schemas/             # Pydantic models for request/response
│   ├── user.py
│   ├── student.py
│   └── supervisor.py
│
├── services/            # Business logic layer
│   ├── auth.py
│   ├── student.py
│   └── supervisor.py
│
├── dependencies/        # Token + role-based dependencies
│   └── auth.py
│
├── utils/               # Utility functions
│   ├── jwt.py           # JWT token creation and validation
│
├── tests/               # API test cases (to be implemented)
└── requirements.txt     # Dependency list
···
