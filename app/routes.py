from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.models import User
from flask import request
from datetime import datetime
import datetime as dt

from app.forms import RegistrationForm
from app.forms import LoginForm
from app.forms import EditProfileForm
from app.forms import EmptyForm
from app.forms import PostForm
from app.models import Post
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from app.forms import ResetPasswordForm

#Adding simple Plotly Graph
import pandas as pd
import json
import plotly
import panel as pn
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.tools as tls
from matplotlib.lines import Line2D
from panel.interact import interact
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#Adding import yfinance as 
import yfinance as yf


#Adding Alpaca API Imports
import os
import requests
#Importing MCForecast Tool
#from MCForecastTools import MCSimulation

debugtoggle = True
# import alpaca_trade_api as tradeapi #####Commenting the deprecated way to call the API
from alpaca_trade_api.rest import REST, TimeFrame #Current way to import Alpaca API
#from dotenv import load_dotenv 
from dotenv import load_dotenv 
load_dotenv()
    

# Set Alpaca API key and secret
api_key1=os.getenv("ALPACA_API_KEY")

# Create the Alpaca API object
api_secret_key1=os.getenv("ALPACA_SECRET_KEY")


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

    
@app.route('/callback/<endpoint>')
def cb2(endpoint):   
    if endpoint == "getStock":
        #return gm(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
        return new_SO_Plot(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
    elif endpoint == "getInfo":
        stock = request.args.get('data')
        st = yf.Ticker(stock)
        return json.dumps(st.info)
    else:
        return "Bad endpoint", 400
    

    
#function to calculate the RSI Technical Indicator
def RSI(df, n=14):
    "function to calculate RSI"
    df = df.copy()
    df["change"] = df["Adj Close"] - df["Adj Close"].shift(1)
    df["gain"] = np.where(df["change"]>=0, df["change"], 0)
    df["loss"] = np.where(df["change"]<0, -1*df["change"], 0)
    df["avgGain"] = df["gain"].ewm(alpha=1/n, min_periods=n).mean()
    df["avgLoss"] = df["loss"].ewm(alpha=1/n, min_periods=n).mean()
    df["rs"] = df["avgGain"]/df["avgLoss"]
    df["rsi"] = 100 - (100/ (1 + df["rs"]))
    return df




def plotly_stochastic_oscillator(dfso, ticker, rng, periods=14):
    data = dfso.copy()
    fig_so= make_subplots(rows=2, cols=1)
    fig_so.append_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Adj Close'],
            increasing_line_color='green',
            decreasing_line_color='red',
            showlegend=False
        ), row=1, col=1
    )
    fig_so.append_trace(go.Scatter(x=data.index, y=data['K'], name='K',
                             line = dict(color='blue', width=2)), row = 2, col = 1)
    fig_so.append_trace(go.Scatter(x=data.index, y=data['D'], name='D',
                             line = dict(color='red', width=2)), row = 2, col = 1)
    # Make it pretty
    layout = go.Layout(
        height=1000, #width=1000,
        plot_bgcolor='#EFEFEF',
        # Font Families
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        title="Trading Indicator: Stochastic Oscillator",
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    # Update options and show plot
    fig_so.update_layout(layout)
    # Create Columns
    sto_ind = pn.Column(fig_so)
    return fig_so




#function stochastic_oscillator
def add_stochastic_oscillator(df, periods=14):
    copy = df.copy()
    high_roll = copy["High"].rolling(periods).max()
    low_roll = copy["Low"].rolling(periods).min()
    # Fast stochastic indicator
    num = copy["Adj Close"] - low_roll
    denom = high_roll - low_roll
    copy["K"] = (num / denom) * 100
    # Slow stochastic indicator
    copy["D"] = copy["K"].rolling(3).mean()   
    return copy
#dfso = add_stochastic_oscillator(df, periods=14)

today = dt.datetime.now()

date_pattern = "%Y-%m-%d"
today_str = today.strftime(date_pattern)
date_ranges = {
    "1M": (today - dt.timedelta(days=30)).strftime(date_pattern),
    "3M": (today - dt.timedelta(days=90)).strftime(date_pattern),
    "6M": (today - dt.timedelta(days=180)).strftime(date_pattern),
    "1Y": (today - dt.timedelta(days=365)).strftime(date_pattern),
    "2Y": (today - dt.timedelta(days=2*365)).strftime(date_pattern),
}


def plot_stochastic_oscillator(dfso, ticker, rng, periods=14):
    start = date_ranges[rng]
    end = today_str
    temp_df = dfso[start:end]
    
    fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True, tight_layout=True, figsize=(12, 10))

    ax[0].set_title(f"{ticker} price, {rng}")
    ax[0].plot(temp_df["Close"], color="tab:blue")

    ax[1].set_title(f"{ticker} Stochastic Oscillator ({periods}-day period), {rng}")
    ax[1].set_ylim(-10, 110)
    ax[1].plot(temp_df["K"], color="tab:blue") # fast
    ax[1].plot(temp_df["D"], color="tab:orange") # slow

    ax[1].axhline(80, color="tab:red", ls="--")
    ax[1].axhline(20, color="tab:green", ls="--")

    custom_lines = [
        Line2D([0], [0], color="tab:blue", lw=4),
        Line2D([0], [0], color="tab:orange", lw=4),
        Line2D([0], [0], color="tab:red", lw=4),
        Line2D([0], [0], color="tab:green", lw=4),
    ]
    ax[1].legend(custom_lines, ["K", "D", "Overbought", "Oversold"], loc="best")
    plotly_fig = tls.mpl_to_plotly(fig)
    return fig

