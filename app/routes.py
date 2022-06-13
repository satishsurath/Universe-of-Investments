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
    fig_so.append_trace(go.Scatter(x=data.index, y=data['Oversold'], name='Oversold',
                         line = dict(color='green', width=2, dash='dash')), row = 2, col = 1)
    fig_so.append_trace(go.Scatter(x=data.index, y=data['Overbought'], name='Overbought',
                         line = dict(color='red', width=2, dash='dash')), row = 2, col = 1)
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
    return fig_so




#function stochastic_oscillator
def add_stochastic_oscillator(df, periods=14):
    df_return = df.copy()
    high_roll = df_return["High"].rolling(periods).max()
    low_roll = df_return["Low"].rolling(periods).min()
    # Fast stochastic indicator
    num = df_return["Adj Close"] - low_roll
    denom = high_roll - low_roll
    df_return["K"] = (num / denom) * 100
    # Slow stochastic indicator
    df_return["D"] = df_return["K"].rolling(3).mean()
    df_return['Oversold'] = 20
    df_return['Overbought'] = 80
    return df_return

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