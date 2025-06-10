package movement; // Or your appropriate package

import java.util.ArrayList;
import java.util.HashMap;

import core.Coord;
import core.Settings;
import core.ModifiableSettings;
import core.SimClock;
import util.Room;

public class SelfStudierMovement extends ExtendedMovementModel {

    public static final String LECTURE_TAKER_MOVEMENT_NS = "LectureTakerMovement";
    public static final String INITIAL_X = "initialX";
    public static final String INITIAL_Y = "initialY";
    public static final String WAIT_TIME = "waitTime";
    public static final String TIME_TABLES_DIR = "timeTablesDir";
    public static final String ROUTE_FILES_DIR = "routeFilesDir";
    public static final String STUDY_ROOM_ASSIGNMENT_FILE = "studyRoomAssignmentFile";

    private Settings groupSettings;
    private Settings ltmSettings;

    private Coord initialCoordinates;
    public static final String START_TIME = "startTime";
    public static final String END_TIME = "endTime";
    private double[] waitTime;
    private double startTime;
    private double endTime;
    public String timeTablesDir;
    private ArrayList<Integer> timeTable;
    public String routeFilesDir;
    private String studyRoomAssignmentFile;
    private HashMap<Integer, Integer> studyRoomAssignment;
    private Room studyRoom;
    private Room breakRoom;
    private Coord studyLocation;
    private int currentTimeInterval;
    private double currentTimeIntervalEndTime;
    private boolean firstStudySession = true;

    private int currentMovementMode;

    // Sub-models
    private SwitchableStationaryMovement stationaryMM;
    private SwitchableProhibitedPolygonRwp randomWaypointMM;
    private MapRouteMovement mapRouteMM;
    private SwitchableSimpleWaypoint simpleWaypointMM;

    private static final int START_MODE = -1;
    private static final int EXIT_MODE = 0;
    private static final int MOVE_TO_NEXT_ROOM_DOOR_MODE = 1;
    private static final int PICK_STUDY_PLACE_MODE = 2;
    private static final int RETURN_TO_STUDY_PLACE_MODE = 3;
    private static final int STUDY_MODE = 4;
    private static final int BREAK_MODE = 5;

    /**
     * Constructor. Reads room settings.
     * 
     * @param settings The settings object, typically namespaced for the group
     *                 using this movement model.
     */
    public SelfStudierMovement(Settings settings) {
        super(settings);
        this.groupSettings = settings;
        this.ltmSettings = new Settings(LECTURE_TAKER_MOVEMENT_NS);

        this.randomWaypointMM = new SwitchableProhibitedPolygonRwp(settings);
        this.stationaryMM = new SwitchableStationaryMovement(settings);
        this.simpleWaypointMM = new SwitchableSimpleWaypoint(settings);
        
        this.waitTime = this.groupSettings.getCsvDoubles(WAIT_TIME, 2);
        this.startTime = this.groupSettings.getDouble(START_TIME, 0);
        this.endTime = this.groupSettings.getDouble(END_TIME, Double.MAX_VALUE);
        this.timeTablesDir = this.groupSettings.getSetting(TIME_TABLES_DIR, "data/group-data/self-studier/time-tables/");
        this.timeTable = new ArrayList<>();
        this.routeFilesDir = this.groupSettings.getSetting(ROUTE_FILES_DIR, "data/group-data/self-studier/routes/");
        this.studyRoomAssignmentFile = this.groupSettings.getSetting(STUDY_ROOM_ASSIGNMENT_FILE, "data/group-data/self-studier/study-room-assignment.txt");
        this.studyRoomAssignment = new HashMap<>();
        this.initialCoordinates = new Coord(
            this.groupSettings.getDouble(INITIAL_X, 0),
            this.groupSettings.getDouble(INITIAL_Y, 0)
        );

        this.studyRoom = null;
        this.breakRoom = null;
        this.studyLocation = null;
        this.currentTimeInterval = 0;
        this.currentTimeIntervalEndTime = 0;
        this.firstStudySession = true;

        this.currentMovementMode = START_MODE;

    }

