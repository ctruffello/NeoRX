import numpy as np

def generar_ranking(df, bacteria, anio_min, anio_max, tipo_muestra):
    """Filtra datos y calcula el ranking ponderado por confianza estadística."""
    
    # Filtro dinámico según elección del usuario
    filtro = (
        (df['DETECCION FINAL'] == bacteria) & 
        (df['TIPO MUESTRA'] == tipo_muestra) & 
        (df['ANIO'] >= anio_min) & 
        (df['ANIO'] <= anio_max)
    )
    
    df_filtrado = df[filtro].copy()
    if df_filtrado.empty: return None, None

    # Lógica de Umbrales del Informe
    if tipo_muestra == "UROCULTIVO":
        # Umbral: E. coli > 50.000, otros > 10.000 [cite: 362]
        umbral_info = "Tratar E. coli si >50.000 UFC; otras si >10.000 UFC."
    else:
        # Umbral Aspirado: Tratar si > 100.000 UFC [cite: 363, 501]
        umbral_info = "Tratar solo si el recuento es >100.000 UFC."

    # Cálculo de estadísticas
    stats = df_filtrado.groupby('ANTIBIOTICO')['ESTADO'].agg(
        Total='count',
        Sensibles=lambda x: (x == 'S').sum()
    )
    
    stats['Susceptibilidad_%'] = (stats['Sensibles'] / stats['Total'] * 100).round(1)
    
    # Ponderación de Wilson (para que 100% con 2 casos baje en el ranking)
    stats['Puntaje_Clinico'] = stats['Susceptibilidad_%'] * (1 - 1 / np.sqrt(stats['Total']))
    stats['Fiabilidad'] = stats['Total'].apply(lambda x: 'ALTA' if x >= 30 else 'BAJA')

    resultado = stats.sort_values(by='Puntaje_Clinico', ascending=False)
    
    return resultado[['Susceptibilidad_%', 'Total', 'Fiabilidad']], umbral_info