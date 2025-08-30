# Complete Guide to Microorganisms Project - Excellenteam 2025

## Executive Summary

This project involves developing a complete application (backend + frontend) to analyze and visualize microbial composition from ~700K environmental samples. Students will work with real microbiome data from different environments (human gut, soil, marine water, etc.) and create an interactive tool to explore this data.

## Learning Objectives

### Technical
- **Data Science**: Create data-driven products
- **Data Engineering**: Work with massive tables (700K rows, thousands of columns)
- **User Experience**: Design user-friendly interfaces
- **Full-Stack Development**: Integrated Backend + Frontend

### Conceptual
- **Interdisciplinarity**: Work outside CS comfort zone
- **Biology**: Understand microbiomes and taxonomy
- **Data Analysis**: Exploration, cleaning, and aggregation

## Data Structure

### Main Files
1. **Microbial Composition** (5 files):
   - `summary.phylum.csv.gz` - 204 phyla
   - `summary.class.csv.gz` - 638 classes
   - `summary.order.csv.gz` - 2,164 orders
   - `summary.family.csv.gz` - 5,932 families
   - `summary.genus.csv.gz` - 29,405 genera

2. **Metadata** (2 files):
   - `biorun-metadata.csv.gz` - Experiment info (700K rows)
   - `biosample-metadata.csv.gz` - Sample info

3. **Taxonomy** (1 file):
   - `gtdb_taxonomy.tsv.gz` - 143,614 complete species

### Data Format

#### Microbial Composition
```csv
biorun,unassigned,d__Bacteria;p__Pseudomonadota,d__Bacteria;p__Actinomycetota,...
DRR070900,1.13,0.67,9.84,...
DRR070907,0.87,0.63,33.03,...
```
- Each row = one biorun (experiment)
- Each column = one taxon
- Values = relative abundance (sum to ~100%)

#### Biorun Metadata
Key columns:
- `run_accession`: Biorun ID
- `organism_name`: Environment type (**KEY FOR THE PROJECT**)
- `biosample`: Biological sample ID

#### Most Common Environments
```
168,279 - human gut metagenome
63,000 - metagenome (genérico)
48,630 - gut metagenome
36,570 - soil metagenome
25,004 - human metagenome
20,429 - mouse gut metagenome
```

## Implementation Phases

### Phase 1: Basic Backend ⭐
**Goal**: API that returns average composition per environment at phylum level

**Specific tasks**:
1. **Data loading**:
   ```python
   import pandas as pd
   phylum_data = pd.read_csv('summary.phylum.csv.gz')
   metadata = pd.read_csv('biorun-metadata.csv.gz')
   ```

2. **Exploratory Data Analysis (EDA)**:
   - Count bioruns per environment
   - Verify that percentages sum to ~100%
   - Identify environments with sufficient samples (n > 100)

3. **Data joining**:
   ```python
   # Connect metadata with composition data
   merged = phylum_data.merge(metadata[['run_accession', 'organism_name']], 
                              left_on='biorun', right_on='run_accession')
   ```

4. **Calculate averages**:
   ```python
   # Average per environment
   env_composition = merged.groupby('organism_name').mean()
   ```

5. **Simple API**:
   ```python
   from flask import Flask, jsonify
   
   @app.route('/composition/<environment>')
   def get_composition(environment):
       # Return average composition for the environment
       return jsonify(composition_data)
   ```

**Expected challenges**:
- Memory: ~1.5GB compressed files
- Missing data: Not all bioruns have metadata
- Inconsistent environment names

### Phase 2: Simple Frontend ⭐⭐
**Goal**: Web interface that consumes the backend

**Specific tasks**:
1. **Environment list**:
   ```javascript
   fetch('/api/environments')
     .then(response => response.json())
     .then(environments => populateDropdown(environments))
   ```

2. **Visualization**:
   - Bar chart or pie chart
   - Use libraries like Chart.js, D3.js, or Plotly
   - Show only the most abundant phyla (>1%)

3. **Backend-frontend communication**:
   - REST API
   - Error handling
   - Loading states

**Suggested technologies**:
- **Backend**: Flask/FastAPI (Python) or Express (Node.js)
- **Frontend**: React, Vue, or vanilla JS
- **Visualization**: Chart.js, Plotly, D3.js

### Phase 3: Precision Improvement ⭐⭐⭐
**Goal**: Use biosample metadata for better predictions

**Specific tasks**:
1. **Explore biosample metadata**:
   ```python
   biosample_meta = pd.read_csv('biosample-metadata.csv.gz')
   print(biosample_meta.columns)  # Thousands of possible columns
   ```

