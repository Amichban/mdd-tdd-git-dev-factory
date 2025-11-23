'use client'

import React, { useCallback, useMemo } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
  NodeTypes,
  Panel,
} from 'reactflow'
import 'reactflow/dist/style.css'

import { EntityNode } from './nodes/EntityNode'
import { WorkflowNode } from './nodes/WorkflowNode'
import { AlgorithmNode } from './nodes/AlgorithmNode'

// Custom node types
const nodeTypes: NodeTypes = {
  entity: EntityNode,
  workflow: WorkflowNode,
  algorithm: AlgorithmNode,
}

// Node type colors
const nodeColors: Record<string, string> = {
  ASSET: '#3B82F6',      // blue
  WORKFLOW: '#10B981',   // green
  ALGORITHM: '#8B5CF6',  // purple
  RULE: '#F59E0B',       // amber
  SKILL: '#EC4899',      // pink
  PIPELINE: '#06B6D4',   // cyan
  SOURCE: '#6366F1',     // indigo
}

interface GraphNode {
  id: string
  type: string
  label: string
  description?: string
  status?: string
  metadata?: Record<string, unknown>
}

interface GraphEdge {
  id: string
  source: string
  target: string
  relationship: string
}

interface OntologyGraphProps {
  nodes: GraphNode[]
  edges: GraphEdge[]
  onNodeClick?: (node: GraphNode) => void
  onEdgeClick?: (edge: GraphEdge) => void
}

export function OntologyGraph({
  nodes: graphNodes,
  edges: graphEdges,
  onNodeClick,
  onEdgeClick,
}: OntologyGraphProps) {
  // Convert graph nodes to React Flow nodes
  const initialNodes: Node[] = useMemo(() => {
    return graphNodes.map((node, index) => {
      // Auto-layout in a grid
      const cols = 4
      const row = Math.floor(index / cols)
      const col = index % cols

      return {
        id: node.id,
        type: node.type === 'WORKFLOW' ? 'workflow'
            : node.type === 'ALGORITHM' ? 'algorithm'
            : 'entity',
        position: { x: col * 300, y: row * 150 },
        data: {
          label: node.label,
          description: node.description,
          nodeType: node.type,
          status: node.status || 'active',
          color: nodeColors[node.type] || '#6B7280',
          metadata: node.metadata,
        },
      }
    })
  }, [graphNodes])

  // Convert graph edges to React Flow edges
  const initialEdges: Edge[] = useMemo(() => {
    return graphEdges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.relationship,
      type: 'smoothstep',
      animated: edge.relationship === 'triggers',
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20,
      },
      style: {
        strokeWidth: 2,
      },
    }))
  }, [graphEdges])

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        const graphNode = graphNodes.find((n) => n.id === node.id)
        if (graphNode) {
          onNodeClick(graphNode)
        }
      }
    },
    [graphNodes, onNodeClick]
  )

  const handleEdgeClick = useCallback(
    (_: React.MouseEvent, edge: Edge) => {
      if (onEdgeClick) {
        const graphEdge = graphEdges.find((e) => e.id === edge.id)
        if (graphEdge) {
          onEdgeClick(graphEdge)
        }
      }
    },
    [graphEdges, onEdgeClick]
  )

  return (
    <div className="w-full h-[600px] bg-gray-50 dark:bg-gray-900 rounded-lg border">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        <Controls />
        <MiniMap
          nodeColor={(node) => node.data.color || '#6B7280'}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
        <Background gap={12} size={1} />

        <Panel position="top-left" className="bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg">
          <h3 className="font-semibold mb-2">Legend</h3>
          <div className="space-y-1 text-sm">
            {Object.entries(nodeColors).map(([type, color]) => (
              <div key={type} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: color }}
                />
                <span>{type}</span>
              </div>
            ))}
          </div>
        </Panel>
      </ReactFlow>
    </div>
  )
}

export default OntologyGraph
