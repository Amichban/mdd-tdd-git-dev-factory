'use client'

import React from 'react'

interface TimelineEvent {
  id: string
  timestamp: string
  title: string
  description?: string
  type?: 'info' | 'success' | 'warning' | 'error'
}

interface TimelineWidgetProps {
  title: string
  events: TimelineEvent[]
  maxEvents?: number
}

export function TimelineWidget({
  title,
  events,
  maxEvents = 10
}: TimelineWidgetProps) {
  const displayEvents = events.slice(0, maxEvents)

  const getTypeStyles = (type?: string) => {
    switch (type) {
      case 'success':
        return {
          dot: 'bg-green-500',
          bg: 'bg-green-50 dark:bg-green-900/20',
          border: 'border-green-200 dark:border-green-800',
          text: 'text-green-700 dark:text-green-400'
        }
      case 'warning':
        return {
          dot: 'bg-yellow-500',
          bg: 'bg-yellow-50 dark:bg-yellow-900/20',
          border: 'border-yellow-200 dark:border-yellow-800',
          text: 'text-yellow-700 dark:text-yellow-400'
        }
      case 'error':
        return {
          dot: 'bg-red-500',
          bg: 'bg-red-50 dark:bg-red-900/20',
          border: 'border-red-200 dark:border-red-800',
          text: 'text-red-700 dark:text-red-400'
        }
      default:
        return {
          dot: 'bg-blue-500',
          bg: 'bg-blue-50 dark:bg-blue-900/20',
          border: 'border-blue-200 dark:border-blue-800',
          text: 'text-blue-700 dark:text-blue-400'
        }
    }
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now.getTime() - date.getTime()
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)

      if (minutes < 1) return 'Just now'
      if (minutes < 60) return `${minutes}m ago`
      if (hours < 24) return `${hours}h ago`
      if (days < 7) return `${days}d ago`

      return date.toLocaleDateString()
    } catch {
      return timestamp
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>

      {displayEvents.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400 text-center py-4">
          No events to display
        </p>
      ) : (
        <div className="space-y-4">
          {displayEvents.map((event, index) => {
            const styles = getTypeStyles(event.type)
            const isLast = index === displayEvents.length - 1

            return (
              <div key={event.id} className="relative flex gap-4">
                {/* Timeline line and dot */}
                <div className="flex flex-col items-center">
                  <div className={`w-3 h-3 rounded-full ${styles.dot} flex-shrink-0`} />
                  {!isLast && (
                    <div className="w-0.5 h-full bg-gray-200 dark:bg-gray-700 mt-1" />
                  )}
                </div>

                {/* Event content */}
                <div className={`flex-1 pb-4 ${isLast ? '' : ''}`}>
                  <div className={`p-3 rounded-lg border ${styles.bg} ${styles.border}`}>
                    <div className="flex items-start justify-between gap-2">
                      <h4 className={`font-medium text-sm ${styles.text}`}>
                        {event.title}
                      </h4>
                      <span className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                        {formatTimestamp(event.timestamp)}
                      </span>
                    </div>
                    {event.description && (
                      <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        {event.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {events.length > maxEvents && (
        <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-2">
          Showing {maxEvents} of {events.length} events
        </p>
      )}
    </div>
  )
}

export default TimelineWidget
