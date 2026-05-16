"""
Motor principal del sistema. Orquesta las funciones del proyecto.
"""

from pathlib import Path
from src.base_de_datos import conectar, inicializar_tablas, verificar_tablas, poblar_regiones_comunas
from src.limpieza import limpiar
from src.normalizacion import normalizar_dataframe
from src.insercion import insertar

RUTA_EXCEL = Path(__file__).parent.parent / "data" / "Antibiograma_2016_2025.xlsx"


def run_engine():
    print("Conectando a la base de datos...")
    conn = conectar()

    print("Creando tablas si no existen...")
    inicializar_tablas(conn)

    print("Cargando regiones y comunas de Chile...")
    poblar_regiones_comunas(conn)

    print(f"\nProcesando archivo de antibiogramas...")
    df_validos, _ = limpiar(RUTA_EXCEL)

    print("\nNormalizando nombres...")
    df_ok, df_desconocidos = normalizar_dataframe(df_validos)
    print(f"  Listos para insertar: {len(df_ok)}")
    if len(df_desconocidos) > 0:
        print(f"  No normalizados: {len(df_desconocidos)} (se omiten)")

    print("\nInsertando en la base de datos...")
    insertados, errores = insertar(conn, df_ok, RUTA_EXCEL.name)

    conn.close()
    print("\nPipeline completo.")
