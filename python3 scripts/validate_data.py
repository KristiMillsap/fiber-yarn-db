import json
import glob
import sys
from pathlib import Path

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_yarn_data(data, filepath):
    errors = []

    if not isinstance(data, dict):
        return ["Root JSON structure must be an object"]

    allowed_root_keys = {"brand", "line_name", "weight_category", "put_up", "recommended_gauge", "fiber_content"}
    extra_keys = set(data.keys()) - allowed_root_keys
    if extra_keys:
        errors.append(f"Unexpected properties found: {', '.join(extra_keys)}")

    required_root = ["brand", "line_name", "weight_category", "put_up", "recommended_gauge", "fiber_content"]
    for req in required_root:
        if req not in data:
            errors.append(f"Missing required field: '{req}'")

    if "brand" in data and not isinstance(data["brand"], str):
        errors.append("'brand' must be a string")

    if "line_name" in data and not isinstance(data["line_name"], str):
        errors.append("'line_name' must be a string")

    if "weight_category" in data:
        wc = data["weight_category"]
        if not isinstance(wc, int) or isinstance(wc, bool) or not (0 <= wc <= 7):
            errors.append("'weight_category' must be an integer between 0 and 7")

    if "put_up" in data:
        put_up = data["put_up"]
        if not isinstance(put_up, dict):
            errors.append("'put_up' must be an object")
        else:
            allowed_put_up = {"weight_grams", "weight_ounces", "yardage", "meters"}
            extra_pu = set(put_up.keys()) - allowed_put_up
            if extra_pu:
                errors.append(f"Unexpected properties in 'put_up': {', '.join(extra_pu)}")

            for pu_req in allowed_put_up:
                if pu_req not in put_up:
                    errors.append(f"Missing required field in 'put_up': '{pu_req}'")
                elif not isinstance(put_up[pu_req], (int, float)) or isinstance(put_up[pu_req], bool) or put_up[pu_req] < 0:
                    errors.append(f"'put_up.{pu_req}' must be a non-negative number")

    if "recommended_gauge" in data:
        rg = data["recommended_gauge"]
        if not isinstance(rg, dict):
            errors.append("'recommended_gauge' must be an object")
        else:
            allowed_rg = {"knit_gauge_4in", "crochet_gauge_4in", "recommended_needle_mm", "recommended_hook_mm"}
            extra_rg = set(rg.keys()) - allowed_rg
            if extra_rg:
                errors.append(f"Unexpected properties in 'recommended_gauge': {', '.join(extra_rg)}")

            for rg_req in allowed_rg:
                if rg_req not in rg:
                    errors.append(f"Missing required field in 'recommended_gauge': '{rg_req}'")
                elif not isinstance(rg[rg_req], (int, float)) or isinstance(rg[rg_req], bool) or rg[rg_req] < 0:
                    errors.append(f"'recommended_gauge.{rg_req}' must be a non-negative number")

    if "fiber_content" in data:
        fc = data["fiber_content"]
        if not isinstance(fc, list) or len(fc) < 1:
            errors.append("'fiber_content' must be a non-empty array")
        else:
            for idx, item in enumerate(fc):
                if not isinstance(item, dict):
                    errors.append(f"'fiber_content[{idx}]' must be an object")
                    continue
                allowed_fc = {"fiber_type", "percentage"}
                extra_fc = set(item.keys()) - allowed_fc
                if extra_fc:
                    errors.append(f"Unexpected properties in 'fiber_content[{idx}]': {', '.join(extra_fc)}")

                if "fiber_type" not in item:
                    errors.append(f"Missing required field 'fiber_type' in 'fiber_content[{idx}]'")
                elif not isinstance(item["fiber_type"], str):
                    errors.append(f"'fiber_type' in 'fiber_content[{idx}]' must be a string")

                if "percentage" not in item:
                    errors.append(f"Missing required field 'percentage' in 'fiber_content[{idx}]'")
                elif not isinstance(item["percentage"], (int, float)) or isinstance(item["percentage"], bool) or not (0 <= item["percentage"] <= 100):
                    errors.append(f"'percentage' in 'fiber_content[{idx}]' must be a number between 0 and 100")

    return errors

def main():
    root_dir = Path(__file__).resolve().parent.parent
    schema_path = root_dir / "schema" / "yarn-v1.schema.json"
    data_dir = root_dir / "data"

    if not schema_path.exists():
        print(f"Error: Schema file not found at {schema_path}")
        sys.exit(1)

    try:
        load_json(schema_path)
    except Exception as e:
        print(f"Error reading schema file: {e}")
        sys.exit(1)

    data_files = glob.glob(str(data_dir / "*.json"))
    if not data_files:
        print(f"No data files found in {data_dir}")
        sys.exit(0)

    has_errors = False
    print(f"Validating {len(data_files)} file(s) against schema...\n")

    for file_path in data_files:
        relative_path = Path(file_path).relative_to(root_dir)
        try:
            data = load_json(file_path)
            validation_errors = validate_yarn_data(data, relative_path)
            if not validation_errors:
                print(f"✓ {relative_path} is valid.")
            else:
                print(f"✗ {relative_path} failed validation:")
                for err in validation_errors:
                    print(f"  - {err}")
                has_errors = True
        except Exception as e:
            print(f"✗ {relative_path} could not be read: {e}")
            has_errors = True

    if has_errors:
        sys.exit(1)
    else:
        print("\nAll files passed validation.")

if __name__ == "__main__":
    main()