    /**
     * Copy constructor.
     * 
     * @param proto The SelfStudierMovement object to copy.
     */
    public SelfStudierMovement(SelfStudierMovement proto) {
        super(proto);
        this.groupSettings = proto.groupSettings;
        this.ltmSettings = proto.ltmSettings;

        this.mapRouteMM = null;
        this.randomWaypointMM = new SwitchableProhibitedPolygonRwp(proto.randomWaypointMM);
        this.stationaryMM = new SwitchableStationaryMovement(proto.stationaryMM);
        this.simpleWaypointMM = new SwitchableSimpleWaypoint(proto.simpleWaypointMM);

        this.waitTime = proto.waitTime;
        this.startTime = proto.startTime;
        this.endTime = proto.endTime;
        this.timeTablesDir = proto.timeTablesDir;
        this.timeTable = new ArrayList<>(proto.timeTable);
        this.routeFilesDir = proto.routeFilesDir;
        this.studyRoomAssignmentFile = proto.studyRoomAssignmentFile;
        this.studyRoomAssignment = new HashMap<>(proto.studyRoomAssignment);
        this.initialCoordinates = proto.initialCoordinates;

        this.studyRoom = proto.studyRoom;
        this.breakRoom = proto.breakRoom;
        this.studyLocation = proto.studyLocation;
        this.currentTimeIntervalEndTime = proto.currentTimeIntervalEndTime;

        this.stationaryMM.setLocation(this.initialCoordinates);
        setCurrentMovementModel(stationaryMM);
        this.currentMovementMode = proto.currentMovementMode;
    }

    @Override
    public MovementModel replicate() {
        return new SelfStudierMovement(this);
    }

    @Override
    public Coord getInitialLocation() {
        return initialCoordinates.clone();
    }

    // Kind of asymmetric check
    // We need to check the exit state rather than end time to give hosts a chance to fully leave the building which can exceed the time of the end of the last lecture (which is the endTime).
    // We need to check the start time rather than the start state because if the hosts are inactive in the start state, they don't receive new orders, which is the only way to change state.

    @Override
    public boolean isActive() {
        if (this.currentMovementMode != EXIT_MODE && SimClock.getTime() >= this.startTime) {
            return true;
        }
        return false;
    }

    @Override
    public double nextPathAvailable() {
        if (this.currentMovementMode == START_MODE) {
            return this.startTime;
        } else if (this.currentMovementMode == MOVE_TO_NEXT_ROOM_DOOR_MODE) {
            return SimClock.getTime();
        } else if (this.currentMovementMode == PICK_STUDY_PLACE_MODE) {
            return SimClock.getTime();
        } else if (this.currentMovementMode == STUDY_MODE) {
            return currentTimeIntervalEndTime;
        } else if (this.currentMovementMode == BREAK_MODE) {
            return Math.min(SimClock.getTime() + generateWaitTime(), this.currentTimeIntervalEndTime);
        } else if (this.currentMovementMode == RETURN_TO_STUDY_PLACE_MODE) {
            return SimClock.getTime();
        } else if (this.currentMovementMode == EXIT_MODE) {
            return Double.MAX_VALUE;
        }
        return Double.MAX_VALUE;
    }

    public ArrayList<Integer> getTimeTable(String timeTableFile) {
        ArrayList<Integer> timeTable = new ArrayList<>();
        try (java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.FileReader(timeTableFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                timeTable.add(Integer.parseInt(line.trim()));
            }
        } catch (java.io.IOException e) {
            System.err.println("Error reading time table file: " + timeTableFile + ". " + e.getMessage());
        }
        return timeTable;
    }

