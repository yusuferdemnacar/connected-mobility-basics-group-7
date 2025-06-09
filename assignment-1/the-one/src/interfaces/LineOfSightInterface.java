package interfaces;

import core.*;
import util.Room;

// loosely based on bluetooth 5.0
public class LineOfSightInterface extends DistanceCapacityInterface {
    /**
     * Reads the interface settings from the Settings file
     */
    public LineOfSightInterface(Settings s) {
        super(s);
    }

    @Override
    /**
     * Tries to connect this host to another host. The other host must be
     * active, within range of this host, and have a clear line of sight of it for
     * the connection to succeed.
     * 
     * @param anotherInterface The interface to connect to
     */
    public void connect(NetworkInterface anotherInterface) {
        if (isScanning()
                && anotherInterface.getHost().isRadioActive()
                && isWithinRange(anotherInterface)
                && !isConnected(anotherInterface)
                && (this != anotherInterface)) {
            // perform costly line of sight check only if all the other conditions hold
            var hostLocation = this.getHost().getLocation();
            var otherLocation = anotherInterface.getHost().getLocation();
            boolean hasClearLineOfSight = isFreePath(hostLocation, otherLocation);
            
            if (hasClearLineOfSight) {
                Connection con = new VBRConnection(this.host, this,
                        anotherInterface.getHost(), anotherInterface);
                connect(con, anotherInterface);
            }
        }
    }

    private boolean isFreePath(Coord thisHostLocation, Coord thatHostLocation) {
        // Checks if there is a room between the two hosts which would obstruct clear
        // line of sight
        for (Room room : DTNSim.allRooms) {
            boolean lineIntersectsRoom = room.lineBetweenCoordsIntersectsRoom(thisHostLocation, thatHostLocation);
            if (lineIntersectsRoom) {
                return false;
            }
        }

        return true;
    }
}