import pandas as pd
import os
import argparse
from datetime import datetime

def convert_holdings_to_csv(excel_file, output_csv=None):
    """
    Convert a mutual funds holdings Excel file to the format needed for the StockPicker app.
    
    Parameters:
    -----------
    excel_file : str
        Path to the Excel file containing mutual fund holdings data
    output_csv : str, optional
        Path where the CSV should be saved. If None, will save to default location.
    
    Returns:
    --------
    str
        Path to the saved CSV file
    """
    try:
        # Check if file exists
        if not os.path.exists(excel_file):
            # Try checking if it's in the MutualFunds directory
            mf_path = os.path.join('assets', 'MutualFunds', os.path.basename(excel_file))
            if os.path.exists(mf_path):
                excel_file = mf_path
            else:
                # Also try absolute path
                abs_mf_path = os.path.join('D:', 'StockPicker', 'assets', 'MutualFunds', os.path.basename(excel_file))
                if os.path.exists(abs_mf_path):
                    excel_file = abs_mf_path
                else:
                    raise FileNotFoundError(f"Could not find Excel file: {excel_file}")
        
        # Read the Excel file - try various ways
        print(f"Reading Excel file: {excel_file}")

        # First, try automatic sheet detection
        try:
            # Try reading the first sheet
            excel_data = pd.read_excel(excel_file, header=None)
            sheet_name = pd.ExcelFile(excel_file).sheet_names[0]
            print(f"Using first sheet: {sheet_name}")
        except Exception as e:
            print(f"Error reading first sheet, trying 'Holdings' sheet: {str(e)}")
            try:
                # Try reading the 'Holdings' sheet explicitly
                excel_data = pd.read_excel(excel_file, sheet_name='Holdings', header=None)
                print("Using 'Holdings' sheet")
            except Exception as e2:
                print(f"Error reading 'Holdings' sheet, trying all sheets: {str(e2)}")
                # Try all sheets and find one with MF data
                xls = pd.ExcelFile(excel_file)
                found_sheet = False
                
                for sheet in xls.sheet_names:
                    try:
                        temp_data = pd.read_excel(excel_file, sheet_name=sheet, header=None)
                        # Check if this sheet contains scheme data
                        for i, row in temp_data.head(20).iterrows():
                            row_data = " ".join([str(cell) for cell in row if cell is not None])
                            if "scheme" in row_data.lower() or "fund" in row_data.lower() or "mutual" in row_data.lower():
                                excel_data = temp_data
                                print(f"Found data in sheet: {sheet}")
                                found_sheet = True
                                break
                        if found_sheet:
                            break
                    except:
                        continue
                
                if not found_sheet:
                    raise ValueError("Could not find any sheet with mutual fund data")
        
        # Now we have the excel_data, let's process it
        
        # Debug info - shape of the data
        print(f"Excel data shape: {excel_data.shape}")
        
        # Try multiple approaches to find the scheme data
        
        # Approach 1: Look for the header row by searching for common column names
        header_row = None
        scheme_col_idx = None
        units_col_idx = None
        
        # Search for header row (look through first 30 rows)
        for i in range(min(30, len(excel_data))):
            row = excel_data.iloc[i]
            # Convert row to strings and clean up
            row_values = [str(val).strip().lower() if val is not None else "" for val in row.values]
            row_text = " ".join(row_values)
            
            # Check if this looks like a header row
            if ("scheme" in row_text and "unit" in row_text) or \
               ("fund" in row_text and "unit" in row_text) or \
               ("scheme name" in row_values) or \
               ("folio" in row_text and "balance" in row_text):
                
                # This could be our header row
                header_row = i
                
                # Find column indices
                for j, val in enumerate(row_values):
                    if "scheme" in val or "fund name" in val or "name" in val:
                        scheme_col_idx = j
                    if "unit" in val or "balance" in val or "holdings" in val:
                        units_col_idx = j
                
                if scheme_col_idx is not None and units_col_idx is not None:
                    print(f"Found header at row {i+1}, scheme col: {scheme_col_idx}, units col: {units_col_idx}")
                    break
        
        if header_row is None:
            # If still not found, try looking for rows with "scheme" or "fund" in them
            for i in range(min(30, len(excel_data))):
                row = excel_data.iloc[i]
                if any("scheme" in str(val).lower() for val in row if val is not None) or \
                   any("fund" in str(val).lower() for val in row if val is not None):
                    print(f"Potential header found at row {i+1}")
                    header_row = i
                    break
        
        # Fall back to a liberal approach if we still haven't found a header
        if header_row is None or scheme_col_idx is None or units_col_idx is None:
            print("Could not find reliable header row. Trying fallback method...")
            
            # Just use the first several rows as candidate headers and look for data patterns
            found_data = False
            test_offset_range = 5  # Try a few different starting rows
            
            for test_header in range(min(10, len(excel_data))):
                for offset in range(test_offset_range):
                    try:
                        # Try this row as header
                        test_df = pd.DataFrame(excel_data.iloc[test_header+offset+1:].values,
                                               columns=excel_data.iloc[test_header])
                        
                        # Find columns that might contain scheme names and units
                        col_candidates = {}
                        for col in test_df.columns:
                            if col is None:
                                continue
                                
                            col_str = str(col).lower()
                            
                            # Check potential scheme name column
                            if "scheme" in col_str or "name" in col_str or "fund" in col_str:
                                # Count non-null values as a quality metric
                                non_null = test_df[col].count()
                                col_candidates[col] = {'type': 'scheme', 'quality': non_null}
                            
                            # Check potential units column
                            elif "unit" in col_str or "balance" in col_str or "holding" in col_str or "quantity" in col_str:
                                # Try to convert to numeric as a quality check
                                try:
                                    numeric_count = pd.to_numeric(test_df[col], errors='coerce').count()
                                    col_candidates[col] = {'type': 'units', 'quality': numeric_count}
                                except:
                                    pass
                        
                        # Find best candidates
                        scheme_cols = {col: info for col, info in col_candidates.items() 
                                      if info['type'] == 'scheme'}
                        units_cols = {col: info for col, info in col_candidates.items() 
                                     if info['type'] == 'units'}
                        
                        if scheme_cols and units_cols:
                            best_scheme_col = max(scheme_cols.items(), key=lambda x: x[1]['quality'])[0]
                            best_units_col = max(units_cols.items(), key=lambda x: x[1]['quality'])[0]
                            
                            # Verify we have enough data
                            if test_df[best_scheme_col].count() >= 10 and test_df[best_units_col].count() >= 10:
                                print(f"Found data with header at row {test_header+1}, offset {offset}")
                                print(f"Scheme column: {best_scheme_col}")
                                print(f"Units column: {best_units_col}")
                                
                                # Create our result dataframe directly
                                result_df = pd.DataFrame({
                                    'Scheme': test_df[best_scheme_col],
                                    'UnitsOwned': test_df[best_units_col]
                                })
                                
                                # Clean and convert units
                                result_df['UnitsOwned'] = pd.to_numeric(result_df['UnitsOwned'], errors='coerce')
                                
                                # Drop rows with NA scheme or units
                                result_df = result_df.dropna(subset=['Scheme', 'UnitsOwned']).reset_index(drop=True)
                                
                                if len(result_df) > 10:  # Make sure we have a reasonable number of funds
                                    # Add empty columns for missing data
                                    result_df['AverageNAV'] = ''  # Not available in Excel
                                    result_df['SchemeCode'] = ''  # Not available in Excel
                                    
                                    # Save to CSV
                                    if output_csv is None:
                                        output_dir = 'assets/PersonalFiles'
                                        os.makedirs(output_dir, exist_ok=True)
                                        output_csv = os.path.join(output_dir, 'myMFPortfolio.csv')
                                    
                                    # Save the data and return
                                    result_df.to_csv(output_csv, index=False)
                                    print(f"Successfully converted mutual fund holdings to: {output_csv}")
                                    print(f"Found {len(result_df)} mutual fund schemes")
                                    return output_csv
                    except Exception as e:
                        # Just try next iteration
                        pass
            
            # If we get here, we couldn't find the data with the fallback method
            raise ValueError("Could not identify mutual fund data in the Excel file with fallback methods")
            
        # Now process the data based on the header we found
        headers = excel_data.iloc[header_row].values
        data_rows = excel_data.iloc[header_row + 1:]
        
        # Create DataFrame
        df = pd.DataFrame(data_rows.values, columns=headers)
        
        # Clean up column names
        df.columns = [str(col).strip() if col is not None else f"Column{i}" 
                       for i, col in enumerate(df.columns)]
        
        # If we already know the scheme and units columns, extract them
        if scheme_col_idx is not None and units_col_idx is not None:
            scheme_col = df.columns[scheme_col_idx] 
            units_col = df.columns[units_col_idx]
        else:
            # Otherwise, try to identify them by name
            scheme_col = None
            units_col = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                if "scheme" in col_lower or "name" in col_lower or "fund" in col_lower:
                    scheme_col = col
                elif "unit" in col_lower or "balance" in col_lower or "holding" in col_lower:
                    units_col = col
        
        if scheme_col is None or units_col is None:
            raise ValueError("Could not identify scheme name and units columns")
                
        # Select and rename relevant columns
        csv_data = df[[scheme_col, units_col]].copy()
        csv_data.columns = ['Scheme', 'UnitsOwned']
        
        # Clean data - drop NAs
        csv_data = csv_data.dropna(subset=['Scheme']).reset_index(drop=True)
        
        # Convert units to numeric
        csv_data['UnitsOwned'] = pd.to_numeric(csv_data['UnitsOwned'], errors='coerce')
        
        # Drop NA units
        csv_data = csv_data.dropna(subset=['UnitsOwned']).reset_index(drop=True)
        
        # Make sure schemes are strings
        csv_data['Scheme'] = csv_data['Scheme'].astype(str)
        
        # Drop any rows with empty schemes
        csv_data = csv_data[csv_data['Scheme'].str.strip() != ''].reset_index(drop=True)
        
        # Add empty columns for missing data
        csv_data['AverageNAV'] = ''  # Not available in Excel
        csv_data['SchemeCode'] = ''  # Not available in Excel
        
        # Save to CSV
        if output_csv is None:
            output_dir = 'assets/PersonalFiles'
            os.makedirs(output_dir, exist_ok=True)
            output_csv = os.path.join(output_dir, 'myMFPortfolio.csv')
            
        csv_data.to_csv(output_csv, index=False)
        print(f"Successfully converted mutual fund holdings to: {output_csv}")
        print(f"Found {len(csv_data)} mutual fund schemes")
        
        return output_csv
        
    except Exception as e:
        print(f"Error converting Excel file: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert mutual fund holdings Excel to CSV format for StockPicker')
    parser.add_argument('excel_file', help='Path to the mutual fund holdings Excel file')
    parser.add_argument('--output', '-o', help='Output CSV file path (optional)')
    
    args = parser.parse_args()
    
    try:
        output_path = convert_holdings_to_csv(args.excel_file, args.output)
        print(f"Conversion completed. CSV saved to: {output_path}")
    except Exception as e:
        print(f"Failed to convert holdings: {str(e)}")
        exit(1) 