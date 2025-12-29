# LinkFarm Backend API

A Flask-based REST API for the LinkFarm marketplace platform - connecting local farmers with customers.

## 🏗️ Architecture

**Platform Type:** Connection/Listing Platform (like Carousell)
**Business Model:** Farmers list products → Customers browse and contact farmers → They arrange purchase/delivery directly
**No Payment Processing:** We facilitate connections, not transactions

## 🛠️ Technology Stack

- **Framework:** Flask 3.1.1
- **Database:** PostgreSQL (Supabase)
- **ORM:** SQLAlchemy 2.0
- **Authentication:** JWT (flask-jwt-extended)
- **Migrations:** Flask-Migrate (Alembic)
- **Validation:** Marshmallow
- **File Storage:** Supabase Storage
- **Testing:** pytest
- **Deployment:** Koyeb (Free Tier)

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.9+
- PostgreSQL (or use Supabase for development)
- pip and virtualenv

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/lilycandoit/linkfarm-backend-py.git
cd linkfarm-backend-py

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration (see Configuration section below)

# 5. Run database migrations
flask db upgrade

# 6. (Optional) Seed database with sample data
# Run seed_data.sql in your PostgreSQL/Supabase dashboard

# 7. Start the development server
python app.py
```

Server will be available at `http://localhost:5000`

---

## ⚙️ Configuration

Create a `.env` file in the backend root with the following variables:

### For Local Development:

```env
# Database Configuration (Local PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/linkfarm

# OR use Supabase connection string
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# Security
SECRET_KEY=your-super-secret-key-here-change-in-production

# CORS - Frontend URL
FRONTEND_URL=http://localhost:5173

# Environment
FLASK_ENV=development

# Supabase Configuration (for file uploads)
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_KEY=your-supabase-service-role-key

# Optional: Google Gemini API (for AI features)
GEMINI_API_KEY=your-gemini-api-key
```

### For Production (Koyeb):

```env
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
FLASK_ENV=production
SECRET_KEY=generate-a-strong-random-key
FRONTEND_URL=https://your-vercel-app.vercel.app
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_KEY=your-service-role-key
GEMINI_API_KEY=your-gemini-api-key
```

**Important:** Never commit your `.env` file to version control!

---

## 📊 Database Migrations

### Creating Migrations

When you modify models (add/remove/change fields):

```bash
# Generate migration file
flask db migrate -m "Description of changes"

# Review the generated migration in migrations/versions/

# Apply migration
flask db upgrade
```

### Common Migration Commands

```bash
flask db current      # Show current migration version
flask db history      # Show all migrations
flask db downgrade    # Rollback last migration
flask db upgrade      # Apply pending migrations
```

### Why Migrations?

- **Schema Version Control:** Track all database changes over time
- **Safe Updates:** Add/modify columns without losing data
- **Team Collaboration:** Share schema changes via Git
- **Rollback Support:** Revert problematic changes easily

---

## 🌱 Seeding Sample Data

To populate your database with sample products for testing:

1. Open Supabase Dashboard → SQL Editor
2. Run the `seed_data.sql` file
3. Creates 1 farmer account and 6 sample products

**Test Login Credentials:**
- Email: `farmer@linkfarm.demo`
- Password: `farmer123`

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run in verbose mode with short tracebacks
pytest -v --tb=line

# Run specific test file
pytest tests/test_auth.py

