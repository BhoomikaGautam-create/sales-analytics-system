# Sales Analytics System

This project processes raw sales transaction data, enriches it with product information from an API, and generates a comprehensive sales report.

---

## 📂 Project Structure
sales-analytics-system/
├── README.md
├── main.py
├── utils/
│   ├── file_handler.py
│   ├── data_processor.py
│   └── api_handler.py
├── data/
│   └── sales_data.txt
├── output/
└── requirements.txt


## ⚙️ Setup Instructions

1. Clone the repository
  
   git clone https://github.com/BhoomikaGautam-create/sales-analytics-system
   cd sales-analytics-system

2. Create a virtual environment
   python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

3 Install dependencies

pip install -r requirements.txt

4 Run Instructions

Run the main script
```bash
python main.py

- This will:- Read data/sales_data.txt
- Enrich transactions with API product info
- Save enriched data to data/enriched_sales_data.txt
- Generate a full report in output/sales_report.txt

Outputs

- data/enriched_sales_data.txt → Pipe‑delimited enriched transactions with API fields.
- output/sales_report.txt → Sales report including:
- Summary statistics
- Enrichment success rate
- Regional breakdown
- Top products

## ✅ Requirements

- Python 3.8+
- requests
- pandas

## 📝 Notes

- No hardcoded file paths — all files are relative.
- Code runs end-to-end without errors.


