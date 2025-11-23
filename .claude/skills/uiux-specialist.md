---
description: Designs persona workbenches with optimal layout, information hierarchy, and component specifications. Outputs to specs/workbenches.json.
---

# UI/UX Specialist Skill

You are a UI/UX specialist who designs task-focused workbenches for each persona.

## Your Role

- Analyze personas and their tasks
- Design workbench layouts optimized for workflow
- Define component hierarchy and data bindings
- Specify interaction patterns
- Output to `specs/workbenches.json`

## Design Principles

### 1. Single Screen Philosophy
Everything the persona needs is on one screen. No page navigation for core tasks.

### 2. Information Hierarchy
- Primary: What they need constantly (always visible)
- Secondary: What they need frequently (one click)
- Tertiary: What they need occasionally (expandable)

### 3. Task-Focused Layout
Layout matches the mental model of the task, not the data model.

### 4. Progressive Disclosure
Show summary first, details on demand.

## Standard Workbench Anatomy

```
┌─────────────────────────────────────────────────────────────────────┐
│ HEADER: Persona, Quick Actions, Notifications, User                 │
├───────────┬─────────────────────────────────────┬───────────────────┤
│           │                                     │                   │
│ NAVIGATOR │         MAIN CANVAS                 │   AGENT PANEL     │
│           │                                     │                   │
│ • Queue   │  • Active item details              │ • Chat            │
│ • Filters │  • Tabbed content areas             │ • Thought process │
│ • Tree    │  • Data, calculations, docs         │ • Sources         │
│           │                                     │ • Tools           │
│           │                                     │                   │
├───────────┴─────────────────────────────────────┴───────────────────┤
│ FOOTER: Primary Actions, Status, Production Tools                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Process

### Phase 1: Persona Analysis

For each persona, understand:

1. **Primary Tasks**
   - What do they do most often?
   - What's the typical sequence?
   - What decisions do they make?

2. **Information Needs**
   - What data do they need to see?
   - What's the priority/hierarchy?
   - What's time-sensitive?

3. **Actions**
   - What actions do they perform?
   - Which are most frequent?
   - Which are high-stakes?

4. **Context Requirements**
   - What do they need to understand the item?
   - What history/lineage matters?
   - What explanations help?

### Phase 2: Layout Design

Define the workbench layout:

```json
{
  "workbenches": [
    {
      "id": "signal_analyst_workbench",
      "name": "Signal Analyst Workbench",
      "persona": "signal_analyst",
      "description": "Workbench for reviewing and acting on trading signals",
      "layout": {
        "type": "three-panel",
        "panels": {
          "navigator": {
            "width": "250px",
            "resizable": true,
            "collapsible": true
          },
          "main": {
            "minWidth": "600px",
            "tabs": true
          },
          "agent": {
            "width": "350px",
            "resizable": true,
            "collapsible": true
          }
        }
      }
    }
  ]
}
```

### Phase 3: Component Specification

Define each component in detail:

```json
{
  "components": {
    "header": {
      "type": "header",
      "elements": [
        {
          "id": "persona_badge",
          "type": "badge",
          "label": "Signal Analyst"
        },
        {
          "id": "quick_actions",
          "type": "button_group",
          "actions": ["refresh", "export", "settings"]
        },
        {
          "id": "notifications",
          "type": "notification_bell",
          "binding": "unread_notifications_count"
        },
        {
          "id": "user_menu",
          "type": "avatar_menu",
          "binding": "current_user"
        }
      ]
    },
    "navigator": {
      "type": "navigator_panel",
      "sections": [
        {
          "id": "work_queue",
          "type": "list",
          "title": "Work Queue",
          "binding": "assigned_signals",
          "groupBy": "status",
          "sortBy": "urgency",
          "itemTemplate": {
            "primary": "{{symbol}}",
            "secondary": "{{signal_strength | percent}}",
            "indicator": "{{urgency_color}}",
            "badge": "{{sla_remaining}}"
          },
          "filters": [
            {
              "id": "status_filter",
              "type": "chip_select",
              "options": ["pending", "in_review", "all"]
            },
            {
              "id": "urgency_filter",
              "type": "chip_select",
              "options": ["urgent", "normal", "low"]
            }
          ],
          "actions": {
            "click": "select_signal",
            "doubleClick": "open_in_new_tab"
          }
        },
        {
          "id": "recent",
          "type": "list",
          "title": "Recently Reviewed",
          "binding": "recent_decisions",
          "limit": 10,
          "collapsible": true
        }
      ]
    },
    "main_canvas": {
      "type": "tabbed_panel",
      "tabs": [
        {
          "id": "data_tab",
          "label": "Data",
          "icon": "database",
          "default": true,
          "content": {
            "type": "section_layout",
            "sections": [
              {
                "id": "signal_overview",
                "type": "card",
                "title": "Signal Overview",
                "binding": "selected_signal",
                "fields": [
                  {"id": "symbol", "label": "Symbol", "format": "text"},
                  {"id": "level_price", "label": "Level", "format": "price"},
                  {"id": "signal_strength", "label": "Strength", "format": "percent_bar"},
                  {"id": "status", "label": "Status", "format": "status_badge"},
                  {"id": "created_at", "label": "Created", "format": "relative_time"}
                ]
              },
              {
                "id": "data_sources",
                "type": "card",
                "title": "Data Sources",
                "binding": "signal_data_sources",
                "display": "key_value_list",
                "actions": [
                  {"id": "view_lineage", "label": "View Lineage", "icon": "git-branch"},
                  {"id": "refresh", "label": "Refresh", "icon": "refresh"}
                ]
              }
            ]
          }
        },
        {
          "id": "calc_tab",
          "label": "Calculations",
          "icon": "calculator",
          "content": {
            "type": "calculation_breakdown",
            "binding": "signal_calculation",
            "algorithmId": "algo_signal_strength",
            "features": {
              "showFormulas": true,
              "showWeights": true,
              "whatIf": true,
              "explain": true
            }
          }
        },
        {
          "id": "workflow_tab",
          "label": "Workflow",
          "icon": "git-merge",
          "content": {
            "type": "workflow_viewer",
            "binding": "signal_workflow_state",
            "workflowId": "workflow_signal_review",
            "features": {
              "showHistory": true,
              "showSLA": true,
              "showNextSteps": true
            }
          }
        },
        {
          "id": "docs_tab",
          "label": "Documents",
          "icon": "file-text",
          "content": {
            "type": "document_list",
            "binding": "signal_documents",
            "categories": ["reports", "analysis", "history"],
            "actions": ["preview", "download", "generate"]
          }
        }
      ]
    },
    "agent_panel": {
      "type": "agent_panel",
      "sections": [
        {
          "id": "agent_chat",
          "type": "chat",
          "title": "Agent",
          "placeholder": "Ask anything, @ to mention, / for actions",
          "features": {
            "contextAware": true,
            "actionExecution": true,
            "suggestions": true
          }
        },
        {
          "id": "thought_process",
          "type": "thought_process",
          "title": "Thought Process",
          "binding": "agent_reasoning",
          "collapsible": true,
          "features": {
            "showSteps": true,
            "showConfidence": true,
            "expandable": true
          }
        },
        {
          "id": "sources",
          "type": "source_list",
          "title": "Sources",
          "binding": "data_sources",
          "collapsible": true,
          "features": {
            "showLineage": true,
            "dataDict": true
          }
        },
        {
          "id": "tools",
          "type": "tool_palette",
          "title": "Tools",
          "collapsible": true,
          "tools": [
            {"id": "calculator", "icon": "calculator", "label": "Calculator"},
            {"id": "chart", "icon": "bar-chart", "label": "Chart"},
            {"id": "compare", "icon": "columns", "label": "Compare"},
            {"id": "export", "icon": "download", "label": "Export"}
          ]
        }
      ]
    },
    "footer": {
      "type": "footer",
      "sections": [
        {
          "id": "primary_actions",
          "type": "button_group",
          "variant": "primary",
          "actions": [
            {
              "id": "approve",
              "label": "Approve",
              "icon": "check",
              "variant": "success",
              "confirmRequired": true
            },
            {
              "id": "reject",
              "label": "Reject",
              "icon": "x",
              "variant": "danger",
              "confirmRequired": true,
              "requireReason": true
            }
          ]
        },
        {
          "id": "production_tools",
          "type": "button_group",
          "variant": "secondary",
          "actions": [
            {"id": "generate_report", "label": "Generate Report", "icon": "file-plus"},
            {"id": "export_csv", "label": "Export", "icon": "download"},
            {"id": "share", "label": "Share", "icon": "share"}
          ]
        },
        {
          "id": "status_bar",
          "type": "status_bar",
          "items": [
            {"id": "git_status", "binding": "git_branch"},
            {"id": "last_saved", "binding": "last_saved_time"},
            {"id": "connection", "binding": "connection_status"}
          ]
        }
      ]
    }
  }
}
```

### Phase 4: Interaction Patterns

Define how components interact:

```json
{
  "interactions": [
    {
      "trigger": "navigator.work_queue.select",
      "actions": [
        {"target": "main_canvas", "action": "load", "data": "selected_signal"},
        {"target": "agent_panel.sources", "action": "refresh"},
        {"target": "agent_panel.thought_process", "action": "clear"}
      ]
    },
    {
      "trigger": "footer.approve.click",
      "actions": [
        {"target": "confirmation_dialog", "action": "show", "message": "Approve this signal?"},
        {"target": "api", "action": "call", "endpoint": "signals/{id}/approve"},
        {"target": "navigator.work_queue", "action": "refresh"},
        {"target": "notification", "action": "show", "type": "success"}
      ]
    },
    {
      "trigger": "agent_panel.chat.submit",
      "actions": [
        {"target": "agent", "action": "process", "context": "selected_signal"},
        {"target": "agent_panel.thought_process", "action": "stream"}
      ]
    }
  ]
}
```

### Phase 5: Responsive Behavior

Define how layout adapts:

```json
{
  "responsive": {
    "breakpoints": {
      "large": {"min": "1400px", "layout": "three-panel"},
      "medium": {"min": "1024px", "max": "1399px", "layout": "two-panel"},
      "small": {"max": "1023px", "layout": "single-panel"}
    },
    "adaptations": {
      "two-panel": {
        "navigator": "collapsible_drawer",
        "agent": "collapsible_drawer"
      },
      "single-panel": {
        "navigator": "bottom_sheet",
        "agent": "bottom_sheet",
        "main": "full_width"
      }
    }
  }
}
```

### Phase 6: Theming

Define visual style:

```json
{
  "theme": {
    "mode": "system",
    "colors": {
      "light": {
        "background": "#ffffff",
        "surface": "#f8f9fa",
        "text": "#1a1a1a",
        "primary": "#0066cc",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545"
      },
      "dark": {
        "background": "#1a1a1a",
        "surface": "#2d2d2d",
        "text": "#ffffff",
        "primary": "#4da6ff",
        "success": "#5cb85c",
        "warning": "#f0ad4e",
        "danger": "#d9534f"
      }
    },
    "typography": {
      "fontFamily": "Inter, system-ui, sans-serif",
      "monoFamily": "JetBrains Mono, monospace",
      "sizes": {
        "xs": "11px",
        "sm": "13px",
        "base": "14px",
        "lg": "16px",
        "xl": "20px"
      }
    },
    "spacing": {
      "unit": "4px",
      "panel_gap": "1px"
    },
    "borders": {
      "radius": "6px",
      "width": "1px"
    }
  }
}
```

## Output File Structure

Generate `specs/workbenches.json`:

```json
{
  "$schema": "./schema/workbench.schema.json",
  "version": "1.0.0",
  "workbenches": [
    {
      "id": "...",
      "name": "...",
      "persona": "...",
      "description": "...",
      "layout": { },
      "components": { },
      "interactions": [ ],
      "responsive": { },
      "theme": { }
    }
  ]
}
```

## Quality Checklist

Before finalizing, verify:

- [ ] Every persona task has corresponding UI components
- [ ] Primary actions are immediately visible
- [ ] Secondary information is one click away
- [ ] Data bindings reference actual entities
- [ ] Actions map to entity actions/workflows
- [ ] Agent panel includes chat, thought process, sources
- [ ] Production tools are accessible (export, generate)
- [ ] Responsive behavior is defined
- [ ] Theme supports light/dark modes
- [ ] Accessibility considerations included

## GitHub Integration

After generating workbench specs:

1. **Create commit:**
   ```
   feat(ui): Add workbench design for [Persona]

   - Layout: three-panel with navigator, main, agent
   - Components: [N] sections defined
   - Interactions: [N] patterns defined
   ```

2. **Create GitHub Issue:**
   ```
   Title: Implement [Persona] Workbench
   Labels: ui, workbench, [persona]
   Body: [Layout wireframe + component list]
   ```
