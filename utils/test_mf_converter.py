import os
import sys
from mf_excel_converter import convert_holdings_to_csv
import pandas as pd

def test_mf_converter(excel_file, output_csv=None):
    """
    Test the mutual fund holdings converter and show detailed results
    """
    print("="*80)
    print(f"TESTING MUTUAL FUND CONVERTER WITH: {excel_file}")
    print("="*80)
    
    try:
        # Run the converter
        result_path = convert_holdings_to_csv(excel_file, output_csv)
        
        # Read the resulting CSV
        result_df = pd.read_csv(result_path)
        
        # Show statistics
        print("\nCONVERSION RESULTS:")
        print(f"- Total mutual funds found: {len(result_df)}")
        
        # Show first 5 schemes
        print("\nFIRST 5 SCHEMES:")
        for i, row in result_df.head(5).iterrows():
            print(f"{i+1}. {row['Scheme']} ({row['UnitsOwned']} units)")
            
        # Show last 5 schemes
        if len(result_df) > 5:
            print("\nLAST 5 SCHEMES:")
            for i, row in result_df.tail(5).iterrows():
                print(f"{i+1}. {row['Scheme']} ({row['UnitsOwned']} units)")
        
        print("\nCONVERSION SUCCESSFUL!")
        print(f"Results saved to: {result_path}")
        return True
    
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nCONVERSION FAILED!")
        return False

if __name__ == "__main__":
    # Check if filename was provided
    if len(sys.argv) < 2:
        print("Usage: python test_mf_converter.py <excel_file> [output_csv]")
        sys.exit(1)
    
    # Get parameters
    excel_file = sys.argv[1]
    output_csv = None if len(sys.argv) < 3 else sys.argv[2]
    
    # Run the test
    success = test_mf_converter(excel_file, output_csv)
    sys.exit(0 if success else 1) 