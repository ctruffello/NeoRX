###### EXPLICACIÓN CÓDIGO
### Primero mencionar que el software está trabajndo sólo con la base de datos del antibiograma en la página UC
### En la columna I "deteccion final" se ve que muchos inputs tienen demasiados typos y nombres diferentes para la misma bacteria. asumo que lo único que importa es el nombre de la bacteria y normalizo los nombres en el sig código
### Lo que hace entonces el código es que primero normaliza el nombre de bacteria inical (aunque esté mal escrita). 
### Luego, asocia lo anotado a un diccionario que tiene todos los typos frecunetes. Entonces lo busca en el diccionario y arroja de diccionario la bacteria bien escrita.




###### ARREGLAR MAYUS, ESPACIOS 
"""
Original: '   esChErichia     coli  '
Limpio:   'Escherichia coli'
"""
def limpiar_mayus_spc(texto):
    # 1. validar que sea string
    if not isinstance(texto, str):
        return "Desconocido"

    # 2. todo a minúsculas
    texto_minusculas = texto.lower()

    # 3. elimina spc inicio, final, dobles
    texto_sin_espacios = " ".join(texto_minusculas.split())

    # 4. solo priemra letra en mayus
    texto_normalizado = texto_sin_espacios.capitalize()


    return texto_normalizado



###### DICCIONARIO ANTIBIÓTICOS
diccionario_bacterias = {
    # Keys (errores) : Values (nombre oficial)
    # Cabe notar que están los errores en minúscila porque antes se traduce todo a minúsculas

    ###### Escherichia coli
    "e. coli": "Escherichia coli",
    "e coli": "Escherichia coli",
    "ecoli": "Escherichia coli",
    "eschericia coli": "Escherichia coli", 

    ###### Staphylococcus aureus
    "s. aureus": "Staphylococcus aureus",
    "staph aureus": "Staphylococcus aureus",

    ###### Pseudomonas aeruginosa
    "p. aeruginosa": "Pseudomonas aeruginosa",
    "pseudomona": "Pseudomonas aeruginosa",

    ###### Klebsiella pneumoniae
    "k. pneumoniae": "Klebsiella pneumoniae",
    "klebsiella p.": "Klebsiella pneumoniae",

    ###### NULL
    "Negativo a las 24 HRS de observación": "Null"
}


###### DICCIONARIO ANTIBIÓTICOS
diccionario_antibioticos = {
    ###### Amikacina
    "amk": "Amikacina",
    "amikacina": "Amikacina",
    "ampicilina sulbactam": "Ampicilina/Sulbactam", # Normalizar el separador
    "amoxicilina/ac.clavulanico": "Amoxicilina/Ácido Clavulánico",
    "clinda": "Clindamicina",
    "genta": "Gentamicina",
}


###### FUNCIONES PARA USO
def normalizar_bacteria(texto):
    limpio = limpiar_mayus_spc(texto)
        resultado = diccionario_bacterias.get(limpio.lower())
        if resultado:
            return resultado
        # Si no está en el diccionario, avisa para que puedas agregarlo después
        print(f"DEBUG: Nueva variante encontrada: {limpio}")
        return limpio


def normalizar_antibiotico(texto):
    limpio = limpiar_mayus_spc(texto)
    # Busca en el diccionario
    return diccionario_antibioticos.get(limpio.lower(), limpio)