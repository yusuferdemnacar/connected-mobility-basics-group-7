/*
 * Copyright 2010 Aalto University, ComNet
 * Released under GPLv3. See LICENSE.txt for details.
 */
package core;

import gui.DTNSimGUI;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import ui.DTNSimTextUI;
import util.Room;

/**
 * Simulator's main class
 */
public class DTNSim {
	public static List<Room> allRooms; // TODO: initialize
	/**
	 * If this option ({@value}) is given to program, batch mode and
	 * Text UI are used
	 */
	public static final String BATCH_MODE_FLAG = "-b";
	/** Delimiter for batch mode index range values (colon) */
	public static final String RANGE_DELIMETER = ":";

	/**
	 * Name of the static method that all resettable classes must have
	 * 
	 * @see #registerForReset(String)
	 */
	public static final String RESET_METHOD_NAME = "reset";
	/** List of class names that should be reset between batch runs */
	private static List<Class<?>> resetList = new ArrayList<Class<?>>();

	/**
	 * Starts the user interface with given arguments.
	 * If first argument is {@link #BATCH_MODE_FLAG}, the batch mode and text UI
	 * is started. The batch mode option must be followed by the number of runs,
	 * or a with a combination of starting run and the number of runs,
	 * delimited with a {@value #RANGE_DELIMETER}. Different settings from run
	 * arrays are used for different runs (see
	 * {@link Settings#setRunIndex(int)}). Following arguments are the settings
	 * files for the simulation run (if any). For GUI mode, the number before
	 * settings files (if given) is the run index to use for that run.
	 * 
	 * @param args Command line arguments
	 */
	public static void main(String[] args) {
		boolean batchMode = false;
		int nrofRuns[] = { 0, 1 };
		String confFiles[];
		int firstConfIndex = 0;
		int guiIndex = 0;

		/* set US locale to parse decimals in consistent way */
		java.util.Locale.setDefault(java.util.Locale.US);

		if (args.length > 0) {
			if (args[0].equals(BATCH_MODE_FLAG)) {
				batchMode = true;
				if (args.length == 1) {
					firstConfIndex = 1;
				} else {
					nrofRuns = parseNrofRuns(args[1]);
					firstConfIndex = 2;
				}
			} else { /* GUI mode */
				try { /* is there a run index for the GUI mode ? */
					guiIndex = Integer.parseInt(args[0]);
					firstConfIndex = 1;
				} catch (NumberFormatException e) {
					firstConfIndex = 0;
				}
			}
			confFiles = args;
		} else {
			confFiles = new String[] { null };
		}

		initSettings(confFiles, firstConfIndex);

		// hardcode rooms for now
		Room EG_5613_009A = new Room("data/fmi-map/5613_EG_009A.wkt", "5613_EG_009A");
		Room EG_5608_038 = new Room("data/fmi-map/5608_EG_038.wkt", "5608_EG_038");
		Room EG_5613_062 = new Room("data/fmi-map/5613_EG_062.wkt", "5613_EG_062");
		Room EG_5611_038 = new Room("data/fmi-map/5611_EG_038.wkt", "5611_EG_038");
		Room magistrale = new Room("data/fmi-map/magistrale.wkt", "magistrale");
		Room EG_5608_059 = new Room("data/fmi-map/5608_EG_059.wkt", "5608_EG_059");
		Room hs_1 = new Room("data/fmi-map/hs_1.wkt", "hs_1");
		Room hs_3 = new Room("data/fmi-map/hs_3.wkt", "hs_3");
		Room EG_5609_022 = new Room("data/fmi-map/5609_EG_022.wkt", "5609_EG_022");
		Room computerhall = new Room("data/fmi-map/computerhall.wkt", "computerhall");
		Room hs_2 = new Room("data/fmi-map/hs_2.wkt", "hs_2");
		Room EG_5613_010 = new Room("data/fmi-map/5613_EG_010.wkt", "5613_EG_010");
		Room EG_5607_014 = new Room("data/fmi-map/5607_EG_014.wkt", "5607_EG_014");
		Room EG_5613_036 = new Room("data/fmi-map/5613_EG_036.wkt", "5613_EG_036");
		Room library = new Room("data/fmi-map/library.wkt", "library");
		Room EG_5613_008 = new Room("data/fmi-map/5613_EG_008.wkt", "5613_EG_008");
		Room EG_5608_053 = new Room("data/fmi-map/5608_EG_053.wkt", "5608_EG_053");
		Room EG_5609_038 = new Room("data/fmi-map/5609_EG_038.wkt", "5609_EG_038");
		Room EG_5608_055 = new Room("data/fmi-map/5608_EG_055.wkt", "5608_EG_055");
		Room EG_5613_054 = new Room("data/fmi-map/5613_EG_054.wkt", "5613_EG_054");
		Room EG_5605_035 = new Room("data/fmi-map/5605_EG_035.wkt", "5605_EG_035");
		Room EG_5608_036 = new Room("data/fmi-map/5608_EG_036.wkt", "5608_EG_036");
		DTNSim.allRooms = Arrays.asList(
				EG_5613_009A,
				EG_5608_038,
				EG_5613_062,
				EG_5611_038,
				magistrale,
				EG_5608_059,
				hs_1,
				hs_3,
				EG_5609_022,
				computerhall,
				hs_2,
				EG_5613_010,
				EG_5607_014,
				EG_5613_036,
				library,
				EG_5613_008,
				EG_5608_053,
				EG_5609_038,
				EG_5608_055,
				EG_5613_054,
				EG_5605_035,
				EG_5608_036);

		if (batchMode) {
			long startTime = System.currentTimeMillis();
			for (int i = nrofRuns[0]; i < nrofRuns[1]; i++) {
				print("Run " + (i + 1) + "/" + nrofRuns[1]);
				Settings.setRunIndex(i);
				resetForNextRun();
				new DTNSimTextUI().start();
			}
			double duration = (System.currentTimeMillis() - startTime) / 1000.0;
			print("---\nAll done in " + String.format("%.2f", duration) + "s");
		} else {
			Settings.setRunIndex(guiIndex);
			new DTNSimGUI().start();
		}
	}

