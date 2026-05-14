--
-- MySQL schema definition for the Coupon System
--
-- This file contains the SQL statements to create all tables
-- for the coupon management system as described in the project proposal.
--
-- Tables include:
-- 1. users - Stores user account information
-- 2. products - Stores product inventory and pricing
-- 3. coupons - Stores coupon configuration and discount details
-- 4. coupon_schedules - Stores time-based activation windows for coupons
-- 5. usage_logs - Tracks coupon usage history for audit and limit enforcement
--
-- Each table includes appropriate columns, data types, constraints,
-- and relationships as specified in the database design.
--
-- Indexes are defined on frequently queried columns for O(1) lookup performance.
-- Foreign key constraints ensure referential integrity between tables.


DROP TABLE IF EXISTS usage_logs;
DROP TABLE IF EXISTS coupon_schedules;
DROP TABLE IF EXISTS coupons;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    telegram_chat_id BIGINT UNIQUE,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE coupons (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(255) NOT NULL UNIQUE,
    visibility ENUM('PUBLIC', 'PRIVATE') NOT NULL DEFAULT 'PRIVATE',
    discount_type ENUM('FIXED', 'PERCENT') NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL,
    max_discount_amount DECIMAL(10, 2) NULL,
    min_order_value DECIMAL(10, 2) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE coupon_schedules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    coupon_id INT NOT NULL, 
    start_time DATETIME NOT NULL, 
    end_time DATETIME NOT NULL, 
    create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE usage_logs (
    id INT PRIMARY KEY AUTO_INCREMENT, 
    coupon_id INT NOT NULL, 
    user_id INT NOT NULL, 
    product_id INT NULL,
    order_value DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) NOT NULL,
    final_price DECIMAL(10, 2) NOT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Indexes 
CREATE INDEX idx_coupons_code ON coupons(code);
CREATE INDEX idx_coupons_visibility ON coupons(visibility);
CREATE INDEX idx_coupon_schedules_coupon_id ON coupon_schedules(coupon_id);
CREATE INDEX idx_coupon_schedules_time ON coupon_schedules(start_time, end_time);
CREATE INDEX idx_usage_logs_coupon_id ON usage_logs(coupon_id);
CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_logs_used_at ON usage_logs(used_at);