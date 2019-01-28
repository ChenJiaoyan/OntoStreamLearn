package reason.smog.zju.edu.cn;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Calendar;

import com.hp.hpl.jena.ontology.Individual;
import com.hp.hpl.jena.ontology.OntClass;
import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;
import com.mongodb.MongoException;
import com.mongodb.util.JSON;

import config.smog.zju.edu.cn.DataConfig;
import config.smog.zju.edu.cn.OWLConfig;

public class DataImporter {

	private OntModel m = null;
	private Calendar cal = null;
	private String station_file = null;
	private Mongo conn = null;
	private DB air_DB = null;
	private DBCollection air_col = null;
	private DB mete_DB = null;
	private DBCollection mete_col = null;

	public DataImporter(Calendar cal) {
		this.m = ModelFactory.createOntologyModel();
		this.cal = cal;
		this.station_file = DataConfig.stations_file;
		try {
			conn = new Mongo(DataConfig.mongoHost);
			air_DB = conn.getDB(DataConfig.air_db);
			air_col = air_DB.getCollection(DataConfig.air_station);
			mete_DB = conn.getDB(DataConfig.mete_db);
			mete_col = mete_DB.getCollection(DataConfig.mete_col);
		} catch (UnknownHostException e) {
			System.out.println("Failed to connect to destination mongodb");
			e.printStackTrace();
		} catch (MongoException e) {
			System.out.println("Failed to connect to destination mongodb");
			e.printStackTrace();
		}
	}

	public OntModel run() {
		importOWL();
		try {
			addStation();
		} catch (IOException e) {
			System.err.println("IO errors in import stations.");
			e.printStackTrace();
		}
		try {
			addSnapshot();
		} catch (UnknownHostException e) {
			System.err.println("Failed to connect to mongodb");
			e.printStackTrace();
		}
		return m;
	}

	public void closeMongo() {
		conn.close();
	}

	private void importOWL() {
		m.getDocumentManager().addAltEntry(OWLConfig.NP_Smog,
				OWLConfig.Ontology_File);
		m.read(OWLConfig.NP_Smog, "TURTLE");
	}

	private void addSnapshot() throws UnknownHostException {
		OntClass snapshotCla = m.getOntClass(OWLConfig.NP_Smog + "Snapshot");
		Individual snapshotInd = m.createIndividual(OWLConfig.NP_Smog
				+ "snapshot", snapshotCla);
		String time_str = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
				.format(cal.getTime());
		time_str = time_str.replace(" ", "T");
		Individual station_ind = m.getIndividual(OWLConfig.NP_Smog
				+ OWLConfig.station);
		m.add(snapshotInd,
				m.getProperty(OWLConfig.NP_Smog + "hasObservatedStation"),
				station_ind);
		m.add(snapshotInd,
				m.getProperty(OWLConfig.NP_Smog + "hasObservedTime"),
				m.createTypedLiteral(time_str, OWLConfig.NP_xsd + "dateTime"));
		m.add(snapshotInd, m.getProperty(OWLConfig.NP_Smog + "hasHourOfDay"),
				addAndGetHourOfDayInd());
		m.add(snapshotInd, m.getProperty(OWLConfig.NP_Smog + "hasDayOfWeek"),
				addAndGetWeekOfDayInd());
		m.add(snapshotInd, m.getProperty(OWLConfig.NP_Smog + "hasAir"),
				addAndGetAirInd());
		m.add(snapshotInd, m.getProperty(OWLConfig.NP_Smog + "hasMeteorology"),
				addAndGetMeteorologyInd());
	}

	private Individual addAndGetMeteorologyInd() {
		String[] mete_values = readMeteorology();
		String[] mete_atts = { "hasCloudCoverValue", "hasTemperatureValue",
				"hasVisibilityValue", "hasHumidityValue" };
		String[] mete_types = { "float", "float", "float", "float" };
		OntClass meteClass = m.getOntClass(OWLConfig.NP_Smog + "Meteorology");
		Individual meteInd = m.createIndividual(OWLConfig.NP_Smog
				+ "meteorology", meteClass);
		if (mete_values != null) {
			for (int i = 0; i < mete_values.length; i++) {
				if (mete_values[i] == null || mete_values[i].equals("null")) {
					m.add(meteInd,
							m.getProperty(OWLConfig.NP_Smog, mete_atts[i]),
							m.createTypedLiteral("-1", OWLConfig.NP_xsd
									+ mete_types[i]));
				} else {
					m.add(meteInd, m.getProperty(OWLConfig.NP_Smog,
							mete_atts[i]), m.createTypedLiteral(mete_values[i],
							OWLConfig.NP_xsd + mete_types[i]));
				}
			}
		}
		m.add(meteInd, m.getProperty(OWLConfig.NP_Smog + "hasWind"),
				addAndGetWindInd());
		m.add(meteInd, m.getProperty(OWLConfig.NP_Smog + "hasWeatherType"),
				addAndGetWeatherTypeInd());
		return meteInd;
	}

