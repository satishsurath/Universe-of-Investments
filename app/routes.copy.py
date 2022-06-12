from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.models import User
from flask import request
from datetime import datetime

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


#Adding import yfinance as 
import yfinance as yf


#Adding Alpaca API Imports
import os
import requests
#Importing MCForecast Tool
from MCForecastTools import MCSimulation

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

#Used for GDP Graph
@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return gm_gdp(request.args.get('data'))

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/new')
def new():
    return render_template('new.html', title='New')
    
    

    
@app.route('/callback2/<endpoint>')
def cb2(endpoint):   
    if endpoint == "getStock":
        return gm(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
    elif endpoint == "getInfo":
        stock = request.args.get('data')
        st = yf.Ticker(stock)
        return json.dumps(st.info)
    else:
        return "Bad endpoint", 400
    
@app.route('/callback3/<endpoint>')
def cb3(endpoint):   
    if endpoint == "getStock":
        return alpaca_get_market_data(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
    elif endpoint == "getInfo":
        stock = request.args.get('data')
        st = yf.Ticker(stock)
        return json.dumps(st.info)
    elif endpoint == "getReturn":
        return mcforecast_get_data(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
    else:
        return "Bad endpoint", 400
    
@app.route('/callback4/<endpoint>')
def cb4(endpoint):   
    if endpoint == "getStock":
        return alpaca_get_market_data(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
    elif endpoint == "getInfo":
        stock = request.args.get('data')
        st = yf.Ticker(stock)
        return json.dumps(st.info)
    elif endpoint == "getReturn":
        return mcforecast_get_data(request.args.get('data'),request.args.get('period'),request.args.get('interval'))
    elif endpoint == "getPortfolio":
        return mcforecast_get_portfolio(request.args.get('stock1'),request.args.get('stock2'),request.args.get('stock3'),request.args.get('stock4'),request.args.get('stock5'))
    elif endpoint == "getCumulativeReturn":
        return mcforecast_get_portfolio_cumulative_return(request.args.get('stock1'),request.args.get('stock2'),request.args.get('stock3'),request.args.get('stock4'),request.args.get('stock5'))
    else:
        return "Bad endpoint", 400
    
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


def mcforecast_get_data(stock,period, interval):
    start_date = "2019-04-10"
    end_date = "2022-04-10"
    # Set the tickers
    # tickers = "AAPL"
    tickers = stock
    timeframe = "1D"
    api = REST(api_key1, api_secret_key1, api_version='v2')
    df2 = api.get_bars(tickers, TimeFrame.Day, start_date, end_date, adjustment='raw').df
    df2.loc[:,'symbol'] = tickers
    pivottable = pd.pivot_table(df2, values='close', index=df2.index, columns=['symbol'])
    ticker_name = [(x,'close') for x in pivottable.columns]
    micolumns = pd.MultiIndex.from_tuples(ticker_name)
    pivottable.columns = micolumns
    chart_title = "Percentage Change for " + stock
    MC_5years = MCSimulation(portfolio_data = pivottable,
        weights = [1],
        num_simulation = 100,
        num_trading_days = 252*5
    )
    

    micolumns = ['close','daily_return']
    MC_5years.portfolio_data.columns = micolumns
    max = (MC_5years.portfolio_data['daily_return'].max())
    min = (MC_5years.portfolio_data['daily_return'].min())
    range = max - min
    margin = range * 0.05
    max = max + margin
    min = min - margin
    
    fig_stock = px.area(MC_5years.portfolio_data, x=MC_5years.portfolio_data.index, y='daily_return', 
        range_y=(min,max), template="seaborn", title=chart_title)
    graphJSON = json.dumps(fig_stock, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def mcforecast_get_portfolio(stock1,stock2,stock3,stock4,stock5):
    start_date = "2019-04-10"
    end_date = "2022-04-10"
    # Set the tickers
    # tickers = "AAPL"
    tickers = [stock1,stock2,stock3,stock4,stock5]
    timeframe = "1D"
    api = REST(api_key1, api_secret_key1, api_version='v2')
    df2 = api.get_bars(tickers, TimeFrame.Day, start_date, end_date, adjustment='raw').df
    pivottable = pd.pivot_table(df2, values='close', index=df2.index, columns=['symbol'])
    ticker_name = [(x,'close') for x in pivottable.columns]
    micolumns = pd.MultiIndex.from_tuples(ticker_name)
    pivottable.columns = micolumns
    #chart_title = "Montecarlo Simulations for " + tickers[0] + ";" + tickers[1] + ";" + tickers[2] + ";" + tickers[3] + ";" + tickers[4] + ";"
    MC_5years = MCSimulation(portfolio_data = pivottable,
        weights = [0.2,0.2,0.2,0.2,0.2],
        num_simulation = 100,
        num_trading_days = 252*5
    )
    MC_5years.calc_cumulative_return()    
    plot_title = f"{MC_5years.nSim} Simulations of Cumulative Portfolio Return Trajectories Over the Next {MC_5years.nTrading} Trading Days."
    fig_stock = px.line(MC_5years.simulated_return, template="seaborn", title=plot_title)
    fig_stock.update_layout(showlegend=False)
    graphJSON = json.dumps(fig_stock, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def mcforecast_get_portfolio_cumulative_return(stock1,stock2,stock3,stock4,stock5):
    start_date = "2019-04-10"
    end_date = "2022-04-10"
    # Set the tickers
    # tickers = "AAPL"
    tickers = [stock1,stock2,stock3,stock4,stock5]
    timeframe = "1D"
    api = REST(api_key1, api_secret_key1, api_version='v2')
    df2 = api.get_bars(tickers, TimeFrame.Day, start_date, end_date, adjustment='raw').df
    pivottable = pd.pivot_table(df2, values='close', index=df2.index, columns=['symbol'])
    ticker_name = [(x,'close') for x in pivottable.columns]
    micolumns = pd.MultiIndex.from_tuples(ticker_name)
    pivottable.columns = micolumns
    #chart_title = "Montecarlo Simulations for " + tickers[0] + ";" + tickers[1] + ";" + tickers[2] + ";" + tickers[3] + ";" + tickers[4] + ";"
    MC_5years = MCSimulation(portfolio_data = pivottable,
        weights = [0.2,0.2,0.2,0.2,0.2],
        num_simulation = 100,
        num_trading_days = 252*5
    )
    MC_5years.calc_cumulative_return()    
    initial_investment = 1000
    # Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $20,000
    ci_lower = round(MC_5years.confidence_interval.iloc[0] * initial_investment, 2)
    ci_upper = round(MC_5years.confidence_interval.iloc[1] * initial_investment, 2)
    # Print results
    data = {}
    cumulative_return = (f"Using <span class='maindiv'>"
                f"<span style='text-decoration: underline;background:#d4dbef;' data-hover=''> Monte-Carlo Simulation, </span> <span class='test'>Monte Carlo simulation (also known as the Monte Carlo Method) lets you see all the possible outcomes of your decisions and assess the impact of risk.<a href='/Educate-Yourself#Monte-Carlo' target='_blank'>Read More</a></span></span>" 
        f" with 95%  <span class='maindiv'>"
                f"<span style='text-decoration: underline;background:#d4dbef;' data-hover=''> confidence, </span> <span class='test'>Learn about the value at risk, how confidence intervals and confidence levels are used to interpret the value at risk and the difference between the two.<a href='/Educate-Yourself#Confidence' target='_blank'>Read More</a></span></span>  "
        f" the projected <span class='maindiv'><span style='text-decoration: underline;background:#d4dbef;' data-hover=''> return, </span> <span class='test'>Return is the financial gain or loss on an investment. Yield measures the income, such as interest and dividends, from an investment and is expressed as a percentage.<a href='/Educate-Yourself#Return' target='_blank'>Read More</a></span></span>  on an initial investment of ${initial_investment} in the portfolio"
      f" over the next 5 years will fall within in the range of"
      f" ${ci_lower:,} and ${ci_upper:,}"
      f"<br><br> This site is for educational and demonstation purposes, only and should not be relied upon as Finanacial Advice")    
    data['key'] = cumulative_return
    json_data = json.dumps(data)
    return json_data



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