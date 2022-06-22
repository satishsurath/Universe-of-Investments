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
import numpy as np
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


pd.DataFrame()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

    
@app.route('/callback/<endpoint>')
def cb2(endpoint):   
    if endpoint == "getStock":
        #return gm(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
        return new_SO_Plot(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
    elif endpoint == "getPASR_MA":
        #return gm(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
        return new_PASR_MA_Plot(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
    elif endpoint == "getPASR_MA_large":
        #return gm(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
        return new_PASR_MA_Plot_large(request.args.get('data'),request.args.get('period'),request.args.get('interval'))    
    elif endpoint == "TradingSignal":
        end = dt.datetime.today()
        s = dt.datetime.today()-dt.timedelta(90)
        e = dt.datetime.today()
        st = dt.datetime.today()-dt.timedelta(2)
        ed = dt.datetime.today()
        stock = request.args.get('data')
        ticker = yf.Ticker(stock)
        #df = yf.download(stock, start, end)
        df = ticker.history(period="2y")
        df = psar(df)
        string_frame = df.iloc[-1].to_string()
        return tradeSignal(df["signal"].iloc[-1], string_frame, stock)
    elif endpoint == "getInfo":
        stock = request.args.get('data')
        st = yf.Ticker(stock)
        return json.dumps(st.info)
    else:
        return "Bad endpoint", 400
    

def new_PASR_MA_Plot_large(stock,period, interval):
    start = dt.datetime.today()-dt.timedelta(360)
    end = dt.datetime.today()
    s = dt.datetime.today()-dt.timedelta(90)
    e = dt.datetime.today()
    st = dt.datetime.today()-dt.timedelta(2)
    ed = dt.datetime.today()
    ticker = yf.Ticker(stock)
    #df = yf.download(stock, start, end)
    df = ticker.history(period="2y")
    #df.head()
    #dfso = add_stochastic_oscillator(df, periods=14)
    df = psar(df)
    #df_global_store = df.copy()
    fig_stock = PSAR_MA_Strategy_large(df.tail(252))
    graphJSON_stock = json.dumps(fig_stock, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON_stock


def new_PASR_MA_Plot(stock,period, interval):
    start = dt.datetime.today()-dt.timedelta(360)
    end = dt.datetime.today()
    s = dt.datetime.today()-dt.timedelta(90)
    e = dt.datetime.today()
    st = dt.datetime.today()-dt.timedelta(2)
    ed = dt.datetime.today()
    ticker = yf.Ticker(stock)
    #df = yf.download(stock, start, end)
    df = ticker.history(period="2y")
    #df.head()
    #dfso = add_stochastic_oscillator(df, periods=14)
    df = psar(df)
    #df_global_store = df.copy()
    fig_stock = PSAR_MA_Strategy(df.tail(252))
    graphJSON_stock = json.dumps(fig_stock, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON_stock




def psar(df, iaf = 0.02, maxaf = 0.2):
    length = len(df)
    dates = list(df.index)
    high = list(df['High'])
    low = list(df['Low'])
    close = list(df['Close'])
    psar = close[0:len(close)]
    psarbull = [None] * length
    psarbear = [None] * length
    bull = True
    af = iaf
    ep = low[0]
    hp = high[0]
    lp = low[0]

    for i in range(2,length):
        if bull:
            psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
        else:
            psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
        reverse = False
        if bull:
            if low[i] < psar[i]:
                bull = False
                reverse = True
                psar[i] = hp
                lp = low[i]
                af = iaf
        else:
            if high[i] > psar[i]:
                bull = True
                reverse = True
                psar[i] = lp
                hp = high[i]
                af = iaf
        if not reverse:
            if bull:
                if high[i] > hp:
                    hp = high[i]
                    af = min(af + iaf, maxaf)
                if low[i - 1] < psar[i]:
                    psar[i] = low[i - 1]
                if low[i - 2] < psar[i]:
                    psar[i] = low[i - 2]
            else:
                if low[i] < lp:
                    lp = low[i]
                    af = min(af + iaf, maxaf)
                if high[i - 1] > psar[i]:
                    psar[i] = high[i - 1]
                if high[i - 2] > psar[i]:
                    psar[i] = high[i - 2]
        if bull:
            psarbull[i] = psar[i]
        else:
            psarbear[i] = psar[i]
 
    startidx = 0
    endidx = len(df)

    result = {"dates":dates, "high":high, "low":low, "close":close, "psar":psar, "psarbear":psarbear, "psarbull":psarbull}
    df["dates"] = result['dates'][startidx:endidx]
    df["close"] = result['close'][startidx:endidx]
    df["psarbear"] = result['psarbear'][startidx:endidx]
    df["PSAR"] = result['psar'][startidx:endidx]
    df["psarbull"] = result['psarbull'][startidx:endidx]
    df['Slow MA'] = df['Close'].rolling(200).mean()
    df['200 MA'] = df["Close"].rolling(200).mean()
    # df['9 MA'], df['21 MA'] = talib.MA(df['Adj Close'], timeperiod=9, matype=0), talib.MA(df['Adj Close'], timeperiod=21, matype=0)
    #df['PSAR'] = real = talib.SAR(df['High'], df['Low'], acceleration=0.02, maximum=0.2)
    # df['upperband'], df['middleband'], df['lowerband'] = talib.BBANDS(df['Adj Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['Action'] = np.where(df['Close'] > df['200 MA'] , 1, 0) 
    df['Action'] = np.where(df['Close'] < df['200 MA'], -1, df['Action'])
    df['PSAR_Action'] = np.where(df['PSAR'] < df['Low'] , 1, 0) 
    df['PSAR_Action'] = np.where(df['PSAR'] > df['High'], -1, df['PSAR_Action'])  
    df['signal'] = df.apply(signal, axis = 1)
    return df



def PSAR_MA_Strategy(df):
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'],name="Candlestick")])

    fig.add_trace(go.Scatter(x=df.index, y=df["psarbull"], name='Buy',mode = 'markers',
                         marker = dict(color='green', size=4)))

    fig.add_trace(go.Scatter(x=df.index, y=df["psarbear"], name='Short / Sell', mode = 'markers',
                         marker = dict(color='red', size=4)))

    fig.add_trace(go.Scatter(x=df.index, y=df['Slow MA'], name='200 Day SMA',
                         line = dict(color='orange', width=2)))

    # fig.add_trace(go.Scatter(x=dfp.index, y=dfp['Fast MA'], name='fast MA',
    #                          line = dict(color='Blue', width=2)))
    # Make it pretty
    layout = go.Layout(
        height=300, #width=1000,
        plot_bgcolor='#EFEFEF',
        # Font Families
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        title="<b>Trading Indicator:</b> Parabolic Stop & Reverse (PSAR)<br>& 200 Days Simple Moving Average Strategy",
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    # Update options and show plot
    fig.update_layout(layout)

    return fig

def PSAR_MA_Strategy_large(df):
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'],high=df['High'],low=df['Low'],close=df['Close'],name="Candlestick")])

    fig.add_trace(go.Scatter(x=df.index, y=df["psarbull"], name='Buy',mode = 'markers',
                         marker = dict(color='green', size=4)))

    fig.add_trace(go.Scatter(x=df.index, y=df["psarbear"], name='Short / Sell', mode = 'markers',
                         marker = dict(color='red', size=4)))

    fig.add_trace(go.Scatter(x=df.index, y=df['Slow MA'], name='200 Day SMA',
                         line = dict(color='orange', width=2)))

    # fig.add_trace(go.Scatter(x=dfp.index, y=dfp['Fast MA'], name='fast MA',
    #                          line = dict(color='Blue', width=2)))
    # Make it pretty
    layout = go.Layout(
        height=1000, #width=1000,
        plot_bgcolor='#EFEFEF',
        # Font Families
        font_family='Monospace',
        font_color='#000000',
        font_size=20,
        title="<b>Trading Indicator:</b> Parabolic Stop & Reverse (PSAR)<br>& 200 Days Simple Moving Average Strategy",
        xaxis=dict(
            rangeslider=dict(
                visible=False
            )
        )
    )
    # Update options and show plot
    fig.update_layout(layout)

    return fig

def tradeSignal(trading_signal_flag,diagnostic_info, stock):
    #df.tail(100)
    # IF df.iloc[-1] == 0 THEN "Closing Position / Do Nothing"
    # IF df.iloc[-1] == 1 THEN "BUY"
    # IF df.iloc[-1] == -1 THEN "SELL / SHORT Sell"
    if trading_signal_flag > 0:
        return "Based on <b>Trading Indicator:</b> Parabolic Stop & Reverse (PSAR) & 200 Days Simple Moving Average Strategy for the Stock <b>" + stock +"</b><br> The Trading Signal is to <b>BUY </b><br><small style='color:#aaa'><br>diagnostic_info:<br>" + diagnostic_info + "</small>"
    elif trading_signal_flag < 0:
        return "Based on <b>Trading Indicator:</b> Parabolic Stop & Reverse (PSAR) & 200 Days Simple Moving Average Strategy for the Stock <b>" + stock +"</b><br> The Trading Signal is to <b>SHORT / SELL</b><br><small style='color:#aaa'><br>diagnostic_info:<br>" + diagnostic_info + "</small>"
    else:
        return "Based on <b>Trading Indicator:</b> Parabolic Stop & Reverse (PSAR) & 200 Days Simple Moving Average Strategy for the Stock <b>" + stock +"</b><br> The Trading Signal is to <b>Close Position</b><br><small style='color:#aaa'><br>diagnostic_info:<br>" + diagnostic_info + "</small>"


    
    
def signal(df):
    if df['Action'] == 1 and df['PSAR_Action'] == 1:
        return 1
    elif df['Action'] == -1 and df['PSAR_Action'] == -1:
        return -1
    else:
        return 0
    


@app.route('/Stock')
def stock():
    return render_template('stock.html')#,  graphJSON=gm())

@app.route('/Porfolio')
def portfolio():
    return render_template('portfolio.html')#,  graphJSON=gm())

@app.route('/Return')
def return_portfolio():
    return render_template('return.html')#,  graphJSON=gm())

@app.route('/Trading-Indicators-for-Portfolio')
def return_trading_Indicators_for_Portfolio():
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



   



