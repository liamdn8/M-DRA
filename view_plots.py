#!/usr/bin/env python3
"""
Simple script to view the generated solution plots.
"""
import os
import subprocess
import sys
from pathlib import Path

def view_plots():
    """Open all available solution plots."""
    results_dir = Path("results")
    
    if not results_dir.exists():
        print("❌ No results directory found. Run a solver first!")
        return
    
    plot_files = []
    
    # Find all plot files
    for solver_dir in results_dir.iterdir():
        if solver_dir.is_dir():
            plot_file = solver_dir / "plot_sol_clusters_load.png"
            if plot_file.exists():
                plot_files.append(plot_file)
    
    if not plot_files:
        print("❌ No plot files found. Run a solver first!")
        return
    
    print(f"📊 Found {len(plot_files)} plot files:")
    for i, plot_file in enumerate(plot_files, 1):
        print(f"   {i}. {plot_file}")
    
    # Try to open with different viewers
    for plot_file in plot_files:
        try:
            # Try different image viewers
            if os.name == 'posix':  # Linux/Unix
                # Try common Linux image viewers
                viewers = ['eog', 'feh', 'display', 'xdg-open']
                for viewer in viewers:
                    try:
                        subprocess.run([viewer, str(plot_file)], check=True, 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(f"✅ Opened {plot_file.name} with {viewer}")
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    print(f"⚠️  Could not open {plot_file.name} - no suitable viewer found")
            else:
                # For Windows/Mac
                subprocess.run([sys.executable, '-c', f'import webbrowser; webbrowser.open("{plot_file}")'])
                print(f"✅ Opened {plot_file.name}")
                
        except Exception as e:
            print(f"❌ Failed to open {plot_file.name}: {e}")
    
    print(f"\n💡 Plot files are saved in the results/ directories")
    print("   You can also view them manually with any image viewer.")

if __name__ == "__main__":
    view_plots()