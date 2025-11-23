/**
 * React hook for connecting to the Signal event stream.
 */

import { useState, useEffect, useCallback, useRef } from 'react'

interface Signal {
  event_id: string
  correlation_id: string
  timestamp: string
  source: {
    system: string
    component: string
    node_ref: string
  }
  type: string
  payload: any
}

interface UseSignalsOptions {
  autoConnect?: boolean
  filter?: {
    node_ref?: string
    type?: string
    system?: string
  }
}

export function useSignals(options: UseSignalsOptions = {}) {
  const { autoConnect = true, filter } = options

  const [signals, setSignals] = useState<Signal[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)

  const connect = useCallback(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/events/ws'

    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        setError(null)

        // Send subscription filter if provided
        if (filter) {
          ws.send(JSON.stringify({ type: 'subscribe', filter }))
        }
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          // Handle different message types
          if (data.type === 'connected' || data.type === 'subscribed' || data.type === 'pong') {
            return
          }

          // Apply client-side filtering
          if (filter) {
            if (filter.node_ref && data.source?.node_ref !== filter.node_ref) return
            if (filter.type && data.type !== filter.type) return
            if (filter.system && data.source?.system !== filter.system) return
          }

          // Add to signals list
          setSignals((prev) => [...prev.slice(-99), data])
        } catch (e) {
          console.error('Failed to parse signal:', e)
        }
      }

      ws.onerror = () => {
        setError('WebSocket connection error')
        setIsConnected(false)
      }

      ws.onclose = () => {
        setIsConnected(false)
      }
    } catch (e) {
      setError('Failed to connect to WebSocket')
    }
  }, [filter])

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  const clearSignals = useCallback(() => {
    setSignals([])
  }, [])

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [autoConnect, connect, disconnect])

  // Send ping to keep connection alive
  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  return {
    signals,
    isConnected,
    error,
    connect,
    disconnect,
    clearSignals,
  }
}

export default useSignals
