# Generate Ontology from Specifications

Invoke the Ontology Expert skill to transform specifications into formal JSON specs.

## Instructions

Use the `ontology-expert` skill to analyze the specifications and generate:
- `specs/entities.json` - Entity definitions
- `specs/algorithms.json` - Calculation logic
- `specs/workflows.json` - Process state machines

## Process

1. Read the existing specifications (from /new-idea output or GitHub Issues)
2. Extract entities from nouns in the specs
3. Extract properties, relationships, and actions
4. Define algorithms for calculated fields
5. Model workflows as state machines
6. Validate against JSON schemas
7. Commit to repository

## Output

Generate and commit:
1. Updated `specs/entities.json`
2. Updated `specs/algorithms.json`
3. Updated `specs/workflows.json`
4. Mermaid diagrams for documentation
5. Plain English summary

After generating specs, automatically run generators:
```bash
python generators/generate_all.py
```

Create a GitHub Issue for ontology review.