#plot_stochastic_oscillator(dfso, ticker, "6M")

def new_SO_Plot(stock,period, interval):
    start = dt.datetime.today()-dt.timedelta(360)
    end = dt.datetime.today()
    s = dt.datetime.today()-dt.timedelta(90)
    e = dt.datetime.today()
    st = dt.datetime.today()-dt.timedelta(2)
    ed = dt.datetime.today()
    ticker = stock
    df = yf.download(stock, start, end)
    #df.head()
    dfso = add_stochastic_oscillator(df, periods=14)
    fig_stock = plotly_stochastic_oscillator(dfso, ticker, "6M")
    #plotly_fig = tls.mpl_to_plotly(fig_stock)
    #graphJSON_stock = json.dumps(plotly_fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON_stock = json.dumps(fig_stock, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON_stock
    
# Return the JSON data for the Plotly graph
def gm(stock,period, interval):
    st = yf.Ticker(stock)
    # Create a line graph
    df_stock = st.history(period=(period), interval=interval)
    df_stock=  df_stock.reset_index()
    df_stock.columns = ['Date-Time']+list(df_stock.columns[1:])
    df_stock.loc[:,'Symbol'] = stock
    max = (df_stock['Close'].max())
    min = (df_stock['Close'].min())
    range = max - min
    margin = range * 0.05
    max = max + margin
    min = min - margin
    chart_title = "Stock Data for " + stock
    fig_stock = px.area(df_stock, x='Date-Time', y="Open",
        hover_data=("Symbol","Open","Close","Volume"), 
        range_y=(min,max), template="seaborn", title=chart_title )


    
    
    # Create a JSON representation of the graph
    graphJSON_stock = json.dumps(fig_stock, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON_stock


def alpaca_get_market_data(stock,period, interval):
    start_date = "2019-04-10"
    end_date = "2022-04-10"
    # Set the tickers
    # tickers = "AAPL"
    tickers = stock
    timeframe = "1D"
    api = REST(api_key1, api_secret_key1, api_version='v2')
    df2 = api.get_bars(tickers, TimeFrame.Day, start_date, end_date, adjustment='raw').df
    df2.loc[:,'symbol'] = tickers
    max = (df2['close'].max())
    min = (df2['close'].min())
    range = max - min
    margin = range * 0.05
    max = max + margin
    min = min - margin
    chart_title = "Stock Data for " + stock
    fig_stock = px.area(df2, x=df2.index, y="open", hover_data=("symbol","open","close","volume"), 
        range_y=(min,max), template="seaborn", title=chart_title)
    graphJSON = json.dumps(fig_stock, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/Stock')
def stock():
    return render_template('stock.html')#,  graphJSON=gm())

@app.route('/Porfolio')
def portfolio():
    return render_template('portfolio.html')#,  graphJSON=gm())

@app.route('/Return')
def return_portfolio():
    return render_template('return.html')#,  graphJSON=gm())


@app.route('/Return-Portfolio')
def return_portfolio_all():
    return render_template('return_all.html')#,  graphJSON=gm())

@app.route('/Educate-Yourself')
def education():
    return render_template('education.html')#,  graphJSON=gm())

@app.route('/Career')
def career():
    return render_template('career.html')#,  graphJSON=gm())