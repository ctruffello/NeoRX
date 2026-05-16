# NeoRX — Ranking de Antibióticos

Sistema que procesa antibiogramas clínicos, limpia los datos y genera un ranking de antibióticos según su tasa de susceptibilidad. Incluye base de datos, API y frontend web.

---

## ¿Qué hace el sistema?

1. Lee un archivo Excel con resultados de antibiogramas
2. Limpia y normaliza los datos (corrige nombres, separa filas inválidas)
3. Guarda todo en una base de datos
4. Calcula qué antibióticos funcionan mejor para cada bacteria
5. Muestra los resultados en una página web con gráfico y tabla

---

## Requisitos

- Python 3.10 o superior
- Las librerías listadas en `requirements.txt`

---

## Instalación (solo la primera vez)

```bash
pip install -r requirements.txt
```

---

## Cómo usar

### Paso 1 — Cargar los datos

Esto lee el Excel, limpia los datos y los guarda en la base de datos.
Solo necesitas hacerlo **una vez** (o cada vez que tengas un archivo nuevo).

```bash
python3 main.py
```

Verás algo así:

```
Procesando archivo de antibiogramas...
  Filas válidas:   21567
  Filas inválidas: 4704 → guardadas en data/no_validos.xlsx
Normalizando nombres...
  Listos para insertar: 21567
Insertando en la base de datos...
  Resultados insertados: 21567
  Estado del archivo: ok
```

### Paso 2 — Levantar la aplicación web

```bash
python3 api/app.py
```

Luego abre el navegador en:

```
http://localhost:8000
```

Para detener el servidor presiona `Ctrl + C` en la terminal.

---

## Archivos importantes

```
NeoRX/
│
├── data/
│   ├── Antibiograma_2016_2025.xlsx   ← Archivo de entrada (datos privados)
│   ├── regiones_comunas.csv          ← Regiones y comunas de Chile
│   └── no_validos.xlsx               ← Filas rechazadas durante la limpieza
│
├── src/                              ← Todo el código del sistema
│   ├── engine.py                     ← Orquesta el proceso completo
│   ├── limpieza.py                   ← Limpia el Excel y separa filas inválidas
│   ├── normalizacion.py              ← Normaliza nombres de bacterias y antibióticos
│   ├── insercion.py                  ← Inserta los datos en la base de datos
│   ├── ranking.py                    ← Calcula el ranking consultando la base de datos
│   └── base_de_datos.py              ← Conexión y estructura de la base de datos
│
├── api/
│   └── app.py                        ← Servidor web (Flask), sirve la API y el frontend
│
├── frontend/
│   └── index.html                    ← Página web con filtros, gráfico y tabla
│
├── neorx.db                          ← Base de datos (se crea automáticamente)
├── main.py                           ← Punto de entrada para cargar datos
└── requirements.txt                  ← Librerías necesarias
```

---

## ¿Qué hace cada archivo de `src/`?

| Archivo | Qué hace |
|---|---|
| `engine.py` | Llama a todos los pasos en orden: limpiar → normalizar → insertar |
| `limpieza.py` | Lee el Excel, descarta filas sin bacteria válida o sin estado S/I/R |
| `normalizacion.py` | Compara nombres sucios contra listas maestras y los corrige automáticamente |
| `insercion.py` | Toma los datos limpios y los guarda en las tablas de la base de datos |
| `ranking.py` | Consulta la base de datos y calcula qué antibióticos tienen mayor susceptibilidad |
| `base_de_datos.py` | Crea la base de datos, las tablas y carga las regiones y comunas de Chile |

---

## ¿Qué hace la API?

| Endpoint | Descripción |
|---|---|
| `GET /` | Abre el frontend (la página web) |
| `GET /bacterias` | Lista de bacterias disponibles |
| `GET /tipos-muestra` | Lista de tipos de muestra |
| `GET /anios` | Rango de años disponibles en los datos |
| `GET /ranking` | Ranking de antibióticos con filtros |

Ejemplo de consulta al ranking:
```
http://localhost:8000/ranking?bacteria=Escherichia coli&tipo_muestra=UROCULTIVO&anio_min=2020&anio_max=2025
```

---

## Base de datos

La base de datos es un archivo local llamado `neorx.db` que se crea automáticamente al correr `main.py`. Contiene estas tablas:

| Tabla | Contenido |
|---|---|
| `clinica` | Clínica de origen de los datos |
| `region` | Regiones de Chile |
| `comuna` | Comunas de Chile |
| `archivo_cargado` | Registro de cada Excel procesado |
| `bacteria` | Catálogo de bacterias normalizadas |
| `antibiotico` | Catálogo de antibióticos normalizados |
| `tipo_muestra` | Tipos de muestra (aspirado, urocultivo) |
| `antibiograma` | Una fila por cada muestra procesada |
| `resultado_antibiotico` | Resultado S/I/R por cada antibiótico probado |
| `log_limpieza` | Registro de errores durante el procesamiento |

---

## Datos inválidos

Las filas del Excel que no pueden procesarse se guardan en `data/no_validos.xlsx` con una columna `MOTIVO_RECHAZO` que explica por qué fueron rechazadas. Por ejemplo:

- `DETECCION FINAL no es bacteria` — el resultado era "Negativo" o "Microbiota"
- `ESTADO inválido (-)` — no tiene resultado S, I o R
- `ANTIBIOTICO vacío` — la fila no tiene antibiótico registrado

---

## Estado actual del proyecto

- [x] Limpieza de datos
- [x] Normalización de bacterias y antibióticos
- [x] Base de datos relacional
- [x] Cálculo de ranking
- [x] API REST
- [x] Frontend web con gráfico y tabla
- [ ] Publicación online (pendiente)
- [ ] Soporte para múltiples clínicas simultáneas (diseño preparado)

---

## Notas técnicas

- La base de datos usa **SQLite** (no requiere instalación, el archivo es `neorx.db`)
- El servidor web usa **Flask** en el puerto `8000`
- El frontend usa **Chart.js** para los gráficos (cargado desde internet)
- El sistema está preparado para escalar a múltiples clínicas: la tabla `clinica` ya existe y cada archivo queda asociado a una clínica
- Para pasar a producción online se recomienda migrar a **PostgreSQL** y alojar en **Railway** o **Render**