	/**
	 * Initializes Settings
	 * 
	 * @param confFiles  File name paths where to read additional settings
	 * @param firstIndex Index of the first config file name
	 */
	private static void initSettings(String[] confFiles, int firstIndex) {
		int i = firstIndex;

		if (i >= confFiles.length) {
			return;
		}

		try {
			Settings.init(confFiles[i]);
			for (i = firstIndex + 1; i < confFiles.length; i++) {
				Settings.addSettings(confFiles[i]);
			}
		} catch (SettingsError er) {
			try {
				Integer.parseInt(confFiles[i]);
			} catch (NumberFormatException nfe) {
				/* was not a numeric value */
				System.err.println("Failed to load settings: " + er);
				System.err.println("Caught at " + er.getStackTrace()[0]);
				System.exit(-1);
			}
			System.err.println("Warning: using deprecated way of " +
					"expressing run indexes. Run index should be the " +
					"first option, or right after -b option (optionally " +
					"as a range of start and end values).");
			System.exit(-1);
		}
	}

	/**
	 * Registers a class for resetting. Reset is performed after every
	 * batch run of the simulator to reset the class' state to initial
	 * state. All classes that have static fields that should be resetted
	 * to initial values between the batch runs should register using
	 * this method. The given class must have a static implementation
	 * for the resetting method (a method called {@value #RESET_METHOD_NAME}
	 * without any parameters).
	 * 
	 * @param className Full name (i.e., containing the packet path)
	 *                  of the class to register. For example:
	 *                  <code>core.SimClock</code>
	 */
	public static void registerForReset(String className) {
		Class<?> c = null;
		try {
			c = Class.forName(className);
			c.getMethod(RESET_METHOD_NAME);
		} catch (ClassNotFoundException e) {
			System.err.println("Can't register class " + className +
					" for resetting; class not found");
			System.exit(-1);

		} catch (NoSuchMethodException e) {
			System.err.println("Can't register class " + className +
					" for resetting; class doesn't contain resetting method");
			System.exit(-1);
		}
		resetList.add(c);
	}

	/**
	 * Resets all registered classes.
	 */
	private static void resetForNextRun() {
		for (Class<?> c : resetList) {
			try {
				Method m = c.getMethod(RESET_METHOD_NAME);
				m.invoke(null);
			} catch (Exception e) {
				System.err.println("Failed to reset class " + c.getName());
				e.printStackTrace();
				System.exit(-1);
			}
		}
	}

	/**
	 * Parses the number of runs, and an optional starting run index, from a
	 * command line argument
	 * 
	 * @param arg The argument to parse
	 * @return The first and (last_run_index - 1) in an array
	 */
	private static int[] parseNrofRuns(String arg) {
		int val[] = { 0, 1 };
		try {
			if (arg.contains(RANGE_DELIMETER)) {
				val[0] = Integer.parseInt(arg.substring(0,
						arg.indexOf(RANGE_DELIMETER))) - 1;
				val[1] = Integer.parseInt(arg.substring(arg.indexOf(RANGE_DELIMETER) + 1, arg.length()));
			} else {
				val[0] = 0;
				val[1] = Integer.parseInt(arg);
			}
		} catch (NumberFormatException e) {
			System.err.println("Invalid argument '" + arg + "' for" +
					" number of runs");
			System.err.println("The argument must be either a single value, " +
					"or a range of values (e.g., '2:5'). Note that this " +
					"option has changed in version 1.3.");
			System.exit(-1);
		}

		if (val[0] < 0) {
			System.err.println("Starting run value can't be smaller than 1");
			System.exit(-1);
		}
		if (val[0] >= val[1]) {
			System.err.println("Starting run value can't be bigger than the " +
					"last run value");
			System.exit(-1);
		}

		return val;
	}

	/**
	 * Prints text to stdout
	 * 
	 * @param txt Text to print
	 */
	private static void print(String txt) {
		System.out.println(txt);
	}
}
