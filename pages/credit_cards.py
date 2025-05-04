import dash
from dash import html, dash_table, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import os
from datetime import datetime

# Register the page - but not in the nav since it's a sub-tab
dash.register_page(
    __name__,
    path='/credit-cards',
    name='Credit Cards',
    title='Credit Cards',
    icon='credit-card',
    order=6,
    nav=False
)

# Load data - create empty table if file doesn't exist
def load_credit_card_data():
    # Check if file exists
    csv_path = 'assets/PersonalFiles/myCreditCards.csv'
    os.makedirs('assets/PersonalFiles', exist_ok=True)
    
    if os.path.exists(csv_path):
        # Read the data if file exists
        df = pd.read_csv(csv_path)
        
        # Calculate additional metrics if data exists
        if not df.empty and 'CreditLimit' in df.columns and 'OutstandingBalance' in df.columns:
            # Calculate available credit
            df['AvailableCredit'] = df['CreditLimit'] - df['OutstandingBalance']
            
            # Calculate days to payment if DueDate exists
            if 'DueDate' in df.columns:
                today = datetime.today().strftime('%Y-%m-%d')
                df['DaysToPayment'] = pd.to_datetime(df['DueDate']).apply(lambda x: (x - pd.to_datetime(today)).days)
            
            # Calculate utilization percentage
            df['Utilization'] = ((df['OutstandingBalance'] / df['CreditLimit']) * 100).round(2)
    else:
        # Create empty DataFrame with correct columns
        df = pd.DataFrame(columns=[
            'Bank', 'CardType', 'CardNumber', 'CreditLimit', 'OutstandingBalance', 
            'MinimumDue', 'DueDate', 'APR'
        ])
        # Save the empty file
        df.to_csv(csv_path, index=False)
    
    return df

# Load data
df = load_credit_card_data()

# Calculate summary metrics
def get_summary(df):
    if df.empty or 'CreditLimit' not in df.columns or 'OutstandingBalance' not in df.columns:
        return {
            'total_credit_limit': 0,
            'total_outstanding': 0,
            'available_credit': 0,
            'overall_utilization': 0,
            'num_cards': 0
        }
    
    total_credit_limit = df['CreditLimit'].sum()
    total_outstanding = df['OutstandingBalance'].sum()
    available_credit = df['AvailableCredit'].sum() if 'AvailableCredit' in df.columns else (total_credit_limit - total_outstanding)
    overall_utilization = (total_outstanding / total_credit_limit * 100).round(2) if total_credit_limit > 0 else 0
    
    return {
        'total_credit_limit': total_credit_limit,
        'total_outstanding': total_outstanding,
        'available_credit': available_credit,
        'overall_utilization': overall_utilization,
        'num_cards': len(df)
    }

summary = get_summary(df)

# Create the DataTable
table = dash_table.DataTable(
    id='credit-cards-table',
    columns=[
        {'name': 'Bank', 'id': 'Bank', 'type': 'text'},
        {'name': 'Card Type', 'id': 'CardType', 'type': 'text'},
        {'name': 'Card Number', 'id': 'CardNumber', 'type': 'text'},
        {'name': 'Credit Limit', 'id': 'CreditLimit', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Outstanding Balance', 'id': 'OutstandingBalance', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Available Credit', 'id': 'AvailableCredit', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Utilization %', 'id': 'Utilization', 'type': 'numeric',
         'format': {'specifier': '.2f'}},
        {'name': 'Minimum Due', 'id': 'MinimumDue', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Due Date', 'id': 'DueDate', 'type': 'text'},
        {'name': 'Days To Payment', 'id': 'DaysToPayment', 'type': 'numeric'},
        {'name': 'APR %', 'id': 'APR', 'type': 'numeric',
         'format': {'specifier': '.2f'}},
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
                'filter_query': '{Utilization} > 80',
                'column_id': 'Utilization'
            },
            'color': '#ff0000'
        },
        {
            'if': {
                'filter_query': '{Utilization} <= 30',
                'column_id': 'Utilization'
            },
            'color': '#00ff00'
        },
        {
            'if': {
                'filter_query': '{DaysToPayment} <= 5',
                'column_id': 'DaysToPayment'
            },
            'color': '#ff0000'
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

# Page layout
layout = html.Div([
    # Add Card Button
    dbc.Row([
        dbc.Col([
            dbc.Button([
                html.I(className="fas fa-plus me-2"),
                "Add Credit Card"
            ], id="open-add-card", color="success", className="mb-3 float-end"),
            # Hidden div for callback output
            html.Div(id="credit-cards-add-container", style={"display": "none"})
        ], width=12),
    ]),
    # Summary Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Credit Limit", className="card-title text-muted"),
                    html.H4(f"₹{summary['total_credit_limit']:,.2f}", className="mb-2 text-white")
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
                    html.H5("Available Credit", className="card-title text-muted"),
                    html.H4(f"₹{summary['available_credit']:,.2f}", className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Utilization", className="card-title text-muted"),
                    html.H4([
                        f"{summary['overall_utilization']}%"
                    ], className=f"mb-2 {'text-danger' if summary['overall_utilization'] > 30 else 'text-success'}")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=3)
    ], className="mb-3"),
    # Table Container
    html.Div([
        table
    ], className="border border-secondary"),
])

# Add button click handler placeholder
@callback(
    Output("credit-cards-add-container", "children"),
    Input("open-add-card", "n_clicks"),
    prevent_initial_call=True
)
def handle_add_click(n_clicks):
    # This would open a modal in a complete implementation
    return "Card button clicked" 