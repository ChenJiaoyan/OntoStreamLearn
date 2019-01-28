package insight.smog.zju.edu.cn;

import java.net.UnknownHostException;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Set;

import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

import config.smog.zju.edu.cn.DataConfig;


/**
 * Hello world!
 *
 */
public class WeatherSummary {
	public static void main(String args[]) throws ParseException, UnknownHostException {
		HashMap<String, Integer> counts = new HashMap<String, Integer>();
		Mongo conn = new Mongo(DataConfig.mongoHost);
		DB db = conn.getDB(DataConfig.mete_db);
		DBCollection col = db.getCollection(DataConfig.mete_col);
		DBCursor cur = col.find();
		while(cur.hasNext()){
			DBObject obj = cur.next();
			ArrayList<DBObject> hours = (ArrayList<DBObject>) ((DBObject) obj
					.get("hourly")).get("data");
			for(int i=0;i<hours.size();i++){
				DBObject hour = hours.get(i);
				if(hour.get("summary")!=null){
					String summary = hour.get("summary").toString();
					if(counts.containsKey(summary)){
						counts.put(summary, counts.get(summary)+1);
					}else{
						counts.put(summary, 1);
					}
				}
			}
		}
		int n = 0;
		Set<String> summaries = counts.keySet();
		Iterator<String> it = summaries.iterator();
		while(it.hasNext()){
			String key = it.next();
			n = n + counts.get(key);
			System.out.println(key + ": " + counts.get(key));
		}
		System.out.println(n);
	}

}
