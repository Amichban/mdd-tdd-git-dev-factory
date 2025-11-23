/**
 * ActionCard - Renders action cards from GenUI Contract.
 */

'use client'

import React, { useState } from 'react'
import { GenUIAction } from './GenUIRenderer'

interface ActionCardProps {
  title?: string
  description?: string
  riskLevel?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  actions?: GenUIAction[]
  onAction: (command: string, params: Record<string, any>) => void
}

export function ActionCard({
  title,
  description,
  riskLevel,
  actions = [],
  onAction,
}: ActionCardProps) {
  const [confirming, setConfirming] = useState<string | null>(null)

  const getRiskColor = (level?: string) => {
    switch (level) {
      case 'CRITICAL': return 'border-red-500 bg-red-50'
      case 'HIGH': return 'border-orange-500 bg-orange-50'
      case 'MEDIUM': return 'border-yellow-500 bg-yellow-50'
      case 'LOW': return 'border-green-500 bg-green-50'
      default: return 'border-gray-200 bg-white'
    }
  }

  const getButtonStyle = (style?: string) => {
    switch (style) {
      case 'PRIMARY':
        return 'bg-blue-600 text-white hover:bg-blue-700'
      case 'SECONDARY':
        return 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      case 'DANGER':
        return 'bg-red-600 text-white hover:bg-red-700'
      case 'GHOST':
        return 'bg-transparent text-gray-600 hover:bg-gray-100'
      default:
        return 'bg-blue-600 text-white hover:bg-blue-700'
    }
  }

  const handleAction = (action: GenUIAction) => {
    if (action.confirm && confirming !== action.command) {
      setConfirming(action.command)
      return
    }
    setConfirming(null)
    onAction(action.command, action.params || {})
  }

  return (
    <div className={`rounded-lg border-l-4 p-4 shadow-sm ${getRiskColor(riskLevel)}`}>
      {title && (
        <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      )}
      {description && (
        <p className="text-sm text-gray-600 mb-4">{description}</p>
      )}

      {riskLevel && (
        <div className="mb-4">
          <span className={`text-xs font-medium px-2 py-1 rounded ${
            riskLevel === 'CRITICAL' ? 'bg-red-100 text-red-800' :
            riskLevel === 'HIGH' ? 'bg-orange-100 text-orange-800' :
            riskLevel === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
            'bg-green-100 text-green-800'
          }`}>
            {riskLevel} Risk
          </span>
        </div>
      )}

      {actions.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={() => handleAction(action)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${getButtonStyle(action.style)}`}
            >
              {confirming === action.command ? 'Confirm?' : action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default ActionCard
