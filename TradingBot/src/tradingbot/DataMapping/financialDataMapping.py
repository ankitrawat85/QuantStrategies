"""
financial_mappings.py - Centralized financial data mappings for:
- Standardized column names
- Statement-specific mappings
- Validation requirements
"""

from typing import Dict, List, Set
from collections import defaultdict
import pandas as pd
# ======================
# 1. STANDARD NAME MAPPINGS
# ======================
STANDARD_NAMES = {
    # Balance Sheet Items
    'total_assets': ['Assets', 'total_assets'],
    'non_current_assets': ['Non Current Assets', 'non_current_assets'],
    'gross_ppe': ['Gross Block', 'gross_ppe'],
    'accumulated_depreciation': ['Less: Accumulated Depreciation', 'accumulated_depr'],
    'net_ppe': ['Net Block', 'net_ppe'],
    'lease_adjustment': ['Lease Adjustment A/c'],
    'cwip': ['Capital Work in Progress'],
    'long_term_investments': ['Long Term Investments'],
    'long_term_loans_advances': ['Long Term Loans & Advances'],
    'other_non_current_assets': ['Other Non Current Assets'],
    'current_assets': ['Current Assets', 'current_assets'],
    'inventory': ['Inventory'],
    'accounts_receivable': ['Accounts Receivable'],
    'short_term_investments': ['Short Term Investments'],
    'cash_and_equivalents': ['Cash & Bank Balances'],
    'other_current_assets': ['Other Current Assets'],
    'short_term_loans_advances': ['Short Term Loans and Advances'],
    'total_liabilities_equity': ['Liabilities'],
    'total_equity': ['Shareholders Funds'],
    'share_capital': ['Share Capital'],
    'share_warrants': ['Share Warrants'],
    'reserves_surplus': ['Reserves'],
    'non_current_liabilities': ['Non Current Liabilities'],
    'long_term_debt_secured': ['Secured Loans'],
    'long_term_debt_unsecured': ['Unsecured Loans'],
    'deferred_tax_liabilities': ['Deferred Tax Assets/Liabilities'],
    'other_long_term_liabilities': ['Other Long Term Liabilities'],
    'long_term_provisions': ['Long Term Provisions'],
    'current_liabilities': ['Current Liabilities'],
    'accounts_payable': ['Accounts Payable'],
    'short_term_debt': ['Short Term Loans'],
    'other_current_liabilities': ['Other Current Liabilities'],
    'short_term_provisions': ['Short Term Provisions'],

    # P&L Items
    'gross_sales': ['Gross Sales'],
    'excise_duty': ['Less: Excise Duty'],
    'revenue': ['Net Sales', 'Total Revenue'],
    'raw_material_costs': ['Raw Material'],
    'material_cost_pct': ['Material Cost (%)'],
    'inventory_change': ['Increase/Decrease in Stock'],
    'other_manufacturing_costs': ['Other Manufacturing Expenses'],
    'employee_costs': ['Employee Cost'],
    'sales_marketing_costs': ['Selling and Distribution Expenses'],
    'energy_costs': ['Power & Fuel Cost'],
    'admin_costs': ['General and Administration Expenses'],
    'other_operating_expenses': ['Miscellaneous Expenses'],
    'operating_profit': ['Operating Profit'],
    'operating_margin_pct': ['OPM (%)'],
    'other_income': ['Other Income'],
    'interest_expense': ['Interest'],
    'profit_before_depreciation_tax': ['PBDT'],
    'depreciation_amortization': ['Depreciation and Amortization'],
    'ebt': ['Profit Before Taxation & Exceptional Items'],
    'exceptional_items': ['Exceptional Income / Expenses'],
    'pbt': ['Profit Before Tax'],
    'total_tax': ['Provision for Taxs'],
    'current_tax': ['Current Income Tax'],
    'deferred_tax': ['Deferred Tax'],
    'other_taxes': ['Other taxes'],
    'net_income': ['Profit After Tax', 'net_profit'],
    'extraordinary_items': ['Extra items'],
    'minority_interest': ['Minority Interest'],
    'associate_income': ['Share of Associate'],
    'shares_outstanding': ['Number of shares(Crs)'],
    'dividend_payout_ratio': ['Dividend Payout Ratio(%)'],

    # Cash Flow Items
    'total_operating_cash_flow': ['Cash from Operating Activity'],
    'non_cash_adjustments': ['Adjustments'],
    'operating_cf_before_wc': ['OCF Before Working Capital'],
    'working_capital_changes': ['Working Capital Changes'],
    'taxes_paid': ['Taxes Paid'],
    'total_investing_cash_flow': ['Cash from Investing Activity'],
    'net_capex': ['Net Fixed Assets Purchased'],
    'fixed_assets_purchased': ['Fixed Assets Purchased'],
    'fixed_assets_sold': ['Fixed Assets Sold'],
    'investments_purchased': ['Investment Purchased'],
    'investments_sold': ['Investment Sold'],
    'interest_received': ['Interest Received'],
    'dividends_received': ['Dividends Received'],
    'subsidiary_investments': ['Subsidiary Investments'],
    'total_financing_cash_flow': ['Cash from Financing Activity'],
    'equity_issuance': ['Proceeds From Shares'],
    'net_debt_issued': ['Net Long Term Borrowings'],
    'debt_issued': ['Proceeds From Borrowings'],
    'debt_repayment': ['Repayment From Borrowings'],
    'interest_paid': ['Interest Paid'],
    'dividends_paid': ['Dividend Paid'],
    'net_cash_flow': ['Net Cash Flow'],
    'cash_at_beginning': ['Opening Cash & Cash Equivalents'],
    'fx_impact': ['Effect of FX'],
    'cash_at_end': ['Closing Cash & Cash Equivalents'],
    'net_capex_estimated': ['Net Capex (est)'],
    'fcf_estimated': ['Free Cash Flow (est)'],

    # Ratios
    'quick_ratio': ['Quick Ratio'],
    'liquid_assets': ['Liquid Assets (Crs)'],
    'current_ratio': ['Current Ratio'],
    'interest_coverage': ['Interest Coverage Ratio'],
    'ebit': ['EBIT (Crs)'],
    'fixed_asset_turnover': ['Fixed Asset Turnover'],
    'net_sales': ['Net Sales (Crs)'],
    'fixed_assets': ['Fixed Assets (Crs)'],
    'cash_conversion_cycle': ['Cash Conversion Cycle'],
    'inventory_days': ['Inventory Days'],
    'days_receivable': ['Days Receivable'],
    'days_payable': ['Days Payable'],
    'debt_to_equity': ['Debt to Equity Ratio'],
    'total_debt': ['Total Debt (Crs)'],
    'shareholders_equity': ['Shareholders Equity (Crs)'],
    'fcf_to_sales': ['Free Cash Flow/Sales (%)'],
    'gross_margin_pct': ['Gross Margin (%)'],
    'roce_pct': ['ROCE (%)'],
    'capital_employed': ['Capital Employed (Crs)'],
    'roa_pct': ['Return on Assets (%)'],
    'roic_pct': ['ROIC (%)'],
    'nopat': ['Op Profit after Taxes (Crs)'],
    'invested_capital': ['Invested Capital (Crs)'],
    'roe_pct': ['ROE (%)'],
    'asset_turnover': ['Asset Turnover ratio'],
    'equity_multiplier': ['Equity Multiplier'],
    'adjusted_eps': ['Adjusted EPS'],
    'pe_ratio': ['P/E'],
    'price_to_book': ['Price to Book'],
    'ev_ebitda': ['EV/EBITDA'],
    'dividend_yield_pct': ['Dividend Yield (%)'],

    # Quarterly Results
    'eps': ['EPS'],
    'dividend_per_share': ['Dividend per Share'],
    'book_value': ['Book Value']
}

