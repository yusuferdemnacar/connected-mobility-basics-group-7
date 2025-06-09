package util;

import core.Coord;

import java.util.ArrayList;
import java.util.List;

// Helper class to store room dimensions
public class Room {
    private String name;
    private List<Coord> polygon;

    public Room(String filePath, String name) {
        this.name = name;
        this.polygon = readPolygon(filePath);
        if (polygon.isEmpty()) {
            System.err.println("LectureTakerMovement: No valid polygon found in file " + filePath);
        }
    }

    public String getName() {
        return name;
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

    public List<Coord> getPolygon() {
        return polygon;
    }

    private class Line {
        private Coord start;
        private Coord end;

        public Line(Coord start, Coord end) {
            this.start = start;
            this.end = end;
        }

        public Coord getStart() {
            return start;
        }

        public Coord getEnd() {
            return end;
        }

        private boolean lineIntersectsSegment(Line segment) {
            double distance1 = this.getStart().distance(this.getEnd());
            double distance2 = segment.getStart().distance(segment.getEnd());

            if (distance1 == 0 || distance2 == 0) {
                return false;
            }

            // Coordinates x1, y1, x2 and y2 designate the start and end point of the line
            // Coordinates x3, y3, x4 and y4 designate the start and end point of the
            // (polygon) segment
            double x1 = this.getStart().getX();
            double x2 = this.getEnd().getX();
            double x3 = segment.getStart().getX();
            double x4 = segment.getEnd().getX();
            double y1 = this.getStart().getY();
            double y2 = this.getEnd().getY();
            double y3 = segment.getStart().getY();
            double y4 = segment.getEnd().getY();

            double denominator = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1);

            // Lines are parallel
            if (denominator == 0) {
                return false;
            }

            double ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denominator;
            double ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denominator;

            // is the intersection along the segments
            if (ua < 0 || ua > 1 || ub < 0 || ub > 1) {
                return false;
            }

            // // Return a object with the x and y coordinates of the intersection
            // let x = x1 + ua * (x2 - x1)
            // let y = y1 + ua * (y2 - y1)

            // return {x, y}

            // just return true for now
            return true;
        }
    }

    public boolean lineBetweenCoordsIntersectsRoom(Coord p1, Coord p2) {
        if (polygon.isEmpty() || polygon.size() < 2) {
            System.err.println("Cannot calculate line intersection with room: room has less than two points");
            return false;
        }

        Line line = new Line(p1, p2);

        // map polygon to lines
        // TODO: not efficient, not pretty, should be made better, but easy for now
        Coord last = polygon.getFirst();
        for (int i = 1; i < polygon.size(); i++) {
            Coord previousPoint = polygon.get(i - 1);
            Coord current = polygon.get(i);
            last = current;

            Line segment = new Line(previousPoint, current);
            if (line.lineIntersectsSegment(segment)) {
                return true;
            }
        }

        Line segment = new Line(last, polygon.getFirst());

        return line.lineIntersectsSegment(segment);
    }
}
