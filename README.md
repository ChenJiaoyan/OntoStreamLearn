# OntoStreamLearn
This space contains some codes and data for our work on ontology stream reasoning and leanring.

1. predictive_reasoning/: "Learning from ontology streams with semantic concept drift" (IJCAI-17), Chen, Jiaoyan, Freddy Lécué, Jeff Pan, and Huajun Chen. 


2. KBPA_StockPrediction/: "Deep Learning for Knowledge-Driven Ontology Stream Prediction." (CCKS-18), Deng, Shumin, Jeff Z. Pan, Jiaoyan Chen, and Huajun Chen.

Air quality and meteology data (download by https://goo.gl/UXEw9C):

    1. Air quality data are stored in DB:Air, Collection:Stations

    2. Meteorology data are stored in DB:forecastio, Collection:Beijing 

    3. Information of the stations: station_location.csv

Air data and meteorology data are separatedly exported to files with "mongodump -d db_name -o dir" command. You can use "mongorestore -d db_name -o dir/*" commend to separatedly import them into Mongo DB.


The codes have been out of maintenance. Please contact Jiaoyan Chen for any questions or interests.
