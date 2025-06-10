package movement; // Or your appropriate package

import java.util.ArrayList;
import java.util.HashMap;

import core.Coord;
import core.Settings;
import core.SimClock;
import util.Room;

public class LectureTakerMovement extends ExtendedMovementModel {

    // Namespace for LectureTakerMovement specific global settings
    public static final String LECTURE_TAKER_MOVEMENT_NS = "LectureTakerMovement";

    public static final String INITIAL_X = "initialX";
    public static final String INITIAL_Y = "initialY";
    public static final String START_TIME = "startTime";
    public static final String END_TIME = "endTime";
    public static final String WAIT_TIME = "waitTime";
    public static final String LECTURE_PERIOD_DURATION_SETTING = "lecturePeriodDuration";

    private Settings groupSettings;
    private Settings ltmSettings;

    private ArrayList<String> roomSequence;
    private HashMap<String, Room> rooms = new HashMap<>();

    private Coord initialCoordinates;
    private double startTime;
    private double endTime;
    private double[] waitTime;
    private Room currentRoom;
    private Room nextRoom;
    private int firstLectureTimeSlot;
    private int currentLectureTimeSlot;
    private int currentMovementMode;
    private double lecturePeriodDuration;

    // Sub-models
    private SwitchableStationaryMovement stationaryMM;
    private SwitchableProhibitedPolygonRwp randomWaypointMM;
    private MapRouteMovement mapRouteMM;

    private static final int START_MODE = -1;
    private static final int EXIT_MODE = 0;
    private static final int MOVE_TO_NEXT_ROOM_DOOR_MODE = 1;
    private static final int RANDOM_WALK_IN_CURRENT_ROOM_MODE = 2;
    private static final int STATIONARY_IN_CURRENT_ROOM_MODE = 3;
    private static final int ROAMING_IN_MAGISTRALE_MODE = 4;

    /**
     * Constructor. Reads room settings.
     * 
     * @param settings The settings object, typically namespaced for the group
     *                 using this movement model.
     */
    public LectureTakerMovement(Settings settings) {
        super(settings);
        this.groupSettings = settings;
        this.ltmSettings = new Settings(LECTURE_TAKER_MOVEMENT_NS);

        this.mapRouteMM = new MapRouteMovement(settings);
        this.randomWaypointMM = new SwitchableProhibitedPolygonRwp(settings);
        this.stationaryMM = new SwitchableStationaryMovement(settings);

        this.startTime = this.groupSettings.getDouble(START_TIME, 0);
        this.endTime = this.groupSettings.getDouble(END_TIME, Double.MAX_VALUE);
        this.waitTime = this.groupSettings.getCsvDoubles(WAIT_TIME, 2);
        this.initialCoordinates = new Coord(
                this.ltmSettings.getDouble(INITIAL_X, 0),
                this.ltmSettings.getDouble(INITIAL_Y, 0));

        this.lecturePeriodDuration = this.ltmSettings.getDouble(LECTURE_PERIOD_DURATION_SETTING, 7200);

        this.firstLectureTimeSlot = 0;
        this.currentLectureTimeSlot = 0;

        this.rooms = new HashMap<>();
        this.currentRoom = null;
        this.nextRoom = null;

        this.currentMovementMode = START_MODE;

    }

    /**
     * Copy constructor.
     * 
     * @param proto The LectureTakerMovement object to copy.
     */
    public LectureTakerMovement(LectureTakerMovement proto) {
        super(proto);
        this.groupSettings = proto.groupSettings;
        this.ltmSettings = proto.ltmSettings;

        this.stationaryMM = new SwitchableStationaryMovement(proto.stationaryMM);
        this.randomWaypointMM = new SwitchableProhibitedPolygonRwp(proto.randomWaypointMM);
        this.mapRouteMM = new MapRouteMovement(proto.mapRouteMM);

        this.firstLectureTimeSlot = proto.firstLectureTimeSlot;
        this.currentLectureTimeSlot = proto.currentLectureTimeSlot;

        this.startTime = proto.startTime;
        this.endTime = proto.endTime;
        this.waitTime = proto.waitTime;
        this.initialCoordinates = proto.initialCoordinates;
        this.lecturePeriodDuration = proto.lecturePeriodDuration;

        this.rooms = new HashMap<>(proto.rooms);

        this.currentRoom = proto.currentRoom;
        this.nextRoom = proto.nextRoom;

        this.stationaryMM.setLocation(this.initialCoordinates);
        setCurrentMovementModel(stationaryMM);
        this.currentMovementMode = proto.currentMovementMode;
    }

