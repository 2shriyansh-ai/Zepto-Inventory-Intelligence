from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).parent
DATA_PATH = ROOT / "zepto_v2.csv"


st.set_page_config(
    page_title="Zepto Inventory Intelligence",
    page_icon=":shopping_trolley:",
    layout="wide",
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    df.columns = [column.strip() for column in df.columns]

    numeric_columns = [
        "mrp",
        "discountPercent",
        "availableQuantity",
        "discountedSellingPrice",
        "weightInGms",
        "quantity",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["Category", "name", "mrp", "discountedSellingPrice"])
    df = df[df["mrp"] > 0].copy()

    df["mrp_rupees"] = df["mrp"] / 100
    df["selling_price_rupees"] = df["discountedSellingPrice"] / 100
    df["estimated_revenue"] = df["selling_price_rupees"] * df["availableQuantity"]
    df["price_per_gram"] = df["selling_price_rupees"] / df["weightInGms"].replace(0, pd.NA)
    df["stock_status"] = df["outOfStock"].map({True: "Out of stock", False: "In stock"})
    return df


def format_money(value):
    if value >= 100000:
        return f"₹{value / 100000:.2f}L"
    return f"₹{value:,.0f}"


df = load_data()

st.title("Zepto Inventory Intelligence")
st.caption("SQL-style inventory analytics for quick-commerce pricing, discounts, stockouts, and category performance.")

with st.sidebar:
    st.header("Filters")
    categories = st.multiselect(
        "Category",
        options=sorted(df["Category"].unique()),
        default=sorted(df["Category"].unique()),
    )
    stock_filter = st.radio("Stock status", ["All", "In stock", "Out of stock"])
    min_discount = st.slider("Minimum discount %", 0, int(df["discountPercent"].max()), 0)

filtered = df[df["Category"].isin(categories)].copy()
if stock_filter != "All":
    filtered = filtered[filtered["stock_status"] == stock_filter]
filtered = filtered[filtered["discountPercent"] >= min_discount]

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
kpi_1.metric("SKUs analyzed", f"{len(filtered):,}")
kpi_2.metric("Categories", f"{filtered['Category'].nunique():,}")
kpi_3.metric("Out of stock", f"{int(filtered['outOfStock'].sum()):,}")
kpi_4.metric("Estimated revenue", format_money(filtered["estimated_revenue"].sum()))

st.divider()

left, right = st.columns(2)

category_revenue = (
    filtered.groupby("Category", as_index=False)["estimated_revenue"]
    .sum()
    .sort_values("estimated_revenue", ascending=False)
    .head(10)
)
fig_revenue = px.bar(
    category_revenue,
    x="estimated_revenue",
    y="Category",
    orientation="h",
    title="Top Categories by Estimated Revenue",
    labels={"estimated_revenue": "Estimated revenue (₹)", "Category": ""},
    color_discrete_sequence=["#6d28d9"],
)
fig_revenue.update_layout(yaxis={"categoryorder": "total ascending"}, height=430)
left.plotly_chart(fig_revenue, use_container_width=True)

category_discount = (
    filtered.groupby("Category", as_index=False)["discountPercent"]
    .mean()
    .sort_values("discountPercent", ascending=False)
    .head(10)
)
fig_discount = px.bar(
    category_discount,
    x="discountPercent",
    y="Category",
    orientation="h",
    title="Highest Average Discount Categories",
    labels={"discountPercent": "Average discount %", "Category": ""},
    color_discrete_sequence=["#f97316"],
)
fig_discount.update_layout(yaxis={"categoryorder": "total ascending"}, height=430)
right.plotly_chart(fig_discount, use_container_width=True)

left, right = st.columns(2)

stock_pressure = (
    filtered[filtered["outOfStock"]]
    .groupby("Category", as_index=False)
    .size()
    .rename(columns={"size": "out_of_stock_skus"})
    .sort_values("out_of_stock_skus", ascending=False)
    .head(10)
)
fig_stock = px.bar(
    stock_pressure,
    x="out_of_stock_skus",
    y="Category",
    orientation="h",
    title="Out-of-Stock Pressure",
    labels={"out_of_stock_skus": "Out-of-stock SKUs", "Category": ""},
    color_discrete_sequence=["#dc2626"],
)
fig_stock.update_layout(yaxis={"categoryorder": "total ascending"}, height=430)
left.plotly_chart(fig_stock, use_container_width=True)

value_products = (
    filtered[filtered["weightInGms"] >= 100]
    .dropna(subset=["price_per_gram"])
    .sort_values("price_per_gram")
    .head(15)
)
right.subheader("Best Value Products")
right.dataframe(
    value_products[
        [
            "Category",
            "name",
            "selling_price_rupees",
            "weightInGms",
            "price_per_gram",
            "discountPercent",
        ]
    ].rename(
        columns={
            "Category": "Category",
            "name": "Product",
            "selling_price_rupees": "Selling Price",
            "weightInGms": "Weight (g)",
            "price_per_gram": "₹ / gram",
            "discountPercent": "Discount %",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.subheader("SKU Explorer")
st.dataframe(
    filtered[
        [
            "Category",
            "name",
            "mrp_rupees",
            "discountPercent",
            "selling_price_rupees",
            "availableQuantity",
            "stock_status",
        ]
    ].rename(
        columns={
            "Category": "Category",
            "name": "Product",
            "mrp_rupees": "MRP",
            "discountPercent": "Discount %",
            "selling_price_rupees": "Selling Price",
            "availableQuantity": "Available Qty",
            "stock_status": "Stock Status",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.caption("Note: estimated revenue is calculated as discounted selling price × available quantity. It is not actual sales revenue.")
