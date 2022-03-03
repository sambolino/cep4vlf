import com.espertech.esper.common.client.EPCompiled;
import com.espertech.esper.common.client.configuration.Configuration;
import com.espertech.esper.compiler.client.CompilerArguments;
import com.espertech.esper.compiler.client.EPCompileException;
import com.espertech.esper.compiler.client.EPCompiler;
import com.espertech.esper.compiler.client.EPCompilerProvider;
import com.espertech.esper.runtime.client.*;
import com.espertech.esperio.csv.AdapterCoordinator;
import com.espertech.esperio.csv.AdapterCoordinatorImpl;
import com.espertech.esperio.csv.AdapterInputSource;
import com.espertech.esperio.csv.CSVInputAdapter;
import com.espertech.esperio.csv.CSVInputAdapterSpec;

import events.BLtick;
import events.GOEStick;
import listeners.GeneralListener;

public class exampleMain {

	public static void main(String[] args) {

		// add classes to the configuration and compile Event Processing Language statements
		EPCompiler compiler = EPCompilerProvider.getCompiler();

		Configuration cepConfig = new Configuration();
		cepConfig.getCommon().addEventType("GOEStick", GOEStick.class);
		cepConfig.getCommon().addEventType("BLtick", BLtick.class);

		CompilerArguments compilerArgs = new CompilerArguments(cepConfig);

		String epl = "@name('GOEStick') select * from GOEStick; "
				+ "@name('BLtick') select * from BLtick; "
				+ "create context SegmentedByStation partition by station from BLtick; "
				+ "context SegmentedByStation insert into AmpAverages select station, "
				+ "avg(amp) as avgamp, max(timestamp) as timestamp, last(date) as date "
				+ "from BLtick.win:ext_timed_batch(timestamp, 1 min); "
				+ "@name('BL-1min-avg') select * from AmpAverages; "
				+ "@name('BL-1min-avg-diff') select e1.station, e1.avgamp, e2.avgamp, "
				+ "e2.avgamp-e1.avgamp as avgdiff, e2.timestamp-e1.timestamp as timediff, e1.date, e2.date "
				+ "from pattern[every e1=AmpAverages -> e2=AmpAverages(Math.abs(avgamp-e1.avgamp)>2 "
				+ "and e1.station=e2.station) where timer:within(5 min)]; ";

		EPCompiled epCompiled;
		try {
			epCompiled = compiler.compile(epl, compilerArgs);
		} catch (EPCompileException ex) {
			// handle exception here
			throw new RuntimeException(ex);
		}

		// obtain runtime and deploy compiled module
		EPRuntime cepRT = EPRuntimeProvider.getDefaultRuntime(cepConfig);

		EPDeployment deployment;
		try {
			deployment = cepRT.getDeploymentService().deploy(epCompiled);
		} catch (EPDeployException ex) {
			// handle exception here
			throw new RuntimeException(ex);
		}

		EPStatement statement1 = cepRT.getDeploymentService().
				getStatement(deployment.getDeploymentId(), "BL-1min-avg-diff");

		// attach callback listener
		statement1.addListener(new GeneralListener());

		// prepare events from csv files
		String filename1 = "bl06_03_2011.csv";
		// String filename1 = "bl15_04_2012.csv";
		CSVInputAdapterSpec spec1 = new CSVInputAdapterSpec(new AdapterInputSource(filename1), "BLtick");
		spec1.setTimestampColumn("timestamp");

		/*
		 * String filename2 = "goes15_04_2012.csv"; CSVInputAdapterSpec spec2 = new
		 * CSVInputAdapterSpec(new AdapterInputSource(filename2), "GOEStick"); String[]
		 * ss = {"date", "a", "timestamp"}; spec2.setPropertyOrder(ss);
		 * spec2.setTimestampColumn("timestamp");
		 * 
		 */ 

		// send events into runtime
		AdapterCoordinator coordinator = new AdapterCoordinatorImpl(cepRT, false);
		coordinator.coordinate(new CSVInputAdapter(spec1));
		// coordinator.coordinate(new CSVInputAdapter(spec2));
		coordinator.start();
		// (new CSVInputAdapter(cepRT, spec1)).start();

	}
}