    @Override
    public boolean newOrders() {
        if (this.currentMovementMode == START_MODE) {
            int hostID = this.getHost().getAddress();
            int nrofHosts = this.groupSettings.getInt("nrofHosts", 1);
            int localHostID = (hostID % nrofHosts) + 1;

            String routeFilePath = this.routeFilesDir + "/self_studier_" + localHostID + "_route.wkt";
            ModifiableSettings hostSpecificSettings = new ModifiableSettings(this.groupSettings);
            hostSpecificSettings.setSetting("routeFile", routeFilePath);

            this.mapRouteMM = new MapRouteMovement(hostSpecificSettings);
            this.mapRouteMM.setHost(getHost());

            String studyRoomName = Room.getStudyRoomName(localHostID, this.studyRoomAssignmentFile);
            String breakRoomName = "magistrale";
            String studyRoomFilePath = this.ltmSettings.getSetting(studyRoomName + ".file", null);
            String breakRoomFilePath = this.ltmSettings.getSetting(breakRoomName + ".file", null);
            this.studyRoom = new Room(studyRoomFilePath, studyRoomName);
            this.breakRoom = new Room(breakRoomFilePath, breakRoomName);

            String timeTableFilePath = this.timeTablesDir + "/self_studier_" + localHostID + "_timetable.txt";
            this.timeTable = getTimeTable(timeTableFilePath);

            this.currentTimeInterval = 1;
            this.currentTimeIntervalEndTime = this.timeTable.get(this.currentTimeInterval - 1);

            this.mapRouteMM.setLocation(this.initialCoordinates);
            setCurrentMovementModel(mapRouteMM);
            this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;

        } else if (this.currentMovementMode == MOVE_TO_NEXT_ROOM_DOOR_MODE) {
            if (this.currentTimeInterval > this.timeTable.size()) {
                this.stationaryMM.setLocation(getCurrentMovementModel().getLastLocation());
                setCurrentMovementModel(stationaryMM);
                this.currentMovementMode = EXIT_MODE;
            } else {
                if (this.mapRouteMM.isReady()) {
                    if (this.firstStudySession) {
                        this.firstStudySession = false;
                        this.randomWaypointMM.setPolygon(this.studyRoom.getPolygon());
                        this.randomWaypointMM.setLocation(getCurrentMovementModel().getLastLocation());
                        setCurrentMovementModel(randomWaypointMM);
                        this.currentMovementMode = PICK_STUDY_PLACE_MODE;
                    } else {
                        if (this.currentTimeInterval % 2 == 0) {
                            this.randomWaypointMM.setPolygon(this.breakRoom.getPolygon());
                            this.randomWaypointMM.setLocation(getCurrentMovementModel().getLastLocation());
                            setCurrentMovementModel(randomWaypointMM);
                            this.currentMovementMode = BREAK_MODE;
                        } else {
                            this.simpleWaypointMM.setLocation(getCurrentMovementModel().getLastLocation());
                            this.simpleWaypointMM.setTargetLocation(this.studyLocation);
                            setCurrentMovementModel(simpleWaypointMM);
                            this.currentMovementMode = RETURN_TO_STUDY_PLACE_MODE;
                        }
                        
                    }
                }
            }
        } else if (this.currentMovementMode == PICK_STUDY_PLACE_MODE) {
            if (this.randomWaypointMM.isReady()) {
                this.stationaryMM.setLocation(getCurrentMovementModel().getLastLocation());
                setCurrentMovementModel(stationaryMM);
                this.currentMovementMode = STUDY_MODE;
                this.studyLocation = this.randomWaypointMM.getLastLocation();
            }
        } else if (this.currentMovementMode == RETURN_TO_STUDY_PLACE_MODE) {
            if (this.stationaryMM.isReady()) {
                this.stationaryMM.setLocation(this.studyLocation);
                setCurrentMovementModel(stationaryMM);
                this.currentMovementMode = STUDY_MODE;
            }
        } else if (this.currentMovementMode == STUDY_MODE) {
            this.currentTimeInterval++;
            if (this.currentTimeInterval - 1 < this.timeTable.size()) {
                this.currentTimeIntervalEndTime = this.timeTable.get(this.currentTimeInterval - 1);
            } else {
                this.currentTimeIntervalEndTime =  this.timeTable.get(this.timeTable.size() - 1);
            }
            this.mapRouteMM.setLocation(getCurrentMovementModel().getLastLocation());
            setCurrentMovementModel(mapRouteMM);
            this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
        } else if (this.currentMovementMode == BREAK_MODE) {
            if (SimClock.getTime() >= this.currentTimeIntervalEndTime) {
                this.currentTimeInterval++;
                if (this.currentTimeInterval - 1 < this.timeTable.size()) {
                    this.currentTimeIntervalEndTime = this.timeTable.get(this.currentTimeInterval - 1);
                } else {
                    this.currentTimeIntervalEndTime = this.timeTable.get(this.timeTable.size() - 1);
                }
                this.mapRouteMM.setLocation(getCurrentMovementModel().getLastLocation());
                setCurrentMovementModel(mapRouteMM);
                this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
            }
        } else if (this.currentMovementMode == EXIT_MODE) {
            // System.out.println("SelfStudierMovement: Exiting, no next room defined.");
        } else {
            System.out.println("SelfStudierMovement: Invalid movement mode, resetting to MOVE_TO_NEXT_ROOM_DOOR_MODE.");
            this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
            setCurrentMovementModel(mapRouteMM);
            mapRouteMM.setLocation(this.initialCoordinates);
        }
        return true;

    }
}