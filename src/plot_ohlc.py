import plotly.graph_objects as go
import pandas as pd


def plot_ohlc(co_df: pd.DataFrame, title: str):

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
                                        hoverinfo='text'),
                    layout=go.Layout(
        title=title,
        width=1200,
        height=600,
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

    # fig.update_layout(title="AAPL Stock", xaxis_rangeslider_visible=False)
    # fig.update_layout(xaxis_rangeslider_visible=False)

    fig.show()

    # fig.write_image('figure.png')


if __name__ == "__main__":
    from json_to_df import df_from_response
    aapl_df = df_from_response('data_aapl.json', title="Apple Stock")
    plot_ohlc(aapl_df)
