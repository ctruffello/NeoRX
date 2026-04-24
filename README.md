--------------------INDICACIONES DE USO-----------------------

POR FAVOR, MANTENER ORDEN DE LAS CARPETAS

¿cÓMO ABRIR LA TERMINAL?
1. Abrir powershell o en vscode apretar Terminal y luego New Terminal
2. Escriben en la terminal cd (PATH de su computadora\NeoRX). El path lo pueden copiar y pegar desde archivos si se ubican dentro de la carpeta que quieren. 


--------------------PARA CORRER EL CÓDIGO (los ---  --- no se escriben por si acaso)---------------------

1. Escribir en la terminal, dentro de la carpeta principal (...\NeoRX) 
---  pip install -r requirements.txt  ---

2. --- python main.py --- 



EN CASO DE QUE NO FUNCIONE CORRER MAIN.PY 
Es probable que haya una falla en los dataset porque se descargaron mal los archivos. En ese caso, previo a correr main.py deben correr
--- python src/generator.py ---
Esto sólo lo tienen que hacer una vez, luego podrán correr
--- python main.py ---
Para hacerlo funcionar


SIEMPRE CORRER TODO DENTRO DE LA CARPETA PRINCIPAL (path de donde lo tengan ustedes\NeoRX)
ejemplo: C:\Users\catru\OneDrive\Escritorio\NeoRX
ejemplo NO: C:\Users\catru\OneDrive\Escritorio\NeoRX\src 


--------------------FUNCINAMIENTO DE LAS CARPETAS--------------------------------------------------------
Cada archivo explica que hace.
--- En data se encuentran los datos. RAW = los que nos mandó el médico. PROCESSED = los ingresados o data aprendida. 
--- en scr (source) está todo el código para el funcionamiento del software. Cada archivo explica que hace, por favor mantener su funcionamiento y no mezclar funciones. Es preferible crear más archivos que tener uno que haga funciones demaisado distintas. 



