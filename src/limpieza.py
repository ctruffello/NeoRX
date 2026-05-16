"""
Limpieza del archivo Excel de antibiogramas.

Separa filas válidas de inválidas y guarda las inválidas en data/no_validos.xlsx
para revisión posterior.
"""

import pandas as pd
from pathlib import Path

RUTA_NO_VALIDOS = Path(__file__).parent.parent / "data" / "no_validos.xlsx"

# Palabras que indican que DETECCION FINAL NO es una bacteria
PALABRAS_NO_BACTERIA = [
    "negativo", "microbiota", "flora", "sin desarrollo", "sin crecimiento",
    "contaminante", "escasa cantidad", "regular cantidad", "abundante cantidad",
    "observacion", "observación", "hrs de", "horas de", "no hubo desarrollo"
]

# Estados que no aportan información clínica útil
ESTADOS_INVALIDOS = {"-", "sin estudio sensibilidad"}

# Correcciones directas de errores tipográficos en ESTADO
CORRECCIONES_ESTADO = {
    "s": "S",
    "i": "I",
    "r": "R",
    "ss": "S",
}


def _es_no_bacteria(texto):
    if pd.isna(texto):
        return True
    texto_lower = str(texto).lower()
    return any(p in texto_lower for p in PALABRAS_NO_BACTERIA)


def _normalizar_estado(valor):
    if pd.isna(valor):
        return None
    limpio = str(valor).strip().lower()
    if limpio in CORRECCIONES_ESTADO:
        return CORRECCIONES_ESTADO[limpio]
    limpio = limpio.upper()
    if limpio in ("S", "I", "R"):
        return limpio
    return None


def limpiar(ruta_excel):
    """
    Lee el Excel, separa filas válidas de inválidas.

    Retorna (df_validos, df_invalidos).
    Los inválidos quedan guardados en data/no_validos.xlsx.
    """
    print(f"  Leyendo {Path(ruta_excel).name}...")
    df = pd.read_excel(ruta_excel)

    total_original = len(df)

    # Eliminar columna vacía (Unnamed: 9)
    df = df.drop(columns=[c for c in df.columns if "Unnamed" in str(c)], errors="ignore")

    # Eliminar filas completamente vacías
    df = df.dropna(how="all").reset_index(drop=True)

    # Limpiar espacios en columnas de texto
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # Normalizar TIPO MUESTRA a mayúsculas
    df["TIPO MUESTRA"] = df["TIPO MUESTRA"].str.upper().str.strip()

    # Detectar motivos de rechazo (una fila puede tener más de uno)
    motivos = pd.Series([""] * len(df), dtype=str)

    mask_no_bacteria = df["DETECCION FINAL"].apply(_es_no_bacteria)
    mask_estado_invalido = df["ESTADO"].isin(ESTADOS_INVALIDOS)
    mask_estado_nulo = df["ESTADO"].isna()
    mask_antibiotico_nulo = df["ANTIBIOTICO"].isna()

    motivos[mask_no_bacteria] += "DETECCION FINAL no es bacteria; "
    motivos[mask_estado_invalido] += "ESTADO inválido (" + df.loc[mask_estado_invalido, "ESTADO"].astype(str) + "); "
    motivos[mask_estado_nulo] += "ESTADO vacío; "
    motivos[mask_antibiotico_nulo] += "ANTIBIOTICO vacío; "

    mask_invalido = mask_no_bacteria | mask_estado_invalido | mask_estado_nulo | mask_antibiotico_nulo

    df_invalidos = df[mask_invalido].copy()
    df_invalidos["MOTIVO_RECHAZO"] = motivos[mask_invalido].str.strip("; ")

    df_validos = df[~mask_invalido].copy()

    # Normalizar ESTADO en las filas válidas
    df_validos["ESTADO"] = df_validos["ESTADO"].apply(_normalizar_estado)

    # Guardar inválidos
    df_invalidos.to_excel(RUTA_NO_VALIDOS, index=False)

    print(f"  Total original:  {total_original}")
    print(f"  Filas válidas:   {len(df_validos)}")
    print(f"  Filas inválidas: {len(df_invalidos)} → guardadas en data/no_validos.xlsx")

    return df_validos, df_invalidos
