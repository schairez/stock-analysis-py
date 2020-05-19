# -*- coding: utf-8 -*-

import sys
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask import Flask
from stocktools.json_to_df import json_to_df
from datetime import datetime as dt
from datetime import timedelta

# TODO:
# Add nav tags for Indices, Stocks, ETFs, Bonds, Forex, Options, Futures, Currencies, News

# Add moving tickers slide horizontally like in wall street (scrolling stock ticker )

# S&P 500 sector performance for the week bar graph; xi companies, y percentage
# model after
# https://us.etrade.com/knowledge/library/perspectives/market-dashboard

# watchlist tab with table of top 10 companies

# add volume to OHLC chart
# use media queries to center based on display-size

colors = {
    'background': '#00336c',
    'text': '#e2efff'
}

dropdown_options = [
    {'label': 'Adobe', 'value': 'ADBE'},
    {'label': 'Apple Inc', 'value': 'AAPL'},
    {'label': 'Amazon', 'value': 'AMZN'},
    {'label': 'Netflix', 'value': 'NFLX'},
    {'label': 'Nike', 'value': 'NKE'},
    {'label': 'Nvidia', 'value': 'NVDA'},
    {'label': 'Oracle', 'value': 'ORCL'},
    {'label': 'Starbucks', 'value': 'SBUX'},
    {'label': 'Tesla', 'value': 'TSLA'},
    {'label': 'Intuit', 'value': 'INTU'},
    {'label': 'Johnson & Johnson', 'value': 'JNJ'},
    {'label': 'JP Morgan Chase', 'value': 'JPM'},
]
# f3f3f1
external_stylesheets = [dbc.themes.BOOTSTRAP, "/assets/style.css"]

server = Flask(__name__)


app = dash.Dash(__name__, server=server,
                external_stylesheets=external_stylesheets,)
app.config.suppress_callback_exceptions = True
app.server.config.suppress_callback_exceptions = True
app.config['suppress_callback_exceptions'] = True

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "10rem",
    "padding": "2rem 1rem",
    "background-color": "#f3f3f1",
    "font-family": ['Poppins', 'sans-serif']

}

title = html.H2(
    children='Investments Dashboard',
    style={
        'fontSize': 25,
        'fontWeight': 150,
        # 'font-family': ['Poppins', 'sans-serif'],
        'textAlign': 'center',
        'color': ' #001731',
    }
)


side_navbar = html.Div([
    title,
    html.Hr(),
    dcc.Location(id="url"),
    dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Bonds", active=True,
                                    href="/bonds", id="page-bonds")),
            dbc.NavItem(dbc.NavLink(
                "Currencies", href="/currencies", id="page-currencies")),
            dbc.NavItem(dbc.NavLink("ETFs", href="/etfs", id="page-etfs")),
            dbc.NavItem(dbc.NavLink("Forex", href="/forex", id="page-forex")),
            dbc.NavItem(dbc.NavLink(
                "Futures", href="/futures", id="page-futures")),
            dbc.NavItem(dbc.NavLink(
                "Stocks", href="/stocks", id="page-stocks")),
            # dbc.NavItem(dbc.NavLink("News", href="/news", id="page-news")),
        ],
        vertical=True,
        pills=True,

    )], style=SIDEBAR_STYLE, className="pretty_container")


stocks_selection_html = html.Div(className="plot_selection_panel pretty_container",
                                 children=[
                                     html.H3("""Choose the company""",
                                             style={
                                                 'fontWeight': 160,
                                                 'margin': 0,
                                                 'fontSize': 15,
                                                 #  'overflow': 'auto',
                                                 'font-family': ['Poppins', 'sans-serif'],
                                                 'display':'inline-block',
                                                 'textAlign': 'center',
                                                 'color': ' #001731', }),
                                     dcc.Dropdown(multi=False,
                                                  clearable=False,
                                                  style=dict(
                                                      width='70%',
                                                      verticalAlign="middle",
                                                      display='inline-block',
                                                  ),
                                                  id='symbolDropdown',
                                                  className="horizontal_dropdowns",
                                                  options=dropdown_options,
                                                  value='AAPL'
                                                  ),
                                     html.Div(
                                         [
                                             dcc.Graph(id='main_graph')
                                         ],
                                         className='pretty_container plot_panel_size',
                                         # style={  # 'float': 'right', 'margin': 'auto'}
                                     ),

                                 ])


