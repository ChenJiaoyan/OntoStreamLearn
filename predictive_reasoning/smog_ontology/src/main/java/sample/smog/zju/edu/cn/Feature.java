package sample.smog.zju.edu.cn;

import java.text.ParseException;
import java.util.ArrayList;
import java.util.Calendar;

import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.util.JSON;

import config.smog.zju.edu.cn.OWLConfig;

public class Feature {
	private String snapshot = null;
	private DBCollection col = null;

	public Feature(String snapshotC, DBCollection collection) {
		this.snapshot = snapshotC;
		this.col = collection;
	}

	public String getAttributes_Air() {
		java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat(
				"yyyy-MM-dd HH");

		Calendar cal = Calendar.getInstance();
		try {
			cal.setTime(sdf.parse(this.snapshot));
		} catch (ParseException e) {
			System.err.println("Error in parse start/end time");
			e.printStackTrace();
		}
		
		String time_str = sdf.format(cal.getTime());
		time_str = time_str.replace(" ", "T") + ":00:00Z";
		String json = "{'$or':[{'station_name':'" + OWLConfig.station
				+ "'},{'position_name':'" + OWLConfig.station + "'}],'area':'"
				+ OWLConfig.city + "','time_point':'" + time_str + "'}";
		DBObject query = (DBObject) JSON.parse(json);
		DBObject obj = col.findOne(query);
		
		if(obj!=null){
			String result = "";
			if(obj.get("co") != null){
				result = result + obj.get("co").toString() + ",";
			}
			if(obj.get("no2") != null){
				result = result + (Integer)obj.get("no2") + ",";
			}
			if(obj.get("o3") != null){
				result = result + (Integer)obj.get("o3") + ",";
			}
			if(obj.get("pm10") != null){
				result = result + (Integer)obj.get("pm10") + ",";
			}
			if(obj.get("pm2_5") != null){
				result = result + (Integer)obj.get("pm2_5") + ",";
			}
			if(obj.get("so2") != null){
				result = result + (Integer)obj.get("so2") + ",";
			}
			return result.substring(0, result.length()-1);
		}else{
			return "0,0,0,0,0,0";
		}
		
	}

	public String getAttributes_AQI() {
		java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat(
				"yyyy-MM-dd HH");
		Calendar cal = Calendar.getInstance();
		try {
			cal.setTime(sdf.parse(this.snapshot));
		} catch (ParseException e) {
			System.err.println("Error in parse start/end time");
			e.printStackTrace();
		}
		
		String result = "";
		for (int i = 0; i < 6; i++) {
			String time_str = sdf.format(cal.getTime());
			time_str = time_str.replace(" ", "T") + ":00:00Z";
			String json = "{'$or':[{'station_name':'" + OWLConfig.station
					+ "'},{'position_name':'" + OWLConfig.station
					+ "'}],'area':'" + OWLConfig.city + "','time_point':'"
					+ time_str + "'}";
			DBObject query = (DBObject) JSON.parse(json);
			DBObject obj = col.findOne(query);
			if (obj != null && obj.get("aqi") != null
					&& (Integer) obj.get("aqi") != 0) {
				result = result + obj.get("aqi").toString() + ",";
			} else {
				result = result + "0,";
			}
			cal.add(Calendar.HOUR_OF_DAY, -1);
		}
		return result.substring(0, result.length()-1);
	}

	public String getAttributes_Mete() {
		java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat(
				"yyyy-MM-dd HH");
		Calendar cal = Calendar.getInstance();
		try {
			cal.setTime(sdf.parse(this.snapshot));
		} catch (ParseException e) {
			System.err.println("Error in parse start/end time");
			e.printStackTrace();
		}
		
		
		sdf = new java.text.SimpleDateFormat(
				"yyyy-MM-dd");
		String date = sdf.format(cal.getTime());
		int hour = cal.get(Calendar.HOUR_OF_DAY);
		String json = "{'position':'" + OWLConfig.station_en + "','date':'"
				+ date + "'}";
		DBObject query = (DBObject) JSON.parse(json);
		DBObject obj = col.findOne(query);
		if(obj==null || obj.get("hourly") == null){
			System.out.println(cal.getTime());
		}
		
		ArrayList<DBObject> hours = (ArrayList<DBObject>) ((DBObject) obj
				.get("hourly")).get("data");
		DBObject obj2 = hours.get(hour);

		String cloudCover = "-1";
		String temperature = "-1";
		String visibility = "-1";
		String humidity = "-1";
		String windSpeed = "-1";
		if (obj2.get("cloudCover") != null) {
			cloudCover = obj2.get("cloudCover").toString();
		}
		if (obj2.get("temperature") != null) {
			temperature = obj2.get("temperature").toString();
		}
		if (obj2.get("visibility") != null) {
			visibility = obj2.get("visibility").toString();
		}
		if (obj2.get("humidity") != null) {
			humidity = obj2.get("humidity").toString();
		}
		if (obj2.get("windSpeed") != null) {
			windSpeed = obj2.get("windSpeed").toString();
		}

		return cloudCover + "," + temperature + "," + visibility + ","
				+ humidity + "," + windSpeed;

	}
}
