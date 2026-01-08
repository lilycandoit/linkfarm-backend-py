#!/usr/bin/env python3
"""
Image Migration Script: Supabase Storage → Cloudinary
=====================================================

Migrates product and farmer profile images from Supabase Storage to Cloudinary.

Features:
- Downloads images from Supabase URLs
- Uploads to Cloudinary with optimization
- Updates database records with new URLs
- Supports dry-run mode for testing
- Detailed progress tracking and error handling

Usage:
    # Dry run (preview changes without modifying database)
    python scripts/migrate_images_to_cloudinary.py --dry-run

    # Migrate only products
    python scripts/migrate_images_to_cloudinary.py --products

    # Migrate only farmers
    python scripts/migrate_images_to_cloudinary.py --farmers

    # Migrate everything (products + farmers)
    python scripts/migrate_images_to_cloudinary.py

Requirements:
    pip install cloudinary requests python-dotenv
"""

import os
import sys
import argparse
import requests
from datetime import datetime
from urllib.parse import urlparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.product import Product
from models.farmer import Farmer

# Cloudinary SDK
try:
    import cloudinary
    import cloudinary.uploader
    from cloudinary.utils import cloudinary_url
except ImportError:
    print("❌ Error: cloudinary package not installed")
    print("Please install: pip install cloudinary")
    sys.exit(1)


