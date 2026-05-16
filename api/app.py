"""
API REST de NeoRX.

Endpoints:
  GET /bacterias              Lista de bacterias disponibles en la base de datos.
  GET /tipos-muestra          Lista de tipos de muestra disponibles.
  GET /anios                  Rango de años disponibles.
  GET /ranking                Ranking de antibióticos con filtros.

Parámetros de /ranking:
  bacteria      (requerido)  Nombre oficial de la bacteria.
  tipo_muestra  (requerido)  Nombre del tipo de muestra.
  anio_min      (opcional)   Año de inicio del filtro.
  anio_max      (opcional)   Año de fin del filtro.

Ejemplo:
  /ranking?bacteria=Escherichia coli&tipo_muestra=UROCULTIVO&anio_min=2020&anio_max=2025
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from src.ranking import generar_ranking, listar_bacterias, listar_tipos_muestra, rango_anios

FRONTEND = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

app = Flask(__name__)


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


def _error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


@app.get("/bacterias")
def endpoint_bacterias():
    return jsonify(listar_bacterias())


@app.get("/tipos-muestra")
def endpoint_tipos_muestra():
    return jsonify(listar_tipos_muestra())


@app.get("/anios")
def endpoint_anios():
    anio_min, anio_max = rango_anios()
    return jsonify({"anio_min": anio_min, "anio_max": anio_max})


@app.get("/ranking")
def endpoint_ranking():
    bacteria     = request.args.get("bacteria", "").strip()
    tipo_muestra = request.args.get("tipo_muestra", "").strip()
    anio_min_db, anio_max_db = rango_anios()

    if not bacteria:
        return _error("El parámetro 'bacteria' es requerido.")
    if not tipo_muestra:
        return _error("El parámetro 'tipo_muestra' es requerido.")

    try:
        anio_min = int(request.args.get("anio_min", anio_min_db))
        anio_max = int(request.args.get("anio_max", anio_max_db))
    except ValueError:
        return _error("Los parámetros 'anio_min' y 'anio_max' deben ser números enteros.")

    if anio_min > anio_max:
        return _error("'anio_min' no puede ser mayor que 'anio_max'.")

    ranking, umbral = generar_ranking(bacteria, tipo_muestra, anio_min, anio_max)

    if ranking is None:
        return _error(
            f"No hay datos para '{bacteria}' en '{tipo_muestra}' entre {anio_min} y {anio_max}.",
            404,
        )

    filas = [
        {
            "antibiotico":       antibiotico,
            "susceptibilidad_%": row["Susceptibilidad_%"],
            "total_casos":       int(row["Total"]),
            "fiabilidad":        row["Fiabilidad"],
        }
        for antibiotico, row in ranking.iterrows()
    ]

    return jsonify({
        "bacteria":     bacteria,
        "tipo_muestra": tipo_muestra,
        "anio_min":     anio_min,
        "anio_max":     anio_max,
        "umbral":       umbral,
        "ranking":      filas,
    })


if __name__ == "__main__":
    print("NeoRX API corriendo en http://localhost:8000")
    app.run(debug=True, port=8000)
