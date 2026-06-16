import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "zepto_v2.csv"
ASSETS_DIR = ROOT / "assets"


def money(value):
    return f"₹{value:,.0f}"


def pct(value):
    return f"{value:.1f}%"


def load_rows():
    rows = []
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            mrp = float(row["mrp"]) / 100
            selling_price = float(row["discountedSellingPrice"]) / 100
            if mrp == 0:
                continue
            rows.append(
                {
                    "category": row["Category"],
                    "name": row["name"],
                    "mrp": mrp,
                    "discount": float(row["discountPercent"]),
                    "quantity": int(row["availableQuantity"]),
                    "selling_price": selling_price,
                    "weight": int(row["weightInGms"]),
                    "out_of_stock": row["outOfStock"].strip().upper() == "TRUE",
                }
            )
    return rows


def top_items(items, key, limit=8, reverse=True):
    return sorted(items, key=key, reverse=reverse)[:limit]


def bar_rows(rows, label_key, value_key, formatter, color="#7c3aed"):
    max_value = max(row[value_key] for row in rows) or 1
    output = []
    for row in rows:
        width = max(6, row[value_key] / max_value * 100)
        output.append(
            f"""
            <div class="bar-row">
              <div class="bar-label">{row[label_key]}</div>
              <div class="bar-track"><span style="width:{width:.2f}%; background:{color};"></span></div>
              <div class="bar-value">{formatter(row[value_key])}</div>
            </div>
            """
        )
    return "\n".join(output)


def table_rows(rows, columns):
    output = []
    for row in rows:
        cells = "".join(f"<td>{formatter(row[key]) if formatter else row[key]}</td>" for key, _, formatter in columns)
        output.append(f"<tr>{cells}</tr>")
    return "\n".join(output)


