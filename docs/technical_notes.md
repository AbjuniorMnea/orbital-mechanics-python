# Technical Documentation - Orbital Mechanics Concepts

## Overview

This document provides deeper technical explanations of the orbital mechanics concepts and algorithms used in this project.

---

## 1. Two-Line Element (TLE) Format

### Structure

TLE data consists of three lines:
```
Line 0: Satellite name
Line 1: Catalog number, epoch, ballistic coefficient, element set number
Line 2: Inclination, RAAN, eccentricity, argument of perigee, mean anomaly, mean motion
```

### Example (ISS):
```
ISS (ZARYA)
1 25544U 98067A   24010.50000000  .00016717  00000-0  10270-3 0  9005
2 25544  51.6400 208.9163 0006317  69.9862  25.2906 15.54225995227020
```

### Field Breakdown (Line 2):
- **51.6400**: Inclination (degrees) - orbit tilt relative to equator
- **208.9163**: RAAN (degrees) - where orbit crosses equator going north
- **0006317**: Eccentricity (no decimal point) - orbit shape (0 = circle, 1 = parabola)
- **69.9862**: Argument of perigee (degrees) - orientation of ellipse
- **25.2906**: Mean anomaly (degrees) - position in orbit at epoch
- **15.54225995**: Mean motion (revs/day) - orbital frequency

---

## 2. SGP4 Propagation Algorithm

### What is SGP4?

**SGP4 (Simplified General Perturbations 4)** is the standard algorithm for propagating Low Earth Orbit (LEO) satellites using TLE data.

### Why SGP4?

- Accounts for atmospheric drag
- Models Earth's oblateness (J2 perturbation)
- Computationally efficient
- Industry standard (used by NORAD/Space Command)

### Perturbations Modeled:

1. **Earth's oblateness (J2):** Earth bulges at equator, causing RAAN drift
2. **Atmospheric drag:** Slows satellite, circularizes orbit
3. **Solar radiation pressure:** Minor effect for LEO
4. **Third-body gravity:** Moon/Sun effects (minimal for LEO)

### Not Modeled:

- High-fidelity gravity field (J3, J4, etc.)
- Solar activity variations
- Precise atmospheric density
- General relativity effects

**Result:** SGP4 is accurate for ~1 week from TLE epoch, degrades beyond that.

---

## 3. Coordinate Systems

### Earth-Centered Inertial (ECI)

**Definition:** Origin at Earth center, axes fixed to stars (not rotating with Earth)

**Properties:**
- X-axis: Points to vernal equinox (First Point of Aries)
- Z-axis: North celestial pole
- Y-axis: Right-hand rule completion

**Use:** SGP4 outputs position/velocity in ECI frame

**Units:** Typically kilometers (km) for position, km/s for velocity

### Earth-Centered Earth-Fixed (ECEF)

**Definition:** Origin at Earth center, axes rotate with Earth

**Properties:**
- X-axis: Equator and Prime Meridian (0° longitude)
- Z-axis: North pole
- Y-axis: 90° East longitude

**Use:** Intermediate step in coordinate transformation

### Geodetic (Latitude, Longitude, Altitude)

**Definition:** Surface-referenced coordinates

**Components:**
- **Latitude:** Angle north/south of equator (-90° to +90°)
- **Longitude:** Angle east/west of Prime Meridian (-180° to +180°)
- **Altitude:** Height above reference ellipsoid (WGS84)

**Use:** Human-readable position, mapping, ground track plotting

---

## 4. Coordinate Transformations

### ECI to ECEF

**Rotation by Greenwich Mean Sidereal Time (GMST):**

```
ECEF = Rz(-GMST) × ECI
```

Where `Rz(θ)` is rotation matrix about Z-axis:
```
[cos(θ)  -sin(θ)   0]
[sin(θ)   cos(θ)   0]
[  0        0      1]
```

**GMST Calculation (simplified):**
```python
J2000_epoch = Jan 1, 2000, 12:00 UTC
seconds_since_J2000 = (current_time - J2000_epoch).total_seconds()
omega_earth = 7.2921159e-5  # rad/s (Earth rotation rate)
GMST = 4.894961 + omega_earth * seconds_since_J2000  # radians
```

### ECEF to Geodetic

**Simplified spherical approximation (used in this project):**
```python
x, y, z = ECEF coordinates
r_equator = sqrt(x² + y²)

latitude = atan2(z, r_equator)
longitude = atan2(y, x)
altitude = sqrt(x² + y² + z²) - R_earth
```

**High-precision method (not implemented here):**
- Iterative solution accounting for Earth ellipsoid (WGS84)
- Handles Earth's equatorial bulge (21 km difference)
- Required for precision applications (GPS, surveying)

---

## 5. Orbital Period Calculation

**From mean motion (n):**
```
Period (minutes) = 2π / n
```

Where `n` is mean motion in radians/minute.

**Example (ISS):**
- Mean motion: 15.54 revs/day
- Convert: 15.54 rev/day × (2π rad/rev) / (1440 min/day) = 0.0678 rad/min
- Period: 2π / 0.0678 = 92.65 minutes

**Alternatively, from altitude:**
```
T = 2π × sqrt(a³ / μ)
```
Where:
- `a` = semi-major axis (km)
- `μ` = Earth's gravitational parameter (398600 km³/s²)

---

