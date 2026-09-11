import argparse
import glob
import json
import sys
from pathlib import Path

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_fiber(fiber_list):
    parts = []
    for item in fiber_list:
        perc = item.get("percentage")
        ftype = item.get("fiber_type", "")
        if perc is not None:
            parts.append(f"{perc}% {ftype}")
        else:
            parts.append(ftype)
    return ", ".join(parts)

def matches_filter(yarn, weight=None, fiber=None, brand=None):
    if weight is not None:
        if yarn.get("weight_category") != weight:
            return False

    if brand is not None:
        yarn_brand = yarn.get("brand", "").lower()
        if brand.lower() not in yarn_brand:
            return False

    if fiber is not None:
        fiber_query = fiber.lower()
        fibers = yarn.get("fiber_content", [])
        found_fiber = any(fiber_query in f.get("fiber_type", "").lower() for f in fibers)
        if not found_fiber:
            return False

    return True

def print_yarn(yarn):
    brand = yarn.get("brand", "Unknown Brand")
    line = yarn.get("line_name", "Unknown Line")
    weight = yarn.get("weight_category", "N/A")
    fiber = format_fiber(yarn.get("fiber_content", []))
    
    put_up = yarn.get("put_up", {})
    grams = put_up.get("weight_grams", "N/A")
    oz = put_up.get("weight_ounces", "N/A")
    yds = put_up.get("yardage", "N/A")
    meters = put_up.get("meters", "N/A")

    print(f"• {brand} - {line}")
    print(f"  CYC Weight Category : {weight}")
    print(f"  Fiber Composition   : {fiber}")
    print(f"  Skein Put-Up        : {grams}g ({oz} oz) / {yds} yds ({meters}m)")
    print()

def main():
    parser = argparse.ArgumentParser(description="Search and filter open-source yarn database.")
    parser.add_argument("-w", "--weight", type=int, choices=range(0, 8), help="Filter by CYC weight category (0-7)")
    parser.add_argument("-f", "--fiber", type=str, help="Case-insensitive fiber search (e.g. wool, cotton)")
    parser.add_argument("-b", "--brand", type=str, help="Case-insensitive brand search")

    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    data_dir = root_dir / "data"

    data_files = glob.glob(str(data_dir / "*.json"))
    if not data_files:
        print(f"No yarn data files found in {data_dir}")
        sys.exit(0)

    yarns = []
    for filepath in data_files:
        try:
            yarns.append(load_json(filepath))
        except Exception as e:
            print(f"Warning: Failed to load {filepath}: {e}", file=sys.stderr)

    matching_yarns = [
        y for y in yarns 
        if matches_filter(y, weight=args.weight, fiber=args.fiber, brand=args.brand)
    ]

    filters_applied = args.weight is not None or args.fiber is not None or args.brand is not None

    if not filters_applied:
        print(f"Listing all {len(matching_yarns)} yarn(s) in database:\n")
    else:
        print(f"Found {len(matching_yarns)} matching yarn(s):\n")

    for yarn in matching_yarns:
        print_yarn(yarn)

if __name__ == "__main__":
    main()
