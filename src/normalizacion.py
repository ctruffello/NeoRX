"""
Normalización de bacterias y antibióticos.

Estrategia en tres pasos:
  1. Limpiar texto (tildes, UFC, paréntesis, espacios).
  2. Revisar alias explícitos (para abreviaturas muy distintas).
  3. Fuzzy matching contra la lista maestra.
"""

import re
import unicodedata
import pandas as pd
from rapidfuzz import fuzz

UMBRAL = 80

# =========================================
# LISTAS MAESTRAS
# =========================================

BACTERIAS_VALIDAS = [
    "Pseudomonas aeruginosa",
    "Klebsiella pneumoniae",
    "Klebsiella oxytoca",
    "Klebsiella variicola",
    "Klebsiella spp",
    "Serratia marcescens",
    "Serratia spp",
    "Escherichia coli",
    "Escherichia hermannii",
    "Streptococcus pneumoniae",
    "Streptococcus pyogenes",
    "Streptococcus agalactiae",
    "Streptococcus dysgalactiae",
    "Streptococcus mitis",
    "Staphylococcus aureus",
    "Staphylococcus haemolyticus",
    "Staphylococcus coagulasa negativa",
    "Proteus mirabilis",
    "Acinetobacter baumannii",
    "Acinetobacter spp",
    "Stenotrophomonas maltophilia",
    "Enterobacter cloacae",
    "Achromobacter spp",
    "Enterococcus faecalis",
    "Enterococcus faecium",
    "Enterococcus gallinarum",
    "Citrobacter freundii",
    "Citrobacter koseri",
    "Citrobacter spp",
    "Morganella morganii",
    "Alcaligenes faecalis",
    "Chryseobacterium sp",
    "Delftia acidovorans",
    "Moraxella catarrhalis",
]

ANTIBIOTICOS_VALIDOS = [
    "Amikacina",
    "Gentamicina",
    "Tobramicina",
    "Ciprofloxacino",
    "Levofloxacino",
    "Moxifloxacino",
    "Meropenem",
    "Imipenem",
    "Ertapenem",
    "Piperacilina/Tazobactam",
    "Cefotaxima",
    "Ceftazidima",
    "Ceftazidima/Avibactam",
    "Cefepime",
    "Cefuroxima IV/IM",
    "Cefuroxima oral",
    "Cefazolina",
    "Cefixime",
    "Cefalotina",
    "Cefadroxilo",
    "Cefoperazona/Sulbactam",
    "Ampicilina",
    "Ampicilina/Sulbactam",
    "Amoxicilina",
    "Clindamicina",
    "Eritromicina",
    "Vancomicina",
    "Oxacilina",
    "Colistin",
    "Aztreonam",
    "Minociclina",
    "Penicilina",
    "Sulfametoxazol/Trimetoprim",
    "Nitrofurantoina",
    "Fosfomicina",
    "Cloranfenicol",
    "Rifampicina",
    "Doxiciclina",
    "Linezolid",
    "Teicoplanina",
]

# Alias explícitos: texto limpio → nombre oficial
# Para casos donde el fuzzy matching no alcanza (abreviaturas muy distintas)
ALIAS_ANTIBIOTICOS = {
    "cotrimoxazol":                    "Sulfametoxazol/Trimetoprim",
    "sulfametoxazol trimetoprim":      "Sulfametoxazol/Trimetoprim",
    "sulfametoxazol/ trimetoprim":     "Sulfametoxazol/Trimetoprim",
    "piper/tazob":                     "Piperacilina/Tazobactam",
    "piperacilina/ tazobactam":        "Piperacilina/Tazobactam",
    "fosfomicina trometanol oral":     "Fosfomicina",
    "fosfomicina trometanol (oral)":   "Fosfomicina",
    "fosfomicina trometanol":          "Fosfomicina",
    "cloramfenicol":                   "Cloranfenicol",
    "vancomocina":                     "Vancomicina",
    "oxaciclina":                      "Oxacilina",
    "nitrufurantoina":                 "Nitrofurantoina",
    "ertapenen":                       "Ertapenem",
    "ceftazidima/ sulbactam":          "Ceftazidima/Avibactam",
    "ceftazidima /avibactam":          "Ceftazidima/Avibactam",
    "cettazidima":                     "Ceftazidima",
    "cefuroximai iv/im":               "Cefuroxima IV/IM",
    "cefuroxima iv/im":                "Cefuroxima IV/IM",
    "cefuroxima oral":                 "Cefuroxima oral",
}

