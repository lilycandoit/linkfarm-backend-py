# LinkFarm Backend API 🚜

**A backend service enabling discovery and direct communication between local farmers and consumers.**

**Live Demo (Frontend):** [https://link-farm-gules.vercel.app](https://link-farm-gules.vercel.app)
**Project Type:** Backend-Focused Full-Stack Portfolio Project

---

## 💡 Background

I grew up in a rural farming community and saw firsthand how farmers often lose value to intermediaries.
LinkFarm explores how a **simple, well-structured backend** can support direct discovery and communication — without the complexity of a full e-commerce system.

The goal is **clarity, reliability, and real-world backend patterns**.

---

## ⚙️ Features & Functionality

This backend powers the core functionality of LinkFarm as a production-ready MVP:

* **Authentication & Authorization**

  * JWT-based authentication + role-based access control (RBAC)
  * Roles: `user`, `farmer`, `admin`
  * Ownership checks for write operations
  * Secure password hashing with `bcrypt`
  * Password reset flow via email verification
  * **Admin dashboard** for platform statistics and management

* **Products & Inquiries**

  * CRUD operations for farm products
  * Public product discovery endpoints
  * Inquiry submission + tracking per farmer

* **Direct Communication**

  * Customer phone number required for follow-ups
  * Facebook Messenger (`m.me`) deep-link integration
  * Email notifications for new inquiries

* **AI-Assisted Listings (Optional Layer)**

  * **Gemini Vision** image scanning to suggest **name, category, and price**
  * Auto-generated product descriptions
  * Implemented as a service layer (kept separate from core business logic)

* **Internationalisation (i18n)**

  * English / Vietnamese support using a custom i18n structure

* **Media Handling**

  * **Cloudinary** for image uploads, automatic optimization, and CDN delivery
  * Faster image loading compared to storing media directly in Supabase

---

## 🏗️ Architecture & Engineering Choices

* **Framework:** Python + Flask (Blueprint-based modular structure)
* **Database:** PostgreSQL (Supabase)
* **ORM:** SQLAlchemy 2.0
* **Migrations:** Alembic (Flask-Migrate)
* **Validation:** Marshmallow schemas
* **Email Service:** Resend (transactional HTML emails)
* **AI Integration:** Google Gemini 2.5 Flash (vision + text)
* **Configuration:** Environment-based settings
* **Security:**

  * JWT via Flask-JWT-Extended
  * CORS configuration
  * Strict access control on sensitive routes

Focus is on **maintainability, clear separation of concerns, and real-world backend workflows**.

---

## 💻 Local Development

### Prerequisites

* Python 3.9+
* PostgreSQL
* `pip` + `virtualenv`

### Setup

```bash
# Clone the repo
git clone https://github.com/lilycandoit/linkfarm-backend-py.git
cd linkfarm-backend-py

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Apply database migrations
flask db upgrade

# Run the backend locally
python app.py
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run a specific test file
python -m pytest tests/test_inquiry.py
```

> Or push to GitHub and let the **CI workflow** run all tests automatically.

---

## 🧪 Testing & CI

* **Automated tests:**

  * 70+ tests covering authentication, admin, product management, inquiries, password reset, and settings
  * Written with **pytest**

* **CI/CD:**

  * GitHub Actions runs tests automatically on `push` or `pull_request` to `main/master`
  * Backend workflow ensures all tests pass before merging, improving reliability

---

## 🚀 Next Improvements

* Interactive farm location mapping
* Even more comprehensive test coverage
* User activity analytics
