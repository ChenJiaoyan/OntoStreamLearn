package insight.smog.zju.edu.cn;

import java.net.UnknownHostException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Set;

import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

import config.smog.zju.edu.cn.DataConfig;

public class Correlation {
	public static void main(String args[]) throws UnknownHostException{
		HashMap<Float, Integer> counts = new HashMap<Float, Integer>();
		Mongo conn = new Mongo(DataConfig.mongoHost);
		DB db = conn.getDB(DataConfig.reasoning_db);
		DBCollection col = db.getCollection(DataConfig.reasoning_corr);
		DBCursor cur = col.find();
		while(cur.hasNext()){
			DBObject obj = cur.next();
			Float corr = Float.parseFloat(obj.get("correlation").toString());
			if(counts.containsKey(corr)){
				counts.put(corr, counts.get(corr)+1);
			}else{
				counts.put(corr, 1);
			}
		}
		int n = 0;
		Set<Float> corrs = counts.keySet();
		Iterator<Float> it = corrs.iterator();
		while(it.hasNext()){
			Float key = it.next();
			n = n + counts.get(key);
			System.out.println(key + ": " + counts.get(key));
		}
		System.out.println(n);
	}
}
