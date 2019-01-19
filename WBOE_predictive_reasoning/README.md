#predictive reasoning with weighted bag of entailment
Experiment codes for air quality level forecasting for the paper "Concept Drift in Ontology Streams? Embedding Semantics with Representation Learning", which is an extension of IJCAI-17 paper.


Following two stations are forecasted:

Beijing (Target station): 奥体中心 Aotizhongxin (1011A) (116.403458,39.98966406)
Surrounding stations:
NorthEast: 顺义新城 Shunyixinheng (1008A) (116.664263,40.17700804)
NorthWest: 昌平镇 Changping (1010A) (116.2330318,40.22994018)
SouthWest: 古城 Gucheng (1012A) (116.1956398,39.91345006)
SouthEast: 农展馆 Nongzhanguan (1005A) (116.470307,39.94700908)

Hangzhou (Target station): 杭州农大 Hangzhounongda (1228A) (120.202073,30.27526505)
Surrounding stations:    
NorthEast: 下沙 Xiasha (1226A) (120.326478,30.31431014)
NorthWest: 和睦小学 Hemuxiaoxue (1230A) (120.1311729, 30.31607706)
SouthWest: 卧龙桥 Wolongqiao (1227A) (120.1384697,30.24927094)
SouthEast: 滨江 Binjiang (1223A) (120.2181926,30.21450741)



The axioms used in these codes are copied (hard codes) from the reasoning program output.
Ontology modeling and reasoning is implemented by Jene (Java) in another project: predictive\_reasoning/smog\_ontology.