# ======================
# 2. STATEMENT MAPPINGS
# ======================
STATEMENT_MAPPINGS = {
    'BalanceSheet': {
        'Assets': 'total_assets',
        'Non Current Assets': 'non_current_assets',
        'Gross Block': 'gross_ppe',
        'Less: Accumulated Depreciation': 'accumulated_depreciation',
        'Less: Impairment of Assets': 'impairment_losses',
        'Net Block': 'net_ppe',
        'Lease Adjustment A/c': 'lease_adjustment',
        'Capital Work in Progress': 'cwip',
        'Long Term Investments': 'long_term_investments',
        'Long Term Loans & Advances': 'long_term_loans_advances',
        'Other Non Current Assets': 'other_non_current_assets',
        'Current Assets': 'current_assets',
        'Inventory': 'inventory',
        'Accounts Receivable': 'accounts_receivable',
        'Short Term Investments': 'short_term_investments',
        'Cash & Bank Balances': 'cash_and_equivalents',
        'Other Current Assets': 'other_current_assets',
        'Short Term Loans and Advances': 'short_term_loans_advances',
        'Liabilities': 'total_liabilities_equity',
        'Shareholders Funds': 'total_equity',
        'Share Capital': 'share_capital',
        'Share Warrants': 'share_warrants',
        'Reserves': 'reserves_surplus',
        'Non Current Liabilities': 'non_current_liabilities',
        'Secured Loans': 'long_term_debt_secured',
        'Unsecured Loans': 'long_term_debt_unsecured',
        'Deferred Tax Assets/Liabilities': 'deferred_tax_liabilities',
        'Other Long Term Liabilities': 'other_long_term_liabilities',
        'Long Term Provisions': 'long_term_provisions',
        'Current Liabilities': 'current_liabilities',
        'Accounts Payable': 'accounts_payable',
        'Short Term Loans': 'short_term_debt',
        'Other Current Liabilities': 'other_current_liabilities',
        'Short Term Provisions': 'short_term_provisions'
    },
    'ProfitAndLoss': {
        'Gross Sales': 'gross_sales',
        'Less: Excise Duty': 'excise_duty',
        'Net Sales': 'revenue',
        'Raw Material': 'raw_material_costs',
        'Material Cost (%)': 'material_cost_pct',
        'Increase/Decrease in Stock': 'inventory_change',
        'Other Manufacturing Expenses': 'other_manufacturing_costs',
        'Employee Cost': 'employee_costs',
        'Selling and Distribution Expenses': 'sales_marketing_costs',
        'Power & Fuel Cost': 'energy_costs',
        'General and Administration Expenses': 'admin_costs',
        'Miscellaneous Expenses': 'other_operating_expenses',
        'Operating Profit': 'operating_profit',
        'OPM (%)': 'operating_margin_pct',
        'Other Income': 'other_income',
        'Interest': 'interest_expense',
        'PBDT': 'profit_before_depreciation_tax',
        'Depreciation and Amortization': 'depreciation_amortization',
        'Profit Before Taxation & Exceptional Items': 'ebt',
        'Exceptional Income / Expenses': 'exceptional_items',
        'Profit Before Tax': 'pbt',
        'Provision for Taxs': 'total_tax',
        'Current Income Tax': 'current_tax',
        'Deferred Tax': 'deferred_tax',
        'Other taxes': 'other_taxes',
        'Profit After Tax': 'net_income',
        'Extra items': 'extraordinary_items',
        'Minority Interest': 'minority_interest',
        'Share of Associate': 'associate_income',
        'Net Profit': 'net_profit',
        'Number of shares(Crs)': 'shares_outstanding',
        'Dividend Payout Ratio(%)': 'dividend_payout_ratio'
    },
    'CashFlow': {
        'Cash from Operating Activity': 'total_operating_cash_flow',
        'Profit Before Tax': 'pbt',
        'Adjustments': 'non_cash_adjustments',
        'OCF Before Working Capital': 'operating_cf_before_wc',
        'Working Capital Changes': 'working_capital_changes',
        'Taxes Paid': 'taxes_paid',
        'Cash from Investing Activity': 'total_investing_cash_flow',
        'Net Fixed Assets Purchased': 'net_capex',
        'Fixed Assets Purchased': 'fixed_assets_purchased',
        'Fixed Assets Sold': 'fixed_assets_sold',
        'Investment Purchased': 'investments_purchased',
        'Investment Sold': 'investments_sold',
        'Interest Received': 'interest_received',
        'Dividends Received': 'dividends_received',
        'Subsidiary Investments': 'subsidiary_investments',
        'Cash from Financing Activity': 'total_financing_cash_flow',
        'Proceeds From Shares': 'equity_issuance',
        'Net Long Term Borrowings': 'net_debt_issued',
        'Proceeds From Borrowings': 'debt_issued',
        'Repayment From Borrowings': 'debt_repayment',
        'Interest Paid': 'interest_paid',
        'Dividend Paid': 'dividends_paid',
        'Net Cash Flow': 'net_cash_flow',
        'Opening Cash & Cash Equivalents': 'cash_at_beginning',
        'Effect of FX': 'fx_impact',
        'Closing Cash & Cash Equivalents': 'cash_at_end',
        'Net Capex (est)': 'net_capex_estimated',
        'Free Cash Flow (est)': 'fcf_estimated'
    },
    'Ratios': {
        'Quick Ratio': 'quick_ratio',
        'Liquid Assets (Crs)': 'liquid_assets',
        'Current Liabilities (Crs)': 'current_liabilities',
        'Current Ratio': 'current_ratio',
        'Current Assets (Crs)': 'current_assets',
        'Interest Coverage Ratio': 'interest_coverage',
        'EBIT (Crs)': 'ebit',
        'Interest Expenses (Crs)': 'interest_expense',
        'Fixed Asset Turnover': 'fixed_asset_turnover',
        'Net Sales (Crs)': 'net_sales',
        'Fixed Assets (Crs)': 'fixed_assets',
        'Cash Conversion Cycle': 'cash_conversion_cycle',
        'Inventory Days': 'inventory_days',
        'Days Receivable': 'days_receivable',
        'Days Payable': 'days_payable',
        'Debt to Equity Ratio': 'debt_to_equity',
        'Total Debt (Crs)': 'total_debt',
        'Shareholders Equity (Crs)': 'shareholders_equity',
        'Free Cash Flow/Sales (%)': 'fcf_to_sales',
        'Free Cash Flow(est) (Crs)': 'fcf_estimated',
        'Gross Margin (%)': 'gross_margin_pct',
        'Op Profit Margin (%)': 'operating_margin_pct',
        'Operating Profit (Crs)': 'operating_profit',
        'Net Profit Margin (%)': 'net_margin_pct',
        'Net Profit (Crs)': 'net_profit',
        'ROCE (%)': 'roce_pct',
        'Capital Employed (Crs)': 'capital_employed',
        'Return on Assets (%)': 'roa_pct',
        'Total Assets (Crs)': 'total_assets',
        'ROIC (%)': 'roic_pct',
        'Op Profit after Taxes (Crs)': 'nopat',
        'Invested Capital (Crs)': 'invested_capital',
        'ROE (%)': 'roe_pct',
        'Net Profit Margin (%)': 'net_margin_pct',
        'Asset Turnover ratio': 'asset_turnover',
        'Equity Multiplier': 'equity_multiplier',
        'Adjusted EPS': 'adjusted_eps',
        'P/E': 'pe_ratio',
        'Price to Book': 'price_to_book',
        'EV/EBITDA': 'ev_ebitda',
        'Dividend Yield (%)': 'dividend_yield_pct'
    },
    'QuarterlyResults': {
        'EPS': 'eps',
        'Dividend per Share': 'dividend_per_share',
        'Book Value': 'book_value'
    }
}

