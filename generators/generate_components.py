#!/usr/bin/env python3
"""
Generate React components from workbench specs.
"""

from pathlib import Path


def generate_workbench_component(workbench: dict) -> str:
    """Generate React component for a workbench."""
    name = workbench['name']
    persona = workbench.get('persona', 'user')
    sections = workbench.get('sections', {})

    code = f'''/**
 * Auto-generated workbench component for {name}.
 * DO NOT EDIT - Generated from specs/workbenches.json
 */

'use client'

import {{ useState, useEffect }} from 'react'
import {{ GenUIRenderer }} from '../genui/GenUIRenderer'
import {{ useSignals }} from '../../hooks/useSignals'

interface {name}Props {{
  userId?: string
}}

export function {name}({{ userId }}: {name}Props) {{
  const [selectedItem, setSelectedItem] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<string>('main')
  const {{ signals, isConnected }} = useSignals()

  return (
    <div className="flex h-screen bg-gray-50">
      {{/* Sidebar - Data Sources */}}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">Data Sources</h2>
        </div>
        <div className="flex-1 overflow-y-auto p-3">
          {{/* Data source list will be populated here */}}
        </div>
      </aside>

      {{/* Main Content */}}
      <main className="flex-1 flex">
        {{/* Read Panel */}}
        <div className="w-[55%] border-r border-gray-200 flex flex-col">
          <div className="bg-white border-b border-gray-200 px-4">
            <div className="flex gap-1">
              <button
                onClick={{() => setActiveTab('main')}}
                className={{`px-4 py-3 text-sm font-medium border-b-2 transition ${{
                  activeTab === 'main'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600'
                }}`}}
              >
                Main
              </button>
              <button
                onClick={{() => setActiveTab('preview')}}
                className={{`px-4 py-3 text-sm font-medium border-b-2 transition ${{
                  activeTab === 'preview'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600'
                }}`}}
              >
                Preview
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-auto bg-white p-4">
            {{/* Canvas read content */}}
          </div>
        </div>

        {{/* Write Panel */}}
        <div className="w-[45%] flex flex-col bg-white">
          <div className="flex-1 overflow-auto p-6">
            {{selectedItem ? (
              <div>
                {{/* Form/editor for selected item */}}
                <GenUIRenderer
                  widget={{{{
                    protocol: 'genui_v1',
                    widget_type: 'FORM',
                    props: {{
                      title: 'Edit Item',
                      data: {{}}
                    }}
                  }}}}
                />
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                Select an item to edit
              </div>
            )}}
          </div>
        </div>
      </main>

      {{/* Right Sidebar - Tools & Agent */}}
      <aside className="w-56 bg-white border-l border-gray-200 p-4 space-y-6">
        {{/* Tools */}}
        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Tools
          </h3>
          <div className="space-y-2">
            {generate_tools_jsx(sections.get('tools', {}))}
          </div>
        </div>

        {{/* Agent */}}
        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Agent
          </h3>
          <div className="grid grid-cols-2 gap-2">
            {generate_agent_buttons_jsx(sections.get('agent', {}))}
          </div>
        </div>

        {{/* Connection Status */}}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center gap-2 text-sm">
            <div className={{`w-2 h-2 rounded-full ${{isConnected ? 'bg-green-500' : 'bg-red-500'}}`}} />
            <span className="text-gray-600">
              {{isConnected ? 'Connected' : 'Disconnected'}}
            </span>
          </div>
        </div>
      </aside>
    </div>
  )
}}

export default {name}
'''

    return code


def generate_tools_jsx(tools_config: dict) -> str:
    """Generate JSX for tools section."""
    tools = tools_config.get('tools', [])
    if not tools:
        return '<button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg">No tools configured</button>'

    jsx_parts = []
    for tool in tools[:4]:  # Limit to 4 tools
        name = tool.get('name', 'Tool')
        jsx_parts.append(
            f'<button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg">{name}</button>'
        )

    return '\n            '.join(jsx_parts)


def generate_agent_buttons_jsx(agent_config: dict) -> str:
    """Generate JSX for agent buttons."""
    capabilities = agent_config.get('capabilities', ['suggest', 'explain'])

    jsx_parts = []
    for cap in capabilities[:4]:  # Limit to 4 buttons
        label = cap.title()
        jsx_parts.append(
            f'<button className="px-3 py-2 text-xs font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg">{label}</button>'
        )

    return '\n            '.join(jsx_parts)


def generate_components(specs: dict, output_dir: Path) -> list[Path]:
    """Generate all component files from specs."""
    workbenches = specs.get('workbenches', {}).get('workbenches', [])
    components_dir = output_dir / 'components' / 'workbenches'
    components_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    for workbench in workbenches:
        name = workbench['name']
        filename = f"{name}.tsx"
        filepath = components_dir / filename

        code = generate_workbench_component(workbench)
        filepath.write_text(code)
        generated_files.append(filepath)
        print(f"  ✓ {filepath}")

    # Generate index file
    index_code = '// Auto-generated workbench exports\n\n'
    for workbench in workbenches:
        name = workbench['name']
        index_code += f"export {{ {name} }} from './{name}'\n"

    index_path = components_dir / 'index.ts'
    index_path.write_text(index_code)
    generated_files.append(index_path)

    return generated_files
