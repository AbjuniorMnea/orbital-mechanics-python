# Build Log - January 11, 2026 - Morning Session

## What I Built:
- ✅ TLE Parser (`src/tle_parser.py`)
- ✅ Parsed ISS orbital elements successfully

## What I Learned:
- **TLE Format:** 3 lines (name + 2 data lines)
- **SGP4 Library:** Industry standard for satellite propagation
- **Orbital Elements:**
  - Inclination: Orbit tilt relative to equator (ISS = 51.64°)
  - RAAN: Where orbit crosses equator going north
  - Eccentricity: Orbit shape (0 = circle, ISS ≈ 0.0006)
  - Mean Motion: Orbits per day (ISS ≈ 15.5)

## Challenges:
- **Mean Motion Conversion:** Initially got wrong units (rad/min vs revs/day)
- **Solution:** Conversion formula: `rad/min * 1440 / (2π)` = revs/day

## Screenshots:
![alt text](TLE_parser.png)

## Next: Orbital Propagation Script
## Afternoon Session (Part 1): Orbital Propagation

### What I Built:
- ✅ Orbital Propagation Script (`src/orbital_propagation.py`)
- ✅ Calculated ISS position over 24 hours
- ✅ Generated CSV output with 49 position points

### What I Learned:
- **Orbital Propagation:** Predicting satellite position over time
- **Coordinate Systems:**
  - ECI (Earth-Centered Inertial): Fixed to stars
  - ECEF (Earth-Centered Earth-Fixed): Rotates with Earth
  - Geodetic: Lat/Lon/Alt
- **ISS Orbital Period:** 92.65 minutes (15.5 orbits/day)
- **Orbital Speed:** 7.69 km/s (27,600 km/h!)
- **Greenwich Mean Sidereal Time (GMST):** Tracks Earth rotation

### Challenges:
- **Coordinate Transformation:** Converting ECI to lat/lon requires accounting for Earth rotation
- **Solution:** Used GMST to rotate coordinates from inertial frame to Earth-fixed frame
- **Datetime Handling:** SGP4 uses Julian Date format, needed conversion

### Output:
- Terminal table showing 49 positions across 24 hours
- CSV file: `outputs/propagation_results.txt` (for plotting/analysis)

### Screenshots:
![alt text](<Parsing TLE from iss_tle.png>)