# ======================
# 3. VALIDATION REQUIREMENTS
# ======================
VALIDATION_REQUIREMENTS = {
    'BalanceSheet': {
        'required': ['total_assets', 'total_liabilities_equity'],
        'recommended': ['current_assets', 'current_liabilities']
    },
    'ProfitAndLoss': {
        'required': ['revenue', 'net_income'],
        'recommended': ['gross_profit', 'operating_profit']
    },
    'CashFlow': {
        'required': ['total_operating_cash_flow'],
        'recommended': ['net_cash_flow']
    },
    'FScore': {
        'required': [
            'total_assets', 'current_assets', 'current_liabilities',
            'net_income', 'total_operating_cash_flow', 'gross_profit'
        ]
    }
}


# F-Score specific requirements
F_SCORE_REQUIREMENTS = {
    'required': [
        'total_assets', 'current_assets', 'current_liabilities',
        'total_liabilities_equity', 'net_income', 'total_operating_cash_flow',
        'gross_profit', 'revenue', 'shares_outstanding'
    ],
    'optional': [
        'long_term_debt', 'debt_to_equity', 'fixed_assets'
    ]
}


# ======================
# 4. UTILITY FUNCTIONS
# ======================
def get_standard_name(raw_name: str) -> str:
    """Convert any financial metric name to standard name"""
    for std_name, aliases in STANDARD_NAMES.items():
        if raw_name in aliases:
            return std_name
    return raw_name  # fallback to original name

