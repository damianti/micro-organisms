'use client'

interface Environment {
  name: string
  type: string
  sampleCount: number
  description: string
}

interface EnvironmentSelectorProps {
  environments: Environment[]
  selectedEnvironment: string
  onEnvironmentChange: (environment: string) => void
  loading: boolean
}

export default function EnvironmentSelector({
  environments,
  selectedEnvironment,
  onEnvironmentChange,
  loading
}: EnvironmentSelectorProps) {
  return (
    <div className="space-y-4">
      <select
        value={selectedEnvironment}
        onChange={(e) => onEnvironmentChange(e.target.value)}
        disabled={loading}
        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <option value="">Choose an environment...</option>
        {environments.map((env) => (
          <option key={env.name} value={env.name}>
            {env.name} ({env.sampleCount.toLocaleString()} samples)
          </option>
        ))}
      </select>

      {selectedEnvironment && !loading && (
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-gray-800 mb-2">Environment Details:</h4>
          <p className="text-gray-600 text-sm">
            {environments.find(env => env.name === selectedEnvironment)?.description}
          </p>
        </div>
      )}
    </div>
  )
}
