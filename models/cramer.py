from copy import deepcopy
from fractions import Fraction

from models.imprimir_matriz import imprimir_matriz
from models.determinante import detMatriz

def reglaCramer(matriz):

    if len(matriz) + 1 != len(matriz[0]):

        print("No es posible resolver el sistema usando la regla de Cramer")
        print("La cantidad de ecuaciones, debe coincidir con las cantidad de incógnitas")
        print("Para resolver sistemas como estos, utilice Gauss-Jordan o Gauss")
    else:

        matCoeficiente = deepcopy(matriz)
        configurarMatriz(matCoeficiente)
        det_mC = detMatriz(matCoeficiente) # Determinante de la matriz de coeficientes

        if det_mC == 0:

            print("El sistema:")
            print("- Tiene infinitas soluciones")
            print("- Es inconsistente")
        else:

            soluciones = []
            for m in range(len(matriz)):

                matrizNueva = deepcopy(matriz)
                configurarMatriz(matrizNueva)

                for i in range(len(matriz)):

                    matrizNueva[i][m] = matriz[i][len(matriz[0]) - 1]

                det_mN = detMatriz(matrizNueva)
                soluciones.append(Fraction(det_mN, det_mC))
            
            print("SOLUCIONES DEL SISTEMA:\n")

            for s in range(len(matriz)):

                print(f"x{s + 1} = {soluciones[s]}")

# Para encontrar la determinantes, se sacan los términos independientes
def configurarMatriz(mat_configurar):

    for fila in mat_configurar:

        fila.pop()