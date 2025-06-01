package movement; // Or your appropriate package

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import core.Coord;
import core.Settings;

public class LectureTakerMovement extends ExtendedMovementModel {

    // Namespace for LectureTakerMovement specific global settings
    public static final String LECTURE_TAKER_MOVEMENT_NS = "LectureTakerMovement";
    // Settings keys
    public static final String LECTURE_NROF_ROOMS_SETTING = "nrofRooms";

    public static final String INITIAL_X = "initialX";
    public static final String INITIAL_Y = "initialY";
    // New settings keys for durations
    public static final String RANDOM_WALK_DURATION_SETTING = "randomWalkDuration";
    public static final String STATIONARY_DURATION_SETTING = "stationaryDuration";

    private Settings ltmSettings;

    private ArrayList<String> roomSequence;
    private HashMap<String, Room> rooms = new HashMap<>();

    private Coord initialGlobalEntrance; // Entrance coordinate for the first room
    private Room currentRoom; // Current room the lecture taker is in
    private Room nextRoom; // Next room to move to
    private int lectureSlot;
    private boolean isFirstOrder = true;

    private int currentMovementMode; // Current movement mode

    private double stationaryPhaseDuration;

    // Sub-models
    private SwitchableStationaryMovement stationaryMM;
    private SwitchableProhibitedPolygonRwp randomWaypointMM; // Random waypoint movement model
    private MapRouteMovement mapRouteMM;

    private static final int MOVE_TO_NEXT_ROOM_DOOR_MODE = 0;
    private static final int RANDOM_WALK_IN_CURRENT_ROOM_MODE = 1;
    private static final int STATIONARY_IN_CURRENT_ROOM_MODE = 2;
    private static final int EXIT_MODE = 3;

    // Helper class to store room dimensions
    private static class Room {
        private String name;
        private List<Coord> polygon;

        Room(String filePath, String name) {
            this.name = name;
            this.polygon = readPolygon(filePath);
            if (polygon.isEmpty()) {
                System.err.println("LectureTakerMovement: No valid polygon found in file " + filePath);
            }
        }

