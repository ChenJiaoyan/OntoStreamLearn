# OntoStreamLearn
This space contains some codes and data for our work on ontology stream reasoning and leanring.

1. predictive_reasoning/: "Learning from ontology streams with semantic concept drift" (IJCAI-17), Chen, Jiaoyan, Freddy Lécué, Jeff Pan, and Huajun Chen. 

2. KBPA_StockPrediction/: "Deep Learning for Knowledge-Driven Ontology Stream Prediction." (CCKS-18), Deng, Shumin, Jeff Z. Pan, Jiaoyan Chen, and Huajun Chen.

3. WBOE_predictive_reasoning/: "Concept Drift in Ontology Streams? Embedding Semantics for Representation Learning" (Journal of Web Semantics, 2019),  Chen, Jiaoyan, Freddy Lécué, Jeff Pan, Chen Huajun and Deng, Shumin (under revision).

## Air quality and meteology data
Air quality and meteology data (download by https://goo.gl/UXEw9C):

    1. Air quality data are stored in DB:Air, Collection:Stations

    2. Meteorology data are stored in DB:forecastio, Collection:Beijing 

    3. Information of the stations: station_location.csv

Air data and meteorology data are separatedly exported to files with "mongodump -d db_name -o dir" command. You can use "mongorestore -d db_name -o dir/*" commend to separatedly import them into Mongo DB.


## Data for KBPA_StockPrediction

    1. The Stock Price Data: extracted from the Google Finance API(http://files.statworx.com/sp500.zip).
    It contains minutely price records of 500 stocks from S&P 500, ranging from 3rd April to 31th August in 2017. 

    2. Background Knowledge of Stocks: It contains correlative companies information of S&P 500 component stocks, which is stored in a knowledge graph, extracted from Wikipedia
    
    3. Real-time Text Data for Stocks: It contains social media data related to S&P 500 index and stocks when the stock market opening.  We have extracted 98617 tweets with respect to S&P 500 index, from 3rd, April, 2017 to 31st, August, 2017. 

For details, you can refer to the paper "Deep Learning for Knowledge-Driven Ontology Stream Prediction" (https://link.springer.com/chapter/10.1007/978-981-13-3146-6_5)

## Note
The codes have been out of maintenance. Please contact Jiaoyan Chen for any questions or interests.
