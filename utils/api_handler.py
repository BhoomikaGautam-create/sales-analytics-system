import requests

BASE_URL = "https://dummyjson.com/products"

def get_all_products(limit=30):
    """
    Fetches all products (default 30, can set limit).
    Returns: list of product dictionaries
    """
    response = requests.get(f"{BASE_URL}?limit={limit}")
    data = response.json()
    return data.get("products", [])


def get_product_by_id(product_id):
    """
    Fetches a single product by ID.
    Returns: product dictionary
    """
    response = requests.get(f"{BASE_URL}/{product_id}")
    return response.json()


def search_products(query, limit=30):
    """
    Searches products by keyword.
    Returns: list of product dictionaries
    """
    response = requests.get(f"{BASE_URL}/search?q={query}&limit={limit}")
    data = response.json()
    return data.get("products", [])

import requests

BASE_URL = "https://dummyjson.com/products"

def fetch_all_products():
    """
    Fetches all products from DummyJSON API

    Returns: list of product dictionaries
    """
    try:
        response = requests.get(f"{BASE_URL}?limit=100")
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])

        cleaned_products = []
        for p in products:
            cleaned_products.append({
                "id": p.get("id"),
                "title": p.get("title"),
                "category": p.get("category"),
                "brand": p.get("brand", "Unknown"),   # safe fallback
                "price": p.get("price"),
                "rating": p.get("rating"),
            })

        print(f"✅ Successfully fetched {len(cleaned_products)} products")
        return cleaned_products

    except Exception as e:
        print(f"❌ Failed to fetch products: {e}")
        return []
    
def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info
    Parameters: api_products from fetch_all_products()

    Returns: dictionary mapping product IDs to info
    """
    product_map = {
        p["id"]: {
            "title": p.get("title"),
            "category": p.get("category"),
            "brand": p.get("brand", "Unknown"),
            "rating": p.get("rating"),
        }
        for p in api_products if p.get("id") is not None
    }

    print(f"✅ Created product mapping for {len(product_map)} products")
    return product_map

import re

def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information

    Parameters:
    - transactions: list of transaction dictionaries
    - product_mapping: dictionary from create_product_mapping()

    Returns: list of enriched transaction dictionaries
    """
    enriched = []

    for tx in transactions:
        try:
            # Extract numeric ID from ProductID (e.g., P101 -> 101)
            match = re.search(r'\d+', tx.get("ProductID", ""))
            product_id = int(match.group()) if match else None

            if product_id and product_id in product_mapping:
                api_info = product_mapping[product_id]
                tx["API_Category"] = api_info.get("category")
                tx["API_Brand"] = api_info.get("brand")
                tx["API_Rating"] = api_info.get("rating")
                tx["API_Match"] = True
            else:
                tx["API_Category"] = None
                tx["API_Brand"] = None
                tx["API_Rating"] = None
                tx["API_Match"] = False

            enriched.append(tx)

        except Exception as e:
            # Graceful error handling
            tx["API_Category"] = None
            tx["API_Brand"] = None
            tx["API_Rating"] = None
            tx["API_Match"] = False
            enriched.append(tx)
            print(f"⚠️ Error enriching transaction {tx.get('TransactionID')}: {e}")

    # Save enriched data to file
    save_enriched_data(enriched, filename="data/enriched_sales_data.txt")

    print(f"✅ Enriched {len(enriched)} transactions and saved to data/enriched_sales_data.txt")
    return enriched


