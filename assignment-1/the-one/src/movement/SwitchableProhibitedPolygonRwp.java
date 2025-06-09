package movement;

import core.Coord;
import core.Settings;

import java.util.Arrays;
import java.util.List;

/**
 * Random Waypoint Movement with a prohibited region where nodes may not move
 * into. The polygon is defined by a *closed* (same point as first and
 * last) path, represented as a list of {@code Coord}s.
 *
 * @author teemuk
 */
public class SwitchableProhibitedPolygonRwp
    extends MovementModel implements SwitchableMovement {

  // ==========================================================================//
  // Settings
  // ==========================================================================//
  /** {@code true} to confine nodes inside the polygon */
  public static final String INVERT_SETTING = "rwpInvert";
  public static final boolean INVERT_DEFAULT = true;
  // ==========================================================================//

  // ==========================================================================//
  // Instance vars
  // ==========================================================================//
  public List<Coord> polygon = Arrays.asList();

  private Coord lastWaypoint;
  /** Inverted, i.e., only allow nodes to move inside the polygon. */
  public final boolean invert;
  // ==========================================================================//

  // ==========================================================================//
  // Implementation
  // ==========================================================================//
  @Override
  public Path getPath() {
    // Creates a new path from the previous waypoint to a new one.
    final Path p;
    p = new Path(super.generateSpeed());
    p.addWaypoint(this.lastWaypoint.clone());

    // Add only one point. An arbitrary number of Coords could be added to
    // the path here and the simulator will follow the full path before
    // asking for the next one.
    Coord c;
    do {
      c = this.randomCoord();
    } while (pathIntersects(this.polygon, this.lastWaypoint, c));
    p.addWaypoint(c);

    this.lastWaypoint = c;
    return p;
  }

  @Override
  public Coord getInitialLocation() {
    do {
      this.lastWaypoint = this.randomCoord();
    } while ((this.invert) ? isOutside(polygon, this.lastWaypoint) : isInside(this.polygon, this.lastWaypoint));
    return this.lastWaypoint;
  }

  @Override
  public void setLocation(Coord lastWaypoint) {
    this.lastWaypoint = lastWaypoint.clone();
  }

  @Override
  public Coord getLastLocation() {
    return this.lastWaypoint.clone();
  }

  @Override
  public MovementModel replicate() {
    return new SwitchableProhibitedPolygonRwp(this);
  }

  private Coord randomCoord() {
    return new Coord(
        rng.nextDouble() * super.getMaxX(),
        rng.nextDouble() * super.getMaxY());
  }
  // ==========================================================================//

  // ==========================================================================//
  // API
  // ==========================================================================//
  public SwitchableProhibitedPolygonRwp(final Settings settings) {
    super(settings);
    // Read the invert setting
    this.invert = settings.getBoolean(INVERT_SETTING, INVERT_DEFAULT);
  }

  public SwitchableProhibitedPolygonRwp(SwitchableProhibitedPolygonRwp other) {
    // Copy constructor will be used when settings up nodes. Only one
    // prototype node instance in a group is created using the Settings
    // passing constructor, the rest are replicated from the prototype.
    super(other);
    // Remember to copy any state defined in this class.
    this.invert = other.invert;
    this.polygon = other.polygon; // Ensure polygon is copied
  }

  public void setPolygon(final List<Coord> polygon) {
    this.polygon = polygon;
  }
  // ==========================================================================//

  // ==========================================================================//
  // Private - geometry
  // ==========================================================================//
  private static boolean pathIntersects(
      final List<Coord> polygon,
      final Coord start,
      final Coord end) {
    final int count = countIntersectedEdges(polygon, start, end);
    return (count > 0);
  }

  private static boolean isInside(
      final List<Coord> polygon,
      final Coord point) {
    final int count = countIntersectedEdges(polygon, point,
        new Coord(-10, 0));
    return ((count % 2) != 0);
  }

  private static boolean isOutside(
      final List<Coord> polygon,
      final Coord point) {
    return !isInside(polygon, point);
  }

  private static int countIntersectedEdges(
      final List<Coord> polygon,
      final Coord start,
      final Coord end) {
    int count = 0;
    for (int i = 0; i < polygon.size() - 1; i++) {
      final Coord polyP1 = polygon.get(i);
      final Coord polyP2 = polygon.get(i + 1);

      final Coord intersection = intersection(start, end, polyP1, polyP2);
      if (intersection == null)
        continue;

      if (isOnSegment(polyP1, polyP2, intersection)
          && isOnSegment(start, end, intersection)) {
        count++;
      }
    }
    return count;
  }

  private static boolean isOnSegment(
      final Coord L0,
      final Coord L1,
      final Coord point) {
    final double crossProduct = (point.getY() - L0.getY()) * (L1.getX() - L0.getX())
        - (point.getX() - L0.getX()) * (L1.getY() - L0.getY());
    if (Math.abs(crossProduct) > 0.0000001)
      return false;

    final double dotProduct = (point.getX() - L0.getX()) * (L1.getX() - L0.getX())
        + (point.getY() - L0.getY()) * (L1.getY() - L0.getY());
    if (dotProduct < 0)
      return false;

    final double squaredLength = (L1.getX() - L0.getX()) * (L1.getX() - L0.getX())
        + (L1.getY() - L0.getY()) * (L1.getY() - L0.getY());
    if (dotProduct > squaredLength)
      return false;

    return true;
  }

  private static Coord intersection(
      final Coord L0_p0,
      final Coord L0_p1,
      final Coord L1_p0,
      final Coord L1_p1) {
    final double[] p0 = getParams(L0_p0, L0_p1);
    final double[] p1 = getParams(L1_p0, L1_p1);
    final double D = p0[1] * p1[0] - p0[0] * p1[1];
    if (D == 0.0)
      return null;

    final double x = (p0[2] * p1[1] - p0[1] * p1[2]) / D;
    final double y = (p0[2] * p1[0] - p0[0] * p1[2]) / D;

    return new Coord(x, y);
  }

  private static double[] getParams(
      final Coord c0,
      final Coord c1) {
    final double A = c0.getY() - c1.getY();
    final double B = c0.getX() - c1.getX();
    final double C = c0.getX() * c1.getY() - c0.getY() * c1.getX();
    return new double[] { A, B, C };
  }

  @Override
  public boolean isReady() {
    return true;

  }
  // ==========================================================================//
}
