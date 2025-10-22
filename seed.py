#!/usr/bin/env python3
"""
Seed script for LinkFarm database

This script populates the database with sample data for development and testing.
It creates:
- Sample users (farmers and customers)
- Farmer profiles
- Products for each farmer
- Sample inquiries from customers

Usage:
    python seed.py

Note: This script is idempotent - it checks for existing data before creating new records.
"""

import os
import sys
from datetime import datetime, timezone

# Add the current directory to the path so we can import our app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.user import User
from models.farmer import Farmer
from models.product import Product
from models.inquiry import Inquiry


def clear_database():
    """
    Clears all data from the database.
    WARNING: This will delete ALL data!
    """
    print("⚠️  Clearing all existing data...")

    # Delete in reverse order of foreign key dependencies
    Inquiry.query.delete()
    Product.query.delete()
    Farmer.query.delete()
    User.query.delete()

    db.session.commit()
    print("✅ Database cleared")


def create_users():
    """Creates sample users (farmers and customers)"""
    print("\n👥 Creating users...")

    users_data = [
        # Farmers
        {
            'username': 'green_valley_farm',
            'email': 'contact@greenvalley.com',
            'password': 'farmer123',
            'role': 'farmer'
        },
        {
            'username': 'sunrise_organics',
            'email': 'hello@sunriseorganics.com',
            'password': 'farmer123',
            'role': 'farmer'
        },
        {
            'username': 'fresh_harvest',
            'email': 'info@freshharvest.com',
            'password': 'farmer123',
            'role': 'farmer'
        },
        # Regular customers
        {
            'username': 'john_customer',
            'email': 'john@example.com',
            'password': 'customer123',
            'role': 'user'
        },
        {
            'username': 'sarah_buyer',
            'email': 'sarah@example.com',
            'password': 'customer123',
            'role': 'user'
        },
        # Admin user
        {
            'username': 'admin',
            'email': 'admin@linkfarm.com',
            'password': 'admin123',
            'role': 'admin'
        }
    ]

    created_users = {}

    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f"  ⏭️  User '{user_data['username']}' already exists, skipping")
            created_users[user_data['username']] = existing_user
            continue

        # Create new user
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            role=user_data['role']
        )
        user.set_password(user_data['password'])

        db.session.add(user)
        created_users[user_data['username']] = user
        print(f"  ✅ Created {user_data['role']}: {user_data['username']}")

    db.session.commit()
    return created_users


def create_farmers(users):
    """Creates farmer profiles for farmer users"""
    print("\n🌾 Creating farmer profiles...")

    farmers_data = [
        {
            'username': 'green_valley_farm',
            'name': 'Michael Green',
            'farm_name': 'Green Valley Farm',
            'location': 'Sonoma County, CA',
            'phone': '+1-555-0101',
            'bio': 'Family-owned organic farm since 1985. We specialize in seasonal vegetables and heritage tomatoes. All our produce is grown using sustainable farming practices.',
            'profile_image_url': 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400'
        },
        {
            'username': 'sunrise_organics',
            'name': 'Emma Rodriguez',
            'farm_name': 'Sunrise Organics',
            'location': 'Napa Valley, CA',
            'phone': '+1-555-0202',
            'bio': 'Certified organic farm focusing on leafy greens and herbs. We use permaculture principles and are committed to regenerative agriculture.',
            'profile_image_url': 'https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400'
        },
        {
            'username': 'fresh_harvest',
            'name': 'David Chen',
            'farm_name': 'Fresh Harvest',
            'location': 'Salinas Valley, CA',
            'phone': '+1-555-0303',
            'bio': 'Small-scale diversified farm growing a wide variety of vegetables, fruits, and flowers. We prioritize flavor and nutritional density.',
            'profile_image_url': 'https://images.unsplash.com/photo-1595273670150-bd0c3c392e46?w=400'
        }
    ]

    created_farmers = {}

    for farmer_data in farmers_data:
        user = users[farmer_data['username']]

        # Check if farmer profile already exists
        existing_farmer = Farmer.query.filter_by(user_id=user.id).first()
        if existing_farmer:
            print(f"  ⏭️  Farmer profile for '{farmer_data['farm_name']}' already exists, skipping")
            created_farmers[farmer_data['username']] = existing_farmer
            continue

        # Create farmer profile
        farmer = Farmer(
            user_id=user.id,
            name=farmer_data['name'],
            farm_name=farmer_data['farm_name'],
            location=farmer_data['location'],
            phone=farmer_data['phone'],
            bio=farmer_data['bio'],
            profile_image_url=farmer_data['profile_image_url']
        )

        db.session.add(farmer)
        created_farmers[farmer_data['username']] = farmer
        print(f"  ✅ Created farmer: {farmer_data['farm_name']}")

    db.session.commit()
    return created_farmers


