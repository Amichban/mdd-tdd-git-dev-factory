/**
 * StatusBadge - Renders status badges from GenUI Contract.
 */

'use client'

import React from 'react'

interface StatusBadgeProps {
  title?: string
  data?: {
    status?: string
    last_run?: string
    count?: number
  }
}

export function StatusBadge({ title, data }: StatusBadgeProps) {
  const getStatusColor = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'success':
      case 'healthy':
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'warning':
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800'
      case 'error':
      case 'failed':
      case 'critical':
        return 'bg-red-100 text-red-800'
      case 'running':
      case 'pending':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="inline-flex items-center gap-2">
      {title && (
        <span className="text-sm text-gray-600">{title}:</span>
      )}
      <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(data?.status)}`}>
        {data?.status || 'Unknown'}
      </span>
      {data?.last_run && (
        <span className="text-xs text-gray-500">
          {new Date(data.last_run).toLocaleString()}
        </span>
      )}
      {data?.count !== undefined && (
        <span className="text-xs text-gray-500">
          ({data.count})
        </span>
      )}
    </div>
  )
}

export default StatusBadge
