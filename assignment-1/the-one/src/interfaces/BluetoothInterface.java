package interfaces;

import core.*;
import util.Room;

import java.util.Collection;

// loosely based on bluetooth 5.0, but only in direct line of sight
public class BluetoothInterface extends NetworkInterface {
    /**
     * Maximum number of parallel connections allowed -setting id ({@value} ).
     */
    public static final String PARALLEL_CONNECTIONS_S = "maximumParallelConnections";

    protected final int maximumParallelConnections;

    /**
     * Reads the interface settings from the Settings file
     */
    public BluetoothInterface(Settings s) {
        super(s);
        maximumParallelConnections = s.getInt(PARALLEL_CONNECTIONS_S);
    }

    /**
     * Copy constructor
     * 
     * @param ni the copied network interface object
     */
    public BluetoothInterface(BluetoothInterface ni) {
        super(ni);
        maximumParallelConnections = ni.maximumParallelConnections;
    }

    public NetworkInterface replicate() {
        return new BluetoothInterface(this);
    }

    /**
     * Tries to connect this host to another host. The other host must be
     * active, within range of this host, and have a clear line of sight of it for
     * the connection to succeed.
     * For simplification, assume both hosts are constrained to support a maximum
     * amount of parallel connections, and that all network interfaces are
     * Bluetooth interface (as in the simulation this is the case)
     * 
     * @param anotherInterface The interface to connect to
     */
    public void connect(NetworkInterface anotherInterface) {
        if (isScanning()
                && anotherInterface.getHost().isRadioActive()
                && isWithinRange(anotherInterface)
                && !isConnected(anotherInterface)
                && (this != anotherInterface)
                && (haveConnectionCapacity(anotherInterface))) {
            // perform costly line of sight check only if all the other conditions hold
            boolean hasClearLineOfSight = hasFreeLineOfSight(this.getHost(), anotherInterface.getHost());

            if (hasClearLineOfSight) {
                Connection con = new VBRConnection(this.host, this,
                        anotherInterface.getHost(), anotherInterface);
                connect(con, anotherInterface);
            }
        }
    }

    private boolean haveConnectionCapacity(NetworkInterface anotherInterface) {
        // assume the other interface is also BluetoothInterface
        // as this function is only called unidirectionally
        return this.connections.size() < this.maximumParallelConnections
                && anotherInterface.getConnections().size() < this.maximumParallelConnections;
    }

    /**
     * Updates the state of current connections (i.e. tears down connections
     * that are out of range and creates new ones).
     */
    public void update() {
        if (optimizer == null) {
            return; /* nothing to do */
        }

        // First break the old ones
        optimizer.updateLocation(this);
        for (int i = 0; i < this.connections.size();) {
            Connection con = this.connections.get(i);
            NetworkInterface anotherInterface = con.getOtherInterface(this);

            // all connections should be up at this stage
            assert con.isUp() : "Connection " + con + " was down!";
            DTNHost from = this.getHost();
            DTNHost to = anotherInterface.getHost();
            if (!isWithinRange(anotherInterface) || !hasFreeLineOfSight(from, to)) {
                disconnect(con, anotherInterface);
                connections.remove(i);
            } else {
                i++;
            }
        }
        // Then find new possible connections
        Collection<NetworkInterface> interfaces = optimizer.getNearInterfaces(this);
        for (NetworkInterface i : interfaces) {
            connect(i);
        }

        /* update all connections */
        for (Connection con : getConnections()) {
            con.update();
        }
    }

    private boolean hasFreeLineOfSight(DTNHost from, DTNHost to) {
        var hostLocation = from.getLocation();
        var otherLocation = to.getLocation();
        return isFreePath(hostLocation, otherLocation);
    }

    /**
     * Creates a connection to another host. This method does not do any checks
     * on whether the other node is in range or active
     * 
     * @param anotherInterface The interface to create the connection to
     */
    public void createConnection(NetworkInterface anotherInterface) {
        if (!isConnected(anotherInterface) && (this != anotherInterface)) {
            Connection con = new VBRConnection(this.host, this,
                    anotherInterface.getHost(), anotherInterface);
            connect(con, anotherInterface);
        }
    }

