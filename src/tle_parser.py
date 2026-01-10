#!/usr/bin/env python3
"""
TLE Parser for Orbital Mechanics

This module parses Two-Line Element (TLE) data for satellites
and extracts orbital parameters using the SGP4 propagator.

Author: AbjuniorMnea
Date: January 11, 2025
"""

from sgp4.api import Satrec, WGS72
from typing import Dict, Tuple, Optional
import sys


class TLEParser:
    """Parse and extract orbital elements from TLE data."""
    
    def __init__(self, tle_file: str):
        """
        Initialize TLE parser with a TLE data file.
        
        Args:
            tle_file: Path to file containing TLE data
        """
        self.tle_file = tle_file
        self.satellite = None
        self.satellite_name = None
        
    def read_tle(self) -> Tuple[str, str, str]:
        """
        Read TLE data from file.
        
        Returns:
            Tuple of (satellite_name, line1, line2)
            
        Raises:
            FileNotFoundError: If TLE file doesn't exist
            ValueError: If TLE format is invalid
        """
        try:
            with open(self.tle_file, 'r') as f:
                lines = f.readlines()
                
            if len(lines) < 3:
                raise ValueError("TLE file must contain at least 3 lines (name + 2 TLE lines)")
            
            # Strip whitespace
            satellite_name = lines[0].strip()
            line1 = lines[1].strip()
            line2 = lines[2].strip()
            
            # Basic validation
            if not line1.startswith('1 ') or not line2.startswith('2 '):
                raise ValueError("Invalid TLE format: Lines must start with '1 ' and '2 '")
            
            return satellite_name, line1, line2
            
        except FileNotFoundError:
            raise FileNotFoundError(f"TLE file not found: {self.tle_file}")
        except Exception as e:
            raise ValueError(f"Error reading TLE file: {str(e)}")
    
    def parse_tle(self) -> Satrec:
        """
        Parse TLE data and create SGP4 satellite object.
        
        Returns:
            SGP4 Satrec object containing orbital parameters
        """
        self.satellite_name, line1, line2 = self.read_tle()
        
        # Parse TLE using SGP4
        self.satellite = Satrec.twoline2rv(line1, line2, WGS72)
        
        return self.satellite
    
    def extract_orbital_elements(self) -> Dict[str, float]:
        """
        Extract and return orbital elements from parsed TLE.
        
        Returns:
            Dictionary containing orbital parameters
        """
        if self.satellite is None:
            raise ValueError("Must call parse_tle() before extracting elements")
        
        # Extract orbital elements
        # Note: SGP4 uses specific units - document them clearly
        elements = {
            'satellite_name': self.satellite_name,
            'epoch_year': self.satellite.epochyr,
            'epoch_days': self.satellite.epochdays,
            'inclination_deg': self.satellite.inclo * 57.2958,  # Convert radians to degrees
            'raan_deg': self.satellite.nodeo * 57.2958,  # Right Ascension of Ascending Node
            'eccentricity': self.satellite.ecco,
            'argument_of_perigee_deg': self.satellite.argpo * 57.2958,
            'mean_anomaly_deg': self.satellite.mo * 57.2958,
            'mean_motion_revs_per_day': self.satellite.no_kozai * 1440.0 / (2.0 * 3.141592653589793),  # Convert rad/min to revs/day
            'bstar': self.satellite.bstar,  # Drag coefficient
        }
        
        return elements
    
    def print_orbital_elements(self):
        """Print orbital elements in human-readable format."""
        elements = self.extract_orbital_elements()
        
        print("\n" + "="*60)
        print(f"ORBITAL ELEMENTS FOR: {elements['satellite_name']}")
        print("="*60)
        print(f"\nEpoch: Year {2000 + elements['epoch_year']}, Day {elements['epoch_days']:.8f}")
        print("\nKeplerian Orbital Elements:")
        print(f"  Inclination:              {elements['inclination_deg']:.4f}°")
        print(f"  RAAN:                     {elements['raan_deg']:.4f}°")
        print(f"  Eccentricity:             {elements['eccentricity']:.7f}")
        print(f"  Argument of Perigee:      {elements['argument_of_perigee_deg']:.4f}°")
        print(f"  Mean Anomaly:             {elements['mean_anomaly_deg']:.4f}°")
        print(f"  Mean Motion:              {elements['mean_motion_revs_per_day']:.8f} revs/day")
        print(f"\nDrag Coefficient (B*):      {elements['bstar']:.8e}")
        print("="*60 + "\n")


def main():
    """Main execution function."""
    # Default TLE file
    tle_file = "iss_tle.txt"
    
    # Allow command line argument for TLE file
    if len(sys.argv) > 1:
        tle_file = sys.argv[1]
    
    try:
        # Create parser instance
        parser = TLEParser(tle_file)
        
        # Parse TLE
        print(f"\nParsing TLE data from: {tle_file}")
        parser.parse_tle()
        
        # Display orbital elements
        parser.print_orbital_elements()
        
        # Return parsed satellite object for potential reuse
        return parser.satellite
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    satellite = main()
