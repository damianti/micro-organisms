"""
🧬 Procesador de Datos de Microbioma
=====================================

Esta clase maneja toda la lógica para:
1. Cargar datos desde archivos comprimidos
2. Limpiar y filtrar datos
3. Unir metadatos con composición microbiana  
4. Calcular composiciones promedio por ambiente

Autor: Proyecto Microorganismos
Fecha: 2025
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import warnings

# Silenciar warnings de pandas para output más limpio
warnings.filterwarnings('ignore')


class MicrobiomeDataProcessor:
    """
    Procesador principal para datos de microbioma.
    
    Esta clase encapsula toda la lógica necesaria para procesar 
    datos de composición microbiana y metadatos.
    """
    
    def __init__(self, data_path: str):
        """
        Inicializar el procesador.
        
        Args:
            data_path (str): Ruta al directorio con archivos de datos
        """
        self.data_path = data_path
        self.metadata = None
        self.phylum_data = None
        self.merged_data = None
        self.composition_by_env = None
        
        # Verificar que la ruta existe
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"❌ Directorio no encontrado: {data_path}")
        
        print(f"✅ Procesador inicializado para: {data_path}")
    
    def load_metadata(self) -> pd.DataFrame:
        """
        Cargar metadatos de bioruns desde archivo comprimido.
        
        Returns:
            pd.DataFrame: Metadatos de bioruns
        """
        try:
            print("📂 Cargando metadatos de bioruns...")
            metadata_file = os.path.join(
                self.data_path, 
                'sandpiper1.0.0.condensed.biorun-metadata.csv.gz'
            )
            
            self.metadata = pd.read_csv(metadata_file)
            
            print(f"✅ Metadatos cargados: {self.metadata.shape}")
            print(f"📊 Memoria usada: {self.metadata.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
            
            return self.metadata
            
        except Exception as e:
            print(f"❌ Error cargando metadatos: {e}")
            raise
    
    def load_phylum_data(self) -> pd.DataFrame:
        """
        Cargar datos de composición microbiana a nivel de filo.
        
        Returns:
            pd.DataFrame: Datos de composición por filo
        """
        try:
            print("🧬 Cargando datos de composición (filos)...")
            phylum_file = os.path.join(
                self.data_path,
                'sandpiper1.0.0.condensed.summary.phylum.csv.gz'
            )
            
            self.phylum_data = pd.read_csv(phylum_file)
            
            print(f"✅ Datos de filos cargados: {self.phylum_data.shape}")
            print(f"🧬 Filos detectados: {self.phylum_data.shape[1] - 1}")  # -1 por columna 'biorun'
            print(f"📊 Memoria usada: {self.phylum_data.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
            
            return self.phylum_data
            
        except Exception as e:
            print(f"❌ Error cargando datos de filos: {e}")
            raise
    
    def filter_metagenomes(self) -> pd.DataFrame:
        """
        Filtrar solo bioruns que sean metagenomas (comunidades microbianas).
        
        Returns:
            pd.DataFrame: Metadatos filtrados solo para metagenomas
        """
        if self.metadata is None:
            raise ValueError("❌ Primero carga los metadatos con load_metadata()")
        
        print("🔬 Filtrando metagenomas...")
        
        # Filtrar filas que contengan 'metagenome' en organism_name
        metagenome_mask = self.metadata['organism_name'].str.contains('metagenome', na=False)
        metagenomes = self.metadata[metagenome_mask].copy()
        
        print(f"📊 Bioruns totales: {len(self.metadata):,}")
        print(f"🦠 Bioruns de metagenomas: {len(metagenomes):,}")
        print(f"📈 Porcentaje de metagenomas: {len(metagenomes)/len(self.metadata)*100:.1f}%")
        
        return metagenomes
    
    def merge_data(self) -> pd.DataFrame:
        """
        Unir metadatos de metagenomas con datos de composición.
        
        Returns:
            pd.DataFrame: Datos unidos con metadatos y composición
        """
        if self.metadata is None:
            raise ValueError("❌ Primero carga los metadatos con load_metadata()")
        if self.phylum_data is None:
            raise ValueError("❌ Primero carga los datos de filos con load_phylum_data()")
        
        print("🔗 Uniendo metadatos con datos de composición...")
        
        # Filtrar metagenomas
        metagenomes = self.filter_metagenomes()
        
        # Seleccionar columnas importantes de metadatos
        metadata_subset = metagenomes[['run_accession', 'organism_name', 'biosample']].copy()
        
        # Hacer inner join
        self.merged_data = self.phylum_data.merge(
            metadata_subset,
            left_on='biorun',
            right_on='run_accession',
            how='inner'
        )
        
        print(f"✅ Datos unidos exitosamente: {self.merged_data.shape}")
        print(f"📉 Datos perdidos en el join: {len(self.phylum_data) - len(self.merged_data):,}")
        
        return self.merged_data
    
    def get_environment_stats(self, min_samples: int = 100) -> pd.Series:
        """
        Obtener estadísticas de ambientes con suficientes muestras.
        
        Args:
            min_samples (int): Número mínimo de muestras por ambiente
            
        Returns:
            pd.Series: Conteo de muestras por ambiente (filtrado)
        """
        if self.merged_data is None:
            raise ValueError("❌ Primero une los datos con merge_data()")
        
        print(f"📊 Analizando ambientes con ≥{min_samples} muestras...")
        
        # Contar muestras por ambiente
        env_counts = self.merged_data['organism_name'].value_counts()
        
        # Filtrar ambientes significativos
        significant_envs = env_counts[env_counts >= min_samples]
        
        print(f"🌍 Ambientes totales: {len(env_counts)}")
        print(f"✅ Ambientes significativos: {len(significant_envs)}")
        print(f"📈 Muestras útiles: {significant_envs.sum():,} ({significant_envs.sum()/len(self.merged_data)*100:.1f}%)")
        
        return significant_envs
    
    def calculate_compositions(self, min_samples: int = 100) -> pd.DataFrame:
        """
        Calcular composición promedio por ambiente.
        
        Args:
            min_samples (int): Número mínimo de muestras por ambiente
            
        Returns:
            pd.DataFrame: Composiciones promedio por ambiente
        """
        if self.merged_data is None:
            raise ValueError("❌ Primero une los datos con merge_data()")
        
        print("🧮 Calculando composiciones promedio por ambiente...")
        
        # Obtener ambientes significativos
        significant_envs = self.get_environment_stats(min_samples)
        
        # Filtrar datos solo para ambientes significativos
        filtered_data = self.merged_data[
            self.merged_data['organism_name'].isin(significant_envs.index)
        ].copy()
        
        # Identificar columnas de filos
        phylum_columns = [col for col in self.merged_data.columns 
                         if col.startswith('d__') or col == 'unassigned']
        
        print(f"🧬 Procesando {len(phylum_columns)} filos")
        
        # Calcular estadísticas por ambiente
        self.composition_by_env = filtered_data.groupby('organism_name')[phylum_columns].agg([
            'mean',  # Promedio
            'std',   # Desviación estándar  
            'count'  # Número de muestras
        ]).round(4)
        
        print(f"✅ Composiciones calculadas para {len(self.composition_by_env)} ambientes")
        
        return self.composition_by_env
    
    def get_composition_for_environment(self, environment: str, min_abundance: float = 0.5) -> Dict:
        """
        Obtener composición de un ambiente específico.
        
        Args:
            environment (str): Nombre del ambiente
            min_abundance (float): Abundancia mínima para incluir filo
            
        Returns:
            Dict: Composición del ambiente con metadatos
        """
        if self.composition_by_env is None:
            raise ValueError("❌ Primero calcula las composiciones con calculate_compositions()")
        
        if environment not in self.composition_by_env.index:
            available_envs = list(self.composition_by_env.index)
            raise ValueError(f"❌ Ambiente '{environment}' no encontrado. Disponibles: {available_envs[:5]}...")
        
        # Obtener composición promedio
        mean_composition = self.composition_by_env.loc[environment].xs('mean', level=1)
        sample_count = int(self.composition_by_env.loc[environment].xs('count', level=1).iloc[0])
        
        # Filtrar filos abundantes
        abundant_phyla = mean_composition[mean_composition > min_abundance]
        
        # Preparar respuesta
        composition_list = []
        for taxon, abundance in abundant_phyla.sort_values(ascending=False).items():
            # Limpiar nombre del taxón para mostrar
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
        Obtener lista de ambientes disponibles con metadatos.
        
        Returns:
            List[Dict]: Lista de ambientes con información
        """
        if self.composition_by_env is None:
            raise ValueError("❌ Primero calcula las composiciones con calculate_compositions()")
        
        environments = []
        for env in self.composition_by_env.index:
            sample_count = int(self.composition_by_env.loc[env].xs('count', level=1).iloc[0])
            environments.append({
                'name': env,
                'sample_count': sample_count
            })
        
        # Ordenar por número de muestras
        environments.sort(key=lambda x: x['sample_count'], reverse=True)
        
        return environments
    
    def _clean_taxon_name(self, taxon: str) -> str:
        """
        Limpiar nombre de taxón para mostrar al usuario.
        
        Args:
            taxon (str): Nombre taxonómico completo
            
        Returns:
            str: Nombre limpio para mostrar
        """
        if taxon == 'unassigned':
            return 'No Asignado'
        
        # Extraer dominio y filo: d__Bacteria;p__Pseudomonadota -> Bacteria - Pseudomonadota
        parts = taxon.split(';')
        if len(parts) >= 2:
            domain = parts[0].replace('d__', '')
            phylum = parts[1].replace('p__', '')
            return f"{domain} - {phylum}"
        else:
            # Si solo hay dominio
            return taxon.replace('d__', '')
    
    def validate_data_integrity(self) -> Dict:
        """
        Validar integridad de los datos cargados.
        
        Returns:
            Dict: Resultados de validación
        """
        if self.phylum_data is None:
            raise ValueError("❌ Primero carga los datos de filos")
        
        print("🔍 Validando integridad de datos...")
        
        # Obtener columnas de abundancia
        abundance_columns = [col for col in self.phylum_data.columns if col != 'biorun']
        
        # Calcular sumas por fila
        row_sums = self.phylum_data[abundance_columns].sum(axis=1)
        
        validation_results = {
            'mean_sum': round(row_sums.mean(), 2),
            'std_sum': round(row_sums.std(), 2),
            'min_sum': round(row_sums.min(), 2),
            'max_sum': round(row_sums.max(), 2),
            'samples_near_100': len(row_sums[(row_sums >= 99) & (row_sums <= 101)]),
            'total_samples': len(row_sums)
        }
        
        print(f"📊 Suma promedio: {validation_results['mean_sum']}%")
        print(f"📊 Desviación estándar: {validation_results['std_sum']}%")
        print(f"✅ Muestras válidas (99-101%): {validation_results['samples_near_100']:,}")
        
        return validation_results
    
    def process_all_data(self, min_samples: int = 100) -> bool:
        """
        Ejecutar todo el pipeline de procesamiento.
        
        Args:
            min_samples (int): Número mínimo de muestras por ambiente
            
        Returns:
            bool: True si el procesamiento fue exitoso
        """
        try:
            print("🚀 Iniciando procesamiento completo de datos...")
            print("-" * 50)
            
            # 1. Cargar datos
            self.load_metadata()
            self.load_phylum_data()
            
            # 2. Validar integridad
            self.validate_data_integrity()
            
            # 3. Procesar
            self.merge_data()
            self.calculate_compositions(min_samples)
            
            print("-" * 50)
            print("✅ Procesamiento completado exitosamente!")
            
            # Estadísticas finales
            envs = self.get_available_environments()
            print(f"🌍 Ambientes procesados: {len(envs)}")
            print(f"📊 Total de muestras útiles: {sum(env['sample_count'] for env in envs):,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en procesamiento: {e}")
            return False


# Funciones de utilidad independientes
def quick_analysis(data_path: str) -> Dict:
    """
    Análisis rápido de los datos sin procesamiento completo.
    
    Args:
        data_path (str): Ruta a los datos
        
    Returns:
        Dict: Resumen estadístico
    """
    processor = MicrobiomeDataProcessor(data_path)
    
    # Solo cargar metadatos para análisis rápido
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
    # Test básico si se ejecuta directamente
    print("🧪 Test del procesador de datos...")
    
    # Cambiar esta ruta según tu configuración
    data_path = "../Microbe-vis-data"
    
    if os.path.exists(data_path):
        processor = MicrobiomeDataProcessor(data_path)
        success = processor.process_all_data(min_samples=50)
        
        if success:
            print("\n🎉 Test completado exitosamente!")
        else:
            print("\n❌ Test falló")
    else:
        print(f"❌ Directorio de datos no encontrado: {data_path}")
        print("💡 Ajusta la variable data_path en el código")
