import yfinance as yf
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Initialize the Dash app
app = Dash(__name__)

# Define available stock options
available_stocks = {
    "Motilal Oswal Midcap": "0P00012ALS.BO",
    "Facebook (Meta)": "META",
    "Netflix": "NFLX"
}

# Duration button labels and corresponding yfinance period values
duration_map = {
    
    '1W': '5d',
    '1M': '1mo',
    '6M': '6mo',
    '1Y': '1y',
    '5Y': '5y',
    'ALL': 'max'
}

# Layout of the app
app.layout = html.Div([
    html.H2('📈 Stock Price Analysis'),

    html.P("Select stock:"),
    dcc.Dropdown(
        id="ticker-dropdown",
        options=[{"label": name, "value": symbol} for name, symbol in available_stocks.items()],
        value="0P00012ALS.BO",
        clearable=False
    ),

    html.Br(),

    html.P("Select Time Duration:"),
    dcc.RadioItems(
        id='duration-selector',
        options=[{'label': label, 'value': value} for label, value in duration_map.items()],
        labelStyle={'display': 'inline-block', 'padding': '10px', 'cursor': 'pointer'},
        inputStyle={"margin-right": "5px"},
        style={
            "background": "#f9f9f9",
            "padding": "10px",
            "border-radius": "10px"
        }
    ),

    html.Br(),

    dcc.Graph(id="time-series-chart"),
])

# Callback to update the graph
@app.callback(
    Output("time-series-chart", "figure"),
    Input("ticker-dropdown", "value"),
    Input("duration-selector", "value")
)
def update_graph(ticker_symbol, period):
    # Fetch historical data for the selected ticker and time period
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period=period)

    if data.empty:
        fig = px.line(title="No data found for this selection.")
    else:
        data.reset_index(inplace=True)
        fig = px.line(data, x="Date", y="Close", title=f"{ticker_symbol} - Closing Prices ({period})")
        fig.update_layout(xaxis_title="Date", yaxis_title="Price")
    
    return fig

# Run the Dash app
if __name__ == "__main__":
    app.run(debug=True)
