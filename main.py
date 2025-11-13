# Calculadora NumExpert
# Función 'Main'
# Para instalar dependencias de la calculadora : pip install -r requirements.txt

from models.interfaz import Interfaz

def main():
    app = Interfaz()
    app.run()

if __name__ == "__main__":
    main()
