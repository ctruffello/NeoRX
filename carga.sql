/* 
Archivo de base de datos
*/
DROP TABLE IF EXISTS clinica;
DROP TABLE IF EXISTS archivo_cargado;
DROP TABLE IF EXISTS bacteria;
DROP TABLE IF EXISTS antibiotico;
DROP TABLE IF EXISTS tipo_muestra;
DROP TABLE IF EXISTS antibiograma;
DROP TABLE IF EXISTS resultado_antibiotico;

CREATE TABLE clinica (
    id_clinica SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL
);

CREATE TABLE archivo_cargado (
    id_archivo SERIAL PRIMARY KEY,
    id_clinica INTEGER NOT NULL REFERENCES clinica(id_clinica),
    nombre_archivo VARCHAR(200) NOT NULL,
    fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bacteria (
    id_bacteria SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE antibiotico (
    id_antibiotico SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE tipo_muestra (
    id_tipo_muestra SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE antibiograma (
    id_antibiograma SERIAL PRIMARY KEY,
    id_archivo INTEGER NOT NULL REFERENCES archivo_cargado(id_archivo),
    id_clinica INTEGER NOT NULL REFERENCES clinica(id_clinica),
    fecha_toma_muestra DATE,
    anio INTEGER,
    id_tipo_muestra INTEGER REFERENCES tipo_muestra(id_tipo_muestra),
    id_bacteria INTEGER REFERENCES bacteria(id_bacteria)
);

CREATE TABLE resultado_antibiotico (
    id_resultado SERIAL PRIMARY KEY,
    id_antibiograma INTEGER NOT NULL REFERENCES antibiograma(id_antibiograma),
    id_antibiotico INTEGER NOT NULL REFERENCES antibiotico(id_antibiotico),
    estado VARCHAR(5) NOT NULL,
    CHECK (estado IN ('S', 'I', 'R'))
);