ALIAS_BACTERIAS = {
    "achoromobacter spp":              "Achromobacter spp",
    "acetinobacter spp":               "Acinetobacter spp",
    "klebsiella ex enterobacter aerogenes": "Klebsiella pneumoniae",
    "no hubo desarrollo enterococcus resistente a vancomicina": None,
}

# =========================================
# LIMPIEZA DE TEXTO
# =========================================

_PATRON_UFC = re.compile(
    r'[\d.,]+\s*(ufc|UFC).*|>\s*[\d.,]+\s*(ufc|UFC).*', re.IGNORECASE
)

def _limpiar(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.strip().lower()
    texto = _PATRON_UFC.sub("", texto).strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"\(.*?\)", " ", texto)       # quitar paréntesis y contenido
    texto = texto.replace(".", " ").replace(",", " ")
    texto = re.sub(r"[^a-z0-9\s/]", " ", texto)
    texto = " ".join(texto.split())
    return texto


def _expandir_abreviatura(texto, lista_limpia):
    palabras = texto.split()
    if len(palabras) == 2:
        inicial, resto = palabras
        if len(inicial) == 1:
            for ref in lista_limpia:
                ref_words = ref.split()
                if len(ref_words) >= 2 and ref_words[0].startswith(inicial) and ref_words[1] == resto:
                    return ref
    return texto


# =========================================
# MOTOR DE NORMALIZACIÓN
# =========================================

def _preparar(lista):
    return [(item, _limpiar(item)) for item in lista]

_BACTERIAS_PREP = _preparar(BACTERIAS_VALIDAS)
_ANTIBIOTICOS_PREP = _preparar(ANTIBIOTICOS_VALIDOS)

def _normalizar(texto_sucio, lista_preparada, alias):
    if not isinstance(texto_sucio, str) or not texto_sucio.strip():
        return "Desconocido"

    limpio = _limpiar(texto_sucio)

    # Paso 1: alias explícito
    if limpio in alias:
        resultado = alias[limpio]
        return resultado if resultado is not None else "Desconocido"

    # Paso 2: expandir abreviatura
    limpio = _expandir_abreviatura(limpio, [l for _, l in lista_preparada])

    # Paso 3: fuzzy matching
    mejor_match = None
    mejor_score = 0
    for original, limpio_ref in lista_preparada:
        score = max(
            fuzz.ratio(limpio, limpio_ref),
            fuzz.partial_ratio(limpio, limpio_ref),
            fuzz.token_sort_ratio(limpio, limpio_ref),
        )
        if score > mejor_score:
            mejor_score = score
            mejor_match = original

    if mejor_score >= UMBRAL:
        return mejor_match
    return "Desconocido"


def normalizar_bacteria(texto):
    return _normalizar(texto, _BACTERIAS_PREP, ALIAS_BACTERIAS)

def normalizar_antibiotico(texto):
    return _normalizar(texto, _ANTIBIOTICOS_PREP, ALIAS_ANTIBIOTICOS)


# =========================================
# APLICAR AL DATAFRAME
# =========================================

def normalizar_dataframe(df):
    """
    Agrega BACTERIA_NORM y ANTIBIOTICO_NORM al DataFrame.
    Retorna (df_ok, df_desconocidos).
    Los desconocidos se deben registrar en log_limpieza.
    """
    df = df.copy()

    print("  Normalizando bacterias...")
    df["BACTERIA_NORM"] = df["DETECCION FINAL"].apply(normalizar_bacteria)

    print("  Normalizando antibióticos...")
    df["ANTIBIOTICO_NORM"] = df["ANTIBIOTICO"].apply(normalizar_antibiotico)

    mask = (df["BACTERIA_NORM"] == "Desconocido") | (df["ANTIBIOTICO_NORM"] == "Desconocido")

    df_desconocidos = df[mask].copy()
    df_ok = df[~mask].copy()

    return df_ok, df_desconocidos
