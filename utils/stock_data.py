import yfinance as yf
import pandas as pd
from typing import Dict, List
import json

def get_stock_info(symbols: List[str]) -> Dict:
    """Fetch detailed information for given stock symbols."""
    stock_info = {}
    
    for symbol in symbols:
        try:
            # Append .NS for NSE symbols
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info
            
            stock_info[symbol] = {
                'sector': info.get('sector', 'Others'),
                'marketCap': info.get('marketCap', 0),
                'industry': info.get('industry', 'Others')
            }
        except:
            stock_info[symbol] = {
                'sector': 'Others',
                'marketCap': 0,
                'industry': 'Others'
            }
    
    return stock_info

def calculate_portfolio_metrics(df: pd.DataFrame) -> Dict:
    """Calculate portfolio metrics including sector distribution."""
    # Get stock info for all symbols
    symbols = df['NSE_Symbol'].tolist()
    stock_info = get_stock_info(symbols)
    
    # Calculate total investment per stock
    df['TotalInvestment'] = df['SharesOwned'] * df['AveragePrice']
    total_portfolio_value = df['TotalInvestment'].sum()
    
    # Calculate sector distribution
    sector_distribution = {}
    for index, row in df.iterrows():
        symbol = row['NSE_Symbol']
        investment = row['TotalInvestment']
        sector = stock_info[symbol]['sector']
        
        if sector in sector_distribution:
            sector_distribution[sector] += investment
        else:
            sector_distribution[sector] = investment
    
    # Convert to percentages
    sector_distribution = {
        k: round((v / total_portfolio_value) * 100, 2)
        for k, v in sector_distribution.items()
    }
    
    # Sort sectors by percentage
    sector_distribution = dict(sorted(
        sector_distribution.items(),
        key=lambda x: x[1],
        reverse=True
    ))
    
    return {
        'category_distribution': {
            'Equity': 100,
            'Debt': 0,
            'Hybrid': 0,
            'Others': 0
        },
        'sector_distribution': sector_distribution,
        'stock_info': stock_info
    } 