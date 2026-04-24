"""
Lee excels y genera archivos pacientes_contexto.csv (csv son los excels pero redactdos en texto) y outcomes.csv
Estos van a la carpeta de data procesada (esta es generada por nuestro código, la data raw es la que nos da el hospital (la q nos mandó gonzalo valenzuela))
"""

import pandas as pd
import numpy as np
import os

def generate_synthetic_data():
    output_path = 'data/processed/'
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    
    file_uc = 'data/raw/Antibiograma_2016_2025_UC.csv'
    file_hsr = 'data/raw/Antibiograma_2016_2025_HRS.csv'
    
    dfs = []
    
    # --- PROCESAR UC ---
    if os.path.exists(file_uc):
        print("⏳ Cargando UC...")
        # Forzamos el separador ';' y limpiamos nombres
        df_uc = pd.read_csv(file_uc, sep=';', on_bad_lines='skip', encoding='utf-8-sig')
        df_uc.columns = df_uc.columns.str.strip()
        
        # Mapeo de ID
        if 'FOLIO' in df_uc.columns:
            df_uc = df_uc.rename(columns={'FOLIO': 'ID_EPISODIO'})
            # Filtro Neumonía
            df_uc = df_uc[df_uc['TIPO MUESTRA'].str.contains('ASPIRADO', na=False, case=False)]
            dfs.append(df_uc)
            print(f"✅ UC procesado: {len(df_uc)} filas.")
        else:
            print(f"❌ Error: No se encontró la columna 'FOLIO' en UC. Columnas: {list(df_uc.columns)}")

    # --- PROCESAR HSR ---
    if os.path.exists(file_hsr):
        print("⏳ Cargando HSR...")
        df_hsr = pd.read_csv(file_hsr, sep=';', on_bad_lines='skip', encoding='utf-8-sig')
        df_hsr.columns = df_hsr.columns.str.strip()
        
        # Mapeo de ID
        if 'ORDEN ATENCION' in df_hsr.columns:
            df_hsr = df_hsr.rename(columns={'ORDEN ATENCION': 'ID_EPISODIO'})
            # Filtro Neumonía
            df_hsr = df_hsr[df_hsr['TIPO MUESTRA'].str.contains('TRAQUEAL', na=False, case=False)]
            dfs.append(df_hsr)
            print(f"✅ HSR procesado: {len(df_hsr)} filas.")
        else:
            print(f"❌ Error: No se encontró 'ORDEN ATENCION' en HSR. Columnas: {list(df_hsr.columns)}")

    if not dfs:
        print("❌ Error: No se pudo unificar ninguna base de datos.")
        return

    # Unión y Generación de Contexto
    df_maestro = pd.concat(dfs, ignore_index=True)
    df_maestro.to_csv(os.path.join(output_path, 'laboratorio_unificado.csv'), index=False)
    
    folios = df_maestro['ID_EPISODIO'].unique()
    
    # Crear tablas de contexto (Lo que el hospital no nos dio)
    df_contexto = pd.DataFrame({
        'ID_EPISODIO': folios,
        'FALLA_RENAL': np.random.choice([0, 1], size=len(folios), p=[0.7, 0.3]),
        'EPILEPSIA': np.random.choice([0, 1], size=len(folios), p=[0.95, 0.05])
    })
    df_outcomes = pd.DataFrame({
        'ID_EPISODIO': folios,
        'EXITO_CLINICO': np.random.choice([0, 1], size=len(folios), p=[0.2, 0.8])
    })

    df_contexto.to_csv(os.path.join(output_path, 'pacientes_contexto.csv'), index=False)
    df_outcomes.to_csv(os.path.join(output_path, 'outcomes_clinicos.csv'), index=False)
    print(f"\n🚀 NeoRX UNIFICADO: {len(folios)} episodios listos para el motor.")

if __name__ == "__main__":
    generate_synthetic_data()