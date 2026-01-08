# Backend Utility Scripts

This folder contains utility scripts for database operations and data migrations.

---

## 📜 Available Scripts

### 1. `create_admin.py` - Create Admin Users

Creates admin users directly in the production database. Perfect for serverless deployments where you can't SSH into the server.

**Usage:**

```bash
# Interactive mode (safest - prompts for credentials)
# Local development
python scripts/create_admin.py

# Production (manually)
python scripts/create_admin.py --env production

# With arguments (for CI/CD automation) - just an example - change with your credentials
python scripts/create_admin.py --env production \
    --username admin \
    --email admin@linkfarm.com \
    --password SecurePass123
```

**What it does:**
- Connects to your database (reads `DATABASE_URL` from `.env` or `.env.production`)
- Creates a new admin user with hashed password
- Assigns admin role and permissions
- Safe to run multiple times (checks if user exists)

**Requirements:**
- Database must be accessible
- `DATABASE_URL` must be set in environment file

---

### 2. `migrate_images_to_cloudinary.py` - Image Migration

Migrates product and farmer profile images from Supabase Storage to Cloudinary for better performance.

**Prerequisites:**

1. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Set environment variables in `.env`:**
   ```bash
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

   Get credentials from: https://console.cloudinary.com/ → Settings → API Keys

**Usage:**

```bash
# 1. Dry run first (preview changes without modifying database)
python scripts/migrate_images_to_cloudinary.py --dry-run

# 2. Migrate only products
python scripts/migrate_images_to_cloudinary.py --products

# 3. Migrate only farmers
python scripts/migrate_images_to_cloudinary.py --farmers

# 4. Migrate everything (products + farmers)
python scripts/migrate_images_to_cloudinary.py
```

**What it does:**
1. Finds all images hosted on Supabase Storage
2. Downloads each image from Supabase
3. Uploads to Cloudinary with automatic optimization:
   - Format conversion (WebP for modern browsers)
   - Quality optimization (`q_auto`)
   - CDN distribution
4. Updates database records with new Cloudinary URLs
5. Skips images already on Cloudinary (idempotent)


**Safety features:**
- Dry run mode for testing
- Skips already migrated images
- Detailed error logging
- Never overwrites existing Cloudinary images

**Troubleshooting:**

| Error | Solution |
|-------|----------|
| "Cloudinary credentials not configured" | Set `CLOUDINARY_*` variables in `.env` |
| "Download failed" | Check Supabase bucket permissions (should be public) |
| "Upload failed" | Verify Cloudinary credentials and usage limits |

---

## 🚀 Quick Reference

```bash
# Create admin user
python scripts/create_admin.py --env production

# Migrate images (dry run first!)
python scripts/migrate_images_to_cloudinary.py --dry-run
python scripts/migrate_images_to_cloudinary.py

# Make script executable
chmod +x scripts/your_script.py

# Install dependencies
pip install -r requirements-dev.txt
```

---

**Last Updated:** 2026-01-08
**Maintained By:** LinkFarm Team
