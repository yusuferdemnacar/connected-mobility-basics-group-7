/*
 * Copyright 2010 Aalto University, ComNet
 * Released under GPLv3. See LICENSE.txt for details.
 */
package movement;

import core.Coord;
import core.Settings;

/**
 * Random waypoint movement model. Creates zig-zag paths within the
 * simulation area.
 */
public class SwitchableRandomWaypoint extends MovementModel implements SwitchableMovement {
	/** how many waypoints should there be per path */
	private static final int PATH_LENGTH = 1;
	private Coord lastWaypoint;
	private Coord upperLeftCorner;
	private Coord lowerRightCorner;

	public SwitchableRandomWaypoint(Settings settings) {
		super(settings);
		this.upperLeftCorner = new Coord(0, 0);
		this.lowerRightCorner = new Coord(getMaxX(), getMaxY());
		this.lastWaypoint = new Coord(0, 0);
	}

	protected SwitchableRandomWaypoint(SwitchableRandomWaypoint rwp) {
		super(rwp);
		this.upperLeftCorner = rwp.upperLeftCorner.clone();
		this.lowerRightCorner = rwp.lowerRightCorner.clone();
		this.lastWaypoint = rwp.lastWaypoint.clone();
	}

	/**
	 * Returns a possible (random) placement for a host
	 * 
	 * @return Random position on the map
	 */
	@Override
	public Coord getInitialLocation() {
		assert rng != null : "MovementModel not initialized!";
		Coord c = randomCoord();

		this.lastWaypoint = c;
		return c;
	}

	@Override
	public Path getPath() {
		Path p;
		p = new Path(generateSpeed());
		p.addWaypoint(lastWaypoint.clone());
		Coord c = lastWaypoint;

		for (int i = 0; i < PATH_LENGTH; i++) {
			c = randomCoord();
			p.addWaypoint(c);
		}

		this.lastWaypoint = c;
		return p;
	}

	@Override
	public SwitchableRandomWaypoint replicate() {
		return new SwitchableRandomWaypoint(this);
	}

	protected Coord randomCoord() {
		assert rng != null : "MovementModel not initialized!";
		double x = upperLeftCorner.getX() + rng.nextDouble() * (lowerRightCorner.getX() - upperLeftCorner.getX());
		double y = upperLeftCorner.getY() + rng.nextDouble() * (lowerRightCorner.getY() - upperLeftCorner.getY());
		return new Coord(x, y);
	}

	@Override
	public void setLocation(Coord lastWaypoint) {
		this.lastWaypoint = lastWaypoint.clone();
	}

	public void setBounds(Coord upperLeft, Coord lowerRight) {
		this.upperLeftCorner = upperLeft.clone();
		this.lowerRightCorner = lowerRight.clone();
	}

	@Override
	public Coord getLastLocation() {
		return this.lastWaypoint.clone();
	}

	@Override
	public boolean isReady() {
		// For RandomWaypoint, it's always ready to generate a new path
		// or this could be tied to some condition if needed.
		return true;

	}

}
