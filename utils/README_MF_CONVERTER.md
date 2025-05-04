# Mutual Fund Holdings Excel to CSV Converter

This utility script helps you convert your mutual fund holdings excel file into the CSV format used by the StockPicker application.

## Usage

### From Command Line

```bash
python utils/mf_excel_converter.py path/to/your/Holdings_Statement.xlsx
```

Optional arguments:
- `--output` or `-o`: Specify a custom output path (default is `assets/PersonalFiles/myMFPortfolio.csv`)

Example:
```bash
python utils/mf_excel_converter.py path/to/your/Holdings_Statement.xlsx --output custom_output.csv
```

### Smart File Location

The converter will look for your Excel file in the following locations:
1. The exact path you specified
2. In the `assets/MutualFunds/` directory 
3. In the `D:/StockPicker/assets/MutualFunds/` directory

So you can also place your holdings files in the MutualFunds directory and simply refer to the filename:

```bash
python utils/mf_excel_converter.py Holdings_Statement.xlsx
```

### From Python Code

You can also import and use the function directly in your Python code:

```python
from utils.mf_excel_converter import convert_holdings_to_csv

# Convert the Excel file to CSV
convert_holdings_to_csv('Holdings_Statement.xlsx')

# Or specify a custom output path
convert_holdings_to_csv('Holdings_Statement.xlsx', 'custom_output.csv')
```

## Excel File Format

The script is designed to work with standard mutual fund holdings statement Excel files that have:

1. A sheet named 'Holdings'
2. A header row containing "HOLDINGS AS ON [DATE]"
3. Column headers that include "Scheme Name" and "Units"

If your Excel file has a different format, you may need to adjust the script accordingly.

## Note

This converter will extract the scheme names and units owned from your Excel file. However, it can't extract the average NAV or scheme code information, so these fields will be left blank in the resulting CSV. You'll need to fill these in manually if required.

## Troubleshooting

If you encounter errors:

1. Make sure your Excel file has a sheet named 'Holdings'
2. Check that the Excel file contains columns for scheme name and units
3. If the structure is different from what the script expects, you may need to modify the script to adapt to your specific Excel format 