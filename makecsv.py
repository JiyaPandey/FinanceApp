import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# ==========================
# 1. Fetch NSE Stocks (India)
# ==========================
print("📥 Fetching NSE stocks...")

# Get today's date in the required format
today = datetime.today().strftime('%Y%m%d')
nse_bhavcopy_url = f"https://www1.nseindia.com/content/historical/EQUITIES/2025/JUN/cm{today}bhav.csv.zip"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nseindia.com"
}

try:
    nse_response = requests.get(nse_bhavcopy_url, headers=headers)
    if nse_response.status_code == 200:
        with open("nse_bhavcopy.zip", "wb") as f:
            f.write(nse_response.content)
        import zipfile
        with zipfile.ZipFile("nse_bhavcopy.zip", 'r') as zip_ref:
            zip_ref.extractall("nse_bhavcopy")
        bhavcopy_filename = f"cm{today}bhav.csv"
        nse_df = pd.read_csv(f"nse_bhavcopy/{bhavcopy_filename}")
        nse_df['Yahoo_Ticker'] = nse_df['SYMBOL'] + ".NS"
        nse_df['Country'] = "India"
        nse_df['Type'] = "Stock"
        nse_df = nse_df[['SYMBOL', 'SERIES', 'Yahoo_Ticker', 'Country', 'Type']]
        nse_df.columns = ['Symbol', 'Company', 'Yahoo_Ticker', 'Country', 'Type']
    else:
        print("Failed to fetch NSE Bhavcopy.")
        nse_df = pd.DataFrame(columns=['Symbol', 'Company', 'Yahoo_Ticker', 'Country', 'Type'])
except Exception as e:
    print(f"Error fetching NSE data: {e}")
    nse_df = pd.DataFrame(columns=['Symbol', 'Company', 'Yahoo_Ticker', 'Country', 'Type'])

# ==========================
# 2. Fetch US Stocks (NASDAQ)
# ==========================
print("📥 Fetching NASDAQ stocks...")
us_df = pd.read_csv("https://raw.githubusercontent.com/datasets/nasdaq-listings/master/data/nasdaq-listed-symbols.csv")
us_df['Yahoo_Ticker'] = us_df['Symbol']
us_df['Country'] = "US"
us_df['Type'] = "Stock"
us_df['Company'] = us_df['Company Name']
us_df = us_df[['Symbol', 'Company', 'Yahoo_Ticker', 'Country', 'Type']]

# ==========================
# 3. Fetch Indian Mutual Funds (from AMFI)
# ==========================
print("📥 Fetching Indian mutual funds (AMFI)...")
amfi_url = "https://www.amfiindia.com/spages/NAVAll.txt"
amfi_response = requests.get(amfi_url, headers=headers)
amfi_text = amfi_response.content.decode('utf-8')
amfi_lines = amfi_text.strip().splitlines()

mutual_funds = []

for line in amfi_lines:
    if line.startswith("Scheme Code") or line.strip() == "":
        continue
    parts = line.split(';')
    if len(parts) >= 5:
        scheme_code = parts[0].strip()
        scheme_name = parts[1].strip()
        amc = parts[2].strip()
        nav_date = parts[3].strip()
        nav = parts[4].strip()
        mutual_funds.append({
            "Symbol": scheme_code,
            "Company": scheme_name,
            "Yahoo_Ticker": "",  # No Yahoo ticker for most mutual funds
            "Country": "India",
            "Type": "MutualFund",
            "AMC": amc,
            "NAV_Date": nav_date,
            "NAV": nav
        })

mf_df = pd.DataFrame(mutual_funds)

# ==========================
# 4. Combine All and Save
# ==========================
print("📦 Combining all data...")

# Ensure all dataframes have same columns
mf_df = mf_df[['Symbol', 'Company', 'Yahoo_Ticker', 'Country', 'Type', 'AMC', 'NAV_Date', 'NAV']]
nse_df['AMC'] = ""
nse_df['NAV_Date'] = ""
nse_df['NAV'] = ""

us_df['AMC'] = ""
us_df['NAV_Date'] = ""
us_df['NAV'] = ""

combined_df = pd.concat([nse_df, us_df, mf_df], ignore_index=True)
combined_df.to_csv("combined_stocks_yahoo.csv", index=False)

print("✅ All data saved to combined_stocks_yahoo.csv")