        public static ArrayList<String> getRoomSequence(String filePath) {
            ArrayList<String> roomSequence = new ArrayList<>();
            try (java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.FileReader(filePath))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    // Assuming each line contains a room name
                    roomSequence.add(line.trim());
                }
            } catch (java.io.IOException e) {
                System.err.println("Error reading room sequence file: " + filePath + ". " + e.getMessage());
            }
            return roomSequence;
        }

        public static List<Coord> readPolygon(String filePath) {
            List<Coord> coords = new ArrayList<>();
            try (java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.FileReader(filePath))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String[] parts = line.substring(line.indexOf('(') + 1, line.indexOf(')')).split("\\s+");
                    double x = Double.parseDouble(parts[0]);
                    double y = Double.parseDouble(parts[1]);
                    // Round coordinates to 3 decimal places
                    // full precision causes bugs in the ray casting algorithm
                    x = Math.round(x * 1000.0) / 1000.0;
                    y = Math.round(y * 1000.0) / 1000.0;
                    coords.add(new Coord(x, y));
                }
            } catch (java.io.IOException e) {
                System.err.println("Error reading WKT file: " + filePath + ". " + e.getMessage());
                // Return an empty list or handle the error as appropriate
                return new ArrayList<>();
            } catch (Exception e) { // Catch other potential parsing errors if format isn't perfect
                System.err.println("Error parsing WKT file: " + filePath + ". " + e.getMessage());
                return new ArrayList<>();
            }
            return coords;
        }
    }

    /**
     * Constructor. Reads room settings.
     * 
     * @param settings The settings object, typically namespaced for the group
     *                 using this movement model.
     */
    public LectureTakerMovement(Settings settings) {
        super(settings);

        this.mapRouteMM = new MapRouteMovement(settings);
        this.randomWaypointMM = new SwitchableProhibitedPolygonRwp(settings);
        this.stationaryMM = new SwitchableStationaryMovement(settings);

        this.lectureSlot = 1;

        Settings ltmSettings = new Settings(LECTURE_TAKER_MOVEMENT_NS);
        this.ltmSettings = ltmSettings;

        double initialX = ltmSettings.getDouble(INITIAL_X, 0);
        double initialY = ltmSettings.getDouble(INITIAL_Y, 0);
        this.initialGlobalEntrance = new Coord(initialX, initialY);

        this.stationaryPhaseDuration = ltmSettings.getDouble(STATIONARY_DURATION_SETTING, 5.0);

    }

    /**
     * Copy constructor.
     * 
     * @param proto The LectureTakerMovement object to copy.
     */
    public LectureTakerMovement(LectureTakerMovement proto) {
        super(proto);
        this.rooms = new HashMap<>(proto.rooms); // Deep copy of the rooms map
        this.initialGlobalEntrance = proto.initialGlobalEntrance.clone();
        this.currentRoom = proto.currentRoom; // Reference copy
        this.nextRoom = proto.nextRoom; // Reference copy
        this.stationaryPhaseDuration = proto.stationaryPhaseDuration;
        this.stationaryMM = new SwitchableStationaryMovement(proto.stationaryMM);
        this.randomWaypointMM = new SwitchableProhibitedPolygonRwp(proto.randomWaypointMM);
        this.mapRouteMM = new MapRouteMovement(proto.mapRouteMM);
        this.lectureSlot = proto.lectureSlot;
        this.isFirstOrder = proto.isFirstOrder;
        this.ltmSettings = proto.ltmSettings; // Reference copy
        mapRouteMM.setLocation(initialGlobalEntrance.clone());
        setCurrentMovementModel(mapRouteMM);
        this.currentMovementMode = proto.currentMovementMode;
    }

    @Override
    public MovementModel replicate() {
        return new LectureTakerMovement(this);
    }

    @Override
    public Coord getInitialLocation() {
        return initialGlobalEntrance.clone();
    }

    @Override
    public boolean newOrders() {
        if (this.isFirstOrder) {
            this.roomSequence = Room
                    .getRoomSequence("data/group-data/" + this.getHost().groupId + "_room_sequence.txt");

            for (int i = 0; i < roomSequence.size(); i++) {
                String roomName = roomSequence.get(i);
                if (!this.rooms.containsKey(roomName)) {
                    String filePath = this.ltmSettings.getSetting(roomName + ".file", null);
                    Room room = new Room(filePath, roomName);
                    rooms.put(roomName, room);
                }

            }

            if (!rooms.isEmpty()) {
                this.currentRoom = null;
                this.nextRoom = rooms.get(roomSequence.get(0));
            } else {
                System.out.println("LectureTakerMovement: No rooms defined, initializing with default values.");
                this.currentRoom = null; // No rooms defined
                this.nextRoom = null; // No next room
                this.currentMovementMode = -1; // Invalid movement mode
            }
            this.isFirstOrder = false; // Set to false after first order
        }
        // System.out.println("LectureTakerMovement: Checking for new orders.");
        // System.out.println("this.currentMovementMode = " + this.currentMovementMode);
        if (this.currentMovementMode == MOVE_TO_NEXT_ROOM_DOOR_MODE) {
            if (this.nextRoom == null) {
                System.out.println("LectureTakerMovement: No next room defined, exiting.");
                this.stationaryMM.setLocation(this.randomWaypointMM.getLastLocation());
                setCurrentMovementModel(stationaryMM);
                this.currentMovementMode = EXIT_MODE;
                return true;
            }
            if (this.mapRouteMM.isReady()) {
                System.out.println(
                        this.getHost().toString() + ": Choosing random waypoint in room " + this.nextRoom.name);
                this.currentRoom = nextRoom; // Update current room
                if (this.lectureSlot >= 0 && this.lectureSlot < this.roomSequence.size()) {
                    this.nextRoom = this.rooms.get(
                            this.roomSequence.get(this.lectureSlot));
                } else {
                    this.nextRoom = null;
                }
                this.randomWaypointMM.setPolygon(currentRoom.polygon);
                this.randomWaypointMM.setLocation(getCurrentMovementModel().getLastLocation());
                setCurrentMovementModel(randomWaypointMM);
                this.currentMovementMode = RANDOM_WALK_IN_CURRENT_ROOM_MODE;
            }
        } else if (this.currentMovementMode == RANDOM_WALK_IN_CURRENT_ROOM_MODE) {
            if (this.randomWaypointMM.isReady()) {
                this.stationaryMM.setLocation(this.randomWaypointMM.getLastLocation());
                setCurrentMovementModel(stationaryMM);
                this.currentMovementMode = STATIONARY_IN_CURRENT_ROOM_MODE;
                System.out.println(this.getHost().toString()
                        + ": Entered stationary phase in room " + this.currentRoom.name
                        + " at time " + core.SimClock.getTime());
            }
        } else if (this.currentMovementMode == STATIONARY_IN_CURRENT_ROOM_MODE) {
            boolean stationaryPhaseFinished = core.SimClock
                    .getTime() >= (this.lectureSlot * this.stationaryPhaseDuration);
            if (stationaryPhaseFinished) {
                this.mapRouteMM.setLocation(getCurrentMovementModel().getLastLocation());
                setCurrentMovementModel(mapRouteMM);
                this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
                System.out.println(this.getHost().toString()
                        + ": Moving to door of next room: " + (this.nextRoom != null ? this.nextRoom.name : "none"));
                this.lectureSlot++;
            }
        } else if (this.currentMovementMode == EXIT_MODE) {
            System.out.println("LectureTakerMovement: Exiting, no next room defined.");
            // Exit mode, no further actions needed
            return true; // No new orders to process
        } else {
            System.out
                    .println("LectureTakerMovement: Invalid movement mode, resetting to MOVE_TO_NEXT_ROOM_DOOR_MODE.");
            this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
            setCurrentMovementModel(mapRouteMM);
            mapRouteMM.setLocation(initialGlobalEntrance.clone());
        }

        return true; // Always return true for new orders

    }
}