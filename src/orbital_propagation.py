#!/usr/bin/env python3
"""
Orbital Propagation for Satellite Tracking

This module propagates satellite orbits forward in time using SGP4
and converts Earth-Centered Inertial (ECI) coordinates to geographic
coordinates (latitude, longitude, altitude).

Author: AbjuniorMnea
Date: January 11, 2026
"""

from sgp4.api import Satrec, jday
from datetime import datetime, timedelta
import numpy as np
import math
from typing import List, Dict, Tuple, Optional
import sys


class OrbitalPropagator:
    """Propagate satellite orbits and calculate positions over time."""
    
    def __init__(self, satellite: Satrec):
        """
        Initialize propagator with SGP4 satellite object.
        
        Args:
            satellite: SGP4 Satrec object from TLE parser
        """
        self.satellite = satellite
        
    @staticmethod
    def datetime_to_jd(dt: datetime) -> Tuple[float, float]:
        """
        Convert Python datetime to Julian Date.
        
        Args:
            dt: Python datetime object
            
        Returns:
            Tuple of (jd, fr) where jd is Julian day integer,
            fr is fractional day
        """
        jd, fr = jday(dt.year, dt.month, dt.day, 
                      dt.hour, dt.minute, dt.second + dt.microsecond / 1e6)
        return jd, fr
    
    def propagate_single(self, dt: datetime) -> Tuple[bool, np.ndarray, np.ndarray]:
        """
        Propagate orbit to a single time point.
        
        Args:
            dt: Target datetime
            
        Returns:
            Tuple of (error_code, position_km, velocity_km_s)
            error_code: 0 if success, non-zero if error
        """
        jd, fr = self.datetime_to_jd(dt)
        
        # Propagate using SGP4
        error, position, velocity = self.satellite.sgp4(jd, fr)
        
        return error, np.array(position), np.array(velocity)
    
    def propagate_multiple(self, 
                          start_time: datetime,
                          duration_hours: float = 24.0,
                          time_step_minutes: float = 10.0) -> List[Dict]:
        """
        Propagate orbit over multiple time steps.
        
        Args:
            start_time: Starting datetime
            duration_hours: How long to propagate (hours)
            time_step_minutes: Time between samples (minutes)
            
        Returns:
            List of dicts containing time, position, velocity
        """
        results = []
        num_steps = int((duration_hours * 60) / time_step_minutes)
        
        for i in range(num_steps + 1):
            # Calculate current time
            current_time = start_time + timedelta(minutes=i * time_step_minutes)
            
            # Propagate
            error, position, velocity = self.propagate_single(current_time)
            
            if error != 0:
                print(f"Warning: Propagation error at {current_time}: code {error}")
                continue
            
            # Convert to geographic coordinates
            lat, lon, alt = self.eci_to_geodetic(position, current_time)
            
            results.append({
                'time': current_time,
                'time_str': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'position_eci_km': position,
                'velocity_eci_km_s': velocity,
                'latitude_deg': lat,
                'longitude_deg': lon,
                'altitude_km': alt,
                'speed_km_s': np.linalg.norm(velocity)
            })
        
        return results
    
    @staticmethod
    def eci_to_geodetic(position_eci: np.ndarray, dt: datetime) -> Tuple[float, float, float]:
        """
        Convert ECI coordinates to geodetic (lat, lon, alt).
        
        This is a simplified conversion using Earth rotation.
        For high precision, use libraries like pyproj or astropy.
        
        Args:
            position_eci: Position vector in ECI frame [x, y, z] km
            dt: Datetime for Earth rotation calculation
            
        Returns:
            Tuple of (latitude_deg, longitude_deg, altitude_km)
        """
        x, y, z = position_eci
        
        # Earth rotation rate (rad/s)
        omega_earth = 7.2921159e-5
        
        # Calculate Greenwich Mean Sidereal Time (simplified)
        # Reference: J2000.0 epoch
        j2000 = datetime(2000, 1, 1, 12, 0, 0)
        seconds_since_j2000 = (dt - j2000).total_seconds()
        gmst_rad = (4.894961212823756 + omega_earth * seconds_since_j2000) % (2 * math.pi)
        
        # Calculate longitude (rotate from ECI to ECEF)
        lon_rad = math.atan2(y, x) - gmst_rad
        
        # Normalize longitude to [-180, 180]
        lon_deg = math.degrees(lon_rad)
        if lon_deg > 180:
            lon_deg -= 360
        elif lon_deg < -180:
            lon_deg += 360
        
        # Calculate latitude (simplified spherical Earth)
        r_xy = math.sqrt(x**2 + y**2)
        lat_rad = math.atan2(z, r_xy)
        lat_deg = math.degrees(lat_rad)
        
        # Calculate altitude
        # Earth equatorial radius (km)
        r_earth = 6378.137
        r_satellite = math.sqrt(x**2 + y**2 + z**2)
        alt_km = r_satellite - r_earth
        
        return lat_deg, lon_deg, alt_km
    
    def calculate_orbital_period(self) -> float:
        """
        Calculate orbital period in minutes.
        
        Returns:
            Period in minutes
        """
        # Mean motion is in rad/min
        mean_motion = self.satellite.no_kozai  # rad/min
        period_minutes = (2 * math.pi) / mean_motion
        return period_minutes
    
    def get_current_position(self) -> Dict:
        """
        Get current position (right now).
        
        Returns:
            Dict with current position data
        """
        current_time = datetime.utcnow()
        results = self.propagate_multiple(current_time, 
                                         duration_hours=0, 
                                         time_step_minutes=0)
        return results[0] if results else None