class ImageMigrator:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.stats = {
            'products_processed': 0,
            'products_migrated': 0,
            'products_skipped': 0,
            'products_failed': 0,
            'farmers_processed': 0,
            'farmers_migrated': 0,
            'farmers_skipped': 0,
            'farmers_failed': 0,
        }

        # Configure Cloudinary
        self.setup_cloudinary()

    def setup_cloudinary(self):
        """Configure Cloudinary from environment variables"""
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        api_key = os.environ.get('CLOUDINARY_API_KEY')
        api_secret = os.environ.get('CLOUDINARY_API_SECRET')

        if not all([cloud_name, api_key, api_secret]):
            print("❌ Error: Missing Cloudinary credentials")
            print("Please set these environment variables:")
            print("  - CLOUDINARY_CLOUD_NAME")
            print("  - CLOUDINARY_API_KEY")
            print("  - CLOUDINARY_API_SECRET")
            sys.exit(1)

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )

        print(f"✅ Cloudinary configured: {cloud_name}")

    def is_supabase_url(self, url):
        """Check if URL is from Supabase Storage"""
        if not url:
            return False
        parsed = urlparse(url)
        return 'supabase' in parsed.netloc.lower() or 'storage' in parsed.path.lower()

    def is_cloudinary_url(self, url):
        """Check if URL is already from Cloudinary"""
        if not url:
            return False
        return 'cloudinary.com' in url

    def download_image(self, url):
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"  ❌ Download failed: {str(e)}")
            return None

    def upload_to_cloudinary(self, image_data, public_id, folder):
        """Upload image to Cloudinary"""
        try:
            result = cloudinary.uploader.upload(
                image_data,
                folder=folder,
                public_id=public_id,
                overwrite=False,  # Don't overwrite if already exists
                resource_type='image',
                # Optimization settings
                quality='auto',
                fetch_format='auto',
            )
            return result['secure_url']
        except Exception as e:
            print(f"  ❌ Upload failed: {str(e)}")
            return None

    def migrate_product_image(self, product):
        """Migrate a single product's image"""
        self.stats['products_processed'] += 1

        # Check if migration needed
        if not product.image_url:
            print(f"  ⏭️  No image URL")
            self.stats['products_skipped'] += 1
            return False

        if self.is_cloudinary_url(product.image_url):
            print(f"  ⏭️  Already on Cloudinary")
            self.stats['products_skipped'] += 1
            return False

        if not self.is_supabase_url(product.image_url):
            print(f"  ⚠️  Unknown image host: {urlparse(product.image_url).netloc}")
            self.stats['products_skipped'] += 1
            return False

        # Download from Supabase
        print(f"  📥 Downloading from Supabase...")
        image_data = self.download_image(product.image_url)
        if not image_data:
            self.stats['products_failed'] += 1
            return False

        # Upload to Cloudinary
        print(f"  📤 Uploading to Cloudinary...")
        public_id = f"product_{product.id}_{datetime.now().strftime('%Y%m%d')}"
        new_url = self.upload_to_cloudinary(
            image_data,
            public_id=public_id,
            folder='linkfarm/products'
        )

        if not new_url:
            self.stats['products_failed'] += 1
            return False

        # Update database
        if not self.dry_run:
            old_url = product.image_url
            product.image_url = new_url
            db.session.commit()
            print(f"  ✅ Migrated!")
            print(f"     Old: {old_url[:60]}...")
            print(f"     New: {new_url[:60]}...")
        else:
            print(f"  🔍 [DRY RUN] Would update to: {new_url[:60]}...")

        self.stats['products_migrated'] += 1
        return True

    def migrate_farmer_image(self, farmer):
        """Migrate a single farmer's profile image"""
        self.stats['farmers_processed'] += 1

        # Check if migration needed
        if not farmer.profile_image_url:
            print(f"  ⏭️  No profile image")
            self.stats['farmers_skipped'] += 1
            return False

        if self.is_cloudinary_url(farmer.profile_image_url):
            print(f"  ⏭️  Already on Cloudinary")
            self.stats['farmers_skipped'] += 1
            return False

        if not self.is_supabase_url(farmer.profile_image_url):
            print(f"  ⚠️  Unknown image host: {urlparse(farmer.profile_image_url).netloc}")
            self.stats['farmers_skipped'] += 1
            return False

        # Download from Supabase
        print(f"  📥 Downloading from Supabase...")
        image_data = self.download_image(farmer.profile_image_url)
        if not image_data:
            self.stats['farmers_failed'] += 1
            return False

        # Upload to Cloudinary
        print(f"  📤 Uploading to Cloudinary...")
        public_id = f"farmer_{farmer.id}_{datetime.now().strftime('%Y%m%d')}"
        new_url = self.upload_to_cloudinary(
            image_data,
            public_id=public_id,
            folder='linkfarm/farmers'
        )

        if not new_url:
            self.stats['farmers_failed'] += 1
            return False

        # Update database
        if not self.dry_run:
            old_url = farmer.profile_image_url
            farmer.profile_image_url = new_url
            db.session.commit()
            print(f"  ✅ Migrated!")
            print(f"     Old: {old_url[:60]}...")
            print(f"     New: {new_url[:60]}...")
        else:
            print(f"  🔍 [DRY RUN] Would update to: {new_url[:60]}...")

        self.stats['farmers_migrated'] += 1
        return True

    def migrate_products(self):
        """Migrate all product images"""
        print("\n" + "="*60)
        print("🌾 MIGRATING PRODUCT IMAGES")
        print("="*60 + "\n")

        products = Product.query.all()
        print(f"Found {len(products)} products\n")

        for i, product in enumerate(products, 1):
            print(f"[{i}/{len(products)}] Product: {product.name} (ID: {product.id})")
            try:
                self.migrate_product_image(product)
            except Exception as e:
                print(f"  ❌ Unexpected error: {str(e)}")
                self.stats['products_failed'] += 1
            print()

    def migrate_farmers(self):
        """Migrate all farmer profile images"""
        print("\n" + "="*60)
        print("👨‍🌾 MIGRATING FARMER PROFILE IMAGES")
        print("="*60 + "\n")

        farmers = Farmer.query.all()
        print(f"Found {len(farmers)} farmers\n")

        for i, farmer in enumerate(farmers, 1):
            print(f"[{i}/{len(farmers)}] Farmer: {farmer.farm_name} (ID: {farmer.id})")
            try:
                self.migrate_farmer_image(farmer)
            except Exception as e:
                print(f"  ❌ Unexpected error: {str(e)}")
                self.stats['farmers_failed'] += 1
            print()

    def print_summary(self):
        """Print migration summary"""
        print("\n" + "="*60)
        print("📊 MIGRATION SUMMARY")
        print("="*60)

        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No changes were made to the database\n")

        print("\n📦 Products:")
        print(f"  Processed:  {self.stats['products_processed']}")
        print(f"  Migrated:   {self.stats['products_migrated']}")
        print(f"  Skipped:    {self.stats['products_skipped']}")
        print(f"  Failed:     {self.stats['products_failed']}")

        print("\n👤 Farmers:")
        print(f"  Processed:  {self.stats['farmers_processed']}")
        print(f"  Migrated:   {self.stats['farmers_migrated']}")
        print(f"  Skipped:    {self.stats['farmers_skipped']}")
        print(f"  Failed:     {self.stats['farmers_failed']}")

        total_migrated = self.stats['products_migrated'] + self.stats['farmers_migrated']
        total_failed = self.stats['products_failed'] + self.stats['farmers_failed']

        print("\n" + "="*60)
        print(f"✅ Total Migrated: {total_migrated}")
        print(f"❌ Total Failed:   {total_failed}")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Migrate images from Supabase Storage to Cloudinary',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be migrated (recommended first step)
  python scripts/migrate_images_to_cloudinary.py --dry-run

  # Migrate only products
  python scripts/migrate_images_to_cloudinary.py --products

  # Migrate only farmers
  python scripts/migrate_images_to_cloudinary.py --farmers

  # Migrate everything
  python scripts/migrate_images_to_cloudinary.py
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying database'
    )
    parser.add_argument(
        '--products',
        action='store_true',
        help='Migrate only product images'
    )
    parser.add_argument(
        '--farmers',
        action='store_true',
        help='Migrate only farmer profile images'
    )

    args = parser.parse_args()

    # Create Flask app context
    app = create_app()

    with app.app_context():
        migrator = ImageMigrator(dry_run=args.dry_run)

        print("\n" + "="*60)
        print("🖼️  IMAGE MIGRATION TOOL")
        print("="*60)
        print(f"Mode: {'🔍 DRY RUN' if args.dry_run else '✅ LIVE MIGRATION'}")
        print("="*60)

        # Determine what to migrate
        if args.products and not args.farmers:
            migrator.migrate_products()
        elif args.farmers and not args.products:
            migrator.migrate_farmers()
        else:
            # Default: migrate both
            migrator.migrate_products()
            migrator.migrate_farmers()

        # Print summary
        migrator.print_summary()

        if args.dry_run:
            print("💡 To perform actual migration, run without --dry-run flag\n")


if __name__ == '__main__':
    main()
