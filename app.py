from flask import Flask, request
from flask_restful import Resource, Api
import pandas as pd
from util import Util
from main import main_process
from apscheduler.schedulers.background import BackgroundScheduler


util = Util()
app = Flask(__name__)
api = Api(app)

#run the main process in the background every 24 hs
sched = BackgroundScheduler(daemon=True)
sched.add_job(main_process,'interval',minutes=5)
sched.start()

class AvgOhlc(Resource):
    
    def get(self):
        tickers = request.args.get('tickers')
        data = util.get_data_from_db(table = 'avg_ohlc')  # get data from the summary table avg_ohlc
        if tickers is None:
            return {'data': data}, 200
        else:
            char_list = tickers.split(',')
            ticker_list = []
            for char in char_list:
                start_pos = char.find("'")
                from_char = char[start_pos+1:]
                end_pos = from_char.find("'")
                ticker_list.append(from_char[:end_pos])
            
            data_ = []
            for element in data:
                if element['ticker'] in ticker_list:
                    data_.append(element)
            return {'data': data_}, 200  # return data and 200 OK

class ClimateScoreCompany(Resource):
    
    def get(self):
        data = util.get_data_from_db(table = 'agg_company_per_climate')  # get data from the summary table agg_company...
        return {'data': data}, 200  # return data and 200 OK

class MarketCapRankAnalytics(Resource):
    
    def get(self):
        data = util.get_data_from_db(table = 'market_cap_rank_analytics')  # get data from the summary table agg_company...
        return {'data': data}, 200  # return data and 200 OK


api.add_resource(AvgOhlc, '/average_ohlc')  # add endpoints
api.add_resource(ClimateScoreCompany, '/climate_score_company_agg')
api.add_resource(MarketCapRankAnalytics, '/market_cap_rank_analytics')

if __name__ == '__main__':
    app.run()  