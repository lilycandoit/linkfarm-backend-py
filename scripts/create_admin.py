#!/usr/bin/env python3
"""
Bootstrap script to create admin user in production database.

This script connects directly to your Supabase database (or any PostgreSQL database)
and creates an admin user. Perfect for serverless deployments where you can't SSH.

Usage:
    # Interactive mode (safest - prompts for everything)
    python scripts/create_admin.py

    # Production database
    python scripts/create_admin.py --env production

    # With arguments (for automation/CI/CD)
    python scripts/create_admin.py --env production \
        --username admin \
        --email admin@linkfarm.com \
        --password SecurePass123

Environment files:
    - Development: .env
    - Production: .env.production

Both should contain: DATABASE_URL=postgresql://...

Created: 2026-01-01
"""

import sys
import os
import argparse
from getpass import getpass

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.user import User
from dotenv import load_dotenv


def get_database_url(env='development'):
    """Load database URL from environment file."""
    env_file = '.env.production' if env == 'production' else '.env'

    # Load environment variables
    load_dotenv(env_file)

    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError(
            f'DATABASE_URL not found in {env_file}\n'
            f'Please create {env_file} with your database connection string.\n'
            f'Example: DATABASE_URL=postgresql://user:pass@host:5432/dbname'
        )

    # Supabase and some hosting providers use postgres://, but SQLAlchemy needs postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)

    return db_url


def create_admin_user(db_url, username, email, password):
    """Create admin user in the database."""

    # Create database connection
    print(f'📡 Connecting to database...')
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if user already exists
        print(f'🔍 Checking if user already exists...')
        existing_user = session.execute(
            text("SELECT id, username, email, role FROM users WHERE username = :username OR email = :email"),
            {"username": username, "email": email}
        ).first()

        if existing_user:
            print(f'\n❌ Error: User already exists!')
            print(f'   Username: {existing_user.username}')
            print(f'   Email: {existing_user.email}')
            print(f'   Role: {existing_user.role}')
            return False

        # Create admin user
        print(f'👤 Creating admin user...')
        admin = User(
            username=username,
            email=email,
            role='admin'
        )
        admin.set_password(password)

        session.add(admin)
        session.commit()

        print('\n✅ Admin user created successfully!')
        print('─' * 50)
        print(f'   Username: {admin.username}')
        print(f'   Email: {admin.email}')
        print(f'   Role: {admin.role}')
        print(f'   ID: {admin.id}')

        # Show database info (without password)
        db_host = db_url.split('@')[1].split('/')[0] if '@' in db_url else 'unknown'
        print(f'   Database: {db_host}')
        print('─' * 50)
        print('\n🎉 You can now login with these credentials!')

        return True

    except Exception as e:
        session.rollback()
        print(f'\n❌ Error creating admin user: {str(e)}')
        print('\nTroubleshooting:')
        print('1. Check your DATABASE_URL is correct')
        print('2. Ensure the database is accessible from your network')
        print('3. Verify the users table exists (run migrations first)')
        return False

    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description='Create admin user in LinkFarm database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  python scripts/create_admin.py

  # Production database
  python scripts/create_admin.py --env production

  # Non-interactive (for CI/CD)
  python scripts/create_admin.py --env production \\
    --username admin \\
    --email admin@linkfarm.com \\
    --password "$ADMIN_PASSWORD"
        """
    )
    parser.add_argument(
        '--env',
        default='development',
        choices=['development', 'production'],
        help='Environment to use (default: development)'
    )
    parser.add_argument('--username', help='Admin username')
    parser.add_argument('--email', help='Admin email')
    parser.add_argument(
        '--password',
        help='Admin password (WARNING: visible in command history - use interactive mode instead)'
    )

    args = parser.parse_args()

    # Header
    print('\n' + '=' * 50)
    print('🔧 LinkFarm Admin User Creation')
    print('=' * 50)
    print(f'Environment: {args.env.upper()}')
    print('=' * 50 + '\n')

    # Get database URL
    try:
        db_url = get_database_url(args.env)
    except ValueError as e:
        print(f'❌ {str(e)}')
        return 1

    # Get credentials (prompt if not provided)
    print('📝 Enter admin credentials:\n')

    username = args.username or input('Username: ')
    email = args.email or input('Email: ')

    if args.password:
        password = args.password
        print('⚠️  Warning: Password was passed via command line (visible in history)')
    else:
        password = getpass('Password: ')
        password_confirm = getpass('Confirm password: ')

        if password != password_confirm:
            print('\n❌ Passwords do not match!')
            return 1

    # Validation
    if not username or not email or not password:
        print('\n❌ All fields are required!')
        return 1

    if len(password) < 8:
        print('\n❌ Password must be at least 8 characters!')
        return 1

    # Confirm production changes
    if args.env == 'production':
        print('\n' + '⚠️ ' * 25)
        print('⚠️  WARNING: You are about to modify the PRODUCTION database!')
        print('⚠️ ' * 25)
        confirm = input('\nType "yes" to continue: ')
        if confirm.lower() != 'yes':
            print('\n❌ Cancelled.')
            return 1
        print()

    # Create admin user
    success = create_admin_user(db_url, username, email, password)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