def save_enriched_data(enriched_transactions, filename="data/enriched_sales_data.txt"):
    """
    Saves enriched transactions back to file in pipe-delimited format
    """
    # Define header with new fields
    header = [
        "TransactionID", "Date", "ProductID", "ProductName", "Quantity",
        "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    try:
        with open(filename, "w", encoding="utf-8") as f:
            # Write header
            f.write("|".join(header) + "\n")

            # Write each transaction
            for tx in enriched_transactions:
                row = [
                    str(tx.get("TransactionID", "")),
                    str(tx.get("Date", "")),
                    str(tx.get("ProductID", "")),
                    str(tx.get("ProductName", "")),
                    str(tx.get("Quantity", "")),
                    str(tx.get("UnitPrice", "")),
                    str(tx.get("CustomerID", "")),
                    str(tx.get("Region", "")),
                    str(tx.get("API_Category", "")) if tx.get("API_Category") is not None else "",
                    str(tx.get("API_Brand", "")) if tx.get("API_Brand") is not None else "",
                    str(tx.get("API_Rating", "")) if tx.get("API_Rating") is not None else "",
                    str(tx.get("API_Match", "")),
                ]
                f.write("|".join(row) + "\n")

        print(f"✅ Enriched data saved to {filename}")

    except Exception as e:
        print(f"❌ Failed to save enriched data: {e}")

import re
import os

def save_enriched_data(enriched, filename="data/enriched_sales_data.txt"):
    """Save enriched transactions to a pipe-delimited file with new API columns."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    header = [
        "TransactionID", "Date", "ProductID", "ProductName",
        "Quantity", "UnitPrice", "CustomerID", "Region",
        "API_Category", "API_Brand", "API_Rating", "API_Match"
    ]

    with open(filename, "w", encoding="utf-8") as f:
        f.write("|".join(header) + "\n")
        for tx in enriched:
            row = [
                str(tx.get("TransactionID", "")),
                str(tx.get("Date", "")),
                str(tx.get("ProductID", "")),
                str(tx.get("ProductName", "")),
                str(tx.get("Quantity", "")),
                str(tx.get("UnitPrice", "")),
                str(tx.get("CustomerID", "")),
                str(tx.get("Region", "")),
                str(tx.get("API_Category", "")),
                str(tx.get("API_Brand", "")),
                str(tx.get("API_Rating", "")),
                str(tx.get("API_Match", ""))
            ]
            f.write("|".join(row) + "\n")


def enrich_sales_data(transactions, product_mapping):
    """
    Partial enrichment:
    - Extract numeric ID from ProductID (P101 → 101).
    - If ID exists in product_mapping, add API fields.
    - If ID doesn't exist, leave API fields as None and API_Match=False.
    - Save enriched data to 'data/enriched_sales_data.txt'.
    """
    enriched = []

    for tx in transactions:
        try:
            # Extract numeric ID
            match = re.search(r'\d+', tx.get("ProductID", ""))
            product_id = int(match.group()) if match else None

            if product_id and product_id in product_mapping:
                # ✅ Enrich with API data
                api_info = product_mapping[product_id]
                tx["API_Category"] = api_info.get("category")
                tx["API_Brand"] = api_info.get("brand")
                tx["API_Rating"] = api_info.get("rating")
                tx["API_Match"] = True
            else:
                # ❌ No enrichment
                tx["API_Category"] = None
                tx["API_Brand"] = None
                tx["API_Rating"] = None
                tx["API_Match"] = False

            enriched.append(tx)

        except Exception as e:
            # Graceful error handling
            tx["API_Category"] = None
            tx["API_Brand"] = None
            tx["API_Rating"] = None
            tx["API_Match"] = False
            enriched.append(tx)
            print(f"⚠️ Error enriching transaction {tx.get('TransactionID')}: {e}")

    # Save to file
    save_enriched_data(enriched, filename="data/enriched_sales_data.txt")

    # Console summary
    enriched_count = sum(1 for tx in enriched if tx["API_Match"])
    print(f"✅ Enriched {enriched_count}/{len(enriched)} transactions ({(enriched_count/len(enriched)*100):.1f}%)")

    return enriched

import os
from datetime import datetime
from collections import defaultdict

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted text report with 8 sections.
    """

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 1. HEADER
    total_records = len(transactions)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. OVERALL SUMMARY
    total_revenue = sum(tx["Quantity"] * tx["UnitPrice"] for tx in transactions)
    avg_order_value = total_revenue / total_records if total_records else 0
    dates = [tx["Date"] for tx in transactions]
    date_range = f"{min(dates)} to {max(dates)}" if dates else "N/A"

    # 3. REGION-WISE PERFORMANCE
    region_sales = defaultdict(lambda: {"revenue": 0, "count": 0})
    for tx in transactions:
        region_sales[tx["Region"]]["revenue"] += tx["Quantity"] * tx["UnitPrice"]
        region_sales[tx["Region"]]["count"] += 1
    total_rev = total_revenue
    region_summary = sorted(region_sales.items(), key=lambda x: x[1]["revenue"], reverse=True)

    # 4. TOP 5 PRODUCTS
    product_sales = defaultdict(lambda: {"qty": 0, "revenue": 0})
    for tx in transactions:
        product_sales[tx["ProductName"]]["qty"] += tx["Quantity"]
        product_sales[tx["ProductName"]]["revenue"] += tx["Quantity"] * tx["UnitPrice"]
    top_products = sorted(product_sales.items(), key=lambda x: x[1]["revenue"], reverse=True)[:5]

    # 5. TOP 5 CUSTOMERS
    customer_sales = defaultdict(lambda: {"spent": 0, "orders": 0})
    for tx in transactions:
        customer_sales[tx["CustomerID"]]["spent"] += tx["Quantity"] * tx["UnitPrice"]
        customer_sales[tx["CustomerID"]]["orders"] += 1
    top_customers = sorted(customer_sales.items(), key=lambda x: x[1]["spent"], reverse=True)[:5]

    # 6. DAILY SALES TREND
    daily_sales = defaultdict(lambda: {"revenue": 0, "transactions": 0, "customers": set()})
    for tx in transactions:
        daily_sales[tx["Date"]]["revenue"] += tx["Quantity"] * tx["UnitPrice"]
        daily_sales[tx["Date"]]["transactions"] += 1
        daily_sales[tx["Date"]]["customers"].add(tx["CustomerID"])
    daily_summary = sorted(daily_sales.items())

    # 7. PRODUCT PERFORMANCE ANALYSIS
    best_day = max(daily_sales.items(), key=lambda x: x[1]["revenue"]) if daily_sales else None
    low_products = [p for p, stats in product_sales.items() if stats["qty"] == 0]
    avg_tx_value_region = {r: (stats["revenue"] / stats["count"]) if stats["count"] else 0
                           for r, stats in region_sales.items()}

    # 8. API ENRICHMENT SUMMARY
    enriched_count = sum(1 for tx in enriched_transactions if tx.get("API_Match"))
    success_rate = (enriched_count / len(enriched_transactions) * 100) if enriched_transactions else 0
    failed_products = [tx["ProductName"] for tx in enriched_transactions if not tx.get("API_Match")]

    # Write report
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("============================================\n")
        f.write("           SALES ANALYTICS REPORT\n")
        f.write(f"         Generated: {now}\n")
        f.write(f"         Records Processed: {total_records}\n")
        f.write("============================================\n\n")

        # Overall Summary
        f.write("OVERALL SUMMARY\n")
        f.write("--------------------------------------------\n")
        f.write(f"Total Revenue:        ₹{total_revenue:,.2f}\n")
        f.write(f"Total Transactions:   {total_records}\n")
        f.write(f"Average Order Value:  ₹{avg_order_value:,.2f}\n")
        f.write(f"Date Range:           {date_range}\n\n")

        # Region-wise performance
        f.write("REGION-WISE PERFORMANCE\n")
        f.write("--------------------------------------------\n")
        f.write("Region    Sales         % of Total  Transactions\n")
        for region, stats in region_summary:
            pct = (stats["revenue"] / total_rev * 100) if total_rev else 0
            f.write(f"{region:<8} ₹{stats['revenue']:,.0f}   {pct:5.2f}%      {stats['count']}\n")
        f.write("\n")

        # Top 5 Products
        f.write("TOP 5 PRODUCTS\n")
        f.write("--------------------------------------------\n")
        f.write("Rank  Product Name                Quantity   Revenue\n")
        for i, (pname, stats) in enumerate(top_products, 1):
            f.write(f"{i:<5} {pname:<25} {stats['qty']:<9} ₹{stats['revenue']:,.0f}\n")
        f.write("\n")

        # Top 5 Customers
        f.write("TOP 5 CUSTOMERS\n")
        f.write("--------------------------------------------\n")
        f.write("Rank  Customer ID   Total Spent   Orders\n")
        for i, (cid, stats) in enumerate(top_customers, 1):
            f.write(f"{i:<5} {cid:<12} ₹{stats['spent']:,.0f}   {stats['orders']}\n")
        f.write("\n")

        # Daily Sales Trend
        f.write("DAILY SALES TREND\n")
        f.write("--------------------------------------------\n")
        f.write("Date        Revenue     Transactions   Unique Customers\n")
        for date, stats in daily_summary:
            f.write(f"{date:<10} ₹{stats['revenue']:,.0f}   {stats['transactions']:<12} {len(stats['customers'])}\n")
        f.write("\n")

        # Product Performance Analysis
        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write("--------------------------------------------\n")
        if best_day:
            f.write(f"Best Selling Day: {best_day[0]} (₹{best_day[1]['revenue']:,.0f})\n")
        else:
            f.write("Best Selling Day: N/A\n")
        f.write(f"Low Performing Products: {', '.join(low_products) if low_products else 'None'}\n")
        f.write("Average Transaction Value per Region:\n")
        for region, avg in avg_tx_value_region.items():
            f.write(f"  {region}: ₹{avg:,.2f}\n")
        f.write("\n")

        # API Enrichment Summary
        f.write("API ENRICHMENT SUMMARY\n")
        f.write("--------------------------------------------\n")
        f.write(f"Total Products Enriched: {enriched_count}\n")
        f.write(f"Success Rate: {success_rate:.2f}%\n")
        f.write(f"Unmatched Products: {', '.join(failed_products) if failed_products else 'None'}\n")
        f.write("\n")

    print(f"✅ Sales report generated at {output_file}")