    @Override
    public MovementModel replicate() {
        return new LectureTakerMovement(this);
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
        } else if (this.currentMovementMode == RANDOM_WALK_IN_CURRENT_ROOM_MODE) {
            return SimClock.getTime();
        } else if (this.currentMovementMode == STATIONARY_IN_CURRENT_ROOM_MODE) {
            return this.currentLectureTimeSlot * this.lecturePeriodDuration;
        } else if (this.currentMovementMode == ROAMING_IN_MAGISTRALE_MODE) {
            double end_of_lecture_slot = this.currentLectureTimeSlot * this.lecturePeriodDuration;
            return Math.min(SimClock.getTime() + generateWaitTime(), end_of_lecture_slot);
        } else if (this.currentMovementMode == EXIT_MODE) {
            return Double.MAX_VALUE;
        }
        return Double.MAX_VALUE;
    }

    @Override
    public boolean newOrders() {
        if (this.currentMovementMode == START_MODE) {
            this.roomSequence = Room.getRoomSequence("data/group-data/" + this.getHost().groupId + "_schedule.txt");
            this.firstLectureTimeSlot = (int) (this.startTime / this.lecturePeriodDuration) + 1;
            this.currentLectureTimeSlot = this.firstLectureTimeSlot;
            for (int i = 0; i < roomSequence.size(); i++) {
                String roomName = roomSequence.get(i);
                if (!this.rooms.containsKey(roomName)) {
                    String filePath = this.ltmSettings.getSetting(roomName + ".file", null);
                    Room room = new Room(filePath, roomName);
                    rooms.put(roomName, room);
                }
            }
            this.currentRoom = null;
            this.nextRoom = rooms.get(roomSequence.get(0));
            this.mapRouteMM.setLocation(this.initialCoordinates);
            setCurrentMovementModel(mapRouteMM);
            this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
        } else if (this.currentMovementMode == MOVE_TO_NEXT_ROOM_DOOR_MODE) {
            if (this.nextRoom == null) {
                this.stationaryMM.setLocation(getCurrentMovementModel().getLastLocation());
                setCurrentMovementModel(stationaryMM);
                this.currentMovementMode = EXIT_MODE;
            } else {
                if (this.mapRouteMM.isReady()) {
                    this.currentRoom = this.nextRoom;
                    this.randomWaypointMM.setPolygon(currentRoom.getPolygon());
                    this.randomWaypointMM.setLocation(getCurrentMovementModel().getLastLocation());
                    setCurrentMovementModel(randomWaypointMM);
                    if (this.currentRoom.getName().equals("magistrale")) {
                        this.currentMovementMode = ROAMING_IN_MAGISTRALE_MODE;
                    } else {
                        this.currentMovementMode = RANDOM_WALK_IN_CURRENT_ROOM_MODE;
                    }
                }
            }
        } else if (this.currentMovementMode == RANDOM_WALK_IN_CURRENT_ROOM_MODE) {
            if (this.randomWaypointMM.isReady()) {
                this.stationaryMM.setLocation(this.randomWaypointMM.getLastLocation());
                setCurrentMovementModel(stationaryMM);
                this.currentMovementMode = STATIONARY_IN_CURRENT_ROOM_MODE;
            }
        } else if (this.currentMovementMode == STATIONARY_IN_CURRENT_ROOM_MODE) {
            this.currentLectureTimeSlot++;
            if (this.currentLectureTimeSlot - this.firstLectureTimeSlot < this.roomSequence.size()) {
                this.nextRoom = this.rooms.get(this.roomSequence.get(this.currentLectureTimeSlot - this.firstLectureTimeSlot));
            } else {
                this.nextRoom = null;
            }
            this.mapRouteMM.setLocation(getCurrentMovementModel().getLastLocation());
            setCurrentMovementModel(mapRouteMM);
            this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
        } else if (this.currentMovementMode == ROAMING_IN_MAGISTRALE_MODE) {
            if (SimClock.getTime() >= (this.currentLectureTimeSlot * this.lecturePeriodDuration)) {
                this.currentLectureTimeSlot++;
                if (this.currentLectureTimeSlot - this.firstLectureTimeSlot < this.roomSequence.size()) {
                    this.nextRoom = this.rooms.get(this.roomSequence.get(this.currentLectureTimeSlot - this.firstLectureTimeSlot));
                } else {
                    this.nextRoom = null;
                }
                if (this.nextRoom != null && this.nextRoom.getName().equals("magistrale")) {
                    this.mapRouteMM.getPath();
                } else {
                    this.mapRouteMM.setLocation(getCurrentMovementModel().getLastLocation());
                    setCurrentMovementModel(mapRouteMM);
                    this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
                }
            }
        } else if (this.currentMovementMode == EXIT_MODE) {
            // System.out.println("LectureTakerMovement: Exiting, no next room defined.");
        } else {
            System.out
                    .println("LectureTakerMovement: Invalid movement mode, resetting to MOVE_TO_NEXT_ROOM_DOOR_MODE.");
            this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
            setCurrentMovementModel(mapRouteMM);
            mapRouteMM.setLocation(this.initialCoordinates);
        }
        return true;

    }
}