def create_products(farmers):
    """Creates sample products for each farmer"""
    print("\n🥬 Creating products...")

    products_data = {
        'green_valley_farm': [
            {
                'name': 'Heirloom Tomatoes',
                'description': 'Mixed variety heirloom tomatoes - Cherokee Purple, Brandywine, and Green Zebra. Perfect for salads and sandwiches.',
                'price': '6.50',
                'unit': 'lb',
                'category': 'Vegetables',
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400'
            },
            {
                'name': 'Organic Lettuce Mix',
                'description': 'Fresh salad mix with red oak, green oak, and romaine lettuce. Harvested this morning!',
                'price': '4.00',
                'unit': 'bunch',
                'category': 'Vegetables',
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400'
            },
            {
                'name': 'Sweet Bell Peppers',
                'description': 'Colorful mix of red, yellow, and orange bell peppers. Crunchy and sweet!',
                'price': '5.00',
                'unit': 'lb',
                'category': 'Vegetables',
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400'
            }
        ],
        'sunrise_organics': [
            {
                'name': 'Baby Spinach',
                'description': 'Tender baby spinach leaves, perfect for salads or smoothies. Grown without pesticides.',
                'price': '3.50',
                'unit': 'bag',
                'category': 'Leafy Greens',
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400'
            },
            {
                'name': 'Fresh Basil',
                'description': 'Aromatic sweet basil - perfect for pesto, caprese salad, or pasta dishes.',
                'price': '2.50',
                'unit': 'bunch',
                'category': 'Herbs',
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1618375569909-3c8616cf7733?w=400'
            },
            {
                'name': 'Kale Variety Pack',
                'description': 'Mix of curly kale and lacinato (dinosaur) kale. Packed with nutrients!',
                'price': '4.50',
                'unit': 'bunch',
                'category': 'Leafy Greens',
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1515363578674-99a7d9777a43?w=400'
            },
            {
                'name': 'Arugula',
                'description': 'Peppery arugula leaves with a slight nutty flavor. Great in salads or on pizza.',
                'price': '3.00',
                'unit': 'bunch',
                'category': 'Leafy Greens',
                'is_available': False,  # Out of season
                'image_url': 'https://images.unsplash.com/photo-1550656643-d7e2b2e75e5e?w=400'
            }
        ],
        'fresh_harvest': [
            {
                'name': 'Strawberries',
                'description': 'Sweet, juicy strawberries picked at peak ripeness. Local and delicious!',
                'price': '7.00',
                'unit': 'pint',
                'category': 'Fruits',
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400'
            },
            {
                'name': 'Rainbow Carrots',
                'description': 'Colorful mix of orange, purple, yellow, and white carrots. Sweet and crunchy!',
                'price': '4.00',
                'unit': 'lb',
                'category': 'Vegetables',
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400'
            },
            {
                'name': 'Fresh Zucchini',
                'description': 'Tender zucchini perfect for grilling, sautéing, or baking into bread.',
                'price': '3.50',
                'unit': 'lb',
                'category': 'Vegetables',
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1567668310258-d1f7a4d5d5e0?w=400'
            },
            {
                'name': 'Cherry Tomatoes',
                'description': 'Sweet cherry tomatoes in red and yellow varieties. Perfect for snacking!',
                'price': '5.50',
                'unit': 'pint',
                'category': 'Vegetables',
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1592841200221-a6898f307baa?w=400'
            }
        ]
    }

    created_products = []

    for username, products in products_data.items():
        farmer = farmers[username]

        for product_data in products:
            # Check if product already exists
            existing_product = Product.query.filter_by(
                farmer_id=farmer.id,
                name=product_data['name']
            ).first()

            if existing_product:
                print(f"  ⏭️  Product '{product_data['name']}' already exists, skipping")
                created_products.append(existing_product)
                continue

            # Create product
            product = Product(
                farmer_id=farmer.id,
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                unit=product_data['unit'],
                category=product_data['category'],
                is_available=product_data['is_available'],
                image_url=product_data['image_url']
            )

            db.session.add(product)
            created_products.append(product)
            status = "✅" if product_data['is_available'] else "⏸️ "
            print(f"  {status} Created: {product_data['name']} ({farmer.farm_name})")

    db.session.commit()
    return created_products


