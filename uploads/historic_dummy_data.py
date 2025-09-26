import pandas as pd
import numpy as np

# Generate quarterly dates
dates = pd.date_range(start="2020-01-01", end="2025-09-01", freq="YE")

# Asset list with relevant info (Ticker, Name, Sector, Asset Class, Category, Subcategory, Location, Exchange, Currency)
assets = [
    ("AAPL", "Apple Inc.", "Information Technology", "Equity", "Equities", "Technology", "United States", "NASDAQ", "USD"),
    ("MSFT", "Microsoft Corp.", "Information Technology", "Equity", "Equities", "Technology", "United States", "NASDAQ", "USD"),
    ("JPM", "JPMorgan Chase & Co.", "Financials", "Equity", "Equities", "Financial Services", "United States", "NYSE", "USD"),
    ("PFE", "Pfizer Inc.", "Health Care", "Equity", "Equities", "Pharmaceuticals", "United States", "NYSE", "USD"),
    ("PLD", "Prologis, Inc.", "Real Estate", "Equity", "Real Estate", "REITs", "United States", "NYSE", "USD"),
    ("KO", "Coca-Cola Co.", "Consumer Staples", "Equity", "Equities", "Beverages", "United States", "NYSE", "USD"),
    ("JNJ", "Johnson & Johnson", "Health Care", "Equity", "Equities", "Pharmaceuticals", "United States", "NYSE", "USD"),
    ("MCD", "McDonald's Corp.", "Consumer Discretionary", "Equity", "Equities", "Restaurants", "United States", "NYSE", "USD"),
    ("BA", "Boeing Co.", "Industrials", "Equity", "Equities", "Aerospace", "United States", "NYSE", "USD"),
    ("NEE", "NextEra Energy, Inc.", "Utilities", "Equity", "Equities", "Utilities", "United States", "NYSE", "USD"),
    ("CVS", "CVS Health Corp.", "Health Care", "Equity", "Equities", "Healthcare Services", "United States", "NYSE", "USD"),
    ("VWO", "Vanguard FTSE Emerging Markets ETF", "Emerging Markets", "Equity", "Equities", "Emerging Markets", "Global", "NYSE", "USD"),
    ("EEM", "iShares MSCI Emerging Markets ETF", "Emerging Markets", "Equity", "Equities", "Emerging Markets", "Global", "NYSE", "USD"),
    ("TLT", "iShares 20+ Year Treasury Bond ETF", "Fixed Income", "Bond", "Fixed Income", "Treasury Bonds", "United States", "NASDAQ", "USD"),
    ("HYG", "iShares iBoxx High Yield Corporate Bond ETF", "Fixed Income", "Bond", "Fixed Income", "High Yield Bonds", "United States", "NYSE", "USD"),
    ("VNQ", "Vanguard Real Estate ETF", "Real Estate", "Equity", "Real Estate", "REITs", "United States", "NYSE", "USD"),
    ("SLV", "iShares Silver Trust", "Materials", "Commodity", "Commodities", "Silver", "Global", "NYSE", "USD"),
    ("URTH", "iShares MSCI World ETF", "Benchmark", "Index Fund", "Benchmark", "Global Equities", "Global", "NYSE", "USD"),
]

np.random.seed(42)  # for reproducible results

rows = []

for ticker, name, sector, asset_class, category, subcategory, location, exchange, currency in assets:
    # Start price between 20 and 500 for equities/commodities, bonds lower variance
    if asset_class == "Bond" or category == "Benchmark":
        start_price = np.random.uniform(80, 120)
    elif asset_class == "Commodity":
        start_price = np.random.uniform(10, 200)
    else:
        start_price = np.random.uniform(20, 500)
    
    # Simulate weekly returns with a small drift and volatility
    if category == "Benchmark":
        drift = 0.0008  # slightly higher drift for benchmarks
        vol = 0.015
    elif asset_class == "Commodity":
        drift = 0.0003
        vol = 0.03
    elif asset_class == "Bond":
        drift = 0.0002
        vol = 0.005
    else:
        drift = 0.0005
        vol = 0.02

    prices = [start_price]
    for _ in range(1, len(dates)):
        shock = np.random.normal(drift, vol)
        new_price = max(prices[-1] * (1 + shock), 0.1)  # price can't be below 0.1
        prices.append(new_price)
    
    prices = np.array(prices)
    
    # Simulate nominal value (units held) roughly proportional to start price (inverse)
    nominal_value = np.round(np.random.uniform(100, 1000))
    
    # Weighting and allocation can be randomized but summing to 100% across assets per date would be complex
    # We'll assign a fixed weighting range for dummy purpose
    weighting = np.round(np.random.uniform(1, 5), 2)
    allocation = weighting  # for simplicity

    # Performance and drawdown calculations
    performance = (prices - start_price) / start_price * 100  # % return from start
    drawdown = (prices - np.maximum.accumulate(prices)) / np.maximum.accumulate(prices) * 100  # % drawdown
    
    for i, date in enumerate(dates):
        rows.append([
            ticker,  # Emittententicker
            name,
            sector,
            asset_class,  # Anlageklasse
            prices[i] * nominal_value,  # Marktwert = price * nominal units
            weighting,
            nominal_value,
            nominal_value,  # Nominale (same as nominal_value for dummy)
            prices[i],  # Kurs
            location,
            exchange,
            currency,
            date,
            date.year,
            allocation,
            performance[i],
            drawdown[i]
        ])

# Create DataFrame
df = pd.DataFrame(rows, columns=[
    "Ticker",              # Emittententicker
    "Name",                # Name
    "Sector",              # Sektor
    "Asset Class",         # Anlageklasse
    "Market Value",        # Marktwert
    "Weight (%)",          # Gewichtung (%)
    "Nominal Value",       # Nominalwert
    "Nominal Units",       # Nominale
    "Price",               # Kurs
    "Country",             # Standort
    "Exchange",            # Börse
    "Currency",            # Marktwährung
    "Date",
    "Year",                # Year (already in English)
    "Allocation (%)",      # Allocation (%)
    "Performance (%)",     # Performance
    "Drawdown (%)"         # Drawdown (%)
])

# Save to CSV
df.to_csv("historic_portfolio.csv", index=False)

print("CSV file created: historic_portfolio.csv")
