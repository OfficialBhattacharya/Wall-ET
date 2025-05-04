import dash
from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import os
from datetime import datetime

# Register the page - but not in the nav since it's a sub-tab
dash.register_page(
    __name__,
    path='/loans',
    name='Loans',
    title='Loans',
    icon='money-bill-alt',
    order=7,
    nav=False
)

# Load data - create empty table if file doesn't exist
def load_loans_data():
    # Check if file exists
    csv_path = 'assets/PersonalFiles/myLoans.csv'
    os.makedirs('assets/PersonalFiles', exist_ok=True)
    
    if os.path.exists(csv_path):
        # Read the data if file exists
        df = pd.read_csv(csv_path)
        
        # Calculate additional metrics if data exists
        if not df.empty and all(col in df.columns for col in ['Principal', 'OutstandingAmount', 'EndDate']):
            today = datetime.today().strftime('%Y-%m-%d')
            
            # Calculate remaining months (simple approximation)
            if 'EndDate' in df.columns:
                df['EndDateObj'] = pd.to_datetime(df['EndDate'])
                df['TodayObj'] = pd.to_datetime(today)
                df['RemainingMonths'] = ((df['EndDateObj'].dt.year - df['TodayObj'].dt.year) * 12 + 
                                      (df['EndDateObj'].dt.month - df['TodayObj'].dt.month))
            
            # Calculate amount paid so far
            df['AmountPaid'] = df['Principal'] - df['OutstandingAmount']
            
            # Calculate progress percentage
            df['Progress'] = ((df['AmountPaid'] / df['Principal']) * 100).round(2)
            
            # Clean up temporary columns if they exist
            if 'EndDateObj' in df.columns and 'TodayObj' in df.columns:
                df = df.drop(['EndDateObj', 'TodayObj'], axis=1)
    else:
        # Create empty DataFrame with correct columns
        df = pd.DataFrame(columns=[
            'LoanType', 'Lender', 'Principal', 'OutstandingAmount', 'InterestRate', 
            'EMI', 'Tenure', 'StartDate', 'EndDate'
        ])
        # Save the empty file
        df.to_csv(csv_path, index=False)
    
    return df

# Load data
df = load_loans_data()

# Calculate summary metrics
def get_summary(df):
    if df.empty or 'Principal' not in df.columns:
        return {
            'total_principal': 0,
            'total_outstanding': 0,
            'total_paid': 0,
            'total_emi': 0,
            'num_loans': 0
        }
    
    total_principal = df['Principal'].sum()
    total_outstanding = df['OutstandingAmount'].sum() if 'OutstandingAmount' in df.columns else 0
    total_paid = df['AmountPaid'].sum() if 'AmountPaid' in df.columns else 0
    total_emi = df['EMI'].sum() if 'EMI' in df.columns else 0
    
    return {
        'total_principal': total_principal,
        'total_outstanding': total_outstanding,
        'total_paid': total_paid,
        'total_emi': total_emi,
        'num_loans': len(df)
    }

summary = get_summary(df)

# Create the DataTable
table = dash_table.DataTable(
    id='loans-table',
    columns=[
        {'name': 'Loan Type', 'id': 'LoanType', 'type': 'text'},
        {'name': 'Lender', 'id': 'Lender', 'type': 'text'},
        {'name': 'Principal', 'id': 'Principal', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Outstanding', 'id': 'OutstandingAmount', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Amount Paid', 'id': 'AmountPaid', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Progress %', 'id': 'Progress', 'type': 'numeric',
         'format': {'specifier': '.2f'}},
        {'name': 'Interest Rate %', 'id': 'InterestRate', 'type': 'numeric',
         'format': {'specifier': '.2f'}},
        {'name': 'EMI', 'id': 'EMI', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Tenure (years)', 'id': 'Tenure', 'type': 'numeric'},
        {'name': 'Remaining Months', 'id': 'RemainingMonths', 'type': 'numeric'},
        {'name': 'Start Date', 'id': 'StartDate', 'type': 'text'},
        {'name': 'End Date', 'id': 'EndDate', 'type': 'text'},
    ],
    data=df.to_dict('records') if not df.empty else [],
    filter_action='native',
    sort_action='native',
    sort_mode='multi',
    page_size=10,
    style_table={
        'overflowX': 'auto',
        'overflowY': 'auto',
        'maxHeight': '60vh',
    },
    style_header={
        'backgroundColor': '#2C3034',
        'color': 'white',
        'fontWeight': 'bold',
        'textAlign': 'left',
        'padding': '10px',
        'border': '1px solid #404040'
    },
    style_cell={
        'backgroundColor': '#1e2124',
        'color': 'white',
        'textAlign': 'left',
        'padding': '10px',
        'border': '1px solid #404040',
        'fontFamily': '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif',
        'minWidth': '100px',
        'maxWidth': '180px',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#212529'
        },
        {
            'if': {
                'filter_query': '{Progress} > 75',
                'column_id': 'Progress'
            },
            'color': '#00ff00'
        },
        {
            'if': {
                'filter_query': '{Progress} < 25',
                'column_id': 'Progress'
            },
            'color': '#ffaa00'
        }
    ],
    style_filter={
        'backgroundColor': '#2C3034',
        'color': 'white',
        'padding': '5px'
    },
    filter_options={
        'case': 'insensitive',
        'placeholder_text': 'Filter...'
    }
)

# Basic modal without any callbacks - just a placeholder
add_loan_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add New Loan"), close_button=True),
        dbc.ModalBody("Loan functionality will be implemented in the future"),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-add-loan", className="ms-auto")
        ),
    ],
    id="add-loan-modal",
    is_open=False,
)

# Page layout
layout = html.Div([
    # Add Loan Button (no callback attached)
    dbc.Row([
        dbc.Col([
            dbc.Button([
                html.I(className="fas fa-plus me-2"),
                "Add Loan"
            ], id="open-add-loan", color="success", className="mb-3 float-end")
        ], width=12),
    ]),
    # Summary Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Principal", className="card-title text-muted"),
                    html.H4(f"₹{summary['total_principal']:,.2f}", className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Outstanding", className="card-title text-muted"),
                    html.H4(f"₹{summary['total_outstanding']:,.2f}", className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Amount Paid", className="card-title text-muted"),
                    html.H4(f"₹{summary['total_paid']:,.2f}", className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Monthly EMI", className="card-title text-muted"),
                    html.H4(f"₹{summary['total_emi']:,.2f}", className="mb-2 text-danger")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=3)
    ], className="mb-3"),
    # Table Container
    html.Div([
        table
    ], className="border border-secondary"),
    # Add modal to layout (but no callbacks)
    add_loan_modal
]) 