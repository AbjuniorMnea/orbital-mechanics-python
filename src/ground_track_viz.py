#!/usr/bin/env python3
"""
Ground Track Visualization for Satellite Tracking

This module creates visual plots of satellite ground tracks
(the path traced on Earth's surface as the satellite orbits).

Author: AbjuniorMnea
Date: January 11, 2026
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import sys
from typing import List, Dict, Optional


class GroundTrackVisualizer:
    """Create ground track visualizations for satellite orbits."""
    
    def __init__(self, figure_size=(16, 9), dpi=150):
        """
        Initialize visualizer.
        
        Args:
            figure_size: Tuple of (width, height) in inches
            dpi: Dots per inch for output image
        """
        self.figure_size = figure_size
        self.dpi = dpi
        
    def plot_ground_track(self,
                         results: List[Dict],
                         title: str = "ISS Ground Track",
                         output_file: str = "outputs/iss_ground_track.png",
                         show_plot: bool = False) -> str:
        """
        Plot satellite ground track on world map.
        
        Args:
            results: List of position dicts from OrbitalPropagator
            title: Plot title
            output_file: Path to save PNG
            show_plot: Whether to display plot (False for headless)
            
        Returns:
            Path to saved image
        """
        # Extract data
        lats = [r['latitude_deg'] for r in results]
        lons = [r['longitude_deg'] for r in results]
        times = [r['time'] for r in results]
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # Plot world map (simple lat/lon grid)
        self._draw_world_map(ax)
        
        # Plot ground track
        self._plot_track_segments(ax, lats, lons)
        
        # Mark start and end points
        ax.plot(lons[0], lats[0], 'go', markersize=12, 
                label=f'Start: {times[0].strftime("%H:%M UTC")}', zorder=5)
        ax.plot(lons[-1], lats[-1], 'rs', markersize=12,
                label=f'End: {times[-1].strftime("%H:%M UTC")}', zorder=5)
        
        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        
        # Labels and title
        ax.set_xlabel('Longitude (degrees)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latitude (degrees)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Set axis limits
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        
        # Set aspect ratio to match map projection
        ax.set_aspect('equal')
        
        # Legend
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
        
        # Add info text
        duration_hours = (times[-1] - times[0]).total_seconds() / 3600
        info_text = (f"Duration: {duration_hours:.1f} hours\n"
                    f"Points: {len(results)}\n"
                    f"Period: ~92.7 min")
        ax.text(0.02, 0.02, info_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='bottom',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Tight layout
        plt.tight_layout()
        
        # Save
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        print(f"\n✅ Ground track saved to: {output_file}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return output_file
    
    def _draw_world_map(self, ax):
        """Draw simple world map outline."""
        # Draw coastlines (simplified)
        # Continents as filled polygons
        
        # Land mass color
        land_color = '#E8E8E8'
        
        # Draw filled rectangles for major land masses (simplified)
        # North America
        ax.add_patch(plt.Rectangle((-170, 15), 90, 60, 
                                   color=land_color, alpha=0.3, zorder=1))
        # South America
        ax.add_patch(plt.Rectangle((-85, -55), 50, 60,
                                   color=land_color, alpha=0.3, zorder=1))
        # Europe
        ax.add_patch(plt.Rectangle((-10, 35), 60, 40,
                                   color=land_color, alpha=0.3, zorder=1))
        # Africa
        ax.add_patch(plt.Rectangle((-20, -35), 60, 70,
                                   color=land_color, alpha=0.3, zorder=1))
        # Asia
        ax.add_patch(plt.Rectangle((50, -10), 130, 70,
                                   color=land_color, alpha=0.3, zorder=1))
        # Australia
        ax.add_patch(plt.Rectangle((110, -45), 50, 35,
                                   color=land_color, alpha=0.3, zorder=1))
        
        # Draw equator
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, 
                  alpha=0.5, label='Equator')
        
        # Draw tropics
        ax.axhline(y=23.5, color='orange', linestyle=':', linewidth=0.8,
                  alpha=0.4, label='Tropic of Cancer')
        ax.axhline(y=-23.5, color='orange', linestyle=':', linewidth=0.8,
                  alpha=0.4, label='Tropic of Capricorn')
        
        # Draw Arctic/Antarctic circles
        ax.axhline(y=66.5, color='cyan', linestyle=':', linewidth=0.8,
                  alpha=0.4)
        ax.axhline(y=-66.5, color='cyan', linestyle=':', linewidth=0.8,
                  alpha=0.4)
        
        # Set background color (ocean)
        ax.set_facecolor('#D6EAF8')
    
    def _plot_track_segments(self, ax, lats, lons):
        """
        Plot ground track, handling discontinuities at ±180° longitude.
        
        When satellite crosses the antimeridian, we need to break the line
        to avoid drawing across the entire map.
        """
        segments_lats = []
        segments_lons = []
        current_seg_lats = []
        current_seg_lons = []
        
        for i in range(len(lons)):
            if i > 0:
                # Check for discontinuity (crossing ±180°)
                lon_diff = abs(lons[i] - lons[i-1])
                if lon_diff > 180:  # Crossed antimeridian
                    # Save current segment
                    if current_seg_lons:
                        segments_lons.append(current_seg_lons)
                        segments_lats.append(current_seg_lats)
                    # Start new segment
                    current_seg_lons = [lons[i]]
                    current_seg_lats = [lats[i]]
                else:
                    current_seg_lons.append(lons[i])
                    current_seg_lats.append(lats[i])
            else:
                current_seg_lons.append(lons[i])
                current_seg_lats.append(lats[i])
        
        # Add final segment
        if current_seg_lons:
            segments_lons.append(current_seg_lons)
            segments_lats.append(current_seg_lats)
        
        # Plot all segments
        for seg_lons, seg_lats in zip(segments_lons, segments_lats):
            ax.plot(seg_lons, seg_lats, 'b-', linewidth=2, alpha=0.7, zorder=3)
            
            # Add direction arrows (every 5 points)
            for i in range(0, len(seg_lons)-1, 5):
                dx = seg_lons[i+1] - seg_lons[i]
                dy = seg_lats[i+1] - seg_lats[i]
                ax.arrow(seg_lons[i], seg_lats[i], dx*0.3, dy*0.3,
                        head_width=3, head_length=2, fc='blue', ec='blue',
                        alpha=0.6, zorder=4)
    
    def plot_multiple_orbits(self,
                            results: List[Dict],
                            num_orbits: int = 3,
                            title: str = "ISS Ground Track - Multiple Orbits",
                            output_file: str = "outputs/iss_multiple_orbits.png",
                            show_plot: bool = False) -> str:
        """
        Plot multiple distinct orbital passes.
        
        Args:
            results: Full propagation results
            num_orbits: Number of orbits to highlight
            title: Plot title
            output_file: Output path
            show_plot: Whether to display
            
        Returns:
            Path to saved image
        """
        # Create figure
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # Draw world map
        self._draw_world_map(ax)
        
        # Calculate points per orbit (assuming ~90 min period)
        if len(results) > 0:
            duration = (results[-1]['time'] - results[0]['time']).total_seconds() / 60
            time_step = duration / len(results)
            points_per_orbit = int(90 / time_step)
        else:
            points_per_orbit = len(results) // num_orbits
        
        # Plot each orbit in different color
        colors = ['blue', 'red', 'green', 'purple', 'orange']
        
        for orbit_num in range(min(num_orbits, len(colors))):
            start_idx = orbit_num * points_per_orbit
            end_idx = start_idx + points_per_orbit
            
            if end_idx > len(results):
                break
            
            orbit_results = results[start_idx:end_idx]
            lats = [r['latitude_deg'] for r in orbit_results]
            lons = [r['longitude_deg'] for r in orbit_results]
            
            # Plot this orbit
            self._plot_track_segments_colored(ax, lats, lons, 
                                             colors[orbit_num],
                                             f"Orbit {orbit_num + 1}")
        
        # Formatting
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_xlabel('Longitude (degrees)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latitude (degrees)', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_aspect('equal')
        ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        print(f"\n✅ Multiple orbits plot saved to: {output_file}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return output_file
    
    def _plot_track_segments_colored(self, ax, lats, lons, color, label):
        """Plot track segments with specific color."""
        segments_lats = []
        segments_lons = []
        current_seg_lats = []
        current_seg_lons = []
        
        for i in range(len(lons)):
            if i > 0:
                lon_diff = abs(lons[i] - lons[i-1])
                if lon_diff > 180:
                    if current_seg_lons:
                        segments_lons.append(current_seg_lons)
                        segments_lats.append(current_seg_lats)
                    current_seg_lons = [lons[i]]
                    current_seg_lats = [lats[i]]
                else:
                    current_seg_lons.append(lons[i])
                    current_seg_lats.append(lats[i])
            else:
                current_seg_lons.append(lons[i])
                current_seg_lats.append(lats[i])
        
        if current_seg_lons:
            segments_lons.append(current_seg_lons)
            segments_lats.append(current_seg_lats)
        
        # Plot segments
        for idx, (seg_lons, seg_lats) in enumerate(zip(segments_lons, segments_lats)):
            if idx == 0:
                ax.plot(seg_lons, seg_lats, color=color, linewidth=2.5, 
                       alpha=0.8, label=label, zorder=3)
            else:
                ax.plot(seg_lons, seg_lats, color=color, linewidth=2.5,
                       alpha=0.8, zorder=3)


def main():
    """Main execution function."""
    # Import required modules
    try:
        from tle_parser import TLEParser
        from orbital_propagation import OrbitalPropagator
    except ImportError as e:
        print(f"Error: Could not import required modules: {e}")
        print("Make sure tle_parser.py and orbital_propagation.py are in the same directory.")
        sys.exit(1)
    
    # Default parameters
    tle_file = "iss_tle.txt"
    duration_hours = 6.0  # 6 hours for visualization (about 4 orbits)
    time_step_minutes = 5.0  # 5-minute intervals for smooth curve
    
    # Parse command line
    if len(sys.argv) > 1:
        tle_file = sys.argv[1]
    if len(sys.argv) > 2:
        duration_hours = float(sys.argv[2])
    
    try:
        # Parse TLE
        print(f"\n{'='*60}")
        print("ISS GROUND TRACK VISUALIZATION")
        print('='*60)
        print(f"\nParsing TLE from: {tle_file}")
        parser = TLEParser(tle_file)
        satellite = parser.parse_tle()
        print(f"Satellite: {parser.satellite_name}")
        
        # Propagate orbit
        propagator = OrbitalPropagator(satellite)
        print(f"\nPropagating orbit for {duration_hours} hours...")
        start_time = datetime.utcnow()
        results = propagator.propagate_multiple(start_time, duration_hours, time_step_minutes)
        print(f"Generated {len(results)} position points")
        
        # Create visualizer
        visualizer = GroundTrackVisualizer()
        
        # Generate ground track plot
        print("\nGenerating ground track visualization...")
        output_file = visualizer.plot_ground_track(
            results,
            title=f"{parser.satellite_name} Ground Track - {duration_hours:.1f} Hours",
            output_file="outputs/iss_ground_track.png"
        )
        
        # Generate multiple orbits plot
        print("\nGenerating multiple orbits visualization...")
        multi_orbit_file = visualizer.plot_multiple_orbits(
            results,
            num_orbits=3,
            title=f"{parser.satellite_name} Ground Track - First 3 Orbits",
            output_file="outputs/iss_multiple_orbits.png"
        )
        
        print(f"\n{'='*60}")
        print("VISUALIZATION COMPLETE!")
        print('='*60)
        print(f"\n📊 Generated visualizations:")
        print(f"  1. Single track: {output_file}")
        print(f"  2. Multiple orbits: {multi_orbit_file}")
        print(f"\n💡 These images are ready for your application portfolio!")
        print('='*60 + '\n')
        
        return output_file, multi_orbit_file
        
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
