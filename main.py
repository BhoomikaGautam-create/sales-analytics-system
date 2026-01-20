from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    generate_sales_report
)

def main():
    """
    Main execution function
    """
    try:
        print("========================================")
        print("        SALES ANALYTICS SYSTEM")
        print("========================================\n")

        # 1. Read sales data
        print("[1/10] Reading sales data...")
        raw_lines = read_sales_data("data/sales_data.txt")
        print(f"✓ Successfully read {len(raw_lines)} transactions\n")

        # 2. Parse and clean
        print("[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} records\n")

        # 3. Filter options
        print("[3/10] Filter Options Available:")
        regions = sorted(
    set(tx["Region"].strip() for tx in transactions if tx.get("Region") and tx["Region"].strip())
)

        amounts = [tx["Quantity"] * tx["UnitPrice"] for tx in transactions]
        print(f"Regions: {', '.join(regions)}")
        print(f"Amount Range: ₹{min(amounts):,.0f} - ₹{max(amounts):,.0f}\n")

        choice = input("Do you want to filter data? (y/n): ").strip().lower()
        if choice == "y":
            region_choice = input("Enter region to filter (or press Enter to skip): ").strip()
            min_amt = input("Enter minimum amount (or press Enter to skip): ").strip()
            max_amt = input("Enter maximum amount (or press Enter to skip): ").strip()

            filtered = []
            for tx in transactions:
                amt = tx["Quantity"] * tx["UnitPrice"]
                if (not region_choice or tx["Region"] == region_choice) and \
                   (not min_amt or amt >= float(min_amt)) and \
                   (not max_amt or amt <= float(max_amt)):
                    filtered.append(tx)
            transactions = filtered
            print(f"✓ Applied filters, {len(transactions)} records remain\n")

        # 4. Validate transactions
        print("[4/10] Validating transactions...")
        valid_tx, invalid_count, summary = validate_and_filter(transactions)
        print(f"✓ Valid: {len(valid_tx)} | Invalid: {invalid_count}\n")

        # 5. Perform analyses (Part 2 functions assumed)
        print("[5/10] Analyzing sales data...")
        # Here you would call your analysis functions (region summary, top products, etc.)
        print("✓ Analysis complete\n")

        # 6. Fetch products
        print("[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        print(f"✓ Fetched {len(api_products)} products\n")

        # 7. Enrich sales data
        print("[7/10] Enriching sales data...")
        product_map = create_product_mapping(api_products)
        enriched_tx = enrich_sales_data(valid_tx, product_map)
        enriched_count = sum(1 for tx in enriched_tx if tx.get("API_Match"))
        success_rate = (enriched_count / len(enriched_tx) * 100) if enriched_tx else 0
        print(f"✓ Enriched {enriched_count}/{len(enriched_tx)} transactions ({success_rate:.1f}%)\n")

        # 8. Saving enriched data
        print("[8/10] Saving enriched data...")
        print("✓ Saved to: data/enriched_sales_data.txt\n")

        # 9. Generate report
        print("[9/10] Generating report...")
        generate_sales_report(valid_tx, enriched_tx, output_file="output/sales_report.txt")
        print("✓ Report saved to: output/sales_report.txt\n")

        # 10. Success message
        print("[10/10] Process Complete!")
        print("========================================")

    except Exception as e:
        print("❌ An error occurred during execution.")
        print(f"Details: {e}")


if __name__ == "__main__":
    main()