	private Individual addAndGetWindInd() {
		OntClass windClass = m.getOntClass(OWLConfig.NP_Smog + "Wind");
		Individual windInd = m.createIndividual(OWLConfig.NP_Smog + "wind",
				windClass);
		String[] wind_values = readWind();
		String[] wind_atts = { "hasWindDirectionValue", "hasWindSpeedValue" };
		String[] wind_types = { "int", "float" };

		if (wind_values != null) {
			for (int i = 0; i < wind_values.length; i++) {
				if (wind_values[i] == null || wind_values[i].equals("null")) {
					m.add(windInd,
							m.getProperty(OWLConfig.NP_Smog, wind_atts[i]),
							m.createTypedLiteral("-1", OWLConfig.NP_xsd
									+ wind_types[i]));
				} else {
					m.add(windInd, m.getProperty(OWLConfig.NP_Smog,
							wind_atts[i]), m.createTypedLiteral(wind_values[i],
							OWLConfig.NP_xsd + wind_types[i]));
				}
			}
		}

		return windInd;
	}

	private Individual addAndGetWeatherTypeInd() {
		OntClass weatherTypeClass = m.getOntClass(OWLConfig.NP_Smog
				+ "WeatherType");
		Individual weatherTypeInd = m.createIndividual(OWLConfig.NP_Smog
				+ "weatherType", weatherTypeClass);
		String[] weatherType_values = readWeatherType();
		if (weatherType_values != null) {
			for (int i = 0; i < weatherType_values.length; i++) {
				m.add(weatherTypeInd, m.getProperty(OWLConfig.NP_Smog,
						"hasWeatherDescriptionValue"), m.createTypedLiteral(
						weatherType_values[i], OWLConfig.NP_xsd + "string"));
			}
		}
		return weatherTypeInd;
	}

	private Individual addAndGetAirInd() {
		String[] air_values = readAir();
		String[] air_atts = { "hasAQIValue", "hasCOValue", "hasNO2Value",
				"hasO3Value", "hasPM10Value", "hasPM25Value", "hasSO2Value",
				"hasPrimaryPollutantValue" };
		String[] air_types = { "int", "float", "int", "int", "int", "int",
				"int", "string" };

		OntClass airCla = m.getOntClass(OWLConfig.NP_Smog + "Air");
		Individual airInd = m.createIndividual(OWLConfig.NP_Smog + "air",
				airCla);
		if (air_values != null) {
			for (int i = 0; i < air_values.length; i++) {
				if (air_values[i] == null || air_values[i].equals("0")
						|| air_values[i].equals("null")) {
					m.add(airInd,
							m.getProperty(OWLConfig.NP_Smog, air_atts[i]),
							m.createTypedLiteral("-1", OWLConfig.NP_xsd
									+ air_types[i]));
				} else {
					m.add(airInd,
							m.getProperty(OWLConfig.NP_Smog, air_atts[i]), m
									.createTypedLiteral(air_values[i],
											OWLConfig.NP_xsd + air_types[i]));
				}
			}
		} else {
			m.add(airInd, m.getProperty(OWLConfig.NP_Smog, "hasAQIValue"),
					m.createTypedLiteral("-1", OWLConfig.NP_xsd + "int"));
		}

		return airInd;
	}

	private Individual addAndGetHourOfDayInd() {
		OntClass hourOfDayCla = m.getOntClass(OWLConfig.NP_Smog + "HourOfDay");
		Individual hourInd = m.createIndividual(OWLConfig.NP_Smog + "hour",
				hourOfDayCla);
		m.add(hourInd, m.getProperty(OWLConfig.NP_Smog, "hasHourValue"), m
				.createTypedLiteral(cal.get(Calendar.HOUR_OF_DAY),
						OWLConfig.NP_xsd + "int"));
		return m.getIndividual(OWLConfig.NP_Smog + "hour");
	}

	private Individual addAndGetWeekOfDayInd() {
		OntClass dayOfWeekCla = m.getOntClass(OWLConfig.NP_Smog + "DayOfWeek");
		Individual dayInd = m.createIndividual(OWLConfig.NP_Smog + "day",
				dayOfWeekCla);
		m.add(dayInd, m.getProperty(OWLConfig.NP_Smog, "hasDayValue"), m
				.createTypedLiteral(cal.get(Calendar.DAY_OF_WEEK),
						OWLConfig.NP_xsd + "int"));

		return m.getIndividual(OWLConfig.NP_Smog + "day");
	}

	private void addStation() throws IOException {
		OntClass stationCla = m.getOntClass(OWLConfig.NP_Smog + "Station");
		ArrayList<String[]> stations = readStation();
		for (int i = 0; i < stations.size(); i++) {
			Individual stationInd = m.createIndividual(OWLConfig.NP_Smog
					+ stations.get(i)[1], stationCla);
			m.add(stationInd,
					m.getProperty(OWLConfig.NP_Smog, "hasNameValue"),
					m.createTypedLiteral(stations.get(i)[1], OWLConfig.NP_xsd
							+ "string"));
			m.add(stationInd, m.getProperty(OWLConfig.NP_Smog, "hasLonValue"),
					m.createTypedLiteral(Float.parseFloat(stations.get(i)[2]),
							OWLConfig.NP_xsd + "float"));
			m.add(stationInd, m.getProperty(OWLConfig.NP_Smog, "hasLatValue"),
					m.createTypedLiteral(Float.parseFloat(stations.get(i)[3]),
							OWLConfig.NP_xsd + "float"));
			m.add(stationInd,
					m.getProperty(OWLConfig.NP_Smog, "hasCityValue"),
					m.createTypedLiteral(stations.get(i)[0], OWLConfig.NP_xsd
							+ "string"));
		}
	}