2. **Handling messy data**:
   - Duplicate columns: 'latitude', 'lat-lon', '_latitude'
   - Extensive missing values
   - Data normalization

3. **Feature engineering**:
   - Extract geographic coordinates
   - Identify relevant metadata per environment
   - Create feature categories

4. **Improvement algorithms**:
   - Clustering by features
   - Conditional filters
   - Weighted averages based on similarity

**Improvement example**:
```python
# Instead of simple average:
soil_avg = soil_samples.mean()

# Location-weighted average:
if lat and lon:
    nearby_samples = find_nearby_samples(lat, lon, soil_samples)
    soil_avg = nearby_samples.mean()
```

### Phase 4: Specific Taxonomic Levels ⭐⭐⭐⭐
**Goal**: Extend to genus, family, order, class

**Technical challenges**:
1. **Sparse tables**:
   - Genus: 29,405 columns
   - Many values = 0
   - Memory and performance issues

2. **Solutions**:
   ```python
   # Use sparse matrices
   from scipy.sparse import csr_matrix
   
   # Filter relevant columns
   abundant_genera = (genus_data > 0.1).sum() > 100
   filtered_data = genus_data.loc[:, abundant_genera]
   ```

3. **Scalable API**:
   ```python
   @app.route('/composition/<environment>/<level>')
   def get_composition(environment, level):
       # level: phylum, class, order, family, genus
       return get_composition_by_level(environment, level)
   ```

### Advanced Phases ⭐⭐⭐⭐⭐

#### Geolocation
- Frontend: Detect user location
- Backend: Find geographically nearby samples
- Visualization: Interactive maps

#### Free Text Search
- NLP for environment matching
- Semantic similarity: "beach" → "marine metagenome"
- Automatic suggestions

#### AI for Parameter Estimation
- Machine Learning to predict temperature by coordinates
- Models to estimate pH, salinity, etc.
- Integration with climate APIs

## Recommended Technical Architecture

### Backend
```
├── app.py                 # Main API
├── data_loader.py         # Data loading and processing
├── composition_analyzer.py # Calculation logic
├── models/               # Data models
├── utils/                # Helper functions
└── tests/                # Unit tests
```

### Frontend
```
├── src/
│   ├── components/       # React/Vue components
│   ├── services/         # API calls
│   ├── utils/           # Helpers
│   └── pages/           # Páginas principales
├── public/              # Static assets
└── package.json         # Dependencies
```

### Database (Optional)
- **SQLite**: For small projects
- **PostgreSQL**: For larger data
- **Redis**: Cache for frequent results

## Tips for Mentors

### Project Management
1. **Start simple**: Phase 1 with hardcoded data
2. **Rapid iteration**: Frequent deploy for feedback
3. **Documentation**: Clear README with setup instructions
4. **Git workflow**: Branches per feature

### Common Debugging
1. **Memory**: Use chunking for large files
2. **Performance**: Implement cache early
3. **Data quality**: Verify joins and missing values
4. **Cross-origin**: Configure CORS correctly

### Evaluation
- **Functionality**: Does it work end-to-end?
- **Code**: Is it well structured?
- **UX**: Is it easy to use?
- **Scalability**: Can it handle more data?

## Technical Resources

### Python Libraries
```python
pandas          # Data manipulation
numpy           # Numerical computing
flask/fastapi   # Web framework
scipy           # Sparse matrices
matplotlib      # Basic plotting
plotly          # Interactive plots
```

### JavaScript Libraries
```javascript
react/vue       // UI framework
axios           // HTTP client
chart.js        // Charts
leaflet         // Maps
lodash          // Utilities
```

### Tools
- **Development**: Jupyter notebooks for EDA
- **Testing**: pytest (Python), jest (JavaScript)
- **Deployment**: Docker, Heroku, Vercel
- **Monitoring**: Simple logging initially

## Next Steps for Students

1. **Initial setup** (1-2 days):
   - Download and explore data
   - Setup environment (Python + JS)
   - Basic EDA in Jupyter

2. **MVP Backend** (3-5 days):
   - API that returns hardcoded data
   - Implement basic endpoint
   - Manual testing

3. **MVP Frontend** (3-5 days):
   - Simple interface with dropdown
   - Basic chart
   - Backend integration

4. **Iteration and improvement** (rest of project):
   - Add functionalities by priority
   - Progressively improve UX
   - Optimize performance

The project is designed to be challenging but achievable, with learning opportunities at each phase!
