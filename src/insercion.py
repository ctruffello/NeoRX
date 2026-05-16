"""
Inserción de datos normalizados en la base de datos.

Flujo:
  1. Registra la clínica y el archivo cargado.
  2. Pobla los catálogos (bacteria, antibiotico, tipo_muestra).
  3. Inserta un antibiograma por cada grupo (FOLIO + BACTERIA_NORM).
  4. Inserta un resultado_antibiotico por cada fila dentro del grupo.
"""

import pandas as pd


COL_CONCENTRACION = "CONCENTRACIÓN "   # tiene un espacio al final en el Excel


def _get_o_crear(cursor, tabla, col_nombre, nombre):
    """Devuelve el id de un registro existente, o lo inserta y devuelve el nuevo id."""
    fila = cursor.execute(
        f"SELECT rowid FROM {tabla} WHERE {col_nombre} = ?", (nombre,)
    ).fetchone()
    if fila:
        return fila[0]
    cursor.execute(f"INSERT INTO {tabla} ({col_nombre}) VALUES (?)", (nombre,))
    return cursor.lastrowid


def _clave_antibiograma(fila):
    """
    Clave para agrupar filas que pertenecen al mismo antibiograma.
    Si hay FOLIO usa (FOLIO, BACTERIA_NORM), si no usa (FECHA, TIPO, BACTERIA_NORM).
    """
    if pd.notna(fila["FOLIO"]):
        return (str(fila["FOLIO"]), fila["BACTERIA_NORM"])
    fecha = fila["FECHA TOMA MUESTRA"]
    fecha_str = pd.Timestamp(fecha).strftime("%Y-%m-%d") if pd.notna(fecha) else "sin_fecha"
    return (fecha_str, str(fila["TIPO MUESTRA"]), fila["BACTERIA_NORM"])


def insertar(conn, df_ok, nombre_archivo):
    """Inserta todas las filas normalizadas. Retorna (insertados, errores)."""
    cursor = conn.cursor()

    # 1. Clínica
    id_clinica = _get_o_crear(cursor, "clinica", "nombre", "Laboratorio UC")

    # 2. Archivo cargado
    cursor.execute(
        "INSERT INTO archivo_cargado (id_clinica, nombre_archivo, estado) VALUES (?, ?, 'procesando')",
        (id_clinica, nombre_archivo),
    )
    id_archivo = cursor.lastrowid
    conn.commit()
    print(f"  Clínica y archivo registrados (id_archivo={id_archivo})")

    # 3. Catálogos
    bacterias_ids = {}
    for nombre in df_ok["BACTERIA_NORM"].unique():
        bacterias_ids[nombre] = _get_o_crear(cursor, "bacteria", "nombre_oficial", nombre)

    antibioticos_ids = {}
    for nombre in df_ok["ANTIBIOTICO_NORM"].unique():
        antibioticos_ids[nombre] = _get_o_crear(cursor, "antibiotico", "nombre_oficial", nombre)

    tipos_ids = {}
    for nombre in df_ok["TIPO MUESTRA"].dropna().unique():
        tipos_ids[nombre] = _get_o_crear(cursor, "tipo_muestra", "nombre", nombre)

    conn.commit()
    print(f"  Catálogos: {len(bacterias_ids)} bacterias, {len(antibioticos_ids)} antibióticos, {len(tipos_ids)} tipos de muestra")

    # 4. Agrupar por antibiograma e insertar
    df_ok = df_ok.copy()
    df_ok["_clave"] = df_ok.apply(_clave_antibiograma, axis=1)

    insertados = 0
    errores = 0

    for clave, grupo in df_ok.groupby("_clave", sort=False):
        primera = grupo.iloc[0]

        fecha = primera["FECHA TOMA MUESTRA"]
        fecha_str = pd.Timestamp(fecha).strftime("%Y-%m-%d") if pd.notna(fecha) else None
        id_bacteria = bacterias_ids[primera["BACTERIA_NORM"]]
        id_tipo = tipos_ids.get(primera["TIPO MUESTRA"])

        cursor.execute(
            """INSERT INTO antibiograma
               (id_archivo, id_clinica, fecha_toma_muestra, id_tipo_muestra, id_bacteria)
               VALUES (?, ?, ?, ?, ?)""",
            (id_archivo, id_clinica, fecha_str, id_tipo, id_bacteria),
        )
        id_antibiograma = cursor.lastrowid

        for _, fila in grupo.iterrows():
            id_antibiotico = antibioticos_ids[fila["ANTIBIOTICO_NORM"]]
            estado = fila["ESTADO"]
            concentracion = fila.get(COL_CONCENTRACION)
            valor_mic = str(concentracion).strip() if pd.notna(concentracion) else None
            if valor_mic == "-":
                valor_mic = None

            try:
                cursor.execute(
                    """INSERT INTO resultado_antibiotico
                       (id_antibiograma, id_antibiotico, estado, valor_mic)
                       VALUES (?, ?, ?, ?)""",
                    (id_antibiograma, id_antibiotico, estado, valor_mic),
                )
                insertados += 1
            except Exception as e:
                errores += 1
                cursor.execute(
                    """INSERT INTO log_limpieza
                       (id_archivo, campo_problema, valor_original, motivo)
                       VALUES (?, 'resultado_antibiotico', ?, ?)""",
                    (id_archivo, str(fila.to_dict()), str(e)),
                )

    # 5. Actualizar estado del archivo
    estado_final = "ok" if errores == 0 else "con_errores"
    cursor.execute(
        "UPDATE archivo_cargado SET estado = ? WHERE id_archivo = ?",
        (estado_final, id_archivo),
    )
    conn.commit()

    print(f"  Resultados insertados: {insertados}")
    if errores > 0:
        print(f"  Errores registrados en log_limpieza: {errores}")
    print(f"  Estado del archivo: {estado_final}")

    return insertados, errores
