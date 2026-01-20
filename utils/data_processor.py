import pandas as pd

def clean_sales_data(filepath):
    df = pd.read_csv(filepath, delimiter="|", encoding="latin1", engine="python")
    total_records = len(df)

    # Drop empty lines
    df.dropna(how="all", inplace=True)

    # Fix commas in ProductName
    if "ProductName" in df.columns:
        df["ProductName"] = df["ProductName"].str.replace(",", "", regex=False)

    # Fix commas in numeric values
    for col in ["Quantity", "UnitPrice", "Revenue"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Apply invalid record filters
    invalid_mask = (
        df["CustomerID"].isna() |
        df["Region"].isna() |
        (df["Quantity"] <= 0) |
        (df["UnitPrice"] <= 0) |
        (~df["TransactionID"].astype(str).str.startswith("T"))
    )

    invalid_records = df[invalid_mask]
    valid_records = df[~invalid_mask]

    print(f"Total records parsed: {total_records}")
    print(f"Invalid records removed: {len(invalid_records)}")
    print(f"Valid records after cleaning: {len(valid_records)}")

    # Save cleaned data here
    valid_records.to_csv("output/cleaned_sales_data.csv", index=False)

    return valid_records

def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions.

    Returns: float (total revenue)
    Example: 1545000.50
    """
    total = 0.0
    for tx in transactions:
        total += tx["Quantity"] * tx["UnitPrice"]
    return total


def region_wise_sales(transactions):
    """
    Analyzes sales by region.

    Returns: dictionary with region statistics
    Format:
    {
        'North': {
            'total_sales': 450000.0,
            'transaction_count': 15,
            'percentage': 29.13
        },
        'South': {...},
        ...
    }
    """
    region_stats = {}
    total_revenue = calculate_total_revenue(transactions)

    # Step 1: Aggregate totals per region
    for tx in transactions:
        region = tx["Region"]
        amount = tx["Quantity"] * tx["UnitPrice"]

        if region not in region_stats:
            region_stats[region] = {
                "total_sales": 0.0,
                "transaction_count": 0,
                "percentage": 0.0,
            }

        region_stats[region]["total_sales"] += amount
        region_stats[region]["transaction_count"] += 1

    # Step 2: Calculate percentages
    for region, stats in region_stats.items():
        if total_revenue > 0:
            stats["percentage"] = round((stats["total_sales"] / total_revenue) * 100, 2)

    # Step 3: Sort by total_sales (descending)
    region_stats = dict(
        sorted(region_stats.items(), key=lambda x: x[1]["total_sales"], reverse=True)
    )

    return region_stats

def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold.

    Returns: list of tuples
    Format:
    [
        ('Laptop', 45, 2250000.0),
        ('Mouse', 38, 19000.0),
        ...
    ]
    """
    product_stats = {}

    # Step 1: Aggregate totals per product
    for tx in transactions:
        product = tx["ProductName"]
        qty = tx["Quantity"]
        revenue = tx["Quantity"] * tx["UnitPrice"]

        if product not in product_stats:
            product_stats[product] = {"total_qty": 0, "total_revenue": 0.0}

        product_stats[product]["total_qty"] += qty
        product_stats[product]["total_revenue"] += revenue

    # Step 2: Sort by total quantity sold (descending)
    sorted_products = sorted(
        product_stats.items(),
        key=lambda x: x[1]["total_qty"],
        reverse=True
    )

    # Step 3: Return top n as list of tuples
    top_n = [
        (product, stats["total_qty"], stats["total_revenue"])
        for product, stats in sorted_products[:n]
    ]

    return top_n


def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns.

    Returns: dictionary of customer statistics
    Format:
    {
        'C001': {
            'total_spent': 95000.0,
            'purchase_count': 3,
            'avg_order_value': 31666.67,
            'products_bought': ['Laptop', 'Mouse', 'Keyboard']
        },
        ...
    }
    """
    customer_stats = {}

    # Step 1: Aggregate per customer
    for tx in transactions:
        cust_id = tx["CustomerID"]
        amount = tx["Quantity"] * tx["UnitPrice"]
        product = tx["ProductName"]

        if cust_id not in customer_stats:
            customer_stats[cust_id] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products_bought": set()
            }

        customer_stats[cust_id]["total_spent"] += amount
        customer_stats[cust_id]["purchase_count"] += 1
        customer_stats[cust_id]["products_bought"].add(product)

    # Step 2: Calculate avg order value & convert products to list
    for cust_id, stats in customer_stats.items():
        stats["avg_order_value"] = round(
            stats["total_spent"] / stats["purchase_count"], 2
        )
        stats["products_bought"] = list(stats["products_bought"])

    # Step 3: Sort by total_spent (descending)
    customer_stats = dict(
        sorted(customer_stats.items(), key=lambda x: x[1]["total_spent"], reverse=True)
    )

    return customer_stats

def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date.

    Returns: dictionary sorted by date
    Format:
    {
        '2024-12-01': {
            'revenue': 125000.0,
            'transaction_count': 8,
            'unique_customers': 6
        },
        ...
    }
    """
    daily_stats = {}

    # Step 1: Aggregate by date
    for tx in transactions:
        date = tx["Date"]
        amount = tx["Quantity"] * tx["UnitPrice"]
        cust_id = tx["CustomerID"]

        if date not in daily_stats:
            daily_stats[date] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "unique_customers": set()
            }

        daily_stats[date]["revenue"] += amount
        daily_stats[date]["transaction_count"] += 1
        daily_stats[date]["unique_customers"].add(cust_id)

    # Step 2: Convert unique_customers set → count
    for date, stats in daily_stats.items():
        stats["unique_customers"] = len(stats["unique_customers"])

    # Step 3: Sort chronologically
    daily_stats = dict(sorted(daily_stats.items(), key=lambda x: x[0]))

    return daily_stats


def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue.

    Returns: tuple (date, revenue, transaction_count)
    Example: ('2024-12-15', 185000.0, 12)
    """
    daily_stats = daily_sales_trend(transactions)

    # Step 1: Find max revenue day
    peak_date, peak_data = max(
        daily_stats.items(),
        key=lambda x: x[1]["revenue"]
    )

    return (peak_date, peak_data["revenue"], peak_data["transaction_count"])

def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales.

    Returns: list of tuples
    Format:
    [
        ('Webcam', 4, 12000.0),
        ('Headphones', 7, 10500.0),
        ...
    ]
    """
    product_stats = {}

    # Step 1: Aggregate totals per product
    for tx in transactions:
        product = tx["ProductName"]
        qty = tx["Quantity"]
        revenue = tx["Quantity"] * tx["UnitPrice"]

        if product not in product_stats:
            product_stats[product] = {"total_qty": 0, "total_revenue": 0.0}

        product_stats[product]["total_qty"] += qty
        product_stats[product]["total_revenue"] += revenue

    # Step 2: Filter products below threshold
    low_products = [
        (product, stats["total_qty"], stats["total_revenue"])
        for product, stats in product_stats.items()
        if stats["total_qty"] < threshold
    ]

    # Step 3: Sort ascending by total quantity
    low_products = sorted(low_products, key=lambda x: x[1])

    return low_products