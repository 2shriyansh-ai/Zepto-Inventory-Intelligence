

📁 Dataset
## 🗂️ Dataset

| Field  | Details |
|--------|---------|
| **Source** | [Kaggle — Zepto Inventory Dataset](https://www.kaggle.com/datasets/palvinder2006/zepto-inventory-dataset/data?select=zepto_v2.csv) |
| **File**   | zepto_v2.csv |
| **Rows**   | ~3,700+ SKUs |
| **Grain**  | One row = one SKU (Stock Keeping Unit) |


 ## Schema

```sql
CREATE TABLE zepto (
    sku_id SERIAL PRIMARY KEY,
    category VARCHAR(120),
    name VARCHAR(150) NOT NULL,
    mrp NUMERIC(8,2),
    discountPercent NUMERIC(5,2),
    availableQuantity INTEGER,
    discountedSellingPrice NUMERIC(8,2),
    weightInGms INTEGER,
    outOfStock BOOLEAN,
    quantity INTEGER
);
```
Note: Duplicate product names exist intentionally — the same product may appear multiple times with different weights, packaging sizes, or discount schemes, mirroring real catalog data.


