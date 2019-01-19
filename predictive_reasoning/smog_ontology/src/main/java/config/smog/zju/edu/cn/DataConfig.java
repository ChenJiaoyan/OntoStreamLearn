package config.smog.zju.edu.cn;

/*
 * This file contains the settings of input, output
 */
public class DataConfig {
	
	
	//The original air quality data and meteorology data
	public static String mongoHost = "10.214.0.95";
	public static String air_db = "Air";
	public static String air_station = "Stations";
	public static String mete_db = "forecastio";
	public static String mete_col = "Beijing";
	public static String stations_file = "station_location.csv";
	
	//intermediate results
	public static String reason_id = "000"; //id for each time your run reasoning steps (Jon0 and Job1)
	public static String exp_id = "1603"; //id for each time you run sampling steps (Job2 and Job3)
	public static String reasoning_db = "Reasoning";
	public static String reasoning_entailments = "Entailments_" + reason_id;
	public static String reasoning_corr = "Correlation_all2_" + reason_id;
	
	//training data: [start_snapshot, cut_snapshot]; testing data: (cut_snapshot, end_snapshot]
	public static String start_snapshot = "2013-06-01 00";
	public static String cut_snapshot = "2014-11-16 00";
	public static String end_snapshot = "2014-12-16 23";
	public static String samples_dir = "/Users/apple/Google Drive/Data/predictive_reasoning/smog_ml/samples2/";
	
	//forecasting time, "6" means forecasting AQI level after 6 hours
	public static int gap = 24;
	
}
