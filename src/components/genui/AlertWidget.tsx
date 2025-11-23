/**
 * AlertWidget - Renders alert widgets from GenUI Contract.
 */

'use client'

import React from 'react'
import { GenUIAction } from './GenUIRenderer'

interface AlertWidgetProps {
  title?: string
  description?: string
  riskLevel?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  actions?: GenUIAction[]
  onAction: (command: string, params: Record<string, any>) => void
}

export function AlertWidget({
  title,
  description,
  riskLevel,
  actions = [],
  onAction,
}: AlertWidgetProps) {
  const getAlertStyle = (level?: string) => {
    switch (level) {
      case 'CRITICAL':
        return {
          bg: 'bg-red-50',
          border: 'border-red-400',
          icon: '🚨',
          titleColor: 'text-red-800',
          textColor: 'text-red-700',
        }
      case 'HIGH':
        return {
          bg: 'bg-orange-50',
          border: 'border-orange-400',
          icon: '⚠️',
          titleColor: 'text-orange-800',
          textColor: 'text-orange-700',
        }
      case 'MEDIUM':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-400',
          icon: '⚡',
          titleColor: 'text-yellow-800',
          textColor: 'text-yellow-700',
        }
      case 'LOW':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-400',
          icon: 'ℹ️',
          titleColor: 'text-blue-800',
          textColor: 'text-blue-700',
        }
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-400',
          icon: '📢',
          titleColor: 'text-gray-800',
          textColor: 'text-gray-700',
        }
    }
  }

  const style = getAlertStyle(riskLevel)

  return (
    <div className={`${style.bg} border-l-4 ${style.border} p-4 rounded-r-lg`}>
      <div className="flex items-start">
        <span className="text-xl mr-3">{style.icon}</span>
        <div className="flex-1">
          {title && (
            <h3 className={`font-semibold ${style.titleColor}`}>{title}</h3>
          )}
          {description && (
            <p className={`text-sm mt-1 ${style.textColor}`}>{description}</p>
          )}

          {actions.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {actions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => onAction(action.command, action.params || {})}
                  className={`px-3 py-1 text-sm rounded ${
                    action.style === 'PRIMARY'
                      ? `${style.bg} ${style.titleColor} border ${style.border} hover:opacity-80`
                      : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AlertWidget
