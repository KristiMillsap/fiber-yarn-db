# Open-Source Yarn Database

An open-source data repository for yarn specifications, attributes, and fiber contents structured according to standard JSON Schema specifications.

## Project Structure

- `schema/`: JSON Schema definitions validating yarn product specifications.
  - `yarn-v1.schema.json`: Schema Draft-07 for yarn metadata (weight category, put-up, gauge, fiber content).
- `data/`: Contains JSON datasets for individual yarn lines.
- `scripts/`: Utility scripts for schema validation and data integrity checks.

## Setup & Prerequisites

Python 3.7+ and `jsonschema` are required to run data validation.

Install dependencies:
