'use client'

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'
import { Bar, Pie } from 'react-chartjs-2'
import { useState } from 'react'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

interface CompositionData {
  [taxon: string]: number
}

interface CompositionChartProps {
  data: CompositionData
}

export default function CompositionChart({ data }: CompositionChartProps) {
  const [chartType, setChartType] = useState<'bar' | 'pie'>('bar')

  // Filter out low abundance taxa and prepare data
  const filteredData = Object.entries(data)
    .filter(([_, abundance]) => abundance > 1) // Only show taxa > 1%
    .sort(([, a], [, b]) => b - a) // Sort by abundance

  const labels = filteredData.map(([taxon]) => {
    // Simplify taxon names for display
    const parts = taxon.split(';')
    const phylum = parts.find(part => part.startsWith('p__'))
    return phylum ? phylum.replace('p__', '') : taxon
  })

  const values = filteredData.map(([, abundance]) => abundance)

  const colors = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6366F1',
    '#14B8A6', '#F0B90B', '#8B5A2B', '#6B7280', '#059669'
  ]

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Relative Abundance (%)',
        data: values,
        backgroundColor: colors.slice(0, values.length),
        borderColor: colors.slice(0, values.length),
        borderWidth: 1,
      },
    ],
  }

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
        display: chartType === 'pie',
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.label}: ${context.parsed.y || context.parsed}%`
          }
        }
      }
    },
    scales: chartType === 'bar' ? {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Relative Abundance (%)'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Phylum'
        }
      }
    } : undefined,
  }

  return (
    <div className="space-y-4">
      {/* Chart Type Selector */}
      <div className="flex space-x-2">
        <button
          onClick={() => setChartType('bar')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            chartType === 'bar'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          📊 Bar Chart
        </button>
        <button
          onClick={() => setChartType('pie')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            chartType === 'pie'
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          🥧 Pie Chart
        </button>
      </div>

      {/* Chart */}
      <div className="h-96">
        {chartType === 'bar' ? (
          <Bar data={chartData} options={options} />
        ) : (
          <Pie data={chartData} options={options} />
        )}
      </div>

      {/* Summary */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="font-medium text-gray-800 mb-2">Summary:</h4>
        <p className="text-sm text-gray-600">
          Showing {filteredData.length} most abundant phyla ({">"} 1% relative abundance).
          Total represented: {values.reduce((sum, val) => sum + val, 0).toFixed(1)}%
        </p>
      </div>
    </div>
  )
}
