'use client'

import React from 'react'

interface ChartDataset {
  label: string
  data: number[]
  color?: string
}

interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

interface ChartWidgetProps {
  title: string
  type: 'line' | 'bar' | 'pie' | 'area'
  data: ChartData
  height?: number
}

export function ChartWidget({
  title,
  type,
  data,
  height = 200
}: ChartWidgetProps) {
  // Calculate chart dimensions
  const maxValue = Math.max(
    ...data.datasets.flatMap(ds => ds.data),
    1
  )

  const colors = [
    '#3B82F6', // blue
    '#10B981', // green
    '#F59E0B', // amber
    '#EF4444', // red
    '#8B5CF6', // purple
    '#EC4899', // pink
  ]

  const renderBarChart = () => {
    const barWidth = 100 / (data.labels.length * data.datasets.length + data.labels.length)
    const groupWidth = barWidth * data.datasets.length

    return (
      <div className="relative" style={{ height: `${height}px` }}>
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 bottom-6 w-10 flex flex-col justify-between text-xs text-gray-500">
          <span>{maxValue}</span>
          <span>{Math.round(maxValue / 2)}</span>
          <span>0</span>
        </div>

        {/* Chart area */}
        <div className="ml-12 h-full flex items-end justify-around pb-6">
          {data.labels.map((label, i) => (
            <div key={label} className="flex items-end gap-1">
              {data.datasets.map((dataset, j) => (
                <div
                  key={`${label}-${dataset.label}`}
                  className="transition-all duration-300 hover:opacity-80"
                  style={{
                    width: `${barWidth * 2}%`,
                    height: `${(dataset.data[i] / maxValue) * 100}%`,
                    backgroundColor: dataset.color || colors[j % colors.length],
                    minHeight: '2px'
                  }}
                  title={`${dataset.label}: ${dataset.data[i]}`}
                />
              ))}
            </div>
          ))}
        </div>

        {/* X-axis labels */}
        <div className="ml-12 flex justify-around text-xs text-gray-500">
          {data.labels.map(label => (
            <span key={label} className="truncate max-w-[60px]" title={label}>
              {label}
            </span>
          ))}
        </div>
      </div>
    )
  }

  const renderLineChart = () => {
    const points = data.datasets.map(dataset => {
      return dataset.data.map((value, i) => ({
        x: (i / (data.labels.length - 1)) * 100,
        y: 100 - (value / maxValue) * 100
      }))
    })

    return (
      <div className="relative" style={{ height: `${height}px` }}>
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 bottom-6 w-10 flex flex-col justify-between text-xs text-gray-500">
          <span>{maxValue}</span>
          <span>{Math.round(maxValue / 2)}</span>
          <span>0</span>
        </div>

        {/* Chart area */}
        <div className="ml-12 h-full relative pb-6">
          <svg className="w-full h-full" preserveAspectRatio="none">
            {data.datasets.map((dataset, i) => {
              const pathPoints = points[i]
              const d = pathPoints
                .map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
                .join(' ')

              return (
                <path
                  key={dataset.label}
                  d={d}
                  fill="none"
                  stroke={dataset.color || colors[i % colors.length]}
                  strokeWidth="2"
                />
              )
            })}
          </svg>
        </div>

        {/* X-axis labels */}
        <div className="ml-12 flex justify-between text-xs text-gray-500">
          {data.labels.map(label => (
            <span key={label} className="truncate max-w-[60px]" title={label}>
              {label}
            </span>
          ))}
        </div>
      </div>
    )
  }

  const renderPieChart = () => {
    const total = data.datasets[0]?.data.reduce((a, b) => a + b, 0) || 1
    let currentAngle = 0

    return (
      <div className="flex items-center justify-center" style={{ height: `${height}px` }}>
        <svg viewBox="0 0 100 100" className="w-32 h-32">
          {data.datasets[0]?.data.map((value, i) => {
            const angle = (value / total) * 360
            const startAngle = currentAngle
            const endAngle = currentAngle + angle
            currentAngle = endAngle

            const startRad = (startAngle - 90) * (Math.PI / 180)
            const endRad = (endAngle - 90) * (Math.PI / 180)

            const x1 = 50 + 40 * Math.cos(startRad)
            const y1 = 50 + 40 * Math.sin(startRad)
            const x2 = 50 + 40 * Math.cos(endRad)
            const y2 = 50 + 40 * Math.sin(endRad)

            const largeArc = angle > 180 ? 1 : 0

            return (
              <path
                key={data.labels[i]}
                d={`M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArc} 1 ${x2} ${y2} Z`}
                fill={colors[i % colors.length]}
                className="hover:opacity-80 transition-opacity"
              >
                <title>{`${data.labels[i]}: ${value}`}</title>
              </path>
            )
          })}
        </svg>

        {/* Legend */}
        <div className="ml-4 space-y-1">
          {data.labels.map((label, i) => (
            <div key={label} className="flex items-center text-xs">
              <div
                className="w-3 h-3 mr-2 rounded-sm"
                style={{ backgroundColor: colors[i % colors.length] }}
              />
              <span className="truncate max-w-[80px]">{label}</span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>

      {type === 'bar' && renderBarChart()}
      {(type === 'line' || type === 'area') && renderLineChart()}
      {type === 'pie' && renderPieChart()}

      {/* Legend for non-pie charts */}
      {type !== 'pie' && data.datasets.length > 1 && (
        <div className="mt-4 flex flex-wrap gap-4 justify-center">
          {data.datasets.map((dataset, i) => (
            <div key={dataset.label} className="flex items-center text-xs">
              <div
                className="w-3 h-3 mr-2 rounded-sm"
                style={{ backgroundColor: dataset.color || colors[i % colors.length] }}
              />
              <span>{dataset.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ChartWidget
