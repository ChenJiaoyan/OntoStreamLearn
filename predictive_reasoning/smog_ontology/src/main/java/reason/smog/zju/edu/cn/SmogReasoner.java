package reason.smog.zju.edu.cn;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.PrintStream;
import java.util.Calendar;
import java.util.Iterator;

import org.mindswap.pellet.jena.PelletReasonerFactory;

import com.hp.hpl.jena.ontology.Individual;
import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.rdf.model.InfModel;
import com.hp.hpl.jena.rdf.model.ModelFactory;
import com.hp.hpl.jena.reasoner.Reasoner;
import com.hp.hpl.jena.reasoner.ReasonerRegistry;
import com.hp.hpl.jena.reasoner.ValidityReport;
import com.hp.hpl.jena.reasoner.ValidityReport.Report;

import config.smog.zju.edu.cn.OWLConfig;

public class SmogReasoner {

	private String result;

	private Calendar cal;

	public SmogReasoner(Calendar calendar) {
		this.cal = calendar;
		this.result = "";
	}

	public String reasoning() {

		System.out.println(cal.getTime());
		DataImporter d = new DataImporter(cal);
		OntModel m = d.run();
		d.closeMongo();
		save(m);
		OntModel im = ModelFactory.createOntologyModel(
				PelletReasonerFactory.THE_SPEC, m);

		//The concepts used for individual classification
		String[] hour_classes_name = { "EveningRushHour", "MorningRushHour",
				"NoneRushHour" };
		individualCheck(im, hour_classes_name, "hour");
		String[] day_classes_name = { "WeekDay", "WeekEnd" };
		individualCheck(im, day_classes_name, "day");
		String[] air_classes_name = { "Emergent", "Good", "Hazardous",
				"Moderate", "Unhealthy", "Veryunhealthy" };
		individualCheck(im, air_classes_name, "air");
		String[] weathertype_classes_name = { "Clear", "Overcast",
				"MostlyCloudy", "Dry", "Humid", "Windy", "Breezy","Foggy","PartlyCloudy" };
		individualCheck(im, weathertype_classes_name, "weatherType");

		return result;
	}

	private void individualCheck(OntModel im, String[] classes_name,
			String ind_name) {
		Individual ind = im.getIndividual(OWLConfig.NP_Smog + ind_name);
		for (int i = 0; i < classes_name.length; i++) {
			if (ind.hasOntClass(OWLConfig.NP_Smog + classes_name[i])) {
				result += "1,";
			} else {
				result += "0,";
			}
		}
		result += "    ";
	}

	public void save(OntModel m) {
		String outputFile = "/Users/apple/Downloads/test.owl";
		try {
			PrintStream ps = new PrintStream(new FileOutputStream(outputFile));
			m.write(ps, "TURTLE");
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}
	}

	public void checkValid(OntModel m) {
		Reasoner reasoner = ReasonerRegistry.getOWLReasoner();
		InfModel inf = ModelFactory.createInfModel(reasoner, m);
		ValidityReport validity = inf.validate();
		if (validity.isValid()) {
			System.out.println("OK");
		} else {
			System.out.println("Conflicts");
			for (Iterator<Report> i = validity.getReports(); i.hasNext();) {
				System.out.println(" - " + i.next());
			}
		}

	}
}
