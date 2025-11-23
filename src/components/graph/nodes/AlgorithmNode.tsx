'use client'

import React, { memo } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { Cpu } from 'lucide-react'

interface AlgorithmNodeData {
  label: string
  description?: string
  nodeType: string
  status: string
  color: string
  metadata?: {
    type?: string
  }
}

export const AlgorithmNode = memo(({ data, selected }: NodeProps<AlgorithmNodeData>) => {
  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 bg-white dark:bg-gray-800 shadow-md
        min-w-[180px] transition-all
        ${selected ? 'ring-2 ring-blue-500' : ''}
      `}
      style={{ borderColor: data.color }}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3"
        style={{ background: data.color }}
      />

      <div className="flex items-center gap-2 mb-1">
        <Cpu className="w-4 h-4" style={{ color: data.color }} />
        <span className="font-semibold text-sm">{data.label}</span>
      </div>

      {data.description && (
        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
          {data.description}
        </p>
      )}

      <div className="mt-2 flex items-center justify-between">
        <span
          className="text-xs px-2 py-0.5 rounded"
          style={{ backgroundColor: `${data.color}20`, color: data.color }}
        >
          ALGORITHM
        </span>
        {data.metadata?.type && (
          <span className="text-xs text-gray-500">
            {data.metadata.type}
          </span>
        )}
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3"
        style={{ background: data.color }}
      />
    </div>
  )
})

AlgorithmNode.displayName = 'AlgorithmNode'