app.layout = html.Div([side_navbar,
                       dbc.Container(id="page-content", className="pt-4"),

                       ])


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}", "active") for i in ["bonds", "currencies",
                                             "etfs", "forex", "futures", "stocks"]],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/{i}" for i in ["bonds", "currencies",
                                          "etfs", "forex", "futures", "stocks"]]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/bonds"]:
        return html.P("This is the content of page 1!")
    elif pathname == "/currencies":
        return html.P("This is the content of page 2. Yay!")
    elif pathname == "/etfs":
        return html.P("Oh cool, this is page 3!sdddddddd")
    elif pathname == "/forex":
        return html.P("Oh cool, this is page 3!")
    elif pathname == "/futures":
        return html.P("This is the content of page 2. Yay!")
    elif pathname == "/stocks":
        return stocks_selection_html

        return html.P("Oh cool, this is page 3!")

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


@app.callback(
    Output('main_graph', 'figure'),
    [Input('symbolDropdown', 'value')],
)
def render_ohlc_graph(symbolDropdown: str):
    print(symbolDropdown)
    symbol_historical_data_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), f'data/data_raw/data_{symbolDropdown.lower()}.json')

    co_df = json_to_df(f"data_{symbolDropdown.lower()}.json",
                       path=symbol_historical_data_path)

    title = f"{symbolDropdown.lower()} Historical Graph"
    hovertext = []
    for i in range(len(co_df['Open'])):
        hovertext.append(
            co_df['Date'][i].strftime("%m/%d/%Y") +
            '<br>O: '+str(round(co_df['AdjOpen'][i], 4)) +
            '\tH: '+str(round(co_df['AdjHigh'][i], 4)) +
            '<br>L: '+str(round(co_df['AdjLow'][i], 4)) +
            '\tC: '+str(co_df['AdjClose'][i]))

    trace_ohlc = go.Candlestick(x=co_df['Date'],
                                open=co_df['AdjOpen'],
                                high=co_df['AdjHigh'],
                                low=co_df['AdjLow'],
                                close=co_df['AdjClose'],
                                text=hovertext,
                                hoverinfo='text',
                                name="OHLC"
                                # increasing_line_color='#0048BA',
                                # decreasing_line_color='#E60000'
                                )
    trace_sma_20_day = go.Scatter(
        x=co_df['Date'], y=co_df['SMA_20day'], name="SMA_20day", visible=True)
    trace_ema_20_day = go.Scatter(
        x=co_df['Date'], y=co_df['EMA_20day'], name="EMA_20day")

    fig = go.Figure(data=[trace_ohlc, trace_sma_20_day, trace_ema_20_day],
                    layout=go.Layout(
        title=title,
        # width=1200,
        # height=600,
        # plot_bgcolor=colors['background'],
        paper_bgcolor='#F9F9F9',
        xaxis_rangeslider_visible=True)
    )
    print(type(fig))

    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"]),  # hide weekends
            # hide Christmas and New Year's
            dict(values=["2015-12-25", "2016-01-01"])
        ]
    )

    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=False
            ),
            type="date"
        )
    )

    return fig


if __name__ == "__main__":

    app.run_server(debug=True, use_reloader=True)

    # fig.update_layout(title="AAPL Stock", xaxis_rangeslider_visible=False)
    # fig.update_layout(xaxis_rangeslider_visible=False)

    # fig.show()

    # fig.write_image('figure.png')
