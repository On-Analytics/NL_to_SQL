-- E-commerce Schema for Testing

-- Cleanup
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    country TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Products Table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Orders Table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    status TEXT NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Order Items Table
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);

-- Seed Data
INSERT INTO users (name, email, country, created_at) VALUES
('Juan Perez', 'juan@example.com', 'Colombia', '2025-01-10 10:00:00+00'),
('Maria Rodriguez', 'maria@example.com', 'Colombia', '2025-01-15 11:30:00+00'),
('John Doe', 'john@example.com', 'USA', '2025-02-01 09:00:00+00'),
('Jane Smith', 'jane@example.com', 'UK', '2025-02-05 14:20:00+00'),
('Carlos Gomez', 'carlos@example.com', 'Colombia', '2025-02-10 16:45:00+00');

INSERT INTO products (name, category, price) VALUES
('Smartphone Alpha', 'Electronics', 599.99),
('Wireless Headphones', 'Electronics', 149.50),
('Coffee Maker Pro', 'Home', 89.00),
('Ergonomic Chair', 'Furniture', 250.00),
('Gaming Mouse', 'Electronics', 59.99);

-- Helper to get IDs (simulating a real seed process)
DO $$
DECLARE
    user_juan UUID;
    user_john UUID;
    prod_phone UUID;
    prod_headphones UUID;
    order_1 UUID;
BEGIN
    SELECT id INTO user_juan FROM users WHERE email = 'juan@example.com';
    SELECT id INTO user_john FROM users WHERE email = 'john@example.com';
    SELECT id INTO prod_phone FROM products WHERE name = 'Smartphone Alpha';
    SELECT id INTO prod_headphones FROM products WHERE name = 'Wireless Headphones';

    -- Order 1: Juan buys a phone
    INSERT INTO orders (user_id, status, total_amount, created_at) 
    VALUES (user_juan, 'completed', 599.99, '2025-01-20 15:00:00+00') RETURNING id INTO order_1;
    INSERT INTO order_items (order_id, product_id, quantity, unit_price) 
    VALUES (order_1, prod_phone, 1, 599.99);

    -- Order 2: John buys headphones
    INSERT INTO orders (user_id, status, total_amount, created_at) 
    VALUES (user_john, 'completed', 149.50, '2025-02-12 10:00:00+00') RETURNING id INTO order_1;
    INSERT INTO order_items (order_id, product_id, quantity, unit_price) 
    VALUES (order_1, prod_headphones, 1, 149.50);
END $$;
