# Microbiome Analyzer - Frontend Demo

This is a demo Next.js application that showcases what students need to build for the Excellenteam 2025 Microorganisms Project.

## Features

- 🦠 **Environment Selection**: Dropdown to choose from different environments (human gut, soil, marine, etc.)
- 📊 **Interactive Charts**: Bar and pie charts showing microbial composition at phylum level
- 📈 **Real-time Stats**: Sample counts and environment information
- 🎨 **Modern UI**: Clean, responsive design with Tailwind CSS
- ⚡ **Loading States**: Simulated API loading for better UX

## What Students Need to Build

This demo shows the **Phase 1 & 2** deliverables from the project guide:

### Phase 1 (Backend)
Students need to create a backend that:
- Loads the real dataset files (~700K samples)
- Connects biorun metadata with composition data
- Calculates average composition per environment
- Provides API endpoints for frontend consumption

### Phase 2 (Frontend)
Students need to create a frontend that:
- Consumes the backend API
- Shows environment selection
- Displays composition charts
- Handles loading and error states

## Mock Data

This demo uses mock data that simulates the real project data:
- **Environments**: Based on actual organism_name values from the dataset
- **Sample Counts**: Actual numbers from the biorun metadata
- **Compositions**: Realistic phylum-level abundances based on biological knowledge

## Running the Demo

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

## Tech Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Chart.js + react-chartjs-2**: Data visualization
- **Mock Data**: Simulates real backend responses

## Next Steps for Students

1. **Replace mock data** with real backend API calls
2. **Add more taxonomic levels** (class, order, family, genus)
3. **Implement geolocation features**
4. **Add advanced filtering and search**
5. **Optimize for large datasets**

## File Structure

```
src/
├── app/
│   └── page.tsx              # Main page
├── components/
│   ├── MicrobiomeAnalyzer.tsx # Main analyzer component
│   ├── EnvironmentSelector.tsx # Environment dropdown
│   ├── CompositionChart.tsx   # Chart visualization
│   └── StatsCard.tsx         # Statistics cards
└── data/
    └── mockData.ts           # Mock dataset
```

This serves as a reference implementation and starting point for the actual project!