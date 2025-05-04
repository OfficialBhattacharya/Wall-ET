import dash
from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import os

# Register the page - but not in the nav since it's a sub-tab
dash.register_page(
    __name__,
    path='/other-investments',
    name='Other Investments',
    title='Other Investments',
    icon='piggy-bank',
    order=4,
    nav=False
)

# Load data - create empty table if file doesn't exist
def load_other_investments_data():
    # Check if file exists
    csv_path = 'assets/PersonalFiles/myOtherInvestments.csv'
    os.makedirs('assets/PersonalFiles', exist_ok=True)
    
    if os.path.exists(csv_path):
        # Read the data if file exists
        df = pd.read_csv(csv_path)
        
        # Calculate metrics if data exists
        if not df.empty:
            df['CurrentValue'] = df['Amount'] * (1 + (df['ExpectedReturn'] / 100))
            df['Profit/Loss'] = df['CurrentValue'] - df['Amount']
            df['Returns %'] = ((df['CurrentValue'] - df['Amount']) / df['Amount'] * 100).round(2)
        
    else:
        # Create empty DataFrame with correct columns
        df = pd.DataFrame(columns=[
            'Investment', 'Amount', 'StartDate', 'EndDate', 'ExpectedReturn'
        ])
        # Save the empty file
        df.to_csv(csv_path, index=False)
    
    return df

# Load data
df = load_other_investments_data()

# Calculate summary metrics
def get_summary(df):
    if df.empty or 'Amount' not in df.columns or 'CurrentValue' not in df.columns:
        return {
            'total_investment': 0,
            'current_value': 0,
            'total_returns': 0,
            'num_investments': 0
        }
    
    total_investment = df['Amount'].sum()
    current_value = df['CurrentValue'].sum()
    total_returns = ((current_value - total_investment) / total_investment * 100).round(2) if total_investment > 0 else 0
    
    return {
        'total_investment': total_investment,
        'current_value': current_value,
        'total_returns': total_returns,
        'num_investments': len(df)
    }

summary = get_summary(df)

# Create the DataTable
table = dash_table.DataTable(
    id='other-investments-table',
    columns=[
        {'name': 'Investment', 'id': 'Investment', 'type': 'text'},
        {'name': 'Amount', 'id': 'Amount', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Start Date', 'id': 'StartDate', 'type': 'text'},
        {'name': 'End Date', 'id': 'EndDate', 'type': 'text'},
        {'name': 'Expected Return %', 'id': 'ExpectedReturn', 'type': 'numeric',
         'format': {'specifier': '.2f'}},
        {'name': 'Current Value', 'id': 'CurrentValue', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Profit/Loss', 'id': 'Profit/Loss', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Returns %', 'id': 'Returns %', 'type': 'numeric',
         'format': {'specifier': '.2f'}}
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
                'filter_query': '{Returns %} > 0',
                'column_id': 'Returns %'
            },
            'color': '#00ff00'
        },
        {
            'if': {
                'filter_query': '{Returns %} < 0',
                'column_id': 'Returns %'
            },
            'color': '#ff0000'
        },
        {
            'if': {
                'filter_query': '{Profit/Loss} > 0',
                'column_id': 'Profit/Loss'
            },
            'color': '#00ff00'
        },
        {
            'if': {
                'filter_query': '{Profit/Loss} < 0',
                'column_id': 'Profit/Loss'
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

# Basic modal without any callbacks - just a placeholder
add_investment_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add New Investment"), close_button=True),
        dbc.ModalBody("Investment functionality will be implemented in the future"),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-add-investment", className="ms-auto")
        ),
    ],
    id="add-investment-modal",
    is_open=False,
)

# Page layout
layout = html.Div([
    # Add Investment Button (no callback attached)
    dbc.Row([
        dbc.Col([
            dbc.Button([
                html.I(className="fas fa-plus me-2"),
                "Add Investment"
            ], id="open-add-investment", color="success", className="mb-3 float-end")
        ], width=12),
    ]),
    # Summary Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Investment", className="card-title text-muted"),
                    html.H4(f"₹{summary['total_investment']:,.2f}", className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Current Value", className="card-title text-muted"),
                    html.H4(f"₹{summary['current_value']:,.2f}", className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Total Returns", className="card-title text-muted"),
                    html.H4([
                        f"{summary['total_returns']}%"
                    ], className=f"mb-2 {'text-success' if summary['total_returns'] > 0 else 'text-danger'}")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=4)
    ], className="mb-3"),
    # Table Container
    html.Div([
        table
    ], className="border border-secondary"),
    # Add modal to layout (but no callbacks)
    add_investment_modal
]) 