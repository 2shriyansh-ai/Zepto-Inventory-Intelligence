# 📦 Zepto Inventory Intelligence — SQL Data Analysis Project

A real-world SQL data analytics project built on an e-commerce inventory dataset scraped from **Zepto** — one of India’s fastest-growing quick-commerce startups.

This project simulates end-to-end analyst workflows:
- Raw data exploration  
- Data cleaning  
- Generating actionable business insights using PostgreSQL  

---

## ❓ Business Questions Answered

- Which product categories generate the highest estimated revenue?
- Which products offer the highest discounts, and are they actually in stock?
- How many products are currently out of stock vs available?
- Which high-MRP products have poor discount rates?
- What is the average discount percentage per category?
- Which products offer the best value for money (price per gram)?

---

## 🗂️ Dataset

| Field  | Details |
|--------|---------|
| **Source** | [Kaggle — Zepto Inventory Dataset](https://www.kaggle.com/datasets/palvinder2006/zepto-inventory-dataset/data?select=zepto_v2.csv) |
| **File**   | zepto_v2.csv |
| **Rows**   | ~3,700+ SKUs |
| **Grain**  | One row = one SKU (Stock Keeping Unit) |

---

## 🧱 Schema

```sql
CREATE TABLE zepto (
    sku_id                 SERIAL PRIMARY KEY,
    category               VARCHAR(120),
    name                   VARCHAR(150) NOT NULL,
    mrp                    NUMERIC(8,2),
    discountPercent        NUMERIC(5,2),
    availableQuantity      INTEGER,
    discountedSellingPrice NUMERIC(8,2),
    weightInGms            INTEGER,
    outOfStock             BOOLEAN,
    quantity               INTEGER
);

## 🔄 Project Workflow

Raw CSV Data
    ↓
Database Setup (pgAdmin + Table Creation)
    ↓
Data Exploration (EDA)
    ↓
Data Cleaning
    ↓
Business Analysis
    ↓
Insights & Findings