def get_statement_mapping(statement_type: str) -> Dict[str, str]:
    """Get column mappings for specific financial statement"""
    return STATEMENT_MAPPINGS.get(statement_type, {})

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Convert dataframe columns to standardized names"""
    return df.rename(columns=lambda x: get_standard_name(str(x).strip()))


def validate_dataframe(df, requirements: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Validate dataframe against requirements
    Returns: {
        'missing_required': [...],
        'missing_recommended': [...],
        'zero_values': [...],
        'null_values': [...]
    }
    """
    results = defaultdict(list)
    available_cols = set(df.columns)
    
    # Check for missing columns
    for col in requirements.get('required', []):
        if not any(alias in available_cols for alias in STANDARD_NAMES.get(col, [col])):
            results['missing_required'].append(col)
    
    for col in requirements.get('recommended', []):
        if not any(alias in available_cols for alias in STANDARD_NAMES.get(col, [col])):
            results['missing_recommended'].append(col)
    
    # Check data quality
    for col in df.columns:
        std_name = get_standard_name(col)
        if df[col].isnull().any():
            results['null_values'].append(std_name)
        if (df[col] == 0).any():
            results['zero_values'].append(std_name)
    
    return dict(results)

def standardize_dataframe(df, statement_type: str = None) -> pd.DataFrame:
    """
    Convert dataframe columns to standardized names
    Optionally filter to specific statement type columns
    """
    # First standardize all columns
    df_std = df.rename(columns=get_standard_name)
    
    # Filter to statement-specific columns if requested
    if statement_type:
        valid_columns = set(STATEMENT_MAPPINGS.get(statement_type, {}).values())
        return df_std[[col for col in df_std.columns if col in valid_columns]]
    
    return df_std