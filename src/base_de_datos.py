"""
Conexión a la base de datos SQLite y creación de tablas.

SQLite viene incluido en Python: no necesita instalación extra.
El archivo neorx.db se crea automáticamente en la carpeta raíz del proyecto.
"""

import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).parent.parent / "neorx.db"

SCHEMA = """
    CREATE TABLE IF NOT EXISTS region (
        codigo_region   INTEGER PRIMARY KEY,
        nombre          TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS comuna (
        codigo_comuna   INTEGER PRIMARY KEY,
        nombre          TEXT NOT NULL,
        codigo_region   INTEGER NOT NULL REFERENCES region(codigo_region)
    );

    CREATE TABLE IF NOT EXISTS clinica (
        id_clinica      INTEGER PRIMARY KEY,
        nombre          TEXT NOT NULL,
        codigo_comuna   INTEGER REFERENCES comuna(codigo_comuna)
    );

    CREATE TABLE IF NOT EXISTS archivo_cargado (
        id_archivo      INTEGER PRIMARY KEY,
        id_clinica      INTEGER NOT NULL REFERENCES clinica(id_clinica),
        nombre_archivo  TEXT NOT NULL,
        fecha_carga     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        estado          TEXT DEFAULT 'procesando'
                        CHECK (estado IN ('procesando', 'ok', 'con_errores'))
    );

    CREATE TABLE IF NOT EXISTS bacteria (
        id_bacteria     INTEGER PRIMARY KEY,
        nombre_oficial  TEXT NOT NULL UNIQUE,
        gram            TEXT
    );

    CREATE TABLE IF NOT EXISTS antibiotico (
        id_antibiotico  INTEGER PRIMARY KEY,
        nombre_oficial  TEXT NOT NULL UNIQUE,
        clase           TEXT
    );

    CREATE TABLE IF NOT EXISTS tipo_muestra (
        id_tipo_muestra INTEGER PRIMARY KEY,
        nombre          TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS antibiograma (
        id_antibiograma     INTEGER PRIMARY KEY,
        id_archivo          INTEGER NOT NULL REFERENCES archivo_cargado(id_archivo),
        id_clinica          INTEGER NOT NULL REFERENCES clinica(id_clinica),
        fecha_toma_muestra  TEXT,
        id_tipo_muestra     INTEGER REFERENCES tipo_muestra(id_tipo_muestra),
        id_bacteria         INTEGER REFERENCES bacteria(id_bacteria)
    );

    CREATE TABLE IF NOT EXISTS resultado_antibiotico (
        id_resultado    INTEGER PRIMARY KEY,
        id_antibiograma INTEGER NOT NULL REFERENCES antibiograma(id_antibiograma),
        id_antibiotico  INTEGER NOT NULL REFERENCES antibiotico(id_antibiotico),
        estado          TEXT NOT NULL CHECK (estado IN ('S', 'I', 'R')),
        valor_mic       TEXT
    );

    CREATE TABLE IF NOT EXISTS log_limpieza (
        id_log          INTEGER PRIMARY KEY,
        id_archivo      INTEGER REFERENCES archivo_cargado(id_archivo),
        numero_fila     INTEGER,
        campo_problema  TEXT,
        valor_original  TEXT,
        valor_asignado  TEXT,
        motivo          TEXT,
        fecha_registro  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""


def conectar():
    """Devuelve una conexión a la base de datos con claves foráneas activadas."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_tablas(conn):
    """Crea todas las tablas si no existen. Seguro de ejecutar múltiples veces."""
    conn.executescript(SCHEMA)
    conn.commit()


def verificar_tablas(conn):
    """Devuelve la lista de tablas que existen en la base de datos."""
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    return [row[0] for row in cursor.fetchall()]


CSV_GEOGRAFIA = Path(__file__).parent.parent / "data" / "regiones_comunas.csv"

def poblar_regiones_comunas(conn):
    """Carga regiones y comunas desde el CSV. Solo se ejecuta si las tablas están vacías."""
    cursor = conn.cursor()

    if cursor.execute("SELECT COUNT(*) FROM region").fetchone()[0] > 0:
        print("  Regiones y comunas ya cargadas, se omite.")
        return

    df = pd.read_csv(CSV_GEOGRAFIA, sep=';', encoding='utf-8-sig')
    df.columns = ['codigo_comuna', 'nombre_comuna', 'codigo_region', 'nombre_region']

    regiones = df[['codigo_region', 'nombre_region']].drop_duplicates()
    for _, fila in regiones.iterrows():
        cursor.execute(
            "INSERT OR IGNORE INTO region (codigo_region, nombre) VALUES (?, ?)",
            (int(fila['codigo_region']), fila['nombre_region'])
        )

    for _, fila in df.iterrows():
        cursor.execute(
            "INSERT OR IGNORE INTO comuna (codigo_comuna, nombre, codigo_region) VALUES (?, ?, ?)",
            (int(fila['codigo_comuna']), fila['nombre_comuna'], int(fila['codigo_region']))
        )

    conn.commit()
    print(f"  {len(regiones)} regiones y {len(df)} comunas cargadas.")
