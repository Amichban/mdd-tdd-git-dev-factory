/**
 * DataTable - Renders data tables from GenUI Contract.
 */

'use client'

import React from 'react'
import { GenUIAction, GenUIColumn } from './GenUIRenderer'

interface DataTableProps {
  title?: string
  columns: GenUIColumn[]
  data: any[]
  actions?: GenUIAction[]
  onAction: (command: string, params: Record<string, any>) => void
}

export function DataTable({
  title,
  columns,
  data,
  actions = [],
  onAction,
}: DataTableProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {title && (
        <div className="px-4 py-3 border-b border-gray-200">
          <h3 className="font-semibold text-gray-900">{title}</h3>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide"
                >
                  {col.label}
                </th>
              ))}
              {actions.length > 0 && (
                <th className="px-4 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wide">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {columns.map((col) => (
                  <td key={col.key} className="px-4 py-3 text-sm text-gray-700">
                    {formatCellValue(row[col.key], col.type)}
                  </td>
                ))}
                {actions.length > 0 && (
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-2">
                      {actions.map((action, actionIndex) => (
                        <button
                          key={actionIndex}
                          onClick={() => onAction(action.command, { ...action.params, row })}
                          className="text-sm text-blue-600 hover:text-blue-800"
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.length === 0 && (
        <div className="px-4 py-8 text-center text-gray-500">
          No data available
        </div>
      )}
    </div>
  )
}

function formatCellValue(value: any, type?: string): string {
  if (value === null || value === undefined) {
    return '-'
  }

  switch (type) {
    case 'date':
      return new Date(value).toLocaleDateString()
    case 'datetime':
      return new Date(value).toLocaleString()
    case 'boolean':
      return value ? 'Yes' : 'No'
    case 'json':
      return JSON.stringify(value)
    default:
      return String(value)
  }
}

export default DataTable
