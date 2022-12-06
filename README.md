# getting_stock_data
**Steps to install:**
- 1) Install requirements.txt
- 2) Create the following tables in Supabase:

	create table stock  
	(  
	  ticker varchar NOT NULL,  
	  name varchar NOT NULL,  
	  primary_exchange varchar,  
	  market_cap numeric,  
	  address varchar,  
	  sic_description varchar,  
	  total_employees numeric,  
	  PRIMARY KEY(ticker)  
	);  

	create table daily  
	(  
	  ticker varchar NOT NULL,  
	  date varchar NOT NULL,  
	  open numeric,  
	  low numeric,  
	  high numeric,  
	  close numeric,  
	  volume numeric,  
	  PRIMARY KEY(ticker, date),  
	  FOREIGN KEY (ticker) REFERENCES stock(ticker)  
	);  

	create table climate_score  
	(  
	  ticker varchar NOT NULL,  
	  date varchar NOT NULL,  
	  climate_change_score varchar,  
	  PRIMARY KEY(ticker, date),  
	  FOREIGN KEY (ticker) REFERENCES stock(ticker)  

	);  

Stock and daily tables are filled from polygon API, climate_score info is scrapped from google/finance.

- 3) Create two additional tables. The following tables are automatically updated via trigger functions when any changes occurs in one of the main tables (daily, stock):

	create table avg_ohlc  
	(  
	  ticker varchar NOT NULL,  
	  open numeric,  
	  high numeric,  
	  low numeric,  
	  close numeric,  
	  volume numeric,  
	  PRIMARY KEY(ticker),  
	  FOREIGN KEY (ticker) REFERENCES stock(ticker)  
	);  

	create table agg_company_per_climate    
	(  
	  ticker varchar NOT NULL,  
	  climate_change_score numeric,  
	  name varchar,  
	  PRIMARY KEY(ticker)  
	);  

- 4) Create two functions in supabase with return type trigger:agg_company_per_climate_function and avg_ohlc_function with the following code:  

	begin
		insert into public.agg_company_per_climate(ticker, climate_change_score, name)  
			select distinct  
			s.ticker,  
			climate_change_score,  
			s.name  
			from climate_score c  
			left join stock s   
			on s.ticker = c.ticker  
			order by climate_change_score asc  
	on conflict(ticker, climate_change_score)  
	do nothing;  
	return null;  
	end;  

	begin  
	  insert into public.avg_ohlc(ticker, open, high, low, close, volume)  
		SELECT ticker,  
		ROUND(AVG(open),4) as open,  
		ROUND(AVG(high),4) as high,  
		ROUND(AVG(low),4) as low,  
		ROUND(AVG(close),4) as close,  
		ROUND(AVG(volume),4) as volume  
		FROM daily  
		group by ticker  
	on conflict(ticker)   
	do update set open = EXCLUDED.open,  
				  high = EXCLUDED.high,  
				  low = EXCLUDED.low,  
				  close = EXCLUDED.close,  
				  volume = EXCLUDED.volume;  
	return null;  
	end;  

- 5) Create two triggers in Supabase:  
agg_company_per_climate_trigger and ohlc_trigger with events after delete, after insert and after delete.  
The first pointing climate_score and the second pointing daily table (so when these tables suffer any change the triggers insert agregated data in agg_company_per_climate and avg_ohlc)

- 6) Add apikey and authorization provided by supabase API to your environment variables as SUPAKEY and SUPA_AUTH  

- 7) Run app.py (the app runs a flask server listening to /average_ohlc and /climate_score_company_agg endpoints which return aggregated information about stocks. Also in background runs a script to get data from APIs and scrape data from google finance every day)
