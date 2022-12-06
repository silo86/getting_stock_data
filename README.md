# getting_stock_data
**Steps to install:**
- 1) Install requirements.txt
- 2) Create the following 3 main tables in Supabase:

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
	);  

	create table climate_score  
	(  
	  ticker varchar NOT NULL,  
	  date varchar NOT NULL,  
	  climate_change_score varchar,  
	  PRIMARY KEY(ticker, date),  

	);  

Stock and daily tables are filled from polygon API, climate_score info is scrapped from google/finance.

- 3) Create additional tables to store calculations based on the 3 main tables. The following tables are automatically updated via trigger functions when any changes occurs in one of the main tables (daily, stock):

	create table avg_ohlc  
	(  
	  ticker varchar NOT NULL,  
	  open numeric,  
	  high numeric,  
	  low numeric,  
	  close numeric,  
	  volume numeric,  
	  PRIMARY KEY(ticker),  
	);  

	create table agg_company_per_climate    
	(  
	  ticker varchar NOT NULL,  
	  climate_change_score varchar,  
	  name varchar,  
	  PRIMARY KEY(ticker,climate_change_score)  
	);  

	create table companies_rank_by_market_cap  
	(  
	market_cap_rank varchar,  
	score_rank int ,  
	ticker varchar NOT NULL,  
	max_mc numeric,  
	PRIMARY KEY(ticker)  
	);  

	create table market_cap_rank_analytics  
	(  
	market_cap_rank varchar NOT NULL,  
	avg_market_cap numeric,  
	avg_num_employees numeric ,  
	avg_weekly_volume numeric,  
	PRIMARY KEY(market_cap_rank)  
	);  

- 4) Create the following functions in supabase with return type trigger: agg_company_per_climate_function, avg_ohlc_function, companies_rank_by_mc_function and report_3_function with the following code:  
	--agg_company_per_climate_function
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

	--avg_ohlc_function
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
	  
	--companies_rank_by_mc_function  
	begin 
	insert into public.companies_rank_by_market_cap(market_cap_rank, score_rank, ticker, max_mc)  
	with rank_by_market_cap as  
	(  
	select  
	RANK() OVER (ORDER BY max(market_cap) DESC) AS score_rank,  
	ticker,  
	max(market_cap) as max_mc  
	from stock  
	group by ticker  
	order by max(market_cap) desc  
	)  
 
	select 
	case when score_rank in (1,2,3) then 'large_cap'  
	when score_rank in (8,9,10) then 'small_cap'  
	else 'mid_cap' end as market_cap_rank,  
	*  
	from rank_by_market_cap  
	on conflict(ticker)  
	do update set market_cap_rank = EXCLUDED.market_cap_rank,  
	score_rank = EXCLUDED.score_rank,  
	max_mc = EXCLUDED.max_mc;  
	return null;  
	end;  

	--report_3_function
	begin 
	insert into public.market_cap_rank_analytics(market_cap_rank, avg_market_cap, avg_num_employees, avg_weekly_volume)
	select
	market_cap_rank,
	--extract(year from s.date::date) as year,
	--extract(week from s.date::date) as week,
	avg(s.market_cap) as avg_market_cap,
	avg(s.total_employees) as avg_num_employees,
	avg(volume) as avg_weekly_volume
	from stock s
	left join daily as d on d.ticker = s.ticker and d.date= s.date
	left join companies_rank_by_market_cap cr
	on s.ticker = cr.ticker
	group by market_cap_rank--, year, week
	on conflict(market_cap_rank)
	do update set avg_market_cap = EXCLUDED.avg_market_cap,
	avg_num_employees = EXCLUDED.avg_num_employees,
	avg_weekly_volume = EXCLUDED.avg_weekly_volume;
	return null;
	end;


- 5) Create four triggers with events after update, after insert and after delete in Supabase:  
- agg_company_per_climate_trigger pointing climate_score (so when this table suffer any change the trigger upsert agregated data in table agg_company_per_climate.)    
- ohlc_trigger  pointing daily table  (so when this table suffer any change the trigger upsert agregated data in table avg_ohlc.)  
- companies_rank_by_mc_trigger pointing table stock (so when this table suffer any change the trigger upsert agregated data in table companies_rank_by_market_cap.) 
- report_3_trigger pointing table stock (so when this table suffer any change the trigger upsert agregated data in table market_cap_rank_analytics.)

- 6) Add apikey, authorization and supabaseUrl provided by supabase API to your environment variables as SUPAKEY, SUPA_AUTH, BASE_ID 

- 7) Run app.py (the app runs a flask server listening to /average_ohlc and /climate_score_company_agg endpoints which return aggregated information about stocks. Also in background runs a script to get data from APIs and scrape data from google finance every day)
