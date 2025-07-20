from tradingbot.API.tejoriAPI import process_financial_data
import os


# Example usage
MASTERS_DIR = '/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot/data/input'
OUTPUT_DIR  = '/Users/ankit/Desktop/GitHub/AlgoTrading/QuantStrategies/TradingBot/data/output'

input_file = os.path.join(MASTERS_DIR, "infy.xlsx")
output_file = os.path.join(OUTPUT_DIR, "tejori_financial_results.xlsx")
output_sheet = "infy"

# Run the complete processing pipeline
success = process_financial_data(
    input_file_path=input_file,
    output_file_path=output_file,
    output_sheet_name=output_sheet
)