	private String[] readWeatherType() {
		String time_str = new java.text.SimpleDateFormat("yyyy-MM-dd")
				.format(cal.getTime());
		String json = "{'position':'" + OWLConfig.station_en + "','date':'"
				+ time_str + "'}";
		DBObject query = (DBObject) JSON.parse(json);
		DBObject obj = mete_col.findOne(query);
		ArrayList<DBObject> hours = (ArrayList<DBObject>) ((DBObject) obj
				.get("hourly")).get("data");
		DBObject obj2 = hours.get(cal.get(Calendar.HOUR_OF_DAY));
		String summary = "null";
		if (obj2.get("summary") != null) {
			summary = obj2.get("summary").toString();
			return summary.split(" and ");
		} else {
			String[] weatherType_values = { summary };
			return weatherType_values;
		}
	}

	private String[] readMeteorology() {
		String time_str = new java.text.SimpleDateFormat("yyyy-MM-dd")
				.format(cal.getTime());
		String json = "{'position':'" + OWLConfig.station_en + "','date':'"
				+ time_str + "'}";
		DBObject query = (DBObject) JSON.parse(json);
		DBObject obj = mete_col.findOne(query);
		ArrayList<DBObject> hours = (ArrayList<DBObject>) ((DBObject) obj
				.get("hourly")).get("data");
		DBObject obj2 = hours.get(cal.get(Calendar.HOUR_OF_DAY));
		String cloudCover = "null";
		String temperature = "null";
		String visibility = "null";
		String humidity = "null";
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
		String[] mete_values = { cloudCover, temperature, visibility, humidity };
		return mete_values;
	}

	private String[] readWind() {
		String time_str = new java.text.SimpleDateFormat("yyyy-MM-dd")
				.format(cal.getTime());
		String json = "{'position':'" + OWLConfig.station_en + "','date':'"
				+ time_str + "'}";
		DBObject query = (DBObject) JSON.parse(json);
		DBObject obj = mete_col.findOne(query);
		ArrayList<DBObject> hours = (ArrayList<DBObject>) ((DBObject) obj
				.get("hourly")).get("data");
		DBObject obj2 = hours.get(cal.get(Calendar.HOUR_OF_DAY));
		String windSpeed = "null";
		String windBearing = "null";
		if (obj2.get("windSpeed") != null) {
			windSpeed = obj2.get("windSpeed").toString();
		}
		if (obj2.get("windBearing") != null) {
			windBearing = obj2.get("windBearing").toString();
		}
		String[] wind_value = { windBearing, windSpeed };
		return wind_value;
	}

	private String[] readAir() {
		String time_str = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
				.format(cal.getTime());
		time_str = time_str.replace(" ", "T");
		time_str = time_str + "Z";
		String json = "{'area':'" + OWLConfig.city + "','position_name':'"
				+ OWLConfig.station + "','time_point':'" + time_str + "'}";
		DBObject query = (DBObject) JSON.parse(json);
		DBObject obj = air_col.findOne(query);
		if (obj != null) {
			String[] air_values = { obj.get("aqi").toString(),
					obj.get("co").toString(), obj.get("no2").toString(),
					obj.get("o3").toString(), obj.get("pm10").toString(),
					obj.get("pm2_5").toString(), obj.get("so2").toString(),
					(String) obj.get("primary_pollutant") };
			return air_values;
		} else {
			json = "{'area':'" + OWLConfig.city + "','station_name':'"
					+ OWLConfig.station + "','time_point':'" + time_str + "'}";
			query = (DBObject) JSON.parse(json);
			obj = air_col.findOne(query);
			if (obj != null) {
				String[] air_values = { obj.get("aqi").toString(),
						obj.get("co").toString(), obj.get("no2").toString(),
						obj.get("o3").toString(), obj.get("pm10").toString(),
						obj.get("pm2_5").toString(), obj.get("so2").toString(),
						(String) obj.get("primary_pollutant") };
				return air_values;
			} else {
				return null;
			}
		}
	}

	private ArrayList<String[]> readStation() throws IOException {
		BufferedReader reader = new BufferedReader(new InputStreamReader(
				new FileInputStream(station_file), "GBK"));
		reader.readLine();
		String line = null;
		ArrayList<String[]> stations = new ArrayList<String[]>();
		while ((line = reader.readLine()) != null) {
			String item[] = line.split(",");
			if (item[0].equals(OWLConfig.city)) {
				stations.add(item);
			}
		}
		reader.close();
		return stations;
	}

}
