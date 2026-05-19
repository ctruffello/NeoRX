"""
Módulo de Alertas Epidemiológicas - Análisis de Tendencias Móviles
"""
import pandas as pd
import numpy as np
from src.base_de_datos import conectar

def detectar_alertas_epidemiologicas(bacteria_filtro=None, tipo_filtro=None, anio_max=None, conn=None):
    """
    Analiza tendencias de resistencia aplicando los filtros seleccionados por el usuario.
    """
    cerrar = conn is None
    if cerrar:
        conn = conectar()

    try:
        # 1. Ajuste Dinámico del Tiempo
        if anio_max:
            # Si el usuario eligió un año límite, simulamos que estamos al final de ese año (31 dic)
            max_fecha = pd.to_datetime(f"{anio_max}-12-31")
        else:
            # Si no, usamos la última fecha real registrada
            cursor = conn.execute("SELECT MAX(fecha_toma_muestra) FROM antibiograma WHERE fecha_toma_muestra IS NOT NULL")
            max_fecha_str = cursor.fetchone()[0]
            if not max_fecha_str: return pd.DataFrame()
            max_fecha = pd.to_datetime(max_fecha_str)
        
        # 2. Definir ventanas de tiempo relativas a la fecha máxima
        inicio_reciente = max_fecha - pd.DateOffset(months=3)
        inicio_baseline = inicio_reciente - pd.DateOffset(months=6)

        # 3. Consulta SQL Dinámica (Incluyendo tipo de muestra)
        query = """
            SELECT 
                b.nombre_oficial AS bacteria,
                ant.nombre_oficial AS antibiotico,
                a.fecha_toma_muestra,
                r.estado
            FROM antibiograma a
            JOIN resultado_antibiotico r ON a.id_antibiograma = r.id_antibiograma
            JOIN bacteria b ON a.id_bacteria = b.id_bacteria
            JOIN antibiotico ant ON r.id_antibiotico = ant.id_antibiotico
            JOIN tipo_muestra tm ON a.id_tipo_muestra = tm.id_tipo_muestra
            WHERE a.fecha_toma_muestra BETWEEN ? AND ?
        """
        
        params = [inicio_baseline.strftime('%Y-%m-%d'), max_fecha.strftime('%Y-%m-%d')]

        # 4. Aplicar filtros si existen
        if bacteria_filtro:
            query += " AND b.nombre_oficial = ?"
            params.append(bacteria_filtro)
            
        if tipo_filtro:
            query += " AND tm.nombre = ?"
            params.append(tipo_filtro)

        # 5. Extraer los datos
        df = pd.read_sql_query(query, conn, params=tuple(params))
        
    finally:
        if cerrar:
            conn.close()

    if df.empty:
        return pd.DataFrame()

    df['fecha'] = pd.to_datetime(df['fecha_toma_muestra'])
    df['es_R'] = (df['estado'] == 'R').astype(int)

    df['Periodo'] = df['fecha'].apply(lambda x: 'Reciente' if x > inicio_reciente else 'Baseline')

    stats = df.groupby(['bacteria', 'antibiotico', 'Periodo']).agg(
        total_casos=('es_R', 'count'),
        casos_R=('es_R', 'sum')
    ).reset_index()

    pivot = stats.pivot(index=['bacteria', 'antibiotico'], columns='Periodo', values=['total_casos', 'casos_R']).fillna(0)
    pivot.columns = [f"{col[0]}_{col[1]}" for col in pivot.columns]
    pivot = pivot.reset_index()

    for col in ['total_casos_Baseline', 'casos_R_Baseline', 'total_casos_Reciente', 'casos_R_Reciente']:
        if col not in pivot.columns:
            pivot[col] = 0

    validos = pivot[(pivot['total_casos_Reciente'] >= 5) & (pivot['total_casos_Baseline'] >= 10)].copy()

    if validos.empty:
        return pd.DataFrame()

    validos['pct_Baseline'] = (validos['casos_R_Baseline'] / validos['total_casos_Baseline']) * 100
    validos['pct_Reciente'] = (validos['casos_R_Reciente'] / validos['total_casos_Reciente']) * 100

    validos['Ratio'] = validos.apply(
        lambda r: r['pct_Reciente'] / r['pct_Baseline'] if r['pct_Baseline'] > 0 else 0, axis=1
    )

    def clasificar(row):
        if row['pct_Baseline'] == 0:
            return 'Vigilancia' if row['pct_Reciente'] > 20 else 'Normal'
        elif row['Ratio'] >= 2.0:
            return 'Posible Alerta'
        elif row['Ratio'] >= 1.5:
            return 'Vigilancia'
        return 'Normal'

    validos['Nivel'] = validos.apply(clasificar, axis=1)
    alertas_finales = validos[validos['Nivel'] != 'Normal'].copy()
    
    if alertas_finales.empty:
        return pd.DataFrame()

    alertas_finales['pct_Baseline'] = alertas_finales['pct_Baseline'].round(1)
    alertas_finales['pct_Reciente'] = alertas_finales['pct_Reciente'].round(1)
    alertas_finales['Ratio'] = alertas_finales['Ratio'].round(1)

    return alertas_finales.sort_values(by='Ratio', ascending=False)[
        ['bacteria', 'antibiotico', 'pct_Baseline', 'pct_Reciente', 'Ratio', 'Nivel']
    ]