package reason.smog.zju.edu.cn;

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
public class Test {
	public static void main(String args[]) throws ParseException, UnknownHostException {
		java.text.DecimalFormat   df   =new   java.text.DecimalFormat("#.00");  
		System.out.println(df.format(12.4454));
	}

}
