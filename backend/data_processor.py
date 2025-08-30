"""
🧬 Microbiome Data Processor
============================

This class handles all the logic for:
1. Loading data from compressed files
2. Cleaning and filtering data
3. Merging metadata with microbial composition  
4. Calculating average compositions by environment

Author: Microorganisms Project
Date: 2025
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import warnings

# Silence pandas warnings for cleaner output
warnings.filterwarnings('ignore')


class MicrobiomeDataProcessor:
    """
    Main processor for microbiome data.
    
    This class encapsulates all necessary logic to process 
    microbial composition data and metadata.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the processor.
        
        Args:
            data_path (str): Path to directory containing data files
        """
        self.data_path = data_path
        self.metadata = None
        self.phylum_data = None
        self.merged_data = None
        self.composition_by_env = None
        
        # Verify path exists
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"❌ Directory not found: {data_path}")
        
        print(f"✅ Processor initialized for: {data_path}")
    
    def load_metadata(self) -> pd.DataFrame:
        """
        Load biorun metadata from compressed file.
        
        Returns:
            pd.DataFrame: Biorun metadata
        """
        try:
            print("📂 Loading biorun metadata...")
            metadata_file = os.path.join(
                self.data_path, 
                'sandpiper1.0.0.condensed.biorun-metadata.csv.gz'
            )
            
            self.metadata = pd.read_csv(metadata_file)
            
            print(f"✅ Metadata loaded: {self.metadata.shape}")
            print(f"📊 Memory used: {self.metadata.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
            
            return self.metadata
            
        except Exception as e:
            print(f"❌ Error loading metadata: {e}")
            raise
    
    def load_phylum_data(self) -> pd.DataFrame:
        """
        Load microbial composition data at phylum level.
        
        Returns:
            pd.DataFrame: Phylum composition data
        """
        try:
            print("🧬 Loading composition data (phyla)...")
            phylum_file = os.path.join(
                self.data_path,
                'sandpiper1.0.0.condensed.summary.phylum.csv.gz'
            )
            
            self.phylum_data = pd.read_csv(phylum_file)
            
            print(f"✅ Phylum data loaded: {self.phylum_data.shape}")
            print(f"🧬 Phyla detected: {self.phylum_data.shape[1] - 1}")  # -1 for 'biorun' column
            print(f"📊 Memory used: {self.phylum_data.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
            
            return self.phylum_data
            
        except Exception as e:
            print(f"❌ Error loading phylum data: {e}")
            raise
    
    def filter_metagenomes(self) -> pd.DataFrame:
        """
        Filter only bioruns that are metagenomes (microbial communities).
        
        Returns:
            pd.DataFrame: Filtered metadata for metagenomes only
        """
        if self.metadata is None:
            raise ValueError("❌ Load metadata first with load_metadata()")
        
        print("🔬 Filtering metagenomes...")
        
        # Filter rows containing 'metagenome' in organism_name
        metagenome_mask = self.metadata['organism_name'].str.contains('metagenome', na=False)
        metagenomes = self.metadata[metagenome_mask].copy()
        
        print(f"📊 Total bioruns: {len(self.metadata):,}")
        print(f"🦠 Metagenome bioruns: {len(metagenomes):,}")
        print(f"📈 Metagenome percentage: {len(metagenomes)/len(self.metadata)*100:.1f}%")
        
        return metagenomes
    
    def merge_data(self) -> pd.DataFrame:
        """
        Merge metagenome metadata with composition data.
        
        Returns:
            pd.DataFrame: Merged data with metadata and composition
        """
        if self.metadata is None:
            raise ValueError("❌ Load metadata first with load_metadata()")
        if self.phylum_data is None:
            raise ValueError("❌ Load phylum data first with load_phylum_data()")
        
        print("🔗 Merging metadata with composition data...")
        
        # Filter metagenomes
        metagenomes = self.filter_metagenomes()
        
        # Select important metadata columns
        metadata_subset = metagenomes[['run_accession', 'organism_name', 'biosample']].copy()
        
        # Perform inner join
        self.merged_data = self.phylum_data.merge(
            metadata_subset,
            left_on='biorun',
            right_on='run_accession',
            how='inner'
        )
        
        print(f"✅ Data merged successfully: {self.merged_data.shape}")
        print(f"📉 Data lost in join: {len(self.phylum_data) - len(self.merged_data):,}")
        
        return self.merged_data
    
    def get_environment_stats(self, min_samples: int = 100) -> pd.Series:
        """
        Get statistics for environments with sufficient samples.
        
        Args:
            min_samples (int): Minimum number of samples per environment
            
        Returns:
            pd.Series: Sample count per environment (filtered)
        """
        if self.merged_data is None:
            raise ValueError("❌ Merge data first with merge_data()")
        
        print(f"📊 Analyzing environments with ≥{min_samples} samples...")
        
        # Count samples per environment
        env_counts = self.merged_data['organism_name'].value_counts()
        
        # Filter significant environments
        significant_envs = env_counts[env_counts >= min_samples]
        
        print(f"🌍 Total environments: {len(env_counts)}")
        print(f"✅ Significant environments: {len(significant_envs)}")
        print(f"📈 Useful samples: {significant_envs.sum():,} ({significant_envs.sum()/len(self.merged_data)*100:.1f}%)")
        
        return significant_envs
    
    def calculate_compositions(self, min_samples: int = 100) -> pd.DataFrame:
        """
        Calculate average composition per environment.
        
        Args:
            min_samples (int): Minimum number of samples per environment
            
        Returns:
            pd.DataFrame: Average compositions per environment
        """
        if self.merged_data is None:
            raise ValueError("❌ Merge data first with merge_data()")
        
        print("🧮 Calculating average compositions per environment...")
        
        # Get significant environments
        significant_envs = self.get_environment_stats(min_samples)
        
        # Filter data for significant environments only
        filtered_data = self.merged_data[
            self.merged_data['organism_name'].isin(significant_envs.index)
        ].copy()
        
        # Identify phylum columns
        phylum_columns = [col for col in self.merged_data.columns 
                         if col.startswith('d__') or col == 'unassigned']
        
        print(f"🧬 Processing {len(phylum_columns)} phyla")
        
        # Calculate statistics per environment
        self.composition_by_env = filtered_data.groupby('organism_name')[phylum_columns].agg([
            'mean',  # Average
            'std',   # Standard deviation  
            'count'  # Number of samples
        ]).round(4)
        
        print(f"✅ Compositions calculated for {len(self.composition_by_env)} environments")
        
        return self.composition_by_env
    
    def get_composition_for_environment(self, environment: str, min_abundance: float = 0.5) -> Dict:
        """
        Get composition for a specific environment.
        
        Args:
            environment (str): Environment name
            min_abundance (float): Minimum abundance to include phylum
            
        Returns:
            Dict: Environment composition with metadata
        """
        if self.composition_by_env is None:
            raise ValueError("❌ Calculate compositions first with calculate_compositions()")
        
        if environment not in self.composition_by_env.index:
            available_envs = list(self.composition_by_env.index)
            raise ValueError(f"❌ Environment '{environment}' not found. Available: {available_envs[:5]}...")
        
        # Get average composition
        mean_composition = self.composition_by_env.loc[environment].xs('mean', level=1)
        sample_count = int(self.composition_by_env.loc[environment].xs('count', level=1).iloc[0])
        
        # Filter abundant phyla
        abundant_phyla = mean_composition[mean_composition > min_abundance]
        
        # Prepare response
        composition_list = []
        for taxon, abundance in abundant_phyla.sort_values(ascending=False).items():
            # Clean taxon name for display
            display_name = self._clean_taxon_name(taxon)
            
            composition_list.append({
                'taxon': display_name,
                'taxon_full': taxon,
                'abundance': round(abundance, 2)
            })
        
        return {
            'environment': environment,
            'total_samples': sample_count,
            'composition': composition_list
        }
    
    def get_available_environments(self) -> List[Dict]:
        """
        Get list of available environments with metadata.
        
        Returns:
            List[Dict]: List of environments with information
        """
        if self.composition_by_env is None:
            raise ValueError("❌ Calculate compositions first with calculate_compositions()")
        
        environments = []
        for env in self.composition_by_env.index:
            sample_count = int(self.composition_by_env.loc[env].xs('count', level=1).iloc[0])
            environments.append({
                'name': env,
                'sample_count': sample_count
            })
        
        # Sort by sample count
        environments.sort(key=lambda x: x['sample_count'], reverse=True)
        
        return environments
    
    def _clean_taxon_name(self, taxon: str) -> str:
        """
        Clean taxon name for user display.
        
        Args:
            taxon (str): Full taxonomic name
            
        Returns:
            str: Clean name for display
        """
        if taxon == 'unassigned':
            return 'Unassigned'
        
        # Extract domain and phylum: d__Bacteria;p__Pseudomonadota -> Bacteria - Pseudomonadota
        parts = taxon.split(';')
        if len(parts) >= 2:
            domain = parts[0].replace('d__', '')
            phylum = parts[1].replace('p__', '')
            return f"{domain} - {phylum}"
        else:
            # If only domain
            return taxon.replace('d__', '')
    
    def validate_data_integrity(self) -> Dict:
        """
        Validate integrity of loaded data.
        
        Returns:
            Dict: Validation results
        """
        if self.phylum_data is None:
            raise ValueError("❌ Load phylum data first")
        
        print("🔍 Validating data integrity...")
        
        # Get abundance columns
        abundance_columns = [col for col in self.phylum_data.columns if col != 'biorun']
        
        # Calculate row sums
        row_sums = self.phylum_data[abundance_columns].sum(axis=1)
        
        validation_results = {
            'mean_sum': round(row_sums.mean(), 2),
            'std_sum': round(row_sums.std(), 2),
            'min_sum': round(row_sums.min(), 2),
            'max_sum': round(row_sums.max(), 2),
            'samples_near_100': len(row_sums[(row_sums >= 99) & (row_sums <= 101)]),
            'total_samples': len(row_sums)
        }
        
        print(f"📊 Average sum: {validation_results['mean_sum']}%")
        print(f"📊 Standard deviation: {validation_results['std_sum']}%")
        print(f"✅ Valid samples (99-101%): {validation_results['samples_near_100']:,}")
        
        return validation_results
    
    def process_all_data(self, min_samples: int = 100) -> bool:
        """
        Execute complete data processing pipeline.
        
        Args:
            min_samples (int): Minimum number of samples per environment
            
        Returns:
            bool: True if processing was successful
        """
        try:
            print("🚀 Starting complete data processing...")
            print("-" * 50)
            
            # 1. Load data
            self.load_metadata()
            self.load_phylum_data()
            
            # 2. Validate integrity
            self.validate_data_integrity()
            
            # 3. Process
            self.merge_data()
            self.calculate_compositions(min_samples)
            
            print("-" * 50)
            print("✅ Processing completed successfully!")
            
            # Final statistics
            envs = self.get_available_environments()
            print(f"🌍 Environments processed: {len(envs)}")
            print(f"📊 Total useful samples: {sum(env['sample_count'] for env in envs):,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
            return False


# Independent utility functions
def quick_analysis(data_path: str) -> Dict:
    """
    Quick analysis of data without complete processing.
    
    Args:
        data_path (str): Path to data
        
    Returns:
        Dict: Statistical summary
    """
    processor = MicrobiomeDataProcessor(data_path)
    
    # Only load metadata for quick analysis
    metadata = processor.load_metadata()
    metagenomes = processor.filter_metagenomes()
    
    env_counts = metagenomes['organism_name'].value_counts()
    
    return {
        'total_bioruns': len(metadata),
        'metagenome_bioruns': len(metagenomes),
        'unique_environments': len(env_counts),
        'top_environments': env_counts.head(10).to_dict()
    }


if __name__ == "__main__":
    # Basic test if run directly
    print("🧪 Testing data processor...")
    
    # Change this path according to your configuration
    data_path = "../Microbe-vis-data"
    
    if os.path.exists(data_path):
        processor = MicrobiomeDataProcessor(data_path)
        success = processor.process_all_data(min_samples=50)
        
        if success:
            print("\n🎉 Test completed successfully!")
        else:
            print("\n❌ Test failed")
    else:
        print(f"❌ Data directory not found: {data_path}")
        print("💡 Adjust the data_path variable in the code")