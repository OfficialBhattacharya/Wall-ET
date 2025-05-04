import dash
from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import os

# Register the page - but not in the nav since it's a sub-tab
dash.register_page(
    __name__,
    path='/savings-accounts',
    name='Savings Accounts',
    title='Savings Accounts',
    icon='bank',
    order=5,
    nav=False
)

# Load data - create empty table if file doesn't exist
def load_savings_accounts_data():
    # Check if file exists
    csv_path = 'assets/PersonalFiles/mySavingsAccounts.csv'
    os.makedirs('assets/PersonalFiles', exist_ok=True)
    
    if os.path.exists(csv_path):
        # Read the data if file exists
        df = pd.read_csv(csv_path)
        
        # Calculate metrics if data exists
        if not df.empty and 'Balance' in df.columns and 'InterestRate' in df.columns:
            df['AnnualInterest'] = (df['Balance'] * df['InterestRate'] / 100).round(2)
    else:
        # Create empty DataFrame with correct columns
        df = pd.DataFrame(columns=[
            'Bank', 'AccountType', 'AccountNumber', 'Balance', 'InterestRate', 'LastUpdated'
        ])
        # Save the empty file
        df.to_csv(csv_path, index=False)
    
    return df

# Load data
df = load_savings_accounts_data()

# Calculate summary metrics
def get_summary(df):
    if df.empty or 'Balance' not in df.columns:
        return {
            'total_balance': 0,
            'total_interest': 0,
            'avg_interest_rate': 0,
            'num_accounts': 0
        }
    
    # Calculate metrics based on available data
    total_balance = df['Balance'].sum()
    total_interest = df['AnnualInterest'].sum() if 'AnnualInterest' in df.columns else 0
    avg_interest_rate = df['InterestRate'].mean().round(2) if 'InterestRate' in df.columns else 0
    
    return {
        'total_balance': total_balance,
        'total_interest': total_interest,
        'avg_interest_rate': avg_interest_rate,
        'num_accounts': len(df)
    }

summary = get_summary(df)

# Create the DataTable
table = dash_table.DataTable(
    id='savings-accounts-table',
    columns=[
        {'name': 'Bank', 'id': 'Bank', 'type': 'text'},
        {'name': 'Account Type', 'id': 'AccountType', 'type': 'text'},
        {'name': 'Account Number', 'id': 'AccountNumber', 'type': 'text'},
        {'name': 'Balance', 'id': 'Balance', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Interest Rate %', 'id': 'InterestRate', 'type': 'numeric',
         'format': {'specifier': '.2f'}},
        {'name': 'Annual Interest', 'id': 'AnnualInterest', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Last Updated', 'id': 'LastUpdated', 'type': 'text'},
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
add_account_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add New Account"), close_button=True),
        dbc.ModalBody("Account functionality will be implemented in the future"),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-add-account", className="ms-auto")
        ),
    ],
    id="add-account-modal",
    is_open=False,
)

# Page layout
layout = html.Div([
    # Add Account Button (no callback attached)
    dbc.Row([
        dbc.Col([
            dbc.Button([
                html.I(className="fas fa-plus me-2"),
                "Add Account"
            ], id="open-add-account", color="success", className="mb-3 float-end")
        ], width=12),
    ]),
    # Summary Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Balance", className="card-title text-muted"),
                    html.H4(f"₹{summary['total_balance']:,.2f}", className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Annual Interest", className="card-title text-muted"),
                    html.H4(f"₹{summary['total_interest']:,.2f}", className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Avg. Interest Rate", className="card-title text-muted"),
                    html.H4([
                        f"{summary['avg_interest_rate']}%"
                    ], className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=4)
    ], className="mb-3"),
    # Table Container
    html.Div([
        table
    ], className="border border-secondary"),
    # Add modal to layout (but no callbacks)
    add_account_modal
]) 