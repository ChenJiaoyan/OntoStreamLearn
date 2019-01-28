package sample.smog.zju.edu.cn;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Set;
import java.util.Iterator;

import config.smog.zju.edu.cn.DataConfig;

/*
 * For each testing snapshot (sample), this file will extract its consistent training snapshots (samples) according
 * to each snapshot's consistent coefficient which is calculated in Job1.
 * The results will be stored in files like consistent_train_exp_id.txt
 * each line in the file contains a snapshot for testing, and its corresponding snapshots for training, separated by 
 * ":" and ";".
 */
public class Job3_ConsistentSamples {

	public static void main(String args[]) {
		ArrayList<String> target_snapshots = null;
		try {
			target_snapshots = getTargetSnapshots();
		} catch (IOException e) {
			System.out.println("Failed to read target snapshots");
			e.printStackTrace();
		}

		
		for (int i = 0; i < target_snapshots.size(); i++) {
			String target_snapshot = target_snapshots.get(i);
			
			File dir = new File(DataConfig.samples_dir + "weights_" +DataConfig.exp_id+"/"+ target_snapshot);
			if(dir.exists()){
				continue;
			}
			
			System.out.println(target_snapshot);
			Snapshot s = new Snapshot(target_snapshot,
					DataConfig.start_snapshot, DataConfig.end_snapshot);
			HashMap<String, String> consistentSnapshots = s
					.getConsistentSnapshots();
			s.closeMongo();

			Set<String> snapshots = consistentSnapshots.keySet();
			Iterator<String> j = snapshots.iterator();
			String result = "";
			while (j.hasNext()) {
				String snapshot = j.next();
				String corr = consistentSnapshots.get(snapshot);
				result += snapshot + ":" + corr + ";";
			}
			HashMap<String, String> results = new HashMap<String, String>();
			results.put(target_snapshot, result);
			try {
				storeResult(results, "weights_" +DataConfig.exp_id+"/"+ target_snapshot);
			} catch (IOException e) {
				System.out.println("Failed to write samples to files.");
				e.printStackTrace();
			}
		}
		

	}

	private static void storeResult(HashMap<String, String> results,
			String file_name) throws IOException {
		FileWriter writer = new FileWriter(DataConfig.samples_dir + file_name);
		Object[] key = results.keySet().toArray();
		Arrays.sort(key);
		for (int i = 0; i < key.length; i++) {
			writer.write(key[i] + ": " + results.get(key[i]) + "\n");
		}
		writer.close();
	}

	private static ArrayList<String> getTargetSnapshots() throws IOException {
		String test_file_name = "targets_" + DataConfig.exp_id + ".txt";
		ArrayList<String> target_snapshots = new ArrayList<String>();
		BufferedReader in = new BufferedReader(new FileReader(
				DataConfig.samples_dir + test_file_name));
		String line = in.readLine();
		while (line != null) {
			target_snapshots.add(line.substring(0, 13));
			line = in.readLine();
		}
		in.close();
		return target_snapshots;
	}

}
