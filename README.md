# FinanceApp

**FinanceApp** is a Streamlit-powered personal finance dashboard that combines:

- Stock and mutual fund analysis
- Portfolio management
- Expense tracking

All integrated into one seamless interface for better financial insights and decisions.

---

## Features

### 1. Stock & Mutual Fund Analysis

- Search and analyze equities or mutual funds via an autocomplete search bar.
- View historical trends through interactive area charts powered by Plotly.
- Data is pulled from Yahoo Finance using the `yfinance` library.

### 2. Portfolio Tracker

- Add and track personal investment entries.
- View portfolio distribution and gains/losses visually.

### 3. Expense Tracker

- Create custom expense/income categories and assign budgets.
- Record financial entries monthly.
- Visualize income vs. expenses using bar and line charts.

---

## How to Run the App

### Step 1: Clone the Repository

```bash
git clone https://github.com/JiyaPandey/FinanceApp.git
cd FinanceApp
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Run the App

```bash
streamlit run source_code/main.py
```

Then open your browser and go to:
[http://localhost:8501](http://localhost:8501)

---

## Project Structure

```
FinanceApp/
│
├── data/                        # CSV and external data files
│   ├── combined_stocks_yahoo.csv
│   ├── nse_bhavcopy.zip
│   ├── nse_stocks.csv
│   └── tickers_list.csv
│
├── src/                 # Application logic
│   ├── main.py                  # Entry point
│   ├── stock_analysis.py        # Stock analysis module
│   ├── portfolio.py             # Portfolio tracking module
│   ├── expense_tracker.py       # Income/expense tracking
│   ├── stock.py                 # Data helpers
│   ├── makecsv.py               # CSV preparation script
│   └── utils.py                 # Shared utility functions
│
├── requirements.txt             # Project dependencies
└── README.md                    # Project documentation
```

---

## Requirements

The app relies on the following Python libraries:

- `streamlit`
- `pandas`
- `yfinance`
- `plotly`

Install them using the provided `requirements.txt`.

---

## Notes

- Make sure the required CSV files are inside the `data/` directory.
- You may need to adjust file paths in your code as:
  `pd.read_csv("data/filename.csv")`
- Files in `__pycache__/` are auto-generated and can be ignored.

---

## License

This project is open-source and available under the **MIT License**.

GitHub Repository: [https://github.com/JiyaPandey/FinanceApp](https://github.com/JiyaPandey/FinanceApp)

```

---

You're all set—just copy and paste this directly into your `README.md` file!
```
