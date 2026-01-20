def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues.
    Returns: list of raw lines (strings)
    """
    encodings = ["utf-8", "latin-1", "cp1252"]

    lines = None
    for enc in encodings:
        try:
            with open(filename, "r", encoding=enc) as f:
                lines = f.readlines()
                break
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []

    if lines is None:
        print("Error: Could not read file with supported encodings.")
        return []

    cleaned_lines = [
        line.strip()
        for line in lines[1:]  # skip header
        if line.strip() != ""  # remove empty lines
    ]

    return cleaned_lines

def read_sales_data(filename):
    """
    Reads sales data from file handling encoding issues.
    Returns: list of raw lines (strings)
    """
    encodings = ["utf-8", "latin-1", "cp1252"]

    lines = None
    for enc in encodings:
        try:
            with open(filename, "r", encoding=enc) as f:
                lines = f.readlines()
                break
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []

    if lines is None:
        print("Error: Could not read file with supported encodings.")
        return []

    cleaned_lines = [
        line.strip()
        for line in lines[1:]  # skip header
        if line.strip() != ""  # remove empty lines
    ]

    return cleaned_lines


def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries.

    Returns: list of dictionaries with keys:
    ['TransactionID', 'Date', 'ProductID', 'ProductName',
     'Quantity', 'UnitPrice', 'CustomerID', 'Region']
    """
    transactions = []

    for line in raw_lines:
        parts = line.split("|")

        # Skip rows with incorrect number of fields
        if len(parts) != 8:
            continue

        transaction_id, date, product_id, product_name, quantity, unit_price, customer_id, region = parts

        # Handle commas in ProductName (remove them)
        product_name = product_name.replace(",", "")

        # Remove commas from numeric fields
        quantity = quantity.replace(",", "")
        unit_price = unit_price.replace(",", "")

        try:
            quantity = int(quantity)
            unit_price = float(unit_price)
        except ValueError:
            # Skip rows with invalid numeric values
            continue

        transaction = {
            "TransactionID": transaction_id.strip(),
            "Date": date.strip(),
            "ProductID": product_id.strip(),
            "ProductName": product_name.strip(),
            "Quantity": quantity,
            "UnitPrice": unit_price,
            "CustomerID": customer_id.strip(),
            "Region": region.strip()
        }

        transactions.append(transaction)

    return transactions

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters.

    Parameters:
    - transactions: list of transaction dictionaries
    - region: filter by specific region (optional)
    - min_amount: minimum transaction amount (Quantity * UnitPrice) (optional)
    - max_amount: maximum transaction amount (optional)

    Returns: tuple (valid_transactions, invalid_count, filter_summary)
    """

    total_input = len(transactions)
    invalid_count = 0
    valid_transactions = []

    # Step 1: Validation
    for tx in transactions:
        if (
            tx.get("Quantity", 0) <= 0
            or tx.get("UnitPrice", 0) <= 0
            or not tx.get("TransactionID", "").startswith("T")
            or not tx.get("ProductID", "").startswith("P")
            or not tx.get("CustomerID", "").startswith("C")
        ):
            invalid_count += 1
            continue
        valid_transactions.append(tx)

    # Step 2: Show available regions
    regions = sorted(set(tx["Region"] for tx in valid_transactions))
    print(f"Available regions: {regions}")

    # Step 3: Show transaction amount range
    amounts = [tx["Quantity"] * tx["UnitPrice"] for tx in valid_transactions]
    if amounts:
        print(f"Transaction amount range: min={min(amounts)}, max={max(amounts)}")

    # Step 4: Apply filters
    filtered_by_region = 0
    filtered_by_amount = 0

    if region:
        before = len(valid_transactions)
        valid_transactions = [tx for tx in valid_transactions if tx["Region"] == region]
        filtered_by_region = before - len(valid_transactions)
        print(f"Filtered by region '{region}': {filtered_by_region} removed")

    if min_amount is not None:
        before = len(valid_transactions)
        valid_transactions = [
            tx for tx in valid_transactions if tx["Quantity"] * tx["UnitPrice"] >= min_amount
        ]
        filtered_by_amount += before - len(valid_transactions)
        print(f"Filtered by min_amount {min_amount}: {before - len(valid_transactions)} removed")

    if max_amount is not None:
        before = len(valid_transactions)
        valid_transactions = [
            tx for tx in valid_transactions if tx["Quantity"] * tx["UnitPrice"] <= max_amount
        ]
        filtered_by_amount += before - len(valid_transactions)
        print(f"Filtered by max_amount {max_amount}: {before - len(valid_transactions)} removed")

    # Step 5: Summary
    filter_summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(valid_transactions),
    }

    return valid_transactions, invalid_count, filter_summary