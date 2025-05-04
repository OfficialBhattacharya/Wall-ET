import dash
from dash import html, dash_table, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from utils.portfolio_utils import load_portfolio_data, get_portfolio_summary, get_stock_name_from_symbol
import pandas as pd
import os
from utils.mf_excel_converter import convert_holdings_to_csv

# Register the page - but not in the nav since it's now a sub-tab
dash.register_page(
    __name__,
    path='/stocks',
    name='Stock Portfolio',
    title='Stock Portfolio',
    icon='chart-line',
    order=2,
    nav=False
)

# Load portfolio data
df = load_portfolio_data()
summary = get_portfolio_summary(df)

# Create the DataTable with filters
table = dash_table.DataTable(
    id='stock-portfolio-table',
    columns=[
        {'name': 'Stock', 'id': 'Stock', 'type': 'text'},
        {'name': 'Shares Owned', 'id': 'SharesOwned', 'type': 'numeric'},
        {'name': 'Average Price', 'id': 'AveragePrice', 'type': 'numeric', 
         'format': {'specifier': ',.2f'}},
        {'name': 'Current Price', 'id': 'Current Price', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Total Investment', 'id': 'TotalInvestment', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Current Value', 'id': 'Current Value', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Profit/Loss', 'id': 'Profit/Loss', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Returns %', 'id': 'Returns %', 'type': 'numeric',
         'format': {'specifier': '.2f'}}
    ],
    data=df.to_dict('records'),
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

# Add Stock Modal
add_stock_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add New Stock"), close_button=True),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Stock Name", html_for="stock-name"),
                        dbc.Input(type="text", id="stock-name", placeholder="Enter stock name or let it auto-fill", required=True),
                    ], width=6),
                    dbc.Col([
                        dbc.Label("NSE Symbol", html_for="nse-symbol"),
                        dbc.Input(type="text", id="nse-symbol", placeholder="Enter NSE symbol", required=True),
                        dbc.FormText("Enter symbol and tab out to auto-fill name", color="secondary"),
                    ], width=6),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Shares Owned", html_for="shares-owned"),
                        dbc.Input(type="number", id="shares-owned", placeholder="Number of shares", min=1, step=1, required=True),
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Average Buy Price", html_for="avg-price"),
                        dbc.Input(type="number", id="avg-price", placeholder="Average price per share", min=0.01, step=0.01, required=True),
                    ], width=6),
                ], className="mb-3"),
                dbc.Alert(
                    "Please fill all the fields correctly.",
                    id="add-stock-alert",
                    is_open=False,
                    color="danger",
                    dismissable=True
                ),
                dbc.Spinner(html.Div(id="loading-output", style={"display": "none"})),
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Close", id="close-add-stock", className="me-2", color="secondary"),
            dbc.Button("Add Stock", id="save-stock", color="success"),
        ]),
    ],
    id="add-stock-modal",
    size="lg",
    is_open=False,
)

# Page layout - now simpler, without the card wrapper since it's in a tab
layout = html.Div([
    # Add Stock Button
    dbc.Row([
        dbc.Col([
            dbc.Button([
                html.I(className="fas fa-plus me-2"),
                "Add Stock"
            ], id="open-add-stock", color="success", className="mb-3 float-end")
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
    # New Metrics Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Number of Stocks", className="card-title text-muted"),
                    html.H4(f"{summary['num_stocks']}", className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Profitable Stocks", className="card-title text-muted"),
                    html.H4(f"{summary['profitable_stocks']} / {summary['num_stocks']}", 
                           className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Balance in Performing", className="card-title text-muted"),
                    html.H4([
                        f"{summary['percent_in_performing']}%"
                    ], className=f"mb-2 {'text-success' if summary['percent_in_performing'] > 0 else 'text-danger'}")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=4)
    ], className="mb-3"),
    # Table Container
    html.Div([
        table
    ], className="border border-secondary"),
    # Add the modal to the layout
    add_stock_modal
])

# Callbacks for the modal
@callback(
    Output("add-stock-modal", "is_open"),
    [Input("open-add-stock", "n_clicks"), Input("close-add-stock", "n_clicks"), Input("save-stock", "n_clicks")],
    [State("add-stock-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open

# Callback to auto-fill stock name from NSE symbol
@callback(
    [Output("stock-name", "value"), Output("loading-output", "children")],
    Input("nse-symbol", "value"),
    prevent_initial_call=True
)
def autofill_stock_name(symbol):
    if not symbol:
        return "", ""
    
    # Get stock name from symbol
    stock_name = get_stock_name_from_symbol(symbol)
    
    return stock_name, ""

@callback(
    [Output("add-stock-alert", "is_open"), Output("add-stock-alert", "children")],
    Input("save-stock", "n_clicks"),
    [
        State("stock-name", "value"),
        State("nse-symbol", "value"),
        State("shares-owned", "value"),
        State("avg-price", "value"),
        State("add-stock-alert", "is_open")
    ],
    prevent_initial_call=True
)
def add_stock(n_clicks, stock_name, nse_symbol, shares_owned, avg_price, is_open):
    if not n_clicks:
        return is_open, ""
    
    # Validate inputs
    if not stock_name or not nse_symbol or not shares_owned or not avg_price:
        return True, "Please fill all fields."
    
    try:
        # Convert to appropriate types
        shares_owned = int(shares_owned)
        avg_price = float(avg_price)
        
        # Create new row for the dataframe
        new_stock = pd.DataFrame({
            'Stock': [stock_name],
            'SharesOwned': [shares_owned],
            'AveragePrice': [avg_price],
            'NSE_Symbol': [nse_symbol]
        })
        
        # Load existing data
        csv_path = 'assets/PersonalFiles/myPortfolio.csv'
        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            
            # Check if stock already exists
            if nse_symbol in existing_data['NSE_Symbol'].values:
                return True, f"Stock with symbol {nse_symbol} already exists in portfolio."
            
            # Append new stock
            updated_data = pd.concat([existing_data, new_stock], ignore_index=True)
        else:
            updated_data = new_stock
        
        # Save to CSV
        updated_data.to_csv(csv_path, index=False)
        
        # Success message and reload page
        return True, "Stock added successfully! Page will reload."
        
    except Exception as e:
        return True, f"Error: {str(e)}"

# Callback to refresh the page after adding a stock
@callback(
    Output("stock-portfolio-table", "data"),
    Input("add-stock-alert", "children"),
    prevent_initial_call=True
)
def refresh_data(alert_message):
    if "Stock added successfully" in alert_message:
        # Reload data
        refreshed_df = load_portfolio_data()
        return refreshed_df.to_dict('records')
    
    # If not successful, return existing data
    return dash.no_update 