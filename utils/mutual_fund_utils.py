import pandas as pd
from typing import Dict
import time
import requests
import json
import os
from datetime import datetime

def get_mf_nav(scheme_code: str) -> float:
    """Get latest NAV for a mutual fund scheme using AMFI API."""
    try:
        # Using AMFI API to get latest NAV
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        
        # Extract the latest NAV
        if 'data' in data and len(data['data']) > 0:
            latest_nav = data['data'][0]['nav']
            return float(latest_nav)
        
        # If no NAV found, return 0
        return 0
            
    except Exception as e:
        print(f"Error fetching NAV for scheme {scheme_code}: {str(e)}")
        return 0

def use_dummy_mf_data_for_testing():
    """Create dummy NAVs for testing - only used if API calls fail."""
    # Map of dummy NAVs based on common schemes
    return {
        '119598': 45.12,  # SBI Blue Chip Fund
        '119551': 57.80,  # Axis Bluechip Fund
        '120505': 110.25,  # HDFC Index Fund-NIFTY 50 Plan
        '122639': 85.45,  # Mirae Asset Large Cap Fund
        '119609': 76.30,  # ICICI Prudential Bluechip Fund
        '119533': 65.20,  # Kotak Standard Multicap Fund
        '120178': 155.90,  # UTI Nifty Index Fund
        '118759': 92.35,  # Aditya Birla Sun Life Frontline Equity Fund
        '100356': 125.60,  # HDFC Mid-Cap Opportunities Fund
        '118560': 84.70,  # ICICI Prudential Value Discovery Fund
    }

def get_mf_info(scheme_code: str) -> Dict:
    """Get detailed information for a mutual fund scheme."""
    try:
        # Using AMFI API to get scheme info
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        
        if 'meta' in data:
            return {
                'scheme_name': data['meta'].get('scheme_name', ''),
                'fund_house': data['meta'].get('fund_house', ''),
                'scheme_type': data['meta'].get('scheme_type', ''),
                'scheme_category': data['meta'].get('scheme_category', ''),
                'scheme_code': data['meta'].get('scheme_code', '')
            }
        
        return {
            'scheme_name': '',
            'fund_house': '',
            'scheme_type': '',
            'scheme_category': '',
            'scheme_code': scheme_code
        }
            
    except Exception as e:
        print(f"Error fetching info for scheme {scheme_code}: {str(e)}")
        return {
            'scheme_name': '',
            'fund_house': '',
            'scheme_type': '',
            'scheme_category': '',
            'scheme_code': scheme_code
        }

def get_scheme_name_from_code(scheme_code: str) -> str:
    """Get the scheme name from scheme code using AMFI API."""
    # Custom mapping for common mutual funds
    custom_name_mapping = {
        '119598': 'SBI Blue Chip Fund-Direct Plan-Growth',
        '119551': 'Axis Bluechip Fund Direct Plan Growth',
        '120505': 'HDFC Index Fund-NIFTY 50 Plan Direct Plan',
        '122639': 'Mirae Asset Large Cap Fund Direct Growth',
        '119609': 'ICICI Prudential Bluechip Fund Direct Plan Growth',
        '119533': 'Kotak Standard Multicap Fund Direct Plan Growth',
        '120178': 'UTI Nifty Index Fund Direct Growth Plan',
        '118759': 'Aditya Birla Sun Life Frontline Equity Fund Direct Growth',
        '100356': 'HDFC Mid-Cap Opportunities Fund Direct Plan Growth',
        '118560': 'ICICI Prudential Value Discovery Fund Direct Plan Growth',
    }
    
    # Check if scheme code exists in our custom mapping
    if scheme_code in custom_name_mapping:
        return custom_name_mapping[scheme_code]
    
    # If not in custom mapping, try AMFI API
    try:
        # Get scheme info
        scheme_info = get_mf_info(scheme_code)
        
        # Get the scheme name
        scheme_name = scheme_info.get('scheme_name', '')
        
        if scheme_name:
            return scheme_name
        else:
            return scheme_code  # Return the code itself if no name is found
    except Exception as e:
        print(f"Error fetching scheme name for {scheme_code}: {str(e)}")
        return scheme_code  # Return the code itself if any error occurs

def load_mf_portfolio_data() -> pd.DataFrame:
    """Load and process mutual fund portfolio data from CSV."""
    # Create directory if it doesn't exist
    os.makedirs('assets/PersonalFiles', exist_ok=True)
    
    # Create the file with sample data if it doesn't exist
    csv_path = 'assets/PersonalFiles/myMFPortfolio.csv'
    if not os.path.exists(csv_path):
        sample_data = pd.DataFrame({
            'Scheme': ['SBI Blue Chip Fund-Direct Plan-Growth', 
                      'Axis Bluechip Fund Direct Plan Growth',
                      'HDFC Index Fund-NIFTY 50 Plan Direct Plan'],
            'UnitsOwned': [123.45, 89.67, 210.34],
            'AverageNAV': [39.75, 52.45, 98.60],
            'SchemeCode': ['119598', '119551', '120505']
        })
        sample_data.to_csv(csv_path, index=False)
    
    # Read the portfolio data
    df = pd.read_csv(csv_path)
    
    # Get dummy data ready for any schemes that fail
    dummy_navs = use_dummy_mf_data_for_testing()
    
    # Try to get live NAVs with fallback to dummy data
    navs = {}
    for scheme_code in df['SchemeCode'].unique():
        # Try to get the NAV
        nav = get_mf_nav(scheme_code)
        
        # If NAV fetch failed, use dummy data without retrying
        if nav == 0:
            nav = dummy_navs.get(scheme_code, 0)
            
        navs[scheme_code] = nav
        time.sleep(0.5)  # Add delay between requests to avoid rate limiting
    
    # Add NAV data to dataframe
    df['Current NAV'] = df['SchemeCode'].map(navs)
    
    # Calculate investment metrics
    df['TotalInvestment'] = df['UnitsOwned'] * df['AverageNAV']
    df['Current Value'] = df['UnitsOwned'] * df['Current NAV']
    df['Profit/Loss'] = df['Current Value'] - df['TotalInvestment']
    df['Returns %'] = ((df['Current Value'] - df['TotalInvestment']) / df['TotalInvestment'] * 100).round(2)
    
    # Reorder columns
    columns = ['Scheme', 'UnitsOwned', 'AverageNAV', 'Current NAV', 'TotalInvestment', 
              'Current Value', 'Profit/Loss', 'Returns %']
    result_df = df[columns].copy()
    
    return result_df

def get_mf_portfolio_summary(df: pd.DataFrame) -> Dict:
    """Calculate mutual fund portfolio summary metrics."""
    total_investment = df['TotalInvestment'].sum()
    current_value = df['Current Value'].sum()
    total_returns = ((current_value - total_investment) / total_investment * 100).round(2) if total_investment > 0 else 0.0
    
    # Calculate new metrics
    num_schemes = len(df)
    profitable_schemes = len(df[df['Returns %'] > 0])
    
    # Calculate percentage of balance in performing schemes
    performing_schemes_value = df[df['Returns %'] > 0]['Current Value'].sum()
    percent_in_performing = ((performing_schemes_value / current_value) * 100).round(2) if current_value > 0 else 0.0
    
    return {
        'total_investment': total_investment,
        'current_value': current_value,
        'total_returns': total_returns,
        'num_schemes': num_schemes,
        'profitable_schemes': profitable_schemes,
        'percent_in_performing': percent_in_performing
    } 