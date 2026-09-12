import glob
import json
import math
import os
import sys
from pathlib import Path

# Common project yardage estimates: (min_yardage, max_yardage)
PROJECT_REQUIREMENTS = {
    "Beanie / Hat": (150, 200),
    "Cowl": (200, 350),
    "Scarf": (300, 500),
    "Shawl / Wrap": (500, 900),
    "Sweater": (1100, 1600),
}

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def matches_weight(yarn, weight_category):
    return yarn.get("weight_category") == weight_category

def matches_fiber(yarn, fiber_pref):
    if not fiber_pref or fiber_pref.strip().lower() in ["any", ""]:
        return True
    
    pref = fiber_pref.strip().lower()
    fibers = yarn.get("fiber_content", [])
    for f in fibers:
        fiber_type = f.get("fiber_type", "").lower()
        if pref in fiber_type:
            return True
    return False

def get_skein_yardage(yarn):
    put_up = yarn.get("put_up", {})
    if isinstance(put_up, dict):
        return put_up.get("yardage")
    return None

def main():
    print("========================================")
    print("      Yarn Project Planner CLI         ")
    print("========================================\n")

    # Prompt user inputs
    while True:
        try:
            cyc_input = input("What CYC yarn weight category do you want to use (0-7)? ").strip()
            cyc_weight = int(cyc_input)
            if 0 <= cyc_weight <= 7:
                break
            print("Please enter a valid CYC weight category between 0 and 7.")
        except ValueError:
            print("Please enter a valid integer between 0 and 7.")

    while True:
        try:
            yardage_input = input("How much total yardage (or meters) do you have available? ").strip()
            available_yardage = float(yardage_input)
            if available_yardage >= 0:
                break
            print("Please enter a non-negative number.")
        except ValueError:
            print("Please enter a valid number.")

    fiber_pref = input("Any specific fiber preference (e.g., Wool, Cotton, Acrylic, or 'Any')? ").strip()

    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data"

    data_files = glob.glob(str(data_dir / "*.json"))
    if not data_files:
        print(f"\nNo yarn data files found in {data_dir}")
        sys.exit(0)

    yarns = []
    for filepath in data_files:
        try:
            yarns.append(load_json(filepath))
        except Exception as e:
            print(f"Warning: Failed to load {filepath}: {e}", file=sys.stderr)

    matching_yarns = [
        y for y in yarns 
        if matches_weight(y, cyc_weight) and matches_fiber(y, fiber_pref)
    ]

    print("\n========================================")
    print("           PROJECT RESULTS              ")
    print("========================================\n")

    if not matching_yarns:
        print("No matching yarns found in the database for your criteria.")
        return

    print(f"Found {len(matching_yarns)} matching yarn(s):\n")

    for yarn in matching_yarns:
        brand = yarn.get("brand", "Unknown Brand")
        line = yarn.get("line_name", "Unknown Line")
        skein_yds = get_skein_yardage(yarn)

        print(f"• {brand} - {line}")
        if skein_yds is not None:
            print(f"  Yardage per skein: {skein_yds} yds")
        else:
            print("  Yardage per skein: Unknown")

        print("  Project Possibilities:")
        for project_name, (min_req, max_req) in PROJECT_REQUIREMENTS.items():
            if available_yardage >= min_req:
                print(f"    [✓] {project_name} (~{min_req}-{max_req} yds): CAN COMPLETE")
            else:
                missing = min_req - available_yardage
                if skein_yds and skein_yds > 0:
                    skeins_needed = math.ceil(missing / skein_yds)
                    print(f"    [ ] {project_name} (~{min_req}-{max_req} yds): Short by {missing:.0f} yds (Need {skeins_needed} more skein(s))")
                else:
                    print(f"    [ ] {project_name} (~{min_req}-{max_req} yds): Short by {missing:.0f} yds")
        print()

if __name__ == "__main__":
    main()
