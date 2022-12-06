import datetime
from datetime import datetime, timedelta
import time
import requests
import os
import json


class Util:
    __api_key = os.getenv('SUPAKEY')
    __authorization = os.getenv('SUPA_AUTH')
    __base_id = os.getenv('BASE_ID')
    
    def __get_date_list(self, start, end):
        ''' Given a start date and end date obtains the list of dates between them (as a date object)
        
        Args:
            start (datetime): the initial date
            end (datetime): the final date
        Returns:
            days (list): list of dates between start and end dates

        '''
        
        delta = end - start  # as timedelta
        days = [start + timedelta(days=i) for i in range(delta.days + 1)]
        return days

    def get_date_range(self, start:str, end:str) -> list:
        ''' Given a start date and end date obtains the list of dates between them (as string)
        
        Args:
            start (str): the initial date
            end (str): the final date
        Returns:
            dates (list of strings): list of dates between start and end dates

        '''

        datelist = [start, end]
        datelist_ = []
        for date in datelist:
            date = datetime.fromisoformat(date)
            datelist_.append(date)
        dates = self.__get_date_list(datelist_[0],datelist_[1])
        dates = [date.strftime('%Y-%m-%d') for date in dates]
        return dates

   
    def get_stock_details_from_polygon(self, ticker:str, date:str):
        ''' Given a ticker and a date get the response object from the polygon API
        
        Args:
            ticker (str): the stock ticker
            date (str): the date
        Returns:
            details_dict (dict): object with the data required

        '''
        print(f'getting details data from ticker {ticker} on {date} from polygon')
        response = requests.get(f'https://api.polygon.io/v3/reference/tickers/{ticker}?date={date}&apiKey=Fz_OgqhVpfFCvAyLTo2ct7Rhyn7LO5pS')
        response = response.json()
        if response['status'] == 'NOT_FOUND':
            print(f'no data found for ticker {ticker} on {date}')
        elif response['status'] == 'ERROR':
            print(f'API limit reached, waiting 60 seconds and trying again...')
            time.sleep(60)
        else:
            details_dict = { 
                'ticker': response['results']['ticker'],
                'name': response['results']['name'],
                'primary_exchange': response['results']['primary_exchange'],
                'market_cap': response['results']['market_cap'],
                'address': response['results']['address']['address1'],
                'sic_description': response['results']['sic_description'],
                'total_employees': response['results']['total_employees']   
            }
            return details_dict

    def get_daily_open_close_from_polygon(self, ticker:str, date:str):
        ''' Given a ticker and a date get the response object from the polygon API
        
        Args:
            ticker (str): the stock ticker
            date (str): the date
        Returns:
            open_close_dict (dict): dict object with the information required

        ''' 

        url = f'https://api.polygon.io/v1/open-close/{ticker}/{date}?adjusted=true&apiKey=Fz_OgqhVpfFCvAyLTo2ct7Rhyn7LO5pS'
        print(f'getting daily data from ticker {ticker} on {date} from polygon')
        response = requests.get(url)
        response = response.json()
        if response['status'] == 'NOT_FOUND':
            print(f'no data found for ticker {ticker} on {date}')
        elif response['status'] == 'ERROR':
            print(f'API limit reached, waiting 60 seconds and trying again...')
            time.sleep(60)
        else:
            open_close_dict = {'ticker': response['symbol'],
                                'date': response['from'],
                                'open': response['open'],
                                'low':response['low'], 
                                'high':response['high'],
                                'close':response['close'],
                                'volume':response['volume']
                            }
            return open_close_dict
    


    def get_data_from_db(self, table:str):
        ''' Given a table name returns data from the table
        
        Args:
            table (str): table name
        Returns:
            data (json): json object with data

        ''' 
        url = f'https://{self.__base_id}.supabase.co/rest/v1/{table}?select=*'
        headers = {'apikey': self.__api_key, 'Authorization': self.__authorization}
        r = requests.get(url=url, headers=headers)
        data = r.json()
        return data


    def upsert_data_into_db(self, table:str,data:list):
        ''' Given a table name and a dataframe upsert data into the table
        
        Args:
            table (str): table name
            data (list of dicts): data to insert in the db
        Returns:

        ''' 

        headers = {'apikey': self.__api_key, 'Authorization': self.__authorization,  'Prefer': 'resolution=merge-duplicates'}
        url = f'https://{self.__base_id}.supabase.co/rest/v1/{table}'

        for item in data: 
            try:
                a = requests.post(url=url, headers=headers, data = item)
                if a.status_code not in (200,201):
                    print(a.text)
            except Exception as e:
                print('An error has ocurred when trying to insert data into supabase/stock', e)


