package reason.smog.zju.edu.cn;

import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Set;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.Mongo;
import com.mongodb.MongoException;

import config.smog.zju.edu.cn.DataConfig;

/*
 * This file calculate the correlation between any two snapshots based on the entailments output by Job0
 * The results are stored in DataConfig.reasoning_corr
 */
public class Job1_correlation {
	private static Mongo conn = null;
	private static DB myDB = null;
	private static DBCollection inCollection = null;
	private static DBCollection outCollection = null;
	private static ArrayList<String> entailments = null;
	private static ArrayList<String> snapshots = null;

	static {
		try {
			conn = new Mongo(DataConfig.mongoHost);
			myDB = conn.getDB(DataConfig.reasoning_db);
			inCollection = myDB.getCollection(DataConfig.reasoning_entailments);
			outCollection = myDB.getCollection(DataConfig.reasoning_corr);
		} catch (UnknownHostException e) {
			System.out.println("Failed to connect to destination mongodb");
			e.printStackTrace();
		} catch (MongoException e) {
			System.out.println("Failed to connect to destination mongodb");
			e.printStackTrace();
		}
		entailments = new ArrayList<String>();
		snapshots = new ArrayList<String>();
	}

	public static void main(String args[]) {
		readEntailments();
		for (int i = 0; i < entailments.size(); i++) {
			System.out.println(snapshots.get(i));
			ArrayList<DBObject> result = new ArrayList<DBObject>();
			for (int j = i + 1; j < entailments.size(); j++) {

				String snapshot_i = snapshots.get(i);
				String snapshot_j = snapshots.get(j);
				if (snapshot_j.compareTo(DataConfig.cut_snapshot) < 0
						|| snapshot_j.compareTo(DataConfig.end_snapshot) > 0) {
					continue;
				}

				// use cal_corr4 if you want to calculate corrlation with all
				// the combinations of the concepts
				// namely, it is especially designed for Exp4: removing and
				// adding concepts are tested.

				HashMap<String, Float> corrs = cal_corr3(entailments.get(i),
						entailments.get(j));
				DBObject saveobj = new BasicDBObject();
				saveobj.put("snapshot_i", snapshot_i);
				saveobj.put("snapshot_j", snapshot_j);
				Set<String> keys = corrs.keySet();
				Iterator<String> it = keys.iterator();
				while (it.hasNext()) {
					String key = it.next();
					saveobj.put(key, corrs.get(key));
				}

				// use cal_corr if you just use all the concepts
				// begin
				// float corr = cal_corr(entailments.get(i),
				// entailments.get(j));
				// DBObject saveobj = new BasicDBObject();
				// saveobj.put("snapshot_i", snapshots.get(i));
				// saveobj.put("snapshot_j", snapshots.get(j));
				// saveobj.put("correlation", corr);
				// end

				result.add(saveobj);
			}
			storeCorr(result);
		}
	}

	private static float cal_corr(String entail_i, String entail_j) {
		entail_i = entail_i.replace(" ", "");
		entail_i = entail_i.substring(0, entail_i.length() - 1);
		entail_j = entail_j.replace(" ", "");
		entail_j = entail_j.substring(0, entail_j.length() - 1);
		String[] e1 = entail_i.split(",");
		String[] e2 = entail_j.split(",");
		// int new_n = 0;
		int inv_n = 0;
		// int obs_n = 0;
		for (int i = 0; i < e1.length; i++) {
			// if (e2[i].equals("1") && e1[i].equals("0")) {
			// new_n += 1;
			// }
			// if (e2[i].equals("0") && e1[i].equals("1")) {
			// obs_n += 1;
			// }
			// if ((e2[i].equals("0") && e1[i].equals("0"))
			// || (e2[i].equals("1") && e1[i].equals("1"))) {
			// inv_n += 1;
			// }
			if (e1[i].equals(e2[i])) {
				inv_n += 1;
			}
		}
		float corr = (float) inv_n / e1.length;
		return corr;
	}

	private static HashMap<String, Float> cal_corr3(String entail_i,
			String entail_j) {
		HashMap<String, Float> corrs = new HashMap<String, Float>();

		String[] tmp_i = entail_i.split("    ");
		String[] tmp_j = entail_j.split("    ");
		corrs.put("0", cal_corr(tmp_i[0] + tmp_i[1], tmp_j[0] + tmp_j[1]));
		corrs.put("1", cal_corr(tmp_i[2], tmp_j[2]));
		corrs.put("2", cal_corr(tmp_i[3], tmp_j[3]));
		corrs.put(
				"01",
				cal_corr(tmp_i[0] + tmp_i[1] + tmp_i[2], tmp_j[0] + tmp_j[1]
						+ tmp_j[2]));
		corrs.put(
				"02",
				cal_corr(tmp_i[0] + tmp_i[1] + tmp_i[3], tmp_j[0] + tmp_j[1]
						+ tmp_j[3]));
		corrs.put("12", cal_corr(tmp_i[2] + tmp_i[3], tmp_j[2] + tmp_j[3]));
		corrs.put(
				"012",
				cal_corr(tmp_i[0] + tmp_i[1] + tmp_i[2] + tmp_i[3], tmp_j[0]
						+ tmp_j[1] + tmp_j[2] + tmp_j[3]));
		return corrs;
	}

	private static HashMap<String, Float> cal_corr4(String entail_i,
			String entail_j) {
		HashMap<String, Float> corrs = new HashMap<String, Float>();

		String[] tmp_i = entail_i.split("    ");
		String[] tmp_j = entail_j.split("    ");

		for (int k = 0; k < 4; k++) {
			String e_i = tmp_i[k];
			String e_j = tmp_j[k];
			corrs.put(k + "", cal_corr(e_i, e_j));
		}

		for (int k1 = 0; k1 < 4; k1++) {
			for (int k2 = k1 + 1; k2 < 4; k2++) {
				String e_i = tmp_i[k1] + tmp_i[k2];
				String e_j = tmp_j[k1] + tmp_j[k2];
				corrs.put(k1 + "" + k2, cal_corr(e_i, e_j));
			}
		}

		for (int k1 = 0; k1 < 4; k1++) {
			for (int k2 = k1 + 1; k2 < 4; k2++) {
				for (int k3 = k2 + 1; k3 < 4; k3++) {
					String e_i = tmp_i[k1] + tmp_i[k2] + tmp_i[k3];
					String e_j = tmp_j[k1] + tmp_j[k2] + tmp_j[k3];
					corrs.put(k1 + "" + k2 + "" + k3, cal_corr(e_i, e_j));
				}
			}
		}

		corrs.put("0123", cal_corr(entail_i, entail_j));

		return corrs;
	}

	private static void readEntailments() {
		DBObject sort_obj = new BasicDBObject();
		sort_obj.put("snapshot", 1);
		DBCursor cur = inCollection.find();
		cur.sort(sort_obj);
		while (cur.hasNext()) {
			DBObject obj = cur.next();
			entailments.add((String) obj.get("result"));
			snapshots.add((String) obj.get("snapshot"));
		}
	}

	private static void storeCorr(ArrayList<DBObject> result) {
		for (int i = 0; i < result.size(); i++) {
			outCollection.save(result.get(i));
		}
	}
}
