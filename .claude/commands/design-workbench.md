# Design Persona Workbench

Invoke the UI/UX Specialist and AI Augmentation skills to design a workbench for a persona.

## Arguments

- `$ARGUMENTS` - The persona name to design the workbench for

## Instructions

Use the `uiux-specialist` and `ai-augmentation` skills to:

1. Analyze the persona's tasks and information needs
2. Design the workbench layout (navigator, main canvas, agent panel)
3. Specify all components with data bindings
4. Define interaction patterns
5. Design AI augmentation features
6. Output to `specs/workbenches.json`

## Process

1. Read the persona definition from specs
2. Identify primary tasks and information needs
3. Design layout following the standard workbench anatomy:
   - Header with quick actions
   - Navigator with work queue
   - Main canvas with tabbed content
   - Agent panel with chat, thought process, sources
   - Footer with primary actions and production tools
4. Define data bindings for each component
5. Specify AI capabilities and transparency requirements
6. Define progressive autonomy rules

## Output

Generate and commit:
1. Updated `specs/workbenches.json` with the new workbench
2. Component specifications
3. Interaction patterns
4. AI augmentation configuration

Create a GitHub Issue for workbench implementation.
