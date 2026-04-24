"""
Función que pregunta Y/N (Sí y no)
Cruce de datos entre el laboratorio y los datos históricos inventados
Reglas sobre casos (fallas renales, epilepsia por ahora)
"""

import pandas as pd

def run_engine():
    try:
        lab = pd.read_csv('data/processed/laboratorio_unificado.csv')
        outcomes = pd.read_csv('data/processed/outcomes_clinicos.csv')
    except:
        print("❌ Error: Ejecuta primero 'python src/generator.py'")
        return

    print("\n" + "="*55)
    print("      NeoRX: AUDITORÍA DE DECISIÓN CLÍNICA      ")
    print("="*55)
    
    renal = input("¿Falla renal? (1: Sí / 2: No): ")
    epi = input("¿Epilepsia? (1: Sí / 2: No): ")

    # 1. ANÁLISIS DE TENDENCIA (Por defecto)
    # Seleccionamos la bacteria más frecuente en el set de datos unificado
    bacteria = lab['DETECCION FINAL'].mode()[0]
    df_bact = lab[lab['DETECCION FINAL'] == bacteria]
    total_muestras = len(df_bact['ID_EPISODIO'].unique())

    # 2. PROCESAMIENTO DE CANDIDATOS
    candidatos = df_bact['ANTIBIOTICO'].value_counts().head(3).index.tolist()
    resultados_comparativa = []

    for atb in candidatos:
        # Sensibilidad Microbiológica
        tests_atb = df_bact[df_bact['ANTIBIOTICO'] == atb]
        sensibles = len(tests_atb[tests_atb['ESTADO'] == 'S'])
        tasa_s = (sensibles / len(tests_atb)) * 100 if len(tests_atb) > 0 else 0
        
        # Éxito Clínico (Cruce con Outcomes)
        ids_atb = tests_atb['ID_EPISODIO'].unique()
        exitos = outcomes[outcomes['ID_EPISODIO'].isin(ids_atb)]['EXITO_CLINICO'].mean() * 100
        
        # Penalizaciones
        penalizacion = 0
        if renal == "1" and any(x in atb for x in ["AMIKACINA", "GENTAMICINA"]): 
            penalizacion = 40 
        if epi == "1" and any(x in atb for x in ["MEROPENEM", "IMIPENEM"]):
            penalizacion = 60 

        score = (tasa_s * 0.4) + (exitos * 0.6) - penalizacion
        
        resultados_comparativa.append({
            'atb': atb,
            'sensibilidad': tasa_s,
            'exito': exitos,
            'score': score,
            'penalizado': penalizacion > 0
        })

    resultados_comparativa = sorted(resultados_comparativa, key=lambda x: x['score'], reverse=True)
    ganador = resultados_comparativa[0]

    # --- SALIDA DE DIAGNÓSTICO ---
    print(f"\n🎯 RECOMENDACIÓN NeoRX: {ganador['atb']}")
    print(f"📈 SCORE DE CONFIANZA: {ganador['score']:.1f}/100")

    print("\n" + "-"*15 + " PROCESO MENTAL DEL MODELO " + "-"*15)
    # Cambio solicitado por el usuario:
    print(f"Patógeno analizado (por defecto): {bacteria}")
    print(f"Base de datos: {total_muestras} casos analizados (UC + HSR).\n")
    
    print(f"{'ANTIBIÓTICO':<20} | {'SENS. LAB':<10} | {'ÉXITO CLIN.':<12} | {'SCORE FINAL'}")
    print("-" * 65)
    for res in resultados_comparativa:
        marcador = "!" if res['penalizado'] else " "
        print(f"{marcador}{res['atb']:<19} | {res['sensibilidad']:>8.1f}% | {res['exito']:>10.1f}% | {res['score']:>10.1f}")
    
    print("\nLÓGICA DE CÁLCULO:")
    print(f"1. Se analiza la bacteria con mayor prevalencia histórica en el hospital.")
    print(f"2. Se prioriza '{ganador['atb']}' por balance óptimo entre laboratorio y resultados reales.")
    if ganador['penalizado']:
        print(f"3. NOTA: El puntaje refleja ajustes por seguridad (riesgo del paciente).")
    print("-" * 65)