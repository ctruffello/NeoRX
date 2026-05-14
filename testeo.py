from database import inicializar_base_de_datos

def testear_sistema():
    print("=== INICIANDO TEST DE INTEGRACIÓN NEORX ===\n")
    
    ruta = 'Antibiograma_2016_2025.xlsx'
    db = inicializar_base_de_datos(ruta)
    
    if db is not None:
        print("\n--- VERIFICACIÓN DE NORMALIZACIÓN ---")
        print(db[['FECHA TOMA MUESTRA', 'ANIO', 'DETECCION FINAL', 'ANTIBIOTICO']].head(10))
        
        print("\n--- VERIFICACIÓN DE TIPOS DE DATOS ---")
        print(f"Tipo de columna ANIO: {db['ANIO'].dtype}")
        print(f"Tipo de columna FECHA: {db['FECHA TOMA MUESTRA'].dtype}")
        
        print("\n--- LISTA DE BACTERIAS ÚNICAS ---")
        print(db['DETECCION FINAL'].unique())

        print("\n--- TOP 20 BACTERIAS ---")
        print(db['DETECCION FINAL'].value_counts().head(20))

        print("\n--- MUESTRA DE VALORES ---")
        print(db['DETECCION FINAL'].unique()[:30])

        print("\n--- % DESCONOCIDOS ---")
        total = len(db)
        desconocidos = (db['DETECCION FINAL'] == "Desconocido").sum()
        print(f"{desconocidos}/{total} = {desconocidos/total:.2%}")

        print("\n=== TEST FINALIZADO ===")

    else:
        print("ERROR: No se pudo cargar la base de datos.")


if __name__ == "__main__":
    testear_sistema()