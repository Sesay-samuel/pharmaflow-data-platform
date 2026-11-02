
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id VARCHAR(20) PRIMARY KEY,
    medicine_name VARCHAR(150) NOT NULL,
    category VARCHAR(80) NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL
        CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS branches (
    branch_id VARCHAR(20) PRIMARY KEY,
    branch_name VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS retail_sales (
    sale_id VARCHAR(20) PRIMARY KEY,
    sale_date DATE NOT NULL,
    branch_id VARCHAR(20) NOT NULL
        REFERENCES branches(branch_id),
    medicine_id VARCHAR(20) NOT NULL
        REFERENCES medicines(medicine_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL
        CHECK (unit_price >= 0),
    total_amount NUMERIC(12, 2) NOT NULL
        CHECK (total_amount >= 0)
);

CREATE TABLE IF NOT EXISTS wholesale_orders (
    order_id VARCHAR(20) PRIMARY KEY,
    order_date DATE NOT NULL,
    supplier_id VARCHAR(20) NOT NULL
        REFERENCES suppliers(supplier_id),
    medicine_id VARCHAR(20) NOT NULL
        REFERENCES medicines(medicine_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_cost NUMERIC(12, 2) NOT NULL
        CHECK (unit_cost >= 0),
    total_cost NUMERIC(12, 2) NOT NULL
        CHECK (total_cost >= 0)
);

CREATE INDEX IF NOT EXISTS idx_retail_date
ON retail_sales(sale_date);

CREATE INDEX IF NOT EXISTS idx_retail_branch
ON retail_sales(branch_id);

CREATE INDEX IF NOT EXISTS idx_wholesale_date
ON wholesale_orders(order_date);
