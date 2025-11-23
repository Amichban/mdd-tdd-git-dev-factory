/**
 * GenUI Renderer - Renders widgets from GenUI Contract.
 * Safe, predictable UI components that only execute registered commands.
 */

'use client'

import React from 'react'
import { ActionCard } from './ActionCard'
import { DataTable } from './DataTable'
import { StatusBadge } from './StatusBadge'
import { AlertWidget } from './AlertWidget'

// GenUI Contract types
export interface GenUIWidget {
  protocol: 'genui_v1'
  widget_type: 'ACTION_CARD' | 'DATA_TABLE' | 'CHART' | 'FORM' | 'ALERT' | 'STATUS_BADGE' | 'TIMELINE'
  props: {
    title?: string
    description?: string
    risk_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
    actions?: GenUIAction[]
    data?: any
    columns?: GenUIColumn[]
  }
}

export interface GenUIAction {
  label: string
  style?: 'PRIMARY' | 'SECONDARY' | 'GHOST' | 'DANGER'
  command: string
  params?: Record<string, any>
  confirm?: boolean
}

export interface GenUIColumn {
  key: string
  label: string
  type?: string
}

interface GenUIRendererProps {
  widget: GenUIWidget
  onCommand?: (command: string, params: Record<string, any>) => void
}

export function GenUIRenderer({ widget, onCommand }: GenUIRendererProps) {
  // Validate protocol
  if (widget.protocol !== 'genui_v1') {
    return (
      <div className="p-4 bg-red-50 text-red-700 rounded-lg">
        Unknown protocol: {widget.protocol}
      </div>
    )
  }

  // Handle command execution
  const handleCommand = (command: string, params: Record<string, any> = {}) => {
    if (onCommand) {
      onCommand(command, params)
    } else {
      console.log('GenUI Command:', command, params)
    }
  }

  // Render based on widget type
  switch (widget.widget_type) {
    case 'ACTION_CARD':
      return (
        <ActionCard
          title={widget.props.title}
          description={widget.props.description}
          riskLevel={widget.props.risk_level}
          actions={widget.props.actions}
          onAction={handleCommand}
        />
      )

    case 'DATA_TABLE':
      return (
        <DataTable
          title={widget.props.title}
          columns={widget.props.columns || []}
          data={widget.props.data || []}
          actions={widget.props.actions}
          onAction={handleCommand}
        />
      )

    case 'STATUS_BADGE':
      return (
        <StatusBadge
          title={widget.props.title}
          data={widget.props.data}
        />
      )

    case 'ALERT':
      return (
        <AlertWidget
          title={widget.props.title}
          description={widget.props.description}
          riskLevel={widget.props.risk_level}
          actions={widget.props.actions}
          onAction={handleCommand}
        />
      )

    case 'FORM':
    case 'CHART':
    case 'TIMELINE':
      return (
        <div className="p-4 bg-gray-50 text-gray-600 rounded-lg">
          Widget type "{widget.widget_type}" coming soon
        </div>
      )

    default:
      return (
        <div className="p-4 bg-yellow-50 text-yellow-700 rounded-lg">
          Unknown widget type: {widget.widget_type}
        </div>
      )
  }
}

export default GenUIRenderer
