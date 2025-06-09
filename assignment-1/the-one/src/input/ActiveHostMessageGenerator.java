package input;

import core.DTNHost;
import core.Settings;
import core.SimScenario;

public class ActiveHostMessageGenerator
    extends SingleMessageGenerator {
  public ActiveHostMessageGenerator(Settings s) {
    super(s);
  }

  @Override
  protected int drawHostAddress(int[] hostRange) {
    boolean isActive;
    int hostID;
    var hosts = SimScenario.getInstance().getHosts();
    var hasActiveHosts = hosts.stream().anyMatch(DTNHost::isMovementActive);
    if (!hasActiveHosts) {
      return -1; // no active nodes
    }
    do {
      hostID = super.drawHostAddress(hostRange);
      int finalHostID = hostID; // for lambda expression
      // if we drew a host that does not exist, the user has supplied a wrong range
      var host = hosts.parallelStream().filter(h -> h.getAddress() == finalHostID).findFirst().orElseThrow();
      isActive = host.isMovementActive();
    } while (!isActive);

    return hostID;
  }

  @Override
  protected int drawToAddress(int[] hostRange, int from) {

    boolean isActive;
    int hostID;
    var hosts = SimScenario.getInstance().getHosts();
    var hasActiveHosts = hosts.stream().anyMatch(DTNHost::isMovementActive);
    if (!hasActiveHosts) {
      return -1; // no active nodes
    }
    do {
      hostID = super.drawToAddress(hostRange, from);
      int finalHostID = hostID; // for lambda expression
      // if we drew a host that does not exist, the user has supplied a wrong range
      var host = hosts.parallelStream().filter(h -> h.getAddress() == finalHostID).findFirst().orElseThrow();
      isActive = host.isMovementActive();
    } while (!isActive);

    return hostID;
  }
}
