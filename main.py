
"""
-------------------ARCHIVO EJECUTABLE---------
Muestra el saludo inicial y llama a las funciones dentro de engine.py 
(que está dentro de la carpeta src) para que funcione la app.

"""

from src.engine import run_engine

def main():
    print("====================================")
    print("      NeoRX: Soporte Clínico        ")
    print("   (Prototipo Enfoque Neumonía)     ")
    print("====================================")
    
    run_engine()

if __name__ == "__main__":
    main()