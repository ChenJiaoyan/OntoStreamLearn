package sample.smog.zju.edu.cn;

import java.io.FileWriter;
import java.io.IOException;
import java.net.UnknownHostException;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.HashMap;

import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;
import com.mongodb.MongoException;
import com.mongodb.util.JSON;

import config.smog.zju.edu.cn.DataConfig;
import config.smog.zju.edu.cn.OWLConfig;

public class Sample {
	private Mongo conn = null;
	private DB air_db = null;
	private DBCollection air_col = null;
	private DB mete_db = null;
	private DBCollection mete_col = null;

	private ArrayList<String> valid_snapshots = null;

	public Sample() {
		try {
			conn = new Mongo(DataConfig.mongoHost);
			air_db = conn.getDB(DataConfig.air_db);
			air_col = air_db.getCollection(DataConfig.air_station);
			mete_db = conn.getDB(DataConfig.mete_db);
			mete_col = mete_db.getCollection(DataConfig.mete_col);
		} catch (UnknownHostException e) {
			System.out.println("Failed to connect to destination mongodb");
			e.printStackTrace();
		} catch (MongoException e) {
			System.out.println("Failed to connect to destination mongodb");
			e.printStackTrace();
		}
		valid_snapshots = new ArrayList<String>();
	}

	private void storeResult(HashMap<String, String> results, String file_name)
			throws IOException {
		FileWriter writer = new FileWriter(DataConfig.samples_dir + file_name);
		Object[] key = results.keySet().toArray();
		Arrays.sort(key);
		for (int i = 0; i < key.length; i++) {
			writer.write(key[i] + "," + results.get(key[i]) + "\n");
		}
		writer.close();
		System.out.println("#: " + key.length);
	}

	private void storeResult2(HashMap<String, String> results, String file_name)
			throws IOException {
		FileWriter writer = new FileWriter(DataConfig.samples_dir + file_name);
		Object[] key = results.keySet().toArray();
		Arrays.sort(key);
		for (int i = 0; i < key.length; i++) {
			writer.write(key[i] + "\n");
		}
		writer.close();
		System.out.println("#: " + key.length);
	}

	public void extractLabelsAndGetValidSnapshots() {
		java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat(
				"yyyy-MM-dd HH");
		Calendar cal1 = Calendar.getInstance();
		Calendar cal2 = Calendar.getInstance();
		try {
			cal1.setTime(sdf.parse(DataConfig.start_snapshot));
			cal2.setTime(sdf.parse(DataConfig.end_snapshot));
		} catch (ParseException e) {
			System.err.println("Error in parse start/end time");
			e.printStackTrace();
		}

		HashMap<String, String> results = new HashMap<String, String>();
		while (cal2.getTimeInMillis() >= cal1.getTimeInMillis()) {
			String snapshot = sdf.format(cal1.getTime());
			System.out.println("-------" + snapshot);

			Calendar cal = Calendar.getInstance();
			try {
				cal.setTime(sdf.parse(snapshot));
			} catch (ParseException e) {
				System.err.println("Error in parse start/end time");
				e.printStackTrace();
			}
			cal.add(Calendar.HOUR_OF_DAY, DataConfig.gap);
			String label_snapshot = sdf.format(cal.getTime());

			String time = label_snapshot.replace(" ", "T") + ":00:00Z";
			String json = "{'$or':[{'station_name':'" + OWLConfig.station
					+ "'},{'position_name':'" + OWLConfig.station
					+ "'}],'area':'" + OWLConfig.city + "','time_point':'"
					+ time + "'}";
			DBObject query = (DBObject) JSON.parse(json);
			DBObject obj = air_col.findOne(query);
			if (obj != null && obj.get("aqi") != null
					&& (Integer) obj.get("aqi") > 0) {
				Integer aqi = (Integer) obj.get("aqi");
				String label = null;
				if (aqi <= 50) {
					label = "0";
				} else if (aqi <= 100) {
					label = "1";
				} else if (aqi <= 150) {
					label = "2";
				} else if (aqi <= 200) {
					label = "3";
				} else if (aqi <= 300) {
					label = "4";
				} else {
					label = "5";
				}
				results.put(snapshot, label);
				this.valid_snapshots.add(snapshot);
			}
			cal1.add(Calendar.HOUR_OF_DAY, 1);
		}
		try {
			storeResult(results, "labels_" + DataConfig.exp_id + ".txt");
		} catch (IOException e) {
			System.err.println("Failed to write results to the file");
			e.printStackTrace();
		}
	}

	public void extractTargets() {
		java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat(
				"yyyy-MM-dd HH");
		Calendar cal1 = Calendar.getInstance();
		Calendar cal2 = Calendar.getInstance();
		try {
			cal1.setTime(sdf.parse(DataConfig.cut_snapshot));
			cal2.setTime(sdf.parse(DataConfig.end_snapshot));
		} catch (ParseException e) {
			System.err.println("Error in parse start/end time");
			e.printStackTrace();
		}

		HashMap<String, String> results = new HashMap<String, String>();
		while (cal2.getTimeInMillis() >= cal1.getTimeInMillis()) {
			String snapshot = sdf.format(cal1.getTime());
			if (this.valid_snapshots.contains(snapshot)) {
				results.put(snapshot, "");
			}
			cal1.add(Calendar.HOUR_OF_DAY, 1);
		}
		try {
			storeResult2(results, "targets.txt");
		} catch (IOException e) {
			System.err.println("Failed to write results to the file");
			e.printStackTrace();
		}
	}

	public void extractFeatures() {
		java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat(
				"yyyy-MM-dd HH");
		Calendar cal1 = Calendar.getInstance();
		Calendar cal2 = Calendar.getInstance();
		try {
			cal1.setTime(sdf.parse(DataConfig.start_snapshot));
			cal2.setTime(sdf.parse(DataConfig.end_snapshot));
		} catch (ParseException e) {
			System.err.println("Error in parse start/end time");
			e.printStackTrace();
		}

		HashMap<String, String> results = new HashMap<String, String>();
		while (cal2.getTimeInMillis() >= cal1.getTimeInMillis()) {
			String snapshot = sdf.format(cal1.getTime());
			System.out.println("----" + snapshot);
			if (this.valid_snapshots.contains(snapshot)) {
				String aqi_f = new Feature(snapshot, air_col)
						.getAttributes_AQI();
				String air_f = new Feature(snapshot, air_col)
						.getAttributes_Air();
				String mete_f = new Feature(snapshot, mete_col)
						.getAttributes_Mete();
				results.put(snapshot, aqi_f + "," + air_f + "," + mete_f);
			}
			cal1.add(Calendar.HOUR_OF_DAY, 1);
		}
		try {
			storeResult(results, "features.txt");
		} catch (IOException e) {
			System.err.println("Failed to write results to the file");
			e.printStackTrace();
		}

	}

	public void closeMongo() {
		conn.close();
	}
}