def print_propagation_results(results: List[Dict], show_all: bool = False):
    """
    Print propagation results in readable format.
    
    Args:
        results: List of propagation results
        show_all: If True, print all results. If False, print summary + first/last few
    """
    if not results:
        print("No results to display")
        return
    
    print("\n" + "="*80)
    print("ORBITAL PROPAGATION RESULTS")
    print("="*80)
    print(f"\nTotal time points: {len(results)}")
    print(f"Time span: {results[0]['time_str']} to {results[-1]['time_str']}")
    
    # Calculate average altitude
    avg_alt = np.mean([r['altitude_km'] for r in results])
    print(f"Average altitude: {avg_alt:.2f} km")
    
    print("\n" + "-"*80)
    print(f"{'Time (UTC)':<20} {'Lat (°)':<10} {'Lon (°)':<10} {'Alt (km)':<10} {'Speed (km/s)':<12}")
    print("-"*80)
    
    if show_all:
        # Print all results
        for r in results:
            print(f"{r['time_str']:<20} {r['latitude_deg']:>8.3f}° "
                  f"{r['longitude_deg']:>8.3f}° {r['altitude_km']:>9.2f} "
                  f"{r['speed_km_s']:>11.3f}")
    else:
        # Print first 3, middle 1, last 3
        for r in results[:3]:
            print(f"{r['time_str']:<20} {r['latitude_deg']:>8.3f}° "
                  f"{r['longitude_deg']:>8.3f}° {r['altitude_km']:>9.2f} "
                  f"{r['speed_km_s']:>11.3f}")
        
        if len(results) > 7:
            print(f"{'...':<20} {'...':<10} {'...':<10} {'...':<10} {'...':<12}")
            mid = len(results) // 2
            r = results[mid]
            print(f"{r['time_str']:<20} {r['latitude_deg']:>8.3f}° "
                  f"{r['longitude_deg']:>8.3f}° {r['altitude_km']:>9.2f} "
                  f"{r['speed_km_s']:>11.3f}")
            print(f"{'...':<20} {'...':<10} {'...':<10} {'...':<10} {'...':<12}")
        
        for r in results[-3:]:
            print(f"{r['time_str']:<20} {r['latitude_deg']:>8.3f}° "
                  f"{r['longitude_deg']:>8.3f}° {r['altitude_km']:>9.2f} "
                  f"{r['speed_km_s']:>11.3f}")
    
    print("="*80 + "\n")


def main():
    """Main execution function."""
    # Import TLE parser
    try:
        from tle_parser import TLEParser
    except ImportError:
        print("Error: Could not import TLEParser. Make sure tle_parser.py is in the same directory.")
        sys.exit(1)
    
    # Default parameters
    tle_file = "iss_tle.txt"
    duration_hours = 24.0
    time_step_minutes = 30.0  # 30-minute intervals
    show_all = False
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        tle_file = sys.argv[1]
    if len(sys.argv) > 2:
        duration_hours = float(sys.argv[2])
    if len(sys.argv) > 3:
        time_step_minutes = float(sys.argv[3])
    if len(sys.argv) > 4 and sys.argv[4].lower() == 'all':
        show_all = True
    
    try:
        # Parse TLE
        print(f"\nParsing TLE from: {tle_file}")
        parser = TLEParser(tle_file)
        satellite = parser.parse_tle()
        
        print(f"Satellite: {parser.satellite_name}")
        
        # Create propagator
        propagator = OrbitalPropagator(satellite)
        
        # Calculate orbital period
        period = propagator.calculate_orbital_period()
        print(f"Orbital period: {period:.2f} minutes ({period/60:.2f} hours)")
        
        # Propagate orbit
        print(f"\nPropagating orbit for {duration_hours} hours with {time_step_minutes}-minute steps...")
        start_time = datetime.utcnow()
        results = propagator.propagate_multiple(start_time, duration_hours, time_step_minutes)
        
        # Display results
        print_propagation_results(results, show_all)
        
        # Save to file (optional)
        output_file = "outputs/propagation_results.txt"
        try:
            with open(output_file, 'w') as f:
                f.write("Time (UTC),Latitude (deg),Longitude (deg),Altitude (km),Speed (km/s)\n")
                for r in results:
                    f.write(f"{r['time_str']},{r['latitude_deg']:.6f},"
                           f"{r['longitude_deg']:.6f},{r['altitude_km']:.6f},"
                           f"{r['speed_km_s']:.6f}\n")
            print(f"Results saved to: {output_file}")
        except Exception as e:
            print(f"Could not save to file: {e}")
        
        return results
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    results = main()
