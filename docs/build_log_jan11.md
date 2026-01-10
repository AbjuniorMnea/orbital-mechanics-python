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
![alt text]({TLE_parser}.png)

## Next: Orbital Propagation Script
