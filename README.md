# OntoStreamLearn
## KBPA_StockPrediction

The Stock Price Data: extracted from the Google Finance API(http://files.statworx.com/sp500.zip).
It contains minutely price records of 500 stocks from S&P 500, ranging from 3rd April to 31th August in 2017. Note that they are cleaned for bank holidays, and aligned with Twitter text by time. In order to align the stock price data with real-time text data, we have chosen the time span of one day. Thus the dataset is managed into daily data.

Background Knowledge of Stocks: It contains correlative companies information of S&P 500 component stocks, which is stored in a knowledge graph. 
Each stock is issued by corresponding Security (also called company), which has GICS Sector, GICS Sub Industry, and Address of Headquarters. 
These background knowledge are all extracted from Wikipedia. 
For example, ABT is one of S&P 500 Component Stocks, and the background knowledge are represented in the form of triples, including ⟨sp500, correlativeStock, ABT⟩, ⟨ABT, relatedSecurity, Abbott Laboratories⟩, ⟨ABT, relatedSector, Health Care⟩, ⟨ABT, relatedSubIndustry, Health Care Equipment⟩, ⟨ABT, relatedCity, North Chicago⟩, ⟨ABT, relatedState, Illinois⟩.

Real-time Text Data for Stocks: It contains social media data related to S&P 500 index and stocks when the stock market opening. 
We have extracted 98617 tweets with respect to S&P 500 index, from 3rd, April, 2017 to 31st, August, 2017. 

For details, you can refer to the paper "Deep Learning for Knowledge-Driven Ontology Stream Prediction" (https://link.springer.com/chapter/10.1007/978-981-13-3146-6_5)