    /**
     * Returns the transmit speed to another interface based on the
     * distance to this interface
     * 
     * @param ni The other network interface
     */
    @Override
    public int getTransmitSpeed(NetworkInterface ni) {
        double distance;

        /* distance to the other interface */
        distance = ni.getLocation().distance(this.getLocation());

        if (distance >= this.transmitRange) {
            return 0;
        }

        return (int) Math.floor(BluetoothLEBitrateCalculator.getBitrateBps(distance));
    }

    /**
     * Returns a string representation of the object.
     * 
     * @return a string representation of the object.
     */
    public String toString() {
        return "BluetoothInterface " + super.toString();
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

// Disclaimer: Claude Sonnet 4 was used to write this
class BluetoothLEBitrateCalculator {

    // Constants
    public static final double MAX_BITRATE_BPS = 1_000_000.0; // 1 Mbps cap for BLE 1M PHY
    public static final double BANDWIDTH_HZ = 1_000_000.0; // 1 MHz channel bandwidth
    public static final double BITS_IN_SYMBOL = 8; // 8 bits per symbol (1 byte)
    public static final double TX_POWER_DBM = 0.0; // Transmit power in dBm
    public static final double FREQUENCY_HZ = 2.4e9; // 2.4 GHz for BLE
    public static final double PATH_LOSS_EXPONENT = 2.0; // Free space exponent
    public static final double REFERENCE_DISTANCE_M = 1.0; // Reference distance d0 in meters
    public static final double PATH_LOSS_AT_REF_DB = 40.0; // Empirical PL(d0) at 1m for 2.4 GHz
    public static final double NOISE_FLOOR_DBM = -114.0; // Noise floor (dBm) at 1 MHz BW

    // Gaussian shadowing (optional, set to 0.0 if not needed)
    public static final double SHADOWING_DB = 0.0;

    // Get path loss in dB for a given distance
    private static double getPathLoss(double distanceMeters) {
        if (distanceMeters < REFERENCE_DISTANCE_M) {
            distanceMeters = REFERENCE_DISTANCE_M;
        }
        return PATH_LOSS_AT_REF_DB + 10 * PATH_LOSS_EXPONENT * Math.log10(distanceMeters / REFERENCE_DISTANCE_M)
                + SHADOWING_DB;
    }

    // Get SNR (linear ratio) from transmit power and path loss
    private static double getSNR(double distanceMeters) {
        double receivedPower_dBm = TX_POWER_DBM - getPathLoss(distanceMeters);
        double snr_dB = receivedPower_dBm - NOISE_FLOOR_DBM;
        return Math.pow(10.0, snr_dB / 10.0); // Convert from dB to linear
    }

    // Compute bitrate using Shannon capacity (bps), capped at 1 Mbps
    public static double getBitrateBps(double distanceMeters) {
        double snr = getSNR(distanceMeters);
        double capacity = BANDWIDTH_HZ * Math.log(1 + snr) / Math.log(BITS_IN_SYMBOL); // Shannon capacity
        double distanceRatio = Math.min(REFERENCE_DISTANCE_M / distanceMeters, 1.0); // adjust capacity based on 1 Mb/s
                                                                                     // at 1m reference distance for
                                                                                     // BLE 1M PHY
        capacity *= distanceRatio;
        return capacity;
    }

    // Convenience: convert to kilobytes per second
    public static double getBitrateKiloBytesPerSec(double distanceMeters) {
        return getBitrateBps(distanceMeters) / 8.0 / 1000.0;
    }

    public static void main(String[] args) {
        for (int d = 0; d <= 200; d += 20) {
            double kbps = BluetoothLEBitrateCalculator.getBitrateKiloBytesPerSec(d);
            System.out.printf("%dm,%.0fkB/s%n", d, kbps);
        }
    }
}