package movement;

import core.Coord;
import core.Settings;

public class SwitchableSimpleWaypoint extends MovementModel implements SwitchableMovement {

    private Coord lastWaypoint;
    private Coord targetWaypoint;
    private boolean isMoving;

    public SwitchableSimpleWaypoint(Settings settings) {
        super(settings);
        this.lastWaypoint = new Coord(0, 0);
        this.targetWaypoint = null;
        this.isMoving = false;
    }

    public SwitchableSimpleWaypoint(SwitchableSimpleWaypoint proto) {
        super(proto);
        this.lastWaypoint = proto.lastWaypoint;
        this.targetWaypoint = proto.targetWaypoint;
        this.isMoving = proto.isMoving;
    }

    @Override
	public Coord getLastLocation() {
		return this.lastWaypoint.clone();
	}

    @Override
	public Coord getInitialLocation() {
		return this.lastWaypoint.clone();
	}

    @Override
	public void setLocation(Coord c) {
		this.lastWaypoint = c.clone();
	}

    public void setTargetLocation(Coord c) {
        this.targetWaypoint = c.clone();
        this.isMoving = true;
    }

    @Override
	public boolean isReady() {
		return true;
	}

    @Override
    public SwitchableSimpleWaypoint replicate() {
        return new SwitchableSimpleWaypoint(this);
    }

    @Override
	public Path getPath() {
		Path p;
		p = new Path(generateSpeed());
		p.addWaypoint(this.lastWaypoint.clone());
		p.addWaypoint(this.targetWaypoint.clone());

		this.lastWaypoint = this.targetWaypoint.clone();
        this.isMoving = false;
		return p;
	}
}
