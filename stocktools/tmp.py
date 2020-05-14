# -*- coding: utf-8 -*-


import plotly.graph_objects as go
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html


def plot_ohlc(co_df: pd.DataFrame, title: str = ""):

    colors = {
        'background': '#11001A',  # onyx
        'text': '#7FDBFF'
    }
    hovertext = []
    for i in range(len(co_df['Open'])):
        hovertext.append(
            co_df['Date'][i].strftime("%m/%d/%Y") +
            '<br>O: '+str(round(co_df['AdjOpen'][i], 4)) +
            '\tH: '+str(round(co_df['AdjHigh'][i], 4)) +
            '<br>L: '+str(round(co_df['AdjLow'][i], 4)) +
            '\tC: '+str(co_df['AdjClose'][i]))

    fig = go.Figure(data=go.Candlestick(x=co_df['Date'],
                                        open=co_df['AdjOpen'],
                                        high=co_df['AdjHigh'],
                                        low=co_df['AdjLow'],
                                        close=co_df['AdjClose'],
                                        text=hovertext,
                                        hoverinfo='text',
                                        increasing_line_color='#0048BA',
                                        decreasing_line_color='#E60000'),

                    layout=go.Layout(
        title=title,
        width=1200,
        height=600,
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        xaxis_rangeslider_visible=False)
    )
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

    app = dash.Dash()
    app.layout = html.Div(
        style={'backgroundColor': colors['background']},
        children=[
            html.H1(
                children='Historical OHLC Chart',
                style={
                    'fontSize': 50,
                    'text-decoration': 'underline',
                    'font-family': 'Ubuntu',
                    'textAlign': 'center',
                    'color': colors['text']
                }
            ),
            html.Div(children='Choose the company symbol below', style={
                'textAlign': 'center',
                'fontSize': 25,
                'color': colors['text']
            }),
            dcc.Graph(
                id='ohlc_graph',
                figure=fig), ]
    )  # html.Label('OHLC Graph'),

    app.run_server(debug=True, use_reloader=True)

    # fig.update_layout(title="AAPL Stock", xaxis_rangeslider_visible=False)
    # fig.update_layout(xaxis_rangeslider_visible=False)

    # fig.show()

    # fig.write_image('figure.png')


if __name__ == "__main__":
    # import .json_to_df as js
    # from json_to_df import json_to_df
    #     from .plot_ohlc import json_to_df

    aapl_df = json_to_df('data_aapl.json', )
    plot_ohlc(aapl_df, title="Apple Stock")
