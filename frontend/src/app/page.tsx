import MicrobiomeAnalyzer from '@/components/MicrobiomeAnalyzer'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-8">
      <div className="max-w-6xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🦠 Microbiome Composition Analyzer
          </h1>
          <p className="text-lg text-gray-600">
            Explore microbial communities across different environments
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Excellenteam 2025 - Demo Application
          </p>
        </header>
        
        <MicrobiomeAnalyzer />
        
        <footer className="text-center mt-8 text-gray-500 text-sm">
          <p>Data based on ~700K biorun samples from various environments</p>
        </footer>
      </div>
    </main>
  )
}