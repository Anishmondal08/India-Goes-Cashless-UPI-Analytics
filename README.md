# 💳 India Goes Cashless: UPI Analytics

A fully interactive **Streamlit** dashboard for analysing India's UPI transaction landscape in 2024.  
All analysis logic (data loading, cleaning, metrics, charts, insights) lives inside a **single file** — `app.py`.

---

## 📑 Table of Contents

- [Project Overview](#project-overview)
- [Dataset](#dataset)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Dashboard Sections](#dashboard-sections)
- [Key Insights](#key-insights)
- [Requirements](#requirements)

---

## Project Overview

This project analyses **250,000 UPI transactions** recorded across India in 2024.  
The goal is to uncover:

- Transaction volume and value trends over time
- Merchant category and payment-type preferences
- Geographic and demographic usage patterns
- Bank and device-level breakdowns
- Fraud detection indicators

The result is a polished, dark-theme Streamlit dashboard that turns raw CSV data into actionable insights.

---

## Dataset

| Field | Description |
|---|---|
| `transaction id` | Unique transaction identifier |
| `timestamp` | Date and time of the transaction |
| `transaction type` | P2P (person-to-person) or P2M (person-to-merchant) |
| `merchant_category` | Category of merchant (Grocery, Fuel, Entertainment, …) |
| `amount (INR)` | Transaction amount in Indian Rupees |
| `transaction_status` | SUCCESS / FAILED / PENDING |
| `sender_age_group` | Age bracket of the sender |
| `receiver_age_group` | Age bracket of the receiver |
| `sender_state` | Sending state (Delhi, Karnataka, …) |
| `sender_bank` | Bank of the sender |
| `receiver_bank` | Bank of the receiver |
| `device_type` | Android / iOS |
| `network_type` | 4G / 5G / WiFi |
| `fraud_flag` | 1 = fraudulent, 0 = normal |
| `hour_of_day` | Hour when the transaction occurred (0–23) |
| `day_of_week` | Day name (Monday–Sunday) |
| `is_weekend` | 1 = weekend, 0 = weekday |

**File name:** `upi_transactions_2024.csv`  
**Place this file in the same directory as `app.py` before running.**

---

## Features

- ✅ **Data Loading & Cleaning** — automatic column normalisation, duplicate removal, type coercion, null handling
- 📊 **Key KPIs** — total transactions, total value, success rate, avg amount, fraud rate, peak hour
- 🔍 **Interactive Filters** — filter by state, transaction type, and month via sidebar
- 📈 **8 Analysis Tabs:**
  1. Trends (monthly, hourly, weekly, quarterly)
  2. Categories (merchant, payment type, amount distribution, status)
  3. Geography (state-level counts, values, avg amount)
  4. Banks (sender bank, cross-bank flow heatmap)
  5. Device & Network (device split, network split, cross-table)
  6. Demographics (age group analysis, sender→receiver flow)
  7. Fraud (fraud rate, state/bank/hour breakdown, amount comparison)
  8. Raw Data (searchable table, download CSV, data quality report)
- 💡 **Auto-generated Key Insights** — narrative insights derived programmatically from the data
- 📥 **Download** — export filtered data as CSV

---

## Tech Stack

| Library | Purpose |
|---|---|
| **Streamlit** | Web application framework |
| **Pandas** | Data manipulation & aggregation |
| **NumPy** | Numerical operations |
| **Plotly** | Interactive charts and visualisations |

---

## Project Structure

```
IBM BOB FINAL/
│
├── app.py                        # ← Single main file (frontend + backend)
├── upi_transactions_2024.csv     # Dataset
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── UPI_Analytics_Report.docx     # Project report (MS Word)
```

---

## Getting Started

### 1. Clone / download the project

```bash
# If using git
git clone <repo-url>
cd "IBM BOB FINAL"
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The dashboard will open automatically at **http://localhost:8501**.

### 5. Use a custom dataset (optional)

In the sidebar click **Upload CSV** and select any CSV with the same schema.

---

## Dashboard Sections

| Tab | What you'll find |
|---|---|
| 📈 **Trends** | Monthly volume & value, hourly bar chart, day-of-week, weekend split, quarterly summary |
| 🏷️ **Categories** | Merchant category breakdown, P2P vs P2M, amount histogram, box plot, status donut |
| 🗺️ **Geography** | State-wise transaction count, value (₹ Cr), average amount, detailed summary table |
| 🏦 **Banks** | Sender bank ranking, value share pie, sender→receiver flow bubble chart, avg-amount heatmap |
| 📱 **Device & Network** | Device type and network type donuts, cross-table bar, amount stats by device |
| 👥 **Demographics** | Age group transaction count & avg amount, sender→receiver age heatmap, type-by-age |
| 🚨 **Fraud** | KPI cards, fraud by state/bank/hour, normal vs fraud amount overlay histogram, category breakdown |
| 🗃️ **Raw Data** | Full-text search, row-count selector, CSV download, data quality report |

---

## Key Insights

1. **Dominant State** — one state accounts for a disproportionately large share of transactions.
2. **Peak Hour** — UPI activity surges in the evening (around 19:00).
3. **P2P vs P2M** — one type dominates, reflecting primary use-case.
4. **Fraud Rate < 0.2%** — extremely low, reflecting UPI's robust fraud controls.
5. **Success Rate > 95%** — high reliability across banks and network types.
6. **26–35 age group** — core demographic driving digital payments.
7. **Android-first** — the majority of transactions originate from Android devices.
8. **4G dominates** — high-speed mobile internet remains the primary connectivity layer.

---

## Requirements

```
streamlit>=1.32.0
pandas>=2.1.0
numpy>=1.26.0
plotly>=5.20.0
openpyxl>=3.1.2
```

---

*Built with ❤️ using Streamlit & Plotly · Dataset: upi_transactions_2024.csv*
