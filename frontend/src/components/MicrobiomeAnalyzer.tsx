'use client'

import { useState } from 'react'
import EnvironmentSelector from './EnvironmentSelector'
import CompositionChart from './CompositionChart'
import StatsCard from './StatsCard'
import { mockEnvironments, mockCompositionData } from '@/data/mockData'

export default function MicrobiomeAnalyzer() {
  const [selectedEnvironment, setSelectedEnvironment] = useState<string>('')
  const [loading, setLoading] = useState(false)

  const handleEnvironmentChange = async (environment: string) => {
    setLoading(true)
    setSelectedEnvironment(environment)
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 800))
    setLoading(false)
  }

  const currentData = selectedEnvironment ? mockCompositionData[selectedEnvironment] : null
  const environmentInfo = selectedEnvironment ? mockEnvironments.find(env => env.name === selectedEnvironment) : null

  return (
    <div className="space-y-6">
      {/* Environment Selection */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold mb-4 text-gray-800">Select Environment</h2>
        <EnvironmentSelector
          environments={mockEnvironments}
          selectedEnvironment={selectedEnvironment}
          onEnvironmentChange={handleEnvironmentChange}
          loading={loading}
        />
      </div>

      {/* Environment Info */}
      {environmentInfo && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatsCard
            title="Total Samples"
            value={environmentInfo.sampleCount.toLocaleString()}
            icon="🧪"
            color="blue"
          />
          <StatsCard
            title="Environment Type"
            value={environmentInfo.type}
            icon="🌍"
            color="green"
          />
          <StatsCard
            title="Taxonomic Level"
            value="Phylum"
            icon="🔬"
            color="purple"
          />
        </div>
      )}

      {/* Composition Chart */}
      {currentData && !loading && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">
            Microbial Composition - {selectedEnvironment}
          </h3>
          <CompositionChart data={currentData} />
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing microbial composition...</p>
        </div>
      )}

      {/* Instructions */}
      {!selectedEnvironment && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">How to use:</h3>
          <ol className="list-decimal list-inside space-y-1 text-blue-700">
            <li>Select an environment from the dropdown above</li>
            <li>View the microbial composition chart</li>
            <li>Explore different environments to compare compositions</li>
          </ol>
          <p className="text-sm text-blue-600 mt-3">
            This is a demo showing what students need to build for their project.
          </p>
        </div>
      )}
    </div>
  )
}
