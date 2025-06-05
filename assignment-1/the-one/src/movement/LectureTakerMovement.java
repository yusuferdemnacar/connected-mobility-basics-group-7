package movement; // Or your appropriate package

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import core.Coord;
import core.Settings;

public class LectureTakerMovement extends ExtendedMovementModel {

    // Namespace for LectureTakerMovement specific global settings
    public static final String LECTURE_TAKER_MOVEMENT_NS = "LectureTakerMovement";

    public static final String INITIAL_X = "initialX";
    public static final String INITIAL_Y = "initialY";
    public static final String START_TIME = "startTime";
    public static final String END_TIME = "endTime";
    // New settings keys for durations
    public static final String LECTURE_PERIOD_DURATION_SETTING = "lecturePeriodDuration";

    private Settings ltmSettings;

    private ArrayList<String> roomSequence;
    private HashMap<String, Room> rooms = new HashMap<>();

    private Coord initialGlobalEntrance;
    private Room currentRoom;
    private Room nextRoom;
    private int lectureSlot;

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
                int lineNumber = 0;
                while ((line = reader.readLine()) != null) {
                    if (lineNumber < 2) {
                        lineNumber++;
                        continue;
                    }
                    String[] parts = line.substring(line.indexOf('(') + 1, line.indexOf(')')).split("\\s+");
                    double x = Double.parseDouble(parts[0]);
                    double y = Double.parseDouble(parts[1]);
                    x = Math.round(x * 1000.0) / 1000.0;
                    y = Math.round(y * 1000.0) / 1000.0;
                    coords.add(new Coord(x, y));
                }
                if (!coords.isEmpty()) {
                    coords.add(coords.get(0).clone());
                }
            } catch (Exception e) {
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

        this.lecturePeriodDuration = ltmSettings.getDouble(LECTURE_PERIOD_DURATION_SETTING, 7200);

        this.currentMovementMode = START_MODE;

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
        this.lecturePeriodDuration = proto.lecturePeriodDuration;
        this.stationaryMM = new SwitchableStationaryMovement(proto.stationaryMM);
        this.randomWaypointMM = new SwitchableProhibitedPolygonRwp(proto.randomWaypointMM);
        this.mapRouteMM = new MapRouteMovement(proto.mapRouteMM);
        this.lectureSlot = proto.lectureSlot;
        this.ltmSettings = proto.ltmSettings;
        this.stationaryMM.setLocation(this.initialGlobalEntrance.clone());
        setCurrentMovementModel(stationaryMM);
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
        if (this.currentMovementMode == START_MODE) {
            this.roomSequence = Room.getRoomSequence("data/group-data/" + this.getHost().groupId + "_room_sequence.txt");

            for (int i = 0; i < roomSequence.size(); i++) {
                String roomName = roomSequence.get(i);
                if (!this.rooms.containsKey(roomName)) {
                    String filePath = this.ltmSettings.getSetting(roomName + ".file", null);
                    Room room = new Room(filePath, roomName);
                    rooms.put(roomName, room);
                }
                
                this.currentRoom = null;
                this.nextRoom = rooms.get(roomSequence.get(0));

                this.mapRouteMM.setLocation(initialGlobalEntrance.clone());
                setCurrentMovementModel(mapRouteMM);
                this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
            }
        } else if (this.currentMovementMode == MOVE_TO_NEXT_ROOM_DOOR_MODE) {

            if (this.nextRoom == null) {
                this.stationaryMM.setLocation(getCurrentMovementModel().getLastLocation());
                setCurrentMovementModel(stationaryMM);
                this.currentMovementMode = EXIT_MODE;
            } else {
                if (this.mapRouteMM.isReady()) {
                    this.currentRoom = this.nextRoom;
                    this.randomWaypointMM.setPolygon(currentRoom.polygon);
                    this.randomWaypointMM.setLocation(getCurrentMovementModel().getLastLocation());
                    setCurrentMovementModel(randomWaypointMM);
                    if (this.currentRoom.name.equals("magistrale")) {
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
            if (core.SimClock.getTime() >= (this.lectureSlot * this.lecturePeriodDuration)) {
                if (this.lectureSlot < this.roomSequence.size()) {
                    this.nextRoom = this.rooms.get(this.roomSequence.get(this.lectureSlot));
                } else {
                    this.nextRoom = null;
                }
                this.mapRouteMM.setLocation(getCurrentMovementModel().getLastLocation());
                setCurrentMovementModel(mapRouteMM);
                this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
                this.lectureSlot++;
            }
        } else if (this.currentMovementMode == ROAMING_IN_MAGISTRALE_MODE) {
            if (core.SimClock.getTime() >= (this.lectureSlot * this.lecturePeriodDuration)) {
                if (this.lectureSlot < this.roomSequence.size()) {
                    this.nextRoom = this.rooms.get(this.roomSequence.get(this.lectureSlot));
                } else {
                    this.nextRoom = null;
                }
                if (this.nextRoom != null && this.nextRoom.name.equals("magistrale")) {
                    this.mapRouteMM.getPath();
                } else {
                    this.mapRouteMM.setLocation(getCurrentMovementModel().getLastLocation());
                    setCurrentMovementModel(mapRouteMM);
                    this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
                }
                this.lectureSlot++;
            }
        } else if (this.currentMovementMode == EXIT_MODE) {
            System.out.println("LectureTakerMovement: Exiting, no next room defined.");
        } else {
            System.out.println("LectureTakerMovement: Invalid movement mode, resetting to MOVE_TO_NEXT_ROOM_DOOR_MODE.");
            this.currentMovementMode = MOVE_TO_NEXT_ROOM_DOOR_MODE;
            setCurrentMovementModel(mapRouteMM);
            mapRouteMM.setLocation(initialGlobalEntrance.clone());
        }

        return true;

    }
}