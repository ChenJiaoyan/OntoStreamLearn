package sample.smog.zju.edu.cn;

import java.net.UnknownHostException;
import java.util.HashMap;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.Mongo;
import com.mongodb.MongoException;

import config.smog.zju.edu.cn.DataConfig;

public class Snapshot {
	private Mongo conn = null;
	private DB myDB = null;
	private DBCollection col = null;
	private String dest_snapshot = null;
	private String start_snapshot = null;

	public Snapshot(String s1, String s2, String s3) {
		try {
			conn = new Mongo(DataConfig.mongoHost);
			myDB = conn.getDB(DataConfig.reasoning_db);
			col = myDB.getCollection(DataConfig.reasoning_corr);
		} catch (UnknownHostException e) {
			System.out.println("Failed to connect to destination mongodb");
			e.printStackTrace();
		} catch (MongoException e) {
			System.out.println("Failed to connect to destination mongodb");
			e.printStackTrace();
		}
		this.dest_snapshot = s1;
		this.start_snapshot = s2;

	}

	public void closeMongo() {
		conn.close();
	}

	public HashMap<String, String> getConsistentSnapshots() {
		HashMap<String, String> snapshots = new HashMap<String, String>();
		DBObject query_obj = new BasicDBObject();
		query_obj.put("snapshot_j", dest_snapshot);
		DBObject sample_interval = new BasicDBObject();
//		sample_interval.put("$gte", start_snapshot);
		sample_interval.put("$lt", dest_snapshot);
		query_obj.put("snapshot_i", sample_interval);
		DBCursor cur = col.find(query_obj);
		while (cur.hasNext()) {
			DBObject obj = cur.next();
			String snapshot_i = obj.get("snapshot_i").toString();
			java.text.DecimalFormat   df   =new   java.text.DecimalFormat("#.00"); 
			String c0 = df.format(((Double)obj.get("0")));
			String c1 = df.format(((Double)obj.get("1")));
			String c2 = df.format(((Double)obj.get("2")));
			String c01 = df.format(((Double)obj.get("01")));
			String c02 = df.format(((Double)obj.get("02")));
			String c12 = df.format(((Double)obj.get("12")));
			String c012 = df.format(((Double)obj.get("012")));
			
			String corr = c0 + "," + c1 + "," + c2 + ","+c01 + "," + c02 + "," + c12 + "," + c012;
			snapshots.put(snapshot_i, corr);
		}
		return snapshots;
	}

}
