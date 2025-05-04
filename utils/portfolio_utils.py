import pandas as pd
from typing import Dict
import yfinance as yf
import time
import requests
import json

def get_live_price(symbol: str) -> float:
    """Get live market price for a given NSE stock symbol using direct Yahoo Finance API."""
    try:
        # Direct Yahoo Finance API approach
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        
        # Extract the last closing price
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            if 'meta' in result and 'regularMarketPrice' in result['meta']:
                price = result['meta']['regularMarketPrice']
                return float(price)
        
        # If no price found through API, use dummy data directly
        return 0
            
    except Exception as e:
        print(f"Error fetching price for {symbol}: {str(e)}")
        return 0

def use_dummy_data_for_testing():
    """Create dummy prices for testing - only used if API calls fail."""
    # Map of dummy prices based on the last available AveragePrice
    return {
        'GAIL': 190.50,
        'MOTHERSON': 140.25,
        'NTPC': 352.75,
        'RPOWER': 42.30,
        'ADANIGREEN': 910.20,
        'INDIANREN': 170.45,
        'SUZLON': 60.80,
        'OBEROIRLTY': 1650.30,
        'TATAMOTORS': 700.90,
        'MAHLIFE': 360.40,
        'DLF': 695.75,
        'TATASTEEL': 155.20,
        'SHRIRAMPPS': 90.50,
        'VIKASECO': 2.75,
        'BLS': 430.60,
        'JYOTISTRUC': 25.30,
        'MOTILALOFS': 200.45,
        'BEL': 290.25,
        'IDFCFIRSTB': 62.30,
        'NHPC': 80.40,
        'L&TFH': 155.25,
        'SBIN': 750.40,
        'NCC': 205.30,
        'BANDHANBNK': 160.45,
        'BANKINDIA': 110.25,
        'IEX': 185.60,
        'ASHOKLEY': 220.40,
        'APOLLOTYRE': 440.25,
        'JIOFIN': 250.75,
        'JKTYRE': 300.40,
        'PNB': 100.25,
        'IDBI': 82.30,
        'TATAPOWER': 385.45,
        'ITC': 420.30,
        'REDINGTON': 245.70
    }

def load_portfolio_data() -> pd.DataFrame:
    """Load and process portfolio data from CSV."""
    # Read the portfolio data
    df = pd.read_csv('assets/PersonalFiles/myPortfolio.csv')
    
    # Get dummy data ready for any stocks that fail
    dummy_prices = use_dummy_data_for_testing()
    
    # Try to get live prices with fallback to dummy data
    prices = {}
    for symbol in df['NSE_Symbol'].unique():
        # Try to get the price
        price = get_live_price(symbol)
        
        # If price fetch failed, use dummy data without retrying
        if price == 0:
            price = dummy_prices.get(symbol, 0)
            print(f"Using dummy price for {symbol}: {price}")
            
        prices[symbol] = price
        time.sleep(0.5)  # Add delay between requests to avoid rate limiting
    
    # Add price data to dataframe
    df['Current Price'] = df['NSE_Symbol'].map(prices)
    
    # Calculate investment metrics
    df['TotalInvestment'] = df['SharesOwned'] * df['AveragePrice']
    df['Current Value'] = df['SharesOwned'] * df['Current Price']
    df['Profit/Loss'] = df['Current Value'] - df['TotalInvestment']
    df['Returns %'] = ((df['Current Value'] - df['TotalInvestment']) / df['TotalInvestment'] * 100).round(2)
    
    # Drop NSE_Symbol column and reorder columns
    columns = ['Stock', 'SharesOwned', 'AveragePrice', 'Current Price', 'TotalInvestment', 
              'Current Value', 'Profit/Loss', 'Returns %']
    result_df = df[columns].copy()
    
    return result_df

def get_portfolio_summary(df: pd.DataFrame) -> Dict:
    """Calculate portfolio summary metrics."""
    total_investment = df['TotalInvestment'].sum()
    current_value = df['Current Value'].sum()
    total_returns = ((current_value - total_investment) / total_investment * 100).round(2)
    
    # Calculate new metrics
    num_stocks = len(df)
    profitable_stocks = len(df[df['Returns %'] > 0])
    
    # Calculate percentage of balance in performing stocks
    performing_stocks_value = df[df['Returns %'] > 0]['Current Value'].sum()
    percent_in_performing = ((performing_stocks_value / current_value) * 100).round(2) if current_value > 0 else 0.0
    
    return {
        'total_investment': total_investment,
        'current_value': current_value,
        'total_returns': total_returns,
        'num_stocks': num_stocks,
        'profitable_stocks': profitable_stocks,
        'percent_in_performing': percent_in_performing
    }

def get_stock_name_from_symbol(symbol: str) -> str:
    """Get the full stock name from NSE symbol using Yahoo Finance."""
    # Custom mapping for common Indian stocks
    custom_name_mapping = {
        'SBIN': 'State Bank Of India',
        'HDFC': 'HDFC Bank Ltd',
        'ICICIBANK': 'ICICI Bank Ltd',
        'INFY': 'Infosys Ltd',
        'TATAMOTORS': 'Tata Motors Ltd',
        'IREDA': 'Indian Renewable Energy Development Agency',
        'IEX': 'Indian Energy Exchange',
        'NHPC': 'NHPC Ltd',
        'NTPC': 'NTPC Ltd',
        'BEL': 'Bharat Electronics Ltd',
        'GAIL': 'GAIL (India) Ltd',
        'LTF': 'L&T Finance Ltd',
        'ITC': 'ITC Ltd',
        'PNB': 'Punjab National Bank',
        'IDBI': 'IDBI Bank Ltd',
    }
    
    # Check if symbol exists in our custom mapping
    if symbol in custom_name_mapping:
        return custom_name_mapping[symbol]
    
    # If not in custom mapping, try Yahoo Finance
    try:
        # Append .NS for NSE symbols
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        
        # Get the long name or short name
        stock_name = info.get('longName', info.get('shortName', ''))
        
        if stock_name:
            return stock_name
        else:
            return symbol  # Return the symbol itself if no name is found
    except Exception as e:
        print(f"Error fetching stock name for {symbol}: {str(e)}")
        return symbol  # Return the symbol itself if any error occurs 