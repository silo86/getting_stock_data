#from logging import raiseExceptions
#import requests
from logger_config import LoggerConfig
#import logging
#import json
#import sys
from util import Util
from scrapper import Scrapper
from datetime import datetime, timedelta
from threading import Timer



loggerConfig = LoggerConfig()
logger = loggerConfig.get_logger()
util = Util()
scrapper = Scrapper()



def main_process():
    tickers = ['F','CMCSA','AAPL', 'ORCL', 'XRX', 'WOR', 'WSM', 'JNJ', 'WCC', 'MMM']
    daily_data = util.get_data_from_db(table = 'daily') 
    #if it is already data in daily table get only 1 day of data from polygon
    max_days = 7 if len(daily_data) == 0 else 1 
    yesterday = (datetime.now() - timedelta(1)).date()

    for ticker in tickers:
        details = []
        daily = []
        while len(details) < max_days:
            if yesterday.weekday() not in (5,6): #market only work on week days
                details.append(util.get_stock_details_from_polygon(ticker, yesterday.strftime('%Y-%m-%d') ))
            while(None in details):
                details.remove(None)
            yesterday = yesterday - timedelta(1)
            
        yesterday = (datetime.now() - timedelta(1)).date()
        while len(daily) < max_days:
            if yesterday.weekday() not in (5,6): #market only work on week days
                daily.append(util.get_daily_open_close_from_polygon(ticker, yesterday.strftime('%Y-%m-%d') ))
            while(None in daily):
                daily.remove(None)
            yesterday = yesterday - timedelta(1)
        yesterday = (datetime.now() - timedelta(1)).date()
        util.upsert_data_into_db('stock',details)
        util.upsert_data_into_db('daily',daily)
    climate_list = scrapper.get_climate_change_score(tickers,'https://www.google.com/finance/') #google url
    util.upsert_data_into_db('climate_score',climate_list)
main_process()




