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
  public ExternalEvent nextEvent() {
		int responseSize = 0; /* zero stands for one way messages */
		int msgSize;
		int interval;
    int pollingInterval = 1;
		int from;
		int to;

		/* Get two *different* nodes randomly from the host ranges */
		from = drawHostAddress(this.hostRange);
		to = drawToAddress(hostRange, from);

		msgSize = drawMessageSize();
		interval = drawNextEventTimeDiff();

		/* Create event and advance to next event */
    // Create a dummy event if there are no active hosts
    if (from == -1 || to == -1) {
      this.nextEventsTime += pollingInterval;
      return new ExternalEvent(this.nextEventsTime);
    }
      
		MessageCreateEvent mce = new MessageCreateEvent(from, to, this.getID(),
				msgSize, responseSize, this.nextEventsTime);
		this.nextEventsTime += interval;

		if (this.msgTime != null && this.nextEventsTime > this.msgTime[1]) {
			/* next event would be later than the end time */
			this.nextEventsTime = Double.MAX_VALUE;
		}

		return mce;
	}

  @Override
  protected int drawHostAddress(int[] hostRange) {
    boolean isActive;
    int hostID;
    var hosts = SimScenario.getInstance().getHosts();
    var hasEnoughActiveHosts = hosts.stream().filter(DTNHost::isMovementActive).count() > 2;
    if (!hasEnoughActiveHosts) {
       return -1; // no active nodes available for message transfer: we need two active distinct hosts
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
    var hasEnoughActiveHosts = hosts.stream().filter(DTNHost::isMovementActive).count() > 2;
    if (!hasEnoughActiveHosts) {
        return -1; // no active nodes available for message transfer: we need two active distinct hosts
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
