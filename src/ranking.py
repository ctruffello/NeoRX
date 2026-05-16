"""
Ranking de antibióticos consultando directamente la base de datos.

La fórmula pondera la susceptibilidad por confianza estadística:
  puntaje = susceptibilidad% × (1 - 1/√total)
Así un 100% con 2 casos baja en el ranking frente a un 90% con 50 casos.
"""

import numpy as np
import pandas as pd
from src.base_de_datos import conectar

_QUERY_RANKING = """
    SELECT
        ant.nombre_oficial  AS antibiotico,
        ra.estado
    FROM resultado_antibiotico ra
    JOIN antibiograma  ag  ON ra.id_antibiograma = ag.id_antibiograma
    JOIN bacteria      b   ON ag.id_bacteria     = b.id_bacteria
    JOIN antibiotico   ant ON ra.id_antibiotico  = ant.id_antibiotico
    JOIN tipo_muestra  tm  ON ag.id_tipo_muestra = tm.id_tipo_muestra
    WHERE b.nombre_oficial  = ?
      AND tm.nombre         = ?
      AND CAST(strftime('%Y', ag.fecha_toma_muestra) AS INTEGER) BETWEEN ? AND ?
"""

_QUERY_BACTERIAS = """
    SELECT DISTINCT b.nombre_oficial
    FROM bacteria b
    JOIN antibiograma ag ON ag.id_bacteria = b.id_bacteria
    ORDER BY b.nombre_oficial
"""

_QUERY_TIPOS = """
    SELECT DISTINCT tm.nombre
    FROM tipo_muestra tm
    JOIN antibiograma ag ON ag.id_tipo_muestra = tm.id_tipo_muestra
    ORDER BY tm.nombre
"""

_QUERY_ANIOS = """
    SELECT
        MIN(CAST(strftime('%Y', fecha_toma_muestra) AS INTEGER)),
        MAX(CAST(strftime('%Y', fecha_toma_muestra) AS INTEGER))
    FROM antibiograma
    WHERE fecha_toma_muestra IS NOT NULL
"""

_UMBRAL = {
    "UROCULTIVO": "Tratar E. coli si >50.000 UFC; otras si >10.000 UFC.",
}
_UMBRAL_DEFAULT = "Tratar solo si el recuento es >100.000 UFC."


def generar_ranking(bacteria, tipo_muestra, anio_min, anio_max, conn=None):
    """
    Retorna (DataFrame con ranking, texto de umbral clínico).
    Retorna (None, None) si no hay datos para los filtros dados.
    """
    cerrar = conn is None
    if cerrar:
        conn = conectar()

    try:
        df = pd.read_sql_query(
            _QUERY_RANKING, conn,
            params=(bacteria, tipo_muestra, anio_min, anio_max)
        )
    finally:
        if cerrar:
            conn.close()

    if df.empty:
        return None, None

    stats = df.groupby("antibiotico")["estado"].agg(
        Total="count",
        Sensibles=lambda x: (x == "S").sum(),
    )

    stats["Susceptibilidad_%"] = (stats["Sensibles"] / stats["Total"] * 100).round(1)
    stats["Puntaje"]           = stats["Susceptibilidad_%"] * (1 - 1 / np.sqrt(stats["Total"]))
    stats["Fiabilidad"]        = stats["Total"].apply(lambda n: "ALTA" if n >= 30 else "BAJA")

    ranking = stats.sort_values("Puntaje", ascending=False)
    umbral  = _UMBRAL.get(tipo_muestra, _UMBRAL_DEFAULT)

    return ranking[["Susceptibilidad_%", "Total", "Fiabilidad"]], umbral


def listar_bacterias(conn=None):
    cerrar = conn is None
    if cerrar:
        conn = conectar()
    try:
        return [r[0] for r in conn.execute(_QUERY_BACTERIAS).fetchall()]
    finally:
        if cerrar:
            conn.close()


def listar_tipos_muestra(conn=None):
    cerrar = conn is None
    if cerrar:
        conn = conectar()
    try:
        return [r[0] for r in conn.execute(_QUERY_TIPOS).fetchall()]
    finally:
        if cerrar:
            conn.close()


def rango_anios(conn=None):
    """Retorna (anio_min, anio_max) disponibles en la base de datos."""
    cerrar = conn is None
    if cerrar:
        conn = conectar()
    try:
        return conn.execute(_QUERY_ANIOS).fetchone()
    finally:
        if cerrar:
            conn.close()
