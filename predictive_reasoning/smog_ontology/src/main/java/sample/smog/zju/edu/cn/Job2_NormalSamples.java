package sample.smog.zju.edu.cn;

//test

public class Job2_NormalSamples {
	
/*
 * extract features and all the samples from original data.
 * It is actually the same as extracting feature vector from assertions.
 * Training data is stored in files like train_air_exp_id.txt, train_mete_exp_id.txt
 * Testing data is stored in files like test_air_exp_id.txt, test_mete_id.txt
 */
	public static void main(String args[]) {
		Sample s = new Sample();
		System.out.println("extract labels and get valid snapshots");
		s.extractLabelsAndGetValidSnapshots();
		
		System.out.println("extract taget snapshots");
//		s.extractTargets();
		
		System.out.println("extract features");
//		s.extractFeatures();
		
		s.closeMongo();
	}	

}
