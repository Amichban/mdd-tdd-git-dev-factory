'use client'

import React, { useCallback, useMemo } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  Panel,
} from 'reactflow'
import 'reactflow/dist/style.css'

interface PipelineStep {
  id: string
  name: string
  type: 'source' | 'transform' | 'sink' | 'decision' | 'parallel'
  status?: 'pending' | 'running' | 'completed' | 'failed'
  config?: Record<string, unknown>
}

interface PipelineConnection {
  from: string
  to: string
  condition?: string
}

interface PipelineGraphProps {
  name: string
  steps: PipelineStep[]
  connections: PipelineConnection[]
  onStepClick?: (step: PipelineStep) => void
}

const stepColors: Record<string, string> = {
  source: '#3B82F6',    // blue
  transform: '#10B981', // green
  sink: '#F59E0B',      // amber
  decision: '#8B5CF6',  // purple
  parallel: '#06B6D4',  // cyan
}

const statusColors: Record<string, string> = {
  pending: '#9CA3AF',
  running: '#3B82F6',
  completed: '#10B981',
  failed: '#EF4444',
}

export function PipelineGraph({
  name,
  steps,
  connections,
  onStepClick,
}: PipelineGraphProps) {
  // Convert pipeline steps to React Flow nodes
  const initialNodes: Node[] = useMemo(() => {
    return steps.map((step, index) => {
      // Horizontal layout
      return {
        id: step.id,
        position: { x: index * 250, y: 100 },
        data: {
          label: step.name,
          type: step.type,
          status: step.status || 'pending',
          config: step.config,
        },
        style: {
          background: 'white',
          border: `2px solid ${stepColors[step.type] || '#6B7280'}`,
          borderRadius: '8px',
          padding: '12px 16px',
          minWidth: '150px',
        },
      }
    })
  }, [steps])

  // Convert connections to React Flow edges
  const initialEdges: Edge[] = useMemo(() => {
    return connections.map((conn, index) => ({
      id: `e-${index}`,
      source: conn.from,
      target: conn.to,
      label: conn.condition,
      type: 'smoothstep',
      animated: true,
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 15,
        height: 15,
      },
      style: {
        strokeWidth: 2,
        stroke: '#6B7280',
      },
    }))
  }, [connections])

  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (onStepClick) {
        const step = steps.find((s) => s.id === node.id)
        if (step) {
          onStepClick(step)
        }
      }
    },
    [steps, onStepClick]
  )

  // Custom node renderer
  const nodeTypes = useMemo(
    () => ({
      default: ({ data }: { data: any }) => (
        <div className="text-center">
          <div className="font-semibold text-sm mb-1">{data.label}</div>
          <div className="flex items-center justify-center gap-2">
            <span
              className="text-xs px-2 py-0.5 rounded"
              style={{
                backgroundColor: `${stepColors[data.type]}20`,
                color: stepColors[data.type],
              }}
            >
              {data.type}
            </span>
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: statusColors[data.status] }}
              title={data.status}
            />
          </div>
        </div>
      ),
    }),
    []
  )

  return (
    <div className="w-full h-[400px] bg-gray-50 dark:bg-gray-900 rounded-lg border">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        <Controls />
        <Background gap={12} size={1} />

        <Panel position="top-left" className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg">
          <h3 className="font-semibold">{name}</h3>
          <p className="text-xs text-gray-500">{steps.length} steps</p>
        </Panel>

        <Panel position="top-right" className="bg-white dark:bg-gray-800 p-2 rounded-lg shadow-lg">
          <div className="flex gap-3 text-xs">
            {Object.entries(statusColors).map(([status, color]) => (
              <div key={status} className="flex items-center gap-1">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: color }}
                />
                <span>{status}</span>
              </div>
            ))}
          </div>
        </Panel>
      </ReactFlow>
    </div>
  )
}

export default PipelineGraph
