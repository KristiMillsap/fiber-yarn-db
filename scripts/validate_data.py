import json
import glob
import sys
from pathlib import Path
from jsonschema import validate, ValidationError, SchemaError

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    root_dir = Path(__file__).resolve().parent.parent
    schema_path = root_dir / "schema" / "yarn-v1.schema.json"
    data_dir = root_dir / "data"

    if not schema_path.exists():
        print(f"Error: Schema file not found at {schema_path}")
        sys.exit(1)

    try:
        schema = load_json(schema_path)
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
            validate(instance=data, schema=schema)
            print(f"✓ {relative_path} is valid.")
        except ValidationError as e:
            print(f"✗ {relative_path} failed validation:")
            print(f"  Message: {e.message}")
            print(f"  Path: {'/'.join(str(p) for p in e.path)}")
            has_errors = True
        except SchemaError as e:
            print(f"Error in schema definition: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ {relative_path} could not be read: {e}")
            has_errors = True

    if has_errors:
        sys.exit(1)
    else:
        print("\nAll files passed validation.")

if __name__ == "__main__":
    main()
