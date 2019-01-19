This package contains the code and data for the air quality forecasting context of the paper - "Learning from ontology streams with semantic concept drift". 
To run the code, you need the following softwares installed:

Java devlopment environment:

    1. Oracle JDK 1.7 (Other versions may also be OK, but are not tested.)

    2. Eclipse 4.4.2 (with Maven)

Database: Mongo DB 3.0.1

Python: 2.7

sklearn:

Data (download by https://goo.gl/UXEw9C):

    1. Air quality data are stored in DB:Air, Collection:Stations

    2. Meteorology data are stored in DB:forecastio, Collection:Beijing 

    3. Information of the stations: station_location.csv

Air data and meteorology data are separatedly exported to files with "mongodump -d db_name -o dir" command. You can use "mongorestore -d db_name -o dir/*" commend to separatedly import them into Mongo DB.

Protege Desktop: 5.0.0

    smog.owl is in dir "smog_forecast".


The whole program contains two parts: 1)java program: map data to assertions, reason, calculate consistence coefficient, and extract samples; 2)python program: ML model training and testing

You can check the java program by importing "smog_forecast" into eclipse. Jar packages can be managed by maven. You can set the parameters of input/output in DataConfig.java. It includes four steps (main function). They should be excuted one by one. They are Job0_entailment.java, Job1_correlation.java, Job2_NormalSamples.java, Job3_ConsistentSamples.jar. There are comments for details in each file. Especially, Job0_entailment.java is quite coupled with the ontology and application. You can run reasoning with Job0 and Job1 (identified by reason_id), and then run Job2 and Job3 for samples (identified by exp_id) independently, so that you can reuse the results of Job0 and Job1.

The python_code mainly contains the following files:

1. base_eva.py: use basic features (you can select F1, F2, F3 or the combinations), SGD method, withoutconsidering samples' consistence

2. consistent_eav.py: base_eva.py's functions + consider samples' consistence

3. SGD_weight_eva.py: consistent_eva.py's functions + different settings of the transformation function g

4. splitweight.py + Correlation_compare.bat: used for Exp4. 
