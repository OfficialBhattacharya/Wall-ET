import dash
from dash import html, dash_table, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from utils.mutual_fund_utils import load_mf_portfolio_data, get_mf_portfolio_summary, get_scheme_name_from_code
import pandas as pd
import os

# Register the page - but not in the nav since it's now a sub-tab
dash.register_page(
    __name__,
    path='/mutual-funds',
    name='Mutual Funds',
    title='Mutual Fund Portfolio',
    icon='chart-pie',
    order=3,
    nav=False
)

# Load mutual fund portfolio data
df = load_mf_portfolio_data()
summary = get_mf_portfolio_summary(df)

# Create the DataTable with filters
table = dash_table.DataTable(
    id='mf-portfolio-table',
    columns=[
        {'name': 'Scheme', 'id': 'Scheme', 'type': 'text'},
        {'name': 'Units Owned', 'id': 'UnitsOwned', 'type': 'numeric',
         'format': {'specifier': ',.2f'}},
        {'name': 'Average NAV', 'id': 'AverageNAV', 'type': 'numeric', 
         'format': {'specifier': ',.2f'}},
        {'name': 'Current NAV', 'id': 'Current NAV', 'type': 'numeric',
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

# Add Mutual Fund Modal
add_mf_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add New Mutual Fund"), close_button=True),
        dbc.ModalBody([
            dbc.Form([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Scheme Name", html_for="scheme-name"),
                        dbc.Input(type="text", id="scheme-name", placeholder="Enter scheme name or let it auto-fill", required=True),
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Scheme Code", html_for="scheme-code"),
                        dbc.Input(type="text", id="scheme-code", placeholder="Enter AMFI scheme code", required=True),
                        dbc.FormText("Enter scheme code and tab out to auto-fill name", color="secondary"),
                    ], width=6),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Units Owned", html_for="units-owned"),
                        dbc.Input(type="number", id="units-owned", placeholder="Number of units", min=0.01, step=0.01, required=True),
                    ], width=6),
                    dbc.Col([
                        dbc.Label("Average NAV", html_for="avg-nav"),
                        dbc.Input(type="number", id="avg-nav", placeholder="Average NAV per unit", min=0.01, step=0.01, required=True),
                    ], width=6),
                ], className="mb-3"),
                dbc.Alert(
                    "Please fill all the fields correctly.",
                    id="add-mf-alert",
                    is_open=False,
                    color="danger",
                    dismissable=True
                ),
                dbc.Spinner(html.Div(id="mf-loading-output", style={"display": "none"})),
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Close", id="close-add-mf", className="me-2", color="secondary"),
            dbc.Button("Add Fund", id="save-mf", color="success"),
        ]),
    ],
    id="add-mf-modal",
    size="lg",
    is_open=False,
)

# Page layout - now simpler, without the card wrapper since it's in a tab
layout = html.Div([
    # Add Mutual Fund Button
    dbc.Row([
        dbc.Col([
            dbc.Button([
                html.I(className="fas fa-plus me-2"),
                "Add Mutual Fund"
            ], id="open-add-mf", color="success", className="mb-3 float-end")
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
                    html.H5("Number of Schemes", className="card-title text-muted"),
                    html.H4(f"{summary['num_schemes']}", className="mb-2 text-white")
                ])
            ], className="bg-dark border-secondary mb-3")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Profitable Schemes", className="card-title text-muted"),
                    html.H4(f"{summary['profitable_schemes']} / {summary['num_schemes']}", 
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
    add_mf_modal
])

# Callbacks for the modal
@callback(
    Output("add-mf-modal", "is_open"),
    [Input("open-add-mf", "n_clicks"), Input("close-add-mf", "n_clicks"), Input("save-mf", "n_clicks")],
    [State("add-mf-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open

# Callback to auto-fill scheme name from scheme code
@callback(
    [Output("scheme-name", "value"), Output("mf-loading-output", "children")],
    Input("scheme-code", "value"),
    prevent_initial_call=True
)
def autofill_scheme_name(scheme_code):
    if not scheme_code:
        return "", ""
    
    # Get scheme name from code
    scheme_name = get_scheme_name_from_code(scheme_code)
    
    return scheme_name, ""

@callback(
    [Output("add-mf-alert", "is_open"), Output("add-mf-alert", "children")],
    Input("save-mf", "n_clicks"),
    [
        State("scheme-name", "value"),
        State("scheme-code", "value"),
        State("units-owned", "value"),
        State("avg-nav", "value"),
        State("add-mf-alert", "is_open")
    ],
    prevent_initial_call=True
)
def add_mutual_fund(n_clicks, scheme_name, scheme_code, units_owned, avg_nav, is_open):
    if not n_clicks:
        return is_open, ""
    
    # Validate inputs
    if not scheme_name or not scheme_code or not units_owned or not avg_nav:
        return True, "Please fill all fields."
    
    try:
        # Convert to appropriate types
        units_owned = float(units_owned)
        avg_nav = float(avg_nav)
        
        # Create new row for the dataframe
        new_scheme = pd.DataFrame({
            'Scheme': [scheme_name],
            'UnitsOwned': [units_owned],
            'AverageNAV': [avg_nav],
            'SchemeCode': [scheme_code]
        })
        
        # Load existing data
        csv_path = 'assets/PersonalFiles/myMFPortfolio.csv'
        if os.path.exists(csv_path):
            existing_data = pd.read_csv(csv_path)
            
            # Check if scheme already exists
            if scheme_code in existing_data['SchemeCode'].values:
                return True, f"Scheme with code {scheme_code} already exists in portfolio."
            
            # Append new scheme
            updated_data = pd.concat([existing_data, new_scheme], ignore_index=True)
        else:
            updated_data = new_scheme
        
        # Save to CSV
        updated_data.to_csv(csv_path, index=False)
        
        # Success message and reload page
        return True, "Mutual Fund added successfully! Page will reload."
        
    except Exception as e:
        return True, f"Error: {str(e)}"

# Callback to refresh the page after adding a mutual fund
@callback(
    Output("mf-portfolio-table", "data"),
    Input("add-mf-alert", "children"),
    prevent_initial_call=True
)
def refresh_data(alert_message):
    if "Mutual Fund added successfully" in alert_message:
        # Reload data
        refreshed_df = load_mf_portfolio_data()
        return refreshed_df.to_dict('records')
    
    # If not successful, return existing data
    return dash.no_update 