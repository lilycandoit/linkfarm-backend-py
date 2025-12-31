# LinkFarm Backend API 🚜
**A backend service enabling discovery and direct communication between local farmers and consumers.**

**Live Demo (Frontend):** https://link-farm-gules.vercel.app
**Project Type:** Backend-Focused Full-Stack Portfolio Project

---

## 💡 Background
I grew up in a rural farming community and saw firsthand how farmers often lose value to intermediaries.
LinkFarm explores how a **simple, well-structured backend** can support direct discovery and communication — without the complexity of a full e-commerce system.

The goal is clarity, reliability, and real-world backend patterns.

---

## ⚙️ What This API Does
This backend powers the core functionality of LinkFarm as a production-ready MVP:

- **Authentication & Authorization**
  - JWT-based authentication
  - Ownership checks for all write operations
  - Secure password hashing with `bcrypt`

- **Product & Inquiry Management**
  - CRUD operations for farm products
  - Public product discovery endpoints
  - Inquiry submission and tracking per farmer

- **Direct Communication Support**
  - Mandatory customer phone numbers for follow-ups
  - Facebook Messenger (`m.me`) deep-link integration
  - Email notifications sent instantly when inquiries are received

- **AI-Assisted Content (Optional Layer)**
  - Image-based product analysis (name, category, price suggestion)
  - Auto-generated product descriptions
  - Designed as a service layer, not tightly coupled to core logic

- **Internationalisation (i18n)**
  - Backend-ready structure for English / Vietnamese content

- **Media Handling**
  - Cloudinary integration for optimized image storage and CDN delivery

---

## 🏗️ Architecture & Engineering Choices
- **Framework:** Python + Flask (Blueprint-based modular structure)
- **Database:** PostgreSQL (Supabase)
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic (Flask-Migrate)
- **Validation:** Marshmallow schemas
- **Email Service:** Resend (transactional HTML emails)
- **AI Integration:** Google Gemini 2.5 Flash (vision + text)
- **Configuration:** Environment-based settings
- **Security:**
  - JWT via Flask-JWT-Extended
  - CORS configuration
  - Strict access control on all sensitive routes

The focus is on **maintainability, clear separation of concerns, and real-world backend workflows**.

---

## 🚀 Next Chapter (Planned Improvements)
- Interactive farm location mapping
- Role-based permissions (admin / farmer)
- More comprehensive test coverage

These are intentionally left out of the MVP to keep the system focused and understandable.

---

## 💻 Local Development

### Prerequisites
- Python 3.9+
- PostgreSQL
- `pip` + `virtualenv`

### Setup
```bash
git clone https://github.com/lilycandoit/linkfarm-backend-py.git
cd linkfarm-backend-py

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

flask db upgrade
python app.py
