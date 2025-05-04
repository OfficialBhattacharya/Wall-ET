import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from utils.stock_data import calculate_portfolio_metrics

# Register the page
dash.register_page(
    __name__,
    path='/market',
    name='Market Analysis',
    title='Market Analysis',
    icon='chart-line',
    order=1  # Make it the second tab
)

# Read the portfolio data
df = pd.read_csv('assets/PersonalFiles/myPortfolio.csv')
portfolio_metrics = calculate_portfolio_metrics(df)

# Create market performance chart
def create_market_chart():
    # This is a placeholder. In a real app, you would fetch real market data
    return go.Figure(
        data=[
            go.Scatter(
                x=['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                y=[100, 105, 103, 107, 110],
                name='Portfolio',
                line=dict(color='#4B0082')
            ),
            go.Scatter(
                x=['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                y=[100, 102, 101, 103, 104],
                name='NIFTY 50',
                line=dict(color='#98FB98')
            )
        ]
    ).update_layout(
        title="Portfolio vs Market Performance",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            tickfont=dict(color='white')
        ),
        height=400,
        margin=dict(t=50, b=0, l=0, r=0)
    )

# For demo purposes, create top gainers and losers
def get_top_gainers_losers():
    # Create sample data for top gainers
    gainers = pd.DataFrame({
        'Stock': ['NTPC', 'GAIL', 'ITC', 'SBIN', 'BEL', 'TATAPOWER', 'TATAMOTORS', 'DLF', 'ADANIGREEN', 'APOLLOTYRE'],
        'Price': [354.55, 189.09, 420.30, 750.40, 290.25, 385.45, 700.90, 695.75, 900.70, 440.25],
        'Change': ['+5.2%', '+4.8%', '+3.9%', '+3.5%', '+3.2%', '+2.9%', '+2.7%', '+2.5%', '+2.3%', '+2.1%']
    })
    
    # Create sample data for top losers
    losers = pd.DataFrame({
        'Stock': ['RPOWER', 'SUZLON', 'JYOTISTRUC', 'VIKASECO', 'BANDHANBNK', 'PNB', 'IDBI', 'L&TFH', 'NHPC', 'BANKINDIA'],
        'Price': [39.99, 56.40, 25.30, 2.75, 160.45, 100.25, 82.30, 155.25, 80.40, 110.25],
        'Change': ['-4.1%', '-3.8%', '-3.5%', '-3.3%', '-3.0%', '-2.8%', '-2.5%', '-2.3%', '-2.0%', '-1.8%']
    })
    
    return gainers, losers

gainers_df, losers_df = get_top_gainers_losers()

# Create tables for top gainers and losers
gainers_table = dash_table.DataTable(
    id='gainers-table',
    columns=[
        {'name': 'Stock', 'id': 'Stock', 'type': 'text'},
        {'name': 'Price', 'id': 'Price', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
        {'name': 'Change', 'id': 'Change', 'type': 'text'}
    ],
    data=gainers_df.to_dict('records'),
    style_table={
        'overflowX': 'auto',
        'overflowY': 'auto',
        'maxHeight': '300px',
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
    ]
)

losers_table = dash_table.DataTable(
    id='losers-table',
    columns=[
        {'name': 'Stock', 'id': 'Stock', 'type': 'text'},
        {'name': 'Price', 'id': 'Price', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
        {'name': 'Change', 'id': 'Change', 'type': 'text'}
    ],
    data=losers_df.to_dict('records'),
    style_table={
        'overflowX': 'auto',
        'overflowY': 'auto',
        'maxHeight': '300px',
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
    ]
)

# Page layout
layout = html.Div([
    dbc.Card([
        dbc.CardHeader([
            html.H3([
                html.I(className="fas fa-chart-line me-2"),
                "Market Analysis"
            ], className="text-center text-primary m-2")
        ], className="bg-dark"),
        dbc.CardBody([
            # Market Performance Chart
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Market Performance", className="card-title text-muted")
                        ], className="bg-dark border-secondary"),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=create_market_chart(),
                                config={'displayModeBar': False}
                            )
                        ], className="p-0")
                    ], className="bg-dark border-secondary mb-3")
                ], width=12)
            ], className="mb-3"),
            
            # Gainers and Losers
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Top 10 Gainers", className="card-title text-success")
                        ], className="bg-dark border-secondary"),
                        dbc.CardBody([
                            gainers_table
                        ], className="p-2")
                    ], className="bg-dark border-secondary mb-3")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Top 10 Losers", className="card-title text-danger")
                        ], className="bg-dark border-secondary"),
                        dbc.CardBody([
                            losers_table
                        ], className="p-2")
                    ], className="bg-dark border-secondary mb-3")
                ], width=6)
            ], className="mb-3")
        ], className="bg-dark p-3")
    ], className="shadow")
], className="p-4") 