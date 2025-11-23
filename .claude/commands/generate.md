# Run Code Generators

Run all code generators to update generated code from specs.

## Instructions

Execute the main generator script to:
1. Validate all JSON specs against schemas
2. Generate Pydantic models from entities.json
3. Generate FastAPI routes from entities.json + workflows.json
4. Generate pytest tests from entities.json + algorithms.json

## Command

```bash
python generators/generate_all.py
```

## Options

To run only specific generators:
- `python generators/generate_all.py --only models`
- `python generators/generate_all.py --only api`
- `python generators/generate_all.py --only tests`

To validate without generating:
- `python generators/generate_all.py --validate-only`

## Output

Report:
- Number of files generated
- List of generated files
- Any validation errors

After generation, run tests to verify:
```bash
pytest tests/ -v
```