def page_shell(title, eyebrow, body):
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      width: 1440px;
      min-height: 900px;
      font-family: Inter, Segoe UI, Arial, sans-serif;
      color: #111827;
      background:
        radial-gradient(circle at top right, rgba(124, 58, 237, 0.18), transparent 30%),
        linear-gradient(135deg, #faf7f0 0%, #ffffff 48%, #f5f3ff 100%);
      padding: 54px;
    }}
    .frame {{
      min-height: 792px;
      border: 1px solid rgba(17, 24, 39, 0.08);
      border-radius: 38px;
      background: rgba(255, 255, 255, 0.86);
      box-shadow: 0 32px 90px rgba(17, 24, 39, 0.14);
      overflow: hidden;
    }}
    .hero {{
      padding: 42px 46px 28px;
      background: #121826;
      color: #fff;
    }}
    .eyebrow {{
      color: #a78bfa;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.22em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 12px 0 0;
      font-size: 48px;
      letter-spacing: -0.04em;
    }}
    .content {{ padding: 34px 40px 42px; }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 18px;
      margin-bottom: 28px;
    }}
    .card {{
      border: 1px solid #eceef4;
      border-radius: 24px;
      padding: 22px;
      background: #fff;
      box-shadow: 0 18px 40px rgba(17, 24, 39, 0.07);
    }}
    .card small {{
      display: block;
      color: #6b7280;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-size: 11px;
    }}
    .card strong {{
      display: block;
      margin-top: 10px;
      font-size: 32px;
      letter-spacing: -0.04em;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 22px;
    }}
    h2 {{
      margin: 0 0 18px;
      font-size: 22px;
      letter-spacing: -0.02em;
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: 210px 1fr 110px;
      gap: 16px;
      align-items: center;
      margin: 14px 0;
      font-size: 14px;
      font-weight: 700;
    }}
    .bar-label {{
      color: #374151;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .bar-track {{
      height: 13px;
      border-radius: 999px;
      background: #ede9fe;
      overflow: hidden;
    }}
    .bar-track span {{
      display: block;
      height: 100%;
      border-radius: 999px;
    }}
    .bar-value {{ text-align: right; color: #111827; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th {{
      text-align: left;
      color: #6b7280;
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 0 10px 12px;
    }}
    td {{
      border-top: 1px solid #eef0f5;
      padding: 12px 10px;
      font-weight: 700;
    }}
    td:last-child, th:last-child {{ text-align: right; }}
    .note {{
      margin-top: 22px;
      color: #6b7280;
      font-size: 13px;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <div class="frame">
    <section class="hero">
      <div class="eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
    </section>
    <main class="content">{body}</main>
  </div>
</body>
</html>"""


def main():
    rows = load_rows()
    ASSETS_DIR.mkdir(exist_ok=True)

    categories = sorted({row["category"] for row in rows})
    available = sum(1 for row in rows if not row["out_of_stock"])
    out_of_stock = len(rows) - available
    revenue = sum(row["selling_price"] * row["quantity"] for row in rows)
    avg_discount = sum(row["discount"] for row in rows) / len(rows)

    revenue_by_category = defaultdict(float)
    discount_by_category = defaultdict(list)
    stock_by_category = Counter()
    for row in rows:
        revenue_by_category[row["category"]] += row["selling_price"] * row["quantity"]
        discount_by_category[row["category"]].append(row["discount"])
        if row["out_of_stock"]:
            stock_by_category[row["category"]] += 1

    revenue_rows = [
        {"category": category, "revenue": value}
        for category, value in revenue_by_category.items()
    ]
    revenue_rows = top_items(revenue_rows, lambda row: row["revenue"], 8)

    discount_rows = [
        {"category": category, "discount": sum(values) / len(values)}
        for category, values in discount_by_category.items()
    ]
    discount_rows = top_items(discount_rows, lambda row: row["discount"], 8)

    dashboard_body = f"""
      <div class="kpis">
        <div class="card"><small>Clean SKUs</small><strong>{len(rows):,}</strong></div>
        <div class="card"><small>Categories</small><strong>{len(categories)}</strong></div>
        <div class="card"><small>In Stock</small><strong>{available:,}</strong></div>
        <div class="card"><small>Estimated Revenue</small><strong>{money(revenue)}</strong></div>
      </div>
      <div class="grid">
        <section class="card">
          <h2>Top Categories by Estimated Revenue</h2>
          {bar_rows(revenue_rows, "category", "revenue", money, "#6d28d9")}
        </section>
        <section class="card">
          <h2>Highest Average Discount Categories</h2>
          {bar_rows(discount_rows, "category", "discount", pct, "#f97316")}
        </section>
      </div>
      <p class="note">Based on cleaned Zepto SKU data after removing zero-MRP rows and converting paise to rupees.</p>
    """

    best_value = [
        {
            "name": row["name"],
            "category": row["category"],
            "discount": row["discount"],
            "price": row["selling_price"],
        }
        for row in top_items(rows, lambda row: row["discount"], 8)
    ]
    stock_rows = [
        {"category": category, "out": count}
        for category, count in stock_by_category.items()
    ]
    stock_rows = top_items(stock_rows, lambda row: row["out"], 8)

    insights_body = f"""
      <div class="kpis">
        <div class="card"><small>Out of Stock</small><strong>{out_of_stock:,}</strong></div>
        <div class="card"><small>Avg Discount</small><strong>{pct(avg_discount)}</strong></div>
        <div class="card"><small>Highest Discount</small><strong>{pct(max(row["discount"] for row in rows))}</strong></div>
        <div class="card"><small>Max MRP</small><strong>{money(max(row["mrp"] for row in rows))}</strong></div>
      </div>
      <div class="grid">
        <section class="card">
          <h2>Top Discounted SKUs</h2>
          <table>
            <thead><tr><th>Product</th><th>Category</th><th>Discount</th></tr></thead>
            <tbody>
              {table_rows(best_value, [("name", "Product", None), ("category", "Category", None), ("discount", "Discount", pct)])}
            </tbody>
          </table>
        </section>
        <section class="card">
          <h2>Out-of-Stock Pressure by Category</h2>
          {bar_rows(stock_rows, "category", "out", lambda value: f"{int(value)} SKUs", "#dc2626")}
        </section>
      </div>
      <p class="note">The SQL project answers inventory, pricing, discounting, stockout, and value-for-money questions.</p>
    """

    (ASSETS_DIR / "zepto-inventory-dashboard.html").write_text(
        page_shell("Zepto Inventory Intelligence", "SQL analytics dashboard", dashboard_body),
        encoding="utf-8",
    )
    (ASSETS_DIR / "zepto-sql-insights.html").write_text(
        page_shell("Business Questions in Action", "Query output snapshot", insights_body),
        encoding="utf-8",
    )

    print(f"Rows analyzed: {len(rows):,}")
    print(f"Categories: {len(categories)}")
    print(f"In stock: {available:,}")
    print(f"Out of stock: {out_of_stock:,}")
    print(f"Estimated revenue: INR {revenue:,.0f}")
    print(f"Average discount: {pct(avg_discount)}")


if __name__ == "__main__":
    main()
