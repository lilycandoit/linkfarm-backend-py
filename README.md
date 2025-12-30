# LinkFarm Backend API 🚜
**Empowering local farmers through direct digital connections.**

**Live Demo:** [https://link-farm-gules.vercel.app](https://link-farm-gules.vercel.app)
**Project Type:** Backend‑Focused Full‑Stack Demo (Portfolio)

---

## 💡 The Inspiration
I grew up in a rural farming community where I saw my parents and neighbours work incredibly hard, only to lose most of their profits to middlemen. LinkFarm is a personal project designed to explore how a simple digital connection can remove barriers between rural producers and urban consumers.

Unlike complex e-commerce platforms, LinkFarm focuses on **discovery and communication over transactions**.

---

## 🛠️ Current Capabilities
The project is a production‑ready MVP that demonstrates clean architecture and secure data handling:

*   **Secure Auth:** JWT‑based authentication with cross‑origin resource sharing (CORS).
*   **Farmer Dashboards:** Dedicated space for farmers to manage listings and incoming inquiries.
*   **Product Discovery:** Real-time product listings with public detail pages.
*   **Direct Communication:**
    *   Mandatory customer phone numbers for direct follow‑ups.
    *   **Facebook Messenger integration** for instant chatting.
    *   Inquiry tracking with ownership‑based authorization.
*   **AI Assistance:** Integrated Google Gemini to auto‑generate persuasive product descriptions.
*   **Internationalisation (i18n):** Multi‑language support structure (English/Vietnamese).
*   **Cloud Storage:** File upload system backed by Supabase Storage.

---

## 🏗️ Technical Architecture & Quality
*   **Backend:** Python/Flask following a modular Blueprint-based structure.
*   **Database:** PostgreSQL (Supabase) managed with SQLAlchemy 2.0.
*   **Migrations:** Robust schema version control using Alembic.
*   **Validation:** Strict schema enforcement via Marshmallow.
*   **Real-time Features:** WebSocket integration (Flask-SocketIO) for instant inquiry notifications.
*   **Analytics:** Comprehensive dashboard with inquiry tracking, product view metrics, and conversion analytics.
*   **Security:**
    *   Password hashing with `bcrypt`.
    *   Strict ownership checks on all write/update operations.
    *   Environment-driven configuration management.

---

## 🚀 Future Roadmap: What's Next?
To take LinkFarm to the next level of production readiness, I plan to focus on:

1.  **Search & Filtering Polish**: Implement PostgreSQL full-text search and advanced category/location filtering. *(Completed)*
2.  ✅ **Real-time Alerts**: Integrate **WebSockets (Flask-SocketIO)** for instant inquiry notifications on the farmer dashboard. *(Completed)*
3.  **Advanced AI Integration**: Use Computer Vision (Gemini 2.0) to analyze product images and suggest optimal pricing/tags.
4.  **Performance Optimization**: Implement Redis caching for high-traffic public listings and server-side image processing for optimized load times.
5.  ✅ **Analytics Dashboard**: Provide farmers with simple charts tracking inquiry volume and product views over time. *(Completed)*

---

## � Local Development

### Prerequisites
- Python 3.9+
- PostgreSQL
- `pip` + `virtualenv`

### Quick Start
```bash
# 1. Setup Environment
git clone https://github.com/lilycandoit/linkfarm-backend-py.git
cd linkfarm-backend-py
python3 -m venv venv
source venv/bin/activate

# 2. Dependencies & Config
pip install -r requirements.txt
cp .env.example .env

# 3. Database Sync
flask db upgrade

# 4. Launch
python app.py
```
*API serves at: `http://localhost:5000`*

### Maintenance Commands
*   **Migrations:** `flask db migrate -m "change description"` then `flask db upgrade`
*   **Rollback:** `flask db downgrade`
*   **Seeding:** Import `seed_data.sql` via your DB management tool.

---

## 👩‍💻 Author
**LiDuong**
*Building software that solves real-world needs.*
GitHub: [https://github.com/lilycandoit](https://github.com/lilycandoit)