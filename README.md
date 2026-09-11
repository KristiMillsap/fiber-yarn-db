# Open-Source Yarn Database

An open-source data repository for yarn specifications, attributes, and fiber contents structured according to standard JSON Schema specifications.

## Project Structure

- `schema/`: JSON Schema definitions validating yarn product specifications.
  - `yarn-v1.schema.json`: Schema Draft-07 for yarn metadata (weight category, put-up, gauge, fiber content).
- `data/`: Contains JSON datasets for individual yarn lines.
- `scripts/`: Utility scripts for schema validation and CLI searching.
  - `validate_data.py`: Script to validate data files against the schema.
  - `search_yarn.py`: CLI tool for querying yarn data.

## Setup & Prerequisites

Python 3.7+ (standard library only).

## Running Validation

Run the validation script to check all JSON files in the `data/` directory:

