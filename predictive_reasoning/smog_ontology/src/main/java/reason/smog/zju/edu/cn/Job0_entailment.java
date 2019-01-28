package reason.smog.zju.edu.cn;

import java.net.UnknownHostException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;
import com.mongodb.MongoException;

import config.smog.zju.edu.cn.DataConfig;
/*
 * For each snapshot (hour), it will import the data and map them to assertions, and then infer the underlying assertions.
 * The results are stored in DataConfig.reasoning_entailments. One snapshot, one record. 
 * Each record contains a sequence of 0/1. 1 represents "one instance belongs a concept", while 0 represents "NOT".
 * Please see the function "SmogReasoner().reasoning()" for details. You need to modify this function for your concepts. 
 */
public class Job0_entailment {

	private static Mongo conn = null;
	private static DB myDB = null;
	private static DBCollection myCollection = null;

	static {
		try {
			conn = new Mongo(DataConfig.mongoHost);
			myDB = conn.getDB(DataConfig.reasoning_db);
			myCollection = myDB.getCollection(DataConfig.reasoning_entailments);
		} catch (UnknownHostException e) {
			System.out.println("Failed to connect to destination mongodb");
			e.printStackTrace();
		} catch (MongoException e) {
			System.out.println("Failed to connect to destination mongodb");
			e.printStackTrace();
		}
	}

	public static void main(String args[]) {

		java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat(
				"yyyy-MM-dd HH");
		Calendar cal = Calendar.getInstance();
		Calendar end_cal = Calendar.getInstance();
		try {
			cal.setTime(sdf.parse(DataConfig.start_snapshot));
			end_cal.setTime(sdf.parse(DataConfig.end_snapshot));
		} catch (ParseException e) {
			System.err.println("Error in parse start/end time");
			e.printStackTrace();
		}

		while (end_cal.getTimeInMillis() >= cal.getTimeInMillis()) {
			String result = new SmogReasoner(cal).reasoning();
			storeResult(cal, result);
			cal.add(Calendar.HOUR_OF_DAY, 1);
		}
		conn.close();

	}

	public static void storeResult(Calendar cal, String result) {
		SimpleDateFormat format = new SimpleDateFormat(
				"yyyy-MM-dd HH");
		DBObject updateCondition = new BasicDBObject();
		updateCondition.put("snapshot", format.format(cal.getTime()));
		DBObject updatedValue = new BasicDBObject();
		updatedValue.put("result", result);
		DBObject updateSetValue = new BasicDBObject("$set", updatedValue);
		myCollection.update(updateCondition, updateSetValue, true, true);
	}

}
