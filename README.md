# Wall-ET

A modern, interactive financial dashboard built with Plotly Dash for tracking your stock portfolio, mutual funds, loans, credit cards, and other investments.

## Features

- Portfolio Overview
  - Net worth trajectory
  - Asset allocation
  - Current portfolio status

- Stock Portfolio
  - Interactive datatable with sorting/filtering
  - Performance tracking
  - Price comparison

- Mutual Funds
  - Fund performance tracking
  - NAV history
  - Investment analysis

- Other Investments
  - Track alternative investments
  - Performance metrics

- Loans
  - Loan tracking and analysis
  - Payment schedules

- Credit Cards
  - Credit card management
  - Balance tracking

- Savings Accounts
  - Interest tracking
  - Balance management

- Market Data
  - Market trends and analysis
  - Stock performance metrics

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Wall-ET.git
cd Wall-ET
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Prepare your data files:
   - Place your data files in the appropriate subdirectories under the `assets` folder
   - See subdirectories for specific data formats required

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to `http://127.0.0.1:8050`

## Data Organization

The application expects data files in the following locations:
- `assets/Stocks/` - Stock portfolio data
- `assets/MutualFunds/` - Mutual fund data
- `assets/OtherInvestments/` - Other investment data
- `assets/SavingsAccounts/` - Savings account data
- `assets/CreditCards/` - Credit card data
- `assets/PersonalFiles/` - Personal financial data

## Security Note

This application is designed for local use. For production deployment:
1. Implement proper authentication
2. Use secure data storage
3. Enable HTTPS
4. Follow security best practices for handling financial data

## Utilities

The application includes several utility scripts in the `utils` directory:
- `mf_excel_converter.py` - Convert mutual fund data from Excel format
- `mutual_fund_utils.py` - Utilities for handling mutual fund data
- `portfolio_utils.py` - Portfolio management utilities
- `stock_data.py` - Stock data handling utilities

## Requirements

See `requirements.txt` for a full list of dependencies. Key components include:
- dash==2.15.0
- dash-bootstrap-components==1.5.0
- pandas==2.1.2
- plotly==5.18.0
- yfinance==0.2.33

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 