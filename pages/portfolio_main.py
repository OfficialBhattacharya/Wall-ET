import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from pages.portfolio import layout as stock_layout
from pages.mutual_funds import layout as mf_layout
from pages.other_investments import layout as other_inv_layout
from pages.savings_accounts import layout as savings_layout
from pages.credit_cards import layout as credit_cards_layout
from pages.loans import layout as loans_layout

# Register the page
dash.register_page(
    __name__,
    path='/',
    name='Portfolio',
    title='Portfolio',
    icon='wallet',
    order=0  # Set to 0 to ensure it appears first
)

# Page layout
layout = html.Div([
    dbc.Card([
        dbc.CardHeader([
            html.H3([
                html.I(className="fas fa-wallet me-2"),
                "My Portfolio"
            ], className="text-center text-primary m-2")
        ], className="bg-dark"),
        dbc.CardBody([
            # Tabs for all portfolio sections
            dbc.Tabs([
                dbc.Tab(
                    stock_layout,
                    label="Stock Portfolio",
                    tab_id="tab-stocks",
                    label_class_name="text-light",
                    active_label_class_name="fw-bold",
                ),
                dbc.Tab(
                    mf_layout,
                    label="Mutual Funds",
                    tab_id="tab-mutual-funds",
                    label_class_name="text-light",
                    active_label_class_name="fw-bold",
                ),
                dbc.Tab(
                    other_inv_layout,
                    label="Other Investments",
                    tab_id="tab-other-investments",
                    label_class_name="text-light",
                    active_label_class_name="fw-bold",
                ),
                dbc.Tab(
                    savings_layout,
                    label="Savings Accounts",
                    tab_id="tab-savings",
                    label_class_name="text-light",
                    active_label_class_name="fw-bold",
                ),
                dbc.Tab(
                    credit_cards_layout,
                    label="Credit Cards",
                    tab_id="tab-credit-cards",
                    label_class_name="text-light",
                    active_label_class_name="fw-bold",
                ),
                dbc.Tab(
                    loans_layout,
                    label="Loans",
                    tab_id="tab-loans",
                    label_class_name="text-light",
                    active_label_class_name="fw-bold",
                ),
            ],
            id="portfolio-tabs",
            active_tab="tab-stocks",
            className="mb-3")
        ], className="bg-dark p-3")
    ], className="shadow")
], className="p-4") 