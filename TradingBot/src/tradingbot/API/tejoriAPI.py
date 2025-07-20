"""

This module read csv files download from Tejori website

"""


# Path to your Excel file
#excel_file = '/infy.xlsx'

from pathlib import Path
import pandas as pd
import numpy as np
import re
import sys
import os
from datetime import datetime
from openpyxl import load_workbook
from tradingbot.utils.functions.commonFunctions import trim_dataframe  , STATEMENT_MAPPINGS

class TejoriDataProcessor:
    def __init__(self):
        self.column_mappings = STATEMENT_MAPPINGS
        
    def clean_financial_data(self, excel_file):
        """Load and clean financial statements from Excel file."""
        def clean_sheet(sheet_name):
            try:
                # Read raw data to find header row
                df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                
                # Find row with 'dates' (case insensitive)
                header_row = df[df[0].astype(str).str.strip().str.lower() == 'dates'].index[0]
                
                # Read with proper headers
                df = pd.read_excel(excel_file, 
                                 sheet_name=sheet_name, 
                                 header=header_row)
                
                # Clean column names
                df.columns = [re.sub(r'(Less:|\.{3,}|\s+)', ' ', col).strip() 
                            for col in df.columns]
                
                df = df.set_index('dates')
                df.index.name = None
                return df.dropna(how='all').apply(pd.to_numeric, errors='ignore')
            except Exception as e:
                print(f"Error cleaning sheet {sheet_name}: {str(e)}")
                return pd.DataFrame()

        # List all sheets to process
        all_sheets = ['BalanceSheet', 'Profit&Loss', 'CashFlow', 'Ratios']
        
        # Get available sheets in the Excel file
        xl = pd.ExcelFile(excel_file)
        available_sheets = [sheet for sheet in all_sheets if sheet in xl.sheet_names]
        
        return {sheet: clean_sheet(sheet) for sheet in available_sheets}

    def transform_financial_data(self, df):
        """Transpose DataFrame and create Year/Quarter multi-index."""
        try:
            transposed_df = df.transpose()
            transposed_df.index = pd.to_datetime(transposed_df.index, errors='coerce')
            
            # Filter out NaT (invalid dates)
            valid_dates = transposed_df.index.notna()
            transposed_df = transposed_df[valid_dates]
            
            years = transposed_df.index.year
            quarters = 'Q' + transposed_df.index.quarter.astype(str)
            
            transposed_df.index = pd.MultiIndex.from_arrays(
                [years, quarters],
                names=['Year', 'Quarter']
            )
            return transposed_df.sort_index(level=['Year', 'Quarter'], ascending=[False, True])
        except Exception as e:
            print(f"Error transforming data: {str(e)}")
            return df

    def prepare_excel_data(self, df, column_mapping):
        """Rename DataFrame columns based on provided mapping."""
        try:
            result_df = df.copy()
            
            # Only rename columns that exist in the DataFrame
            existing_cols = {k: v for k, v in column_mapping.items() 
                            if k in result_df.columns}
            result_df = result_df.rename(columns=existing_cols)
            
            return result_df
        except Exception as e:
            print(f"Error renaming columns: {str(e)}")
            return df

    def save_to_output(self, df, output_file_path, sheet_name):
        """
        Robust function to save DataFrame to Excel sheet, handling various edge cases.
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            
            if os.path.exists(output_file_path):
                try:
                    # Try reading the existing file first to check if it's valid
                    existing_sheets = pd.ExcelFile(output_file_path).sheet_names
                    
                    # Create a new Excel writer object
                    with pd.ExcelWriter(output_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        df.to_excel(writer, sheet_name=sheet_name)
                except:
                    # If the existing file is corrupted, create a new one
                    print("Existing file appears corrupted, creating new file...")
                    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name=sheet_name)
            else:
                # Create new file
                with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name)
            
            return True
        except Exception as e:
            print(f"Error saving to output: {str(e)}")
            
            # Fallback: Try saving with xlsxwriter engine
            try:
                print("Trying fallback with xlsxwriter engine...")
                with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name=sheet_name)
                return True
            except Exception as fallback_error:
                print(f"Fallback save failed: {str(fallback_error)}")
                return False

    def process_financial_data(self, input_file_path, output_file_path, output_sheet_name,
                                ticker=None, append_to_existing=True):
            """
            Main function to process financial data from input to output.
            
            Args:
                input_file_path (str): Path to input Excel file
                output_file_path (str): Path to output Excel file
                output_sheet_name (str): Base name of sheet to create/update
                ticker (str): Trading symbol to add as a column
                append_to_existing (bool): Whether to append to existing sheet or create new
            """
            try:
                # Step 1: Load and clean data
                print("Loading and cleaning data...")
                sheets_dict = self.clean_financial_data(input_file_path)
                print(f"Found sheets: {list(sheets_dict.keys())}")
                
                # Step 2: Process each sheet
                processed_data = []
                for sheet_name, df in sheets_dict.items():
                    print(f"Processing {sheet_name}...")
                    transformed = self.transform_financial_data(df)
                    renamed = self.prepare_excel_data(transformed, self.column_mappings.get(sheet_name, {}))
                    processed_data.append(renamed)
                
                # Step 3: Combine all data with priority to later sheets
                print("Combining data...")
                # Process sheets in reverse order so later sheets take precedence
                combined_df = pd.concat(processed_data[::-1], axis=1)
                # Keep first occurrence of each column (from later sheets due to reversal)
                combined_df = combined_df.loc[:, ~combined_df.columns.duplicated(keep='first')]
                
                # Step 4: Add trading symbol column if provided
                if ticker:
                    combined_df['tradingsymbol'] = ticker
                
                # Step 5: Reset index before file saving 
                combined_df.reset_index(inplace=True)

                # Step 6: Trim spaces in columns 
                combined_df = trim_dataframe(combined_df)

                # Determine sheet name based on append_to_existing flag
                final_sheet_name = output_sheet_name if append_to_existing else ticker if ticker else output_sheet_name
                
                combined_df['composite_key'] = (
                                                combined_df['tradingsymbol'] + '_' + 
                                                combined_df['Quarter'] + '_' +   
                                                combined_df['Year'].astype(str) 
                                            )
                
                # Step 7: Reorder columns to put key columns first
                # Get list of all columns except our key columns
                other_columns = [col for col in combined_df.columns 
                                if col not in ['composite_key', 'tradingsymbol', 'Year', 'Quarter']]
                
                # Create new column order with key columns first
                new_column_order = ['composite_key','tradingsymbol', 'Year', 'Quarter'] + other_columns
                combined_df = combined_df[new_column_order]
                            
                # Step 7: Handle existing data if appending
                if os.path.exists(output_file_path) and append_to_existing:
                    try:
                        # Read existing data
                        existing_df = pd.read_excel(output_file_path, sheet_name=final_sheet_name)
                        
                        # If ticker is provided, remove existing records for this ticker and matching Year/Quarter
                        if ticker and 'tradingsymbol' in existing_df.columns:
                            # Create composite key for comparison
                            existing_df['composite_key'] = (
                                existing_df['tradingsymbol'] + '_' + 
                                existing_df['Quarter'] + '_' + 
                                existing_df['Year'].astype(str)
                            )
                            
                            # Keep only records that don't match our new data
                            existing_df = existing_df[
                                ~existing_df['composite_key'].isin(combined_df['composite_key'])
                            ]
                            
                        # Concatenate the cleaned existing data with new data
                        combined_df = pd.concat([existing_df, combined_df])
                        combined_df.drop(columns=['composite_key'],inplace=True)


                        # Remove any Unnamed columns (like Unnamed: 0 or Unnamed: 0.1)
                        unnamed_cols = [col for col in combined_df.columns if str(col).startswith('Unnamed:')]
                        if unnamed_cols:
                            combined_df = combined_df.drop(columns=unnamed_cols, errors='ignore')
             
                    except Exception as e:
                        print(f"Error reading existing data, creating new sheet: {str(e)}")
                        # If any error occurs, proceed with just the new data
                
                # Step 8: Save to output
                print(f"Saving to {output_file_path}...")
                if self.save_to_output(combined_df, output_file_path, final_sheet_name):
                    print(f"Successfully processed and saved data to sheet: {final_sheet_name}")
                    return True
                else:
                    print("Failed to save output.")
                    return False
                    
            except Exception as e:
                print(f"Error in processing: {str(e)}")
                return False

if __name__ == "__main__":
    # Example usage
    # Configuration
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    DATA_DIR = os.path.join(ROOT_DIR, "data")
    MASTERS_DIR = os.path.join(DATA_DIR, "input")
    OUTPUT_DIR = os.path.join(DATA_DIR, "output")
    
    input_file = os.path.join(MASTERS_DIR, "adani.xlsx")
    output_file = os.path.join(OUTPUT_DIR, "tejori_financial_results.xlsx")

    output_sheet = "financial"
    tejori_processor = TejoriDataProcessor()
    # Run the complete processing pipeline
    success = tejori_processor.process_financial_data(
        input_file_path=input_file,
        output_file_path=output_file,
        output_sheet_name=output_sheet,
        ticker="ADANI",
        append_to_existing=True
    )
    
    if success:
        print("Processing completed successfully")
    else:
        print("Processing failed")
        sys.exit(1)