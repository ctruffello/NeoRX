from rapidfuzz import fuzz
import unicodedata
import re

# =========================================
# 1. LIMPIEZA ULTRA ROBUSTA
# =========================================
def limpiar_texto(texto):
    if not isinstance(texto, str) or texto.strip() == "":
        return ""

    texto = texto.lower()

    # quitar tildes
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')

    # reemplazar símbolos comunes
    texto = texto.replace(".", " ")
    texto = texto.replace(",", " ")
    texto = texto.replace("-", " ")

    # eliminar caracteres raros
    texto = re.sub(r'[^a-z0-9\s/]', ' ', texto)

    # limpiar espacios
    texto = " ".join(texto.split())

    return texto


# =========================================
# 2. LISTAS MAESTRAS
# =========================================
BACTERIAS_VALIDAS = [
    "Escherichia coli",
    "Staphylococcus aureus",
    "Pseudomonas aeruginosa",
    "Klebsiella pneumoniae",
    "Enterococcus faecalis",
    "Proteus mirabilis",
    "Enterobacter cloacae",
    "Klebsiella oxytoca"
]

ANTIBIOTICOS_VALIDOS = [
    "Amikacina",
    "Gentamicina",
    "Clindamicina",
    "Ceftriaxona",
    "Ampicilina/Sulbactam",
    "Amoxicilina/Acido clavulanico",
    "Ciprofloxacino",
    "Meropenem",
    "Vancomicina"
]


# =========================================
# 3. PREPARACIÓN
# =========================================
def preparar_lista(lista):
    return [(item, limpiar_texto(item)) for item in lista]


BACTERIAS_PREP = preparar_lista(BACTERIAS_VALIDAS)
ANTIBIOTICOS_PREP = preparar_lista(ANTIBIOTICOS_VALIDOS)


# =========================================
# 4. EXPANSIÓN AUTOMÁTICA DE ABREVIATURAS
# =========================================
def expandir_abreviatura(texto):
    palabras = texto.split()

    # caso típico: "e coli", "s aureus"
    if len(palabras) == 2:
        inicial, resto = palabras

        if len(inicial) == 1:
            for _, limpio_ref in BACTERIAS_PREP:
                ref_words = limpio_ref.split()

                if len(ref_words) >= 2:
                    if ref_words[0].startswith(inicial) and ref_words[1] == resto:
                        return limpio_ref

    return texto


# =========================================
# 5. MOTOR AUTOMÁTICO
# =========================================
def normalizar_automatico(texto_sucio, lista_preparada):
    if not isinstance(texto_sucio, str) or texto_sucio.strip() == "":
        return "Desconocido"

    limpio = limpiar_texto(texto_sucio)

    # 🔥 clave: expandir abreviatura antes del matching
    limpio = expandir_abreviatura(limpio)

    mejor_match = None
    mejor_score = 0

    for original, limpio_ref in lista_preparada:

        score = max(
            fuzz.ratio(limpio, limpio_ref),
            fuzz.partial_ratio(limpio, limpio_ref),
            fuzz.token_sort_ratio(limpio, limpio_ref)
        )

        if score > mejor_score:
            mejor_score = score
            mejor_match = original

    if mejor_score >= 80:
        return mejor_match

    return "Desconocido"


# =========================================
# 6. FUNCIONES FINALES
# =========================================
def normalizar_bacteria(texto):
    return normalizar_automatico(texto, BACTERIAS_PREP)


def normalizar_antibiotico(texto):
    return normalizar_automatico(texto, ANTIBIOTICOS_PREP)