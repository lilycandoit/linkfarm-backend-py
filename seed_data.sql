-- ============================================================
-- LinkFarm Seed Data Script for Supabase
-- ============================================================
-- This script creates sample data for testing your deployed app
-- Run this in Supabase SQL Editor: https://app.supabase.com
--
-- What this creates:
-- - 1 test farmer user (email: farmer@linkfarm.demo)
-- - 1 farmer profile (Green Valley Farm)
-- - 6 sample products (vegetables, fruits, honey)
-- ============================================================

-- Step 1: Create a test farmer user
-- Password is hashed with bcrypt: "farmer123"
INSERT INTO users (id, username, email, password_hash, role, created_at, updated_at)
VALUES (
  gen_random_uuid()::text,
  'greenvalley_farmer',
  'farmer@linkfarm.demo',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYPOKK6M.ne',
  'farmer',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO NOTHING;

-- Step 2: Create farmer profile for the test user
INSERT INTO farmers (id, user_id, name, farm_name, location, phone, bio, profile_image_url, created_at, updated_at)
SELECT
  gen_random_uuid()::text,
  u.id,
  'Nguyen Van A',
  'Green Valley Organic Farm',
  'Hanoi, Vietnam',
  '+84 123 456 789',
  'Family-owned organic farm specializing in fresh vegetables, fruits, and natural products. We practice sustainable farming and deliver fresh produce daily.',
  'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400',
  NOW(),
  NOW()
FROM users u
WHERE u.email = 'farmer@linkfarm.demo'
ON CONFLICT DO NOTHING;

-- Step 3: Create sample products
-- Get the farmer_id from the farmer we just created
WITH farmer_info AS (
  SELECT f.id as farmer_id
  FROM farmers f
  JOIN users u ON f.user_id = u.id
  WHERE u.email = 'farmer@linkfarm.demo'
  LIMIT 1
)
INSERT INTO products (id, farmer_id, name, description, price, unit, category, stock_quantity, image_url, is_available, created_at, updated_at)
SELECT
  gen_random_uuid()::text,
  farmer_id,
  'Fresh Organic Tomatoes',
  'Vine-ripened, juicy tomatoes grown without pesticides. Perfect for salads and cooking.',
  2.50,
  'kg',
  'Vegetables',
  100,
  'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400',
  true,
  NOW(),
  NOW()
FROM farmer_info
UNION ALL
SELECT
  gen_random_uuid()::text,
  farmer_id,
  'Sweet Carrots',
  'Crunchy orange carrots harvested fresh daily. Rich in vitamins and perfect for salads.',
  1.80,
  'kg',
  'Vegetables',
  80,
  'https://images.unsplash.com/photo-1447175008436-054170c2e979?w=400',
  true,
  NOW(),
  NOW()
FROM farmer_info
UNION ALL
SELECT
  gen_random_uuid()::text,
  farmer_id,
  'Fresh Green Lettuce',
  'Crisp, fresh lettuce harvested every morning. Organically grown without chemicals.',
  1.20,
  'head',
  'Vegetables',
  50,
  'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400',
  true,
  NOW(),
  NOW()
FROM farmer_info
UNION ALL
SELECT
  gen_random_uuid()::text,
  farmer_id,
  'Organic Honey',
  'Pure wildflower honey harvested from our farm. Natural sweetener with amazing health benefits.',
  8.50,
  'jar (500g)',
  'Products',
  30,
  'https://images.unsplash.com/photo-1587049352846-4a222e784fbb?w=400',
  true,
  NOW(),
  NOW()
FROM farmer_info
UNION ALL
SELECT
  gen_random_uuid()::text,
  farmer_id,
  'Fresh Strawberries',
  'Sweet, juicy strawberries grown in our greenhouse. Perfect for desserts and snacking.',
  4.20,
  'kg',
  'Fruits',
  40,
  'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400',
  true,
  NOW(),
  NOW()
FROM farmer_info
UNION ALL
SELECT
  gen_random_uuid()::text,
  farmer_id,
  'Baby Spinach',
  'Tender baby spinach leaves, rich in iron and nutrients. Great for smoothies and salads.',
  2.00,
  'bunch',
  'Vegetables',
  60,
  'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400',
  true,
  NOW(),
  NOW()
FROM farmer_info;

-- Step 4: Verify the data was inserted successfully
SELECT
  'Data inserted successfully!' as message,
  COUNT(*) as total_products,
  u.email as farmer_email,
  f.farm_name
FROM products p
JOIN farmers f ON p.farmer_id = f.id
JOIN users u ON f.user_id = u.id
WHERE u.email = 'farmer@linkfarm.demo'
GROUP BY u.email, f.farm_name;

-- ============================================================
-- OPTIONAL: View all inserted data
-- ============================================================
-- Uncomment the queries below to see the inserted data

-- View farmer details
-- SELECT id, username, email, role, created_at
-- FROM users
-- WHERE email = 'farmer@linkfarm.demo';

-- View farm profile
-- SELECT f.name, f.farm_name, f.location, f.phone, f.bio, u.email
-- FROM farmers f
-- JOIN users u ON f.user_id = u.id
-- WHERE u.email = 'farmer@linkfarm.demo';

-- View all products
-- SELECT
--   p.name,
--   p.price,
--   p.unit,
--   p.category,
--   p.stock_quantity,
--   f.farm_name
-- FROM products p
-- JOIN farmers f ON p.farmer_id = f.id
-- JOIN users u ON f.user_id = u.id
-- WHERE u.email = 'farmer@linkfarm.demo'
-- ORDER BY p.created_at DESC;

-- ============================================================
-- TEST LOGIN CREDENTIALS
-- ============================================================
-- Email: farmer@linkfarm.demo
-- Password: farmer123
--
-- Use these credentials to login to your app and manage products!
-- ============================================================