def create_inquiries(users, farmers, products):
    """Creates sample customer inquiries"""
    print("\n💬 Creating inquiries...")

    inquiries_data = [
        {
            'farmer_username': 'green_valley_farm',
            'customer_username': 'john_customer',
            'product_name': 'Heirloom Tomatoes',
            'message': 'Hi! I\'m interested in your heirloom tomatoes. Do you have Cherokee Purple available this week? I need about 5 pounds.',
            'status': 'new'
        },
        {
            'farmer_username': 'green_valley_farm',
            'customer_username': 'sarah_buyer',
            'product_name': None,  # General inquiry
            'message': 'Hello! I\'m interested in buying produce weekly for my restaurant. Do you offer wholesale pricing for bulk orders?',
            'status': 'read'
        },
        {
            'farmer_username': 'sunrise_organics',
            'customer_username': 'john_customer',
            'product_name': 'Baby Spinach',
            'message': 'Is this spinach organic and pesticide-free? Also, when is the best time to pick up?',
            'status': 'responded'
        },
        {
            'farmer_username': 'fresh_harvest',
            'customer_username': 'sarah_buyer',
            'product_name': 'Strawberries',
            'message': 'These strawberries look amazing! Are they still available? I\'d like to order 3 pints.',
            'status': 'new'
        },
        {
            'farmer_username': 'fresh_harvest',
            'customer_username': 'john_customer',
            'product_name': 'Rainbow Carrots',
            'message': 'Do you have rainbow carrots with greens attached? I\'d love to use them for a recipe!',
            'status': 'read'
        }
    ]

    created_inquiries = []

    for inquiry_data in inquiries_data:
        farmer = farmers[inquiry_data['farmer_username']]
        customer = users[inquiry_data['customer_username']]

        # Find product if specified
        product = None
        if inquiry_data['product_name']:
            product = Product.query.filter_by(
                farmer_id=farmer.id,
                name=inquiry_data['product_name']
            ).first()

        # Check if similar inquiry already exists
        existing_inquiry = Inquiry.query.filter_by(
            farmer_id=farmer.id,
            customer_email=customer.email,
            message=inquiry_data['message']
        ).first()

        if existing_inquiry:
            print(f"  ⏭️  Similar inquiry already exists, skipping")
            created_inquiries.append(existing_inquiry)
            continue

        # Create inquiry
        inquiry = Inquiry(
            farmer_id=farmer.id,
            product_id=product.id if product else None,
            customer_name=customer.username,
            customer_email=customer.email,
            customer_phone='+1-555-9999',  # Sample phone
            message=inquiry_data['message'],
            status=inquiry_data['status']
        )

        db.session.add(inquiry)
        created_inquiries.append(inquiry)
        product_info = f" about {inquiry_data['product_name']}" if product else ""
        print(f"  ✅ Created inquiry to {farmer.farm_name}{product_info}")

    db.session.commit()
    return created_inquiries


def main():
    """Main function to seed the database"""
    print("🌱 LinkFarm Database Seeding")
    print("=" * 50)

    # Create Flask app and push context
    app = create_app()

    with app.app_context():
        # Ask for confirmation if we should clear existing data
        print("\nOptions:")
        print("1. Add seed data (keeps existing data)")
        print("2. Clear database and add seed data (DESTRUCTIVE)")
        choice = input("\nEnter your choice (1 or 2): ").strip()

        if choice == '2':
            confirm = input("⚠️  Are you sure you want to delete ALL data? Type 'yes' to confirm: ").strip()
            if confirm.lower() == 'yes':
                clear_database()
            else:
                print("❌ Aborted")
                return

        # Create all seed data
        users = create_users()
        farmers = create_farmers(users)
        products = create_products(farmers)
        inquiries = create_inquiries(users, farmers, products)

        print("\n" + "=" * 50)
        print("✅ Seeding complete!")
        print(f"\n📊 Summary:")
        print(f"  - Users: {len(users)}")
        print(f"  - Farmers: {len(farmers)}")
        print(f"  - Products: {len(products)}")
        print(f"  - Inquiries: {len(inquiries)}")

        print("\n🔐 Test Credentials:")
        print("  Farmer accounts:")
        print("    - green_valley_farm / farmer123")
        print("    - sunrise_organics / farmer123")
        print("    - fresh_harvest / farmer123")
        print("  Customer accounts:")
        print("    - john_customer / customer123")
        print("    - sarah_buyer / customer123")
        print("  Admin account:")
        print("    - admin / admin123")
        print("\n🎉 You can now login and test the platform!")


if __name__ == '__main__':
    main()