# Run tests with coverage
pytest --cov=. --cov-report=html
```

---

## 📁 Project Structure

```
linkfarm-backend-py/
├── app.py                  # Application factory
├── config.py               # Configuration classes
├── extensions.py           # Flask extensions
├── models/                 # SQLAlchemy models
│   ├── user.py
│   ├── farmer.py
│   ├── product.py
│   └── inquiry.py
├── routes/                 # API blueprints
│   ├── auth.py            # /api/login, /api/register
│   ├── farmer.py          # /api/farmers/*
│   ├── product.py         # /api/products/*
│   ├── inquiry.py         # /api/inquiries/*
│   ├── upload.py          # /api/upload/*
│   ├── dashboard.py       # /api/dashboard/*
│   └── ai.py              # /api/ai/*
├── schemas/               # Marshmallow schemas
│   ├── user_schema.py
│   ├── farmer_schema.py
│   └── product_schema.py
├── migrations/            # Alembic migrations
├── tests/                 # pytest tests
├── uploads/               # Local file uploads (dev only)
├── requirements.txt       # Python dependencies
├── Procfile               # Koyeb deployment config
├── runtime.txt            # Python version for deployment
└── seed_data.sql          # Sample data SQL script
```

---

## 🚢 Deployment

### Deploying to Koyeb (Free Tier)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **Deploy on Koyeb**
   - Connect your GitHub repository
   - Koyeb auto-detects Python and uses `Procfile`
   - Set environment variables in Koyeb dashboard
   - Deploy!

3. **Set Environment Variables on Koyeb**
   - `DATABASE_URL` - Supabase connection string
   - `FLASK_ENV=production`
   - `SECRET_KEY` - Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
   - `FRONTEND_URL` - Your Vercel URL (NO trailing slash!)
   - `SUPABASE_URL` - From Supabase dashboard
   - `SUPABASE_KEY` - service_role key from Supabase

4. **Run Migrations on Production**
   ```bash
   # Run locally against production database
   export DATABASE_URL="your-supabase-url"
   export FLASK_ENV=production
   flask db upgrade
   ```

### Deployment Files

- `Procfile` - Tells Koyeb how to start the app
- `runtime.txt` - Specifies Python version (3.12.8)
- `requirements.txt` - Python dependencies

---

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/register` | Register new user | No |
| POST | `/api/login` | Login and get JWT token | No |

### Farmer Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/farmers` | List all farmers | No |
| GET | `/api/farmers/me` | Get my farmer profile | Yes |
| POST | `/api/farmers` | Create farmer profile | Yes |
| PUT | `/api/farmers/<id>` | Update farmer profile | Yes (Owner) |

### Product Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/products` | List all products (paginated) | No |
| GET | `/api/products/<id>` | Get product details | No |
| POST | `/api/products` | Create new product | Yes (Farmer) |
| PUT | `/api/products/<id>` | Update product | Yes (Owner) |
| DELETE | `/api/products/<id>` | Delete product | Yes (Owner) |

### Inquiry Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/inquiries` | Create inquiry | Yes |
| GET | `/api/inquiries/farmers/<id>/inquiries` | Get farmer's inquiries | Yes (Owner) |
| PATCH | `/api/inquiries/<id>/status` | Update inquiry status | Yes (Farmer) |

---

## 🔒 Security Features

- **JWT Authentication:** Secure token-based auth
- **Password Hashing:** bcrypt with salt rounds
- **CORS Protection:** Configured for specific frontend origin
- **SQL Injection Prevention:** SQLAlchemy ORM with parameterized queries
- **Environment Variables:** Secrets stored outside code
- **Input Validation:** Marshmallow schemas validate all inputs

---

## 🐛 Common Issues

### Issue: CORS errors in frontend

**Solution:** Ensure `FRONTEND_URL` in Koyeb has NO trailing slash:
```
✅ FRONTEND_URL=https://your-app.vercel.app
❌ FRONTEND_URL=https://your-app.vercel.app/
```

### Issue: Database connection fails

**Solution:**
- Check Supabase connection string uses Session Pooler (port 6543)
- Verify password has no special characters that need URL encoding
- Ensure `DATABASE_URL` starts with `postgresql://` not `postgres://`

### Issue: Migrations fail on Koyeb

**Solution:**
- Run migrations locally against production database
- Koyeb free tier doesn't provide shell access
- Use: `DATABASE_URL=<prod-url> flask db upgrade` locally

---

## 📝 Development Notes

### Adding a New Model

1. Create model file in `models/`
2. Import in `app.py` (so Flask-Migrate detects it)
3. Create Marshmallow schema in `schemas/`
4. Generate migration: `flask db migrate -m "Add ModelName"`
5. Apply migration: `flask db upgrade`
6. Create API routes in `routes/`

### Code Style

- Follow PEP 8 guidelines
- Use SQLAlchemy 2.0 syntax (`db.select()` not `Model.query`)
- Document functions with docstrings
- Keep routes thin, logic in models/services

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is part of a portfolio demonstration.

---

## 👤 Author

**Lily Do**
GitHub: [@lilycandoit](https://github.com/lilycandoit)

---

## 🙏 Acknowledgments

- Flask framework and ecosystem
- Supabase for database and storage
- Koyeb for free tier deployment
- Vercel for frontend hosting

---

**Live Demo:** [LinkFarm on Vercel](https://link-farm-gules.vercel.app)