## 6. Ground Track Geometry

### Why Sinusoidal Shape?

The ground track appears sinusoidal because:

1. **Satellite orbits in plane:** Fixed inclination relative to equator
2. **Earth rotates beneath orbit:** Creates apparent westward motion
3. **Projection onto 2D map:** Great circle on sphere → sinusoid on flat map

### Latitude Bounds

**Maximum latitude = Inclination**

For ISS (51.6° inclination):
- Northernmost point: 51.6°N
- Southernmost point: 51.6°S

**Coverage area:** Between ±51.6° latitude (68% of Earth's surface)

### Westward Shift

**Earth rotates ~25° during one ISS orbit:**
```
Earth rotation: 360° / 24 hours = 15°/hour
ISS period: 92.65 min = 1.544 hours
Shift per orbit: 15° × 1.544 = 23.16°
```

**Visible in ground track:** Each successive orbit crosses equator ~23° west of previous

---

## 7. Altitude Variations

### Why Does Altitude Change?

Even though ISS orbit is nearly circular (e ≈ 0.0006), altitude varies due to:

1. **Eccentric orbit:** Perigee (low point) vs apogee (high point)
2. **Reference ellipsoid:** Altitude measured from WGS84, which varies with latitude
3. **Coordinate approximations:** Spherical Earth assumption introduces ~1% error

### Typical ISS Altitude Range

- **Nominal:** ~420 km
- **Observed in data:** 365-370 km (depends on TLE epoch and reboost schedule)
- **Decay rate:** ~100 m/day without reboost (atmospheric drag)

---

## 8. Error Sources & Limitations

### Propagation Accuracy

| Time from TLE Epoch | Expected Error | Cause |
|---------------------|---------------|-------|
| 0-24 hours | <1 km | Minimal |
| 1-7 days | 1-5 km | Atmospheric density uncertainty |
| >7 days | >10 km | Drag model errors, unmodeled perturbations |

### Coordinate Transformation Accuracy

- **Simplified GMST:** ~0.1° error in longitude
- **Spherical Earth:** ~1 km altitude error
- **Good enough for:** Visualization, educational purposes
- **Not sufficient for:** Precision tracking, collision avoidance

### Recommendations for Higher Accuracy

1. Use fresh TLE data (<24 hours old)
2. Implement full WGS84 ellipsoid conversion
3. Use high-precision GMST (IAU 2000A/B models)
4. Consider atmospheric density variations
5. For critical applications: Use SGP4-XP or numerical integrators

---

## 9. Validation Methods

### Cross-Check with Known Values

**ISS Parameters (as of 2024):**
- Period: 90-93 minutes ✅
- Altitude: 400-420 km ✅
- Inclination: 51.64° ✅
- Velocity: ~7.66 km/s ✅

### Visual Inspection

- Ground track should be smooth sinusoid
- Latitude bounds should match inclination
- Westward shift should be consistent

### Online Tracking Comparison

Compare results with:
- [Heavens Above](https://www.heavens-above.com/)
- [N2YO](https://www.n2yo.com/)
- [ISS Tracker](https://www.iss-tracker.com/)

---

## 10. Extending This Project

### Adding Real-Time TLE Updates

```python
import requests

def fetch_latest_tle(satellite_id="25544"):
    """Fetch latest TLE from Celestrak."""
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={satellite_id}&FORMAT=TLE"
    response = requests.get(url)
    return response.text
```

### Ground Station Visibility

Calculate when satellite is above local horizon:

```python
def is_visible(sat_lat, sat_lon, sat_alt, 
               station_lat, station_lon,
               min_elevation=10):
    """
    Determine if satellite is visible from ground station.
    Requires: Great circle distance + elevation angle calculation
    """
    # Implementation requires spherical trigonometry
    pass
```

### Orbit Maneuver Planning

Calculate Δv required for altitude change:

```python
def hohmann_transfer(r1, r2, mu=398600):
    """
    Calculate Δv for Hohmann transfer between circular orbits.
    
    Args:
        r1: Initial orbit radius (km)
        r2: Final orbit radius (km)
        mu: Gravitational parameter (km³/s²)
    
    Returns:
        delta_v: Total Δv required (km/s)
    """
    import math
    
    # Velocities in circular orbits
    v1 = math.sqrt(mu / r1)
    v2 = math.sqrt(mu / r2)
    
    # Transfer orbit velocities
    v_transfer_1 = math.sqrt(mu * (2/r1 - 2/(r1+r2)))
    v_transfer_2 = math.sqrt(mu * (2/r2 - 2/(r1+r2)))
    
    # Total Δv
    delta_v = abs(v_transfer_1 - v1) + abs(v2 - v_transfer_2)
    return delta_v
```

---

## References

1. Vallado, D. A. (2013). *Fundamentals of Astrodynamics and Applications* (4th ed.). Microcosm Press.
2. Kelso, T. S. "Frequently Asked Questions: Two-Line Element Set Format". CelesTrak. https://celestrak.org/columns/v04n03/
3. Hoots, F. R., & Roehrich, R. L. (1980). *Spacetrack Report No. 3: Models for Propagation of NORAD Element Sets*. US Air Force.
4. Curtis, H. D. (2014). *Orbital Mechanics for Engineering Students* (3rd ed.). Butterworth-Heinemann.

---

**Last Updated:** January 11, 2026
